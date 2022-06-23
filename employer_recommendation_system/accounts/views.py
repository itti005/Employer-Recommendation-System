from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from spoken.models import SpokenGroup
from moodle.models import MdlUser
from .forms import ChangePasswordForm, RegisterForm, PasswordResetForm
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
from spoken.models import SpokenStudent as SpkStudent
import random
import string
from spoken.backends import *
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseRedirect
from django.conf import settings
from datetime import datetime
SITE_URL = getattr(settings, "SITE_URL", "https://jrs.spoken-tutorial.org/")
PASSWORD_MAIL_SENDER = getattr(settings, "NO_REPLY_SPOKEN_MAIL", "no-reply@spoken-tutorial.org")

class LoginViewCustom(LoginView):
	template_name = 'accounts/login.html'					

	def get_success_url(self):	
		role_url = {
		settings.ROLES['MANAGER'][1]:'/manager',
		settings.ROLES['STUDENT'][1]:'/student',
		settings.ROLES['EMPLOYER'][1]:'/employer',
		"STUDENT_ILW" : '/student',
		}
		url = role_url[self.request.user.groups.all()[0].name]
		r = self.request.POST.get('next')
		r2 = self.request.get_full_path()
		r1 = self.redirect_field_name
		if 'change-password' in r2:
			return reverse('change_password')
		return url

# class RegisterView(generic.CreateView):
# 	form_class = RegisterForm
# 	template_name = 'accounts/register.html'
	
# 	def get_success_url(self):
# 		messages.add_message(self.request, messages.INFO, 'Successfully Registered !')
# 		return reverse('login')

# 	def form_valid(self, form):
# 		response = super().form_valid(form)
# 		user = UserModel.objects.get(Q(username__iexact=form.data['username']) | Q(email__iexact=form.data['email']))
# 		group_type = form.data['group']
# 		if group_type=='students':
# 			pass
		
# 		g = Group.objects.get(name=group_type)
# 		user.groups.add(g)
# 		user.save()
# 		return response
def update_msg(request):
	django_messages = []
	for message in messages.get_messages(request):
			django_messages.append({'message':message.message,'tag':message.tags})	
			return django_messages

# def validate_student(request):
# #def validate_student():
# 	email = request.GET.get('email', None)
# 	#email = 'ankita7@gmail.com' 

# 	if User.objects.filter(email__iexact=email).exists():
# 		data = {'is_rec_student':True}
# 		messages.success(request,'Email Id already registered with recommendation system')
# 		data['messages'] = update_msg(request)
# 		return JsonResponse(data)

# 	is_spoken_student = User.objects.using('spk').filter(email__iexact=email).exists()
# 	data = {'is_spoken_student':is_spoken_student}
# 	if is_spoken_student:
# 		user = User.objects.using('spk').filter(email__iexact=email)[0]
# 		try:
# 			student = SpkStudent.objects.using('spk').filter(user_id=user.id)[0]
# 			attendance_exists = TestAttendance.objects.using('spk').filter(student_id=student.id).exists()
# 			if attendance_exists:
# 				data['is_spk_test_user']=True
# 				data['email']=email
# 				messages.success(request,'Email registered with spoken tutorial')
# 				data['messages'] = update_msg(request)
# 				return JsonResponse(data)
# 		except Exception as e:
# 			messages.error(request,'Email is not registered with spoken tutorial test')
# 			data['messages']=update_msg(request)
# 			return JsonResponse(data)
# 	else:
# 		messages.error(request,'Email is not registered with spoken tutorial')
# 		data['messages']=update_msg(request)
# 		return JsonResponse(data)	
# 	return JsonResponse(data)

def register_student(request):
	if request.method == 'POST':
		email = request.POST['student_email']
		password = request.POST['password']
		try:
			user = User.objects.using('spk').get(Q(email__iexact=email))
			if user is not None:
				if user.check_password(password):
					# rec_user = User.objects.create_user(username=user.username,password=user.password,email=user.email
					# 	,first_name=user.first_name,last_name=user.last_name)
					rec_user = User.objects.using('spk').get(pk=user.id)
					rec_user.pk = None
					rec_user.save(using='default')
					try:
						student_group = Group.objects.get(id=settings.ROLES['STUDENT'][0])
						rec_user.groups.add(student_group)
						rec_user.save()
						student_obj=RecStudent.objects.create(user=rec_user)
						# fetch student university from spoken db
						student_spk = SpkStudent.objects.using('spk').filter(user_id=user.id)[0]
						# univ = TestAttendance.objects.using('spk').filter(student_id=student.id)
						testAttendance = TestAttendance.objects.using('spk').filter(student_id=student_spk.id).select_related('test')
						academic_insti = testAttendance[0].test.academic_id
						student_obj.university = AcademicCenter.objects.using('spk').get(pk=academic_insti).institution_name
						student_obj.save()
						
					except Exception as e:
						print(e)
					login(request, rec_user)
					return render(request, 'emp/student_homepage.html')
				else:
					messages.add_message(request, messages.INFO, 'Incorrect password !')
					return render(request, 'register.html',{'email':email})
		except Exception as e:
			print(e)
	return render(request, 'accounts/login.html')
def create_profile(user, phone):
    confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(7))
    profile = Profile(user=user, confirmation_code=confirmation_code, phone=phone,created=datetime.now())
    profile.save()
    return profile

def reset_password(request):
	context = {}
	form = PasswordResetForm()
	context['form'] = form
	if request.method == "POST":
		form = PasswordResetForm(request.POST)
		context['form'] = form
		if form.is_valid():
			email=request.POST['email']
			password = ''.join( random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
			
			# check if the user exists in SpokenUser
			spoken_user = SpokenUser.objects.filter(Q(email=email) | Q(username=email)).first()
			# check if the user exists in MdlUser
			mdl_user = MdlUser.objects.filter(email=email).first()
			if mdl_user:
				mdl_pwd = encript_mdl_password(password)
				mdl_user.password = mdl_pwd
				mdl_user.save()
				if not spoken_user:
					spoken_user = SpokenUser.objects.create(email=email,username=email,password=password,
                    is_active=True,is_superuser=0,is_staff=0,date_joined=datetime.now(),first_name=mdl_user.firstname,last_name=mdl_user.lastname)
					group = SpokenGroup.objects.get(name='Student')
					try:
						SpokenUserGroup.objects.create(user=spoken_user,group=group)
					except:
						print("User has Student role")
			else:
				print("Student is not mdluser")

			spoken_user.password = make_password(password)
			spoken_user.save()
			
			
			if not spoken_user.profile_set.first():
				profile = create_profile(spoken_user,None)
			changePassUrl = SITE_URL+"accounts/change-password"
			
			subject  = "Spoken Tutorial password reset"
			to = [spoken_user.email]
			message = '''Hi {0},

Your account password at 'Spoken Tutorials' has been reset
and you have been issued with a new temporary password.

Your current login information is now:
   username: {1}
   password: {2}

With respect to change your password kindly follow the steps written below :

Step 1. Visit below link to change the password. Provide temporary password given above in the place of Old Password field.
    {3}

Step 2.Use this changed password for spoken Forum Login, Moodle Login & Job Recommendation System also.

In most mail programs, this should appear as a blue link which you can just click on.  If that doesn't work, then cut and 
paste the address into the address line at the top of your web browser window.

Best Wishes,
Admin
Spoken Tutorials
IIT Bombay.
'''.format(spoken_user.username, spoken_user.username, password,changePassUrl)

			print(f"username ***************** {spoken_user.email}\npassword ******************** {password}\nchangePassUrl ************** {changePassUrl}")
			email = EmailMultiAlternatives(
                subject, message, PASSWORD_MAIL_SENDER,
                to = to, bcc = [], cc = [],
                headers={'Reply-To': PASSWORD_MAIL_SENDER, "Content-type":"text/html;charset=iso-8859-1"}
            )
			try:
				result = email.send(fail_silently=False)
				messages.success(request, "New password has been sent to your email "+spoken_user.email)
				return HttpResponseRedirect(SITE_URL+'accounts/change-password/')

			except Exception as e:
				print(e)
		else:
			print(form.errors)
	return render(request, 'accounts/password_reset.html',context)

def changeMdlUserPass(email, password_string):
    # updated mdl pass when auth user pass change
    try:
        user = MdlUser.objects.filter(email=email).first()
        password_encript = encript_mdl_password(password_string)
        user.password = password_encript
        user.save()
        return True
    except Exception:
        return False

# @login_required
def change_password(request):
	context = {}
	form = ChangePasswordForm()
	if request.user.is_anonymous:
		# return HttpResponseRedirect(reverse('change_password'))
		return HttpResponseRedirect(SITE_URL+'login/?next=/accounts/change-password')

	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			profile = Profile.objects.get(user_id = form.cleaned_data['userid'], confirmation_code = form.cleaned_data['code'])
			user = profile.user
			user.password = make_password(form.cleaned_data['new_password'])
			# user.set_password(form.cleaned_data['new_password'])
			user.save()
			changeMdlUserPass(user.email, form.cleaned_data['new_password'])
			messages.success(request, "Your account password has been updated successfully!")
			# return HttpResponseRedirect("/login/")
			return HttpResponseRedirect(reverse('login'))
	
	context['form'] = form
	# get code from profile
	# s = request.user.student
	# spk_user_id = s.spk_usr_id
	try:
		spk_user = SpokenUser.objects.filter(email=request.user.email)[0]
		spk_user_id = spk_user.id
	except:
		print("Not a spoken user") #fossee user
	context['userid'] = spk_user.id
	profile = Profile.objects.filter(user_id=spk_user_id).first()
	if profile:
		context['code'] = profile.confirmation_code

	return render(request, 'accounts/change_password.html', context)
