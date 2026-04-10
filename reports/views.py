import io
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse
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


@login_required
def generate_excel(request):
    """Generate and return an Excel report of all teams and departments."""

    # Create a new Excel workbook to hold our report data
    workbook = openpyxl.Workbook()

    # ── Sheet 1: All Teams ──────────────────────────────────────────────
    # The active sheet is created automatically — rename it
    sheet1 = workbook.active
    sheet1.title = 'All Teams'

    # Define header style — dark blue background, white bold text
    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill('solid', fgColor='1e3a8a')
    center = Alignment(horizontal='center')

    # Write the column headers for the teams sheet
    headers = ['Team Name', 'Department', 'Organisation', 'Manager', 'Status', 'Members']
    for col, header in enumerate(headers, 1):
        cell = sheet1.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center

    # Query all teams with related fields using select_related to avoid
    # extra database hits (one query instead of many)
    teams = Team.objects.select_related(
        'department',
        'department__organisation',
        'manager'
    ).prefetch_related('members')  # prefetch_related handles ManyToMany fields

    # Write one row per team into the spreadsheet
    for row, team in enumerate(teams, 2):
        # Get manager's full name or fall back to username, or 'No Manager'
        if team.manager:
            manager_name = team.manager.get_full_name() or team.manager.username
        else:
            manager_name = 'No Manager'

        sheet1.cell(row=row, column=1, value=team.name)
        sheet1.cell(row=row, column=2, value=team.department.department_name)
        sheet1.cell(row=row, column=3, value=team.department.organisation.organisation_name)
        sheet1.cell(row=row, column=4, value=manager_name)
        sheet1.cell(row=row, column=5, value=team.get_status_display())
        sheet1.cell(row=row, column=6, value=team.members.count())

    # Auto-size columns so content is not cut off
    for col in sheet1.columns:
        sheet1.column_dimensions[col[0].column_letter].width = 22

    # ── Sheet 2: Department Summary ─────────────────────────────────────
    sheet2 = workbook.create_sheet(title='Department Summary')

    # Write headers for department summary sheet
    dept_headers = ['Department', 'Organisation', 'Team Count', 'Dept Head']
    for col, header in enumerate(dept_headers, 1):
        cell = sheet2.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center

    # Annotate each department with a count of its teams
    departments = Department.objects.annotate(
        team_count=Count('teams')
    ).select_related('organisation', 'dept_head')

    # Write one row per department
    for row, dept in enumerate(departments, 2):
        if dept.dept_head:
            head_name = dept.dept_head.get_full_name() or dept.dept_head.username
        else:
            head_name = 'Not Assigned'

        sheet2.cell(row=row, column=1, value=dept.department_name)
        sheet2.cell(row=row, column=2, value=dept.organisation.organisation_name)
        sheet2.cell(row=row, column=3, value=dept.team_count)
        sheet2.cell(row=row, column=4, value=head_name)

    for col in sheet2.columns:
        sheet2.column_dimensions[col[0].column_letter].width = 22

    # ── Sheet 3: Teams Without a Manager ────────────────────────────────
    sheet3 = workbook.create_sheet(title='No Manager')

    # Write headers for the no manager sheet
    no_mgr_headers = ['Team Name', 'Department', 'Status']
    for col, header in enumerate(no_mgr_headers, 1):
        cell = sheet3.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = PatternFill('solid', fgColor='cc0000')  # Red header for warning
        cell.alignment = center

    # Filter to only teams where the manager field is empty
    teams_no_manager = Team.objects.filter(
        manager__isnull=True
    ).select_related('department')

    # Write one row per team without a manager
    for row, team in enumerate(teams_no_manager, 2):
        sheet3.cell(row=row, column=1, value=team.name)
        sheet3.cell(row=row, column=2, value=team.department.department_name)
        sheet3.cell(row=row, column=3, value=team.get_status_display())

    for col in sheet3.columns:
        sheet3.column_dimensions[col[0].column_letter].width = 22

    # Set the correct content type for .xlsx files
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    # Tell the browser to download the file with this filename
    response['Content-Disposition'] = 'attachment; filename="sky_teams_report.xlsx"'

    # Write the workbook directly to the HTTP response
    workbook.save(response)
    return response