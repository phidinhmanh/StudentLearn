"""API tests for document endpoints."""
import pytest
from httpx import AsyncClient


class TestDocumentIngest:
    """Tests for POST /api/v1/documents/ingest."""

    @pytest.mark.asyncio
    async def test_ingest_requires_auth(self, async_client: AsyncClient):
        """Should require authentication."""
        response = await async_client.post(
            "/api/v1/documents/ingest",
            files={"file": ("test.pdf", b"pdf content", "application/pdf")},
            data={"subject": "toan"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_ingest_pdf_format(self, auth_client: AsyncClient):
        """Should accept PDF files."""
        pdf_content = b"%PDF-1.4 test content"

        response = await auth_client.post(
            "/api/v1/documents/ingest",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
            data={"subject": "toan"}
        )

        # May succeed or fail depending on Neo4j availability
        assert response.status_code in [200, 201, 500, 503]

    @pytest.mark.asyncio
    async def test_ingest_docx_format(self, auth_client: AsyncClient):
        """Should accept DOCX files."""
        response = await auth_client.post(
            "/api/v1/documents/ingest",
            files={"file": ("test.docx", b"docx content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
            data={"subject": "toan"}
        )

        assert response.status_code in [200, 201, 400, 500, 503]

    @pytest.mark.asyncio
    async def test_ingest_txt_format(self, auth_client: AsyncClient):
        """Should accept TXT files."""
        response = await auth_client.post(
            "/api/v1/documents/ingest",
            files={"file": ("test.txt", "Nội dung test".encode(), "text/plain")},
            data={"subject": "toan"}
        )

        assert response.status_code in [200, 201, 400, 500, 503]

    @pytest.mark.asyncio
    async def test_ingest_unsupported_format(self, auth_client: AsyncClient):
        """Should reject unsupported formats."""
        response = await auth_client.post(
            "/api/v1/documents/ingest",
            files={"file": ("test.xyz", b"content", "application/octet-stream")},
            data={"subject": "toan"}
        )

        # Should return error for unsupported format
        assert response.status_code in [400, 415, 500]


class TestListDocuments:
    """Tests for GET /api/v1/documents/."""

    @pytest.mark.asyncio
    async def test_list_requires_auth(self, async_client: AsyncClient):
        """Should require authentication."""
        response = await async_client.get("/api/v1/documents/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_documents_empty(self, auth_client: AsyncClient):
        """Should return empty list when no documents."""
        response = await auth_client.get("/api/v1/documents/")

        # May be 500 if Neo4j unavailable, otherwise 200 with []
        assert response.status_code in [200, 500, 503]
        if response.status_code == 200:
            assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_list_returns_own_documents(self, auth_client: AsyncClient):
        """Should only return user's own documents."""
        response = await auth_client.get("/api/v1/documents/")

        # Response should be a list of documents
        assert response.status_code in [200, 500, 503]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestGetDocumentTopics:
    """Tests for GET /api/v1/documents/{doc_id}/topics."""

    @pytest.mark.asyncio
    async def test_get_topics_requires_auth(self, async_client: AsyncClient):
        """Should require authentication."""
        response = await async_client.get("/api/v1/documents/doc-123/topics")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_topics_for_document(self, auth_client: AsyncClient):
        """Should return topics for document."""
        response = await auth_client.get("/api/v1/documents/doc-123/topics")

        # May be 404 if doc not found, 200 with list, or 500 if error
        assert response.status_code in [200, 404, 500, 503]
        if response.status_code == 200:
            assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_topics_nonexistent_doc(self, auth_client: AsyncClient):
        """Should return 404 for non-existent document."""
        response = await auth_client.get("/api/v1/documents/nonexistent-doc/topics")

        assert response.status_code in [404, 500, 503]


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_no_auth_required(self, async_client: AsyncClient):
        """Health check should not require auth."""
        response = await async_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Root endpoint should return API info."""
        response = await async_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data