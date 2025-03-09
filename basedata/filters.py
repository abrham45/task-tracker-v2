from django_filters import rest_framework as filters

from basedata.models import Department, Position


class PositionFilter(filters.FilterSet):
    departments = filters.ModelMultipleChoiceFilter(
        field_name="department__id",
        help_text="Filter by the ID of departments.",
        to_field_name="id",
        queryset=Department.objects.all(),
    )

    class Meta:
        model = Position
        fields = []
