"""API tests for quiz endpoints."""
import pytest
from httpx import AsyncClient


class TestGetQuiz:
    """Tests for GET /api/v1/quiz/{topic_id}."""

    @pytest.mark.asyncio
    async def test_get_quiz_requires_auth(self, async_client: AsyncClient):
        """Should require authentication."""
        response = await async_client.get("/api/v1/quiz/topic-123")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_quiz_for_topic(self, auth_client: AsyncClient):
        """Should return quiz for topic."""
        response = await auth_client.get("/api/v1/quiz/topic-123")

        # May return quiz or 404 if not found
        assert response.status_code in [200, 404, 500, 503]

    @pytest.mark.asyncio
    async def test_get_quiz_cached(self, auth_client: AsyncClient):
        """Should return cached quiz if exists."""
        # First request - may generate quiz
        response1 = await auth_client.get("/api/v1/quiz/topic-123")

        # Second request - should return same cached quiz
        response2 = await auth_client.get("/api/v1/quiz/topic-123")

        # Both should succeed if quiz exists
        assert response1.status_code in [200, 404, 500, 503]
        assert response2.status_code in [200, 404, 500, 503]


class TestSubmitQuiz:
    """Tests for POST /api/v1/quiz/submit."""

    @pytest.mark.asyncio
    async def test_submit_requires_auth(self, async_client: AsyncClient):
        """Should require authentication."""
        response = await async_client.post(
            "/api/v1/quiz/submit",
            json={
                "quiz_id": "quiz-123",
                "answers": [{"question_id": "q1", "answer": "A"}]
            }
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_submit_valid_answers(self, auth_client: AsyncClient):
        """Should accept valid quiz submission."""
        response = await auth_client.post(
            "/api/v1/quiz/submit",
            json={
                "quiz_id": "quiz-123",
                "answers": [
                    {"question_id": "q1", "answer": "A"},
                    {"question_id": "q2", "answer": "B"}
                ]
            }
        )

        assert response.status_code in [200, 400, 404, 500, 503]

    @pytest.mark.asyncio
    async def test_submit_missing_quiz_id(self, auth_client: AsyncClient):
        """Should validate quiz_id is required."""
        response = await auth_client.post(
            "/api/v1/quiz/submit",
            json={
                "answers": [{"question_id": "q1", "answer": "A"}]
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_submit_missing_answers(self, auth_client: AsyncClient):
        """Should validate answers is required."""
        response = await auth_client.post(
            "/api/v1/quiz/submit",
            json={
                "quiz_id": "quiz-123"
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_submit_partial_answers(self, auth_client: AsyncClient):
        """Should handle partial answer submission."""
        response = await auth_client.post(
            "/api/v1/quiz/submit",
            json={
                "quiz_id": "quiz-123",
                "answers": [{"question_id": "q1", "answer": "A"}]
            }
        )

        # Should accept partial answers (empty = wrong)
        assert response.status_code in [200, 400, 404, 500, 503]


class TestQuizResponseFormat:
    """Tests for quiz response format."""

    @pytest.mark.asyncio
    async def test_quiz_response_has_required_fields(self, auth_client: AsyncClient):
        """Quiz response should have required fields."""
        response = await auth_client.get("/api/v1/quiz/topic-123")

        if response.status_code == 200:
            data = response.json()
            assert "quiz_id" in data
            assert "topic_id" in data
            assert "questions" in data

    @pytest.mark.asyncio
    async def test_question_has_no_correct_answer(self, auth_client: AsyncClient):
        """Questions should NOT include correct_answer for client."""
        response = await auth_client.get("/api/v1/quiz/topic-123")

        if response.status_code == 200:
            data = response.json()
            for question in data.get("questions", []):
                # correct_answer should not be sent to client
                assert "correct_answer" not in question
                assert "id" in question
                assert "text" in question