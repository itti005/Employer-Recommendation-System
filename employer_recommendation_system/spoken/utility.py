
from spoken.models import EventTestStatus, FossCategory, Participant, SpokenStudent,SpokenUser
from django.contrib.auth.models import User
from emp.models import Student
from django.contrib.auth.models import Group
from django.contrib import messages
import datetime
from django.contrib.auth.hashers import make_password

def create_jrs_user(sp_user):
    try:
        user = User(username=sp_user.email,email=sp_user.email,first_name=sp_user.first_name,last_name=sp_user.last_name,is_active=sp_user.is_active)
        user.save()
    except Exception as e:
        print(e)
        return None
    return user

def create_student(sp_user,jrs_user,is_student_role,spk_student_record,is_ilw):
    Student.objects.create(user=jrs_user,spk_usr_id=sp_user.id)
    jrs_student = Student.objects.get(user=jrs_user)
    if is_student_role or spk_student_record:
        group = Group.objects.get(name='STUDENT')
        jrs_user.groups.add(group)
        if spk_student_record:
            jrs_student.gender = spk_student_record.gender
            jrs_student.spk_student_id = spk_student_record.id
            jrs_student.save()
        else:
            spk_student = SpokenStudent(user=sp_user,verified=1,error=0)
            spk_student.save()
            jrs_student.spk_student_id = spk_student.id
            jrs_student.save()
    if is_ilw:
        create_ilw_student_role(jrs_user)
    
    
    return jrs_student

def create_ilw_student_role(jrs_user):
    group = Group.objects.get(name='STUDENT_ILW')
    jrs_user.groups.add(group)

# def create_hr_manager(request,sp_user):
def create_hr_manager(jrs_user):
    
    # user = create_jrs_user(sp_user)
    # if not user:
    #     messages.error(request,'Problem occurred while registering the user for Job Recommendation System')
    #     return None
    if jrs_user:
        jrs_user.groups.add(Group.objects.get(name='MANAGER'))
    return jrs_user

def fetch_ilw_scores(student):
    scores = []
    spk_user = student.spk_usr_id
    try:
        participant = Participant.objects.get(user_id=spk_user.id)
        test_status = EventTestStatus.objects.filter(participant_id=participant.id)
        for item in test_status:
            foss_obj = FossCategory.objects.get(id=item.fossid_id)
            scores.append({'foss':foss_obj.id,'name':foss_obj.foss,'grade':item.mdlgrade,'quiz':item.mdlquiz_id,'mdl':item})

    except:
        pass
    return scores

def create_mdl_user_in_jrs(mdluser,password):
    try:
        spk_user = SpokenUser.objects.create(email=mdluser.email,username=mdluser.username,password=password,
        is_active=True,is_superuser=0,is_staff=0,date_joined=datetime.now(),first_name=mdluser.firstname,last_name=mdluser.lastname)
        spk_user.password = make_password(password)
        spk_user.save()
    except Exception as e:
        print(e)
        return None
    spk_student = SpokenStudent.objects.create(user=spk_user,verified=1,error=0)
    jrs_user = create_jrs_user(spk_user)
    jrs_student = create_student(spk_user,jrs_user,False)
    return jrs_user


