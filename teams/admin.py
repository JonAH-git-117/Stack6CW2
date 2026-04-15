import io
import os
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse   # changed
from django.template.loader import render_to_string
from django.urls import path
from django.db.models import Count

# from weasyprint import HTML, CSS

from .models import (
    Team, Skill, Dependency, 
    Organisation, Department, ContactChannel, 
    Repository, Project, Message, 
    Meeting, AuditLog
)


class TeamModelAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('report/', self.admin_site.admin_view(self.report), name='teams_report'),
        ]
        return custom_urls + urls

    def report(self, request):
        """Temporarily disabled PDF generation to avoid WeasyPrint errors."""

        html = render_to_string('admin/teams/report.html', {
            'teams': Team.objects.select_related(
                'department',
                'department__organisation',
                'manager'
            ).prefetch_related('members'),

            'departments': Department.objects.annotate(
                team_count=Count('teams')
            ).select_related('organisation'),

            'teams_without_manager': Team.objects.filter(
                manager__isnull=True
            ).select_related('department'),

            'total_teams': Team.objects.count(),
            'total_departments': Department.objects.count(),
        })

        return HttpResponse("PDF generation temporarily disabled")


# Register models
admin.site.register(Team, TeamModelAdmin)
admin.site.register(Skill)
admin.site.register(Dependency)
admin.site.register(Organisation)
admin.site.register(Department)
admin.site.register(ContactChannel)
admin.site.register(Repository)
admin.site.register(Project)
admin.site.register(Message)
admin.site.register(Meeting)
admin.site.register(AuditLog)