import os
import uuid
import logging
from typing import List, Dict, Optional

import cognee
from cognee import remember, search, visualize_graph, SearchType

from app.config import get_settings
from app.services.base_graph_service import BaseGraphService
from app.services.factory import get_user_service, get_quiz_service, get_progress_service

logger = logging.getLogger(__name__)
settings = get_settings()

# Sync environment for Cognee explicitly
os.environ["LLM_PROVIDER"] = "gemini"
os.environ["LLM_MODEL"] = f"gemini/{settings.gemini_model}"
os.environ["LLM_API_KEY"] = settings.gemini_api_key

os.environ["EMBEDDING_PROVIDER"] = "gemini"
os.environ["EMBEDDING_MODEL"] = "gemini/gemini-embedding-001"
os.environ["EMBEDDING_API_KEY"] = settings.gemini_api_key


class CogneeService(BaseGraphService):
    """Facade for Cognee knowledge‑graph + delegating app data to SQLite services."""

    def __init__(self):
        self._user_service = get_user_service()
        self._quiz_service = get_quiz_service()
        self._progress_service = get_progress_service()
        self._documents: Dict[str, Dict] = {}  # doc_id → doc metadata
        self._topics_by_doc: Dict[str, List[Dict]] = {}  # doc_id → topics list

    # ---------------------------------------------------------------------
    #  Graph (knowledge) methods – use Cognee API directly
    # ---------------------------------------------------------------------
    async def is_connected(self) -> bool:
        # Cognee is a local library – assume always ready.
        return True

    async def get_connection_status(self) -> Dict:
        return {
            "status": "connected",
            "provider": "cognee",
            "message": "Cognee graph service ready",
        }

    async def create_document(self, filename: str, user_id: str) -> str:
        # Generate a UUID; the actual ingestion will be performed by ``ingest_text``.
        doc_id = str(uuid.uuid4())
        self._documents[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "user_id": user_id,
            "uploaded_at": __import__("datetime").datetime.now()
        }
        return doc_id

    async def ingest_text(self, text: str, dataset_name: str = "default") -> None:
        """Ingest raw text into Cognee.

        ``cognee.remember`` accepts a string (or any iterable of strings) and
        handles chunking, embedding, and graph construction internally.
        """
        try:
            await remember(text, dataset_name=dataset_name)
        except Exception as exc:
            logger.error(f"Cognee ingest_text failed: {exc}")
            raise

    async def get_documents_by_user(self, user_id: str) -> List[Dict]:
        return [doc for doc in self._documents.values() if doc["user_id"] == user_id]

    async def get_document(self, doc_id: str) -> Optional[Dict]:
        return self._documents.get(doc_id)

    async def batch_upsert_topics(self, topics: List[Dict], doc_id: str = None) -> List[Dict]:
        """Create topics by feeding synthetic *topic* documents to Cognee.

        Cognee's native pipeline extracts entities from any text, so we construct
        a short description for each topic and let ``remember`` do the heavy
        lifting. The returned list mirrors the input (with possible enrichment).
        Also stores topics in local map for retrieval via get_topics_by_document.
        """
        created = []
        doc_key = doc_id or "default"
        for t in topics:
            name = t.get("name", "Unnamed")
            description = t.get("description", "")
            typ = t.get("type", "concept")
            synthetic = f"Topic: {name}\nType: {typ}\nDescription: {description}"  # noqa: E501
            topic_id = name.lower().replace(" ", "_")
            try:
                await remember(synthetic, dataset_name=doc_key)
                topic_dict = {"id": topic_id, "name": name, "type": typ, "description": description}
                created.append(topic_dict)
            except Exception as exc:
                logger.error(f"Failed to upsert topic {name}: {exc}")
        # Store in local map for get_topics_by_document
        if doc_id:
            existing = self._topics_by_doc.get(doc_id, [])
            existing.extend(created)
            self._topics_by_doc[doc_id] = existing
        return created

    async def batch_upsert_edges(self, edges: List[Dict]) -> int:
        """Create edges by feeding synthetic *relationship* documents.

        Each edge dict is expected to contain ``from_name``, ``to_name`` and
        ``relation``. We embed this information in a short sentence and let
        Cognee's graph builder infer the connection.
        """
        count = 0
        for e in edges:
            from_name = e.get("from_name", "")
            to_name = e.get("to_name", "")
            relation = e.get("relation", "relatedTo")
            synthetic = f"Relation: {from_name} {relation} {to_name}."
            try:
                await remember(synthetic, dataset_name="edges")
                count += 1
            except Exception as exc:
                logger.error(f"Failed to upsert edge {from_name}->{to_name}: {exc}")
        return count

    async def get_topics_by_document(self, doc_id: str) -> List[Dict]:
        """Return topics linked to this document from local map."""
        return self._topics_by_doc.get(doc_id, [])

    async def get_all_topics(self) -> List[Dict]:
        """Return all topic‑like nodes from the graph.

        ``visualize_graph`` returns a serialisable dict containing ``nodes`` and
        ``edges``. We filter nodes whose ``type`` is ``topic`` (or infer from the
        presence of a ``name`` field). If the structure changes in future Cognee
        versions, this function will gracefully return an empty list.
        """
        try:
            graph = await visualize_graph()
            nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
            topics = [n for n in nodes if n.get("type", "").lower() == "topic" or "topic" in n.get("name", "").lower()]
            return topics
        except Exception as exc:
            logger.error(f"visualize_graph failed: {exc}")
            return []

    async def get_topic_with_neighbors(self, topic_id: str) -> Optional[Dict]:
        """Fetch a single topic node together with its immediate neighbors.

        We perform a focused ``search`` query using the topic name. The result set
        is expected to contain the topic itself plus any linked nodes. We then
        separate ``prereqs_from`` (incoming ``prerequisite`` edges) and
        ``related`` (outgoing ``relatedTo`` edges) to match the original API.
        """
        try:
            # Retrieve the whole graph and filter locally – cheap for current sizes.
            graph = await visualize_graph()
            nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
            edges = graph.get("edges", []) if isinstance(graph, dict) else []
            topic = next((n for n in nodes if n.get("id") == topic_id), None)
            if not topic:
                return None
            prereqs = []
            related = []
            for e in edges:
                fr = e.get("from_name", "").lower().replace(" ", "_")
                to = e.get("to_name", "").lower().replace(" ", "_")
                rel = e.get("relation", "")
                if to == topic_id:
                    if rel == "prerequisite":
                        node = next((n for n in nodes if n.get("id") == fr), None)
                        if node:
                            prereqs.append({"node": node})
                elif fr == topic_id:
                    if rel == "relatedTo":
                        node = next((n for n in nodes if n.get("id") == to), None)
                        if node:
                            related.append({"node": node})
            result = {**topic, "prereqs_from": prereqs, "related": related}
            return result
        except Exception as exc:
            logger.error(f"get_topic_with_neighbors failed: {exc}")
            return None

    # ---------------------------------------------------------------------
    #  Application‑level delegations (unchanged, now routed to SQLite services)
    # ---------------------------------------------------------------------
    async def create_user(self, user_id: str, email: str, name: str, hashed_password: str) -> bool:
        return await self._user_service.create_user(user_id, email, name, hashed_password)

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        return await self._user_service.get_user_by_email(email)

    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        return await self._user_service.get_user_by_id(user_id)

    async def save_quiz(self, quiz_id: str, topic_id: str, questions: List[Dict]) -> bool:
        return await self._quiz_service.save_quiz(quiz_id, topic_id, questions)

    async def get_quiz(self, quiz_id: str) -> Optional[Dict]:
        return await self._quiz_service.get_quiz(quiz_id)

    async def get_quiz_by_topic(self, topic_id: str) -> Optional[Dict]:
        return await self._quiz_service.get_quiz_by_topic(topic_id)

    async def upsert_progress(self, user_id: str, topic_id: str, skill_level: int) -> bool:
        return await self._progress_service.upsert_progress(user_id, topic_id, skill_level)

    async def get_user_progress(self, user_id: str) -> List[Dict]:
        return await self._progress_service.get_user_progress(user_id)

    async def save_learning_path(self, user_id: str, path_json: str) -> bool:
        return await self._progress_service.save_learning_path(user_id, path_json)

    async def get_learning_path(self, user_id: str) -> Optional[Dict]:
        return await self._progress_service.get_learning_path(user_id)

    def invalidate_learning_path(self, user_id: str):
        self._progress_service.invalidate_learning_path(user_id)

    # ---------------------------------------------------------------------
    #  Cognee specific search / recall helpers
    # ---------------------------------------------------------------------
    async def search(self, query: str) -> str:
        """Query Cognee using direct RAG search."""
        from app.services.cognee_engine import search_graph
        return await search_graph(query)

    async def recall(self, query: str, datasets: List[str] = None) -> List[Dict]:
        """Recall context from datasets."""
        from app.services.cognee_engine import recall_context
        if datasets is None:
            datasets = ["math_grade_10"]
        return await recall_context(query, datasets=datasets)
