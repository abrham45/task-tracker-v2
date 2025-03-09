from datetime import datetime
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from basedata.models import Department, Position

User = get_user_model()


@override_settings(ALLOWED_EMAIL_DOMAINS=["icog.et"])
class UserRegistrationTestCase(APITestCase):
    # @mock.patch("config.settings.ALLOWED_EMAIL_DOMAINS", TEST_ALLOWED_EMAIL_DOMAINS)
    # @override_settings(ALLOWED_EMAIL_DOMAINS=TEST_ALLOWED_EMAIL_DOMAINS)
    @mock.patch("config.settings.ALLOWED_EMAIL_DOMAINS", ["icog.et"])
    def setUp(self):
        settings.TEST_ALLOWED_EMAIL_DOMAINS = ["icog.et"]
        # Create a test user
        Group.objects.create(name="Not-Assigned")
        self.user = User.objects.create_user(
            email="test.user@icog.et",
            password="testpassword123",
            first_name="Test",
            last_name="User",
        )
        self.user.is_active = True
        self.user.save()

        # Create a test superuser
        Group.objects.create(name="Super-Admin")
        self.superuser = User.objects.create_superuser(
            email="super.user@icog.et",
            password="testpassword123",
            first_name="Super",
            last_name="User",
        )
        self.superuser.is_active = True
        self.superuser.save()

        # Login
        self.admin_token = str(RefreshToken.for_user(self.superuser).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        # Define URLs
        self.register_url = reverse("user-signup", kwargs={"version": "v1"})
        self.login_url = reverse("jwt-create", kwargs={"version": "v1"})
        self.user_detail_url = reverse(
            "user-detail", kwargs={"version": "v1", "id": str(self.user.id)}
        )
        self.refresh_url = reverse("jwt-refresh", kwargs={"version": "v1"})
        self.protected_url = reverse("user-list", kwargs={"version": "v1"})

        # Initialize APIClient
        self.client = APIClient()

    def test_superuser_creation(self):
        """
        Ensure a superuser can be created and has the correct attributes.
        """
        superuser = User.objects.create_superuser(
            email="new.superuser@icog.et",
            password="password",
            first_name="Super",
            last_name="User",
        )
        self.assertEqual(superuser.email, "new.superuser@icog.et")
        self.assertTrue(superuser.is_staff, "Superuser should have is_staff=True")
        self.assertTrue(
            superuser.is_superuser, "Superuser should have is_superuser=True"
        )
        self.assertTrue(superuser.is_active, "Superuser should have is_active=True")

    def test_user_registration(self):
        """
        Ensure a new user can register.
        """
        self.client.credentials()

        data = {
            "email": "new.user@icog.et",
            "password": "newpassword123",
        }

        response = self.client.post(self.register_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new.user@icog.et").exists())

        user = User.objects.get(email="new.user@icog.et")

        # Check if first_name and last_name are extracted correctly
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "User")

    def test_user_registration_with_invalid_data(self):
        """
        Ensure a user cannot register with invalid data.
        """
        # email with not allowed domain
        invalid_data = {
            "email": "test.userone@other.com",
            "password": "1234abcd!A",
        }
        response = self.client.post(self.register_url, invalid_data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Invalid email should be rejected",
        )
        self.assertIn(
            "email",
            response.json()["errors"],
            "Error response should contain 'email' key.",
        )

        # Invalid email
        invalid_data = {
            "email": "invalidemail@icog.et",
            "password": "1234abcd!A",
        }
        response = self.client.post(self.register_url, invalid_data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Invalid email should be rejected",
        )
        self.assertIn(
            "email",
            response.json()["errors"],
            "Error response should contain 'email' key.",
        )

        # Invalid password
        invalid_data = {
            "email": "test.usertwo@icog.et",
            "password": "password1234",
        }
        response = self.client.post(self.register_url, invalid_data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Invalid password should be rejected",
        )
        self.assertIn(
            "password",
            response.json()["errors"],
            "Error response should contain 'password' key.",
        )

    def test_created_by_updated_by_created_date_updated_date(self):
        """
        Ensure created_by, updated_by, created_date, and updated_date are
        correctly set during user creation.
        """
        data = {
            "email": "new.user@icog.et",
            "password": "newpassword123",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_user = User.objects.get(email="new.user@icog.et")

        # Check created_by and updated_by
        self.assertIsNone(
            new_user.created_by,
            "created_by should be None for unauthenticated creation",
        )
        self.assertIsNone(
            new_user.updated_by,
            "updated_by should be None for unauthenticated creation",
        )

        # Check created_date and updated_date
        self.assertIsNotNone(new_user.created_date, "created_date should be set")
        self.assertIsNotNone(new_user.updated_date, "updated_date should be set")

        # Ensure timestamps are within a reasonable range
        now = datetime.now()
        self.assertAlmostEqual(
            new_user.created_date.timestamp(),
            now.timestamp(),
            delta=10,
            msg="created_date should be recent",
        )
        self.assertAlmostEqual(
            new_user.updated_date.timestamp(),
            now.timestamp(),
            delta=10,
            msg="updated_date should be recent",
        )

    def test_created_by_updated_by_created_date_updated_date_authenticated(self):
        """
        Ensure created_by, updated_by, created_date, and updated_date are
        correctly set during user creation for authenticated user.
        """
        data = {
            "email": "new.user@icog.et",
            "password": "newpassword123",
        }

        # Authenticate the request
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_user = User.objects.get(email="new.user@icog.et")

        # Check created_by and updated_by
        self.assertEqual(
            new_user.created_by,
            self.user,
            "created_by should be the authenticated user",
        )
        self.assertEqual(
            new_user.updated_by,
            self.user,
            "updated_by should be the authenticated user",
        )

        # Check timestamps
        now = datetime.now()
        self.assertAlmostEqual(
            new_user.created_date.timestamp(),
            now.timestamp(),
            delta=10,
            msg="created_date should be recent",
        )
        self.assertAlmostEqual(
            new_user.updated_date.timestamp(),
            now.timestamp(),
            delta=10,
            msg="updated_date should be recent",
        )

    def test_updated_by_updated_date_on_update(self):
        """
        Ensure updated_by and updated_date are correctly set during user update.
        """
        # Authenticate the request
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")

        # Update the user
        update_data = {
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
        }
        response = self.client.patch(self.user_detail_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Fetch the updated user
        updated_user = User.objects.get(id=self.user.id)

        # Check updated_by and updated_date
        self.assertEqual(
            updated_user.updated_by,
            self.superuser,
            "updated_by should correctly reset user",
        )
        self.assertIsNotNone(updated_user.updated_date, "updated_date should be set")

        # Ensure updated_date is recent
        now = datetime.now()
        self.assertAlmostEqual(
            updated_user.updated_date.timestamp(),
            now.timestamp(),
            delta=10,
            msg="updated_date should be recent",
        )

    def test_user_registration_is_active_false(self):
        """
        Ensure a newly registered user has is_active=False by default.
        """
        data = {
            "email": "new.user@icog.et",
            "password": "newpassword123",
        }
        response = self.client.post(self.register_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_user = User.objects.get(email="new.user@icog.et")
        self.assertFalse(new_user.is_active, "Newly registered user should be inactive")

    def test_user_deletion_not_allowed(self):
        """
        Ensure that user deletion is not allowed,
        neither for the user themselves nor by a superuser.
        """
        # DELETE /users/me/
        # Authenticate the request
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        # Provide the 'version' argument when reversing the URL
        url = reverse("user-me", kwargs={"version": "v1"})
        response = self.client.delete(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            "User deletion should not be allowed for /users/me/.",
        )
        self.assertIn(
            "detail", response.json()["errors"], "Expected error message for deletion."
        )

        # DELETE /users/{id}
        # Authenticate the request
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")

        delete_url = reverse(
            "user-detail", kwargs={"version": "v1", "id": str(self.user.id)}
        )
        response = self.client.delete(delete_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
            "User deletion should not be allowed for /users/{id}/.",
        )
        self.assertIn(
            "detail", response.json()["errors"], "Expected error message for deletion."
        )

    def test_user_deactivation_not_allowed_for_non_superuser(self):
        """
        Ensure user activation/deactivation not allowed for non-superuser.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

        put_data = {
            "is_not_deactivated": not self.user.is_not_deactivated,
        }
        update_url = reverse(
            "user-detail", kwargs={"version": "v1", "id": str(self.user.id)}
        )

        # Test PATCH request
        response = self.client.patch(update_url, put_data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "User activation/deactivation should not be allowed for non-superusers.",
        )
        self.assertIn(
            "detail", response.json()["errors"], "Expected error message for deletion."
        )

        # Prepare PUT request
        update_data = {
            "first_name": f"{self.user.first_name}",
            "last_name": f"{self.user.last_name}",
            "email": f"{self.user.email}",
            "bio": f"{self.user.bio}",
            "phone_number": f"{self.user.phone_number}"
            if self.user.phone_number
            else "",
            "is_not_deactivated": f"{self.user.is_not_deactivated}",
        }

        # Test PATCH request
        response = self.client.patch(update_url, update_data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "User activation/deactivation should not be allowed for non-superusers.",
        )
        self.assertIn(
            "detail", response.json()["errors"], "Expected error message for deletion."
        )

    def test_user_deactivation_allowed_for_superuser(self):
        """
        Ensure user activation/deactivation allowed for superuser.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")

        update_url = reverse(
            "user-detail", kwargs={"version": "v1", "id": str(self.user.id)}
        )

        # Test PATCH request
        put_data = {
            "is_not_deactivated": not self.user.is_not_deactivated,
        }
        response = self.client.patch(update_url, put_data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "User activation/deactivation should be allowed for superusers.",
        )

        # Test PUT request
        update_data = {
            "first_name": f"{self.user.first_name}",
            "last_name": f"{self.user.last_name}",
            "email": f"{self.user.email}",
            "bio": f"{self.user.bio}",
            "phone_number": f"{self.user.phone_number}"
            if self.user.phone_number
            else "",
            "is_not_deactivated": f"{self.user.is_not_deactivated}",
        }
        response = self.client.patch(update_url, update_data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "User activation/deactivation should be allowed for superusers.",
        )

    def tearDown(self):
        Position.objects.all().delete()
        Department.objects.all().delete()
        User.objects.all().delete()
