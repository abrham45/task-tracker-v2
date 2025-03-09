from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from basedata.models import Department
from users.models import Role

User = get_user_model()


class DepartmentViewSetTestCase(APITestCase):
    def setUp(self):
        # Create users
        Role.objects.create(name="Super-Admin")
        self.admin_user = User.objects.create_superuser(
            email="admin@email.com",
            password="1234abcd!A",
            first_name="Admin",
            last_name="User",
        )

        Role.objects.create(name="Not-Assigned")
        self.user = User.objects.create_user(
            email="user@email.com",
            password="1234abcd!A",
            first_name="Regular",
            last_name="User",
        )
        self.user.is_active = True
        self.user.save()

        # Create a department
        self.department1 = Department.objects.create(
            department_name="Engineering",
            department_description="Handles technical tasks.",
            created_by=self.admin_user,
            updated_by=self.admin_user,
        )
        self.department2 = Department.objects.create(
            department_name="HR",
            department_description="Handles human resources.",
            created_by=self.admin_user,
            updated_by=self.admin_user,
        )

        # Generate JWT tokens for the users
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)

        # Authenticate as admin user for tests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")

        # Define URLs
        self.list_create_url = reverse("department-list", kwargs={"version": "v1"})

    def test_list_departments(self):
        """
        Ensure the admin user can list all departments.
        """
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, "Status code should be 200 OK"
        )

        response_data = response.json()["data"]
        self.assertIn(
            "count", response_data, "Paginated response should include 'count'"
        )
        self.assertIn(
            "results", response_data, "Paginated response should include 'results'"
        )

        self.assertEqual(
            response_data["count"], 2, "There should be 2 departments in total"
        )

        results = response_data["results"]
        self.assertEqual(
            len(results), 2, "There should be 2 departments in the results"
        )
        self.assertIn(
            self.department1.department_name,
            [department["name"] for department in results],
            f"'{self.department1.department_name}' should be listed in the results",
        )
        self.assertIn(
            self.department2.department_name,
            [department["name"] for department in results],
            f"'{self.department2.department_name}' should be listed in the results",
        )

    def test_list_departments_unauthorized(self):
        """
        Ensure unauthorized users cannot list departments.
        """
        self.client.credentials()
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthorized users should receive 401",
        )

    def test_create_department(self):
        """
        Ensure the admin user can create a new department.
        """
        data = {"name": "Finance", "description": "Handles financial matters."}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Department should be created successfully",
        )
        self.assertEqual(
            response.json()["data"]["name"],
            "Finance",
            "Department name should be 'Finance'",
        )
        self.assertTrue(
            Department.objects.filter(department_name="Finance").exists(),
            "Department should be saved in the database",
        )

    def test_create_department_forbidden(self):
        """
        Ensure non-superadmin users cannot create departments.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        data = {"name": "Marketing", "description": "Handles marketing tasks."}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular User should not be allowed to create departments",
        )

    def test_update_department(self):
        """
        Ensure the admin user can update a department.
        """
        url = reverse(
            "department-detail",
            kwargs={"version": "v1", "pk": self.department1.id},
        )
        data = {"name": "Tech", "description": "Handles tech matters."}
        response = self.client.put(url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Department should be updated successfully",
        )
        self.assertEqual(
            response.json()["data"]["name"],
            "Tech",
            "Department name should be updated to 'Tech'",
        )
        self.assertTrue(
            Department.objects.filter(department_name="Tech").exists(),
            "Updated department should be in the database",
        )

    def test_update_department_unauthorized(self):
        """
        Ensure non-superadmin users cannot update departments.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse(
            "department-detail",
            kwargs={"version": "v1", "pk": self.department1.id},
        )
        data = {"name": "NewName", "description": "New description."}
        response = self.client.put(url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be allowed to update departments",
        )

    def test_delete_department(self):
        """
        Ensure the admin user can delete a department.
        """
        url = reverse(
            "department-detail",
            kwargs={"version": "v1", "pk": self.department2.id},
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Department should be deleted successfully",
        )
        self.assertFalse(
            Department.objects.filter(id=self.department2.id).exists(),
            "Deleted department should no longer exist",
        )

    def test_delete_department_unauthorized(self):
        """
        Ensure non-admin users cannot delete departments.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse(
            "department-detail",
            kwargs={"version": "v1", "pk": self.department1.id},
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be allowed to delete departments",
        )

    def tearDown(self):
        Department.objects.all().delete()
        User.objects.all().delete()
