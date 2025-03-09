import re

from django.contrib.auth import get_user_model
from djoser import serializers as djoser_serializers
from djoser.social.serializers import (
    ProviderAuthSerializer as BaseProviderAuthSerializer,
)
from drf_spectacular.utils import extend_schema_field
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
)

from basedata.models import Position
from basedata.serializers import (
    PositionBasicSerializer,
    RoleSerializer,
)
from config import settings
from users.models import Role

User = get_user_model()


class ProviderAuthSerializer(BaseProviderAuthSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = data["user"]

        if not user.is_not_deactivated:
            raise AuthenticationFailed(
                "Your account has been deactivated, please contact support.",
                code="user_inactive",
            )

        return data


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_role"] = user.groups.first().name if user.groups.exists() else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_not_deactivated:
            raise AuthenticationFailed(
                "Your account has been deactivated, please contact support.",
                code="user_inactive",
            )
        return data


class UserCreateSerializer(djoser_serializers.UserCreateSerializer):
    class Meta(djoser_serializers.UserCreateSerializer.Meta):
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "first_name",
            "last_name",
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]

    def validate_email(self, value):
        allowed_email_domains = settings.ALLOWED_EMAIL_DOMAINS
        allowed_domains_regex = "|".join(
            re.escape(domain) for domain in allowed_email_domains
        )
        pattern = rf"^[a-zA-Z]+\.[a-zA-Z]+@({allowed_domains_regex})$"

        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Email invalid. Please enter a valid email address."
            )

        return value


class UserSerializer(djoser_serializers.UserSerializer):
    role = serializers.SerializerMethodField()
    phone_number = PhoneNumberField(required=False, allow_blank=True, allow_null=True)
    is_active = serializers.BooleanField(source="is_not_deactivated", required=False)
    position = PositionBasicSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "bio",
            "phone_number",
            "position",
            "role",
            "is_active",
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "position",
            "role",
            "created_by",
            "updated_by",
            "created_date",
            "updated_date",
        ]

    @extend_schema_field(RoleSerializer)
    def get_role(self, user):
        user_role = user.groups.first()
        return RoleSerializer(user_role).data if user_role else None


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["profile_picture"]


class RolesAssignSerializer(serializers.Serializer):
    role = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), required=False
    )

    def save(self):
        user = self.context["user"]
        roles = [self.validated_data["role"]] if self.validated_data.get("role") else []
        user.groups.set(roles)
        user.save()
        return user


class PositionAssignSerializer(serializers.Serializer):
    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        required=False,
        allow_null=True,
    )
