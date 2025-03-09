from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from basedata.models import Department, Position
from users.models import Role

User = get_user_model()


class AssignPositionActionTestCase(APITestCase):
    def setUp(self):
        # Create roles
        Role.objects.create(name="Super-Admin")
        Role.objects.create(name="Not-Assigned")
        hr_role = Role.objects.create(name="HR")

        hr_permissions = [
            "view_position",
            "view_user",
            "change_user",
        ]
        for perm in hr_permissions:
            hr_role.permissions.add(
                *Permission.objects.filter(
                    codename=perm,
                )
            )

        # Create users
        self.admin_user = User.objects.create_superuser(
            email="admin@email.com",
            password="1234abcd!A",
            first_name="firstname",
            last_name="lastname",
        )
        self.admin_user.save()

        self.user = User.objects.create_user(
            email="user@email.com",
            password="1234abcd!A",
            first_name="firstname",
            last_name="lastname",
        )

        self.hr_user = User.objects.create_user(
            email="hr.user@email.com",
            password="1234abcd!A",
            first_name="HR",
            last_name="User",
        )
        self.hr_user.is_active = True
        self.hr_user.groups.add(hr_role)
        self.hr_user.save()

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

        # Create positions
        self.position1 = Position.objects.create(
            department=self.department1,
            position_name="Lead",
            position_description="Handles technical tasks.",
            created_by=self.hr_user,
            updated_by=self.hr_user,
        )

        self.position2 = Position.objects.create(
            department=self.department1,
            position_name="SWE1",
            position_description="Handles technical tasks.",
            created_by=self.hr_user,
            updated_by=self.hr_user,
        )

        # Generate JWT tokens for the users
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.hr_user_token = str(RefreshToken.for_user(self.hr_user).access_token)

        # Authenticate as HR user for tests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.hr_user_token}")

        # Define URLs
        self.list_create_url = reverse("user-list", kwargs={"version": "v1"})
        self.assign_position_url = reverse(
            "user-assign-position", kwargs={"version": "v1", "id": str(self.user.id)}
        )

    def test_list_users(self):
        """
        Ensure the hr user can list all users.
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

        self.assertEqual(response_data["count"], 3, "There should be 3 users in total")

    def test_assign_position_to_user(self):
        """
        Ensure the HR user can assign a position to a user.
        """
        data = {"position": self.position1.id}
        response = self.client.patch(self.assign_position_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Position should be assigned successfully",
        )
        self.user.refresh_from_db()
        self.assertEqual(
            User.objects.filter(id=self.user.id)[0].position,
            self.position1,
            "User's position should be updated.",
        )

    def test_assign_position_to_nonexistent_user(self):
        """
        Ensure assigning a position to a non-existent user returns 404.
        """
        # Use a non-existent user ID in the URL
        invalid_assign_role_url = reverse(
            "user-assign-position", kwargs={"version": "v1", "id": 999}
        )
        data = {"position": self.position1.id}
        response = self.client.patch(invalid_assign_role_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Non-existent user ID should return 404",
        )

    def test_assign_nonexistent_position_to_user(self):
        """
        Ensure assigning a non-existent position to a user returns 400
        with the correct error message.
        """
        data = {"position": 999}  # Non-existent position ID
        response = self.client.patch(self.assign_position_url, data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Assigning a non-existent position should return 400 Bad Request",
        )

        self.assertIn(
            "position",
            response.data,
            "Response should include 'position' in the error message",
        )
        self.assertEqual(
            response.data["position"][0],
            'Invalid pk "999" - object does not exist.',
            "Error message should specify that the position ID is invalid",
        )

    def test_assign_position_unauthorized(self):
        """
        Ensure non-HR users cannot assign roles.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        data = {"position": self.position1.id}
        response = self.client.patch(self.assign_position_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be allowed to assign positions.",
        )

    def tearDown(self):
        Position.objects.all().delete()
        Department.objects.all().delete()
        User.objects.all().delete()
        Role.objects.all().delete()
