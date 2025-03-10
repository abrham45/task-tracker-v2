from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as Role
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from basedata.models import ChallengeGroup, ChallengeType, Department, Position

User = get_user_model()


class ChallengeTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source="challenge_type_name",
        min_length=2,
        validators=[UniqueValidator(queryset=ChallengeType.objects.all())],
    )
    description = serializers.CharField(
        source="challenge_type_description",
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    class Meta:
        model = ChallengeType
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]


class ChallengeTypeBasicSerializer(ChallengeTypeSerializer):
    class Meta:
        model = ChallengeType
        fields = ["id", "name"]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Example Challenge Group",
            description="An example of a Challenge Group object.",
            value={
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "string",
                "description": "string",
                "challenge_type": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "string",
                },
                "created_by": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "updated_by": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "created_date": "2025-02-23T16:11:30.797Z",
                "updated_date": "2025-02-23T16:11:30.797Z",
            },
            response_only=True,
        )
    ]
)
class ChallengeGroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source="challenge_group_name",
        min_length=2,
        validators=[UniqueValidator(queryset=ChallengeGroup.objects.all())],
    )
    description = serializers.CharField(
        source="challenge_group_description",
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    class Meta:
        model = ChallengeGroup
        fields = [
            "id",
            "challenge_type",
            "name",
            "description",
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["challenge_type"] = ChallengeTypeBasicSerializer(
            instance.challenge_type
        ).data
        return representation


class ChallengeGroupBasicSerializer(ChallengeGroupSerializer):
    class Meta:
        model = ChallengeGroup
        fields = ["id", "challenge_type", "name"]


class DepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source="department_name",
        min_length=2,
        validators=[UniqueValidator(queryset=Department.objects.all())],
    )
    description = serializers.CharField(
        source="department_description",
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]


class DepartmentBasicSerializer(DepartmentSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Example Position",
            description="An example of a Position object.",
            value={
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "string",
                "description": "string",
                "department": {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "string",
                },
                "created_by": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "updated_by": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "created_date": "2025-02-23T16:11:30.797Z",
                "updated_date": "2025-02-23T16:11:30.797Z",
            },
            response_only=True,
        )
    ]
)
class PositionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        source="position_name",
        validators=[UniqueValidator(queryset=Position.objects.all())],
        min_length=2,
    )
    description = serializers.CharField(
        source="position_description", required=False, allow_blank=True, allow_null=True
    )

    class Meta:
        model = Position
        fields = [
            "id",
            "name",
            "description",
            "department",
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["department"] = DepartmentBasicSerializer(
            instance.department
        ).data
        return representation


class PositionBasicSerializer(PositionSerializer):
    department = DepartmentBasicSerializer()

    class Meta:
        model = Position
        fields = ["id", "name", "department"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name"]
