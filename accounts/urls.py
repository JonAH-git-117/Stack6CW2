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
    path('login/', views.login_view, name='login'),
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
    # URL path for viewing a user's public profile and yses dynamic username in the URL 
    path('profile/<str:username>/', views.profile_view, name='profile_view'),

    # Password Reset Flow 

    # User enters their email address to request a reset
    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html'
    ), name='password_reset'),
    # Confirmation that the reset email has been sent
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    # User clicks link in email and enters new password
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    # Confirmation that the password has been reset successfully
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]