import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Contact, AgentSession, AgentStep, QueryHistory, AgentComparison
from .serializers import (
    ContactSerializer,
    AgentSessionListSerializer,
    AgentSessionDetailSerializer,
    AgentRunRequestSerializer,
    CompareAgentsRequestSerializer,
    AgentComparisonSerializer,
    RecursiveQARequestSerializer,
)
from .tasks import run_agent_task, run_comparison_task, run_recursive_qa_task
from .services.graph_visualizer import GraphVisualizer

logger = logging.getLogger(__name__)


class ContactViewSet(viewsets.ModelViewSet):
    """CRUD for contacts database."""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    search_fields = ["name", "email", "department"]
    filterset_fields = ["department", "is_active"]


class AgentSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """View agent execution sessions."""
    queryset = AgentSession.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AgentSessionDetailSerializer
        return AgentSessionListSerializer

    filterset_fields = ["agent_type", "status"]
    search_fields = ["user_message"]
    ordering_fields = ["created_at", "execution_time_ms"]

    @action(detail=False, methods=["post"])
    def run(self, request):
        """Execute an agent and return results."""
        serializer = AgentRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = AgentSession.objects.create(
            agent_type=serializer.validated_data["agent_type"],
            status=AgentSession.Status.PENDING,
            user_message=serializer.validated_data["message"],
            user_name_target=serializer.validated_data.get("user_name", ""),
            created_by=request.user if request.user.is_authenticated else None,
        )

        # Run synchronously for immediate response (small tasks)
        # For large tasks, use Celery async
        task = run_agent_task.delay(str(session.id))

        return Response(
            {
                "session_id": str(session.id),
                "task_id": task.id,
                "status": "pending",
                "message": "Agent execution started",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["post"], url_path="run-sync")
    def run_sync(self, request):
        """Execute an agent synchronously and return results immediately."""
        serializer = AgentRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = AgentSession.objects.create(
            agent_type=serializer.validated_data["agent_type"],
            status=AgentSession.Status.PENDING,
            user_message=serializer.validated_data["message"],
            user_name_target=serializer.validated_data.get("user_name", ""),
            created_by=request.user if request.user.is_authenticated else None,
        )

        from .tasks import _execute_agent
        _execute_agent(str(session.id))

        session.refresh_from_db()
        return Response(AgentSessionDetailSerializer(session).data)

    @action(detail=False, methods=["post"])
    def compare(self, request):
        """Run both ReAct and Rigid agents and compare results."""
        serializer = CompareAgentsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = run_comparison_task.delay(
            serializer.validated_data["message"],
            serializer.validated_data.get("user_name", ""),
        )

        return Response(
            {"task_id": task.id, "status": "pending", "message": "Comparison started"},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["post"], url_path="compare-sync")
    def compare_sync(self, request):
        """Run comparison synchronously."""
        serializer = CompareAgentsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from .tasks import _execute_comparison
        comparison = _execute_comparison(
            serializer.validated_data["message"],
            serializer.validated_data.get("user_name", ""),
        )

        return Response(AgentComparisonSerializer(comparison).data)

    @action(detail=False, methods=["post"], url_path="recursive-qa")
    def recursive_qa(self, request):
        """Run recursive Q&A tuneup."""
        serializer = RecursiveQARequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = AgentSession.objects.create(
            agent_type=AgentSession.AgentType.RECURSIVE,
            status=AgentSession.Status.PENDING,
            user_message=serializer.validated_data["query"],
        )

        task = run_recursive_qa_task.delay(
            str(session.id),
            serializer.validated_data.get("max_refinements", 3),
            serializer.validated_data.get("target_confidence", 0.85),
        )

        return Response(
            {
                "session_id": str(session.id),
                "task_id": task.id,
                "status": "pending",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=False, methods=["post"], url_path="recursive-qa-sync")
    def recursive_qa_sync(self, request):
        """Run recursive Q&A synchronously."""
        serializer = RecursiveQARequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = AgentSession.objects.create(
            agent_type=AgentSession.AgentType.RECURSIVE,
            status=AgentSession.Status.PENDING,
            user_message=serializer.validated_data["query"],
        )

        from .tasks import _execute_recursive_qa
        _execute_recursive_qa(
            str(session.id),
            serializer.validated_data.get("max_refinements", 3),
            serializer.validated_data.get("target_confidence", 0.85),
        )

        session.refresh_from_db()
        return Response(AgentSessionDetailSerializer(session).data)


class AgentComparisonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgentComparison.objects.all()
    serializer_class = AgentComparisonSerializer


class GraphViewSet(viewsets.ViewSet):
    """Visualize agent graph definitions as Mermaid diagrams or JSON."""

    def list(self, request):
        """Get all agent graph definitions."""
        fmt = request.query_params.get("output_format", "mermaid")
        if fmt == "mermaid":
            return Response(GraphVisualizer.get_all_mermaid())
        return Response({
            t: GraphVisualizer.get_graph_json(t)
            for t in ["react", "rigid", "multi", "recursive"]
        })

    def retrieve(self, request, pk=None):
        """Get graph visualization for a specific agent type."""
        fmt = request.query_params.get("output_format", "mermaid")
        try:
            if fmt == "mermaid":
                data = GraphVisualizer.get_mermaid(pk)
                return Response({"agent_type": pk, "format": "mermaid", "diagram": data})
            else:
                data = GraphVisualizer.get_graph_json(pk)
                return Response({"agent_type": pk, "format": "json", "graph": data})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
