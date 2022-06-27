from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django import forms
from spoken.models import SpokenStudent, Participant, Profile
from moodle.models import MdlUser

from spoken.models import SpokenUser

class RegisterForm(UserCreationForm):   #form for employer registration
	class Meta:
		model = get_user_model()
		fields = ('email', 'username', 'password1', 'password2')

class PasswordResetForm(forms.Form):
	email = forms.EmailField()

	def clean_email(self):
		email = self.cleaned_data['email']
		error = 1
		err_msg = None
		try:
			user = SpokenUser.objects.filter(email=email).first()
			if user:
				#check if mdl user or belongs to 'Student' or 'HR-Manager' group or entry in 'Student' table
				spk_student_role = 	'Student' in [role.group.name for role in user.spokenusergroup_set.all()]
				spk_student_record = SpokenStudent.objects.filter(user_id=user.id).first()
				is_mdl_user = MdlUser.objects.filter(email=email).first()
				is_hr = 'HR-Manager' in [role.group.name for role in user.spokenusergroup_set.all()]
				is_ilw = Participant.objects.filter(user=user)
				if not (spk_student_role or spk_student_record or is_mdl_user or is_hr or is_ilw):
					error = 1
					err_msg = "Only Student or HR can register on JRS. Please follow https://spoken-tutorial.org/accounts/forgot-password/ to change the password."
				else:
					if user.is_active:
						error = 0
					else:
						error = 1
						err_msg = "Your account is not activated. Kindly activate the account by clicking on the activation link which has been sent to your registered email id."
			else:
				user = MdlUser.objects.filter(email=email).first()
				if user:
					error = 0
				else:
					#create spoken user with email
					error = 1
					err_msg = f"{email} does not exist in Spoken Tutorial & Online Test Portal."
		except Exception as e:
			print(e)
		if error:
			raise forms.ValidationError( err_msg )

class ChangePasswordForm(forms.Form):
	old_password = forms.CharField(widget=forms.PasswordInput())
	new_password = forms.CharField(widget=forms.PasswordInput(),min_length=8,)
	confirm_new_password = forms.CharField(widget=forms.PasswordInput(),min_length=8,)
	code = forms.CharField()
	userid = forms.CharField()

	def clean(self):
		profile = Profile.objects.get(user_id = self.cleaned_data['userid'],confirmation_code=self.cleaned_data['code'])
		user = profile.user
		p1 = self.cleaned_data['old_password']
		
		if 'old_password' in self.cleaned_data:
			pwd = make_password(self.cleaned_data['old_password'])
			if pwd != user.password:
			# if not user.check_password(self.cleaned_data['old_password']):
				raise forms.ValidationError("Old password did not match")
		new_password = self.cleaned_data.get('new_password')
		confirm_new_password = self.cleaned_data.get('confirm_new_password')
		if new_password and confirm_new_password:
			if new_password != confirm_new_password:
				raise forms.ValidationError("Passwords did not match")
		else:
			raise forms.ValidationError("Passwords did not match")
		return self.cleaned_data

	