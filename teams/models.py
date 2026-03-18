from django.db import models
from django.conf import settings

# adding classes to better reflect the logical ERD

class Organisation(models.Model):
    
    # an important note for those looking over this model, the "Primary Key" is created automatically 
    # for each class as "id"
    organisation_name = models.CharField(max_length=100)
    organisation_description = models.TextField()

    def __str__(self):
        return self.organisation_name

class Department(models.Model):
    
    department_name = models.CharField(max_length=100)
    department_description = models.TextField()
    department_location = models.CharField(max_length=100, blank=True, null=True)
    
    # organisationID FK
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="departments"
    )
    # userID FK
    dept_head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments"
    )

    def __str__(self):
        return self.department_name

class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    # including a Foreign Key for linking the Team(s) and Department(s) together
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='teams', 
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_teams'
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='teams',
        blank=True
    )

    def __str__(self):
        return self.name

# Contact Channel was implemented as per the logical ERD

class ContactChannel(models.Model):
    Channel_Types = [
        ("slack", "Slack"),
        ("teams", "Microsoft Teams"),
        ("email", "Email"),
        ("other", "Other"),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="contact_channels")
    Channel_Types = models.CharField(max_length=20, choices=Channel_Types)
    Channel_Value = models.CharField(max_length=255) # e.g. #team-name or email address

    def __str__(self):
        return f"{self.team} - {self.Channel_Types}: {self.Channel_Value}"

# Repository was included 

class Repository(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='repositories')
    name = models.CharField(max_length=100)
    url = models.URLField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# skills were factored into how the models relate to one another

class Skill(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='skills')

    def __str__(self):
        return self.name

class Dependency(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='dependencies')
    depends_on = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='dependent_teams')

    class Meta:
        unique_together = ('team', 'depends_on')  # prevent duplicate dependency entries

    def __str__(self):
        return f"{self.team} depends on {self.depends_on}"

# Implemented a project 

class Project(models.Model):
    STATUS_CHOICES = [
        ("blocked" "Blocked"),
        ("planned", "Planned"),
        ("active", "Active"),
        ("completed", "Completed"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    # Many teams can work on the same project, and a team can have many projects
    teams = models.ManyToManyField(
        Team,
        related_name='projects',
        blank=True
    )
    # Members assigned specifically to this project (may differ from team members)
    assigned_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='projects',
        blank=True
    )

    def __str__(self):
        return self.name

class Message(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
    ]
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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.subject} ({self.status})"


class Meeting(models.Model):
    PLATFORM_CHOICES = [
        ('zoom', 'Zoom'),
        ('teams', 'Microsoft Teams'),
        ('google_meet', 'Google Meet'),
        ('in_person', 'In Person'),
        ('other', 'Other'),
    ]
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
    message = models.TextField(blank=True, null=True) # optional notes/agenda

    def __str__(self):
        return f"{self.title} at {self.scheduled_at}"


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=255) # e.g. "Updated Team", "Deleted Department"
    model_name = models.CharField(max_length=100) # e.g. "Team", "Department"
    object_id = models.PositiveIntegerField() # ID of the affected record
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True) # optional extra info

    def __str__(self):
        return f"{self.user} - {self.action} on {self.model_name} ({self.timestamp})"