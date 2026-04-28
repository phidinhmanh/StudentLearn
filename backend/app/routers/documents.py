from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from app.auth.dependencies import get_current_user
from app.models.schemas import DocumentIngestResponse, DocumentResponse, TopicResponse
from app.services.factory import get_graph_service
from app.services.document_parser import parse_document
from app.services.cognee_engine import ingest_document as cognee_ingest
import aiofiles
import os
import tempfile
from app.config import get_settings
from typing import List


GRAPH_UNAVAILABLE_DETAIL = "Database connection failed. Please try again later."
GEMINI_UNAVAILABLE_DETAIL = "AI service failed. Please try again later."


def _handle_dependency_error(exc: Exception) -> None:
    if isinstance(exc, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=GRAPH_UNAVAILABLE_DETAIL,
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=GEMINI_UNAVAILABLE_DETAIL,
    ) from exc


router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(
    file: UploadFile = File(...),
    subject: str = "general",
    current_user: dict = Depends(get_current_user),
):
    """Upload and ingest a document to extract knowledge graph"""
    user_id = current_user["sub"]

    file_size = 0
    file_bytes = b""
    while chunk := file.file.read(1024 * 1024):
        file_size += len(chunk)
        if file_size > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.max_file_size_mb}MB",
            )
        file_bytes += chunk

    allowed_types = [".pdf", ".docx", ".txt"]
    if not any(file.filename.lower().endswith(ext) for ext in allowed_types):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}",
        )

    try:
        service = get_graph_service()
        doc_id = await service.create_document(file.filename, user_id)
    except RuntimeError as exc:
        _handle_dependency_error(exc)

    try:
        chunks = parse_document(file_bytes, file.filename)
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content found in document",
            )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    # Save file to a temporary location for Cognee ingestion
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        # Ingest into Cognee (Local-first)
        await cognee_ingest(tmp_path, dataset_name=f"doc_{doc_id}")
        
        # We can still extract topics for our local metadata if needed, 
        # but the primary graph is now in Cognee.
        # For now, let's keep the response structure.
        result = {"topics_created": 0, "edges_created": 0} 
    except Exception as exc:
        _handle_dependency_error(exc)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return DocumentIngestResponse(
        doc_id=doc_id,
        filename=file.filename,
        status="success",
        topics_extracted=result["topics_created"],
        edges_created=result["edges_created"],
    )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(current_user: dict = Depends(get_current_user)):
    """List all documents for current user"""
    user_id = current_user["sub"]
    try:
        service = get_graph_service()
        docs = await service.get_documents_by_user(user_id)
    except RuntimeError as exc:
        _handle_dependency_error(exc)
    return [DocumentResponse(**d) for d in docs]


@router.get("/{doc_id}/topics", response_model=List[TopicResponse])
async def get_document_topics(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get all topics extracted from a document"""
    user_id = current_user["sub"]
    try:
        service = get_graph_service()
        doc = await service.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if doc.get("user_id") != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        topics = await service.get_topics_by_document(doc_id)
    except RuntimeError as exc:
        _handle_dependency_error(exc)
    return [TopicResponse(**t) for t in topics]
