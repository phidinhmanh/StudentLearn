# Service exports for easy import elsewhere.
# The factories create singleton instances; we expose the getters.
from app.services.factory import (
    get_user_service,
    get_quiz_service,
    get_progress_service,
    get_graph_service,
)

# Backwards compatible names (some code may import QuizService directly)
# The factory returns a concrete instance; we expose the type for type checking.
QuizService = get_quiz_service  # type: ignore
ProgressService = get_progress_service  # type: ignore
UserService = get_user_service  # type: ignore

__all__ = [
    "get_user_service",
    "UserService",
    "get_quiz_service",
    "QuizService",
    "get_progress_service",
    "ProgressService",
    "get_graph_service",
]
