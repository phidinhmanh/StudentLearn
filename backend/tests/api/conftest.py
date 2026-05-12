"""Fixtures for API tests."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Dict, List

import pytest
from httpx import AsyncClient, ASGITransport

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def mock_service():
    """Mock service with in-memory user store and async-compatible methods for API tests.
    
    This single mock replaces neo4j_service, user_service, quiz_service, and progress_service
    to simplify testing.
    """
    from datetime import datetime
    
    mock = MagicMock()
    
    # Simple in-memory store for the mock
    users = {}
    documents = {
        "doc-123": {
            "id": "doc-123",
            "filename": "test.pdf",
            "user_id": None,
            "uploaded_at": datetime.utcnow()
        }
    }

    # Use AsyncMocks for all methods that are 'await'ed in routers
    # User operations
    async def mock_create_user(user_id, email, name, hashed_password):
        user = {
            "id": user_id,
            "email": email,
            "name": name,
            "hashed_password": hashed_password,
        }
        users[email] = user
        for doc in documents.values():
            if doc["user_id"] is None:
                doc["user_id"] = user_id
        return True

    async def mock_get_user_by_email(email):
        return users.get(email)

    async def mock_get_user_by_id(user_id):
        for u in users.values():
            if u["id"] == user_id:
                return u
        return None

    async def mock_get_document(doc_id):
        return documents.get(doc_id)

    async def mock_get_documents_by_user(user_id):
        return [doc for doc in documents.values() if doc["user_id"] == user_id]

    # Assign as AsyncMocks
    mock.create_user = AsyncMock(side_effect=mock_create_user)
    mock.get_user_by_email = AsyncMock(side_effect=mock_get_user_by_email)
    mock.get_user_by_id = AsyncMock(side_effect=mock_get_user_by_id)
    mock.get_document = AsyncMock(side_effect=mock_get_document)
    mock.get_documents_by_user = AsyncMock(side_effect=mock_get_documents_by_user)
    
    # Other services (Topic, Quiz, Progress, Path)
    mock.get_topics_by_document = AsyncMock(return_value=[])
    mock.upsert_topic = AsyncMock(return_value="topic-123")
    mock.upsert_edge = AsyncMock(return_value=True)
    mock.get_all_topics = AsyncMock(return_value=[])
    mock.get_topic_with_neighbors = AsyncMock(return_value=None)
    mock.save_quiz = AsyncMock(return_value=True)
    mock.get_quiz_by_topic = AsyncMock(return_value=None)
    mock.get_quiz = AsyncMock(return_value=None)
    mock.upsert_progress = AsyncMock(return_value=True)
    mock.get_user_progress = AsyncMock(return_value=[])
    mock.save_learning_path = AsyncMock(return_value=True)
    mock.get_learning_path = AsyncMock(return_value=None)
    mock.invalidate_learning_path = AsyncMock(return_value=True)
    
    # Health & Connection
    mock.get_connection_status = AsyncMock(return_value={"status": "ok", "graph_provider": "cognee", "connection": "connected"})
    mock.batch_upsert_topics = AsyncMock(return_value=[])
    mock.batch_upsert_edges = AsyncMock(return_value=0)
    
    # In-memory helper for fixtures (sync access)
    mock._users = users 
    
    return mock


from contextlib import ExitStack

def _mock_service_patches(mock_service):
    """Patch the factory's singletons."""
    import app.services.factory as factory_module

    original_graph = factory_module._graph_service
    original_user = factory_module._user_service
    original_quiz = factory_module._quiz_service
    original_progress = factory_module._progress_service

    factory_module._graph_service = mock_service
    factory_module._user_service = mock_service
    factory_module._quiz_service = mock_service
    factory_module._progress_service = mock_service

    class _PatchContext:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            factory_module._graph_service = original_graph
            factory_module._user_service = original_user
            factory_module._quiz_service = original_quiz
            factory_module._progress_service = original_progress

    return _PatchContext()


@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    from app.main import app as main_app
    return main_app


@pytest.fixture
async def async_client(app, mock_service):
    """Create async HTTP client for testing."""
    with _mock_service_patches(mock_service):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture
async def auth_client(app, mock_service):
    """Create authenticated client."""
    with _mock_service_patches(mock_service):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            email = "apitest@example.com"
            reg_response = await client.post("/api/v1/auth/register", json={
                "email": email,
                "password": "testpassword123",
                "name": "API Test User"
            })

            if reg_response.status_code in [200, 201]:
                token = reg_response.json().get("access_token", "")
                client.headers["Authorization"] = f"Bearer {token}"
                # Sync access to the store via helper
                user = mock_service._users.get(email)
                client.user_id = user["id"] if user else "user-123"
            else:
                client.headers["Authorization"] = "Bearer mock-token"
                client.user_id = "user-123"

            yield client


@pytest.fixture
def sample_quiz_answers() -> List[Dict]:
    return [
        {"question_id": "q1", "answer": "A"},
        {"question_id": "q2", "answer": "B"},
    ]


@pytest.fixture(autouse=True)
def mock_gemini_global():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content='{"nodes": [{"name": "Test Topic", "type": "concept"}], "edges": []}'
    )
    with patch("app.utils.gemini_client.get_llm", return_value=mock_llm), \
         patch("app.services.graph_extractor.get_llm", return_value=mock_llm), \
         patch("app.services.quiz_generator.get_llm", return_value=mock_llm), \
         patch("app.services.learning_path_engine.get_llm", return_value=mock_llm):
        yield mock_llm


@pytest.fixture(autouse=True)
def mock_document_parsers():
    from app.services.document_parser import TextChunk
    mock_chunks = [TextChunk(text="Mock content", page_number=1, char_count=12)]
    with patch("app.services.document_parser.parse_pdf", return_value=mock_chunks), \
         patch("app.services.document_parser.parse_docx", return_value=mock_chunks), \
         patch("app.services.document_parser.parse_txt", return_value=mock_chunks):
        yield


@pytest.fixture
def sample_progress_update() -> Dict:
    return {"skill_level": 2}
