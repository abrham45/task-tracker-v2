from axes.decorators import axes_dispatch
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from djoser.social.views import ProviderAuthView as BaseProviderAuthView
from djoser.views import UserViewSet as DjoserUserViewSet
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
)

from config import settings
from core.permissions import HasRole
from users.filters import UserFilter
from users.serializers import (
    PositionAssignSerializer,
    ProfilePictureSerializer,
    ProviderAuthSerializer,
    RolesAssignSerializer,
    TokenObtainPairSerializer,
    UserCreateSerializer,
    UserSerializer,
)

User = get_user_model()


class ProviderAuthView(BaseProviderAuthView):
    serializer_class = ProviderAuthSerializer
    provider_options = ["google-oauth2"]

    @extend_schema(
        description=(
            "Returns the provider's authorization URL to start the OAuth2 flow."
        ),
        parameters=[
            OpenApiParameter(
                name="provider",
                type=str,
                location=OpenApiParameter.PATH,
                enum=provider_options,
                description="OAuth2 provider.",
            ),
            OpenApiParameter(
                name="redirect_uri",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Redirect URI after successful authentication.",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "authorization_url": {
                            "type": "string",
                            "format": "uri",
                            "description": "Authorization URL to initiate OAuth2 flow.",
                        },
                    },
                },
                description="Authorization URL returned successfully.",
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        redirect_uri = request.GET.get("redirect_uri")
        if redirect_uri not in settings.DJOSER["SOCIAL_AUTH_ALLOWED_REDIRECT_URIS"]:
            return Response(
                {
                    "non_field_errors": [
                        "redirect_uri must be in SOCIAL_AUTH_ALLOWED_REDIRECT_URIS"
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().get(request, *args, **kwargs)

    @extend_schema(
        description=(
            "Receives an OAuth2 authorization code "
            "and exchanges it for an access token."
        ),
        parameters=[
            OpenApiParameter(
                name="provider",
                type=str,
                location=OpenApiParameter.PATH,
                enum=provider_options,
                description="OAuth2 provider.",
            ),
            OpenApiParameter(
                name="state",
                type=str,
                location=OpenApiParameter.QUERY,
                description="State of the OAuth2 authorization code.",
            ),
            OpenApiParameter(
                name="code",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Code to exchange for an access token.",
            ),
        ],
        request={},
        responses={
            200: OpenApiResponse(
                response={
                    "type": "object",
                    "properties": {
                        "access": {
                            "type": "string",
                        },
                        "refresh": {
                            "type": "string",
                        },
                    },
                },
                description="Successful authentication.",
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@method_decorator(axes_dispatch, name="dispatch")
@extend_schema(
    # description=(""),
    request=TokenObtainPairSerializer,
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "access": {
                        "type": "string",
                    },
                    "refresh": {
                        "type": "string",
                    },
                },
            },
        ),
    },
)
class TokenObtainPairView(BaseTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    http_method_names = ["get", "post", "put", "patch"]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filterset_class = UserFilter
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = [
        "email",
        "first_name",
        "last_name",
        "created_date",
        "updated_date",
    ]

    def get_queryset(self):
        user = self.request.user
        user_is_lead = user.groups.filter(name="Leads").exists()
        user_is_hr = user.groups.filter(name="HR").exists()

        if (
            self.action == "list"
            and user_is_lead
            and user.position
            and user.position.department
        ):
            return User.objects.filter(
                position__department=user.position.department, is_active=True
            )

        if self.action in ["list", "assign_position"] and user_is_hr:
            return User.objects.filter(is_active=True)

        return super().get_queryset()

    def get_permissions(self):
        if not self.request.user.is_superuser and self.action in ["assign_position"]:
            return [HasRole("HR")]
        return super().get_permissions()

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

        super().perform_create(serializer)

    def perform_update(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.validated_data["updated_by"] = self.request.user

        super().perform_update(serializer)

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        pass

    def update(self, request, *args, **kwargs):
        new_is_active = request.data.get("is_active")
        user = self.request.user

        if not user.is_superuser and new_is_active != user.is_active:
            raise PermissionDenied(
                {"detail": "You do not have permission to perform this action."}
            )

        return super().update(request, *args, **kwargs)

    @action(
        detail=False,
        methods=["post"],
        url_path="signup",
        serializer_class=UserCreateSerializer,
        permission_classes=[AllowAny],
    )
    def signup(self, request, *args, **kwargs):
        """Custom user creation endpoint at /users/signup/"""
        return super().create(request, *args, **kwargs)

    @extend_schema(request=ProfilePictureSerializer, responses=UserSerializer)
    @action(detail=True, methods=["post"], url_path="upload_profile_picture")
    def upload_profile_picture(self, request, pk=None, *args, **kwargs):
        user = self.get_object()
        serializer = ProfilePictureSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_serializer = UserSerializer(user, context={"request": request})
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ProfilePictureSerializer, responses=UserSerializer)
    @action(detail=False, methods=["post"], url_path="me/upload_profile_picture")
    def me_upload_profile_picture(self, request, *args, **kwargs):
        user = request.user
        serializer = ProfilePictureSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_serializer = UserSerializer(user, context={"request": request})
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=RolesAssignSerializer, responses=UserSerializer)
    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[*DjoserUserViewSet.permission_classes, IsAdminUser],
    )
    def assign_role(self, request, pk=None, *args, **kwargs):
        user = self.get_object()
        serializer = RolesAssignSerializer(data=request.data, context={"user": user})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_serializer = UserSerializer(user, context={"request": request})
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=PositionAssignSerializer, responses=UserSerializer)
    @action(detail=True, methods=["patch"])
    def assign_position(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = PositionAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        position = serializer.validated_data.get("position", None)

        # Check if position is already assigned to another user
        if position and User.objects.filter(position=position).exists():
            return Response(
                {"detail": "Position is already assigned to another user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Assign the position to the current user
        user.position = position
        user.save()

        user_serializer = UserSerializer(user, context=self.get_serializer_context())
        return Response(user_serializer.data, status.HTTP_200_OK)
