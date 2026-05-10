from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, BackgroundTasks
from app.auth.dependencies import get_current_user
from app.models.schemas import DocumentIngestResponse, DocumentResponse, TopicResponse, TaskStatusResponse
from app.services.factory import get_graph_service
from app.services.document_parser import parse_document
from app.services.task_manager import create_task, update_task, update_task_progress, get_task
import os
import tempfile
import logging
import traceback
import uuid
from app.config import get_settings
from typing import List


logger = logging.getLogger(__name__)
GRAPH_UNAVAILABLE_DETAIL = "Database connection failed. Please try again later."
GEMINI_UNAVAILABLE_DETAIL = "AI service failed. Please try again later."

# Error code mapping: keyword → (error_code, recoverable)
_ERROR_CODE_MAP = {
    "429": ("RATE_LIMIT_EXCEEDED", True),
    "quota": ("RATE_LIMIT_EXCEEDED", True),
    "rate limit": ("RATE_LIMIT_EXCEEDED", True),
    "exhausted": ("RATE_LIMIT_EXCEEDED", True),
    "timeout": ("TIMEOUT", True),
    "timed out": ("TIMEOUT", True),
    "connection": ("SERVICE_UNAVAILABLE", True),
    "network": ("SERVICE_UNAVAILABLE", True),
    "database": ("DATABASE_ERROR", False),
    "db ": ("DATABASE_ERROR", False),
    "api key": ("CONFIG_ERROR", False),
    "authenticate": ("AUTH_ERROR", True),
    "unauthorized": ("AUTH_ERROR", True),
    "permission": ("AUTH_ERROR", False),
}

# Friendly user-facing messages
_FRIENDLY_MESSAGES = {
    "RATE_LIMIT_EXCEEDED": "Quá nhiều yêu cầu. Vui lòng chờ vài phút rồi thử lại.",
    "TIMEOUT": "Yêu cầu mất quá lâu. Vui lòng thử với tài liệu nhỏ hơn.",
    "SERVICE_UNAVAILABLE": "Dịch vụ AI tạm thời không khả dụng. Vui lòng thử lại sau.",
    "DATABASE_ERROR": "Lỗi lưu trữ dữ liệu. Vui lòng liên hệ hỗ trợ.",
    "CONFIG_ERROR": "Lỗi cấu hình hệ thống. Vui lòng kiểm tra API key.",
    "AUTH_ERROR": "Lỗi xác thực. Vui lòng đăng nhập lại.",
    "PROCESSING_ERROR": "Xử lý tài liệu gặp lỗi. Vui lòng thử lại.",
    "INTERNAL_ERROR": "Lỗi hệ thống nội bộ. Đã ghi log để kiểm tra.",
}


def _map_exception(exc: Exception) -> tuple[str, bool, str]:
    """Map exception to (error_code, recoverable, friendly_message)."""
    msg_lower = str(exc).lower()
    for key, (code, rec) in _ERROR_CODE_MAP.items():
        if key in msg_lower:
            return code, rec, _FRIENDLY_MESSAGES.get(code, str(exc)[:100])
    if isinstance(exc, RuntimeError):
        return "PROCESSING_ERROR", True, "Xử lý tài liệu gặp lỗi. Vui lòng thử lại."
    return "INTERNAL_ERROR", False, "Lỗi hệ thống. Đã ghi log để kiểm tra."


def _get_diag_logger():
    """Get the diagnostics logger defined in app.utils.diagnostic"""
    from app.utils.diagnostic import _get_diag_logger as get_actual_logger
    return get_actual_logger()


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


def _run_cognee_ingest(tmp_path: str, dataset_name: str) -> None:
    """Sync wrapper — runs the async cognee ingestion in a separate thread."""
    import asyncio
    asyncio.run(_cognee_ingest_async(tmp_path, dataset_name))


async def _cognee_ingest_async(tmp_path: str, dataset_name: str) -> None:
    from app.services.cognee_engine import ingest_document as cognee_ingest
    await cognee_ingest(tmp_path, dataset_name=dataset_name)


async def run_ingestion_task(task_id: str, tmp_path: str, dataset_name: str):
    """Background task: parse document → extract knowledge graph → save topics/edges."""
    import time
    import threading
    from app.services.document_parser import parse_document
    from app.services.graph_extractor import extract_knowledge_graph
    from app.services.factory import get_graph_service

    diag_logger = _get_diag_logger()
    start_time = time.time()
    stop_heartbeat = threading.Event()

    # Heartbeat milestones: elapsed_seconds → (progress, message)
    milestones = [
        (10, 30, "AI Analysis: Reading document segments..."),
        (30, 40, "AI Analysis: Extracting entities..."),
        (60, 55, "AI Analysis: Finding relationships..."),
        (120, 70, "AI Analysis: Processing concept graph..."),
        (180, 85, "AI Analysis: Finalizing extraction..."),
    ]

    def heartbeat_loop():
        while not stop_heartbeat.is_set():
            elapsed = time.time() - start_time
            msg = "AI Analysis: Still extracting knowledge graph..."
            prog = 25
            for t, p, m in milestones:
                if elapsed >= t:
                    prog = p
                    msg = m
            update_task_progress(task_id, prog, msg, "cognee_ingest")
            time.sleep(10)

    try:
        # ── Step 1: Parse document ──────────────────────────────────────────
        update_task_progress(task_id, 5, "Reading file...", "file_received")
        with open(tmp_path, "rb") as f:
            file_bytes = f.read()
        filename = os.path.basename(tmp_path)

        update_task_progress(task_id, 15, "Parsing document...", "parsing")
        chunks = parse_document(file_bytes, filename)
        update_task_progress(task_id, 22, f"Found {len(chunks)} text sections. Starting AI analysis...", "parsing")

        # ── Step 2: Extract knowledge graph (direct LLM, no Cognee) ─────────
        hb_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        hb_thread.start()

        try:
            diag_logger.info(f"Graph extraction START for {task_id} ({len(chunks)} chunks)")
            service = get_graph_service()
            doc_id = dataset_name.replace("doc_", "")
            result = await extract_knowledge_graph(chunks, doc_id)
            diag_logger.info(f"Graph extraction SUCCESS: {result}")
        except Exception as e:
            diag_logger.error(f"Graph extraction FAILED for {task_id}: {e}")
            raise
        finally:
            stop_heartbeat.set()
            hb_thread.join(timeout=1)

        # ── Step 3: Finalize ───────────────────────────────────────────────
        elapsed = time.time() - start_time
        topics_count = result.get("topics_created", 0)
        edges_count = result.get("edges_created", 0)
        update_task(task_id,
            status="completed",
            progress=100,
            message=f"Extracted {topics_count} topics, {edges_count} edges in {elapsed:.0f}s",
            result={
                "doc_id": doc_id,
                "filename": filename,
                "topics_extracted": topics_count,
                "edges_created": edges_count,
                "elapsed_seconds": round(elapsed, 1),
            }
        )


    except Exception as exc:
        error_id = str(uuid.uuid4())[:8]
        error_code, recoverable, friendly_msg = _map_exception(exc)

        diag_logger.error(
            f"[{error_id}] Ingestion task {task_id} FAILED\n"
            f"  Filename: {tmp_path}\n"
            f"  Error Code: {error_code}\n"
            f"  Recoverable: {recoverable}\n"
            f"  Exception: {type(exc).__name__}: {str(exc)}\n"
            f"  Traceback:\n{traceback.format_exc()}"
        )

        update_task(task_id,
            status="failed",
            progress=0,
            message=friendly_msg,
            error={
                "error_code": error_code,
                "detail": str(exc)[:200],
                "recoverable": recoverable,
                "log_id": error_id
            }
        )
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass


@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    subject: str = "general",
    current_user: dict = Depends(get_current_user),
):
    """Upload and ingest a document asynchronously to extract knowledge graph"""
    user_id = current_user["sub"]

    file_bytes = await file.read()
    file_size = len(file_bytes)
    
    if file_size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {settings.max_file_size_mb}MB",
        )

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

    # Save file to a temporary location for Cognee ingestion
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    # Create background task tracking
    task_id = create_task(doc_id, file.filename)

    # Add to background tasks — runs asynchronously, does NOT block this request
    background_tasks.add_task(run_ingestion_task, task_id, tmp_path, f"doc_{doc_id}")

    # Return 202 Accepted immediately — task runs in background
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "doc_id": doc_id,
            "filename": file.filename,
            "task_id": task_id,
            "status": "processing",
            "message": "Document queued. Poll GET /documents/tasks/{task_id} for progress.",
        },
    )


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_ingest_status(task_id: str, current_user: dict = Depends(get_current_user)):
    """Check the status of a background ingestion task"""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(**task)


@router.get("/tasks/{task_id}")
async def get_task_detail(task_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get detailed task information including step-by-step progress log.
    Used by UI for real-time progress bar updates.
    """
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


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
