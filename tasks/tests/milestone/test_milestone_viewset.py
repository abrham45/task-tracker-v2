from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from basedata.models import Department, Position
from tasks.models import KSI, Milestone
from users.models import Role

User = get_user_model()


class MilestoneViewSetTestCase(APITestCase):
    def setUp(self):
        # Create roles
        Role.objects.create(name="Super-Admin")
        Role.objects.create(name="Not-Assigned")
        leads_role = Role.objects.create(name="Leads")

        lead_permissions = [
            "add_milestone",
            "change_milestone",
            "delete_milestone",
            "view_milestone",
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
            milestone_description="Description for Milestone 1",
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

        # Generate JWT tokens
        self.lead_token = str(RefreshToken.for_user(self.lead_user).access_token)
        self.lead2_token = str(RefreshToken.for_user(self.lead_user2).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)

        # Authenticate as lead user for tests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead_token}")

        # Define URLs
        self.list_create_url = reverse("milestone-list", kwargs={"version": "v1"})
        self.detail_url = lambda pk: reverse(
            "milestone-detail", kwargs={"version": "v1", "pk": pk}
        )

    def test_list_milestones(self):
        """
        Ensure the department lead user can list all Milestones in its department.
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
        self.assertEqual(response_data["count"], 1, "There should be 1 milestone.")
        self.assertIn(
            self.milestone.milestone_name,
            [milestone["name"] for milestone in response_data["results"]],
            f"'{self.milestone.milestone_name}' should be listed in the results",
        )
        self.assertNotIn(
            self.milestone2.milestone_name,
            [milestone["name"] for milestone in response_data["results"]],
            f"'{self.milestone2.milestone_name}' should not be listed in the results",
        )

    def test_create_milestone(self):
        """
        Ensure the lead user can create a new Milestone.
        """
        payload = {
            "name": "New Milestone",
            "description": "New Milestone description",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "weight": "10",
            "ksi": self.ksi.id,
            "status": "not_started",
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Lead user should be able to create a milestone.",
        )
        self.assertTrue(
            Milestone.objects.filter(milestone_name="New Milestone").exists(),
            "Milestone should be created.",
        )

    def test_create_milestone_with_weight_over_100_for_ksi(self):
        """
        Ensure the lead user can't create a new Milestone with a
        weight sum over 100 for a ksi
        """
        payload = {
            "name": "New Milestone",
            "description": "New Milestone description",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "weight": "100",
            "ksi": self.ksi.id,
            "status": "not_started",
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Lead user shouldn't be able to create a milestone with weight over 100.",
        )
        self.assertIn(
            "weight",
            response.json()["errors"],
            "Response should include error message for weight.",
        )

    def test_update_milestone(self):
        """
        Ensure the lead user can update an existing Milestone.
        """
        payload = {"name": "Updated Milestone Name"}
        response = self.client.patch(
            self.detail_url(self.milestone.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Lead user should be able to update a milestone.",
        )
        self.milestone.refresh_from_db()
        self.assertEqual(
            self.milestone.milestone_name,
            payload["name"],
            "Milestone name should be updated.",
        )

    def test_update_milestone_with_weight_over_100_for_ksi(self):
        """
        Ensure the lead user can update an existing Milestone with
        weight over 100 for ksi.
        """
        self.new_milestone = Milestone.objects.create(
            milestone_name="Milestone 1",
            milestone_description="Description for Milestone 1",
            start_date="2024-01-01",
            end_date="2024-12-31",
            ksi=self.ksi,
            weight=50,
            status="in_progress",
            created_by=self.lead_user,
            updated_by=self.lead_user,
        )
        payload = {"weight": 100}
        response = self.client.patch(
            self.detail_url(self.new_milestone.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Lead user should not be able to update a milestone with weight over 100.",
        )
        self.assertIn(
            "weight",
            response.json()["errors"],
            "Response should include error message for weight.",
        )
        old_weight = self.new_milestone.weight
        self.new_milestone.refresh_from_db()
        self.assertEqual(
            self.new_milestone.weight,
            old_weight,
            "Milestone weight should not be updated.",
        )

    def test_delete_milestone(self):
        """
        Ensure the lead user can delete an existing Milestone.
        """
        response = self.client.delete(self.detail_url(self.milestone.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Lead user should be able to delete a milestone.",
        )
        self.assertFalse(
            Milestone.objects.filter(id=self.milestone.id).exists(),
            "Milestone should no longer exist in the database.",
        )

    def test_lead_from_other_department_update_milestone(self):
        """
        Ensure lead user from other department can update an existing Milestone.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead2_token}")
        payload = {"name": "Updated Milestone Name"}
        response = self.client.patch(
            self.detail_url(self.milestone.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Lead user shouldn't be able to find and update the milestone.",
        )

    def test_lead_from_other_department_delete_milestone(self):
        """
        Ensure lead user from other department can't delete an existing Milestone.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead2_token}")
        response = self.client.delete(self.detail_url(self.milestone.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Lead user shouldn't be able to find and delete a milestone.",
        )
        self.assertTrue(
            Milestone.objects.filter(id=self.milestone.id).exists(),
            "Milestone should still exist in the database.",
        )

    def test_unauthorized_access(self):
        """
        Ensure unauthorized users cannot access the milestone endpoints.
        """
        self.client.credentials()
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthorized users should not be able to access milestones.",
        )

    def test_regular_user_cannot_list_milestones(self):
        """
        Ensure a regular user cannot list the milestones.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to see milestones.",
        )

    def test_regular_user_cannot_create_milestone(self):
        """
        Ensure a regular user cannot create a new Milestone.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {
            "name": "New Milestone",
            "description": "New Milestone description",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "weight": "80",
            "ksi": self.ksi.id,
            "status": "not_started",
        }
        response = self.client.post(self.list_create_url, payload, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to create a new Milestone.",
        )

    def test_regular_user_cannot_update_milestone(self):
        """
        Ensure a regular user cannot update an existing Milestone.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {"name": "Updated Milestone Name"}
        response = self.client.patch(
            self.detail_url(self.milestone.id), payload, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to update a Milestone.",
        )

    def test_regular_user_cannot_delete_milestone(self):
        """
        Ensure a regular user cannot delete an existing Milestone.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.delete(self.detail_url(self.milestone.id))
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be able to delete a Milestone.",
        )
