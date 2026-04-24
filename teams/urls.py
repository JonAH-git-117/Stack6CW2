from django.urls import path
from . import views

urlpatterns = [
    # Teams directory page — displays all teams with search and filter
    path('', views.team_list, name='team_list'),
    # Individual team detail page — displays full info for a specific team
    path('team/<int:id>/', views.team_detail, name='team_detail'),
    # Schedule meeting page — allows users to schedule a meeting
    path('schedule-meeting/', views.schedule_meeting, name='schedule_meeting'),
    # Dashboard page — displays the main dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    # Admin — Team Management page (staff only)
    path('admin/team-management/', views.team_management, name='team_management'),
    # Admin — User Access Management page (staff only)
    path('admin/user-access/', views.user_access_management, name='user_access_management'),
    path('delete-meeting/<int:meeting_id>/', views.delete_meeting, name='delete_meeting'),
]