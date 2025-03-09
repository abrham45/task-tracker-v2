from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from users.views import (
    ProviderAuthView,
    TokenObtainPairView,
    UserViewSet,
)

router = DefaultRouter()

router.register("users", UserViewSet, "user")

urlpatterns = [
    path("", include(router.urls)),
    path("users/login", TokenObtainPairView.as_view(), name="jwt-create"),
    path("users/token/refresh", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("users/token/verify", TokenVerifyView.as_view(), name="jwt-verify"),
    re_path(
        r"^users/oauth/(?P<provider>\S+)/$",
        ProviderAuthView.as_view(),
        name="provider-auth",
    ),
]
