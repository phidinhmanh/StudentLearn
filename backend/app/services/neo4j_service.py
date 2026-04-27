from datetime import datetime
import uuid
from typing import List, Dict, Optional, Any

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

from app.config import get_settings

settings = get_settings()


def _to_python_datetime(value: Any) -> Any:
    if hasattr(value, "to_native"):
        native = value.to_native()
        if isinstance(native, datetime):
            return native
    return value


class Neo4jService:
    def __init__(self):
        self._driver = None
        self._initialized = False
        self._init_error: Optional[str] = None

    def _ensure_driver(self):
        """Lazy initialization of driver - only create when needed"""
        if self._driver is not None:
            return
        try:
            self._driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            self._initialized = True
            self._ensure_constraints()
        except (ServiceUnavailable, AuthError) as e:
            self._init_error = str(e)
            self._driver = None
            raise RuntimeError(f"Cannot connect to Neo4j: {e}")

    @property
    def driver(self):
        """Get driver, lazy initializing if needed"""
        self._ensure_driver()
        if self._driver is None:
            raise ConnectionError("Neo4j driver not available")
        return self._driver

    @property
    def is_connected(self) -> bool:
        """Check if Neo4j is connected"""
        try:
            self._ensure_driver()
            with self._driver.session() as session:
                session.run("RETURN 1")
            return True
        except Exception:
            return False

    def get_connection_status(self) -> Dict[str, str]:
        """Get detailed connection status"""
        try:
            self._ensure_driver()
            with self._driver.session() as session:
                session.run("RETURN 1")
            return {"status": "connected", "error": None}
        except Exception as e:
            return {"status": "disconnected", "error": str(e)}

    def _ensure_constraints(self):
        """Create constraints and indexes on startup"""
        if self._driver is None:
            return
        try:
            with self._driver.session() as session:
                constraints = [
                    "CREATE CONSTRAINT topic_id IF NOT EXISTS FOR (t:Topic) REQUIRE t.id IS UNIQUE",
                    "CREATE CONSTRAINT doc_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
                    "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
                    "CREATE CONSTRAINT quiz_id IF NOT EXISTS FOR (q:Quiz) REQUIRE q.id IS UNIQUE",
                ]
                indexes = [
                    "CREATE INDEX topic_name_idx IF NOT EXISTS FOR (t:Topic) ON (t.name)",
                ]
                for c in constraints + indexes:
                    try:
                        session.run(c)
                    except Exception:
                        pass
        except Exception:
            pass

    def close(self):
        """Close the driver connection"""
        if self._driver:
            self._driver.close()
            self._driver = None
            self._initialized = False

    # === Document operations ===

    def create_document(self, filename: str, user_id: str) -> str:
        doc_id = str(uuid.uuid4())
        with self.driver.session() as session:
            session.run(
                """
                CREATE (d:Document {
                    id: $doc_id,
                    filename: $filename,
                    user_id: $user_id,
                    uploaded_at: datetime()
                })
                """,
                doc_id=doc_id,
                filename=filename,
                user_id=user_id,
            )
        return doc_id

    def get_documents_by_user(self, user_id: str) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:Document {user_id: $user_id})
                RETURN d.id as id, d.filename as filename, d.uploaded_at as uploaded_at
                ORDER BY d.uploaded_at DESC
                """,
                user_id=user_id,
            )
            records = [dict(r) for r in result]
            for record in records:
                record["uploaded_at"] = _to_python_datetime(record.get("uploaded_at"))
            return records

    def get_document(self, doc_id: str) -> Optional[Dict]:
        with self.driver.session() as session:
            result = session.run(
                "MATCH (d:Document {id: $doc_id}) RETURN d",
                doc_id=doc_id,
            )
            record = result.single()
            return dict(record["d"]) if record else None

    # === Topic operations ===

    def upsert_topic(self, name: str, description: str = "", topic_type: str = "concept",
                     difficulty: str = "medium", subject: str = "", doc_id: str = None) -> str:
        """Create or update topic, link to document"""
        topic_id = str(uuid.uuid4())

        with self.driver.session() as session:
            # Merge topic (avoid duplicates by name)
            result = session.run(
                """
                MERGE (t:Topic {name: $name})
                ON CREATE SET t.id = $topic_id, t.description = $description,
                              t.type = $topic_type, t.difficulty = $difficulty,
                              t.subject = $subject, t.created_at = datetime()
                ON MATCH SET t.description = COALESCE($description, t.description),
                            t.type = COALESCE($topic_type, t.type),
                            t.difficulty = COALESCE($difficulty, t.difficulty),
                            t.subject = COALESCE($subject, t.subject)
                RETURN t.id as id
                """,
                name=name,
                topic_id=topic_id,
                description=description,
                topic_type=topic_type,
                difficulty=difficulty,
                subject=subject,
            )
            record = result.single()
            actual_topic_id = record["id"] if record else topic_id

            # Link to document if doc_id provided
            if doc_id:
                session.run(
                    """
                    MATCH (d:Document {id: $doc_id})
                    MATCH (t:Topic {id: $topic_id})
                    MERGE (d)-[:FROM_DOC]->(t)
                    """,
                    doc_id=doc_id,
                    topic_id=actual_topic_id,
                )

            return actual_topic_id

    def upsert_edge(self, from_name: str, to_name: str, relation: str,
                    weight: float = 1.0, properties: Dict = None) -> bool:
        """Create edge between topics by name"""
        with self.driver.session() as session:
            props_str = ""
            if properties:
                props_parts = [f"e.{k} = ${k}" for k in properties.keys()]
                props_str = "SET " + ", ".join(props_parts)

            query = f"""
                MATCH (a:Topic {{name: $from_name}})
                MATCH (b:Topic {{name: $to_name}})
                MERGE (a)-[r:{relation}]->(b)
                SET r.weight = COALESCE(r.weight, 0) + $weight
                {props_str}
                RETURN count(r) as cnt
            """
            result = session.run(
                query,
                from_name=from_name,
                to_name=to_name,
                relation=relation,
                weight=weight,
                **(properties or {}),
            )
            return result.single()["cnt"] > 0

    def get_topics_by_document(self, doc_id: str) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (d:Document {id: $doc_id})-[:FROM_DOC]->(t:Topic)
                RETURN t.id as id, t.name as name, t.description as description,
                       t.type as type, t.difficulty as difficulty, t.subject as subject
                """,
                doc_id=doc_id,
            )
            return [dict(r) for r in result]

    def get_all_topics(self) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (t:Topic)
                OPTIONAL MATCH (t)<-[:prerequisite]-(prev:Topic)
                OPTIONAL MATCH (t)-[:prerequisite]->(next:Topic)
                RETURN t.id as id, t.name as name, t.description as description,
                       t.type as type, t.difficulty as difficulty, t.subject as subject,
                       collect(DISTINCT prev.name) as prerequisites,
                       collect(DISTINCT next.name) as dependents
                """
            )
            return [dict(r) for r in result]

    def get_topic_with_neighbors(self, topic_id: str) -> Optional[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (t:Topic {id: $topic_id})
                OPTIONAL MATCH (t)<-[r:prerequisite]-(prev:Topic)
                OPTIONAL MATCH (t)-[r2:prerequisite]->(next:Topic)
                OPTIONAL MATCH (t)-[r3:sequenceOf|relatedTo]-(other:Topic)
                RETURN t.id as id, t.name as name, t.description as description,
                       collect(DISTINCT {node: prev, rel: 'prerequisite'}) as prereqs_from,
                       collect(DISTINCT {node: next, rel: 'prerequisite'}) as prereqs_to,
                       collect(DISTINCT {node: other, rel: type(r3)}) as related
                """,
                topic_id=topic_id,
            )
            record = result.single()
            return dict(record) if record else None

    # === User / Auth operations ===

    def create_user(self, user_id: str, email: str, name: str, hashed_password: str) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (u:User {
                    id: $user_id,
                    email: $email,
                    name: $name,
                    hashed_password: $hashed_password,
                    created_at: datetime()
                })
                """,
                user_id=user_id,
                email=email,
                name=name,
                hashed_password=hashed_password,
            )
            return True

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        with self.driver.session() as session:
            result = session.run(
                "MATCH (u:User {email: $email}) RETURN u",
                email=email,
            )
            record = result.single()
            return dict(record["u"]) if record else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        with self.driver.session() as session:
            result = session.run(
                "MATCH (u:User {id: $user_id}) RETURN u",
                user_id=user_id,
            )
            record = result.single()
            return dict(record["u"]) if record else None

    # === Quiz operations ===

    def save_quiz(self, quiz_id: str, topic_id: str, questions: List[Dict]) -> bool:
        with self.driver.session() as session:
            session.run(
                """
                MATCH (t:Topic {id: $topic_id})
                CREATE (q:Quiz {id: $quiz_id, topic_id: $topic_id, created_at: datetime()})
                CREATE (q)-[:FOR_TOPIC]->(t)
                """,
                quiz_id=quiz_id,
                topic_id=topic_id,
            )

            for q in questions:
                session.run(
                    """
                    MATCH (q:Quiz {id: $quiz_id})
                    CREATE (qn:Question {
                        id: $q_id,
                        text: $text,
                        type: $q_type,
                        options: $options,
                        correct_answer: $correct_answer,
                        explanation: $explanation
                    })
                    CREATE (q)-[:CONTAINS]->(qn)
                    """,
                    quiz_id=quiz_id,
                    q_id=str(uuid.uuid4()),
                    text=q["text"],
                    q_type=q.get("type", "multiple_choice"),
                    options=str(q.get("options", [])),
                    correct_answer=q["correct_answer"],
                    explanation=q.get("explanation", ""),
                )
        return True

    def get_quiz_by_topic(self, topic_id: str) -> Optional[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (q:Quiz {topic_id: $topic_id})
                OPTIONAL MATCH (q)-[:CONTAINS]->(qn:Question)
                RETURN q.id as quiz_id, q.topic_id as topic_id, q.created_at as created_at,
                       collect({
                           id: qn.id,
                           text: qn.text,
                           type: qn.type,
                           options: qn.options,
                           explanation: qn.explanation
                       }) as questions
                ORDER BY q.created_at DESC
                LIMIT 1
                """,
                topic_id=topic_id,
            )
            record = result.single()
            if not record:
                return None
            data = dict(record)
            # Parse options from string
            for q in data["questions"]:
                if q["options"] and isinstance(q["options"], str):
                    import ast
                    try:
                        q["options"] = ast.literal_eval(q["options"])
                    except:
                        q["options"] = []
            # Remove questions with no id (empty collect)
            data["questions"] = [q for q in data["questions"] if q["id"]]
            return data

    def get_quiz(self, quiz_id: str) -> Optional[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (q:Quiz {id: $quiz_id})
                OPTIONAL MATCH (q)-[:CONTAINS]->(qn:Question)
                RETURN q.id as quiz_id, q.topic_id as topic_id, q.created_at as created_at,
                       collect({
                           id: qn.id,
                           text: qn.text,
                           type: qn.type,
                           options: qn.options,
                           correct_answer: qn.correct_answer,
                           explanation: qn.explanation
                       }) as questions
                """,
                quiz_id=quiz_id,
            )
            record = result.single()
            if not record:
                return None
            data = dict(record)
            for q in data["questions"]:
                if q["options"] and isinstance(q["options"], str):
                    import ast
                    try:
                        q["options"] = ast.literal_eval(q["options"])
                    except:
                        q["options"] = []
            data["questions"] = [q for q in data["questions"] if q["id"]]
            return data

    # === Progress operations ===

    def upsert_progress(self, user_id: str, topic_id: str, skill_level: int) -> bool:
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {id: $user_id})
                MERGE (u)-[p:HAS_PROGRESS]->(prog:Progress {topic_id: $topic_id})
                SET prog.skill_level = $skill_level,
                    prog.last_attempt = datetime()
                """,
                user_id=user_id,
                topic_id=topic_id,
                skill_level=skill_level,
            )
        return True

    def get_user_progress(self, user_id: str) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[p:HAS_PROGRESS]->(prog:Progress)
                MATCH (t:Topic {id: prog.topic_id})
                RETURN prog.topic_id as topic_id, t.name as topic_name,
                       prog.skill_level as skill_level, prog.last_attempt as last_attempt
                """,
                user_id=user_id,
            )
            return [dict(r) for r in result]

    # === Learning Path ===

    def save_learning_path(self, user_id: str, path_json: str) -> bool:
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {id: $user_id})
                MERGE (u)-[lp:HAS_PATH]->(path:LearningPath)
                SET path.path_json = $path_json,
                    path.generated_at = datetime()
                """,
                user_id=user_id,
                path_json=path_json,
            )
        return True

    def get_learning_path(self, user_id: str) -> Optional[Dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[lp:HAS_PATH]->(path:LearningPath)
                RETURN path.path_json as path_json, path.generated_at as generated_at
                ORDER BY path.generated_at DESC
                LIMIT 1
                """,
                user_id=user_id,
            )
            record = result.single()
            return dict(record) if record else None

    def invalidate_learning_path(self, user_id: str) -> bool:
        with self.driver.session() as session:
            session.run(
                """
                MATCH (u:User {id: $user_id})-[lp:HAS_PATH]->(path:LearningPath)
                DELETE lp
                DELETE path
                """,
                user_id=user_id,
            )
        return True


# Singleton instance
_neo4j_service: Optional[Neo4jService] = None


def get_neo4j_service() -> Neo4jService:
    """Get Neo4j service singleton (lazy initialization)"""
    global _neo4j_service
    if _neo4j_service is None:
        _neo4j_service = Neo4jService()
    return _neo4j_service