from rest_framework_simplejwt.tokens import RefreshToken


class TokenStrategy:
    @classmethod
    def obtain(cls, user):
        refresh = RefreshToken.for_user(user)

        refresh.payload["user_role"] = (
            user.groups.first().name if user.groups.exists() else None
        )

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
