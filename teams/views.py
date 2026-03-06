from django.shortcuts import render
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