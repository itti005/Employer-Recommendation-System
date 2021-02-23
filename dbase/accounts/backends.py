from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

#get user model
UserModel = get_user_model()

class EmailBackend(ModelBackend):
	def authenticate(self, request, username=None, password=None, **kwargs):
		try:
			print(" ************* getting user **********")
			user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
			print(" ************* username or email is : {}".format(user))
		except UserModel.DoesNotExist:
			print(" ************* UserModel.DoesNotExist")
			return None
		except MultipleObjectsReturned:
			return User.objects.filter(email=username).order_by('id').first()

		if user.check_password(password) and self.user_can_authenticate(user):
			return user

	def get_user(self, user_id):
		try:
			user = UserModel.objects.get(pk=user_id)
		except UserModel.DoesNotExist:
			return None
		return user if self.user_can_authenticate(user) else None