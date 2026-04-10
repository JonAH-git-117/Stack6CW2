# Import path function for defining URL patterns
from django.urls import path
# Import views from the accounts app
from . import views
# Import Django's built-in authentication views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # URL path for the signup page
    path('signup/', views.signup, name='signup'),
    # URL path for the login page
    path('login/', views.login, name='login'),
    # URL path for logout - no template needed, just redirects
    path('logout/', views.logout, name='logout'),
    # URL path for updating the user's profile
    path('update-profile/', views.update_profile, name='update_profile'),
    # URL path for changing password using Django's built-in CBV
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/change_password.html'
    ), name='change_password'),
    # URL path for password change success page
    path('change-password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/change_password_done.html'
    ), name='password_change_done'),
]