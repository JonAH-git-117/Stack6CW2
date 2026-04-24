from django.contrib import admin
from django.urls import path, include
from teams.views import team_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', team_list, name='home'),
    path('teams/', include('teams.urls')),

    # Student 3 - Messages
    path('messages/', include('django_messages_practice.messages_app.urls')),

    # Student 5 - Reports
    path('reports/', include('reports.urls')),

    # Student 6 - Visualisation
    path('visualisation/', include('visualisation.urls')),

    path('accounts/', include('accounts.urls')),
]