# Import render and redirect shortcuts
from django.shortcuts import render, redirect
# Import authentication functions - aliased to avoid naming conflicts
# with our own login/logout view functions
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
# Import the built-in login form
from django.contrib.auth.forms import AuthenticationForm
# Import decorator to restrict views to logged-in users only
from django.contrib.auth.decorators import login_required
# Import messages framework for displaying alerts to the user
from django.contrib import messages
# Import our custom signup form from forms.py
from .forms import CustomUserCreationForm


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


def login(request):
    # Initialise an empty authentication form for GET requests
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