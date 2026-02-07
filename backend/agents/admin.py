from django.contrib import admin
from .models import Contact, AgentSession, AgentStep, QueryHistory, AgentComparison


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "department", "role", "is_active"]
    search_fields = ["name", "email", "department"]
    list_filter = ["department", "is_active"]


class AgentStepInline(admin.TabularInline):
    model = AgentStep
    extra = 0
    readonly_fields = ["id", "created_at"]


class QueryHistoryInline(admin.TabularInline):
    model = QueryHistory
    extra = 0
    readonly_fields = ["id", "created_at"]


@admin.register(AgentSession)
class AgentSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "agent_type", "status", "user_message", "execution_time_ms", "created_at"]
    list_filter = ["agent_type", "status"]
    search_fields = ["user_message"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [AgentStepInline, QueryHistoryInline]


@admin.register(AgentComparison)
class AgentComparisonAdmin(admin.ModelAdmin):
    list_display = ["id", "query", "winner", "created_at"]
    readonly_fields = ["id", "created_at"]
