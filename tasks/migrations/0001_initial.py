# Generated by Django 5.1.7 on 2025-03-26 09:28

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="KPI",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("kpi_name", models.CharField(max_length=255)),
                ("kpi_description", models.TextField(blank=True, null=True)),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("failed", "Failed"),
                            ("completed", "Completed"),
                            ("pending", "Pending"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("planed_kpi", models.IntegerField(default=1)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "KPI",
                "verbose_name_plural": "KPIs",
            },
        ),
        migrations.CreateModel(
            name="KSI",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("ksi_name", models.CharField(max_length=255)),
                ("ksi_description", models.TextField(blank=True, null=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_started", "Not Started"),
                            ("ongoing", "Ongoing"),
                            ("on_review", "On Review"),
                            ("completed", "Completed"),
                            ("overdue", "Overdue"),
                            ("terminated", "Terminated"),
                        ],
                        default="not_started",
                        max_length=20,
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "KSI",
                "verbose_name_plural": "KSIs",
            },
        ),
        migrations.CreateModel(
            name="MajorActivity",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("major_activity_name", models.CharField(max_length=255)),
                ("major_activity_description", models.TextField(blank=True, null=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("weight", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_started", "Not Started"),
                            ("ongoing", "Ongoing"),
                            ("on_review", "On Review"),
                            ("completed", "Completed"),
                            ("overdue", "Overdue"),
                            ("terminated", "Terminated"),
                        ],
                        default="not_started",
                        max_length=20,
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Major Activity",
                "verbose_name_plural": "Major Activities",
                "db_table": "tasks_major_activity",
            },
        ),
        migrations.CreateModel(
            name="Milestone",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("milestone_name", models.CharField(max_length=255)),
                ("milestone_description", models.TextField(blank=True, null=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("weight", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_started", "Not Started"),
                            ("ongoing", "Ongoing"),
                            ("on_review", "On Review"),
                            ("completed", "Completed"),
                            ("overdue", "Overdue"),
                            ("terminated", "Terminated"),
                        ],
                        default="not_started",
                        max_length=20,
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("task_name", models.CharField(max_length=255)),
                ("task_description", models.TextField(blank=True, null=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("actual_start_date", models.DateField(blank=True, null=True)),
                ("actual_end_date", models.DateField(blank=True, null=True)),
                ("weight", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_started", "Not Started"),
                            ("ongoing", "Ongoing"),
                            ("on_review", "On Review"),
                            ("completed", "Completed"),
                            ("overdue", "Overdue"),
                            ("terminated", "Terminated"),
                        ],
                        default="not_started",
                        max_length=20,
                    ),
                ),
                (
                    "approval_status",
                    models.CharField(
                        choices=[
                            ("denied", "Denied"),
                            ("approved", "Approved"),
                            ("pending", "Pending"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("feedback", models.TextField(blank=True, null=True)),
                ("other_challenge", models.TextField(blank=True, null=True)),
                ("link", models.URLField(blank=True, max_length=2048, null=True)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
