from django.shortcuts import render

# Create your views here.
import io
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.db.models import Count
from weasyprint import HTML, CSS

from teams.models import Team, Department, Organisation


@login_required
def reports_dashboard(request):
    """Display the reports dashboard page."""
    # Get summary statistics to display on the dashboard
    total_teams = Team.objects.count()
    total_departments = Department.objects.count()

    # Get teams with no manager assigned
    teams_without_manager = Team.objects.filter(
        manager__isnull=True
    ).select_related('department')

    # Get active and disabled team counts
    active_teams = Team.objects.filter(status='active').count()
    disabled_teams = Team.objects.filter(status='disabled').count()

    # Get department summary with team counts
    dept_summary = Department.objects.annotate(
        team_count=Count('teams')
    ).select_related('organisation')

    context = {
        'total_teams': total_teams,
        'total_departments': total_departments,
        'teams_without_manager': teams_without_manager,
        'active_teams': active_teams,
        'disabled_teams': disabled_teams,
        'dept_summary': dept_summary,
    }
    return render(request, 'reports/reports_dashboard.html', context)


@login_required
def generate_pdf(request):
    """Generate a PDF file from a string of HTML."""
    # Render the HTML template with all the data we want in the report
    html = render_to_string('reports/report.html', {
        # Get all teams with their related department, organisation and manager
        # select_related performs a SQL JOIN to avoid extra queries
        'teams': Team.objects.select_related(
            'department',
            'department__organisation',
            'manager'
        ).prefetch_related('members'),  # prefetch_related used for ManyToMany fields

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
    pdf = htmldoc.write_pdf(
        stylesheets=[
            CSS(os.path.join(settings.BASE_DIR, 'teams', 'static', 'teams', 'style.css'))
        ]
    )

    # Write the PDF bytes to an in-memory buffer
    buffer = io.BytesIO(pdf)

    # Return the buffer as a downloadable PDF file attachment
    return FileResponse(buffer, as_attachment=True, filename='sky_teams_report.pdf')