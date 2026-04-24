"""Fixtures for API tests."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Dict, List

import pytest
from httpx import AsyncClient, ASGITransport

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def mock_neo4j():
    """Mock Neo4j service with in-memory user store for API tests."""
    mock = MagicMock()

    from datetime import datetime
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

    def mock_create_user(user_id, email, name, hashed_password):
        user = {
            "id": user_id,
            "email": email,
            "name": name,
            "hashed_password": hashed_password,
        }
        users[email] = user
        # Assign existing mock docs to the first user created for convenience in tests
        for doc in documents.values():
            if doc["user_id"] is None:
                doc["user_id"] = user_id
        return True

    def mock_create_document(filename, user_id):
        doc_id = f"doc-{len(documents) + 1}"
        documents[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "user_id": user_id,
            "uploaded_at": datetime.utcnow()
        }
        return doc_id

    def mock_get_user_by_email(email):
        return users.get(email)

    def mock_get_user_by_id(user_id):
        for u in users.values():
            if u["id"] == user_id:
                return u
        return None

    def mock_get_document(doc_id):
        return documents.get(doc_id)

    def mock_get_documents_by_user(user_id):
        return [doc for doc in documents.values() if doc["user_id"] == user_id]

    # User operations (in-memory)
    mock.create_user.side_effect = mock_create_user
    mock.create_document.side_effect = mock_create_document
    mock.get_user_by_email.side_effect = mock_get_user_by_email
    mock.get_user_by_id.side_effect = mock_get_user_by_id
    mock.get_document.side_effect = mock_get_document
    mock.get_documents_by_user.side_effect = mock_get_documents_by_user
    mock.get_topics_by_document.return_value = []

    # Topic operations
    mock.upsert_topic.return_value = "topic-123"
    mock.upsert_edge.return_value = True
    mock.get_all_topics.return_value = []
    mock.get_topic_with_neighbors.return_value = None

    # Quiz operations
    mock.save_quiz.return_value = True
    mock.get_quiz_by_topic.return_value = None
    mock.get_quiz.return_value = None

    # Progress operations
    mock.upsert_progress.return_value = True
    mock.get_user_progress.return_value = []

    # Learning path operations
    mock.save_learning_path.return_value = True
    mock.get_learning_path.return_value = None
    mock.invalidate_learning_path.return_value = True

    return mock


from contextlib import ExitStack

def _neo4j_patches(mock_neo4j):
    """Patch get_neo4j_service by directly setting the singleton."""
    import app.services.neo4j_service as neo4j_module

    # Save original
    original_service = neo4j_module._neo4j_service

    # Set mock as the singleton so all get_neo4j_service() calls return it
    neo4j_module._neo4j_service = mock_neo4j

    class _PatchContext:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            neo4j_module._neo4j_service = original_service

    return _PatchContext()


@pytest.fixture
def app():
    """Create FastAPI app for testing."""
    from app.main import app as main_app
    return main_app


@pytest.fixture
async def async_client(app, mock_neo4j):
    """Create async HTTP client for testing."""
    with _neo4j_patches(mock_neo4j):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture
async def auth_client(app, mock_neo4j):
    """Create authenticated client."""
    with _neo4j_patches(mock_neo4j):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Register (mock supports in-memory user store)
            email = "apitest@example.com"
            reg_response = await client.post("/api/v1/auth/register", json={
                "email": email,
                "password": "testpassword123",
                "name": "API Test User"
            })

            if reg_response.status_code in [200, 201]:
                token = reg_response.json().get("access_token", "")
                client.headers["Authorization"] = f"Bearer {token}"
                # Store user_id in client for tests to use
                user = mock_neo4j.get_user_by_email(email)
                client.user_id = user["id"]

            yield client


@pytest.fixture
def sample_quiz_answers() -> List[Dict]:
    """Sample quiz answers."""
    return [
        {"question_id": "q1", "answer": "A"},
        {"question_id": "q2", "answer": "B"},
    ]


@pytest.fixture(autouse=True)
def mock_gemini_global():
    """Globally mock LLM to avoid real API calls in any test."""
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

    """Mock document parsers to avoid complex format handling in API tests."""
    from app.services.document_parser import TextChunk
    mock_chunks = [TextChunk(text="Mock content", page_number=1, char_count=12)]

    with patch("app.services.document_parser.parse_pdf", return_value=mock_chunks), \
         patch("app.services.document_parser.parse_docx", return_value=mock_chunks), \
         patch("app.services.document_parser.parse_txt", return_value=mock_chunks):
        yield


@pytest.fixture
def sample_progress_update() -> Dict:
    """Sample progress update."""
    return {"skill_level": 2}
