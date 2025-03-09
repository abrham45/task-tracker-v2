from rest_framework import permissions
from rest_framework.permissions import DjangoModelPermissions


class CustomDjangoModelPermissions(DjangoModelPermissions):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        model_cls = getattr(getattr(view, "queryset", None), "model", None)

        if request.method in permissions.SAFE_METHODS and model_cls:
            app_label = model_cls._meta.app_label
            model_name = model_cls._meta.model_name
            permission_codename = f"{app_label}.view_{model_name}"
            return request.user.has_perm(permission_codename)

        return super().has_permission(request, view)


class HasRole(permissions.BasePermission):
    """
    Allows access only to users in the specified groups.
    Usage: permission_classes = [HasRole("HR")]
    """

    def __init__(self, allowed_role):
        self.allowed_roles = allowed_role

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name=self.allowed_roles).exists()
        )
