"""Analytics API views for dashboards and reporting."""

from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response

from agents.models import AgentSession, AgentComparison, QueryHistory
from documents.models import Document


@api_view(["GET"])
def dashboard_stats(request):
    """Get dashboard overview statistics."""
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    total_sessions = AgentSession.objects.count()
    recent_sessions = AgentSession.objects.filter(created_at__gte=last_24h).count()

    by_type = AgentSession.objects.values("agent_type").annotate(
        count=Count("id"),
        avg_time=Avg("execution_time_ms"),
    )

    by_status = AgentSession.objects.values("status").annotate(count=Count("id"))

    success_rate = 0
    completed = AgentSession.objects.filter(status="completed").count()
    if total_sessions > 0:
        success_rate = round(completed / total_sessions * 100, 1)

    comparisons = AgentComparison.objects.count()
    react_wins = AgentComparison.objects.filter(winner="react").count()
    rigid_wins = AgentComparison.objects.filter(winner="rigid").count()

    avg_confidence = QueryHistory.objects.filter(
        confidence_score__isnull=False
    ).aggregate(avg=Avg("confidence_score"))

    documents = Document.objects.count()
    processed_docs = Document.objects.filter(processing_status="completed").count()

    return Response({
        "overview": {
            "total_sessions": total_sessions,
            "recent_sessions_24h": recent_sessions,
            "success_rate": success_rate,
            "total_documents": documents,
            "processed_documents": processed_docs,
        },
        "by_agent_type": list(by_type),
        "by_status": list(by_status),
        "comparisons": {
            "total": comparisons,
            "react_wins": react_wins,
            "rigid_wins": rigid_wins,
            "tie_or_none": comparisons - react_wins - rigid_wins,
        },
        "recursive_qa": {
            "avg_confidence": avg_confidence.get("avg"),
            "total_iterations": QueryHistory.objects.count(),
        },
    })


@api_view(["GET"])
def performance_trends(request):
    """Get performance trends over time."""
    days = int(request.query_params.get("days", 7))
    now = timezone.now()
    start = now - timedelta(days=days)

    sessions = AgentSession.objects.filter(created_at__gte=start)

    daily_data = []
    for i in range(days):
        day_start = start + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        day_sessions = sessions.filter(created_at__gte=day_start, created_at__lt=day_end)

        daily_data.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "total": day_sessions.count(),
            "completed": day_sessions.filter(status="completed").count(),
            "failed": day_sessions.filter(status="failed").count(),
            "avg_execution_ms": day_sessions.aggregate(
                avg=Avg("execution_time_ms")
            )["avg"],
        })

    return Response({"days": days, "trends": daily_data})


@api_view(["GET"])
def agent_leaderboard(request):
    """Compare agent performance metrics."""
    agent_types = ["react", "rigid", "multi", "recursive"]
    leaderboard = []

    for agent_type in agent_types:
        sessions = AgentSession.objects.filter(agent_type=agent_type)
        total = sessions.count()
        completed = sessions.filter(status="completed").count()

        leaderboard.append({
            "agent_type": agent_type,
            "total_runs": total,
            "success_count": completed,
            "success_rate": round(completed / total * 100, 1) if total > 0 else 0,
            "avg_execution_ms": sessions.aggregate(
                avg=Avg("execution_time_ms")
            )["avg"],
            "avg_retries": sessions.aggregate(
                avg=Avg("retry_count")
            )["avg"],
        })

    leaderboard.sort(key=lambda x: x["success_rate"], reverse=True)
    return Response(leaderboard)
