"""Shared fixtures for all tests."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from typing import List

import pytest

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.document_parser import TextChunk


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_text_chunks() -> List[TextChunk]:
    """Sample text chunks for testing."""
    return [
        TextChunk(
            text="Hàm số bậc hai là hàm số có dạng y = ax^2 + bx + c, trong đó a ≠ 0. "
                 "Đồ thị của hàm số bậc hai là một parabol.",
            page_number=1,
            char_count=100
        ),
        TextChunk(
            text="Đỉnh của parabol là điểm có tọa độ (x = -b/2a, y = -Δ/4a). "
                 "Parabol có trục đối xứng là đường thẳng x = -b/2a.",
            page_number=2,
            char_count=100
        ),
        TextChunk(
            text="Phương trình bậc hai ax^2 + bx + c = 0 có nghiệm khi Δ ≥ 0. "
                 "Công thức nghiệm: x = (-b ± √Δ) / 2a.",
            page_number=3,
            char_count=100
        ),
    ]


@pytest.fixture
def sample_topic_data() -> dict:
    """Sample topic data for testing."""
    return {
        "topic_id": "test-topic-001",
        "name": "Hàm số bậc hai",
        "description": "Khái niệm về hàm số bậc hai và đồ thị parabol",
        "subject": "toan",
        "skill_level": 2,
        "prerequisites": [],
        "related_topics": ["phuong-trinh-bac-hai"]
    }


@pytest.fixture
def sample_quiz_questions() -> List[dict]:
    """Sample quiz questions for testing."""
    return [
        {
            "question_id": "q1",
            "question": "Hàm số bậc hai có dạng tổng quát là gì?",
            "question_type": "multiple_choice",
            "options": [
                "y = ax + b",
                "y = ax^2 + bx + c",
                "y = ax^3 + bx^2 + cx + d",
                "y = a/x"
            ],
            "correct_answer": "y = ax^2 + bx + c"
        },
        {
            "question_id": "q2",
            "question": "Đỉnh của parabol có tọa độ x bằng bao nhiêu?",
            "question_type": "multiple_choice",
            "options": ["-b/2a", "b/2a", "-b/a", "b/a"],
            "correct_answer": "-b/2a"
        }
    ]


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for testing."""
    return {
        "user_id": "test-user-001",
        "email": "test@example.com",
        "name": "Test User",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqKx8KvP8a"
    }


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from app.config import Settings

    return Settings(
        gemini_api_key="test-api-key",
        openrouter_api_key="test-openrouter-key",
        openrouter_model="openai/gpt-oss-120b",
        openrouter_base_url="https://openrouter.ai/api/v1",
        openrouter_provider_order="nvidia,groq,together",
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="test-password",
        jwt_secret_key="test-secret-key",
        jwt_algorithm="HS256",
        access_token_expire_minutes=30,
        max_file_size_mb=100
    )


@pytest.fixture
def mock_neo4j_session():
    """Mock Neo4j session."""
    session = MagicMock()
    session.run = AsyncMock(return_value=MagicMock(__aenter__=AsyncMock(), __aexit__=AsyncMock()))
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver."""
    driver = MagicMock()
    session = MagicMock()
    session.run = AsyncMock(return_value=MagicMock(__aenter__=AsyncMock(), __aexit__=AsyncMock()))
    session.close = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    driver.session = MagicMock(return_value=session)
    driver.close = AsyncMock()
    return driver


# ============================================================================
# File Fixtures
# ============================================================================

@pytest.fixture
def sample_pdf_content():
    """Sample PDF content as bytes."""
    # Minimal PDF structure
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        b"4 0 obj << /Length 44 >> stream\n"
        b"BT /F1 12 Tf 100 700 Td (Test PDF content) Tj ET\n"
        b"endstream endobj\n"
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000266 00000 n \n0000000351 00000 n \n"
        b"trailer << /Size 6 /Root 1 0 R >>\n"
        b"startxref\n440\n%%EOF"
    )
    return pdf_content


@pytest.fixture
def sample_docx_content():
    """Sample DOCX content as bytes (minimal)."""
    import zipfile
    import io

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zf:
        # Add minimal DOCX structure
        zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        zf.writestr("word/document.xml", '<?xml version="1.0"?><document><body><paragraph>Test DOCX content</paragraph></body></document>')

    buffer.seek(0)
    return buffer.getvalue()


@pytest.fixture
def sample_txt_content():
    """Sample text content with double newlines for paragraph splitting."""
    return "Đây là đoạn văn 1.\n\nĐây là đoạn văn 2.\n\nĐây là đoạn văn 3."