import uuid
from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    """Simulated contact database (from notebook)."""
    name = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=200)
    role = models.CharField(max_length=200, blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.department})"


class AgentSession(models.Model):
    """Tracks an agent execution session."""

    class AgentType(models.TextChoices):
        REACT = "react", "Adaptive ReAct"
        RIGID = "rigid", "Rigid Plan-and-Execute"
        MULTI = "multi", "Multi-Agent Orchestrator"
        RECURSIVE = "recursive", "Recursive Q&A Tuneup"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_type = models.CharField(max_length=20, choices=AgentType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    user_message = models.TextField(help_text="Original user query / instruction")
    user_name_target = models.CharField(
        max_length=200, blank=True, default="",
        help_text="Target contact name extracted from message",
    )
    final_result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True, default="")
    execution_time_ms = models.IntegerField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    graph_definition = models.JSONField(
        null=True, blank=True,
        help_text="Mermaid / LangGraph graph definition for visualization",
    )
    langsmith_run_id = models.CharField(max_length=100, blank=True, default="")
    langfuse_trace_id = models.CharField(max_length=100, blank=True, default="")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="agent_sessions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.agent_type}] {self.user_message[:60]}"


class AgentStep(models.Model):
    """Individual step within an agent execution (node traversal)."""

    class StepStatus(models.TextChoices):
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        AgentSession, on_delete=models.CASCADE, related_name="steps"
    )
    node_name = models.CharField(max_length=100, help_text="LangGraph node name")
    step_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=StepStatus.choices)
    input_state = models.JSONField(null=True, blank=True)
    output_state = models.JSONField(null=True, blank=True)
    log_messages = models.JSONField(default=list, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["session", "step_number"]
        unique_together = [("session", "step_number")]

    def __str__(self):
        return f"Step {self.step_number}: {self.node_name} [{self.status}]"


class QueryHistory(models.Model):
    """Stores recursive Q&A refinement history."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        AgentSession, on_delete=models.CASCADE, related_name="query_history"
    )
    iteration = models.IntegerField(default=1)
    original_query = models.TextField()
    refined_query = models.TextField(blank=True, default="")
    answer = models.TextField(blank=True, default="")
    confidence_score = models.FloatField(null=True, blank=True)
    sources_used = models.JSONField(default=list, blank=True)
    feedback = models.TextField(blank=True, default="")
    is_final = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["session", "iteration"]

    def __str__(self):
        return f"Iteration {self.iteration}: {self.original_query[:50]}"


class AgentComparison(models.Model):
    """Side-by-side comparison of ReAct vs Rigid agent runs."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.TextField()
    react_session = models.ForeignKey(
        AgentSession, on_delete=models.CASCADE, related_name="react_comparisons"
    )
    rigid_session = models.ForeignKey(
        AgentSession, on_delete=models.CASCADE, related_name="rigid_comparisons"
    )
    winner = models.CharField(max_length=20, blank=True, default="")
    analysis = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comparison: {self.query[:50]}"
