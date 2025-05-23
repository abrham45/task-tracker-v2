# Generated by Django 5.1.7 on 2025-03-26 09:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("basedata", "0002_initial"),
        ("tasks", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="kpi",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="kpis_created_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="kpi",
            name="updated_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="kpis_updated_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="ksi",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ksis_created_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="ksi",
            name="department",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ksis",
                to="basedata.department",
            ),
        ),
        migrations.AddField(
            model_name="ksi",
            name="updated_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ksis_updated_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="majoractivity",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="major_activities_created_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="majoractivity",
            name="department",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="major_activities",
                to="basedata.department",
            ),
        ),
        migrations.AddField(
            model_name="majoractivity",
            name="kpi",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="major_activities",
                to="tasks.kpi",
            ),
        ),
        migrations.AddField(
            model_name="majoractivity",
            name="updated_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="major_activities_updated_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="milestone",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="milestones_created_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="milestone",
            name="ksi",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="milestones",
                to="tasks.ksi",
            ),
        ),
        migrations.AddField(
            model_name="milestone",
            name="updated_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="milestones_updated_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="kpi",
            name="milestone",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="kpis",
                to="tasks.milestone",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="challenge_groups",
            field=models.ManyToManyField(
                blank=True, related_name="tasks", to="basedata.challengegroup"
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="created_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tasks_created_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="major_activity",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tasks",
                to="tasks.majoractivity",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="parent_task",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sub_tasks",
                to="tasks.task",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="positions",
            field=models.ManyToManyField(
                blank=True, related_name="tasks", to="basedata.position"
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="updated_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tasks_updated_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
