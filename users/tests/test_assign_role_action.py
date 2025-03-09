from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Role

User = get_user_model()


class AssignRoleActionTestCase(APITestCase):
    def setUp(self):
        # Create roles
        self.admin_role = Role.objects.create(name="Super-Admin")
        self.user_role = Role.objects.create(name="Not-Assigned")

        # Create users
        self.admin_user = User.objects.create_superuser(
            email="admin@email.com",
            password="1234abcd!A",
            first_name="firstname",
            last_name="lastname",
        )
        self.admin_user.role = self.admin_role
        self.admin_user.save()

        self.user = User.objects.create_user(
            email="user@email.com",
            password="1234abcd!A",
            first_name="firstname",
            last_name="lastname",
        )

        # Generate JWT tokens for the users
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)

        # Authenticate as admin user for tests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")

        # Define URLs
        self.list_create_url = reverse("role-list", kwargs={"version": "v1"})
        self.assign_role_url = reverse(
            "user-assign-role", kwargs={"version": "v1", "id": str(self.user.id)}
        )

    def test_assign_role_to_user(self):
        """
        Ensure the admin user can assign a role to a user.
        """
        data = {"role": self.user_role.id}
        response = self.client.patch(self.assign_role_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Role should be assigned successfully",
        )
        self.user.refresh_from_db()
        assigned_groups = list(self.user.groups.all())
        self.assertEqual(
            len(assigned_groups), 1, "User should belong to exactly one group"
        )
        self.assertEqual(
            assigned_groups[0].id,
            self.user_role.id,
            "User's role should be updated to the correct group",
        )

    def test_assign_role_to_nonexistent_user(self):
        """
        Ensure assigning a role to a non-existent user returns 404.
        """
        # Use a non-existent user ID in the URL
        invalid_assign_role_url = reverse(
            "user-assign-role", kwargs={"version": "v1", "id": 999}
        )
        data = {"role": self.user_role.id}
        response = self.client.patch(invalid_assign_role_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Non-existent user ID should return 404",
        )

    def test_assign_nonexistent_role_to_user(self):
        """
        Ensure assigning a non-existent role to a user returns 400
        with the correct error message.
        """
        data = {"role": 999}  # Non-existent role ID
        response = self.client.patch(self.assign_role_url, data, format="json")

        # Check the HTTP response status code
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Assigning a non-existent role should return 400 Bad Request",
        )

        # Check the error message in the response
        self.assertIn(
            "role", response.data, "Response should include 'role' in the error message"
        )
        self.assertEqual(
            response.data["role"][0],
            'Invalid pk "999" - object does not exist.',
            "Error message should specify that the role ID is invalid",
        )

    def test_assign_role_unauthorized(self):
        """
        Ensure non-admin users cannot assign roles.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        data = {"role": self.user_role.id}
        response = self.client.patch(self.assign_role_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be allowed to assign roles",
        )

    def test_assign_role_invalid_data(self):
        """
        Ensure assigning a role with invalid data returns 400.
        """
        data = {
            "role": "invalid"  # Invalid role ID
        }
        response = self.client.patch(self.assign_role_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Invalid data should return 400",
        )
        self.assertIn(
            "role",
            response.json()["errors"],
            "Validation error for role should be present",
        )

    def tearDown(self):
        User.objects.all().delete()
        Role.objects.all().delete()
