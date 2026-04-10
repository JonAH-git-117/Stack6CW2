from django.contrib import admin
from .models import (
    Team, Skill, Dependency, 
    Organisation, Department, ContactChannel, 
    Repository, Project, Message, 
    Meeting, AuditLog
)

admin.site.register(Team)
admin.site.register(Skill)
admin.site.register(Dependency)
# added to admin file on 11 / 03 / 2026
admin.site.register(Organisation)
admin.site.register(Department)
# added new models to admin on 18 / 03 / 2026
admin.site.register(ContactChannel)
admin.site.register(Repository)
admin.site.register(Project)
admin.site.register(Message)
admin.site.register(Meeting)
admin.site.register(AuditLog)