# Standard Django imports for rendering templates, retrieving objects and redirecting
from django.shortcuts import render, get_object_or_404, redirect

# get_user_model returns the active User model as defined in settings.py
from django.contrib.auth import get_user_model

# Import the built-in Django User model directly for use in admin views
from django.contrib.auth.models import User

# Decorators to restrict access
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

# Messages framework for displaying success/error alerts
from django.contrib import messages

# Q objects allow complex database queries using OR conditions
from django.db.models import Count, Prefetch, Q

# timezone is used for upcoming meetings
from django.utils import timezone

# JSON handling for calendar data
import json
from django.core.serializers.json import DjangoJSONEncoder

# Import models from the teams app
from .models import Team, TeamType, Organisation, Department, Dependency, AuditLog, Meeting


@login_required
def dashboard(request):
    upcoming_meetings = Meeting.objects.filter(
        scheduled_at__gte=timezone.now()
    ).order_by('scheduled_at')[:5]

    context = {
        'upcoming_meetings': upcoming_meetings,
    }

    return render(request, 'teams/dashboard.html', context)


@login_required
def team_list(request):
    keyword = request.GET.get('keyword') or ""
    department = request.GET.get('department')
    manager = request.GET.get('manager')
    status = request.GET.get('status')

    teams = Team.objects.select_related('department', 'manager').prefetch_related('members')

    if keyword:
        teams = teams.filter(
            Q(name__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(department__department_name__icontains=keyword) |
            Q(manager__username__icontains=keyword) |
            Q(manager__first_name__icontains=keyword) |
            Q(manager__last_name__icontains=keyword)
        )

    if department:
        teams = teams.filter(department__department_name=department)

    if manager:
        teams = teams.filter(manager__username=manager)

    if status:
        teams = teams.filter(status__iexact=status)

    UserModel = get_user_model()

    departments = Department.objects.all()
    managers = UserModel.objects.filter(managed_teams__isnull=False).distinct()

    context = {
        'teams': teams,
        'keyword': keyword,
        'selected_department': department,
        'selected_manager': manager,
        'selected_status': status,
        'departments': departments,
        'managers': managers,
    }

    return render(request, 'teams/team_list.html', context)


@login_required
def team_detail(request, id):
    team = get_object_or_404(Team, id=id)
    member_count = team.members.count()

    context = {
        'team': team,
        'teams': Team.objects.all(),
        'member_count': member_count,
    }

    return render(request, 'teams/team_detail.html', context)


@login_required
def organisation_page(request):
    query = request.GET.get('q', '').strip()
    department_filter = request.GET.get('department', '')
    team_type_filter = request.GET.get('team_type', '')
    direction_filter = request.GET.get('direction', '')

    teams = Team.objects.select_related(
        'department',
        'department__organisation',
        'manager',
        'team_type',
    )

    if query:
        teams = teams.filter(
            Q(name__icontains=query) |
            Q(department__department_name__icontains=query) |
            Q(manager__username__icontains=query) |
            Q(manager__first_name__icontains=query) |
            Q(manager__last_name__icontains=query) |
            Q(dependencies__depends_on__name__icontains=query) |
            Q(dependent_teams__team__name__icontains=query)
        )

    if department_filter:
        teams = teams.filter(department_id=department_filter)

    if team_type_filter:
        teams = teams.filter(team_type_id=team_type_filter)

    if direction_filter == 'upstream':
        teams = teams.filter(dependencies__isnull=False)
    elif direction_filter == 'downstream':
        teams = teams.filter(dependent_teams__isnull=False)

    teams = teams.distinct().annotate(
        upstream_count=Count('dependencies', distinct=True),
        downstream_count=Count('dependent_teams', distinct=True),
    ).order_by('name')

    departments = Department.objects.select_related(
        'organisation',
        'dept_head',
    ).annotate(
        team_count=Count('teams', distinct=True)
    ).prefetch_related(
        Prefetch('teams', queryset=teams, to_attr='filtered_teams')
    ).order_by('department_name')

    if department_filter:
        departments = departments.filter(id=department_filter)

    if query:
        departments = departments.filter(
            Q(id__in=teams.values('department_id')) |
            Q(department_name__icontains=query) |
            Q(department_description__icontains=query) |
            Q(dept_head__username__icontains=query) |
            Q(dept_head__first_name__icontains=query) |
            Q(dept_head__last_name__icontains=query)
        ).distinct()
    elif team_type_filter or direction_filter:
        departments = departments.filter(id__in=teams.values('department_id')).distinct()

    organisations = Organisation.objects.prefetch_related(
        Prefetch('departments', queryset=departments, to_attr='filtered_departments')
    ).order_by('organisation_name')

    if query or department_filter or team_type_filter or direction_filter:
        organisations = organisations.filter(
            id__in=departments.values('organisation_id')
        ).distinct()

    team_types = TeamType.objects.prefetch_related(
        Prefetch('teams', queryset=teams, to_attr='filtered_teams')
    ).annotate(
        team_count=Count('teams', distinct=True)
    ).order_by('name')

    if team_type_filter:
        team_types = team_types.filter(id=team_type_filter)
    elif query or department_filter or direction_filter:
        team_types = team_types.filter(id__in=teams.values('team_type_id')).distinct()

    unassigned_teams = teams.filter(team_type__isnull=True)

    dependencies = Dependency.objects.select_related(
        'team',
        'team__department',
        'team__team_type',
        'depends_on',
        'depends_on__department',
        'depends_on__team_type',
    )

    if query:
        dependencies = dependencies.filter(
            Q(team__name__icontains=query) |
            Q(depends_on__name__icontains=query) |
            Q(team__department__department_name__icontains=query) |
            Q(depends_on__department__department_name__icontains=query) |
            Q(team__manager__username__icontains=query) |
            Q(depends_on__manager__username__icontains=query)
        )

    if department_filter:
        dependencies = dependencies.filter(
            Q(team__department_id=department_filter) |
            Q(depends_on__department_id=department_filter)
        )

    if team_type_filter:
        dependencies = dependencies.filter(
            Q(team__team_type_id=team_type_filter) |
            Q(depends_on__team_type_id=team_type_filter)
        )

    if direction_filter == 'upstream':
        dependencies = dependencies.filter(team__in=teams)
    elif direction_filter == 'downstream':
        dependencies = dependencies.filter(depends_on__in=teams)

    dependencies = dependencies.distinct().order_by('team__name', 'depends_on__name')

    context = {
        'organisations': organisations,
        'departments': departments,
        'teams': teams,
        'team_types': team_types,
        'unassigned_teams': unassigned_teams,
        'dependencies': dependencies,
        'departments_for_filter': Department.objects.order_by('department_name'),
        'team_types_for_filter': TeamType.objects.order_by('name'),
        'query': query,
        'selected_department': department_filter,
        'selected_team_type': team_type_filter,
        'selected_direction': direction_filter,
        'organisation_count': Organisation.objects.count(),
        'department_count': Department.objects.count(),
        'team_count': Team.objects.count(),
        'team_type_count': TeamType.objects.count(),
        'dependency_count': Dependency.objects.count(),
    }

    return render(request, 'teams/organisation.html', context)


@login_required
def schedule_meeting(request):
    UserModel = get_user_model()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        date = request.POST.get('date')
        time = request.POST.get('time')
        platform = request.POST.get('platform')
        team_id = request.POST.get('team')
        attendee_ids = request.POST.getlist('attendees')
        agenda = request.POST.get('agenda', '')

        from django.utils.dateparse import parse_datetime
        scheduled_at = parse_datetime(f"{date}T{time}")
        if scheduled_at is None:
            messages.error(request, "Please provide a valid meeting date and time.")
            return redirect('schedule_meeting')
        if timezone.is_naive(scheduled_at):
            scheduled_at = timezone.make_aware(scheduled_at)

        team = get_object_or_404(Team, id=team_id) if team_id else None

        meeting = Meeting.objects.create(
            title=title,
            organiser=request.user,
            platform=platform,
            scheduled_at=scheduled_at,
            message=agenda,
            team=team,
        )

        if attendee_ids:
            meeting.attendees.set(attendee_ids)

        messages.success(request, f"Meeting '{title}' scheduled successfully.")
        return redirect('schedule_meeting')

    db_meetings = Meeting.objects.all().values('id', 'title', 'scheduled_at')

    meetings_json = json.dumps([
        {
            'id': m['id'],
            'title': m['title'],
            'day': m['scheduled_at'].day,
            'month': m['scheduled_at'].month - 1,
            'year': m['scheduled_at'].year,
        }
        for m in db_meetings
    ], cls=DjangoJSONEncoder)

    teams_with_members = {}

    for team in Team.objects.prefetch_related('members').all():
        teams_with_members[str(team.id)] = [
            {
                'id': member.id,
                'name': member.get_full_name() or member.username,
                'email': member.email or '',
            }
            for member in team.members.all()
        ]

    team_members_json = json.dumps(teams_with_members, cls=DjangoJSONEncoder)

    all_users = UserModel.objects.filter(is_active=True)

    all_users_json = json.dumps([
        {
            'id': user.id,
            'name': user.get_full_name() or user.username,
            'email': user.email or '',
        }
        for user in all_users
    ], cls=DjangoJSONEncoder)

    upcoming_meetings = Meeting.objects.filter(
        scheduled_at__gte=timezone.now()
    ).select_related('team', 'organiser').order_by('scheduled_at')[:10]

    context = {
        'users': all_users,
        'teams': Team.objects.all(),
        'platforms': Meeting.PLATFORM_CHOICES,
        'meetings_json': meetings_json,
        'team_members_json': team_members_json,
        'all_users_json': all_users_json,
        'upcoming_meetings': upcoming_meetings,
    }

    return render(request, 'teams/schedule_meeting.html', context)


@login_required
def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    meeting.delete()
    messages.success(request, "Meeting cancelled successfully.")
    return redirect('schedule_meeting')


@staff_member_required
def team_management(request):
    query = request.GET.get('q', '')
    department_filter = request.GET.get('department', '')
    status_filter = request.GET.get('status', '')

    teams = Team.objects.select_related('department', 'manager').all()

    if query:
        teams = teams.filter(
            Q(name__icontains=query) |
            Q(manager__first_name__icontains=query) |
            Q(manager__last_name__icontains=query) |
            Q(department__department_name__icontains=query)
        )

    if department_filter:
        teams = teams.filter(department__id=department_filter)

    if status_filter:
        teams = teams.filter(status=status_filter)

    selected_team = None
    selected_team_id = request.GET.get('selected_team')

    if selected_team_id:
        selected_team = get_object_or_404(Team, id=selected_team_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save':
            team_id = request.POST.get('team_id')
            name = request.POST.get('name', '').strip()
            dept_id = request.POST.get('department', '')
            status = request.POST.get('status', 'active')
            manager_id = request.POST.get('manager', '')
            description = request.POST.get('description', '')

            if team_id:
                team = get_object_or_404(Team, id=team_id)
                old_name = team.name

                team.name = name
                team.status = status
                team.description = description

                if dept_id:
                    team.department = get_object_or_404(Department, id=dept_id)

                team.manager = get_object_or_404(User, id=manager_id) if manager_id else None
                team.save()

                AuditLog.objects.create(
                    user=request.user,
                    action='update',
                    model_name='Team',
                    object_id=team.id,
                    details=f"Updated team: {old_name} → {name}"
                )

                messages.success(request, f"Team '{name}' updated successfully.")

            else:
                dept = get_object_or_404(Department, id=dept_id) if dept_id else None
                manager = get_object_or_404(User, id=manager_id) if manager_id else None

                team = Team.objects.create(
                    name=name,
                    status=status,
                    description=description,
                    department=dept,
                    manager=manager,
                )

                AuditLog.objects.create(
                    user=request.user,
                    action='create',
                    model_name='Team',
                    object_id=team.id,
                    details=f"Created new team: {name}"
                )

                messages.success(request, f"Team '{name}' created successfully.")

            return redirect('team_management')

        elif action == 'delete':
            team_id = request.POST.get('team_id')
            team = get_object_or_404(Team, id=team_id)
            team_name = team.name
            team_id_value = team.id

            team.delete()

            AuditLog.objects.create(
                user=request.user,
                action='delete',
                model_name='Team',
                object_id=team_id_value,
                details=f"Deleted team: {team_name}"
            )

            messages.success(request, f"Team '{team_name}' deleted.")
            return redirect('team_management')

    departments = Department.objects.all()
    managers = User.objects.filter(is_active=True)
    audit_entries = AuditLog.objects.order_by('-timestamp')[:10]

    context = {
        'teams': teams,
        'departments': departments,
        'managers': managers,
        'selected_team': selected_team,
        'audit_entries': audit_entries,
        'query': query,
        'department_filter': department_filter,
        'status_filter': status_filter,
    }

    return render(request, 'teams/team_management.html', context)


@staff_member_required
def user_access_management(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.all()

    if query:
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'disabled':
        users = users.filter(is_active=False)

    selected_user = None
    selected_user_id = request.GET.get('selected_user')

    if selected_user_id:
        selected_user = get_object_or_404(User, id=selected_user_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        target_user = get_object_or_404(User, id=user_id)

        if action == 'activate':
            target_user.is_active = True
            target_user.save()

            AuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='User',
                object_id=target_user.id,
                details=f"Activated user: {target_user.username}"
            )

            messages.success(request, f"User '{target_user.username}' activated.")

        elif action == 'disable':
            if target_user == request.user:
                messages.error(request, "You cannot disable your own account.")
            else:
                target_user.is_active = False
                target_user.save()

                AuditLog.objects.create(
                    user=request.user,
                    action='update',
                    model_name='User',
                    object_id=target_user.id,
                    details=f"Disabled user: {target_user.username}"
                )

                messages.success(request, f"User '{target_user.username}' disabled.")

        elif action == 'grant_admin':
            target_user.is_staff = True
            target_user.save()

            AuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='User',
                object_id=target_user.id,
                details=f"Granted admin rights to: {target_user.username}"
            )

            messages.success(request, f"Admin rights granted to '{target_user.username}'.")

        elif action == 'revoke_admin':
            if target_user == request.user:
                messages.error(request, "You cannot revoke your own admin rights.")
            else:
                target_user.is_staff = False
                target_user.save()

                AuditLog.objects.create(
                    user=request.user,
                    action='update',
                    model_name='User',
                    object_id=target_user.id,
                    details=f"Revoked admin rights from: {target_user.username}"
                )

                messages.success(request, f"Admin rights revoked from '{target_user.username}'.")

        elif action == 'reset_password':
            from django.contrib.auth.forms import PasswordResetForm

            form = PasswordResetForm({'email': target_user.email})

            if form.is_valid():
                form.save(
                    request=request,
                    use_https=False,
                    email_template_name='registration/password_reset_email.html'
                )

            AuditLog.objects.create(
                user=request.user,
                action='update',
                model_name='User',
                object_id=target_user.id,
                details=f"Password reset triggered for: {target_user.username}"
            )

            messages.success(request, f"Password reset email sent to '{target_user.email}'.")

        return redirect(f'/teams/admin/user-access/?selected_user={user_id}')

    audit_entries = AuditLog.objects.order_by('-timestamp')[:10]

    context = {
        'users': users,
        'selected_user': selected_user,
        'audit_entries': audit_entries,
        'query': query,
        'status_filter': status_filter,
    }

    return render(request, 'teams/user_access_management.html', context)
