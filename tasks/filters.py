from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from basedata.models import Department, Position
from tasks.models import (
    KPI,
    KSI,
    STATUS_CHOICES,
    MajorActivity,
    Milestone,
    Task,
)

User = get_user_model()


class KSIFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(
        field_name="status",
        help_text="Filter by status",
        choices=STATUS_CHOICES,
        lookup_expr="in",
    )
    departments = filters.ModelMultipleChoiceFilter(
        field_name="department__id",
        help_text="Filter by the ID of departments.",
        to_field_name="id",
        queryset=Department.objects.all(),
    )

    class Meta:
        model = KSI
        fields = []


class MilestoneFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(
        field_name="status",
        help_text="Filter by status",
        choices=STATUS_CHOICES,
        lookup_expr="in",
    )
    departments = filters.ModelMultipleChoiceFilter(
        field_name="ksi__department__id",
        help_text="Filter by the ID of departments.",
        to_field_name="id",
        queryset=Department.objects.all(),
    )
    ksi = filters.ModelMultipleChoiceFilter(
        field_name="ksi__id",
        help_text="Filter by the ID of KSIs.",
        to_field_name="id",
        queryset=KSI.objects.all(),
    )

    class Meta:
        model = Milestone
        fields = []


class KPIFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(
        field_name="status",
        help_text="Filter by status",
        choices=KPI.STATUS_CHOICES,
        lookup_expr="in",
    )
    departments = filters.ModelMultipleChoiceFilter(
        field_name="milestone__ksi__department__id",
        help_text="Filter by the ID of departments.",
        to_field_name="id",
        queryset=Department.objects.all(),
    )
    ksi = filters.ModelMultipleChoiceFilter(
        field_name="milestone__ksi__id",
        help_text="Filter by the ID of KSIs.",
        to_field_name="id",
        queryset=KSI.objects.all(),
    )
    milestone = filters.ModelMultipleChoiceFilter(
        field_name="milestone__id",
        help_text="Filter by the ID of milestones.",
        to_field_name="id",
        queryset=Milestone.objects.all(),
    )

    class Meta:
        model = KPI
        fields = []


class MajorActivityFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(
        field_name="status",
        help_text="Filter by status",
        choices=STATUS_CHOICES,
        lookup_expr="in",
    )
    departments = filters.ModelMultipleChoiceFilter(
        field_name="department__id",
        help_text="Filter by the ID of departments.",
        to_field_name="id",
        queryset=Department.objects.all(),
    )
    ksi = filters.ModelMultipleChoiceFilter(
        field_name="kpi__milestone__ksi__id",
        help_text="Filter by the ID of KSIs.",
        to_field_name="id",
        queryset=KSI.objects.all(),
    )
    milestone = filters.ModelMultipleChoiceFilter(
        field_name="kpi__milestone__id",
        help_text="Filter by the ID of milestones.",
        to_field_name="id",
        queryset=Milestone.objects.all(),
    )
    kpi = filters.ModelMultipleChoiceFilter(
        field_name="kpi__id",
        help_text="Filter by the ID of KPIs.",
        to_field_name="id",
        queryset=KPI.objects.all(),
    )

    class Meta:
        model = MajorActivity
        fields = []


class TaskFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(
        field_name="status",
        help_text="Filter by status",
        choices=STATUS_CHOICES,
        lookup_expr="in",
    )
    approval_status = filters.MultipleChoiceFilter(
        field_name="approval_status",
        help_text="Filter by approval status",
        choices=Task.APPROVAL_STATUS_CHOICES,
        lookup_expr="in",
    )
    departments = filters.ModelMultipleChoiceFilter(
        field_name="major_activity__department__id",
        help_text="Filter by the ID of departments.",
        to_field_name="id",
        queryset=Department.objects.all(),
    )
    ksi = filters.ModelMultipleChoiceFilter(
        field_name="major_activity__kpi__milestone__ksi__id",
        help_text="Filter by the ID of KSIs.",
        to_field_name="id",
        queryset=KSI.objects.all(),
    )
    milestone = filters.ModelMultipleChoiceFilter(
        field_name="major_activity__kpi__milestone__id",
        help_text="Filter by the ID of milestones.",
        to_field_name="id",
        queryset=Milestone.objects.all(),
    )
    kpi = filters.ModelMultipleChoiceFilter(
        field_name="major_activity__kpi__id",
        help_text="Filter by the ID of KPIs.",
        to_field_name="id",
        queryset=KPI.objects.all(),
    )
    major_activity = filters.ModelMultipleChoiceFilter(
        field_name="major_activity__id",
        help_text="Filter by the ID of Major Activities.",
        to_field_name="id",
        queryset=MajorActivity.objects.all(),
    )
    position = filters.ModelMultipleChoiceFilter(
        field_name="positions__id",
        help_text="Filter by the ID of position.",
        to_field_name="id",
        queryset=Position.objects.all(),
    )
    parent_task = filters.ModelMultipleChoiceFilter(
        field_name="parent_task__id",
        help_text="Filter by the ID of the parent task.",
        to_field_name="id",
        queryset=Task.objects.all(),
    )

    class Meta:
        model = Task
        fields = []
