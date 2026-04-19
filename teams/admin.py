import io
import os
from django.contrib import admin
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import path
from django.db.models import Count
from django.template.response import TemplateResponse
from django.contrib.auth.models import User

# from weasyprint import HTML, CSS

from .models import (
    Team, Skill, Dependency, 
    Organisation, Department, ContactChannel, 
    Repository, Project, Message, 
    Meeting, AuditLog
)


class TeamModelAdmin(admin.ModelAdmin):

    def get_urls(self):
        """Register custom admin URLs for report and admin dashboard pages."""
        urls = super().get_urls()
        custom_urls = [
            # URL for PDF report generation 
            path('report/', self.admin_site.admin_view(self.report), name='teams_report'),
            # URL for admin dashboard overview page 
            path('admin-dashboard/', self.admin_site.admin_view(self.admin_dashboard), name='admin_dashboard'),
        ]
        return custom_urls + urls

    def report(self, request):
        """
        Generates an HTML report of teams and departments.
        Uses render_to_string to build the report template context.
        WeasyPrint PDF generation temporarily disabled.
        """
        html = render_to_string('admin/teams/report.html', {
            # All teams with related department, organisation and manager data
            'teams': Team.objects.select_related(
                'department',
                'department__organisation',
                'manager'
            ).prefetch_related('members'),

            # Departments annotated with their team count
            'departments': Department.objects.annotate(
                team_count=Count('teams')
            ).select_related('organisation'),

            # Teams that have no manager assigned
            'teams_without_manager': Team.objects.filter(
                manager__isnull=True
            ).select_related('department'),

            'total_teams': Team.objects.count(),
            'total_departments': Department.objects.count(),
        })

        return HttpResponse("PDF generation temporarily disabled")

    def admin_dashboard(self, request):
        """
        Renders the admin dashboard overview page (Wireframe 10).
        Provides summary statistics and recent audit trail entries.
        Uses TemplateResponse as per lecture pattern for custom admin pages.
        """
        context = dict(
            # Includes admin site context (user, site title etc.)
            self.admin_site.each_context(request),
            # Summary card data
            total_teams=Team.objects.count(),
            total_users=User.objects.count(),
            disabled_users=User.objects.filter(is_active=False).count(),
            # Most recent 5 audit log entries
            recent_audit=AuditLog.objects.order_by('-id')[:5],
        )
        return TemplateResponse(request, 'admin/teams/admin_dashboard.html', context)


# Register all models with the Django admin site
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