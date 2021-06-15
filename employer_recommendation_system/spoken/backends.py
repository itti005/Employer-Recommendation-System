from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from spoken.models import SpokenUser, SpokenStudent, TestAttendance, Profile
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from emp.models import Student

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
                                user.first_name = sp_user.first_name
                                user.last_name = sp_user.last_name
                                user.is_active = True
                                user.save()
                                group = Group.objects.get(name='STUDENT')
                                user.groups.add(group)
                                st_profile = Profile.objects.filter(user=sp_user).first()
                                spk_student_id = SpokenStudent.objects.get(user=sp_user).id
                                Student.objects.create(user=user, 
                                    state=st_profile.state.name if st_profile.state else "", 
                                    phone=st_profile.phone, address=st_profile.address, 
                                    spk_usr_id=sp_user.id, spk_student_id=spk_student_id,gender=student.gender, 
                                    location=st_profile.location.name if st_profile.location else "", 
                                    district=st_profile.district.name if st_profile.district else "", 
                                    city=st_profile.city.name if st_profile.city else "")
                            else:
                                return None
                        except SpokenStudent.DoesNotExist:
                            return None
                return user
        except SpokenUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None