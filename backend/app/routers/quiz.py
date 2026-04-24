from fastapi import APIRouter, HTTPException, status, Depends
from app.auth.dependencies import get_current_user
from app.models.schemas import (
    QuizResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
)
from app.services.quiz_generator import generate_quiz
from app.services.assessment_engine import evaluate_quiz


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


def _raise_quiz_error(exc: Exception) -> None:
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    _handle_dependency_error(exc)


def _raise_submit_error(exc: Exception) -> None:
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    _handle_dependency_error(exc)


router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/{topic_id}", response_model=QuizResponse)
async def get_quiz(topic_id: str, current_user: dict = Depends(get_current_user)):
    """Generate or get cached quiz for a topic"""
    try:
        result = await generate_quiz(topic_id)
        return QuizResponse(**result)
    except Exception as exc:
        _raise_quiz_error(exc)


@router.post("/submit", response_model=QuizSubmitResponse)
async def submit_quiz(
    data: QuizSubmitRequest,
    current_user: dict = Depends(get_current_user),
):
    """Submit quiz answers and get evaluation"""
    user_id = current_user["sub"]
    answers = [{"question_id": a.question_id, "answer": a.answer} for a in data.answers]

    try:
        result = await evaluate_quiz(user_id, data.quiz_id, answers)
        return QuizSubmitResponse(**result)
    except Exception as exc:
        _raise_submit_error(exc)
