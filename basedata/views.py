from django.contrib.auth.models import Group as Role
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from basedata.filters import PositionFilter
from basedata.models import ChallengeGroup, ChallengeType, Department, Position
from basedata.serializers import (
    ChallengeGroupSerializer,
    ChallengeTypeSerializer,
    DepartmentSerializer,
    PositionSerializer,
    RoleSerializer,
)


class ChallengeTypeViewSet(viewsets.ModelViewSet):
    queryset = ChallengeType.objects.all()
    serializer_class = ChallengeTypeSerializer
    search_fields = ["challenge_type_name"]
    ordering_fields = ["challenge_type_name"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Field to order by (use prefix '-' for descending order).",
                enum=ordering_fields + [f"-{field}" for field in ordering_fields],
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.validated_data["created_by"] = self.request.user
            serializer.validated_data["updated_by"] = self.request.user
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.validated_data["updated_by"] = self.request.user
        return super().perform_update(serializer)


class ChallengeGroupViewSet(viewsets.ModelViewSet):
    queryset = ChallengeGroup.objects.all()
    serializer_class = ChallengeGroupSerializer
    search_fields = ["challenge_group_name"]
    ordering_fields = ["challenge_group_name"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Field to order by (use prefix '-' for descending order).",
                enum=ordering_fields + [f"-{field}" for field in ordering_fields],
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.validated_data["created_by"] = self.request.user
            serializer.validated_data["updated_by"] = self.request.user
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.validated_data["updated_by"] = self.request.user
        return super().perform_update(serializer)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    search_fields = ["department_name"]
    ordering_fields = ["department_name"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Field to order by (use prefix '-' for descending order).",
                enum=ordering_fields + [f"-{field}" for field in ordering_fields],
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.validated_data["created_by"] = self.request.user
            serializer.validated_data["updated_by"] = self.request.user
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.validated_data["updated_by"] = self.request.user
        return super().perform_update(serializer)


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    search_fields = ["position_name"]
    filterset_class = PositionFilter
    ordering_fields = ["position_name"]

    def get_queryset(self):
        user = self.request.user
        user_is_lead = (
            user.is_authenticated and user.groups.filter(name="Leads").exists()
        )

        if self.action == "list" and user_is_lead and user.position:
            return Position.objects.filter(department=user.position.department)

        return super().get_queryset()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Field to order by (use prefix '-' for descending order).",
                enum=ordering_fields + [f"-{field}" for field in ordering_fields],
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.validated_data["created_by"] = self.request.user
            serializer.validated_data["updated_by"] = self.request.user
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.validated_data["updated_by"] = self.request.user
        return super().perform_update(serializer)

    @action(detail=False, methods=["get"])
    def unassigned(self, request, *args, **kwargs):
        """Returns positions that are not assigned to any user."""
        unassigned_positions = Position.objects.filter(user=None)
        page = self.paginate_queryset(unassigned_positions)

        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(unassigned_positions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    search_fields = ["name"]
    ordering_fields = ["name"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Field to order by (use prefix '-' for descending order).",
                enum=ordering_fields + [f"-{field}" for field in ordering_fields],
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
