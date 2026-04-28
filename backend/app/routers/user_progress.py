from fastapi import APIRouter, HTTPException, status, Depends
from app.auth.dependencies import get_current_user
from app.models.schemas import ProgressUpdate, ProgressResponse
from app.services.factory import get_graph_service
from typing import List


NEO4J_UNAVAILABLE_DETAIL = "Database connection failed. Please try again later."


def _handle_dependency_error(exc: Exception) -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=NEO4J_UNAVAILABLE_DETAIL,
    ) from exc


router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/{user_id}", response_model=List[ProgressResponse])
async def get_progress(
    user_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get all topic progress for user"""
    if current_user["sub"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        service = get_graph_service()
        progress = await service.get_user_progress(user_id)
    except RuntimeError as exc:
        _handle_dependency_error(exc)
    return [ProgressResponse(**p) for p in progress]


@router.put("/{user_id}/{topic_id}")
async def update_progress(
    user_id: str,
    topic_id: str,
    data: ProgressUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update self-rating for a topic"""
    if current_user["sub"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        service = get_graph_service()
        await service.upsert_progress(user_id, topic_id, data.skill_level)
        if hasattr(service, "invalidate_learning_path"):
            await service.invalidate_learning_path(user_id)
    except RuntimeError as exc:
        _handle_dependency_error(exc)

    return {"message": "Progress updated"}
