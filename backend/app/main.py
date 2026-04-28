from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.auth.router import router as auth_router
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


@app.get("/")
async def root():
    return {
        "message": "StudentLearning GraphRAG API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }