from rest_framework import serializers
from .models import Contact, AgentSession, AgentStep, QueryHistory, AgentComparison


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class AgentStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentStep
        fields = "__all__"


class QueryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryHistory
        fields = "__all__"


class AgentSessionListSerializer(serializers.ModelSerializer):
    steps_count = serializers.IntegerField(source="steps.count", read_only=True)
    iterations_count = serializers.IntegerField(source="query_history.count", read_only=True)

    class Meta:
        model = AgentSession
        fields = [
            "id", "agent_type", "status", "user_message", "user_name_target",
            "execution_time_ms", "retry_count", "created_at", "updated_at",
            "steps_count", "iterations_count",
        ]


class AgentSessionDetailSerializer(serializers.ModelSerializer):
    steps = AgentStepSerializer(many=True, read_only=True)
    query_history = QueryHistorySerializer(many=True, read_only=True)

    class Meta:
        model = AgentSession
        fields = "__all__"


class AgentRunRequestSerializer(serializers.Serializer):
    agent_type = serializers.ChoiceField(choices=AgentSession.AgentType.choices)
    message = serializers.CharField(max_length=2000)
    user_name = serializers.CharField(max_length=200, required=False, default="")
    document_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )
    enable_tracing = serializers.BooleanField(required=False, default=True)
    max_iterations = serializers.IntegerField(required=False, default=5, min_value=1, max_value=20)


class CompareAgentsRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    user_name = serializers.CharField(max_length=200, required=False, default="")


class AgentComparisonSerializer(serializers.ModelSerializer):
    react_session = AgentSessionDetailSerializer(read_only=True)
    rigid_session = AgentSessionDetailSerializer(read_only=True)

    class Meta:
        model = AgentComparison
        fields = "__all__"


class RecursiveQARequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=2000)
    document_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )
    max_refinements = serializers.IntegerField(required=False, default=3, min_value=1, max_value=10)
    target_confidence = serializers.FloatField(required=False, default=0.85, min_value=0.0, max_value=1.0)


class GraphVisualizationSerializer(serializers.Serializer):
    agent_type = serializers.ChoiceField(choices=AgentSession.AgentType.choices)
    format = serializers.ChoiceField(
        choices=[("mermaid", "Mermaid"), ("json", "JSON")],
        default="mermaid",
    )
