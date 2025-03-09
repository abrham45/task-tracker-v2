from django.core.validators import MinLengthValidator
from django.db import models

from core.models import BaseModel


class ChallengeType(BaseModel):
    challenge_type_name = models.CharField(
        max_length=50, validators=[MinLengthValidator(2)], unique=True
    )
    challenge_type_description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Challenge Type"
        verbose_name_plural = "Challenge Types"
        db_table = "basedata_challenge_type"

    def __str__(self):
        return self.challenge_type_name


class ChallengeGroup(BaseModel):
    challenge_type = models.ForeignKey(
        "basedata.ChallengeType",
        related_name="challenge_groups",
        on_delete=models.PROTECT,
    )
    challenge_group_name = models.CharField(
        max_length=50, validators=[MinLengthValidator(2)], unique=True
    )
    challenge_group_description = models.TextField(blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Challenge Group"
        verbose_name_plural = "Challenge Groups"
        db_table = "basedata_challenge_group"

    def __str__(self):
        return self.challenge_group_name


class Department(BaseModel):
    department_name = models.CharField(
        max_length=50, validators=[MinLengthValidator(2)], unique=True
    )
    department_description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.department_name


class Position(BaseModel):
    department = models.ForeignKey(
        "basedata.Department", on_delete=models.PROTECT, related_name="positions"
    )
    position_name = models.CharField(
        max_length=50, validators=[MinLengthValidator(2)], unique=True
    )
    position_description = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.position_name
