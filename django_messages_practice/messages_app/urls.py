from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('new/', views.new_message, name='new_message'),
    path('drafts/', views.drafts, name='drafts'),
    path('sent/', views.sent, name='sent'),
]