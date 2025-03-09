from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from basedata.models import Department, Position
from tasks.models import KSI
from users.models import Role

User = get_user_model()


class KSIViewSetTestCase(APITestCase):
    def setUp(self):
        # Create roles
        Role.objects.create(name="Super-Admin")
        Role.objects.create(name="Not-Assigned")
        leads_role = Role.objects.create(name="Leads")

        lead_permissions = [
            "add_ksi",
            "change_ksi",
            "delete_ksi",
            "view_ksi",
            "view_user",
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
        self.user = User.objects.create_user(
            email="user@email.com",
            password="1234abcd!A",
            first_name="Regular",
            last_name="User",
        )
        self.user.is_active = True
        self.user.save()

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

        # Create departments
        self.department = Department.objects.create(
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

        # Create KSI instance
        self.ksi = KSI.objects.create(
            ksi_name="Strategic Initiative 1",
            ksi_description="Description for KSI 1",
            start_date="2024-01-01",
            end_date="2024-12-31",
            department=self.department,
            status="not_started",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )
        self.ksi2 = KSI.objects.create(
            ksi_name="Strategic Initiative 2",
            ksi_description="Description for KSI 2",
            start_date="2024-01-01",
            end_date="2024-12-31",
            department=self.department2,
            status="not_started",
            created_by=self.lead_user2,
            updated_by=self.lead_user2,
        )

        # Generate JWT tokens
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.lead_token = str(RefreshToken.for_user(self.lead_user).access_token)
        self.lead2_token = str(RefreshToken.for_user(self.lead_user2).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)

        # Authenticate as admin user for tests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead_token}")

        # Define URLs
        self.list_create_url = reverse("ksi-list", kwargs={"version": "v1"})
        self.detail_url = lambda pk: reverse(
            "ksi-detail", kwargs={"version": "v1", "pk": pk}
        )

    def test_list_ksis(self):
        """
        Ensure the lead user can list all KSIs in it's department.
        """
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, "Status code is not 200 OK"
        )

        response_data = response.json()["data"]
        self.assertIn(
            "count", response_data, "Paginated response should include 'count'"
        )
        self.assertIn(
            "results", response_data, "Paginated response should include 'results'"
        )

        self.assertEqual(response_data["count"], 1, "There should be 2 ksi in total")
        self.assertIn(
            self.ksi.ksi_name,
            [ksi["name"] for ksi in response_data["results"]],
            f"'{self.ksi.ksi_name}' should be listed in the results",
        )
        self.assertNotIn(
            self.ksi2.ksi_name,
            [ksi["name"] for ksi in response_data["results"]],
            f"'{self.ksi2.ksi_name}' should not be listed in the results",
        )

    def test_create_ksi(self):
        """
        Ensure a KSI can be created by lead user.
        """
        payload = {
            "name": "New KSI",
            "description": "New KSI description",
            "start_date": "2024-02-01",
            "end_date": "2024-12-31",
            "status": "not_started",
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, "Status code is not 200 OK"
        )

        ksi = KSI.objects.get(ksi_name="New KSI")
        self.assertEqual(
            ksi.ksi_description,
            payload["description"],
            "KSI description should match the input.",
        )

    def test_update_ksi(self):
        """
        Ensure a KSI can be updated by department lead user.
        """
        payload = {"name": "Updated KSI Name"}
        response = self.client.patch(
            self.detail_url(self.ksi.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, "Status code is not 200 OK"
        )

        self.ksi.refresh_from_db()
        self.assertEqual(
            self.ksi.ksi_name, payload["name"], "KSI name should be updated."
        )

    def test_delete_ksi(self):
        """
        Ensure a KSI can be deleted by a department lead user.
        """
        response = self.client.delete(self.detail_url(self.ksi.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "KSI should be deleted successfully.",
        )
        self.assertFalse(
            KSI.objects.filter(id=self.ksi.id).exists(),
            "KSI should no longer exist in the database.",
        )

    def test_lead_from_other_department_update_ksi(self):
        """
        Ensure a KSI can't be updated by lead user from another department.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead2_token}")
        payload = {"name": "Updated KSI Name"}
        response = self.client.patch(
            self.detail_url(self.ksi.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND, "KSI should not be found."
        )

    def test_lead_from_another_department_delete_ksi(self):
        """
        Ensure a KSI can't be deleted by a lead user from another department.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead2_token}")
        response = self.client.delete(self.detail_url(self.ksi.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "KSI should not be found.",
        )
        self.assertTrue(
            KSI.objects.filter(id=self.ksi.id).exists(),
            "KSI should still exist in the database.",
        )

    def test_unauthorized_access(self):
        """
        Ensure unauthorized users cannot access the KSI endpoints.
        """
        self.client.credentials()
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthorized users should not be able to access KSIs.",
        )

    def test_regular_user_cannot_list_ksis(self):
        """
        Ensure a regular user cannot list KSIs.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to list KSIs.",
        )

    def test_regular_user_cannot_create_ksi(self):
        """
        Ensure a regular user cannot create a KSI.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {
            "name": "Unauthorized KSI",
            "description": "Should not be created",
            "start_date": "2024-02-01",
            "end_date": "2024-12-31",
            "department": self.department.id,
            "status": "not_started",
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to create a KSI.",
        )

    def test_regular_user_cannot_update_ksi(self):
        """
        Ensure a regular user cannot update a KSI.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {"name": "Unauthorized Update"}
        response = self.client.patch(
            self.detail_url(self.ksi.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to update a KSI.",
        )

    def test_regular_user_cannot_delete_ksi(self):
        """
        Ensure a regular user cannot delete a KSI.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.delete(self.detail_url(self.ksi.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to delete a KSI.",
        )
        self.assertTrue(
            KSI.objects.filter(id=self.ksi.id).exists(),
            "KSI should still be in the database.",
        )
