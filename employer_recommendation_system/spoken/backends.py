from distutils.log import error
import django


from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from spoken.models import SpokenUser
from django.contrib.auth.hashers import check_password
from .utility import *
from .helper import *
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import authenticate
from django.core.validators import validate_email

class SpokenStudentBackend(ModelBackend):    
    def authenticate(self, request, username=None, password=None): #Only check for email
        email=username
        try:
            validate_email(email)
        except:
            #check if that username belongs to HR
            #if yes; authenticate using spk
            # sp_user = SpokenUser.objects.get(username=username)
            jrs_user = User.objects.filter(username=username) # Check for existing JRS user with no email
            if jrs_user:
                if check_password(password, jrs_user[0].password) :
                    return jrs_user[0]
            else:
                return None

            print("Invalid Email")
            # messages.add_message(request,messages.ERROR,'Please enter valid Email.')
            return None
        jrs_user=is_jrs_user(email)
        if jrs_user:#check password in jrs_db else in spk_db
            if jrs_user.password: #fossee
                if check_password(password, jrs_user.password):
                    return jrs_user
                else:
                    return None
            else:#check spk password; spk, ilw
                sp_user = SpokenUser.objects.get(email=email)
                if check_password(password, sp_user.password): #For spk students & ilw
                    return jrs_user
                else:
                    messages.add_message(request,messages.INFO,"Please enter correct password. Password should be same as Spoken Tuttorial login.")
                    return None
        else:#new user; first time login
            sp_user = is_spk_user(email)
            if sp_user:
                if check_password(password, sp_user.password):
                    if is_hr_manager(sp_user):
                        jrs_user = create_jrs_user(sp_user)
                        create_hr_manager(jrs_user)
                        return jrs_user
                    else:
                        is_student_role = is_spk_student_role(sp_user)
                        is_student_record = is_spk_student_record(sp_user)
                        is_ilw = is_ILW(sp_user)
                        if is_student_role or is_student_record or is_ilw:
                            jrs_user = create_jrs_user(sp_user)
                            create_student(sp_user,jrs_user,is_student_role,is_student_record,is_ilw)
                            # if is_ilw:
                            #     create_ilw_student_role(jrs_user)
                            return jrs_user


        mdl_user = is_mdl_user(email,password)
        if mdl_user:
            jrs_user = create_mdl_user_in_jrs(mdl_user,password)
            return jrs_user
        print(f"{email} : Does not belong to jrs-auth_user, spk-auth_user & mdl-user or authentication not valid")
        return None                

                    

        #     if user:
        #         return user
        #     else: #show password incorrect message
        #         messages.add_message("Password entered is incorrect")
        # else:
            




        # sp_user = None
        # try:
        #     sp_user = SpokenUser.objects.get(username=username)
        # except SpokenUser.DoesNotExist: #username does not exist in Spoken Tutorial 
        #     pass
        # if sp_user:
        #     if check_password(password, sp_user.password): #For spk students & ilw
        #         try:
        #             user = User.objects.get(username=username)
        #             return user
        #         except User.DoesNotExist:
        #             if SpokenUserGroup.objects.filter(group__name='HR-Manager', user=sp_user):# check for HR Role in SPK
        #                 user = create_hr_manager(request,sp_user)
        #                 return user
        #             spk_student_role = 'Student' in [role.group.name for role in sp_user.spokenusergroup_set.all()]
        #             spk_student_record = SpokenStudent.objects.filter(user_id=sp_user.id).first()
        #             is_ilw = Participant.objects.filter(user_id=sp_user.id)
        #             if spk_student_role or spk_student_record or is_ilw: # check for student status in SPK
        #                 jrs_user = create_jrs_user(sp_user)
        #                 if jrs_user:
        #                     create_student(sp_user,jrs_user,spk_student_record)
        #                     if is_ilw:
        #                         create_ilw_student_role(jrs_user)
        #                     return jrs_user
                    
                        
        
        # if MdlUser.objects.filter(email=username).first(): #Check for moodle entry
        #     mdl_pwd = encript_mdl_password(password)
        #     mdluser = MdlUser.objects.filter(email=username, password=mdl_pwd).last()
        #     if mdluser :
        #         try:
        #             spk_user = SpokenUser.objects.create(email=mdluser.email,username=mdluser.username,password=password,
        #             is_active=True,is_superuser=0,is_staff=0,date_joined=datetime.now(),first_name=mdluser.firstname,last_name=mdluser.lastname)
        #             spk_user.password = make_password(password)
        #             spk_user.save()
        #         except Exception as e:
        #             print(e)
        #             return None
        #         spk_student = SpokenStudent.objects.create(user=spk_user,verified=1,error=0)
        #         jrs_user = create_jrs_user(spk_user)
        #         jrs_student = create_student(sp_user,jrs_user,False)
        #         return jrs_user

        
        # return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None