from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views import generic
from django.urls import reverse_lazy, reverse
from .forms import RegisterForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.models import Group,User
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from emp.models import *
from django.conf import settings
UserModel = get_user_model()
from emp.models import Student as RecStudent
class LoginViewCustom(LoginView):
	template_name = 'accounts/login.html'					

	def get_success_url(self):	
		print("************** here")							#return profile template based on the user role
		role_url = {
		settings.ROLES['MANAGER'][1]:'/manager',
		settings.ROLES['STUDENT'][1]:'/student',
		settings.ROLES['EMPLOYER'][1]:'/employer',
		}
		print("************** role_url",role_url)
		print("************** dic",self.request.user.groups.all()[0].name )
		url = role_url[self.request.user.groups.all()[0].name]
		print("************** url",url)
		print("************** url",url)
		return url

	def get_context_data(self, **kwargs):
		context = super(LoginView, self).get_context_data(**kwargs)
		context['success'] = "msg here"
		print("inside login ******************* ")
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
			student = SpkStudent.objects.using('spk').filter(user_id=user.id)[0]
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

def register_student(request):
	if request.method == 'POST':
		email = request.POST['student_email']
		password = request.POST['password']
		try:
			user = User.objects.using('spk').get(Q(email__iexact=email))
			if user is not None:
				if user.check_password(password):
					print("pwd matched *************")
					# rec_user = User.objects.create_user(username=user.username,password=user.password,email=user.email
					# 	,first_name=user.first_name,last_name=user.last_name)
					rec_user = User.objects.using('spk').get(pk=user.id)
					rec_user.pk = None
					rec_user.save(using='default')
					try:
						print('inside try ------------ ')
						student_group = Group.objects.get(id=settings.ROLES['STUDENT'][0])
						rec_user.groups.add(student_group)
						rec_user.save()
						print(f"-----------------{rec_user}")
						print(f'{rec_user} is saved ************')
						student_obj=RecStudent.objects.create(user=rec_user)
						print('1')
						# fetch student university from spoken db
						student_spk = SpkStudent.objects.using('spk').filter(user_id=user.id)[0]
						print('2')
						# univ = TestAttendance.objects.using('spk').filter(student_id=student.id)
						testAttendance = TestAttendance.objects.using('spk').filter(student_id=student_spk.id).select_related('test')
						print('3')
						academic_insti = testAttendance[0].test.academic_id
						print('4')
						student_obj.university = AcademicCenter.objects.using('spk').get(pk=academic_insti).institution_name
						print('5')
						print("univ --------- {}".format(student_obj.university))
						
						student_obj.save()
						
					except Exception as e:
						print("inside exception ------------------------ ")
						print(e)
					login(request, rec_user)
					return render(request, 'emp/student_homepage.html')
				else:
					messages.add_message(request, messages.INFO, 'Incorrect password !')
					return render(request, 'register.html',{'email':email})
		except Exception as e:
			print(e)
	return render(request, 'accounts/login.html')




