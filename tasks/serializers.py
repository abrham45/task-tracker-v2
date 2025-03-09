from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Sum
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_serializer,
)
from rest_framework import serializers

from basedata.models import ChallengeGroup, Department, Position
from basedata.serializers import (
    ChallengeGroupBasicSerializer,
    DepartmentBasicSerializer,
)
from tasks.models import (
    KPI,
    KSI,
    MajorActivity,
    Milestone,
    Task,
)


def validate_weight_sum(
    value, queryset, message_part, instance=None, max_weight=Decimal("100.00")
):
    """
    Validate that the weight does not cause
    the total weight of related objects to exceed max_weight.
    """
    current_total_weight = queryset.exclude(pk=getattr(instance, "id", None)).aggregate(
        total_weight=Sum("weight")
    ).get("total_weight") or Decimal("0.00")
    total_weight = current_total_weight + Decimal(value)

    if total_weight > max_weight:
        raise serializers.ValidationError(
            f"The total weight for {message_part} cannot exceed {max_weight}."
            f" Current total: {current_total_weight}."
        )

    return value


User = get_user_model()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Example KSI",
            description="An example of a KSI object.",
            value={
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "string",
                "description": "string",
                "department": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "string",
                },
                "start_date": "2025-02-23",
                "end_date": "2025-02-23",
                "completion_percentage": 0,
                "status": "not_started",
                "created_date": "2025-02-23T12:33:07.680Z",
                "updated_date": "2025-02-23T12:33:07.680Z",
            },
            response_only=True,
        )
    ]
)
class KSISerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="ksi_name")
    description = serializers.CharField(
        source="ksi_description", required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = KSI
        fields = [
            "id",
            "name",
            "description",
            "department",
            "start_date",
            "end_date",
            "completion_percentage",
            "status",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "department",
            "created_date",
            "updated_date",
        ]

    def validate_end_date(self, value):
        start_date = self.initial_data.get("start_date")

        if start_date:
            start_date = serializers.DateField().to_internal_value(start_date)
            if value < start_date:
                raise serializers.ValidationError(
                    "End date can't be earlier than start date."
                )

        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["department"] = DepartmentBasicSerializer(
            instance.department
        ).data
        return representation


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Example KSI",
            description="An example of a KSI object.",
            value={
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "ksi": {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "name": "string"},
                "name": "string",
                "description": "string",
                "weight": "5",
                "start_date": "2025-02-23",
                "end_date": "2025-02-23",
                "completion_percentage": 0,
                "status": "not_started",
                "created_date": "2025-02-23T21:41:03.198Z",
                "updated_date": "2025-02-23T21:41:03.198Z",
            },
            response_only=True,
        )
    ]
)
class MilestoneSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="milestone_name")
    description = serializers.CharField(
        source="milestone_description",
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    ksi = serializers.PrimaryKeyRelatedField(queryset=KSI.objects.all())

    class Meta:
        model = Milestone
        fields = [
            "id",
            "ksi",
            "name",
            "description",
            "weight",
            "start_date",
            "end_date",
            "completion_percentage",
            "status",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["created_date", "updated_date"]

    def validate_start_date(self, value):
        ksi = self.initial_data.get("ksi", None)
        if not ksi and self.instance and self.instance.ksi:
            ksi = self.instance.ksi.id

        if ksi:
            try:
                ksi_instance = KSI.objects.get(id=ksi)
            except KSI.DoesNotExist:
                return value

            min_start_date = ksi_instance.start_date
            if value < min_start_date:
                raise serializers.ValidationError(
                    f"Start date can't be earlier than '{min_start_date}',"
                    f" start date of KSI '{ksi_instance.ksi_name}'"
                )
        return value

    def validate_end_date(self, value):
        start_date = self.initial_data.get("start_date")

        if start_date:
            start_date = serializers.DateField().to_internal_value(start_date)
            if value < start_date:
                raise serializers.ValidationError(
                    "End date can't be earlier than start date."
                )

        ksi = self.initial_data.get("ksi", None)
        if not ksi and self.instance and self.instance.ksi:
            ksi = self.instance.ksi.id

        if ksi:
            try:
                ksi_instance = KSI.objects.get(id=ksi)
            except KSI.DoesNotExist:
                return value

            max_end_date = ksi_instance.end_date
            if value > max_end_date:
                raise serializers.ValidationError(
                    f"End date can't be later than '{max_end_date}',"
                    f" end date of KSI '{ksi_instance.ksi_name}'"
                )

        return value

    def validate_weight(self, value):
        ksi = self.initial_data.get("ksi", None)
        if not ksi and self.instance and self.instance.ksi:
            ksi = self.instance.ksi.id

        if ksi:
            if not (Decimal("0.00") <= value <= Decimal("100.00")):
                raise serializers.ValidationError(
                    "Weight must be between 0.00 and 100.00."
                )

            try:
                ksi_instance = KSI.objects.get(id=ksi)
            except KSI.DoesNotExist:
                return value

            queryset = ksi_instance.milestones.all()
            message_part = f"milestones under the KSI '{ksi_instance.ksi_name}'"
            return validate_weight_sum(value, queryset, message_part, self.instance)
        else:
            return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["ksi"] = (
            {"id": instance.ksi.id, "name": instance.ksi.ksi_name}
            if instance.ksi
            else None
        )
        return representation


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Example KSI",
            description="An example of a KSI object.",
            value={
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "milestone": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "string",
                },
                "name": "string",
                "description": "string",
                "start_date": "2025-02-23",
                "end_date": "2025-02-23",
                "status": "pending",
                "created_by": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "updated_by": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            },
            response_only=True,
        )
    ]
)
class KPISerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="kpi_name")
    description = serializers.CharField(
        source="kpi_description", required=False, allow_blank=True, allow_null=True
    )
    milestone = serializers.PrimaryKeyRelatedField(queryset=Milestone.objects.all())

    class Meta:
        model = KPI
        fields = [
            "id",
            "milestone",
            "name",
            "description",
            "start_date",
            "end_date",
            "status",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["created_date", "updated_date"]

    def validate_start_date(self, value):
        milestone = self.initial_data.get("milestone", None)
        if not milestone and self.instance and self.instance.milestone:
            milestone = self.instance.milestone.id

        if milestone:
            try:
                milestone_instance = Milestone.objects.get(pk=milestone)
            except Milestone.DoesNotExist:
                return value

            min_start_date = milestone_instance.start_date
            if value < min_start_date:
                raise serializers.ValidationError(
                    f"Start date can't be earlier than '{min_start_date}',"
                    f" start date of milestone '{milestone_instance.milestone_name}'"
                )
        return value

    def validate_end_date(self, value):
        start_date = self.initial_data.get("start_date")

        if start_date:
            start_date = serializers.DateField().to_internal_value(start_date)
            if value < start_date:
                raise serializers.ValidationError(
                    "End date can't be earlier than the start date."
                )

        milestone = self.initial_data.get("milestone", None)
        if not milestone and self.instance and self.instance.milestone:
            milestone = self.instance.milestone.id

        if milestone:
            try:
                milestone_instance = Milestone.objects.get(pk=milestone)
            except Milestone.DoesNotExist:
                return value

            max_end_date = milestone_instance.end_date
            if value > max_end_date:
                raise serializers.ValidationError(
                    f"Start date can't be later than '{max_end_date}',"
                    f" end date of milestone '{milestone_instance.milestone_name}'"
                )

        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["milestone"] = (
            {"id": instance.milestone.id, "name": instance.milestone.milestone_name}
            if instance.milestone
            else None
        )
        return representation


class KSIBasicSerializer(KSISerializer):
    class Meta:
        model = KSI
        fields = ["id", "name"]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Example KSI",
            description="An example of a KSI object.",
            value={
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "milestone": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "string",
                },
                "department": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "string",
                },
                "name": "string",
                "description": "string",
                "weight": "",
                "start_date": "2025-02-23",
                "end_date": "2025-02-23",
                "completion_percentage": 0,
                "status": "not_started",
                "created_date": "2025-02-23T21:47:47.792Z",
                "updated_date": "2025-02-23T21:47:47.792Z",
            },
            response_only=True,
        )
    ]
)
class MajorActivitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="major_activity_name")
    description = serializers.CharField(
        source="major_activity_description",
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    kpi = serializers.PrimaryKeyRelatedField(queryset=KPI.objects.all())
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = MajorActivity
        fields = [
            "id",
            "kpi",
            "department",
            "name",
            "description",
            "weight",
            "start_date",
            "end_date",
            "completion_percentage",
            "status",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["created_date", "updated_date"]

    def validate_start_date(self, value):
        kpi = self.initial_data.get("kpi", None)
        if not kpi and self.instance and self.instance.kpi:
            kpi = self.instance.kpi.id

        if kpi:
            try:
                kpi_instance = KPI.objects.get(pk=kpi)
            except KPI.DoesNotExist:
                return value

            min_start_date = kpi_instance.start_date
            if value < min_start_date:
                raise serializers.ValidationError(
                    f"Start date can't be earlier than '{min_start_date}',"
                    f" start date of KPI '{kpi_instance.kpi_name}'"
                )
        return value

    def validate_end_date(self, value):
        start_date = self.initial_data.get("start_date")

        if start_date:
            start_date = serializers.DateField().to_internal_value(start_date)
            if value < start_date:
                raise serializers.ValidationError(
                    "End date can't be earlier than start date."
                )

            max_end_date = start_date + MajorActivity.MAX_DAYS_SPAN
            if value > max_end_date:
                raise serializers.ValidationError(
                    f"End date can't be later than '{max_end_date}'"
                    f" as major activities cannot exceed"
                    f" '{MajorActivity.MAX_DAYS_SPAN}' period."
                )

        kpi = self.initial_data.get("kpi", None)
        if not kpi and self.instance and self.instance.kpi:
            kpi = self.instance.kpi.id

        if kpi:
            try:
                kpi_instance = KPI.objects.get(pk=kpi)
            except KPI.DoesNotExist:
                return value

            max_end_date = kpi_instance.end_date
            if value > max_end_date:
                raise serializers.ValidationError(
                    f"End date can't be later than '{max_end_date}',"
                    f" end date of KPI '{kpi_instance.kpi_name}'"
                )

        return value

    def validate_weight(self, value):
        kpi = self.initial_data.get("kpi", None)
        if not kpi and self.instance and self.instance.kpi:
            kpi = self.instance.kpi.id

        if kpi:
            if not (Decimal("0.00") <= value <= Decimal("100.00")):
                raise serializers.ValidationError(
                    "Weight must be between 0.00 and 100.00."
                )

            try:
                kpi_instance = KPI.objects.get(pk=kpi)
            except KPI.DoesNotExist:
                return value

            queryset = kpi_instance.major_activities.all()
            message_part = f"major activities under the KPI '{kpi_instance.kpi_name}'"
            return validate_weight_sum(value, queryset, message_part, self.instance)
        else:
            return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["kpi"] = (
            {"id": instance.kpi.id, "name": instance.kpi.kpi_name}
            if instance.kpi
            else None
        )
        representation["department"] = (
            {"id": instance.department.id, "name": instance.department.department_name}
            if instance.department
            else None
        )
        return representation


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Example KSI",
            description="An example of a KSI object.",
            value={
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "parent_task": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "string",
                },
                "major_activity": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "string",
                },
                "positions": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "name": "string",
                        "user": {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "name": "string",
                        },
                    }
                ],
                "name": "string",
                "description": "string",
                "weight": "50",
                "start_date": "2025-02-23",
                "end_date": "2025-02-23",
                "actual_start_date": "2025-02-23",
                "actual_end_date": "2025-02-23",
                "completion_percentage": 0,
                "status": "not_started",
                "approval_status": "denied",
                "feedback": "string",
                "files": ["string"],
                "sub_tasks": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "parent_task": {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "name": "string",
                        },
                        "major_activity": {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "name": "string",
                        },
                        "positions": [
                            {
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "name": "string",
                                "user": {
                                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                    "name": "string",
                                },
                            }
                        ],
                        "name": "string",
                        "description": "string",
                        "weight": "50",
                        "start_date": "2025-02-23",
                        "end_date": "2025-02-23",
                        "actual_start_date": "2025-02-23",
                        "actual_end_date": "2025-02-23",
                        "completion_percentage": 0,
                        "status": "not_started",
                        "approval_status": "denied",
                        "feedback": "string",
                        "files": ["string"],
                        "sub_tasks": [],
                        "challenge_groups": [
                            {
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "name": "string",
                                "challenge_type": {
                                    "id": "",
                                    "name": "",
                                },
                            }
                        ],
                        "other_challenge": "string",
                        "link": "string",
                        "created_date": "2025-02-23T21:49:42.393Z",
                        "updated_date": "2025-02-23T21:49:42.393Z",
                    }
                ],
                "challenge_groups": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "name": "string",
                        "challenge_type": {
                            "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "name": "string",
                        },
                    }
                ],
                "other_challenge": "string",
                "link": "string",
                "created_date": "2025-02-23T21:49:42.393Z",
                "updated_date": "2025-02-23T21:49:42.393Z",
            },
            response_only=True,
        )
    ]
)
class TaskSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="task_name")
    description = serializers.CharField(
        source="task_description", required=False, allow_null=True, allow_blank=True
    )
    parent_task = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(), required=False, allow_null=True
    )
    major_activity = serializers.PrimaryKeyRelatedField(
        queryset=MajorActivity.objects.all()
    )
    positions = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        many=True,
        required=False,
        allow_empty=True,
        allow_null=True,
    )
    actual_start_date = serializers.DateField(required=False, allow_null=True)
    sub_tasks = serializers.SerializerMethodField()
    challenge_groups = serializers.PrimaryKeyRelatedField(
        queryset=ChallengeGroup.objects.all(),
        many=True,
        required=False,
        allow_empty=True,
        allow_null=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "parent_task",
            "major_activity",
            "positions",
            "name",
            "description",
            "weight",
            "start_date",
            "end_date",
            "actual_start_date",
            "actual_end_date",
            "completion_percentage",
            "status",
            "approval_status",
            "feedback",
            "sub_tasks",
            "challenge_groups",
            "other_challenge",
            "link",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "sub_tasks",
            "positions",
            "created_date",
            "updated_date",
        ]

    def get_sub_tasks(self, obj):
        sub_tasks = obj.sub_tasks.all()
        return TaskSerializer(sub_tasks, many=True).data

    def validate_start_date(self, value):
        major_activity = self.initial_data.get("major_activity", None)
        if not major_activity and self.instance and self.instance.major_activity:
            major_activity = self.instance.major_activity.id

        if major_activity:
            parent_task = self.initial_data.get("parent_task", None)
            if not parent_task and self.instance and self.instance.parent_task:
                parent_task = self.instance.parent_task.id

            if parent_task:
                try:
                    parent_task_instance = Task.objects.get(id=parent_task)
                except Task.DoesNotExist:
                    return value

                min_start_date = parent_task_instance.start_date
                if value < min_start_date:
                    raise serializers.ValidationError(
                        f"Start date can't be earlier than '{min_start_date}',"
                        f" start date of parent task '{parent_task_instance.task_name}'"
                    )
            else:
                try:
                    major_activity_instance = MajorActivity.objects.get(
                        pk=major_activity
                    )
                except MajorActivity.DoesNotExist:
                    return value

                min_start_date = major_activity_instance.start_date
                if value < min_start_date:
                    raise serializers.ValidationError(
                        f"Start date can't be earlier than '{min_start_date}',"
                        f" start date of major activity"
                        f" '{major_activity_instance.major_activity_name}'"
                    )
        return value

    def validate_end_date(self, value):
        start_date = self.initial_data.get("start_date")

        if start_date:
            start_date = serializers.DateField().to_internal_value(start_date)
            if value < start_date:
                raise serializers.ValidationError(
                    "End date can't be earlier than start date."
                )

            max_end_date = start_date + Task.MAX_DAYS_SPAN
            if value > max_end_date:
                raise serializers.ValidationError(
                    f"End date can't be later than '{max_end_date}'"
                    f" as tasks cannot exceed '{Task.MAX_DAYS_SPAN}' period."
                )

        major_activity = self.initial_data.get("major_activity", None)
        if not major_activity and self.instance and self.instance.major_activity:
            major_activity = self.instance.major_activity.id

        if major_activity:
            parent_task = self.initial_data.get("parent_task", None)
            if not parent_task and self.instance and self.instance.parent_task:
                parent_task = self.instance.parent_task.id

            if parent_task:
                try:
                    parent_task_instance = Task.objects.get(id=parent_task)
                except Task.DoesNotExist:
                    return value

                max_end_date = parent_task_instance.end_date
                if value > max_end_date:
                    raise serializers.ValidationError(
                        f"End date can't be later than '{max_end_date}',"
                        f" end date of parent task '{parent_task_instance.task_name}'"
                    )
                pass
            else:
                try:
                    major_activity_instance = MajorActivity.objects.get(
                        pk=major_activity
                    )
                except MajorActivity.DoesNotExist:
                    return value

                max_end_date = major_activity_instance.end_date
                if value > max_end_date:
                    raise serializers.ValidationError(
                        f"End date can't be later than '{max_end_date}',"
                        f" end date of major activity"
                        f" '{major_activity_instance.major_activity_name}'"
                    )

        return value

    def validate_actual_end_date(self, value):
        actual_start_date = self.initial_data.get("actual_start_date")

        if actual_start_date:
            actual_start_date = serializers.DateField().to_internal_value(
                actual_start_date
            )
            if value < actual_start_date:
                raise serializers.ValidationError(
                    "Actual end date can't be earlier than start date."
                )

        return value

    def validate_weight(self, value):
        major_activity = self.initial_data.get("major_activity", None)
        if not major_activity and self.instance and self.instance.major_activity:
            major_activity = self.instance.major_activity.id

        if major_activity:
            if not (Decimal("0.00") <= value <= Decimal("100.00")):
                raise serializers.ValidationError(
                    "Weight must be between 0.00 and 100.00."
                )

            parent_task = self.initial_data.get("parent_task", None)
            if not parent_task and self.instance and self.instance.parent_task:
                parent_task = self.instance.parent_task.id

            if parent_task:
                try:
                    parent_task_instance = Task.objects.get(id=parent_task)
                except Task.DoesNotExist:
                    return value

                queryset = Task.objects.filter(parent_task=parent_task_instance)
                message_part = (
                    f"subtasks under the task '{parent_task_instance.task_name}'"
                )
                return validate_weight_sum(value, queryset, message_part, self.instance)
            else:
                try:
                    major_activity_instance = MajorActivity.objects.get(
                        pk=major_activity
                    )
                except MajorActivity.DoesNotExist:
                    return value

                queryset = Task.objects.filter(
                    major_activity=major_activity_instance, parent_task=None
                )
                message_part = (
                    f"tasks under the major activity"
                    f" '{major_activity_instance.major_activity_name}'"
                )
                return validate_weight_sum(value, queryset, message_part, self.instance)

        else:
            return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["parent_task"] = (
            {"id": instance.parent_task.id, "name": instance.parent_task.task_name}
            if instance.parent_task
            else None
        )
        representation["major_activity"] = (
            {
                "id": instance.major_activity.id,
                "name": instance.major_activity.major_activity_name,
            }
            if instance.major_activity
            else None
        )
        representation["positions"] = [
            {
                "id": position.id,
                "name": position.position_name,
                "user": (
                    {
                        "id": position.user.id,
                        "name": f"{position.user.first_name} {position.user.last_name}",
                    }
                    if getattr(position, "user", None)
                    else None
                ),
            }
            for position in instance.positions.all()
        ]
        representation["challenge_groups"] = ChallengeGroupBasicSerializer(
            instance.challenge_groups.all(), many=True
        ).data
        return representation


class TaskPositionSerializer(serializers.ModelSerializer):
    positions = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Position.objects.all())
    )

    class Meta:
        model = Task
        fields = ["positions"]


class MajorActivityNestedSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="major_activity_name")

    class Meta:
        model = MajorActivity
        fields = ["id", "name"]


class KPINestedSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="kpi_name")
    major_activities = MajorActivityNestedSerializer(many=True, read_only=True)

    class Meta:
        model = KPI
        fields = ["id", "name", "major_activities"]


class MilestoneNestedSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="milestone_name")
    kpis = KPINestedSerializer(many=True, read_only=True)

    class Meta:
        model = Milestone
        fields = ["id", "name", "kpis"]


class KSINestedSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="ksi_name")
    milestones = MilestoneNestedSerializer(many=True, read_only=True)

    class Meta:
        model = KSI
        fields = ["id", "name", "milestones"]
