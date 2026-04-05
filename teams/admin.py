import io
import os
from django.contrib import admin
from django.conf import settings
from django.http import FileResponse
from django.template.loader import render_to_string
from django.urls import path
from django.db.models import Count
from weasyprint import HTML, CSS

from .models import (
    Team, Skill, Dependency, 
    Organisation, Department, ContactChannel, 
    Repository, Project, Message, 
    Meeting, AuditLog
)

class TeamModelAdmin(admin.ModelAdmin):

    def get_urls(self):
        # Get the default admin URLs first
        urls = super().get_urls()
        # Add our custom report URL to the list
        custom_urls = [
            path('report/', self.admin_site.admin_view(self.report), name='teams_report'),
        ]
        # Custom URLs go first so they take priority over default URLs
        return custom_urls + urls

    def report(self, request):
        """Generate a PDF file from a string of HTML."""
        # Render the HTML template with all the data we want in the report
        html = render_to_string('admin/teams/report.html', {
            # Get all teams with their related department, organisation and manager
            # select_related performs a SQL JOIN to avoid extra queries
            'teams': Team.objects.select_related(
                'department',
                'department__organisation',
                'manager'
            ).prefetch_related('members'), # prefetch_related used for ManyToMany fields

            # Get all departments with a count of how many teams they have
            'departments': Department.objects.annotate(
                team_count=Count('teams')
            ).select_related('organisation'),

            # Filter to only get teams that have no manager assigned
            'teams_without_manager': Team.objects.filter(
                manager__isnull=True
            ).select_related('department'),

            # Summary counts for the report header
            'total_teams': Team.objects.count(),
            'total_departments': Department.objects.count(),
        })

        # Convert the HTML string into a WeasyPrint HTML object
        # base_url="" ensures relative URLs are handled correctly
        htmldoc = HTML(string=html, base_url="")

        # Generate the PDF, passing in the project's stylesheet
        # so the report styling matches the rest of the site
        pdf = htmldoc.write_pdf(
            stylesheets=[
                CSS(os.path.join(settings.BASE_DIR, 'teams', 'static', 'teams', 'style.css'))
            ]
        )

        # Write the PDF bytes to an in-memory buffer
        buffer = io.BytesIO(pdf)

        # Return the buffer as a downloadable PDF file attachment
        return FileResponse(buffer, as_attachment=True, filename='sky_teams_report.pdf')

# Register Team with our custom admin class for report generation
admin.site.register(Team, TeamModelAdmin)

# All other models registered with default admin
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