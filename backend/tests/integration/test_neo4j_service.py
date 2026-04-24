"""Integration tests for Neo4j service."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import List, Dict, Any


class MockSession:
    """Mock Neo4j session for testing."""

    def __init__(self):
        self.data = {}
        self.queries = []

    def run(self, query: str, **params):
        """Mock run - store query and params."""
        self.queries.append((query, params))
        return self._create_result(query, params)

    def _create_result(self, query, params):
        """Create mock result based on query type."""
        result = MagicMock()
        result.single = MagicMock(return_value=self._get_single_result(query, params))
        result.__iter__ = MagicMock(return_value=iter(self._get_iter_results(query, params)))
        return result

    def _get_single_result(self, query, params):
        """Get single result based on query."""
        if "MATCH (u:User {email:" in query:
            email = params.get("email")
            if email == "existing@test.com":
                return {"u": {"id": "user-1", "email": email, "name": "Test User"}}
            return None
        elif "MATCH (u:User {id:" in query:
            user_id = params.get("user_id")
            if user_id == "user-1":
                return {"u": {"id": user_id, "email": "test@test.com", "name": "Test"}}
            return None
        return None

    def _get_iter_results(self, query, params):
        """Get iterable results."""
        if "MATCH (d:Document {user_id:" in query:
            return [
                {"id": "doc-1", "filename": "test.pdf", "uploaded_at": "2024-01-01"},
                {"id": "doc-2", "filename": "test2.pdf", "uploaded_at": "2024-01-02"},
            ]
        elif "MATCH (d:Document {id:" in query and "FROM_DOC" in query:
            return [
                {"id": "topic-1", "name": "Topic 1", "description": "Desc 1"},
                {"id": "topic-2", "name": "Topic 2", "description": "Desc 2"},
            ]
        return []

    def close(self):
        """Mock close."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


@pytest.fixture
def mock_driver():
    """Create mock Neo4j driver."""
    driver = MagicMock()

    def create_session():
        session = MockSession()
        return session

    driver.session = MagicMock(side_effect=create_session)
    driver.close = MagicMock()
    return driver


@pytest.fixture
def neo4j_service_with_mock(mock_driver):
    """Neo4jService with mock driver."""
    from app.services import neo4j_service as module

    # Save original
    original_service = module._neo4j_service
    original_driver = None

    # Create mock service
    with patch.object(module, "GraphDatabase") as mock_gdb:
        mock_gdb.driver.return_value = mock_driver

        # Create service instance directly
        service = module.Neo4jService.__new__(module.Neo4jService)
        service.driver = mock_driver

        # Mock _ensure_constraints to avoid running on test
        service._ensure_constraints = MagicMock()

        yield service

        # Restore
        module._neo4j_service = original_service


class TestNeo4jServiceDocuments:
    """Tests for document operations."""

    def test_create_document_returns_id(self, neo4j_service_with_mock):
        """Should return a document ID."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        doc_id = neo4j_service_with_mock.create_document("test.pdf", "user-1")
        assert doc_id is not None
        assert isinstance(doc_id, str)

    def test_create_document_stores_query(self, neo4j_service_with_mock):
        """Should execute create query."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        neo4j_service_with_mock.create_document("test.pdf", "user-1")

        assert len(session.queries) > 0
        assert "CREATE (d:Document" in session.queries[0][0]

    def test_get_documents_by_user_returns_list(self, neo4j_service_with_mock):
        """Should return list of documents."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        docs = neo4j_service_with_mock.get_documents_by_user("user-1")
        assert isinstance(docs, list)

    def test_get_documents_by_user_orders_by_date(self, neo4j_service_with_mock):
        """Should order by uploaded_at descending."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        neo4j_service_with_mock.get_documents_by_user("user-1")

        query = session.queries[0][0]
        assert "ORDER BY d.uploaded_at DESC" in query


class TestNeo4jServiceTopics:
    """Tests for topic operations."""

    def test_upsert_topic_returns_id(self, neo4j_service_with_mock):
        """Should return topic ID."""
        mock_result = MagicMock()
        mock_result.single.return_value = {"id": "topic-123"}

        session = MockSession()
        session.run = MagicMock(return_value=mock_result)

        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        topic_id = neo4j_service_with_mock.upsert_topic(
            name="Test Topic",
            description="Test desc",
            subject="toan"
        )

        assert topic_id == "topic-123"

    def test_upsert_topic_uses_merge(self, neo4j_service_with_mock):
        """Should use MERGE to avoid duplicates."""
        mock_result = MagicMock()
        mock_result.single.return_value = {"id": "topic-123"}

        session = MockSession()
        original_run = session.run
        def wrapped_run(query, **params):
            original_run(query, **params)
            return mock_result
        session.run = MagicMock(side_effect=wrapped_run)

        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        neo4j_service_with_mock.upsert_topic(name="Test Topic")

        assert len(session.queries) > 0
        query = session.queries[0][0]
        assert "MERGE (t:Topic" in query

    def test_upsert_topic_links_to_document(self, neo4j_service_with_mock):
        """Should link topic to document when doc_id provided."""
        mock_result = MagicMock()
        mock_result.single.return_value = {"id": "topic-123"}

        session = MockSession()
        original_run = session.run
        def wrapped_run(query, **params):
            original_run(query, **params)
            return mock_result
        session.run = MagicMock(side_effect=wrapped_run)

        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        neo4j_service_with_mock.upsert_topic(
            name="Test Topic",
            doc_id="doc-123"
        )

        # Should have at least 2 queries: MERGE topic + MATCH/MERGE edge
        assert len(session.queries) >= 2

    def test_get_topics_by_document(self, neo4j_service_with_mock):
        """Should return topics linked to document."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        topics = neo4j_service_with_mock.get_topics_by_document("doc-123")
        assert isinstance(topics, list)

    def test_get_all_topics(self, neo4j_service_with_mock):
        """Should return all topics."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        topics = neo4j_service_with_mock.get_all_topics()

        assert len(session.queries) > 0
        query = session.queries[0][0]
        assert "MATCH (t:Topic)" in query


class TestNeo4jServiceUsers:
    """Tests for user operations."""

    def test_create_user(self, neo4j_service_with_mock):
        """Should create user node."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        result = neo4j_service_with_mock.create_user(
            user_id="user-123",
            email="test@test.com",
            name="Test User",
            hashed_password="hashed"
        )

        assert result is True
        query = session.queries[0][0]
        assert "CREATE (u:User" in query

    def test_get_user_by_email_found(self, neo4j_service_with_mock):
        """Should return user when found."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        user = neo4j_service_with_mock.get_user_by_email("existing@test.com")
        assert user is not None
        assert user["email"] == "existing@test.com"

    def test_get_user_by_email_not_found(self, neo4j_service_with_mock):
        """Should return None when not found."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        user = neo4j_service_with_mock.get_user_by_email("notfound@test.com")
        assert user is None

    def test_get_user_by_id(self, neo4j_service_with_mock):
        """Should get user by ID."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        user = neo4j_service_with_mock.get_user_by_id("user-1")
        assert user is not None


class TestNeo4jServiceQuiz:
    """Tests for quiz operations."""

    def test_save_quiz(self, neo4j_service_with_mock):
        """Should save quiz with questions."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        questions = [
            {"text": "Q1", "type": "mc", "correct_answer": "A"},
            {"text": "Q2", "type": "mc", "correct_answer": "B"},
        ]

        result = neo4j_service_with_mock.save_quiz("quiz-1", "topic-1", questions)

        assert result is True
        # Should create Quiz node + Question nodes
        assert len(session.queries) >= 2

    def test_get_quiz_by_topic(self, neo4j_service_with_mock):
        """Should get quiz by topic ID."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        quiz = neo4j_service_with_mock.get_quiz_by_topic("topic-1")
        # Returns None if no quiz found
        assert quiz is None or isinstance(quiz, dict)

    def test_get_quiz(self, neo4j_service_with_mock):
        """Should get quiz by quiz ID."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        quiz = neo4j_service_with_mock.get_quiz("quiz-1")
        assert quiz is None or isinstance(quiz, dict)


class TestNeo4jServiceProgress:
    """Tests for progress operations."""

    def test_upsert_progress(self, neo4j_service_with_mock):
        """Should upsert user progress."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        result = neo4j_service_with_mock.upsert_progress("user-1", "topic-1", 2)

        assert result is True
        query = session.queries[0][0]
        assert "MERGE (u)" in query
        assert "HAS_PROGRESS" in query

    def test_get_user_progress(self, neo4j_service_with_mock):
        """Should get all user progress."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        progress = neo4j_service_with_mock.get_user_progress("user-1")

        assert isinstance(progress, list)


class TestNeo4jServiceLearningPath:
    """Tests for learning path operations."""

    def test_save_learning_path(self, neo4j_service_with_mock):
        """Should save learning path."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        path_json = '{"path": [{"topic_id": "t1", "priority": 1}]}'
        result = neo4j_service_with_mock.save_learning_path("user-1", path_json)

        assert result is True
        query = session.queries[0][0]
        assert "HAS_PATH" in query

    def test_get_learning_path(self, neo4j_service_with_mock):
        """Should get learning path."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        path = neo4j_service_with_mock.get_learning_path("user-1")
        assert path is None or isinstance(path, dict)

    def test_invalidate_learning_path(self, neo4j_service_with_mock):
        """Should delete learning path."""
        session = MockSession()
        neo4j_service_with_mock.driver.session = MagicMock()
        neo4j_service_with_mock.driver.session.return_value.__enter__.return_value = session

        result = neo4j_service_with_mock.invalidate_learning_path("user-1")

        assert result is True
        query = session.queries[0][0]
        assert "DELETE" in query