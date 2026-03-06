from django.db import models
from django.conf import settings


class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
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