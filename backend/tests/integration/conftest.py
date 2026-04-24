"""Fixtures for integration tests."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.document_parser import TextChunk


# ============================================================================
# Mock Neo4j Driver
# ============================================================================

class MockNeo4jSession:
    """Mock Neo4j session."""

    def __init__(self):
        self._data = {}
        self._queries = []

    def run(self, query, **params):
        """Mock run method."""
        self._queries.append((query, params))
        return MockResult(query, params, self._data)

    def close(self):
        """Mock close method."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class MockResult:
    """Mock Neo4j result."""

    def __init__(self, query, params, data_store):
        self.query = query
        self.params = params
        self.data_store = data_store
        self._single_data = None

    def single(self):
        """Return single record."""
        return self._single_data

    def __iter__(self):
        """Iterate over records."""
        return iter([])


@pytest.fixture
def mock_neo4j_session_factory():
    """Factory for creating mock Neo4j sessions."""
    def create_session(mock_data=None):
        session = MockNeo4jSession()
        if mock_data:
            session._data.update(mock_data)
        return session
    return create_session


@pytest.fixture
def mock_neo4j_driver(mock_neo4j_session_factory):
    """Mock Neo4j driver."""
    driver = MagicMock()

    def create_session():
        return mock_neo4j_session_factory()

    driver.session = MagicMock(side_effect=create_session)
    driver.close = MagicMock()

    return driver


@pytest.fixture
def mock_neo4j_service(mock_neo4j_driver):
    """Mock Neo4j service with injected driver."""
    with patch("app.services.neo4j_service.GraphDatabase") as mock_gdb:
        mock_gdb.driver.return_value = mock_neo4j_driver

        # Import after patching
        from app.services.neo4j_service import Neo4jService

        # Create instance with mocked driver
        service = Neo4jService.__new__(Neo4jService)
        service.driver = mock_neo4j_driver
        return service


# ============================================================================
# Mock Gemini LLM
# ============================================================================

@pytest.fixture
def mock_llm_response():
    """Factory for mock LLM responses."""
    def create_response(text: str):
        response = MagicMock()
        response.content = text
        return response
    return create_response


@pytest.fixture
def mock_gemini_llm(mock_llm_response):
    """Mock Gemini LLM."""
    llm = MagicMock()

    def invoke_side_effect(prompt):
        return mock_llm_response(
            '{"nodes": [{"name": "Test Topic", "type": "concept", "description": "Test description"}], "edges": []}'
        )

    llm.invoke = MagicMock(side_effect=invoke_side_effect)
    return llm


@pytest.fixture
def mock_gemini_llm_factory():
    """Factory for different LLM responses per test."""
    responses = {}

    def register_response(prompt_contains: str, response_json: str):
        responses[prompt_contains] = response_json

    def invoke(prompt: str):
        # Find matching response
        for key, response in responses.items():
            if key in prompt:
                return mock_llm_response(response)
        # Default response
        return mock_llm_response('{"nodes": [], "edges": []}')

    with patch("app.utils.gemini_client.get_llm") as mock:
        mock.return_value = MagicMock(invoke=invoke)
        yield register_response


# ============================================================================
# Sample Data
# ============================================================================

@pytest.fixture
def sample_entities():
    """Sample extracted entities."""
    return [
        {"name": "Hàm số bậc hai", "type": "concept", "description": "Dạng y = ax^2 + bx + c", "difficulty": "medium"},
        {"name": "Parabol", "type": "concept", "description": "Đồ thị hàm bậc hai", "difficulty": "medium"},
        {"name": "Đỉnh parabol", "type": "concept", "description": "Điểm cao nhất/thấp nhất", "difficulty": "hard"},
    ]


@pytest.fixture
def sample_relations():
    """Sample extracted relations."""
    return [
        {"from_name": "Parabol", "to_name": "Hàm số bậc hai", "relation": "relatedTo", "weight": 1.0},
        {"from_name": "Đỉnh parabol", "to_name": "Parabol", "relation": "contains", "weight": 1.0},
    ]


@pytest.fixture
def sample_chunks_for_extraction():
    """Sample text chunks for graph extraction."""
    return [
        TextChunk(text="Hàm số bậc hai có dạng y = ax^2 + bx + c, với a ≠ 0. Đồ thị của nó là một parabol.", page_number=1, char_count=100),
        TextChunk(text="Parabol có đỉnh là điểm có tọa độ (-b/2a, -Δ/4a).", page_number=2, char_count=80),
        TextChunk(text="Đỉnh parabol là điểm đặc biệt dùng để vẽ đồ thị.", page_number=3, char_count=60),
    ]