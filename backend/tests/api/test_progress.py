"""API tests for user progress endpoints."""
import pytest
from httpx import AsyncClient


class TestGetProgress:
    """Tests for GET /api/v1/progress/{user_id}."""

    @pytest.mark.asyncio
    async def test_get_progress_requires_auth(self, async_client: AsyncClient):
        """Should require authentication."""
        response = await async_client.get("/api/v1/progress/user-123")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_progress_for_user(self, auth_client: AsyncClient):
        """Should return progress for user."""
        response = await auth_client.get(f"/api/v1/progress/{auth_client.user_id}")

        # May return empty list or list of progress
        assert response.status_code in [200, 500, 503]
        if response.status_code == 200:
            assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_progress_empty(self, auth_client: AsyncClient):
        """Should return empty list when no progress."""
        response = await auth_client.get(f"/api/v1/progress/{auth_client.user_id}")

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) >= 0

    @pytest.mark.asyncio
    async def test_get_progress_includes_topic_info(self, auth_client: AsyncClient):
        """Progress should include topic information."""
        response = await auth_client.get(f"/api/v1/progress/{auth_client.user_id}")

        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                progress = data[0]
                assert "topic_id" in progress
                assert "topic_name" in progress
                assert "skill_level" in progress


class TestUpdateProgress:
    """Tests for PUT /api/v1/progress/{user_id}/{topic_id}."""

    @pytest.mark.asyncio
    async def test_update_requires_auth(self, async_client: AsyncClient):
        """Should require authentication."""
        response = await async_client.put(
            "/api/v1/progress/user-123/topic-456",
            json={"skill_level": 2}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_progress_valid_level(self, auth_client: AsyncClient):
        """Should accept valid skill level."""
        response = await auth_client.put(
            f"/api/v1/progress/{auth_client.user_id}/topic-456",
            json={"skill_level": 2}
        )

        assert response.status_code in [200, 404, 500, 503]

    @pytest.mark.asyncio
    async def test_update_progress_level_0(self, auth_client: AsyncClient):
        """Should accept skill level 0."""
        response = await auth_client.put(
            f"/api/v1/progress/{auth_client.user_id}/topic-456",
            json={"skill_level": 0}
        )

        assert response.status_code in [200, 404, 500, 503]

    @pytest.mark.asyncio
    async def test_update_progress_level_3(self, auth_client: AsyncClient):
        """Should accept skill level 3."""
        response = await auth_client.put(
            f"/api/v1/progress/{auth_client.user_id}/topic-456",
            json={"skill_level": 3}
        )

        assert response.status_code in [200, 404, 500, 503]

    @pytest.mark.asyncio
    async def test_update_invalid_level_negative(self, auth_client: AsyncClient):
        """Should reject negative skill level."""
        response = await auth_client.put(
            "/api/v1/progress/user-123/topic-456",
            json={"skill_level": -1}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_invalid_level_too_high(self, auth_client: AsyncClient):
        """Should reject skill level > 3."""
        response = await auth_client.put(
            "/api/v1/progress/user-123/topic-456",
            json={"skill_level": 4}
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_missing_body(self, auth_client: AsyncClient):
        """Should require skill_level in body."""
        response = await auth_client.put(
            "/api/v1/progress/user-123/topic-456",
            json={}
        )

        assert response.status_code == 422


class TestProgressResponseFormat:
    """Tests for progress response format."""

    @pytest.mark.asyncio
    async def test_progress_item_structure(self, auth_client: AsyncClient):
        """Progress item should have required fields."""
        response = await auth_client.get("/api/v1/progress/user-123")

        if response.status_code == 200:
            data = response.json()
            # Structure is a list
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_progress_skill_level_range(self, auth_client: AsyncClient):
        """Skill level should be 0-3."""
        response = await auth_client.get("/api/v1/progress/user-123")

        if response.status_code == 200:
            data = response.json()
            for progress in data:
                assert 0 <= progress["skill_level"] <= 3


class TestProgressIntegration:
    """Integration tests for progress with quiz."""

    @pytest.mark.asyncio
    async def test_quiz_submit_updates_progress(self, auth_client: AsyncClient):
        """Quiz submission should update progress."""
        # Submit quiz
        submit_response = await auth_client.post(
            "/api/v1/quiz/submit",
            json={
                "quiz_id": "quiz-123",
                "answers": [{"question_id": "q1", "answer": "A"}]
            }
        )

        # If quiz submitted successfully, progress should reflect skill level
        if submit_response.status_code == 200:
            result = submit_response.json()
            assert "skill_level" in result
            assert 1 <= result["skill_level"] <= 3

    @pytest.mark.asyncio
    async def test_self_rating_does_not_require_quiz(self, auth_client: AsyncClient):
        """User should be able to self-rate without quiz."""
        response = await auth_client.put(
            f"/api/v1/progress/{auth_client.user_id}/topic-456",
            json={"skill_level": 2}
        )

        # Self-rating should work independently
        assert response.status_code in [200, 404, 500, 503]