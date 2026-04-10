from django.urls import path
from . import views

urlpatterns = [
    # Main visualisation dashboard showing all Bokeh charts
    path('', views.visualisation_dashboard, name='visualisation_dashboard'),
]