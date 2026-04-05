from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('pdf/', views.generate_pdf, name='generate_pdf'),
]