from django.contrib import admin
from .models import Team, Skill, Dependency, Organisation, Department
from django.contrib.auth.models import User

admin.site.register(Team)
admin.site.register(Skill)
admin.site.register(Dependency)
# added to admin file on 11 / 03 / 2026
admin.site.register(Organisation)
admin.site.register(Department)