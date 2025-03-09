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


class TaskViewSetTestCase(APITestCase):
    def setUp(self):
        # Create roles
        Role.objects.create(name="Super-Admin")
        Role.objects.create(name="Not-Assigned")
        leads_role = Role.objects.create(name="Leads")
        experts_role = Role.objects.create(name="Experts")

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

        # Create permissions for experts
        expert_permissions = [
            "view_task",
            "change_task",
        ]
        for perm in expert_permissions:
            experts_role.permissions.add(
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
        self.expert_user.groups.add(experts_role)
        self.expert_user.save()

        self.expert_user2 = User.objects.create_user(
            email="expert2@email.com",
            password="1234abcd!A",
            first_name="Expert2",
            last_name="User",
        )
        self.expert_user2.is_active = True
        self.expert_user2.groups.add(experts_role)
        self.expert_user2.save()

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
            department_description="Handles finaincial tasks.",
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

        self.expert_user2.position = self.position4
        self.expert_user2.save()

        self.ksi = KSI.objects.create(
            ksi_name="Strategic Initiative 1",
            start_date="2024-01-01",
            end_date="2024-12-31",
            department=self.department,
            status="not_started",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )

        self.ksi2 = KSI.objects.create(
            ksi_name="Strategic Initiative 2",
            start_date="2024-01-01",
            end_date="2024-12-31",
            department=self.department2,
            status="not_started",
            created_by=self.lead_user2,
            updated_by=self.lead_user2,
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

        self.milestone2 = Milestone.objects.create(
            milestone_name="Milestone 2",
            start_date="2024-01-01",
            end_date="2024-12-31",
            ksi=self.ksi2,
            weight=50,
            status="in_progress",
            created_by=self.lead_user2,
            updated_by=self.lead_user2,
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

        self.kpi2 = KPI.objects.create(
            kpi_name="Milestone 2",
            start_date="2024-01-01",
            end_date="2024-12-31",
            milestone=self.milestone2,
            status="in_progress",
            created_by=self.lead_user2,
            updated_by=self.lead_user2,
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

        self.major_activity2 = MajorActivity.objects.create(
            major_activity_name="Major Activity 2",
            start_date="2024-01-01",
            end_date="2024-12-31",
            kpi=self.kpi2,
            department=self.department2,
            weight=70,
            status="in_progress",
            created_by=self.lead_user2,
            updated_by=self.lead_user2,
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
        self.task.positions.add(self.position3)

        self.task2 = Task.objects.create(
            task_name="test task 2",
            start_date="2024-01-01",
            end_date="2024-12-31",
            major_activity=self.major_activity2,
            weight=70,
            status="in_progress",
            created_by=self.lead_user2,
            updated_by=self.lead_user2,
        )
        self.task2.positions.add(self.position4)

        # Generate JWT tokens
        self.lead_token = str(RefreshToken.for_user(self.lead_user).access_token)
        self.lead2_token = str(RefreshToken.for_user(self.lead_user2).access_token)
        self.expert_token = str(RefreshToken.for_user(self.expert_user).access_token)
        self.expert2_token = str(RefreshToken.for_user(self.expert_user2).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)

        # Authenticate as lead user for tests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.expert_token}")

        # Define URLs
        self.list_create_url = reverse("task-list", kwargs={"version": "v1"})
        self.detail_url = lambda pk: reverse(
            "task-detail", kwargs={"version": "v1", "pk": pk}
        )

    def test_list_task(self):
        """
        Ensure the expert user can list all Tasks assigned to it.
        """
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, "Status code should be 200 OK"
        )

        response_data = response.json()["data"]
        self.assertIn(
            "count", response_data, "Paginated response should include 'count'."
        )
        self.assertIn(
            "results", response_data, "Paginated response should include 'results'."
        )
        self.assertEqual(response_data["count"], 1, "There should be 1 Task.")
        self.assertIn(
            self.task.task_name,
            [task["name"] for task in response_data["results"]],
            f"'{self.task.task_name}' should be in the results",
        )
        self.assertNotIn(
            self.task2.task_name,
            [task["name"] for task in response_data["results"]],
            f"'{self.task2.task_name}' should not be in the results.",
        )

    def test_create_task(self):
        """
        Ensure expert user can't create a new Task.
        """
        payload = {
            "name": "New Test Task",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "major_activity": self.major_activity.id,
            "weight": 75,
            "status": "not_started",
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Lead user should not be able to create a Task.",
        )
        self.assertFalse(
            Task.objects.filter(
                task_name="New Test Task",
            ).exists(),
            "Task should not be created.",
        )

    def test_update_task(self):
        """
        Ensure the expert user can update an existing Task.
        """
        payload = {"name": "Updated Task Name"}
        response = self.client.patch(
            self.detail_url(self.task.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Lead user should be able to update a Task.",
        )
        self.task.refresh_from_db()
        self.assertEqual(
            self.task.task_name,
            payload["name"],
            "Task name should be updated.",
        )

    def test_update_status_task(self):
        """
        Ensure the expert user can update an existing Task status only upto 'on_review'.
        """
        payload = {"status": "on_review"}
        response = self.client.patch(
            self.detail_url(self.task.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Expert user should be able to update a Task's status to 'on_review'.",
        )

        payload = {"status": "completed"}
        response = self.client.patch(
            self.detail_url(self.task.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Expert user should be able to update a Task's status to 'completed'.",
        )

    def test_expert_user_update_not_assigned_task(self):
        """
        Ensure expert user cant update tasks that are not assigned to it.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.expert2_token}")
        payload = {"name": "Updated Task Name"}
        response = self.client.patch(
            self.detail_url(self.task.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Experts should not be able to update a Task that is not assigned to them.",
        )

    def test_delete_task(self):
        """
        Ensure expert user can delete an existing Task.
        """
        response = self.client.delete(self.detail_url(self.task.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Expert user should not be able to delete a Task.",
        )
        self.assertTrue(
            Task.objects.filter(id=self.task.id).exists(),
            "Task should still exist in the database.",
        )
