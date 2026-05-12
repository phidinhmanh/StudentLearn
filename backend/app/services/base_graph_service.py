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
