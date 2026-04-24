from django.db import models
from django.conf import settings


class Organisation(models.Model):
    organisation_name = models.CharField(max_length=100)
    organisation_description = models.TextField()

    def __str__(self):
        return self.organisation_name


class Department(models.Model):
    department_name = models.CharField(max_length=100)
    department_description = models.TextField()
    department_location = models.CharField(max_length=100, blank=True, null=True)
    specialisation = models.CharField(max_length=150, blank=True, default="")

    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="departments"
    )

    dept_head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments"
    )

    def __str__(self):
        return self.department_name


class TeamType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Team(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("disabled", "Disabled"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='teams'
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_teams'
    )

    team_type = models.ForeignKey(
        TeamType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teams"
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='teams',
        blank=True
    )

    def __str__(self):
        return self.name


class ContactChannel(models.Model):
    CHANNEL_TYPES = [
        ("slack", "Slack"),
        ("teams", "Microsoft Teams"),
        ("email", "Email"),
        ("jira", "Jira Board"),
        ("other", "Other"),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="contact_channels")
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES)
    channel_value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.team} - {self.channel_type}: {self.channel_value}"


class Repository(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='repositories')
    name = models.CharField(max_length=100)
    url = models.URLField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='skills')

    def __str__(self):
        return self.name


class Dependency(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='dependencies')
    depends_on = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='dependent_teams')
    dependency_type = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        unique_together = ('team', 'depends_on')

    def __str__(self):
        return f"{self.team} depends on {self.depends_on}"


class Project(models.Model):
    STATUS_CHOICES = (
        ("blocked", "Blocked"),
        ("planned", "Planned"),
        ("active", "Active"),
        ("completed", "Completed"),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned"
    )

    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    teams = models.ManyToManyField(Team, related_name='projects', blank=True)
    assigned_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='projects', blank=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='received_messages'
    )

    subject = models.CharField(max_length=255)
    body = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.subject} ({self.status})"


class Meeting(models.Model):
    PLATFORM_CHOICES = (
        ('zoom', 'Zoom'),
        ('teams', 'Microsoft Teams'),
        ('google_meet', 'Google Meet'),
        ('in_person', 'In Person'),
        ('other', 'Other'),
    )

    title = models.CharField(max_length=255)

    organiser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organised_meetings'
    )

    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='meetings',
        blank=True
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='meetings'
    )

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    scheduled_at = models.DateTimeField()
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} at {self.scheduled_at}"


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )

    action = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.action} on {self.model_name} ({self.timestamp})"
