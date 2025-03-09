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

        self.lead_user.position = self.position
        self.lead_user.save()

        self.lead_user2.position = self.position2
        self.lead_user2.save()

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

        # Generate JWT tokens
        self.lead_token = str(RefreshToken.for_user(self.lead_user).access_token)
        self.lead2_token = str(RefreshToken.for_user(self.lead_user2).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)

        # Authenticate as lead user for tests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead_token}")

        # Define URLs
        self.list_create_url = reverse("task-list", kwargs={"version": "v1"})
        self.detail_url = lambda pk: reverse(
            "task-detail", kwargs={"version": "v1", "pk": pk}
        )

    def test_list_task(self):
        """
        Ensure the lead user can list all Tasks in its department.
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
        Ensure the lead user can create a new Task.
        """
        payload = {
            "name": "New Test Task",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "major_activity": self.major_activity.id,
            "weight": 15,
            "status": "not_started",
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Lead user should be able to create a Task.",
        )
        self.assertTrue(
            Task.objects.filter(
                task_name="New Test Task",
            ).exists(),
            "Task should be created.",
        )

    def test_create_task_with_weight_over_100_for_major_activity(self):
        """
        Ensure the lead user can't create a new Task with
        cumulative sum of weight over 100 for a major activity.
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
            status.HTTP_400_BAD_REQUEST,
            "Lead user should not be able to create"
            " a Task with weight over 100 for a major activity.",
        )
        self.assertIn(
            "weight",
            response.json()["errors"],
            "Response should contain error message for weight.",
        )

    def test_update_task_with_weight_over_100_for_major_activity(self):
        """
        Ensure the lead user can't update an existing Task with
        cumulative sum of weight over 100 for a major activity.
        """
        new_task = Task.objects.create(
            task_name="test task 1",
            start_date="2024-01-01",
            end_date="2024-12-31",
            major_activity=self.major_activity,
            weight=30,
            status="in_progress",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )
        payload = {"weight": 90}
        response = self.client.patch(
            self.detail_url(new_task.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Lead user shouldn't be able to update"
            " a Task with weight over 100 for a major activity.",
        )
        old_weight = new_task.weight
        new_task.refresh_from_db()
        self.assertEqual(
            new_task.weight,
            old_weight,
            "Task weight should not be updated.",
        )

    def test_update_task(self):
        """
        Ensure the lead user can update an existing Task.
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

    def test_create_subtask_with_weight_over_100_for_task(self):
        """
        Ensure the lead user can't create a new subtask with
        cumulative sum of weight over 100 for a task.
        """
        Task.objects.create(
            parent_task=self.task,
            task_name="test task 1",
            start_date="2024-01-01",
            end_date="2024-12-31",
            major_activity=self.major_activity,
            weight=30,
            status="in_progress",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )
        payload = {
            "parent_task": self.task.id,
            "name": "New Test Subtask",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "major_activity": self.major_activity.id,
            "weight": 75,
            "status": "not_started",
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Lead user should not be able to create"
            " a subtask with weight over 100 for a task.",
        )
        self.assertIn(
            "weight",
            response.json()["errors"],
            "Response should contain error message for weight.",
        )

    def test_update_subtask_with_weight_over_100_for_task(self):
        """
        Ensure the lead user can't update an existing subtask with
        cumulative sum of weight over 100 for a task.
        """
        new_task = Task.objects.create(
            parent_task=self.task,
            task_name="test sub task 1",
            start_date="2024-01-01",
            end_date="2024-12-31",
            major_activity=self.major_activity,
            weight=50,
            status="in_progress",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )
        Task.objects.create(
            parent_task=self.task,
            task_name="test sub task 2",
            start_date="2024-01-01",
            end_date="2024-12-31",
            major_activity=self.major_activity,
            weight=50,
            status="in_progress",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )
        payload = {"weight": 90}
        response = self.client.patch(
            self.detail_url(new_task.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Lead user shouldn't be able to update"
            " a subtask with weight over 100 for a task.",
        )
        old_weight = new_task.weight
        new_task.refresh_from_db()
        self.assertEqual(
            new_task.weight,
            old_weight,
            "Task weight should not be updated.",
        )

    def test_lead_user_from_other_department_update_task(self):
        """
        Ensure lead user from other department can update an existing Task.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead2_token}")
        payload = {"name": "Updated Task Name"}
        response = self.client.patch(
            self.detail_url(self.task.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Lead user should not be able to update a Task from other department.",
        )

    def test_delete_task(self):
        """
        Ensure the lead user can delete an existing Task.
        """
        response = self.client.delete(self.detail_url(self.task.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Lead user should be able to delete a Task.",
        )
        self.assertFalse(
            Task.objects.filter(id=self.task.id).exists(),
            "Task should no longer exist in the database.",
        )

    def test_lead_from_other_department_delete_task(self):
        """
        Ensure lead user from other department can't delete an existing Task.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead2_token}")
        response = self.client.delete(self.detail_url(self.task.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Lead from other department should be able to get a task and delete it.",
        )
        self.assertTrue(
            Task.objects.filter(id=self.task.id).exists(),
            "Task should still exist in the database.",
        )

    def test_unauthorized_access(self):
        """
        Ensure unauthorized users cannot access the Task endpoints.
        """
        self.client.credentials()
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthorized users should not be able to access Task.",
        )

    def test_regular_user_cannot_list_tasks(self):
        """
        Ensure a regular user cannot list the Task.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to see Tasks.",
        )

    def test_regular_user_cannot_create_tasks(self):
        """
        Ensure a regular user cannot create a new Task.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {
            "name": "New Task",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "major_activity": self.major_activity.id,
            "weight": 45,
            "status": "not_started",
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to create a new Task.",
        )

    def test_regular_user_cannot_update_task(self):
        """
        Ensure a regular user cannot update an existing Task.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {"name": "Updated Task Name"}
        response = self.client.patch(
            self.detail_url(self.task.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to update a Task.",
        )

    def test_regular_user_cannot_delete_task(self):
        """
        Ensure a regular user cannot delete an existing Task.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.delete(self.detail_url(self.task.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to delete a Task.",
        )
