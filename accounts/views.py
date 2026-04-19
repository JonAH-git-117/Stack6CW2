

# Import render and redirect shortcuts
from django.shortcuts import render, redirect, get_object_or_404
# Import authentication functions - aliased to avoid naming conflicts
# with our own login/logout view functions
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
# Import the built-in login form
from django.contrib.auth.forms import AuthenticationForm
# Import decorator to restrict views to logged-in users only
from django.contrib.auth.decorators import login_required
# Import messages framework for displaying alerts to the user
from django.contrib import messages
# Import our custom forms from forms.py
from .forms import CustomUserCreationForm, UserUpdateForm
# Import Profile model to retrieve profile data for the view
from .models import Profile

from django.contrib.auth.decorators import login_required


def signup(request):
    # Initialise an empty form for GET requests
    form = CustomUserCreationForm()
    if request.method == 'POST':
        # Populate the form with the submitted POST data
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user to the database
            form.save()
            # Redirect to login page after successful signup
            # as shown in the Week 7 lecture slides
            return redirect('login')
    # Render the signup template with the form
    return render(request, 'accounts/signup.html', {
        'form': form,
    })


def login_view(request):       # Initialise an empty authentication form for GET requests
    form = AuthenticationForm()
    if request.method == 'POST':
        # Populate the form with the submitted POST data
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Attempt to authenticate the user with the provided credentials
            user = authenticate(
                request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user is None:
                # Credentials did not match any user
                messages.error(request, 'Username and password do not match.')
                return render(request, 'accounts/login.html', {'form': form})
            # Log the user in and redirect to the home page
            auth_login(request, user)
            return redirect('home')
        # Form was submitted but was not valid
        messages.error(request, 'Some issues were found with the information you entered.')
    # Render the login template with the form
    return render(request, 'accounts/login.html', {
        'form': form,
    })


# Restrict this view to logged-in users only
@login_required
def logout(request):
    # Log the user out
    auth_logout(request)
    # Redirect to home page after logout
    return redirect('home')


# Restrict this view to logged-in users only
# as shown in the django4 lecture slides
@login_required
def update_profile(request):
    if request.method == 'POST':
        # Populate the form with submitted POST data and the current
        # user instance so we update the existing record, not create a new one
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            # Save the updated user data to the database
            user_form.save()
            # Display a success flash message to the user
            messages.success(request, 'Your profile was successfully updated!')
            # Redirect to home page after successful update
            return redirect('home')
        else:
            # Display an error flash message if the form is invalid
            messages.error(request, 'Please correct the error below.')
    else:
        # GET request - pre-populate the form with the current user's
        # existing data using instance=request.user
        user_form = UserUpdateForm(instance=request.user)
    # Render the update profile template passing the form as context
    return render(request, 'accounts/update_profile.html', {
        'user_form': user_form,
    })

# Profile view page — read only display of user profile (profile_view)
@login_required
def profile_view(request, username):
    # Retrieve the profile using the username from the URL
    # as shown in the lecture slides
    from django.contrib.auth.models import User
    user_obj = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user_obj)
    # Render the profile template passing the profile as context
    return render(request, 'accounts/profile.html', {
        'profile': profile,
    })