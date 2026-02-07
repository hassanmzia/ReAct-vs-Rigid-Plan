"""
PDF & Document Processing Service.

Handles:
- PDF text extraction
- Text chunking for RAG
- Token counting
"""

import logging
import os

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def process_document(document_id: str):
    """Process a document: extract text, chunk it, store chunks."""
    from documents.models import Document, DocumentChunk

    doc = Document.objects.get(id=document_id)
    doc.processing_status = Document.ProcessingStatus.PROCESSING
    doc.save(update_fields=["processing_status"])

    try:
        file_path = doc.file.path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if doc.doc_type == "pdf":
            text, page_count = _extract_pdf(file_path)
            doc.page_count = page_count
        elif doc.doc_type in ("txt", "md"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            text = ""

        doc.extracted_text = text

        # Chunk the text
        chunks = _chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        doc.chunk_count = len(chunks)

        # Save chunks
        for i, chunk_text in enumerate(chunks):
            DocumentChunk.objects.create(
                document=doc,
                chunk_index=i,
                content=chunk_text,
                page_number=None,
                token_count=len(chunk_text.split()),
            )

        doc.processing_status = Document.ProcessingStatus.COMPLETED
        doc.save()
        logger.info(f"Processed document '{doc.title}': {len(chunks)} chunks")

    except Exception as e:
        logger.exception(f"Document processing failed: {e}")
        doc.processing_status = Document.ProcessingStatus.FAILED
        doc.metadata["error"] = str(e)
        doc.save()
        raise


def _extract_pdf(file_path: str) -> tuple[str, int]:
    """Extract text from PDF."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages), len(reader.pages)
    except ImportError:
        logger.warning("pypdf not installed, returning empty text")
        return "", 0


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
