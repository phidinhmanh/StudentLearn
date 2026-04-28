from typing import Optional
from app.config import get_settings
from app.services.base_graph_service import BaseGraphService
from app.services.cognee_service import CogneeService

settings = get_settings()

_graph_service: Optional[BaseGraphService] = None

def get_graph_service() -> BaseGraphService:
    """Factory function to get the configured graph service instance"""
    global _graph_service
    
    if _graph_service is None:
        provider = settings.graph_provider.lower()
        # Default to Cognee
        _graph_service = CogneeService()
            
    return _graph_service
