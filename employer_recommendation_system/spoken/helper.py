from django.contrib.auth.models import User
from spoken.models import SpokenUser, SpokenStudent, TestAttendance, Profile, SpokenUserGroup,Participant
from moodle.models import MdlUser
import hashlib
from django.contrib.auth.hashers import make_password

def is_jrs_user(email):
    try:
        return User.objects.get(email=email)
    except Exception as e:
        print(f"Exception : {e}")
        return None

def pwd_exists(email):
    return User.objects.filter(email=email)[0].password

def auth_jrs(email):
    pass

def is_spk_user(email):
    result = SpokenUser.objects.filter(email=email)
    if len(result) > 1:
        print("Found multiple users; mail web-team & the user .& display relevant message")
    else:
        return result[0]

def is_spk_student_role(sp_user):
    b = 'Student' in [role.group.name for role in sp_user.spokenusergroup_set.all()]
    return b

def is_spk_student_record(sp_user):
    return SpokenStudent.objects.filter(user_id=sp_user.id).first()

def is_ILW(sp_user):
    return Participant.objects.filter(user_id=sp_user.id)

def is_hr_manager(sp_user):
    return SpokenUserGroup.objects.filter(group__name='HR-Manager', user=sp_user)

def encript_mdl_password(password):
    password = hashlib.md5((password + 'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').encode('utf-8')).hexdigest()
    return password

def is_mdl_user(email,password):
    if MdlUser.objects.filter(email=email).first():
        mdl_pwd = encript_mdl_password(password)
        mdluser = MdlUser.objects.filter(email=email, password=mdl_pwd).last()
        return mdluser
    return None

    
