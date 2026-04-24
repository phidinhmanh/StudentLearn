from typing import List, Optional
import fitz  # PyMuPDF
from docx import Document


class TextChunk:
    def __init__(self, text: str, page_number: int = 0, char_count: int = 0):
        self.text = text
        self.page_number = page_number
        self.char_count = char_count

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "page_number": self.page_number,
            "char_count": self.char_count,
        }


def parse_document(file_bytes: bytes, filename: str) -> List[TextChunk]:
    """Parse document and return list of text chunks"""
    if filename.lower().endswith(".pdf"):
        return parse_pdf(file_bytes)
    elif filename.lower().endswith(".docx"):
        return parse_docx(file_bytes)
    elif filename.lower().endswith(".txt"):
        return parse_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file format: {filename}")


def parse_pdf(file_bytes: bytes) -> List[TextChunk]:
    """Extract text from PDF using PyMuPDF"""
    chunks = []
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        if text.strip():
            # Split by paragraphs for better chunking
            paragraphs = text.split("\n\n")
            for para in paragraphs:
                if para.strip():
                    chunks.append(TextChunk(
                        text=para.strip(),
                        page_number=page_num + 1,
                        char_count=len(para),
                    ))

    doc.close()
    return chunks


def parse_docx(file_bytes: bytes) -> List[TextChunk]:
    """Extract text from DOCX using python-docx"""
    import io
    chunks = []
    doc = Document(io.BytesIO(file_bytes))

    page_num = 1
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            chunks.append(TextChunk(
                text=text,
                page_number=page_num,
                char_count=len(text),
            ))
            # Simple page estimation: every ~30 paragraphs = 1 page
            if len(chunks) % 30 == 0:
                page_num += 1

    return chunks


def parse_txt(file_bytes: bytes) -> List[TextChunk]:
    """Parse plain text file"""
    text = file_bytes.decode("utf-8", errors="replace")
    # Split by double newlines (paragraphs)
    paragraphs = text.split("\n\n")
    chunks = []
    for para in paragraphs:
        if para.strip():
            chunks.append(TextChunk(
                text=para.strip(),
                page_number=1,
                char_count=len(para),
            ))
    return chunks


def chunk_for_embedding(chunks: List[TextChunk], target_size: int = 1000, overlap: int = 100) -> List[str]:
    """Merge chunks into larger pieces suitable for embedding"""
    all_text = "\n\n".join([c.text for c in chunks])
    if not all_text:
        return []

    # Ensure overlap is smaller than target_size
    if overlap >= target_size:
        overlap = target_size // 2

    result = []
    start = 0
    step = target_size - overlap

    while start < len(all_text):
        end = start + target_size
        result.append(all_text[start:end])
        start += step

    return result