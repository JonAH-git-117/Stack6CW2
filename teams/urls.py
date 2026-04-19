from django.urls import path
from . import views
from . import views

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('dashboard/', views.dashboard, name='dashboard'),  # 👈 ADD THIS
    path('team/<int:id>/', views.team_detail, name='team_detail'),
    path('schedule-meeting/', views.schedule_meeting, name='schedule_meeting'),
]
