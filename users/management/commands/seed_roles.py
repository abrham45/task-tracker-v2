import time

from django.contrib.auth.models import Group as Role
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seeds roles in the database"

    def handle(self, *args, **options):
        role_permissions = {
            "Not-Assigned": [],
            "Super-Admin": [],  # all permission are assigned
            "Leads": [
                # Users
                "view_user",
                # Departments
                "view_department",
                # Positions
                "view_position",
                # KSIs
                "view_ksi",
                "add_ksi",
                "change_ksi",
                "delete_ksi",
                # Milestones
                "view_milestone",
                "add_milestone",
                "change_milestone",
                "delete_milestone",
                # KPIs
                "view_kpi",
                "add_kpi",
                "change_kpi",
                "delete_kpi",
                # MajorActivities
                "view_majoractivity",
                "add_majoractivity",
                "change_majoractivity",
                "delete_majoractivity",
                # Tasks
                "view_task",
                "add_task",
                "change_task",
                "delete_task",
                # TaskFiles
                "view_taskfile",
                "add_taskfile",
                "change_taskfile",
                "delete_taskfile",
            ],
            "Experts": [
                # Users
                "view_user",
                # Departments
                "view_department",
                # Positions
                "view_position",
                # Tasks
                "view_task",
                "change_task",
                # TaskFiles
                "view_taskfile",
                "add_taskfile",
                "change_taskfile",
                "delete_taskfile",
            ],
            "Operation-Team": [
                # Users
                "view_user",
                # Departments
                "view_department",
                # Positions
                "view_position",
                # KSIs
                "view_ksi",
                # Milestones
                "view_milestone",
                # KPIs
                "view_kpi",
                # MajorActivities
                "view_majoractivity",
                # Tasks
                "view_task",
                # TaskFiles
                "view_taskfile",
            ],
            "CEO": [
                # Users
                "view_user",
                # Departments
                "view_department",
                # Positions
                "view_position",
                # KSIs
                "view_ksi",
                # Milestones
                "view_milestone",
                # KPIs
                "view_kpi",
                # MajorActivities
                "view_majoractivity",
                # Tasks
                "view_task",
                # TaskFiles
            ],
            "HR": [
                # Users
                "view_user",
                "change_user",
                # Departments
                "view_department",
                # Positions
                "view_position",
                "add_position",
                "change_position",
                "delete_position",
            ],
        }

        for role, permissions in role_permissions.items():
            # Create role
            role_obj, created = Role.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created role '{role}'"))
            else:
                self.stdout.write(self.style.WARNING(f"Role '{role}' already exists"))

            # Add permissions to role
            if role_obj.name == "Super-Admin":
                super_admin_permissions = Permission.objects.all()
                role_obj.permissions.add(*super_admin_permissions)
                self.stdout.write(
                    self.style.SUCCESS("Added All permissions to role 'Super-Admin'")
                )
                continue

            for codename in permissions:
                permission = Permission.objects.get(codename=codename)

                if permission:
                    role_obj.permissions.add(permission)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Added permission '{permission}' to role '{role}'"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Permission '{permission}' not found")
                    )

            time.sleep(1)
            self.stdout.write("-----------------------------------------------")
