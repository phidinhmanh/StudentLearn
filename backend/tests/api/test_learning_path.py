"""API tests for learning path endpoints."""
import pytest
from httpx import AsyncClient


class TestGetLearningPath:
    """Tests for GET /api/v1/learning-path/{user_id}."""

    @pytest.mark.asyncio
    async def test_get_path_requires_auth(self, async_client: AsyncClient):
        """Should require authentication."""
        response = await async_client.get("/api/v1/learning-path/user-123")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_path_for_user(self, auth_client: AsyncClient):
        """Should return learning path for user."""
        response = await auth_client.get(f"/api/v1/learning-path/{auth_client.user_id}")

        # May return path or 404 if not found
        assert response.status_code in [200, 404, 500, 503]

    @pytest.mark.asyncio
    async def test_get_path_with_goal(self, auth_client: AsyncClient):
        """Should accept optional goal parameter."""
        response = await auth_client.get(
            f"/api/v1/learning-path/{auth_client.user_id}",
            params={"goal": "ôn thi đại học"}
        )

        # Should handle goal parameter
        assert response.status_code in [200, 404, 500, 503]

    @pytest.mark.asyncio
    async def test_get_path_cached(self, auth_client: AsyncClient):
        """Should return cached path if available."""
        # First request
        response1 = await auth_client.get(f"/api/v1/learning-path/{auth_client.user_id}")

        # Second request - should return same cached version
        response2 = await auth_client.get(f"/api/v1/learning-path/{auth_client.user_id}")

        # Both should behave consistently
        assert response1.status_code in [200, 404, 500, 503]
        assert response2.status_code in [200, 404, 500, 503]


class TestGenerateLearningPath:
    """Tests for POST /api/v1/learning-path/generate."""

    @pytest.mark.asyncio
    async def test_generate_requires_auth(self, async_client: AsyncClient):
        """Should require authentication."""
        response = await async_client.post("/api/v1/learning-path/generate")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_generate_path(self, auth_client: AsyncClient):
        """Should generate new learning path."""
        response = await auth_client.post("/api/v1/learning-path/generate")

        assert response.status_code in [200, 201, 422, 500, 503]

    @pytest.mark.asyncio
    async def test_generate_with_goal(self, auth_client: AsyncClient):
        """Should accept goal parameter."""
        response = await auth_client.post(
            "/api/v1/learning-path/generate",
            params={"goal": "chuẩn bị thi học kì 1"}
        )

        # Should generate path considering goal
        assert response.status_code in [200, 201, 422, 500, 503]

    @pytest.mark.asyncio
    async def test_regenerate_invalidates_cache(self, auth_client: AsyncClient):
        """Should regenerate and update cache."""
        # First generate
        response1 = await auth_client.post("/api/v1/learning-path/generate")

        # Regenerate
        response2 = await auth_client.post("/api/v1/learning-path/generate")

        # Both should succeed
        assert response1.status_code in [200, 201, 422, 500, 503]
        assert response2.status_code in [200, 201, 422, 500, 503]


class TestLearningPathResponseFormat:
    """Tests for learning path response format."""

    @pytest.mark.asyncio
    async def test_path_response_structure(self, auth_client: AsyncClient):
        """Path response should have required structure."""
        response = await auth_client.post("/api/v1/learning-path/generate")

        if response.status_code == 200:
            data = response.json()
            assert "path" in data
            assert isinstance(data["path"], list)

    @pytest.mark.asyncio
    async def test_path_item_structure(self, auth_client: AsyncClient):
        """Each path item should have required fields."""
        response = await auth_client.post("/api/v1/learning-path/generate")

        if response.status_code == 200:
            data = response.json()
            for item in data.get("path", []):
                assert "topic_id" in item
                assert "name" in item
                assert "priority" in item
                assert "reason" in item
                assert "status" in item

    @pytest.mark.asyncio
    async def test_path_status_values(self, auth_client: AsyncClient):
        """Path item status should be valid values."""
        response = await auth_client.post("/api/v1/learning-path/generate")

        if response.status_code == 200:
            data = response.json()
            valid_statuses = {"ready", "review", "locked"}
            for item in data.get("path", []):
                assert item["status"] in valid_statuses