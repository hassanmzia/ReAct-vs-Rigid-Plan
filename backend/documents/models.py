import uuid
from django.db import models


class Document(models.Model):
    """Uploaded document for RAG processing."""

    class DocType(models.TextChoices):
        PDF = "pdf", "PDF"
        TXT = "txt", "Text"
        DOCX = "docx", "Word Document"
        MD = "md", "Markdown"

    class ProcessingStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    file = models.FileField(upload_to="documents/%Y/%m/")
    doc_type = models.CharField(max_length=10, choices=DocType.choices)
    file_size = models.IntegerField(default=0)
    page_count = models.IntegerField(null=True, blank=True)
    processing_status = models.CharField(
        max_length=20, choices=ProcessingStatus.choices, default=ProcessingStatus.PENDING
    )
    extracted_text = models.TextField(blank=True, default="")
    chunk_count = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    """Text chunk from a processed document for RAG."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.IntegerField()
    content = models.TextField()
    page_number = models.IntegerField(null=True, blank=True)
    token_count = models.IntegerField(default=0)
    embedding_vector = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["document", "chunk_index"]
        unique_together = [("document", "chunk_index")]

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"
