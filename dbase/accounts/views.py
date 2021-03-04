from django.shortcuts import render
from django.contrib.auth import views as auth_views
from django.views import generic
from django.urls import reverse_lazy, reverse
from .forms import LoginForm, RegisterForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.models import Group,User
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from events.models import *
from django.contrib.auth import authenticate, login
from emp.models import *
UserModel = get_user_model()
# Create your views here.
class LoginView(auth_views.LoginView):
	form_class = LoginForm
	template_name = 'accounts/login.html'

	def get_success_url(self):
		if self.request.user.is_superuser:
			return '/employer'
		elif self.request.user.groups.filter(name = "employer").exists():
			return '/employer'
		elif self.request.user.groups.filter(name = "students").exists():
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
		if group_type=='students':
			pass
		
		g = Group.objects.get(name=group_type)
		user.groups.add(g)
		user.save()
		return response
def update_msg(request):
	django_messages = []
	for message in messages.get_messages(request):
			django_messages.append({'message':message.message,'tag':message.tags})	
			return django_messages

def validate_student(request):
	email = request.GET.get('email', None)
	if User.objects.filter(email__iexact=email).exists():
		data = {'is_rec_student':True}
		messages.success(request,'Email Id already registered with recommendation system')
		data['messages'] = update_msg(request)
		return JsonResponse(data)

	is_spoken_student = User.objects.using('spk').filter(email__iexact=email).exists()
	data = {'is_spoken_student':is_spoken_student}
	if is_spoken_student:
		user = User.objects.using('spk').filter(email__iexact=email)[0]
		try:
			student = Student.objects.using('spk').filter(user_id=user.id)[0]
			attendance_exists = TestAttendance.objects.using('spk').filter(student_id=student.id).exists()
			if attendance_exists:
				data['is_spk_test_user']=True
				data['email']=email
				messages.success(request,'Email registered with spoken tutorial')
				data['messages'] = update_msg(request)
				return JsonResponse(data)
		except Exception as e:
			messages.error(request,'Email is not registered with spoken tutorial test')
			data['messages']=update_msg(request)
			return JsonResponse(data)
	else:
		messages.error(request,'Email is not registered with spoken tutorial')
		data['messages']=update_msg(request)
		return JsonResponse(data)	
	return JsonResponse(data)

def register_user(request):
	if request.method == 'POST':
		email = request.POST['student_email']
		password = request.POST['password']
		try:
			user = User.objects.using('spk').get(Q(email__iexact=email))
			if user is not None:
				if user.check_password(password):
					rec_user = User.objects.create_user(username=user.username,password=user.password,email=user.email
						,first_name=user.first_name,last_name=user.last_name)
					try:
						student_group = Group.objects.get(id=2)
						rec_user.groups.add(student_group)
						rec_user.save()
						student_obj=student.objects.create(user=rec_user)
					except Exception as e:
						pass
					login(request, rec_user)
					return render(request, 'emp/student_profile.html')
				else:
					messages.add_message(request, messages.INFO, 'Incorrect password !')
					return render(request, 'register.html',{'email':email})
		except Exception as e:
			pass
	return render(request, 'login.html')



