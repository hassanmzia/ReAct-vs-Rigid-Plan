from rest_framework import serializers
from .models import Document, DocumentChunk


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ["id", "chunk_index", "content", "page_number", "token_count"]


class DocumentSerializer(serializers.ModelSerializer):
    chunks_count = serializers.IntegerField(source="chunks.count", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id", "title", "file", "doc_type", "file_size", "page_count",
            "processing_status", "chunk_count", "chunks_count",
            "metadata", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "doc_type", "file_size", "page_count",
                            "processing_status", "chunk_count", "created_at", "updated_at"]


class DocumentDetailSerializer(serializers.ModelSerializer):
    chunks = DocumentChunkSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = "__all__"


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    title = serializers.CharField(max_length=500, required=False)
