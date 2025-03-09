from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from basedata.models import Department, Position
from tasks.models import KPI, KSI, MajorActivity, Milestone, Task
from users.models import Role

User = get_user_model()


class TestTaskAssignmentAction(APITestCase):
    def setUp(self):
        # Create roles
        Role.objects.create(name="Super-Admin")
        Role.objects.create(name="Not-Assigned")
        leads_role = Role.objects.create(name="Leads")
        expert_role = Role.objects.create(name="Experts")

        lead_permissions = [
            "view_department",
            "view_milestone",
            "view_kpi",
            "add_majoractivity",
            "change_majoractivity",
            "delete_majoractivity",
            "view_majoractivity",
            "add_task",
            "change_task",
            "delete_task",
            "view_task",
        ]
        for perm in lead_permissions:
            leads_role.permissions.add(
                *Permission.objects.filter(
                    codename=perm,
                )
            )

        expert_permissions = [
            "change_task",
            "view_task",
        ]
        for perm in expert_permissions:
            expert_role.permissions.add(
                *Permission.objects.filter(
                    codename=perm,
                )
            )

        # Create users
        self.admin_user = User.objects.create_superuser(
            email="admin@email.com",
            password="1234abcd!A",
            first_name="Admin",
            last_name="User",
        )
        self.lead_user = User.objects.create_user(
            email="lead@email.com",
            password="1234abcd!A",
            first_name="Lead",
            last_name="User",
        )
        self.lead_user.is_active = True
        self.lead_user.groups.add(leads_role)
        self.lead_user.save()

        self.lead_user2 = User.objects.create_user(
            email="lead2@email.com",
            password="1234abcd!A",
            first_name="Lead2",
            last_name="User",
        )
        self.lead_user2.is_active = True
        self.lead_user2.groups.add(leads_role)
        self.lead_user2.save()

        self.expert_user = User.objects.create_user(
            email="expert@email.com",
            password="1234abcd!A",
            first_name="Expert",
            last_name="User",
        )
        self.expert_user.is_active = True
        self.expert_user.groups.add(expert_role)
        self.expert_user.save()

        self.user = User.objects.create_user(
            email="user@email.com",
            password="1234abcd!A",
            first_name="Regular",
            last_name="User",
        )
        self.user.is_active = True
        self.user.save()

        # Create department and KSI
        self.department = Department.objects.create(
            department_name="Engineering",
            department_description="Handles technical tasks.",
            created_by=self.admin_user,
            updated_by=self.admin_user,
        )

        self.department2 = Department.objects.create(
            department_name="Finance",
            department_description="Handles financial tasks.",
            created_by=self.admin_user,
            updated_by=self.admin_user,
        )

        # Create positions
        self.position = Position.objects.create(
            department=self.department,
            position_name="Engineering",
            position_description="Handles technical tasks.",
            created_by=self.admin_user,
            updated_by=self.admin_user,
        )
        self.position2 = Position.objects.create(
            department=self.department2,
            position_name="HR",
            position_description="Handles human resources.",
            created_by=self.admin_user,
            updated_by=self.admin_user,
        )
        self.position3 = Position.objects.create(
            department=self.department,
            position_name="SWE 1",
            position_description="Handles technical tasks.",
            created_by=self.admin_user,
            updated_by=self.admin_user,
        )
        self.position4 = Position.objects.create(
            department=self.department2,
            position_name="Recruiter 1",
            position_description="Handles human resources.",
            created_by=self.admin_user,
            updated_by=self.admin_user,
        )

        self.lead_user.position = self.position
        self.lead_user.save()

        self.lead_user2.position = self.position2
        self.lead_user2.save()

        self.expert_user.position = self.position3
        self.expert_user.save()

        self.ksi = KSI.objects.create(
            ksi_name="Strategic Initiative 1",
            start_date="2024-01-01",
            end_date="2024-12-31",
            department=self.department,
            status="not_started",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )

        # Create milestone instance
        self.milestone = Milestone.objects.create(
            milestone_name="Milestone 1",
            start_date="2024-01-01",
            end_date="2024-12-31",
            ksi=self.ksi,
            weight=50,
            status="in_progress",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )

        # Create kpi instance
        self.kpi = KPI.objects.create(
            kpi_name="Milestone 1",
            start_date="2024-01-01",
            end_date="2024-12-31",
            milestone=self.milestone,
            status="in_progress",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )

        # Create major_activity instance
        self.major_activity = MajorActivity.objects.create(
            major_activity_name="Major Activity 1",
            start_date="2024-01-01",
            end_date="2024-12-31",
            kpi=self.kpi,
            department=self.department,
            weight=70,
            status="in_progress",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )

        # Create task instance
        self.task = Task.objects.create(
            task_name="test task 1",
            start_date="2024-01-01",
            end_date="2024-12-31",
            major_activity=self.major_activity,
            weight=70,
            status="in_progress",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )

        # Generate JWT tokens
        self.lead_token = str(RefreshToken.for_user(self.lead_user).access_token)
        self.lead2_token = str(RefreshToken.for_user(self.lead_user2).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)

        # Authenticate as lead user for tests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead_token}")

        # Define URLs
        self.add_users_url = reverse(
            "task-add-positions", kwargs={"version": "v1", "pk": str(self.task.id)}
        )
        self.remove_users_url = reverse(
            "task-remove-positions", kwargs={"version": "v1", "pk": str(self.task.id)}
        )

    def test_add_positions_to_task(self):
        """
        Ensure the lead user can add positions to a Task.
        """
        payload = {"positions": [self.position.id]}
        response = self.client.patch(self.add_users_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Lead user should be able to add positions to a Task.",
        )
        self.assertIn(
            self.position,
            self.task.positions.all(),
            "Expert positions should be assigned to the Task.",
        )

    def test_remove_positions_from_task(self):
        """
        Ensure the lead user can remove users from a Task.
        """
        self.task.positions.add(self.position)
        payload = {"positions": [self.position.id]}
        response = self.client.patch(self.remove_users_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Lead user should be able to remove postions from a Task.",
        )
        self.assertNotIn(
            self.position,
            self.task.positions.all(),
            "Position should be removed from the Task.",
        )

    def test_other_department_lead_user_cannot_add_positinos(self):
        """
        Ensure a lead user from another department cannot add positinos to a Task.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead2_token}")
        payload = {"positions": [self.position.id]}
        response = self.client.patch(self.add_users_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Leads from other departments shouldn't be able to add positions.",
        )

    def test_other_department_lead_user_cannot_remove_positions(self):
        """
        Ensure a lead user from another department cannot remove positions from a Task.
        """
        self.task.positions.add(self.position)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead2_token}")
        payload = {"positions": [self.position.id]}
        response = self.client.patch(self.remove_users_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Leads from other departments shouldn't be able to remove positions.",
        )

    def test_regular_user_cannot_add_positions(self):
        """
        Ensure a regular user cannot add positions to a Task.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {"positions": [self.position.id]}
        response = self.client.patch(self.add_users_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to add positions to a Task.",
        )

    def test_regular_user_cannot_remove_positions(self):
        """
        Ensure a regular user cannot remove users from a Task.
        """
        self.task.positions.add(self.position)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {"positions": [self.position.id]}
        response = self.client.patch(self.remove_users_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to remove positions from a Task.",
        )
