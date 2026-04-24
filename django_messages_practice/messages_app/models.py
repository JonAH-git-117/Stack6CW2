from django.db import models


class Message(models.Model):
    recipient = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_draft = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} -> {self.recipient}"
