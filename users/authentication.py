from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import (
    JWTAuthentication as BaseJWTAuthentication,
)


class JWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "users.authentication.JWTAuthentication"
    name = "JWTAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }


class JWTAuthentication(BaseJWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        if not user.is_not_deactivated:
            raise AuthenticationFailed(
                "Your account has been deactivated, please contact support.",
                code="user_inactive",
            )

        return user
