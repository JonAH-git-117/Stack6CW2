from django.db import models
from django.conf import settings

# adding classes to better reflect the logical ERD

class Organisation(models.Model):
    
    # an important note for those looking over this model, the "Primary Key" is created automatically for each class as "id"
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

class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    # including a Foreign Key for linking the Team(s) and Department(s) together
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE, 
        related_name='teams', 
        null=True, 
        blank=True
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_teams'
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='teams'
    )

    email = models.EmailField()

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

    def __str__(self):
        return f"{self.team} depends on {self.depends_on}"