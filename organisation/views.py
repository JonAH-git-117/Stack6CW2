from django.shortcuts import render, get_object_or_404
from teams.models import Organisation, Department


def organisation_list(request):

    organisations = Organisation.objects.all()

    context = {
        'organisations': organisations,
    }

    return render(request, 'organisation/organisation_list.html', context)


def organisation_detail(request, id):

    organisation = get_object_or_404(Organisation, id=id)

    departments = Department.objects.filter(organisation=organisation)

    context = {
        'organisation': organisation,
        'departments': departments,
    }

    return render(request, 'organisation/organisation_detail.html', context)



def department_detail(request,id):

    department = get_object_or_404(Department, id=id)

    teams = department.teams.all()

    context = {
        'department' : department,
        'teams' : teams,
    }

    return render (request, 'teams/department_detail.html', context)