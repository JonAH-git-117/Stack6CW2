# Import path function for defining URL patterns
from django.urls import path
# Import views from the accounts app
from . import views

urlpatterns = [
    # URL path for the signup page
    path('signup/', views.signup, name='signup'),
    # URL path for the login page
    path('login/', views.login, name='login'),
    # URL path for logout - no template needed, just redirects
    path('logout/', views.logout, name='logout'),
]