from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms

class RegisterForm(UserCreationForm):   #form for employer registration
	class Meta:
		model = get_user_model()
		fields = ('email', 'username', 'password1', 'password2')

