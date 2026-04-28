from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class BaseGraphService(ABC):
    @abstractmethod
    async def is_connected(self) -> bool:
        pass

    @abstractmethod
    async def get_connection_status(self) -> Dict:
        pass

    @abstractmethod
    async def create_document(self, filename: str, user_id: str) -> str:
        pass

    @abstractmethod
    async def get_documents_by_user(self, user_id: str) -> List[Dict]:
        pass

    @abstractmethod
    async def get_document(self, doc_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    async def batch_upsert_topics(self, topics: List[Dict], doc_id: str = None) -> List[Dict]:
        pass

    @abstractmethod
    async def batch_upsert_edges(self, edges: List[Dict]) -> int:
        pass

    @abstractmethod
    async def get_topics_by_document(self, doc_id: str) -> List[Dict]:
        pass

    @abstractmethod
    async def get_all_topics(self) -> List[Dict]:
        pass

    @abstractmethod
    async def get_topic_with_neighbors(self, topic_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    async def create_user(self, user_id: str, email: str, name: str, hashed_password: str) -> bool:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    async def save_quiz(self, quiz_id: str, topic_id: str, questions: List[Dict]) -> bool:
        pass

    @abstractmethod
    async def get_quiz(self, quiz_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    async def get_quiz_by_topic(self, topic_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    async def upsert_progress(self, user_id: str, topic_id: str, skill_level: int) -> bool:
        pass

    @abstractmethod
    async def get_user_progress(self, user_id: str) -> List[Dict]:
        pass

    @abstractmethod
    async def save_learning_path(self, user_id: str, path_json: str) -> bool:
        pass

    @abstractmethod
    async def get_learning_path(self, user_id: str) -> Optional[Dict]:
        pass
