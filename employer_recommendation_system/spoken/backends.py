from datetime import datetime
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from moodle.models import MdlUser
from spoken.models import SpokenUser, SpokenStudent, TestAttendance, Profile, SpokenUserGroup
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from emp.models import Student
import hashlib
from django.contrib import messages
from django.contrib.auth.hashers import make_password

def create_jrs_user(sp_user):
    try:
        user = User(username=sp_user.username)
        user.email = sp_user.email
        user.first_name = sp_user.first_name
        user.last_name = sp_user.last_name
        user.is_active = True
        user.save()
    except Exception as e:
        print(e)
        return None
    return user

def encript_mdl_password(password):
    password = hashlib.md5((password + 'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').encode('utf-8')).hexdigest()
    return password

class SpokenStudentBackend(ModelBackend):    


    def authenticate(self, request, username=None, password=None):
        sp_user = None
        try:
            sp_user = SpokenUser.objects.get(username=username)
        except SpokenUser.DoesNotExist:
            try:
                sp_user = SpokenUser.objects.get(email=username)
            except:
                pass
        # if SpokenUser exists : 
        if sp_user:
            pwd_valid = check_password(password, sp_user.password)
            if pwd_valid:
                try:
                    user = User.objects.get(username=username)
                    return user
                except User.DoesNotExist:
                    try:
                        user = User.objects.get(email=username)
                        return user
                    except User.DoesNotExist:
                        # check for HR Role
                        if SpokenUserGroup.objects.filter(group__name='HR-Manager', user=sp_user).count() == 1:
                            user = create_jrs_user(sp_user)
                            if not user:
                                messages.error(request,'Problem occurred while registering the user for Job Recommendation System')
                                return None
                            user.groups.add(Group.objects.get(name='MANAGER'))
                            return user
                        spk_student_role = False
                        spk_student_record = False
                        if 'Student' in [role.group.name for role in sp_user.spokenusergroup_set.all()]:
                            spk_student_role = True
                        spk_student = SpokenStudent.objects.filter(user_id=sp_user.id).first()
                        if spk_student:
                            spk_student_record = True
                        if spk_student_role or spk_student_record:
                            user = create_jrs_user(sp_user)
                            group = Group.objects.get(name='STUDENT')
                            user.groups.add(group)
                            Student.objects.create(user=user, 
                                        spk_usr_id=sp_user.id )
                            jrs_student = Student.objects.get(user=user)
                            if spk_student_record:
                                jrs_student.gender = spk_student.gender
                                jrs_student.spk_student_id = spk_student.id
                                jrs_student.save()
                                return user
                            else:
                                #create spoken student account
                                spk_student = SpokenStudent(user=sp_user,verified=1,error=0)
                                spk_student.save()
                                jrs_student.spk_student_id = spk_student.id
                                jrs_student.save()
                                return user
        mdl_user = MdlUser.objects.filter(email=username).first()
        if mdl_user:
            #  check mdl password
            mdl_pwd = encript_mdl_password(password)
            mdluser = MdlUser.objects.filter(email=username, password=mdl_pwd).last()
            if mdluser :
                try:
                    spk_user = SpokenUser.objects.create(email=mdluser.email,username=mdluser.username,password=password,
                    is_active=True,is_superuser=0,is_staff=0,date_joined=datetime.now(),first_name=mdluser.firstname,last_name=mdluser.lastname)
                    spk_user.password = make_password(password)
                    spk_user.save()
                except Exception as e:
                    print(e)
                    return None
                spk_student = SpokenStudent.objects.create(user=spk_user,verified=1,error=0)
                user = create_jrs_user(spk_user)
                group = Group.objects.get(name='STUDENT')
                user.groups.add(group)
                Student.objects.create(user=user, spk_usr_id=spk_user.id,spk_student_id=spk_student.id )
                return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None