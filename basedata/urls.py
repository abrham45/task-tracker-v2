from django.urls import include, path
from rest_framework.routers import DefaultRouter

from basedata.views import (
    ChallengeGroupViewSet,
    ChallengeTypeViewSet,
    DepartmentViewSet,
    PositionViewSet,
    RoleViewSet,
)

router = DefaultRouter()
router.register("departments", DepartmentViewSet, "department")
router.register("positions", PositionViewSet, "position")
router.register("roles", RoleViewSet, "role")
router.register("challenge_types", ChallengeTypeViewSet, "challenge_type")
router.register("challenge_groups", ChallengeGroupViewSet, "challenge_group")

urlpatterns = [
    path("basedata/", include(router.urls)),
]
