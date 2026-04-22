# Standard Django imports for rendering templates, retrieving objects and redirecting
from django.shortcuts import render, get_object_or_404, redirect
# get_user_model returns the active User model as defined in settings.py
from django.contrib.auth import get_user_model
# Import the built-in Django User model directly for use in admin views
from django.contrib.auth.models import User
# Decorator to restrict views to logged-in users only
from django.contrib.auth.decorators import login_required
# Decorator to restrict views to staff/admin users only
from django.contrib.admin.views.decorators import staff_member_required
# Messages framework for displaying success/error alerts to the user
from django.contrib import messages
# Q objects allow complex database queries using OR conditions
from django.db.models import Q
# timezone is used to get the current datetime for filtering upcoming meetings
from django.utils import timezone
# Import models from the teams app
from .models import Team, Department, AuditLog, Meeting


# Dashboard view — displays upcoming meetings for the logged-in user
@login_required
def dashboard(request):
    # Filter meetings scheduled from now onwards and order by soonest first
    # scheduled_at__gte means "scheduled at greater than or equal to now"
    upcoming_meetings = Meeting.objects.filter(
        scheduled_at__gte=timezone.now()
    ).order_by('scheduled_at')[:5]

    context = {
        'upcoming_meetings': upcoming_meetings,
    }
    return render(request, 'teams/dashboard.html', context)


# Restrict this view to logged-in users only
# as shown in the django4 lecture slides
@login_required
def team_list(request):
    # Retrieve search/filter parameters from the GET request
    # Uses 'or ""' to default to empty string if parameter is not present
    keyword = request.GET.get('keyword') or ""
    department = request.GET.get('department')
    manager = request.GET.get('manager')
    status = request.GET.get('status')

    # Start with all teams in the database
    teams = Team.objects.all()

    # Filter by keyword if provided — searches team name using case-insensitive match
    if keyword:
        teams = teams.filter(name__icontains=keyword)

    # Filter by department name if selected
    if department:
        teams = teams.filter(department__department_name=department)

    # Filter by manager username if selected
    if manager:
        teams = teams.filter(manager__username=manager)

    # Filter by status if selected — iexact makes it case-insensitive
    if status:
        teams = teams.filter(status__iexact=status)

    # Use get_user_model() to get the active User model as per lecture slides
    User = get_user_model()

    # Retrieve all departments and managers for the filter dropdowns
    departments = Department.objects.all()
    managers = User.objects.all()

    # Pass all data to the template via context dictionary
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


# Restrict this view to logged-in users only
@login_required
def team_detail(request, id):
    # Retrieve the team by ID or return a 404 if not found
    team = get_object_or_404(Team, id=id)

    # Count the number of members in this team using the ManyToManyField
    member_count = team.members.count()

    # Hardcoded upstream dependencies per team name
    # These represent which teams this team depends on
    if team.name == "Backend Engineering":
        upstream = ["Infrastructure", "Authentication"]
        downstream = ["Frontend Engineering", "Mobile Apps"]
    elif team.name == "Frontend Engineering":
        upstream = ["Backend Engineering"]
        downstream = ["UI Users"]
    elif team.name == "Data Engineering":
        upstream = ["Backend Engineering", "External Data"]
        downstream = ["Analytics Platform"]
    elif team.name == "DevOps":
        upstream = ["Backend Engineering", "Infrastructure"]
        downstream = ["All Engineering Teams"]
    elif team.name == "Support Team":
        upstream = ["All Engineering Teams"]
        downstream = ["End Users"]
    elif team.name == "Security Team":
        upstream = ["DevOps", "Backend Engineering"]
        downstream = ["All Engineering Teams"]
    else:
        upstream = []
        downstream = []

    # Hardcoded skills per team name
    # These represent the key skills associated with each team
    if team.name == "Backend Engineering":
        skills = ["Python", "Django", "REST APIs", "Docker"]
    elif team.name == "Frontend Engineering":
        skills = ["HTML", "CSS", "JavaScript", "UI Design"]
    elif team.name == "Data Engineering":
        skills = ["Python", "SQL", "Data Analysis", "Machine Learning"]
    elif team.name == "DevOps":
        skills = ["CI/CD", "Docker", "Kubernetes", "Cloud Infrastructure"]
    elif team.name == "Support Team":
        skills = ["Troubleshooting", "Customer Support", "System Monitoring", "Communication"]
    elif team.name == "Security Team":
        skills = ["Cybersecurity", "Pen Testing", "Risk Analysis", "Encryption"]
    else:
        skills = []

    # Pass team data, dependencies, skills and member count to the template
    context = {
        'team': team,
        'upstream': upstream,
        'downstream': downstream,
        'skills': skills,
        'teams': Team.objects.all(),
        'member_count': member_count,
    }

    return render(request, 'teams/team_detail.html', context)


# Restrict this view to logged-in users only
@login_required
def schedule_meeting(request):
    # Render the schedule meeting template
    return render(request, 'teams/schedule_meeting.html')


# Restrict this view to staff/admin users only
# Uses @staff_member_required instead of @login_required
# as this page should only be accessible to admin users
@staff_member_required
def team_management(request):
    # Retrieve search/filter parameters from the GET request
    query = request.GET.get('q', '')
    department_filter = request.GET.get('department', '')
    status_filter = request.GET.get('status', '')

    # Start with all teams, using select_related to avoid extra DB queries
    teams = Team.objects.select_related('department', 'manager').all()

    # Filter by keyword across team name, manager name and department name
    # Q objects allow combining multiple conditions with OR
    if query:
        teams = teams.filter(
            Q(name__icontains=query) |
            Q(manager__first_name__icontains=query) |
            Q(manager__last_name__icontains=query) |
            Q(department__department_name__icontains=query)
        )

    # Filter by department if selected
    if department_filter:
        teams = teams.filter(department__id=department_filter)

    # Filter by status if selected
    if status_filter:
        teams = teams.filter(status=status_filter)

    # If a team has been selected from the table, retrieve it for the edit form
    selected_team = None
    selected_team_id = request.GET.get('selected_team')
    if selected_team_id:
        selected_team = get_object_or_404(Team, id=selected_team_id)

    # Handle form submissions — save (create/update) or delete
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save':
            # Retrieve form fields from POST data
            team_id = request.POST.get('team_id')
            name = request.POST.get('name', '').strip()
            dept_id = request.POST.get('department', '')
            status = request.POST.get('status', 'active')
            manager_id = request.POST.get('manager', '')
            description = request.POST.get('description', '')

            if team_id:
                # Edit existing team — retrieve by ID and update fields
                team = get_object_or_404(Team, id=team_id)
                old_name = team.name
                team.name = name
                team.status = status
                team.description = description
                if dept_id:
                    team.department = get_object_or_404(Department, id=dept_id)
                # Assign manager if selected, otherwise set to None
                team.manager = get_object_or_404(User, id=manager_id) if manager_id else None
                team.save()
                # Log the update action to the AuditLog model
                AuditLog.objects.create(
                    user=request.user,
                    action='update',
                    model_name='Team',
                    object_id=team.id,
                    details=f"Updated team: {old_name} → {name}"
                )
                messages.success(request, f"Team '{name}' updated successfully.")
            else:
                # Create a new team with the submitted form data
                dept = get_object_or_404(Department, id=dept_id) if dept_id else None
                manager = get_object_or_404(User, id=manager_id) if manager_id else None
                team = Team.objects.create(
                    name=name,
                    status=status,
                    description=description,
                    department=dept,
                    manager=manager,
                )
                # Log the create action to the AuditLog model
                AuditLog.objects.create(
                    user=request.user,
                    action='create',
                    model_name='Team',
                    object_id=team.id,
                    details=f"Created new team: {name}"
                )
                messages.success(request, f"Team '{name}' created successfully.")

            # Redirect back to team management page after saving
            return redirect('team_management')

        elif action == 'delete':
            # Retrieve and delete the selected team
            team_id = request.POST.get('team_id')
            team = get_object_or_404(Team, id=team_id)
            team_name = team.name
            team_id_val = team.id
            team.delete()
            # Log the delete action to the AuditLog model
            AuditLog.objects.create(
                user=request.user,
                action='delete',
                model_name='Team',
                object_id=team_id_val,
                details=f"Deleted team: {team_name}"
            )
            messages.success(request, f"Team '{team_name}' deleted.")

            # Redirect back to team management page after deleting
            return redirect('team_management')

    # Pass all departments and active users for the create/edit form dropdowns
    departments = Department.objects.all()
    managers = User.objects.filter(is_active=True)

    # Retrieve the 10 most recent audit log entries for the audit trail section
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


# Restrict this view to staff/admin users only
@staff_member_required
def user_access_management(request):
    # Retrieve search/filter parameters from the GET request
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    # Start with all users in the database
    users = User.objects.all()

    # Filter by keyword across first name, last name, username and email
    # Q objects allow combining multiple conditions with OR
    if query:
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    # Filter by active or disabled status if selected
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'disabled':
        users = users.filter(is_active=False)

    # If a user has been selected from the table, retrieve them for the detail panel
    selected_user = None
    selected_user_id = request.GET.get('selected_user')
    if selected_user_id:
        selected_user = get_object_or_404(User, id=selected_user_id)

    # Handle POST actions — activate, disable, grant/revoke admin, reset password
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        # Retrieve the target user or return 404 if not found
        target_user = get_object_or_404(User, id=user_id)

        if action == 'activate':
            # Re-enable a disabled user account
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
            # Prevent admin from disabling their own account
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
            # Grant staff/admin privileges to the selected user
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
            # Prevent admin from revoking their own admin rights
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
            # Trigger Django's built-in password reset email to the user
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

        # Redirect back to the same user's detail panel after the action
        return redirect(f'/teams/admin/user-access/?selected_user={user_id}')

    # Retrieve the 10 most recent audit log entries for the account history section
    audit_entries = AuditLog.objects.order_by('-timestamp')[:10]

    context = {
        'users': users,
        'selected_user': selected_user,
        'audit_entries': audit_entries,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'teams/user_access_management.html', context)