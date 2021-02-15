from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.views import generic
from django.urls import reverse_lazy, reverse
from .forms import LoginForm, RegisterForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
# Create your views here.
class LoginView(auth_views.LoginView):
	form_class = LoginForm
	template_name = 'accounts/login.html'

	def get_success_url(self):
		if self.request.user.is_superuser:
			return '/admin_section'
		return '/'

	def get_context_data(self, **kwargs):
		# print("*********************** kwargs: {}".format(**kwargs))
		context = super(LoginView, self).get_context_data(**kwargs)
		context['success'] = "msg here"
		return context

class RegisterView(generic.CreateView):
	form_class = RegisterForm
	template_name = 'accounts/register.html'
	
	def get_success_url(self):
		messages.add_message(self.request, messages.INFO, 'Successfully Registered !')
		return reverse('login')