from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from basedata.models import Department, Position
from users.models import Role

User = get_user_model()


class PositionViewSetTestCase(APITestCase):
    def setUp(self):
        # Create roles
        Role.objects.create(name="Super-Admin")
        Role.objects.create(name="Not-Assigned")
        leads_role = Role.objects.create(name="Leads")
        hr_role = Role.objects.create(name="HR")

        lead_permissions = [
            "view_position",
        ]
        for perm in lead_permissions:
            leads_role.permissions.add(
                *Permission.objects.filter(
                    codename=perm,
                )
            )

        hr_permissions = [
            "add_position",
            "change_position",
            "delete_position",
            "view_position",
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

        self.lead_user = User.objects.create_user(
            email="lead.user@email.com",
            password="1234abcd!A",
            first_name="Lead",
            last_name="User",
        )
        self.lead_user.is_active = True
        self.lead_user.department = self.department1
        self.lead_user.groups.add(leads_role)
        self.lead_user.save()

        self.lead_user2 = User.objects.create_user(
            email="lead2.user@email.com",
            password="1234abcd!A",
            first_name="Lead 2",
            last_name="User",
        )
        self.lead_user2.is_active = True
        self.lead_user2.department = self.department2
        self.lead_user2.groups.add(leads_role)
        self.lead_user2.save()

        self.position1 = Position.objects.create(
            department=self.department1,
            position_name="Lead",
            position_description="Handles technical tasks.",
            created_by=self.hr_user,
            updated_by=self.hr_user,
        )
        self.lead_user.position = self.position1
        self.lead_user.save()

        self.position2 = Position.objects.create(
            department=self.department1,
            position_name="SWE1",
            position_description="Handles technical tasks.",
            created_by=self.hr_user,
            updated_by=self.hr_user,
        )

        self.position3 = Position.objects.create(
            department=self.department1,
            position_name="UI-UX 1",
            position_description="Handles user interfaces.",
            created_by=self.hr_user,
            updated_by=self.hr_user,
        )
        self.position4 = Position.objects.create(
            department=self.department2,
            position_name="HR Lead",
            created_by=self.hr_user,
            updated_by=self.hr_user,
        )
        self.lead_user2.position = self.position4
        self.lead_user2.save()

        self.position5 = Position.objects.create(
            department=self.department2,
            position_name="Technical Recruiter 1",
            created_by=self.hr_user,
            updated_by=self.hr_user,
        )

        # Generate JWT tokens for the users
        self.admin_token = str(RefreshToken.for_user(self.admin_user).access_token)
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.hr_user_token = str(RefreshToken.for_user(self.hr_user).access_token)
        self.lead_user_token = str(RefreshToken.for_user(self.lead_user).access_token)
        self.lead_user2_token = str(RefreshToken.for_user(self.lead_user2).access_token)

        # Authenticate as admin user for tests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.hr_user_token}")

        # Define URLs
        self.list_create_url = reverse("position-list", kwargs={"version": "v1"})
        self.detail_url = lambda pk: reverse(
            "position-detail", kwargs={"version": "v1", "pk": pk}
        )

    def test_list_positions(self):
        """
        Ensure the hr user can list all positions.
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
            response_data["count"], 5, "There should be 5 departments in total"
        )

    def test_list_positions_department_leads(self):
        """
        Ensure the lead user can list all positions in its department.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.lead_user_token}")
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
            response_data["count"], 3, "There should be 3 departments in total"
        )

        results = response_data["results"]
        self.assertIn(
            self.position1.position_name,
            [position["name"] for position in results],
            f"'{self.position1.position_name}' should be listed in the results",
        )
        self.assertNotIn(
            self.position4.position_name,
            [position["name"] for position in results],
            f"'{self.position4.position_name}' should be listed in the results",
        )

    def test_list_position_unauthorized(self):
        """
        Ensure unauthorized users cannot list positions.
        """
        self.client.credentials()
        response = self.client.get(self.list_create_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Unauthorized users should receive 401",
        )

    def test_create_position(self):
        """
        Ensure the hr user can create a new position.
        """
        data = {"name": "DevOps 1", "department": str(self.department1.id)}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Position should be created successfully",
        )
        self.assertEqual(
            response.json()["data"]["name"],
            "DevOps 1",
            "Position name should be 'DevOps 1'",
        )
        self.assertTrue(
            Position.objects.filter(position_name="DevOps 1").exists(),
            "Position should be saved in the database",
        )

    def test_create_position_forbidden(self):
        """
        Ensure non-hr users cannot create positions.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        data = {
            "name": "Marketing manager 1",
            "description": "Handles marketing tasks.",
        }
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular User should not be allowed to create positions",
        )

    def test_update_position(self):
        """
        Ensure the hr user can update a position.
        """
        data = {"description": "Handles software development."}
        response = self.client.patch(
            self.detail_url(self.position1.id), data, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Position should be updated successfully",
        )
        self.assertEqual(
            response.json()["data"]["description"],
            "Handles software development.",
            "Position description should be updated",
        )

    def test_update_position_unauthorized(self):
        """
        Ensure non-hr users cannot update positions.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        data = {"name": "NewName", "description": "New description."}
        response = self.client.put(
            self.detail_url(self.position1.id), data, format="json"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be allowed to update positions",
        )

    def test_delete_position(self):
        """
        Ensure the hr user can delete a position.
        """
        response = self.client.delete(self.detail_url(self.position5.id), format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Position should be deleted successfully",
        )
        self.assertFalse(
            Position.objects.filter(id=self.position5.id).exists(),
            "Deleted position should no longer exist",
        )

    def test_delete_position_unauthorized(self):
        """
        Ensure non-hr users cannot delete departments.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.delete(self.detail_url(self.position5.id), format="json")
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Regular user should not be allowed to delete departments",
        )

    def tearDown(self):
        Position.objects.all().delete()
        Department.objects.all().delete()
        User.objects.all().delete()
        Role.objects.all().delete()
