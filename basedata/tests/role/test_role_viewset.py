from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Role

User = get_user_model()


class RoleViewSetTestCase(APITestCase):
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

        self.user = User.objects.create_user(
            email="user@email.com",
            password="1234abcd!A",
            first_name="firstname",
            last_name="lastname",
        )
        self.user.is_active = True
        self.user.save()

        # Generate JWT tokens for the users
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)

        # Authenticate as admin user for tests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")

        # Define URLs
        self.list_create_url = reverse("role-list", kwargs={"version": "v1"})

    def test_list_roles(self):
        """
        Ensure the admin user can list all roles.
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

        self.assertEqual(response_data["count"], 2, "There should be 2 roles in total")

        results = response_data["results"]
        self.assertEqual(len(results), 2, "There should be 2 roles in the results")
        self.assertIn(
            self.admin_role.name,
            [role["name"] for role in results],
            f"Role '{self.admin_role.name}' should be listed in the results",
        )
        self.assertIn(
            self.user_role.name,
            [role["name"] for role in results],
            f"Role '{self.user_role.name}' should be listed in the results",
        )

    def test_list_roles_unauthorized(self):
        """
        Ensure unauthorized users cannot list roles.
        """
        self.client.credentials()  # Remove authentication
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthorized users should receive 401",
        )

    def test_create_role(self):
        """
        Ensure the admin user can create a new role.
        """
        data = {"name": "team_lead"}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Role should be created successfully",
        )
        self.assertEqual(
            response.json()["data"]["name"],
            "team_lead",
            "Role name should be 'team_lead'",
        )
        self.assertTrue(
            Role.objects.filter(name="team_lead").exists(),
            "Role should be saved in the database",
        )

    def test_create_role_forbidden(self):
        """
        Ensure non-superadmin users cannot create roles.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        data = {"name": "team_lead"}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular User should not be allowed to create roles",
        )

    def test_create_role_with_duplicate_name(self):
        """
        Ensure duplicate role names are not allowed.
        """
        data = {"name": self.admin_role.name}  # Use existing role name
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Duplicate role names should not be allowed",
        )
        self.assertIn(
            "name",
            response.json()["errors"],
            "Validation error for name should be present",
        )

    def test_update_role(self):
        """
        Ensure super-admin user can update a role.
        """
        url = reverse("role-detail", kwargs={"version": "v1", "pk": self.user_role.id})
        data = {"name": "senior_employee"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Role should be updated successfully",
        )
        self.assertEqual(
            response.json()["data"]["name"],
            "senior_employee",
            "Role name should be 'senior_employee'",
        )
        self.assertTrue(
            Role.objects.filter(name="senior_employee").exists(),
            "Updated role should be in the database",
        )

    def test_update_role_invalid(self):
        """
        Ensure updating a non-existent role returns 404.
        """
        url = reverse(
            "role-detail", kwargs={"version": "v1", "pk": 999}
        )  # Non-existent role ID
        data = {"name": "invalid_role"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Non-existent role ID should return 404",
        )

    def test_update_role_unauthorized(self):
        """
        Ensure non-admin users cannot update roles.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse("role-detail", kwargs={"version": "v1", "pk": self.user.id})
        data = {"name": "senior_employee"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be allowed to update roles",
        )

    def test_delete_role(self):
        """
        Ensure the super-admin user can delete a role.
        """
        data = {"name": "toBeDeleted"}
        self.client.post(self.list_create_url, data, format="json")
        tobedeleted_role = Role.objects.get(name="toBeDeleted")
        url = reverse(
            "role-detail", kwargs={"version": "v1", "pk": tobedeleted_role.id}
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Role should be deleted successfully",
        )
        self.assertFalse(
            Role.objects.filter(name="toBeDeleted").exists(),
            "Deleted role should no longer exist",
        )

    def test_delete_role_unauthorized(self):
        """
        Ensure non-admin users cannot delete roles.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        url = reverse("role-detail", kwargs={"version": "v1", "pk": self.user_role.id})
        response = self.client.delete(url, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be allowed to delete roles",
        )

    def tearDown(self):
        User.objects.all().delete()
        Role.objects.all().delete()
