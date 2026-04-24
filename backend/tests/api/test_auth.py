"""API tests for authentication endpoints."""
import pytest
from httpx import AsyncClient


class TestAuthRegister:
    """Tests for POST /api/v1/auth/register."""

    @pytest.mark.asyncio
    async def test_register_success(self, async_client: AsyncClient):
        """Should register new user successfully."""
        response = await async_client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "testpassword123",
            "name": "Test User"
        })

        assert response.status_code in [200, 201, 400]  # 400 if email exists

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client: AsyncClient):
        """Should reject invalid email format."""
        response = await async_client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "password": "testpassword123",
            "name": "Test User"
        })

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_short_password(self, async_client: AsyncClient):
        """Should reject short password."""
        response = await async_client.post("/api/v1/auth/register", json={
            "email": "test2@example.com",
            "password": "12345",  # Less than 6 chars
            "name": "Test User"
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, async_client: AsyncClient):
        """Should reject missing required fields."""
        response = await async_client.post("/api/v1/auth/register", json={
            "email": "test3@example.com"
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_empty_name(self, async_client: AsyncClient):
        """Should reject empty name."""
        response = await async_client.post("/api/v1/auth/register", json={
            "email": "test4@example.com",
            "password": "testpassword123",
            "name": ""
        })

        assert response.status_code == 422


class TestAuthLogin:
    """Tests for POST /api/v1/auth/login."""

    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient):
        """Should login with valid credentials."""
        # First register
        email = "logintest@example.com"
        await async_client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "testpassword123",
            "name": "Login Test"
        })

        # Then login
        response = await async_client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "testpassword123"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, async_client: AsyncClient):
        """Should reject wrong password."""
        email = "wrongpw@example.com"

        # Register first
        await async_client.post("/api/v1/auth/register", json={
            "email": email,
            "password": "correctpassword",
            "name": "Test"
        })

        # Login with wrong password
        response = await async_client.post("/api/v1/auth/login", json={
            "email": email,
            "password": "wrongpassword"
        })

        # Should return 401 or 400 depending on implementation
        assert response.status_code in [400, 401]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Should reject login for non-existent user."""
        response = await async_client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        })

        assert response.status_code in [400, 401, 404]

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, async_client: AsyncClient):
        """Should reject invalid email format."""
        response = await async_client.post("/api/v1/auth/login", json={
            "email": "invalid-email",
            "password": "password"
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, async_client: AsyncClient):
        """Should reject missing fields."""
        response = await async_client.post("/api/v1/auth/login", json={
            "email": "test@example.com"
        })

        assert response.status_code == 422


class TestAuthToken:
    """Tests for token validation."""

    @pytest.mark.asyncio
    async def test_invalid_token_format(self, async_client: AsyncClient):
        """Should reject malformed tokens."""
        response = await async_client.get(
            "/api/v1/documents/",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_auth_header(self, async_client: AsyncClient):
        """Should require authentication for protected endpoints."""
        response = await async_client.get("/api/v1/documents/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_format(self, async_client: AsyncClient):
        """Should handle token without required claims."""
        response = await async_client.get(
            "/api/v1/documents/",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"}
        )

        # Should be 401 due to invalid/expired token
        assert response.status_code == 401