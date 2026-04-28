import os
import uuid
import asyncio
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import cognee
from cognee.api.v1.search import SearchType

from app.config import get_settings
from app.services.base_graph_service import BaseGraphService
from app.services.cognee_engine import (
    ingest_document as cognee_ingest,
    search_graph as cognee_search,
    recall_context as cognee_recall
)

settings = get_settings()

class CogneeService(BaseGraphService):
    def __init__(self):
        self.initialized = False
        self._metadata_file = "cognee_metadata.json"
        self._load_metadata()

    def _load_metadata(self):
        """Load application metadata (users, documents, etc.) from local file"""
        if os.path.exists(self._metadata_file):
            try:
                with open(self._metadata_file, "r") as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = self._get_empty_metadata()
        else:
            self.metadata = self._get_empty_metadata()

    def _get_empty_metadata(self):
        return {
            "users": {}, 
            "documents": {}, 
            "quizzes": {}, 
            "progress": {}, 
            "paths": {}, 
            "topics": {},
            "edges": []
        }

    def _save_metadata(self):
        """Save application metadata to local file"""
        with open(self._metadata_file, "w") as f:
            json.dump(self.metadata, f)

    async def is_connected(self) -> bool:
        return True # Cognee is local by default

    async def get_connection_status(self) -> Dict:
        return {
            "status": "connected",
            "provider": "cognee",
            "message": "Local metadata store and Cognee graph ready"
        }

    async def create_document(self, filename: str, user_id: str) -> str:
        doc_id = str(uuid.uuid4())
        self.metadata["documents"][doc_id] = {
            "id": doc_id,
            "filename": filename,
            "user_id": user_id,
            "uploaded_at": datetime.now().isoformat(),
            "topics": []
        }
        self._save_metadata()
        return doc_id

    async def get_documents_by_user(self, user_id: str) -> List[Dict]:
        return [doc for doc in self.metadata["documents"].values() if doc["user_id"] == user_id]

    async def get_document(self, doc_id: str) -> Optional[Dict]:
        return self.metadata["documents"].get(doc_id)

    async def batch_upsert_topics(self, topics: List[Dict], doc_id: str = None) -> List[Dict]:
        inserted = []
        for t in topics:
            name = t.get("name")
            if not name: continue
            
            # Use name as ID for simple lookup or UUID
            t_id = name.lower().replace(" ", "_")
            topic_data = {
                "id": t_id,
                "name": name,
                "type": t.get("type", "concept"),
                "description": t.get("description", ""),
                "difficulty": t.get("difficulty", "medium")
            }
            self.metadata["topics"][t_id] = topic_data
            inserted.append(topic_data)
            
            if doc_id and doc_id in self.metadata["documents"]:
                if t_id not in self.metadata["documents"][doc_id]["topics"]:
                    self.metadata["documents"][doc_id]["topics"].append(t_id)
        
        self._save_metadata()
        return inserted

    async def batch_upsert_edges(self, edges: List[Dict]) -> int:
        count = 0
        for edge in edges:
            self.metadata["edges"].append(edge)
            count += 1
        self._save_metadata()
        return count

    async def get_topics_by_document(self, doc_id: str) -> List[Dict]:
        doc = self.metadata["documents"].get(doc_id)
        if not doc or "topics" not in doc:
            return []
        return [self.metadata["topics"].get(tid) for tid in doc["topics"] if tid in self.metadata["topics"]]

    async def get_all_topics(self) -> List[Dict]:
        return list(self.metadata["topics"].values())

    async def get_topic_with_neighbors(self, topic_id: str) -> Optional[Dict]:
        topic = self.metadata["topics"].get(topic_id)
        if not topic:
            return None
            
        # Find neighbors in metadata edges
        prereqs_from = []
        related = []
        
        for edge in self.metadata["edges"]:
            from_name = edge.get("from_name", "").lower().replace(" ", "_")
            to_name = edge.get("to_name", "").lower().replace(" ", "_")
            rel = edge.get("relation", "")
            
            if to_name == topic_id:
                if rel == "prerequisite":
                    prereqs_from.append({"node": self.metadata["topics"].get(from_name)})
            elif from_name == topic_id:
                if rel == "relatedTo":
                    related.append({"node": self.metadata["topics"].get(to_name)})
                    
        return {
            **topic,
            "prereqs_from": [p for p in prereqs_from if p["node"]],
            "related": [r for r in related if r["node"]]
        }

    async def create_user(self, user_id: str, email: str, name: str, hashed_password: str) -> bool:
        self.metadata["users"][user_id] = {
            "id": user_id,
            "email": email,
            "name": name,
            "hashed_password": hashed_password,
            "created_at": datetime.now().isoformat()
        }
        self._save_metadata()
        return True

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        for user in self.metadata["users"].values():
            if user["email"] == email:
                return user
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        return self.metadata["users"].get(user_id)

    async def save_quiz(self, quiz_id: str, topic_id: str, questions: List[Dict]) -> bool:
        self.metadata["quizzes"][quiz_id] = {
            "id": quiz_id,
            "topic_id": topic_id,
            "questions": questions,
            "created_at": datetime.now().isoformat()
        }
        self._save_metadata()
        return True

    async def get_quiz(self, quiz_id: str) -> Optional[Dict]:
        return self.metadata["quizzes"].get(quiz_id)

    async def get_quiz_by_topic(self, topic_id: str) -> Optional[Dict]:
        for quiz in self.metadata["quizzes"].values():
            if quiz["topic_id"] == topic_id:
                return quiz
        return None

    async def upsert_progress(self, user_id: str, topic_id: str, skill_level: int) -> bool:
        key = f"{user_id}:{topic_id}"
        self.metadata["progress"][key] = {
            "user_id": user_id,
            "topic_id": topic_id,
            "skill_level": skill_level,
            "last_attempt": datetime.now().isoformat()
        }
        self._save_metadata()
        return True

    async def get_user_progress(self, user_id: str) -> List[Dict]:
        return [p for p in self.metadata["progress"].values() if p["user_id"] == user_id]

    async def save_learning_path(self, user_id: str, path_json: str) -> bool:
        self.metadata["paths"][user_id] = {
            "path_json": path_json,
            "generated_at": datetime.now().isoformat()
        }
        self._save_metadata()
        return True

    async def get_learning_path(self, user_id: str) -> Optional[Dict]:
        return self.metadata["paths"].get(user_id)

    def invalidate_learning_path(self, user_id: str):
        if user_id in self.metadata["paths"]:
            del self.metadata["paths"][user_id]
            self._save_metadata()

    # --- Cognee Specific Ingestion ---
    async def ingest_text(self, text: str, dataset_name: str = "default"):
        """Add text to Cognee and process it"""
        # Save text to a temp file first since cognee_engine.ingest_document expects a file_path
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
            tmp.write(text)
            tmp_path = tmp.name
        
        try:
            await cognee_ingest(tmp_path, dataset_name=dataset_name)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    async def search(self, query: str) -> str:
        """Search via Cognee RAG"""
        return await cognee_search(query)

    async def recall(self, query: str, datasets: List[str] = None) -> List[Dict]:
        """Recall context via Cognee V2"""
        return await cognee_recall(query, datasets = datasets)
