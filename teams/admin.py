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
    Team, TeamType, Skill, Dependency,
    Organisation, Department, ContactChannel, 
    Repository, Project, Message, 
    Meeting, AuditLog
)


class TeamModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'manager', 'team_type', 'status')
    search_fields = ('name', 'department__department_name', 'manager__username')
    list_filter = ('status', 'department', 'team_type')

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
        Renders the admin teams report page using the existing report.html template.
        Uses TemplateResponse consistent with the admin_dashboard view above.
        WeasyPrint PDF generation temporarily disabled — HTML rendered instead.
        """
        context = dict(
            self.admin_site.each_context(request),
            teams=Team.objects.select_related(
                'department',
                'department__organisation',
                'manager'
            ).prefetch_related('members'),
            departments=Department.objects.annotate(
                team_count=Count('teams')
            ).select_related('organisation'),
            teams_without_manager=Team.objects.filter(
                manager__isnull=True
            ).select_related('department'),
            total_teams=Team.objects.count(),
            total_departments=Department.objects.count(),
        )
        return TemplateResponse(request, 'admin/teams/report.html', context)

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


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('organisation_name',)
    search_fields = ('organisation_name', 'organisation_description')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_name', 'organisation', 'dept_head', 'specialisation')
    search_fields = (
        'department_name',
        'department_description',
        'specialisation',
        'dept_head__username',
        'dept_head__first_name',
        'dept_head__last_name',
    )
    list_filter = ('organisation',)


class TeamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


class DependencyAdmin(admin.ModelAdmin):
    list_display = ('team', 'depends_on', 'dependency_type')
    search_fields = ('team__name', 'depends_on__name', 'dependency_type')
    list_filter = ('dependency_type',)


# Register all models with the Django admin site
admin.site.register(Team, TeamModelAdmin)
admin.site.register(TeamType, TeamTypeAdmin)
admin.site.register(Skill)
admin.site.register(Dependency, DependencyAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(ContactChannel)
admin.site.register(Repository)
admin.site.register(Project)
admin.site.register(Message)
admin.site.register(Meeting)
admin.site.register(AuditLog)
