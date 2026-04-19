


from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.http import HttpResponse

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

from teams.models import Department, Team


@login_required
def reports_dashboard(request):

    total_teams = Team.objects.count()
    total_departments = Department.objects.count()

    teams_without_manager = Team.objects.filter(
        manager__isnull=True
    ).select_related('department')

    active_teams = Team.objects.filter(status='active').count()
    disabled_teams = Team.objects.filter(status='disabled').count()

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
def generate_excel(request):

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Teams"

    header_font = Font(bold=True)
    headers = ["Team", "Department", "Status"]

    for col, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col, value=header)
        cell.font = header_font

    teams = Team.objects.select_related('department')

    for row, team in enumerate(teams, 2):
        sheet.cell(row=row, column=1, value=team.name)
        sheet.cell(row=row, column=2, value=team.department.department_name)
        sheet.cell(row=row, column=3, value=team.get_status_display())

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="report.xlsx"'

    workbook.save(response)
    return response