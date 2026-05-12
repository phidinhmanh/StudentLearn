from typing import Optional
from app.config import get_settings
from app.services.base_graph_service import BaseGraphService

settings = get_settings()

_graph_service: Optional[BaseGraphService] = None
_user_service: Optional["UserService"] = None
_quiz_service: Optional["QuizService"] = None
_progress_service: Optional["ProgressService"] = None

def get_graph_service() -> BaseGraphService:
    """Factory function to get the configured graph service instance."""
    global _graph_service
    if _graph_service is None:
        provider = settings.graph_provider.lower()
        # Lazy import to avoid circular dependency (CogneeService imports factory)
        from app.services.cognee_service import CogneeService
        _graph_service = CogneeService()
    return _graph_service

def get_user_service():
    from app.services.user_service import UserService
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service

def get_quiz_service():
    from app.services.quiz_service import QuizService
    global _quiz_service
    if _quiz_service is None:
        _quiz_service = QuizService()
    return _quiz_service

def get_progress_service():
    from app.services.progress_service import ProgressService
    global _progress_service
    if _progress_service is None:
        _progress_service = ProgressService()
    return _progress_service
