from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Team, Department
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def team_list(request):

    keyword = request.GET.get('keyword') or ""
    department = request.GET.get('department')
    manager = request.GET.get('manager')
    status = request.GET.get('status')

    teams = Team.objects.all()

    if keyword:
        teams = teams.filter(name__icontains=keyword)

    if department:
        teams = teams.filter(department__department_name=department)

    if manager:
        teams = teams.filter(manager__username=manager)

    if status:
        teams = teams.filter(status__iexact=status)

    User = get_user_model()
    departments = Department.objects.all()
    managers = User.objects.all()

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

    context = {
        'team': team,
        'upstream': upstream,
        'downstream': downstream,
        'skills': skills,
        'teams': Team.objects.all(),

       
        'member_count': member_count,
    }

    return render(request, 'teams/team_detail.html', context)


@login_required
def schedule_meeting(request):
        return render(request, 'teams/schedule_meeting.html')