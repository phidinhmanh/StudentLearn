from pydantic import BaseModel, EmailStr, Field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


# === Auth ===

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class User(BaseModel):
    id: str
    email: str
    name: str
    created_at: Optional[datetime] = None


# === Document ===

class DocumentIngestResponse(BaseModel):
    doc_id: str
    filename: str
    task_id: str
    status: str


class ErrorDetail(BaseModel):
    error_code: str
    detail: Optional[str] = None
    recoverable: bool = True
    log_id: Optional[str] = None


class DiagnosticCheck(BaseModel):
    name: str
    status: bool
    message: str
    details: Optional[Dict[str, Any]] = None


class DiagnosticResponse(BaseModel):
    overall_status: str  # "ok" | "degraded"
    checks: list[DiagnosticCheck]


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[Union[str, Dict[str, Any]]] = None


class DocumentResponse(BaseModel):
    id: str
    filename: str
    uploaded_at: datetime


class TopicResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    difficulty: Optional[str] = None
    subject: Optional[str] = None


# === Quiz ===

class QuizQuestion(BaseModel):
    id: str
    text: str
    type: str = "multiple_choice"
    options: List[str] = []
    explanation: Optional[str] = None
    cognitive_level: str = "application"  # bloom taxonomy higher-order: "understanding"|"application"|"analyze"


class QuizResponse(BaseModel):
    quiz_id: str
    topic_id: str
    questions: List[QuizQuestion]


class QuizSubmitAnswer(BaseModel):
    question_id: str
    answer: str


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: List[QuizSubmitAnswer]


class QuizResultDetail(BaseModel):
    question_id: str
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: Optional[str] = None


class QuizSubmitResponse(BaseModel):
    quiz_id: str
    topic_id: str
    correct_count: int
    total: int
    score: str
    skill_level: int
    feedback: str
    results: List[QuizResultDetail]


# === Learning Path ===

class LearningPathItem(BaseModel):
    topic_id: str
    name: str
    priority: int
    reason: str
    estimated_time: str
    status: str  # ready, review, locked


class LearningPathResponse(BaseModel):
    path: List[LearningPathItem]
    summary: Optional[str] = None


# === Progress ===

class ProgressUpdate(BaseModel):
    skill_level: int = Field(..., ge=0, le=3)


class ProgressResponse(BaseModel):
    topic_id: str
    topic_name: str
    skill_level: int
    last_attempt: Optional[datetime] = None