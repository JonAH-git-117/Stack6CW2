from django.contrib.auth.models import User
from django.test import TestCase

from .models import Message


class MessagesViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="messageuser",
            password="testpass123",
        )

    def test_inbox_requires_login(self):
        response = self.client.get("/messages/inbox/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_inbox_loads_for_logged_in_user(self):
        self.client.login(username="messageuser", password="testpass123")
        Message.objects.create(
            recipient="messageuser",
            subject="Welcome",
            body="Hello from the portal.",
        )

        response = self.client.get("/messages/inbox/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome")

    def test_send_new_message_creates_sent_message(self):
        self.client.login(username="messageuser", password="testpass123")

        response = self.client.post("/messages/new/", {
            "recipient": "Code Warriors",
            "subject": "Standup",
            "body": "Please join the standup.",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Message.objects.filter(subject="Standup", is_draft=False).exists())

    def test_save_draft_creates_draft_message(self):
        self.client.login(username="messageuser", password="testpass123")

        response = self.client.post("/messages/new/", {
            "recipient": "Mobile Apps",
            "subject": "Draft update",
            "body": "Draft body.",
            "save_draft": "1",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Message.objects.filter(subject="Draft update", is_draft=True).exists())

    def test_sent_and_drafts_views_load(self):
        self.client.login(username="messageuser", password="testpass123")
        Message.objects.create(recipient="A", subject="Sent", body="Body", is_draft=False)
        Message.objects.create(recipient="B", subject="Draft", body="Body", is_draft=True)

        sent_response = self.client.get("/messages/sent/")
        draft_response = self.client.get("/messages/drafts/")

        self.assertEqual(sent_response.status_code, 200)
        self.assertEqual(draft_response.status_code, 200)
        self.assertContains(sent_response, "Sent")
        self.assertContains(draft_response, "Draft")
