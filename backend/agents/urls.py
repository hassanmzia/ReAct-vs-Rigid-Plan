from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"contacts", views.ContactViewSet)
router.register(r"sessions", views.AgentSessionViewSet)
router.register(r"comparisons", views.AgentComparisonViewSet)
router.register(r"graphs", views.GraphViewSet, basename="graph")

urlpatterns = [
    path("", include(router.urls)),
]
