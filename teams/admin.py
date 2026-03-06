from django.contrib import admin
from .models import Team, Skill, Dependency
from django.contrib.auth.models import User

admin.site.register(Team)
admin.site.register(Skill)
admin.site.register(Dependency)
