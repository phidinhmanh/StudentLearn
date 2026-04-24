"""Unit tests for document parser."""
import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock
from app.services.document_parser import (
    parse_document,
    parse_pdf,
    parse_docx,
    parse_txt,
    chunk_for_embedding,
    TextChunk,
)


class TestParseDocument:
    """Tests for parse_document function."""

    @patch("app.services.document_parser.fitz.open")
    def test_parses_pdf(self, mock_fitz_open, sample_pdf_content):
        """Should parse PDF files."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Test PDF content"
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc

        chunks = parse_document(sample_pdf_content, "test.pdf")
        assert len(chunks) == 1
        assert chunks[0].text == "Test PDF content"

    @patch("app.services.document_parser.Document")
    def test_parses_docx(self, mock_doc_class, sample_docx_content):
        """Should parse DOCX files."""
        mock_doc = MagicMock()
        mock_para = MagicMock()
        mock_para.text = "Test DOCX content"
        mock_doc.paragraphs = [mock_para]
        mock_doc_class.return_value = mock_doc

        chunks = parse_document(sample_docx_content, "test.docx")
        assert len(chunks) == 1
        assert chunks[0].text == "Test DOCX content"

    def test_parses_txt(self, sample_txt_content):
        """Should parse TXT files."""
        chunks = parse_document(sample_txt_content.encode(), "test.txt")
        assert len(chunks) > 0
        assert all(isinstance(c, TextChunk) for c in chunks)

    def test_raises_on_unsupported_format(self, sample_txt_content):
        """Should raise ValueError for unsupported formats."""
        with pytest.raises(ValueError, match="Unsupported file format"):
            parse_document(sample_txt_content, "test.xyz")

    @patch("app.services.document_parser.fitz.open")
    @patch("app.services.document_parser.Document")
    def test_case_insensitive_extension(self, mock_doc_class, mock_fitz_open, sample_txt_content):
        """Should handle case-insensitive file extensions."""
        # Setup mock PDF
        mock_pdf = MagicMock()
        mock_pdf.__len__.return_value = 1
        mock_pdf.__getitem__.return_value = MagicMock(get_text=MagicMock(return_value="pdf"))
        mock_fitz_open.return_value = mock_pdf

        # Setup mock DOCX
        mock_docx = MagicMock()
        mock_docx.paragraphs = [MagicMock(text="docx")]
        mock_doc_class.return_value = mock_docx

        chunks_txt = parse_document(sample_txt_content.encode(), "test.TXT")
        assert len(chunks_txt) > 0

        chunks_pdf = parse_document(b"pdf", "test.PDF")
        assert len(chunks_pdf) == 1

        chunks_docx = parse_document(b"docx", "test.Docx")
        assert len(chunks_docx) == 1


class TestParsePDF:
    """Tests for parse_pdf function."""

    @patch("app.services.document_parser.fitz.open")
    def test_returns_list_of_chunks(self, mock_fitz_open, sample_pdf_content):
        """Should return list of TextChunk objects."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Test content"
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc

        chunks = parse_pdf(sample_pdf_content)
        assert isinstance(chunks, list)
        assert len(chunks) == 1
        assert isinstance(chunks[0], TextChunk)

    @patch("app.services.document_parser.fitz.open")
    def test_empty_pdf(self, mock_fitz_open):
        """Should handle empty PDF."""
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 0
        mock_fitz_open.return_value = mock_doc

        chunks = parse_pdf(b"empty")
        assert isinstance(chunks, list)
        assert len(chunks) == 0

    @patch("app.services.document_parser.fitz.open")
    def test_chunks_have_page_numbers(self, mock_fitz_open, sample_pdf_content):
        """Chunks should have valid page numbers."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Test content"
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc

        chunks = parse_pdf(sample_pdf_content)
        assert chunks[0].page_number == 1

    @patch("app.services.document_parser.fitz.open")
    def test_chunks_have_char_count(self, mock_fitz_open, sample_pdf_content):
        """Chunks should have character count."""
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Test content"
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_fitz_open.return_value = mock_doc

        chunks = parse_pdf(sample_pdf_content)
        assert chunks[0].char_count == len("Test content")


class TestParseDOCX:
    """Tests for parse_docx function."""

    @patch("app.services.document_parser.Document")
    def test_returns_list_of_chunks(self, mock_doc_class, sample_docx_content):
        """Should return list of TextChunk objects."""
        mock_doc = MagicMock()
        mock_para = MagicMock()
        mock_para.text = "Test content"
        mock_doc.paragraphs = [mock_para]
        mock_doc_class.return_value = mock_doc

        chunks = parse_docx(sample_docx_content)
        assert isinstance(chunks, list)
        assert len(chunks) == 1

    @patch("app.services.document_parser.Document")
    def test_chunks_have_page_numbers(self, mock_doc_class, sample_docx_content):
        """Chunks should have valid page numbers."""
        mock_doc = MagicMock()
        mock_para = MagicMock()
        mock_para.text = "Test content"
        mock_doc.paragraphs = [mock_para] * 35 # Should trigger page increment
        mock_doc_class.return_value = mock_doc

        chunks = parse_docx(sample_docx_content)
        assert chunks[0].page_number == 1
        assert chunks[34].page_number == 2

    @patch("app.services.document_parser.Document")
    def test_handles_empty_docx(self, mock_doc_class, sample_docx_content):
        """Should handle empty DOCX."""
        mock_doc = MagicMock()
        mock_doc.paragraphs = []
        mock_doc_class.return_value = mock_doc

        chunks = parse_docx(sample_docx_content)
        assert isinstance(chunks, list)
        assert len(chunks) == 0


class TestParseTXT:
    """Tests for parse_txt function."""

    def test_returns_list_of_chunks(self, sample_txt_content):
        """Should return list of TextChunk objects."""
        chunks = parse_txt(sample_txt_content.encode())
        assert len(chunks) > 0
        assert all(isinstance(c, TextChunk) for c in chunks)

    def test_splits_by_paragraphs(self, sample_txt_content):
        """Should split by double newlines (paragraphs)."""
        chunks = parse_txt(sample_txt_content.encode())
        assert len(chunks) >= 2  # At least 2 paragraphs

    def test_handles_empty_file(self):
        """Should handle empty file."""
        chunks = parse_txt(b"")
        assert isinstance(chunks, list)

    def test_handles_single_line(self):
        """Should handle single line without newlines."""
        chunks = parse_txt(b"Single line content")
        assert len(chunks) == 1

    def test_utf8_encoding(self):
        """Should handle UTF-8 Vietnamese characters."""
        content = "Hàm số bậc hai là gì?".encode()
        chunks = parse_txt(content)
        assert len(chunks) > 0
        assert "Hàm số bậc hai là gì?" in chunks[0].text


class TestChunkForEmbedding:
    """Tests for chunk_for_embedding function."""

    def test_returns_list_of_strings(self, sample_text_chunks):
        """Should return list of strings."""
        result = chunk_for_embedding(sample_text_chunks)
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)

    def test_respects_target_size(self, sample_text_chunks):
        """Should respect target_size parameter."""
        result = chunk_for_embedding(sample_text_chunks, target_size=50)
        for chunk in result:
            assert len(chunk) <= 50 + 100  # overlap allows slightly more

    def test_overlap_between_chunks(self, sample_text_chunks):
        """Should have overlap between consecutive chunks."""
        result = chunk_for_embedding(sample_text_chunks, target_size=100, overlap=20)
        if len(result) >= 2:
            # Last 20 chars of first chunk should be in first 20 chars of second
            assert result[0][-20:] in result[1]

    def test_handles_empty_chunks(self):
        """Should handle empty chunk list."""
        result = chunk_for_embedding([])
        assert result == []

    def test_single_chunk(self, sample_text_chunks):
        """Should handle single chunk."""
        result = chunk_for_embedding([sample_text_chunks[0]])
        assert len(result) >= 1


class TestTextChunk:
    """Tests for TextChunk class."""

    def test_to_dict(self):
        """Should convert to dictionary."""
        chunk = TextChunk(text="Test content", page_number=1, char_count=12)
        result = chunk.to_dict()
        assert result == {
            "text": "Test content",
            "page_number": 1,
            "char_count": 12,
        }

    def test_init_with_defaults(self):
        """Should have default values."""
        chunk = TextChunk(text="Test")
        assert chunk.page_number == 0
        assert chunk.char_count == 0