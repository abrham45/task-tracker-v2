from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.permissions import HasRole
from tasks.filters import (
    KPIFilter,
    KSIFilter,
    MajorActivityFilter,
    MilestoneFilter,
    TaskFilter,
)
from tasks.models import KPI, KSI, MajorActivity, Milestone, Task
from tasks.serializers import (
    KPISerializer,
    KSINestedSerializer,
    KSISerializer,
    MajorActivitySerializer,
    MilestoneSerializer,
    TaskPositionSerializer,
    TaskSerializer,
)


class KSIViewSet(viewsets.ModelViewSet):
    queryset = KSI.objects.all()
    serializer_class = KSISerializer
    search_fields = ["ksi_name"]
    filterset_class = KSIFilter
    ordering_fields = [
        "ksi_name",
        "start_date",
        "end_date",
        "created_date",
        "updated_date",
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        user_is_lead = (
            user.is_authenticated and user.groups.filter(name="Leads").exists()
        )

        if user.position and user.position.department and user_is_lead:
            queryset = queryset.filter(department=user.position.department)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Field to order by (user prefix '-' for descending order).",
                enum=ordering_fields + [f"-{field}" for field in ordering_fields],
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.position or not user.position.department:
            return Response(
                {
                    "detail": "You are not authorized to perform this action,"
                    " no associated department."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.validated_data["created_by"] = user
        serializer.validated_data["updated_by"] = user
        serializer.validated_data["department"] = user.position.department
        serializer.save()

    def perform_update(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.validated_data["updated_by"] = self.request.user

        return super().perform_update(serializer)

    @extend_schema(responses=KSINestedSerializer(many=True))
    @action(detail=False, methods=["get"], pagination_class=None)
    def structure(self, request, *args, **kwargs):
        user = self.request.user
        queryset = self.get_queryset()

        user_is_lead = (
            user.is_authenticated and user.groups.filter(name="Leads").exists()
        )

        if user.position and user.position.department and user_is_lead:
            queryset = queryset.filter(department=user.position.department)

        serializer = KSINestedSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    search_fields = ["milestone_name"]
    filterset_class = MilestoneFilter
    ordering_fields = [
        "milestone_name",
        "weight",
        "start_date",
        "end_date",
        "created_date",
        "updated_date",
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        user_is_lead = (
            user.is_authenticated and user.groups.filter(name="Leads").exists()
        )

        if user.position and user.position.department and user_is_lead:
            queryset = queryset.filter(ksi__department=user.position.department)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Field to order by (user prefix '-' for descending order).",
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


class KPIViewSet(viewsets.ModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer
    search_fields = ["kpi_name"]
    filterset_class = KPIFilter
    ordering_fields = [
        "kpi_name",
        "start_date",
        "end_date",
        "created_date",
        "updated_date",
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        user_is_lead = (
            user.is_authenticated and user.groups.filter(name="Leads").exists()
        )

        if user.position and user.position.department and user_is_lead:
            queryset = queryset.filter(
                milestone__ksi__department=user.position.department
            )

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Field to order by (user prefix '-' for descending order).",
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


class MajorActivityViewSet(viewsets.ModelViewSet):
    queryset = MajorActivity.objects.all()
    serializer_class = MajorActivitySerializer
    search_fields = ["major_activity_name"]
    filterset_class = MajorActivityFilter
    ordering_fields = [
        "major_activity_name",
        "weight",
        "start_date",
        "end_date",
        "created_date",
        "updated_date",
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        user_is_lead = (
            user.is_authenticated and user.groups.filter(name="Leads").exists()
        )

        if user.position and user.position.department and user_is_lead:
            queryset = queryset.filter(
                Q(department=user.position.department)
                | Q(kpi__milestone__ksi__department=user.position.department)
            )

        return queryset

    def get_permissions(self):
        if self.action == "assign":
            return HasRole("Leads")
        return super().get_permissions()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Field to order by (user prefix '-' for descending order).",
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

    @extend_schema(responses=MajorActivitySerializer(many=True))
    @action(methods=["get"], detail=False)
    def assigned(self, request, *args, **kwargs):
        user = request.user
        major_activities = self.queryset

        if not (user and user.position and user.position.department):
            assigned_major_activities = major_activities.none()
        else:
            assigned_major_activities = major_activities.filter(
                department=request.user.position.department
            )

        page = self.paginate_queryset(assigned_major_activities)
        serializer = MajorActivitySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    search_fields = ["task_name"]
    filterset_class = TaskFilter
    ordering_fields = [
        "task_name",
        "weight",
        "start_date",
        "end_date",
        "actual_start_date",
        "actual_end_date",
        "created_date",
        "updated_date",
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        user_is_lead = (
            user.is_authenticated and user.groups.filter(name="Leads").exists()
        )
        user_is_expert = (
            user.is_authenticated and user.groups.filter(name="Experts").exists()
        )

        if user.position and user.position.department and user_is_lead:
            queryset = queryset.filter(
                Q(major_activity__department=user.position.department)
                | Q(
                    major_activity__kpi__milestone__ksi__department=user.position.department
                )
            )

        if user.position and user_is_expert:
            expert_tasks = queryset.filter(positions=user.position)
            expert_sub_tasks = queryset.filter(parent_task__in=expert_tasks)
            queryset = expert_tasks | expert_sub_tasks
            queryset = queryset.distinct()

        # get only parent tasks on list to embed subtasks
        if self.action == "list":
            queryset = queryset.filter(parent_task=None)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Field to order by (user prefix '-' for descending order).",
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        old_approval_status = instance.approval_status
        new_status = request.data.get("status")
        new_approval_status = request.data.get("approval_status")
        user = self.request.user

        user_is_lead = user.groups.filter(name="Leads").exists()
        user_is_operation_team = user.groups.filter(name="Operation-Team").exists()

        is_status_being_updated = old_status != new_status
        is_approval_status_being_updated = old_approval_status != new_approval_status

        # Check if the status is being changed to "completed"
        if (
            new_status
            and is_status_being_updated
            and new_status == "completed"
            and not user_is_lead
        ):
            raise PermissionDenied(
                {
                    "detail": "You do not have permission to perform this action,"
                    "Only users with role 'Leads' can mark tasks 'completed'."
                }
            )

        # Check if the approval status is being changed
        if (
            new_approval_status
            and is_approval_status_being_updated
            and not user_is_operation_team
        ):
            raise PermissionDenied(
                {
                    "detail": "You do not have permission to perform this action,"
                    "Only users with role 'Operation-Team' can mark tasks 'approved'."
                }
            )

        return super().update(request, *args, **kwargs)

    @extend_schema(request=TaskPositionSerializer, responses=TaskSerializer)
    @action(detail=True, methods=["patch"])
    def add_positions(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = TaskPositionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        positions = serializer.validated_data["positions"]

        task.positions.add(*positions)

        task_serializer = TaskSerializer(task, context={"request": request})
        return Response(task_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=TaskPositionSerializer, responses=TaskSerializer)
    @action(detail=True, methods=["patch"])
    def remove_positions(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = TaskPositionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        positions = serializer.validated_data["positions"]
        task.positions.remove(*positions)

        task_serializer = TaskSerializer(task, context={"request": request})
        return Response(task_serializer.data, status=status.HTTP_200_OK)
