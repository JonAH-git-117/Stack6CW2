# Standard library imports for file handling and OS path operations
import io
import os

# openpyxl is a Python library for creating and editing Excel (.xlsx) files
# It allows us to create workbooks, sheets, and style cells
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

# Django imports — following the same patterns shown in the lectures
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import FileResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

# WeasyPrint converts HTML strings into PDF documents
# HTML handles the conversion, CSS allows us to pass stylesheets to the PDF
from weasyprint import HTML, CSS

# Import models from the teams app — reports has no models of its own
# as it only reads and displays existing data from the shared database
from teams.models import Department, Organisation, Team


@login_required  # Restricts access to logged-in users only — as shown in lecture 7
def reports_dashboard(request):
    """
    Display the reports dashboard page showing summary statistics,
    department breakdown and teams without a manager.
    Uses Django's QuerySet API to retrieve data.
    """

    # Count total number of teams and departments in the database
    # .count() is a QuerySet method that returns an integer — no loop needed
    total_teams = Team.objects.count()
    total_departments = Department.objects.count()

    # Filter teams where the manager field is NULL (no manager assigned)
    # select_related('department') performs a SQL JOIN to get department
    # data in the same query — avoids extra database hits
    teams_without_manager = Team.objects.filter(
        manager__isnull=True
    ).select_related('department')

    # Filter teams by their status field using the STATUS_CHOICES
    # defined in the Team model — returns a count integer
    active_teams = Team.objects.filter(status='active').count()
    disabled_teams = Team.objects.filter(status='disabled').count()

    # annotate() adds a calculated team_count field to each department
    # Count('teams') uses the related_name='teams' defined in the Team model
    # select_related('organisation') fetches organisation data in one query
    dept_summary = Department.objects.annotate(
        team_count=Count('teams')
    ).select_related('organisation')

    # Build the context dictionary to pass data to the template
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
    """
    Generate a PDF report of all teams and return it as a downloadable file.
    Uses WeasyPrint to convert an HTML template into a PDF document.
    """

    # render_to_string() renders a Django template to a string of HTML
    # rather than returning an HTTP response — this gives us the HTML
    # as a Python string that we can pass to WeasyPrint
    html = render_to_string('reports/report.html', {

        # Get all teams with related fields pre-fetched to avoid extra queries
        # select_related performs SQL JOINs for ForeignKey relationships
        # prefetch_related handles ManyToMany relationships (team members)
        'teams': Team.objects.select_related(
            'department',
            'department__organisation',
            'manager'
        ).prefetch_related('members'),

        # Annotate departments with a count of their teams
        # select_related fetches the linked organisation in the same query
        'departments': Department.objects.annotate(
            team_count=Count('teams')
        ).select_related('organisation'),

        # Filter for teams with no manager — isnull=True checks for NULL
        'teams_without_manager': Team.objects.filter(
            manager__isnull=True
        ).select_related('department'),

        # Simple count values for the report summary header
        'total_teams': Team.objects.count(),
        'total_departments': Department.objects.count(),
    })

    # Pass the HTML string to WeasyPrint's HTML class
    # base_url="" ensures any relative file paths are resolved correctly
    htmldoc = HTML(string=html, base_url="")

    # write_pdf() converts the HTML to PDF bytes
    # We pass the project's existing stylesheet so the PDF styling
    # matches the rest of the site
    pdf = htmldoc.write_pdf(
        stylesheets=[
            CSS(os.path.join(settings.BASE_DIR, 'teams', 'static', 'teams', 'style.css'))
        ]
    )

    # Write the raw PDF bytes into an in-memory buffer
    # io.BytesIO() creates a file-like object in memory — no disk writes needed
    buffer = io.BytesIO(pdf)

    # Return the buffer as a FileResponse with as_attachment=True
    # This tells the browser to download the file rather than display it
    return FileResponse(buffer, as_attachment=True, filename='sky_teams_report.pdf')


@login_required
def generate_excel(request):
    """
    Generate an Excel (.xlsx) report of all teams and departments
    and return it as a downloadable file.
    Uses openpyxl to create a workbook with three sheets:
    1. All Teams — full team listing
    2. Department Summary — team counts per department
    3. No Manager — teams without a manager assigned
    """

    # Create a new blank Excel workbook
    # A workbook is the top-level container — it holds one or more sheets
    workbook = openpyxl.Workbook()

    # Sheet 1: All Teams
    # workbook.active returns the default first sheet created automatically
    sheet1 = workbook.active
    sheet1.title = 'All Teams'

    # Define reusable header styles for all sheets
    # Font — bold white text for contrast against the dark header background
    header_font = Font(bold=True, color='FFFFFF')
    # PatternFill — solid dark blue background matching the site's colour scheme
    header_fill = PatternFill('solid', fgColor='1e3a8a')
    # Alignment — centre the header text horizontally in each cell
    center = Alignment(horizontal='center')

    # Write column headers for Sheet 1
    headers = ['Team Name', 'Department', 'Organisation', 'Manager', 'Status', 'Members']
    for col, header in enumerate(headers, 1):
        cell = sheet1.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center

    # Retrieve all teams with related data in a single optimised query
    # select_related handles ForeignKey fields (department, organisation, manager)
    # prefetch_related handles ManyToMany fields (members)
    teams = Team.objects.select_related(
        'department',
        'department__organisation',
        'manager'
    ).prefetch_related('members')

    # Write one data row per team starting from row 2 (row 1 is headers)
    for row, team in enumerate(teams, 2):
        # get_full_name() returns "First Last" — fall back to username if empty
        manager_name = (
            team.manager.get_full_name() or team.manager.username
            if team.manager else 'No Manager'
        )

        # Write each field into the correct column for this row
        sheet1.cell(row=row, column=1, value=team.name)
        sheet1.cell(row=row, column=2, value=team.department.department_name)
        sheet1.cell(row=row, column=3, value=team.department.organisation.organisation_name)
        sheet1.cell(row=row, column=4, value=manager_name)
        # get_status_display() returns the human-readable label e.g. "Active"
        sheet1.cell(row=row, column=5, value=team.get_status_display())
        # .count() on a ManyToMany field returns the number of related objects
        sheet1.cell(row=row, column=6, value=team.members.count())

    # Auto-size all columns so content is not cut off in Excel
    for col in sheet1.columns:
        sheet1.column_dimensions[col[0].column_letter].width = 22

    # Sheet 2: Department Summary
    # create_sheet() adds a new sheet to the workbook
    sheet2 = workbook.create_sheet(title='Department Summary')

    dept_headers = ['Department', 'Organisation', 'Team Count', 'Dept Head']
    for col, header in enumerate(dept_headers, 1):
        cell = sheet2.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center

    # annotate() adds a team_count field to each department queryset object
    # select_related fetches organisation and dept_head in the same query
    departments = Department.objects.annotate(
        team_count=Count('teams')
    ).select_related('organisation', 'dept_head')

    for row, dept in enumerate(departments, 2):
        # dept_head is a ForeignKey to the User model — may be null
        head_name = (
            dept.dept_head.get_full_name() or dept.dept_head.username
            if dept.dept_head else 'Not Assigned'
        )

        sheet2.cell(row=row, column=1, value=dept.department_name)
        sheet2.cell(row=row, column=2, value=dept.organisation.organisation_name)
        sheet2.cell(row=row, column=3, value=dept.team_count)
        sheet2.cell(row=row, column=4, value=head_name)

    for col in sheet2.columns:
        sheet2.column_dimensions[col[0].column_letter].width = 22

    # Sheet 3: Teams Without a Manager
    sheet3 = workbook.create_sheet(title='No Manager')

    no_mgr_headers = ['Team Name', 'Department', 'Status']
    for col, header in enumerate(no_mgr_headers, 1):
        cell = sheet3.cell(row=1, column=col, value=header)
        cell.font = header_font
        # Red header fill to visually flag this as a warning sheet
        cell.fill = PatternFill('solid', fgColor='cc0000')
        cell.alignment = center

    # Filter to only teams where manager is NULL in the database
    teams_no_manager = Team.objects.filter(
        manager__isnull=True
    ).select_related('department')

    for row, team in enumerate(teams_no_manager, 2):
        sheet3.cell(row=row, column=1, value=team.name)
        sheet3.cell(row=row, column=2, value=team.department.department_name)
        sheet3.cell(row=row, column=3, value=team.get_status_display())

    for col in sheet3.columns:
        sheet3.column_dimensions[col[0].column_letter].width = 22

    # Return the workbook as a downloadable HTTP response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    # Content-Disposition tells the browser to download rather than display
    response['Content-Disposition'] = 'attachment; filename="sky_teams_report.xlsx"'

    # Write the workbook directly into the HTTP response object
    workbook.save(response)
    return response