from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from basedata.models import Department, Position
from tasks.models import KPI, KSI, Milestone
from users.models import Role

User = get_user_model()


class KPIViewSetTestCase(APITestCase):
    def setUp(self):
        # Create roles
        Role.objects.create(name="Super-Admin")
        Role.objects.create(name="Not-Assigned")
        leads_role = Role.objects.create(name="Leads")

        lead_permissions = [
            "add_kpi",
            "change_kpi",
            "delete_kpi",
            "view_kpi",
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
            status="pending",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )
        self.kpi2 = KPI.objects.create(
            kpi_name="KPI 2",
            start_date="2024-01-01",
            end_date="2024-12-31",
            milestone=self.milestone2,
            status="pending",
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
        self.list_create_url = reverse("kpi-list", kwargs={"version": "v1"})
        self.detail_url = lambda pk: reverse(
            "kpi-detail", kwargs={"version": "v1", "pk": pk}
        )

    def test_list_kpis(self):
        """
        Ensure the department lead user can list all KPIs in its department.
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
        self.assertEqual(response_data["count"], 1, "There should be 1 KPI.")
        self.assertIn(
            self.kpi.kpi_name,
            [kpi["name"] for kpi in response_data["results"]],
            f"'{self.kpi.kpi_name}' should be listed in the results",
        )
        self.assertNotIn(
            self.kpi2.kpi_name,
            [kpi["name"] for kpi in response_data["results"]],
            f"'{self.kpi2.kpi_name}' should not be listed in the results",
        )

    def test_create_kpi(self):
        """
        Ensure the lead user can create a new KPI.
        """
        payload = {
            "name": "New KPI",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "milestone": self.milestone.id,
            "status": "pending",
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Lead user should be able to create a KPI.",
        )
        self.assertTrue(
            KPI.objects.filter(kpi_name="New KPI").exists(),
            "KPI should be created.",
        )

    def test_update_kpi(self):
        """
        Ensure the lead user can update an existing KPI.
        """
        payload = {"name": "Updated KPI Name"}
        response = self.client.patch(
            self.detail_url(self.kpi.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Lead user should be able to update a KPI.",
        )
        self.kpi.refresh_from_db()
        self.assertEqual(
            self.kpi.kpi_name,
            payload["name"],
            "KPI name should be updated.",
        )

    def test_delete_kpi(self):
        """
        Ensure the lead user can delete an existing KPI.
        """
        response = self.client.delete(self.detail_url(self.kpi.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Lead user should be able to delete a KPI.",
        )
        self.assertFalse(
            KPI.objects.filter(id=self.kpi.id).exists(),
            "KPI should no longer exist in the database.",
        )

    def test_lead_from_other_department_update_kpi(self):
        """
        Ensure the lead user from other department can't update an existing KPI.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead2_token}")
        payload = {"name": "Updated KPI Name"}
        response = self.client.patch(
            self.detail_url(self.kpi.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Lead user should be able to find and update a KPI.",
        )

    def test_lead_from_other_department_delete_kpi(self):
        """
        Ensure the lead user from other department can't delete an existing KPI.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead2_token}")
        response = self.client.delete(self.detail_url(self.kpi.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Lead user should be able to find and delete a KPI.",
        )
        self.assertTrue(
            KPI.objects.filter(id=self.kpi.id).exists(),
            "KPI should still exist in the database.",
        )

    def test_unauthorized_access(self):
        """
        Ensure unauthorized users cannot access the KPI endpoints.
        """
        self.client.credentials()
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthorized users should not be able to access kPI.",
        )

    def test_regular_user_cannot_list_kpis(self):
        """
        Ensure a regular user cannot list the KPIs.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to see KPIs.",
        )

    def test_regular_user_cannot_create_kpi(self):
        """
        Ensure a regular user cannot create a new KPI.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {
            "name": "New KPI",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "milestone": self.milestone.id,
            "status": "pending",
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to create a new KPI.",
        )

    def test_regular_user_cannot_update_kpi(self):
        """
        Ensure a regular user cannot update an existing KPI.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {"name": "Updated KPI Name"}
        response = self.client.patch(
            self.detail_url(self.milestone.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to update a KPI.",
        )

    def test_regular_user_cannot_delete_kpi(self):
        """
        Ensure a regular user cannot delete an existing KPI.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.delete(self.detail_url(self.milestone.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to delete a KPI.",
        )
