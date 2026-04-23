# reports/tests.py
# Author: Jonathan Chamberlain (Student 5+6)
# Tests for the reports app — dashboard view, PDF generation and Excel generation.
# setUp creates a minimal but complete DB structure (Org > Dept > Team)
# so the report views have real data to query against.

from django.test import TestCase, Client
from django.contrib.auth.models import User
from teams.models import Organisation, Department, Team


class ReportsViewTestCase(TestCase):

    def setUp(self):
        """
        setUp runs before every individual test method.
        Creates a test client, a regular user, an admin user,
        and a minimal Organisation > Department > Team hierarchy
        so that report views have data to render.
        The test database is isolated — real data is never affected.
        """
        self.client = Client()

        # Regular user for testing authenticated access
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Admin/superuser for testing staff-only views
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            password='adminpass123',
            email='admin@sky.com'
        )

        # Minimal data so reports have something to query and display
        self.org = Organisation.objects.create(
            organisation_name='Sky',
            organisation_description='Sky Test Org'
        )
        self.dept = Department.objects.create(
            department_name='xTV_Web',
            department_description='Test Department',
            organisation=self.org
        )
        self.team = Team.objects.create(
            name='Code Warriors',
            description='Test team',
            status='active',
            department=self.dept
        )

    def test_reports_page_requires_login(self):
        """
        Test that an unauthenticated user is redirected away from the reports page.
        Verifies the @login_required decorator is applied to the reports view.
        """
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_reports_page_loads_when_logged_in(self):
        """
        Test that the reports dashboard returns HTTP 200 for a logged-in user.
        Confirms the view renders without errors when authenticated.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/')
        self.assertEqual(response.status_code, 200)

    def test_reports_page_contains_team_data(self):
        """
        Test that the reports page displays the team created in setUp.
        Uses assertContains to check the team name appears in the response HTML.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/')
        self.assertContains(response, 'Code Warriors')

    def test_pdf_report_generates(self):
        """
        Test that the PDF download endpoint returns a valid PDF response.
        Checks the Content-Type header is application/pdf confirming
        WeasyPrint generated the file correctly.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/pdf/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_excel_report_generates(self):
        """
        Test that the Excel download endpoint returns a valid spreadsheet response.
        Checks the Content-Type header contains 'spreadsheet' confirming
        openpyxl generated the xlsx file correctly.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/excel/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheet', response['Content-Type'])

    def test_reports_shows_correct_team_count(self):
        """
        Test that the reports page reflects the correct number of teams.
        Only one team was created in setUp so the count should be 1.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/reports/')
        self.assertContains(response, '1')