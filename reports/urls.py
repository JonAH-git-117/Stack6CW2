# Import path function for defining URL patterns
from django.urls import path

# Import views from the current app using relative import
from . import views

# URL patterns for the reports app
urlpatterns = [
    # These are included in config/urls.py under the 'reports/' prefix
    # So the full URLs are:

    # Reports dashboard — shows summary stats and download buttons
    path('', views.reports_dashboard, name='reports_dashboard'), # /reports/ — dashboard

    # Generates and downloads a PDF report using WeasyPrint
    path('pdf/', views.generate_pdf, name='generate_pdf'), # /reports/pdf/ — PDF download

    # Generates and downloads an Excel report using openpyxl
    path('excel/', views.generate_excel, name='generate_excel'), # /reports/excel/ — Excel download
]