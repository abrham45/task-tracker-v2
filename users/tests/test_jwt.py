import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class JWTTestCase(APITestCase):
    def setUp(self):
        # Suppress Axes logs during testing
        logging.getLogger("axes").setLevel(logging.CRITICAL)
        logging.getLogger("axes.handlers").setLevel(logging.CRITICAL)
        logging.getLogger("axes.models").setLevel(logging.CRITICAL)

        # Create a test user
        Group.objects.create(name="Not-Assigned")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User",
        )
        self.user.is_active = True
        self.user.save()

        # Create a test superuser
        Group.objects.create(name="Super-Admin")
        self.superuser = User.objects.create_superuser(
            email="superuser@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="superuser",
        )
        self.superuser.is_active = True
        self.superuser.save()

        # Define URLs
        self.register_url = reverse("user-signup", kwargs={"version": "v1"})
        self.login_url = reverse("jwt-create", kwargs={"version": "v1"})
        self.user_detail_url = reverse(
            "user-detail", kwargs={"version": "v1", "id": str(self.user.id)}
        )
        self.refresh_url = reverse("jwt-refresh", kwargs={"version": "v1"})
        self.validate_url = reverse("jwt-verify", kwargs={"version": "v1"})
        self.protected_url = reverse("user-list", kwargs={"version": "v1"})

        # Initialize APIClient
        self.client = APIClient()

    def _get_access_token(self, user):
        """Helper method to generate an access token for the test user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_user_cannot_login_before_activation(self):
        """
        Ensure a user cannot log in before their account is activated.
        """
        # Register a new user
        data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
        }
        self.client.post(self.register_url, data, format="json")

        # Attempt to log in
        login_data = {
            "email": "newuser@example.com",
            "password": "newpassword123",
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(
            login_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Inactive user should not be able to log in",
        )

    def test_manually_deactivated_user_cannot_login(self):
        """
        Ensure a user cannot log in if account is manually deactivated.
        """
        self.user = User.objects.create_user(
            email="deactivateduser@example.com",
            password="testpassword123",
        )
        self.user.is_active = True
        self.user.is_not_deactivated = False
        self.user.save()

        # Attempt to log in
        login_data = {
            "email": "deactivateduser@example.com",
            "password": "testpassword123",
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(
            login_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Deactivated user should not be able to log in",
        )
        self.assertIn(
            login_response.json()["errors"]["detail"],
            "Your account has been deactivated, please contact support.",
            "Response should contain message about account state.",
        )

    def test_manually_deactivated_user_cannot_authenticate(self):
        """
        Ensure a user cannot authenticate with token if account is manually deactivated.
        """
        access_token = self._get_access_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # manually deactivate user
        self.user.is_not_deactivated = False
        self.user.save()

        response = self.client.get(self.protected_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Deactivated user should not be able to authenticate using token.",
        )
        self.assertIn(
            response.json()["errors"]["detail"],
            "Your account has been deactivated, please contact support.",
            "Response should contain message about account state.",
        )

    def test_user_login(self):
        """
        Ensure a user can log in and receive JWT tokens.
        """
        data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
        }
        response = self.client.post(self.login_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data, "Access token should be in the response")
        self.assertIn(
            "refresh", response.data, "Refresh token should be in the response"
        )

    def test_invalid_login_credentials(self):
        """
        Ensure a user cannot log in with invalid credentials.
        """
        invalid_data = {
            "email": "testuser@example.com",
            "password": "wrongpassword",
        }
        response = self.client.post(self.login_url, invalid_data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Invalid credentials should be rejected",
        )

    def test_token_refresh(self):
        """
        Ensure a user can refresh their access token.
        """
        # Log in to get a refresh token
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        refresh_token = login_response.data["refresh"]

        # Refresh the access token
        refresh_data = {"refresh": refresh_token}
        refresh_response = self.client.post(
            self.refresh_url, refresh_data, format="json"
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn(
            "access",
            refresh_response.data,
            "New access token should be in the response",
        )

    def test_invalid_token_refresh(self):
        """
        Ensure an invalid refresh token cannot be used to refresh the access token.
        """
        refresh_data = {"refresh": "invalid.refresh.token"}
        refresh_response = self.client.post(
            self.refresh_url, refresh_data, format="json"
        )
        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Invalid refresh token should be rejected",
        )

    def test_token_verify(self):
        """
        Ensure a user can verify their access token.
        """
        # Log in to get a refresh token
        login_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        access_token = login_response.data["access"]

        # Verify the access token
        verify_data = {"token": access_token}
        verify_response = self.client.post(
            self.validate_url, verify_data, format="json"
        )
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

    def test_invalid_token_verify(self):
        """
        Ensure an invalid access token cannot be used to verify the access token.
        """
        verify_data = {"token": "invalid.access.token"}
        verify_response = self.client.post(
            self.validate_url, verify_data, format="json"
        )
        self.assertEqual(
            verify_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Invalid access token should be rejected",
        )
        self.assertIn(
            "code",
            verify_response.json()["errors"],
            "Token not valid message should be returned",
        )

    def test_protected_endpoint_without_token(self):
        """
        Ensure a protected endpoint cannot be accessed without a token.
        """
        response = self.client.get(self.protected_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Protected endpoint should require authentication",
        )

    def test_protected_endpoint_with_token(self):
        """
        Ensure a protected endpoint can be accessed with a valid token.
        """
        access_token = self._get_access_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.protected_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Authenticated user should access the endpoint",
        )

    def test_protected_endpoint_with_invalid_token(self):
        """
        Ensure a protected endpoint cannot be accessed with an invalid token.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token")
        response = self.client.get(self.protected_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Invalid token should not access the endpoint",
        )

    def test_superuser_access_to_protected_endpoint(self):
        """
        Ensure a superuser can access protected endpoints.
        """
        access_token = self._get_access_token(self.superuser)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get(self.protected_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Superuser should be able to access protected endpoints",
        )

    def test_lockout_after_multiple_failed_attempts(self):
        """
        Ensure a user is locked out after exceeding the maximum allowed login attempts.
        """
        invalid_data = {
            "email": "testuser@example.com",
            "password": "wrongpassword",
        }

        for _ in range(5):
            self.client.post(self.login_url, invalid_data, format="json")

        # Attempt login with correct credentials
        valid_data = {
            "email": "testuser@example.com",
            "password": "testpassword123",
        }
        response = self.client.post(self.login_url, valid_data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
            "User should be locked out after multiple failed attempts",
        )
