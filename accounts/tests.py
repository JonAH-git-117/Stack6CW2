# accounts/tests.py
# Author: Jonathan Chamberlain (Student 5+6)
# Tests for the accounts app — login, signup, profile, update profile,
# change password and logout views

from django.test import TestCase, Client
from django.contrib.auth.models import User


class AccountsViewTestCase(TestCase):

    def setUp(self):
        """
        setUp runs before every individual test method.
        Creates a test user and a test client to simulate browser requests.
        A fresh test database is created for each test run — real data is never affected.
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@sky.com',
            first_name='Test',
            last_name='User'
        )

    def test_login_page_loads(self):
        """
        Test that the login page returns HTTP 200 (OK) for unauthenticated users.
        Verifies the login URL is accessible and the view renders correctly.
        """
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_with_valid_credentials(self):
        """
        Test that posting valid credentials to the login view
        redirects the user (HTTP 302) — indicating successful authentication.
        """
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_with_invalid_credentials(self):
        """
        Test that posting incorrect credentials keeps the user
        on the login page (HTTP 200) rather than redirecting them.
        """
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_signup_page_loads(self):
        """
        Test that the signup/registration page returns HTTP 200.
        Verifies the self-registration page is accessible to unauthenticated users.
        """
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user(self):
        """
        Test that submitting the signup form with valid data
        creates a new User record in the database.
        Uses assertIs to confirm the user now exists after POST.
        """
        self.client.post('/accounts/signup/', {
            'username': 'newuser',
            'password1': 'Skypass123!',
            'password2': 'Skypass123!',
            'email': 'newuser@sky.com',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_profile_page_requires_login(self):
        """
        Test that an unauthenticated user attempting to access a profile page
        is redirected (HTTP 302) to the login page.
        Uses assertIn to confirm the redirect target is the login URL.
        """
        response = self.client.get('/accounts/profile/testuser/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_page_loads_when_logged_in(self):
        """
        Test that an authenticated user can access their own profile page
        and receive HTTP 200 (OK).
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/accounts/profile/{self.user.username}/')
        self.assertEqual(response.status_code, 200)

    def test_update_profile_requires_login(self):
        """
        Test that the update profile page redirects unauthenticated users.
        Ensures the @login_required decorator is working correctly.
        """
        response = self.client.get('/accounts/update-profile/')
        self.assertEqual(response.status_code, 302)

    def test_logout_redirects(self):
        """
        Test that logging out redirects the user (HTTP 302).
        Confirms the logout view terminates the session and redirects correctly.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 302)

    def test_change_password_requires_login(self):
        """
        Test that the change password page redirects unauthenticated users.
        Ensures protected views are not accessible without a valid session.
        """
        response = self.client.get('/accounts/change-password/')
        self.assertEqual(response.status_code, 302)