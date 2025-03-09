from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tasks.views import (
    KPIViewSet,
    KSIViewSet,
    MajorActivityViewSet,
    MilestoneViewSet,
    TaskViewSet,
)

router = DefaultRouter()

router.register("kpis", KPIViewSet, "kpi")
router.register("ksis", KSIViewSet, "ksi")
router.register("major_activities", MajorActivityViewSet, "major_activity")
router.register("milestones", MilestoneViewSet, "milestone")
router.register("tasks", TaskViewSet, "task")

urlpatterns = [
    path("", include(router.urls)),
]
