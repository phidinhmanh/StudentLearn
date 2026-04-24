from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.auth.dependencies import get_current_user
from app.models.schemas import LearningPathResponse
from app.services.learning_path_engine import get_personalized_path, generate_learning_path


NEO4J_UNAVAILABLE_DETAIL = "Database connection failed. Please try again later."
GEMINI_UNAVAILABLE_DETAIL = "AI service failed. Please try again later."


def _handle_dependency_error(exc: Exception) -> None:
    if isinstance(exc, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=NEO4J_UNAVAILABLE_DETAIL,
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=GEMINI_UNAVAILABLE_DETAIL,
    ) from exc


router = APIRouter(prefix="/learning-path", tags=["learning_path"])


@router.get("/{user_id}", response_model=LearningPathResponse)
async def get_learning_path(
    user_id: str,
    goal: str = Query("master_all", description="Learning goal"),
    current_user: dict = Depends(get_current_user),
):
    """Get personalized learning path for user (cached if available)"""
    if current_user["sub"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        result = await get_personalized_path(user_id, goal)
        return LearningPathResponse(**result)
    except Exception as exc:
        _handle_dependency_error(exc)


@router.post("/generate", response_model=LearningPathResponse)
async def regenerate_learning_path(
    user_id: str,
    goal: str = Query("master_all"),
    current_user: dict = Depends(get_current_user),
):
    """Force regenerate learning path"""
    if current_user["sub"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        result = await generate_learning_path(user_id, goal)
        return LearningPathResponse(**result)
    except Exception as exc:
        _handle_dependency_error(exc)
