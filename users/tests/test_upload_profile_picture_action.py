import io
import tempfile
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Role

User = get_user_model()


# Create a secure temporary directory for media files
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
)
class UserProfilePictureTests(APITestCase):
    """
    Test profile picture upload, mocks storage to avoid real uploads.
    """

    @mock.patch.object(default_storage, "save")
    def setUp(self, mock_save):
        Role.objects.create(name="Not-Assigned")
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )

        Role.objects.create(name="Super-Admin")
        self.other_user = User.objects.create_superuser(
            email="otheruser@example.com",
            password="password123",
            first_name="Other",
            last_name="User",
        )

        # Create a valid image file
        image_file = io.BytesIO()
        image = Image.new("RGB", (100, 100), color="red")
        image.save(image_file, format="JPEG")
        image_file.seek(0)
        self.valid_image = SimpleUploadedFile(
            "test_image.jpg", image_file.read(), content_type="image/jpeg"
        )

        self.admin_token = str(RefreshToken.for_user(self.user).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")

    def test_authenticated_user_can_upload_profile_picture(self):
        """
        Test that an authenticated user can upload a profile picture.
        """
        url = reverse("user-me-upload-profile-picture", kwargs={"version": "v1"})
        response = self.client.post(url, {"profile_picture": self.valid_image})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("profile_picture", response.data)

    def test_upload_profile_picture_invalid_format(self):
        """
        Test that uploading a profile picture with an invalid format is rejected.
        """
        url = reverse("user-me-upload-profile-picture", kwargs={"version": "v1"})
        invalid_file = SimpleUploadedFile(
            "test_file.txt", content=b"not_an_image", content_type="text/plain"
        )
        response = self.client.post(url, {"profile_picture": invalid_file})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profile_picture", response.data)

    def test_unauthenticated_user_cannot_upload(self):
        """
        Test that unauthenticated users cannot upload a profile picture.
        """
        self.client.credentials()
        url = reverse("user-me-upload-profile-picture", kwargs={"version": "v1"})
        response = self.client.post(url, {"profile_picture": self.valid_image})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_owner_cannot_upload_to_another_user_profile(self):
        """
        Test that a user cannot upload a profile picture for another user's account.
        """
        url = reverse(
            "user-upload-profile-picture",
            kwargs={"version": "v1", "id": self.other_user.id},
        )
        response = self.client.post(url, {"profile_picture": self.valid_image})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
