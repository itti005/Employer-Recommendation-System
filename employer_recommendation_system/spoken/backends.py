from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from spoken.models import SpokenUser, SpokenStudent, TestAttendance
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group

class SpokenStudentBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None):
        try:
            sp_user = SpokenUser.objects.get(username=username)
            pwd_valid = check_password(password, sp_user.password)
            if pwd_valid:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    try:
                        user = User.objects.get(email=username)
                    except User.DoesNotExist:
                        try:
                            student = SpokenStudent.objects.get(user=sp_user)
                            attendance_exists = TestAttendance.objects.filter(student_id=student.id).exists()
                            if attendance_exists:
                                user = User(username=sp_user.username)
                                user.email = sp_user.email
                                user.is_active = True
                                user.save()
                                group = Group.objects.get(name='STUDENT')
                                user.groups.add(group)
                        except SpokenStudent.DoesNotExist:
                            pass
                return user
        except SpokenUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None