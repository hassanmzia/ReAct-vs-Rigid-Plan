from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_stats, name="dashboard-stats"),
    path("trends/", views.performance_trends, name="performance-trends"),
    path("leaderboard/", views.agent_leaderboard, name="agent-leaderboard"),
]
