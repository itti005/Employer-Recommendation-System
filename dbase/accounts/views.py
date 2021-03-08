from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.views import generic
from django.urls import reverse_lazy, reverse
from .forms import LoginForm, RegisterForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()
# Create your views here.
class LoginView(auth_views.LoginView):
	form_class = LoginForm
	template_name = 'accounts/login.html'

	def get_success_url(self):
		print("------------------------ {}".format(self.request.user.groups.all()))
		if self.request.user.is_superuser:
			print("********************* It is a superuser")
			return '/employer'
		elif self.request.user.groups.filter(name = "employer").exists():
			print("********************* It is a employer")
			return '/employer'
		elif self.request.user.groups.filter(name = "students").exists():
			print("********************* It is a student")
			return '/students'

	def get_context_data(self, **kwargs):
		context = super(LoginView, self).get_context_data(**kwargs)
		context['success'] = "msg here"
		return context

class RegisterView(generic.CreateView):
	form_class = RegisterForm
	template_name = 'accounts/register.html'
	
	def get_success_url(self):
		messages.add_message(self.request, messages.INFO, 'Successfully Registered !')
		return reverse('login')

	def form_valid(self, form):
		response = super().form_valid(form)
		user = UserModel.objects.get(Q(username__iexact=form.data['username']) | Q(email__iexact=form.data['email']))
		group_type = form.data['group']
		print(" group_type *********************")
		print(group_type)
		print(" group_type *********************")
		g = Group.objects.get(name=group_type)
		print(" g ********************* {}".format(g))
		user.groups.add(g)
		print("************ groups - {}".format(self.request.user.groups.all()))
		user.save()
		print("************ groups - {}".format(self.request.user.groups.all()))
		# g.user_set.add(self.request.user.id)
		return response