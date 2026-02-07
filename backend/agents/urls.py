from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"contacts", views.ContactViewSet)
router.register(r"sessions", views.AgentSessionViewSet)
router.register(r"comparisons", views.AgentComparisonViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("graph/", views.graph_visualization, name="graph-visualization"),
    path("graphs/", views.all_graphs, name="all-graphs"),
]
