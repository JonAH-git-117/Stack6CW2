from django.shortcuts import render, get_object_or_404
from .models import Team


def team_list(request):

    keyword = request.GET.get('keyword')

    teams = Team.objects.all()

    if keyword:
        teams = teams.filter(name__icontains=keyword)

    context = {
        'teams': teams
    }

    return render(request, 'teams/team_list.html', context)


def team_detail(request, id):

    team = get_object_or_404(Team, id=id)

    context = {
        'team': team
    }

    return render(request, 'teams/team_detail.html', context)


def schedule_meeting(request):
    return render(request, 'teams/schedule_meeting.html')


