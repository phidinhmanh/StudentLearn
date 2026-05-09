# Mock xxhash before any langchain import — Windows WDAC blocks the C extension
import sys
from types import ModuleType
if "xxhash" not in sys.modules:
    xxhash_mock = ModuleType("xxhash")
    xxhash_mock.xxh32 = lambda *a, **k: None
    xxhash_mock.xxh32_digest = lambda *a, **k: b"\x00" * 4
    xxhash_mock.xxh64 = lambda *a, **k: None
    xxhash_mock.xxh64_digest = lambda *a, **k: b"\x00" * 8
    xxhash_mock.xxh64_intdigest = lambda *a, **k: 0
    sys.modules["xxhash"] = xxhash_mock
    sys.modules["xxhash._xxhash"] = xxhash_mock

if "langsmith._internal._uuid" not in sys.modules:
    ls_uuid_mock = ModuleType("langsmith._internal._uuid")
    ls_uuid_mock.uuid7 = lambda *a, **k: None
    ls_uuid_mock.uuid7_deterministic = lambda *a, **k: None
    sys.modules["langsmith._internal._uuid"] = ls_uuid_mock

from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json

from app.auth.router import router as auth_router
from app.auth.dependencies import get_current_user
from app.models.schemas import DiagnosticResponse
from app.routers import documents, quiz, learning_path, user_progress, graph_rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting StudentLearning GraphRAG API...")
    yield
    # Shutdown
    from app.services.factory import get_graph_service
    service = get_graph_service()
    if hasattr(service, "close"):
        await service.close()
    print("Shutting down...")


app = FastAPI(
    title="StudentLearn AI",
    description="GraphRAG system for personalized learning with Cognee and Gemini",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(quiz.router, prefix="/api/v1")
app.include_router(learning_path.router, prefix="/api/v1")
app.include_router(user_progress.router, prefix="/api/v1")
app.include_router(graph_rag.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    from app.services.factory import get_graph_service
    service = get_graph_service()
    status_info = await service.get_connection_status()

    overall_status = "ok" if status_info["status"] == "connected" else "degraded"

    return {
        "status": overall_status,
        "service": "StudentLearning GraphRAG",
        "graph_provider": status_info.get("provider", "unknown"),
        "connection": status_info
    }


@app.get("/api/v1/health/diagnostic", response_model=DiagnosticResponse)
async def diagnostic(current_user: dict = Depends(get_current_user)):
    from app.utils.diagnostic import check_all
    return await check_all()


@app.get("/api/v1/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml():
    """Serve OpenAPI spec as downloadable YAML file."""
    from fastapi.responses import PlainTextResponse
    try:
        import yaml
        return PlainTextResponse(
            yaml.safe_dump(app.openapi()),
            media_type="application/x-yaml"
        )
    except ImportError:
        return Response(
            content=json.dumps(app.openapi(), ensure_ascii=False, indent=2),
            media_type="application/json"
        )


@app.get("/")
async def root():
    return {
        "message": "StudentLearning GraphRAG API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }