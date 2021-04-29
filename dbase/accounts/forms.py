from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms

class RegisterForm(UserCreationForm):
	class Meta:
		model = get_user_model()
		fields = ('email', 'username', 'password1', 'password2')

# class LoginForm(AuthenticationForm):
# 	username = forms.CharField(label='Email / Username')		#subclassed AuthenticationForm only to explicitly mention to the user that any of email or username can be used to login