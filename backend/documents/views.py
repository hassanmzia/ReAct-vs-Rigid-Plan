import os
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Document, DocumentChunk
from .serializers import (
    DocumentSerializer,
    DocumentDetailSerializer,
    DocumentUploadSerializer,
)
from .services.pdf_processor import process_document

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DocumentDetailSerializer
        return DocumentSerializer

    filterset_fields = ["doc_type", "processing_status"]
    search_fields = ["title"]

    def create(self, request, *args, **kwargs):
        upload_serializer = DocumentUploadSerializer(data=request.data)
        upload_serializer.is_valid(raise_exception=True)

        uploaded_file = upload_serializer.validated_data["file"]
        filename = uploaded_file.name
        ext = os.path.splitext(filename)[1].lower().lstrip(".")

        doc_type_map = {"pdf": "pdf", "txt": "txt", "docx": "docx", "md": "md"}
        doc_type = doc_type_map.get(ext, "txt")

        title = upload_serializer.validated_data.get("title") or filename

        doc = Document.objects.create(
            title=title,
            file=uploaded_file,
            doc_type=doc_type,
            file_size=uploaded_file.size,
        )

        # Process in background
        try:
            process_document(str(doc.id))
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            doc.processing_status = Document.ProcessingStatus.FAILED
            doc.save(update_fields=["processing_status"])

        doc.refresh_from_db()
        return Response(DocumentSerializer(doc).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def reprocess(self, request, pk=None):
        doc = self.get_object()
        doc.chunks.all().delete()
        doc.processing_status = Document.ProcessingStatus.PENDING
        doc.save(update_fields=["processing_status"])

        try:
            process_document(str(doc.id))
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        doc.refresh_from_db()
        return Response(DocumentSerializer(doc).data)

    @action(detail=True, methods=["get"])
    def chunks(self, request, pk=None):
        doc = self.get_object()
        from .serializers import DocumentChunkSerializer
        chunks = doc.chunks.all()
        return Response(DocumentChunkSerializer(chunks, many=True).data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "")
        if not query:
            return Response({"error": "Query parameter 'q' is required"}, status=400)

        chunks = DocumentChunk.objects.filter(content__icontains=query)[:20]
        results = []
        for chunk in chunks:
            results.append({
                "document_id": str(chunk.document_id),
                "document_title": chunk.document.title,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "content": chunk.content[:500],
                "relevance": "keyword_match",
            })

        return Response({"query": query, "results": results, "count": len(results)})
