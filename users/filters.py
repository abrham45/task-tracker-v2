from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django_filters import rest_framework as filters

from basedata.models import Department

User = get_user_model()


class UserFilter(filters.FilterSet):
    departments = filters.ModelMultipleChoiceFilter(
        field_name="position__department__id",
        help_text="Filter by the ID of departments.",
        to_field_name="id",
        queryset=Department.objects.all(),
    )
    roles = filters.ModelMultipleChoiceFilter(
        field_name="groups__id",
        help_text="Filter by the ID of roles.",
        to_field_name="id",
        queryset=Group.objects.all(),
    )

    class Meta:
        model = User
        fields = []
