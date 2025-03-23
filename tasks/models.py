import os
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.db import models

from core.models import BaseModel

STATUS_CHOICES = (
    ("not_started", "Not Started"),
    ("ongoing", "Ongoing"),
    ("on_review", "On Review"),
    ("completed", "Completed"),
    ("overdue", "Overdue"),
    ("terminated", "Terminated"),
)


def upload_file_to(instance, filename):
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"task-files/{name}-{timestamp}{ext}"


class KSI(BaseModel):
    department = models.ForeignKey(
        "basedata.Department", on_delete=models.PROTECT, related_name="ksis"
    )
    ksi_name = models.CharField(max_length=255)
    ksi_description = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_started"
    )

    created_by = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="ksis_created_by"
    )
    updated_by = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="ksis_updated_by"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "KSI"
        verbose_name_plural = "KSIs"

    def __str__(self):
        return self.ksi_name

    @property
    def completion_percentage(self) -> Decimal:
        milestones = self.milestones.all()
        if not milestones:
            return Decimal("100.00") if self.status == "completed" else Decimal("0.00")

        weighted_completion_percentage = sum(
            (milestone.completion_percentage * milestone.weight) / 100
            for milestone in milestones
        )

        # Automatically update 'status'
        if (
            weighted_completion_percentage == Decimal(100)
            and self.status != "completed"
        ):
            self.status = "completed"
            self.save(update_fields=["status"])

        if self.end_date > datetime.now().date() and self.status != "completed":
            self.status = "overdue"
            self.save(update_fields=["status"])

        return Decimal(weighted_completion_percentage).quantize(
            Decimal("0.00"), rounding=ROUND_HALF_UP
        )


class Milestone(BaseModel):
    ksi = models.ForeignKey(
        "tasks.KSI", on_delete=models.PROTECT, related_name="milestones"
    )
    milestone_name = models.CharField(max_length=255)
    milestone_description = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    weight = models.DecimalField(decimal_places=2, max_digits=10)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_started"
    )

    created_by = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="milestones_created_by"
    )
    updated_by = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="milestones_updated_by"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.milestone_name

    @property
    def completion_percentage(self) -> Decimal:
        kpis = self.kpis.all()
        if not kpis:
            return Decimal(100) if self.status == "completed" else Decimal(0)

        major_activities = MajorActivity.objects.filter(kpi__in=kpis)
        if not major_activities:
            return Decimal("100.00") if self.status == "completed" else Decimal("0.00")

        weighted_completion_percentage = sum(
            (major_activity.completion_percentage * major_activity.weight) / 100
            for major_activity in major_activities
        )

        # Automatically update 'status'
        if (
            weighted_completion_percentage == Decimal(100)
            and self.status != "completed"
        ):
            self.status = "completed"
            self.save(update_fields=["status"])

        if self.end_date > datetime.now().date() and self.status != "completed":
            self.status = "overdue"
            self.save(update_fields=["status"])

        return Decimal(weighted_completion_percentage).quantize(
            Decimal("0.00"), rounding=ROUND_HALF_UP
        )


class KPI(BaseModel):
    STATUS_CHOICES = (
        ("failed", "Failed"),
        ("completed", "Completed"),
        ("pending", "Pending"),
    )
    milestone = models.ForeignKey(
        "tasks.Milestone", on_delete=models.PROTECT, related_name="kpis"
    )
    kpi_name = models.CharField(max_length=255)
    kpi_description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    planed_kpi= models.IntegerField(default=1)

    created_by = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="kpis_created_by"
    )
    updated_by = models.ForeignKey(
        "users.User", on_delete=models.PROTECT, related_name="kpis_updated_by"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"

    def __str__(self):
        return self.kpi_name


class MajorActivity(BaseModel):
    MAX_DAYS_SPAN = timedelta(days=30)

    kpi = models.ForeignKey(
        "tasks.KPI", on_delete=models.PROTECT, related_name="major_activities"
    )
    department = models.ForeignKey(
        "basedata.Department",
        on_delete=models.PROTECT,
        related_name="major_activities",
        null=True,
        blank=True,
    )
    major_activity_name = models.CharField(max_length=255)
    major_activity_description = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    weight = models.DecimalField(decimal_places=2, max_digits=10)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_started"
    )

    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="major_activities_created_by",
    )
    updated_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="major_activities_updated_by",
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Major Activity"
        verbose_name_plural = "Major Activities"
        db_table = "tasks_major_activity"

    def __str__(self):
        return self.major_activity_name

    @property
    def completion_percentage(self) -> Decimal:
        tasks = self.tasks.filter(parent_task=None)
        if not tasks:
            return Decimal("100.00") if self.status == "completed" else Decimal("0.00")

        weighted_completion_percentage = sum(
            (task.completion_percentage * task.weight) / 100 for task in tasks
        )

        # Automatically update 'status'
        if (
            weighted_completion_percentage == Decimal(100)
            and self.status != "completed"
        ):
            self.status = "completed"
            self.save(update_fields=["status"])

        if self.end_date > datetime.now().date() and self.status != "completed":
            self.status = "overdue"
            self.save(update_fields=["status"])

        return Decimal(weighted_completion_percentage).quantize(
            Decimal("0.00"), rounding=ROUND_HALF_UP
        )


class Task(BaseModel):
    APPROVAL_STATUS_CHOICES = (
        ("denied", "Denied"),
        ("approved", "Approved"),
        ("pending", "Pending"),
    )
    MAX_DAYS_SPAN = timedelta(days=30)

    parent_task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.PROTECT,
        related_name="sub_tasks",
        null=True,
        blank=True,
    )
    major_activity = models.ForeignKey(
        "tasks.MajorActivity", on_delete=models.PROTECT, related_name="tasks"
    )
    positions = models.ManyToManyField(
        "basedata.Position", related_name="tasks", blank=True
    )
    task_name = models.CharField(max_length=255)
    task_description = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    weight = models.DecimalField(decimal_places=2, max_digits=10)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_started"
    )
    approval_status = models.CharField(
        max_length=20, choices=APPROVAL_STATUS_CHOICES, default="pending"
    )
    feedback = models.TextField(null=True, blank=True)
    challenge_groups = models.ManyToManyField(
        "basedata.ChallengeGroup", related_name="tasks", blank=True
    )
    other_challenge = models.TextField(null=True, blank=True)
    link = models.URLField(max_length=2048, blank=True, null=True)

    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="tasks_created_by",
    )
    updated_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="tasks_updated_by",
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_name

    @property
    def completion_percentage(self) -> Decimal:
        sub_tasks = self.sub_tasks.all()
        if not sub_tasks:
            return Decimal("100.00") if self.status == "completed" else Decimal("0.00")

        weighted_completion_percentage = sum(
            (sub_task.completion_percentage * sub_task.weight) / 100
            for sub_task in sub_tasks
        )

        # Automatically update 'status'
        if (
            weighted_completion_percentage == Decimal(100)
            and self.status != "completed"
        ):
            self.status = "completed"
            self.save(update_fields=["status"])

        if self.end_date > datetime.now().date() and self.status != "completed":
            self.status = "overdue"
            self.save(update_fields=["status"])

        return Decimal(weighted_completion_percentage).quantize(
            Decimal("0.00"), rounding=ROUND_HALF_UP
        )
