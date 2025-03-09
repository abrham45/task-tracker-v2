from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"^api/(?P<version>v[0-9]+)/", include("basedata.urls")),
    re_path(r"^api/(?P<version>v[0-9]+)/", include("tasks.urls")),
    re_path(r"^api/(?P<version>v[0-9]+)/", include("users.urls")),
    # Documentation
    re_path(
        r"^api/(?P<version>v[0-9]+)/schema/$",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    re_path(
        r"^api/(?P<version>v[0-9]+)/docs/swagger-ui/$",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
