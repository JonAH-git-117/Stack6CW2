# Import the built-in Django User model
from django.contrib.auth.models import User
# Import the built-in Django UserCreationForm
from django.contrib.auth.forms import UserCreationForm
# Import Django forms module
from django import forms

# Extend the default UserCreationForm to include additional fields
# as shown in the Week 7 lecture slides
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # Use the built-in User model
        model = User
        # Add first_name, last_name and email to the default fields
        # (username, password1, password2)
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')