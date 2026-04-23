# visualisation/tests.py
# Author: Jonathan Chamberlain (Student 5+6)
# Tests for the visualisation app — checks the Bokeh chart page loads correctly
# under various data conditions: single team, multiple teams, disabled teams.

from django.test import TestCase, Client
from django.contrib.auth.models import User
from teams.models import Organisation, Department, Team


class VisualisationViewTestCase(TestCase):

    def setUp(self):
        """
        setUp runs before every individual test method.
        Creates a test client, a regular user, and a minimal
        Organisation > Department > Team hierarchy so the
        Bokeh charts have data to render.
        The test database is isolated — real data is never affected.
        """
        self.client = Client()

        # Regular user for testing authenticated access
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Minimal org structure required for Team creation
        self.org = Organisation.objects.create(
            organisation_name='Sky',
            organisation_description='Sky Test Org'
        )
        self.dept = Department.objects.create(
            department_name='xTV_Web',
            department_description='Test Department',
            organisation=self.org
        )

        # One active team to serve as baseline chart data
        self.team = Team.objects.create(
            name='Code Warriors',
            description='Test team',
            status='active',
            department=self.dept
        )

    def test_visualisation_page_requires_login(self):
        """
        Test that an unauthenticated user is redirected away from the
        visualisation page. Verifies @login_required is applied to the view.
        """
        response = self.client.get('/visualisation/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_visualisation_page_loads_when_logged_in(self):
        """
        Test that the visualisation page returns HTTP 200 for a logged-in user.
        Confirms Bokeh chart generation completes without errors.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/visualisation/')
        self.assertEqual(response.status_code, 200)

    def test_visualisation_contains_chart(self):
        """
        Test that the visualisation page embeds Bokeh chart content.
        Bokeh renders charts by injecting a <script> tag into the page —
        assertContains checks this tag is present in the response HTML.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/visualisation/')
        self.assertContains(response, 'script')

    def test_visualisation_shows_department_name(self):
        """
        Test that the department name appears in the chart data on the page.
        Confirms the Bokeh chart is reading department names from the database.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/visualisation/')
        self.assertContains(response, 'xTV_Web')

    def test_visualisation_with_multiple_teams(self):
        """
        Test that the visualisation page handles multiple teams without errors.
        Adds a second team to the same department and confirms the page
        still returns HTTP 200, verifying the chart scales with more data.
        """
        Team.objects.create(
            name='The Debuggers',
            description='Second test team',
            status='active',
            department=self.dept
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/visualisation/')
        self.assertEqual(response.status_code, 200)

    def test_visualisation_with_disabled_team(self):
        """
        Test that the visualisation page handles disabled teams correctly.
        Adds a disabled team and confirms the page returns HTTP 200,
        verifying the Active vs Disabled chart accounts for both statuses.
        """
        Team.objects.create(
            name='Old Team',
            description='Disbanded team',
            status='disabled',
            department=self.dept
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/visualisation/')
        self.assertEqual(response.status_code, 200)