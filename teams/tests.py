from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import ContactChannel, Department, Dependency, Meeting, Organisation, Repository, Skill, Team, TeamType


class OrganisationPageEmptyDatabaseTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="viewer",
            password="test-password",
        )

    def test_anonymous_user_redirected_from_root_organisations_page(self):
        response = self.client.get("/organisations/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertIn("next=/organisations/", response.url)

    def test_logged_in_user_can_access_empty_organisation_page(self):
        self.client.force_login(self.user)

        response = self.client.get("/organisations/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Organisation Structure")
        self.assertContains(response, "No organisations found.")
        self.assertContains(response, "No team types created yet.")
        self.assertContains(response, "No dependencies recorded yet.")


class OrganisationPageDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="viewer", password="test-password")
        cls.dept_head = User.objects.create_user(
            username="alex_head",
            password="test-password",
            first_name="Alex",
            last_name="Leader",
        )
        cls.manager = User.objects.create_user(
            username="manager_user",
            password="test-password",
            first_name="Morgan",
            last_name="Manager",
        )

        cls.organisation = Organisation.objects.create(
            organisation_name="Sky Engineering",
            organisation_description="Engineering organisation for team discovery.",
        )
        cls.department = Department.objects.create(
            department_name="Platform Engineering",
            department_description="Builds shared platforms.",
            department_location="Osterley",
            specialisation="Backend services",
            organisation=cls.organisation,
            dept_head=cls.dept_head,
        )
        cls.product_department = Department.objects.create(
            department_name="Product Engineering",
            department_description="Builds product journeys.",
            department_location="Leeds",
            specialisation="Customer products",
            organisation=cls.organisation,
        )

        cls.platform_type = TeamType.objects.create(
            name="Platform",
            description="Shared services and API teams.",
        )
        cls.product_type = TeamType.objects.create(
            name="Product",
            description="Product delivery teams.",
        )

        cls.backend_team = Team.objects.create(
            name="Backend Services",
            description="Provides backend APIs.",
            department=cls.department,
            manager=cls.manager,
            team_type=cls.platform_type,
        )
        cls.frontend_team = Team.objects.create(
            name="Frontend Development",
            description="Builds web features.",
            department=cls.product_department,
            manager=cls.manager,
            team_type=cls.product_type,
        )
        cls.mobile_team = Team.objects.create(
            name="Mobile Apps",
            description="Builds mobile features.",
            department=cls.product_department,
            manager=cls.manager,
            team_type=cls.product_type,
        )

        Dependency.objects.create(
            team=cls.frontend_team,
            depends_on=cls.backend_team,
            dependency_type="API",
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_organisation_department_leader_specialisation_and_teams_display(self):
        response = self.client.get("/organisations/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sky Engineering")
        self.assertContains(response, "Platform Engineering")
        self.assertContains(response, "Alex Leader")
        self.assertContains(response, "Backend services")
        self.assertContains(response, "Backend Services")

    def test_team_type_displays_when_assigned(self):
        response = self.client.get("/organisations/")

        self.assertContains(response, "Platform")
        self.assertContains(response, "Shared services and API teams.")
        self.assertContains(response, "Product")

    def test_upstream_downstream_dependency_relationship_displays(self):
        response = self.client.get("/organisations/")

        self.assertContains(response, "Frontend Development depends on Backend Services")
        self.assertContains(response, "Backend Services is upstream of Frontend Development")
        self.assertContains(response, "Frontend Development is downstream from Backend Services")
        self.assertContains(response, "API")

    def test_teams_app_organisation_url_also_works(self):
        response = self.client.get(reverse("organisation_page"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Organisation Structure")

    def test_team_detail_view_organisation_link_uses_root_route(self):
        response = self.client.get(reverse("team_detail", args=[self.backend_team.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/organisations/"')
        self.assertContains(response, "Team Type")
        self.assertContains(response, "Platform")

    def test_search_filter_returns_expected_content(self):
        response = self.client.get("/organisations/", {"q": "Frontend"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Frontend Development")
        self.assertContains(response, "Backend Services")
        self.assertNotContains(response, "Mobile Apps")

    def test_department_and_team_type_filters_return_expected_content(self):
        response = self.client.get(
            "/organisations/",
            {
                "department": str(self.department.id),
                "team_type": str(self.platform_type.id),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend Services")


class TeamAndScheduleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(
            username="teamviewer",
            password="test-password",
            first_name="Taylor",
            last_name="Manager",
            email="manager@example.com",
        )
        cls.member = User.objects.create_user(
            username="member1",
            password="test-password",
            email="member1@example.com",
        )
        org = Organisation.objects.create(
            organisation_name="Sky",
            organisation_description="Demo org",
        )
        cls.department = Department.objects.create(
            department_name="Search Department",
            department_description="Department for search tests.",
            organisation=org,
        )
        cls.team_type = TeamType.objects.create(name="Delivery")
        cls.team = Team.objects.create(
            name="Searchable Team",
            description="Mission and responsibilities for the team.",
            department=cls.department,
            manager=cls.user,
            team_type=cls.team_type,
        )
        cls.team.members.add(cls.member)
        Skill.objects.create(team=cls.team, name="Python")
        Repository.objects.create(
            team=cls.team,
            name="Main Repository",
            url="https://example.com/repo",
        )
        ContactChannel.objects.create(
            team=cls.team,
            channel_type="email",
            channel_value="searchable@example.com",
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_team_list_keyword_search_matches_department_and_manager(self):
        by_department = self.client.get("/teams/", {"keyword": "Search Department"})
        by_manager = self.client.get("/teams/", {"keyword": "Taylor"})

        self.assertContains(by_department, "Searchable Team")
        self.assertContains(by_manager, "Searchable Team")

    def test_team_detail_displays_core_team_information(self):
        response = self.client.get(reverse("team_detail", args=[self.team.id]))

        self.assertContains(response, "Mission and responsibilities")
        self.assertContains(response, "teamviewer")
        self.assertContains(response, "member1")
        self.assertContains(response, "Python")
        self.assertContains(response, "Main Repository")
        self.assertContains(response, "Open Link")

    def test_schedule_page_creates_meeting(self):
        response = self.client.post("/teams/schedule-meeting/", {
            "title": "Planning Meeting",
            "team": str(self.team.id),
            "date": (timezone.now() + timezone.timedelta(days=1)).date().isoformat(),
            "time": "10:30",
            "platform": "teams",
            "attendees": [str(self.member.id)],
            "agenda": "Planning agenda",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Meeting.objects.filter(title="Planning Meeting").exists())
