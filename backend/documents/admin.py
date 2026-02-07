from django.contrib import admin
from .models import Document, DocumentChunk


class DocumentChunkInline(admin.TabularInline):
    model = DocumentChunk
    extra = 0
    readonly_fields = ["id", "chunk_index", "token_count", "page_number"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "doc_type", "processing_status", "chunk_count", "created_at"]
    list_filter = ["doc_type", "processing_status"]
    search_fields = ["title"]
    inlines = [DocumentChunkInline]
