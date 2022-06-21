
from spoken.models import EventTestStatus, Participant, SpokenUser, TestAttendance
from .models import JobShortlist, Job,STATUS
from spoken.models import FossMdlCourses, SpokenCity, SpokenState, InstituteType,FossCategory
import pandas as pd
import datetime
from spoken.helper import is_spk_student_role, is_ILW

RATING = {
    'ONLY_VISIBLE_TO_ADMIN_HR':0,
    'DISPLAY_ON_HOMEPAGE':1,
    'VISIBLE_TO_ALL_USERS':2
}
JOB_RATING=[(RATING['VISIBLE_TO_ALL_USERS'],'Visible to all users'),(RATING['ONLY_VISIBLE_TO_ADMIN_HR'],'Only visible to Admin/HR'),(RATING['DISPLAY_ON_HOMEPAGE'],'Display on homepage')]
JOB_STATUS=[(1,'Active'),(0,'Inactive')]
COMPANY_RATING = [(RATING['VISIBLE_TO_ALL_USERS'],'Visible to all users'),(RATING['ONLY_VISIBLE_TO_ADMIN_HR'],'Only visible to Admin/HR'),(RATING['DISPLAY_ON_HOMEPAGE'],'Display on homepage')]

CURRENT_EDUCATION = 1
PAST_EDUCATION = 2
JOB_APP_STATUS = {'RECEIVED_APP':0,'FIRST_SHORTLIST':1,'REJECTED':2}
DEFAULT_JOB_TYPE=1
SECOND_SHORTLIST_EMAIL = 2
MANDATORY_FOSS = 1
OPTIONAL_FOSS = 2
DISPLAY_ON_HOMEPAGE = 1
ACTIVE = 1

APPLIED = 0 # student has applied but not yet shortlisted by HR Manager
APPLIED_SHORTLISTED = 1 # student has applied & shortlisted by HR Manager

def has_spk_student_role(student):
    return 'STUDENT' in [x.name for x in student.user.groups.all()]

def has_ilw_role(student):
    return 'STUDENT_ILW' in [x.name for x in student.user.groups.all()]

def has_fossee_role(student):
    return 'STUDENT_FOSSEE' in [x.name for x in student.user.groups.all()]

#called
def get_applied_joblist(rec_student): #Jobs where student has applied
    return JobShortlist.objects.filter(student=rec_student,status__in=[APPLIED,APPLIED_SHORTLISTED])

def has_student_role(student):
    student_roles = list(set(['STUDENT','STUDENT_ILW','STUDENT_FOSSEE']).intersection([x.name for x in student.user.groups.all()]))
    return student_roles
#called
def get_applied_jobs(rec_student):
    js = JobShortlist.objects.filter(student=rec_student)
    return [x.job for x in js]

# ????????????
def get_eligible_jobs(spk_user_id):  #Jobs for which the student has not yet applied
    all_jobs = Job.objects.all().filter(rating=RATING['DISPLAY_ON_HOMEPAGE'],status=STATUS['ACTIVE'])
    if not all_jobs:
        all_jobs = Job.objects.all().filter(status=STATUS['ACTIVE'])
    applied_jobs = [x.job for x in get_applied_joblist(spk_user_id)]
    return list(set(all_jobs)-set(applied_jobs))

def merge_scores(d1,d2):
    for key in d2.keys():
        if key not in d1:
            d1[key] = d2[key]
        else:
            if d2[key] > d1[key]:
                d1[key] = d2[key]

# def fetch_ta_scores(student,df_fmc):
def fetch_ta_scores(student):
    fmc = FossMdlCourses.objects.values('foss_id','mdlcourse_id','mdlquiz_id')
    df_fmc = pd.DataFrame(fmc)
    df_fmc = df_fmc.set_index(['mdlcourse_id','mdlquiz_id'])
    scores = []
    ta = TestAttendance.objects.filter(student_id = student.spk_student_id,status__gte=3)
    for item in ta :
        if item.mdlcourse_id and item.mdlquiz_id:
            foss_id = df_fmc.loc[(item.mdlcourse_id,item.mdlquiz_id)].values[0][0]
            fs = FossCategory.objects.get(id=foss_id)
            scores.append({'foss': foss_id,
                        'name':fs.foss,'grade':item.mdlgrade,'quiz':item.mdlquiz_id,'mdl':item})
    return scores

def fetch_ilw_scores(student):
    # fmc = FossMdlCourses.objects.values('foss_id','mdlcourse_id','mdlquiz_id')
    # df_fmc = pd.DataFrame(fmc)
    # df_fmc = df_fmc.set_index(['mdlcourse_id','mdlquiz_id'])
    scores = []
    try:
        participant = Participant.objects.get(user=student.spk_usr_id)
        ets = EventTestStatus.objects.filter(participant=participant,part_status__gte=2)
        for item in ets:
            foss_obj = FossCategory.objects.get(id=item.fossid_id)
            scores.append({'foss':foss_obj.id,'name':foss_obj.foss,'grade':item.mdlgrade,'quiz':item.mdlquiz_id,'mdl':item})

    except Participant.DoesNotExist:
        print(f"{student} : Not an ILW student")
    return scores

def fetch_fossee_scores(student):
    pass

#function to get student spoken test scores; returns list of dictionary of foss & scores
def fetch_student_scores(student):  #parameter : recommendation student obj
    scores = {}
    # fmc = FossMdlCourses.objects.values('foss_id','mdlcourse_id','mdlquiz_id')
    # df_fmc = pd.DataFrame(fmc)
    # df_fmc = df_fmc.set_index(['mdlcourse_id','mdlquiz_id']
    groups = [x.name for x in student.user.groups.all()]
    if 'STUDENT' in groups:
        s = fetch_ta_scores(student)
        scores = merge_scores(scores,s)
        
    if 'STUDENT_ILW' in groups:
        s = fetch_ilw_scores(student)
        scores = merge_scores(scores,s)

    if 'STUDENT_FOSSEE' in groups:
        #scores = scores + fetch_fossee_scores(student,df_fmc)
        pass #ToDO #FOSSEE

    return scores


def is_job_recommended_ta(job,student):
    scores = fetch_ta_scores(student)
    states = get_query_state_list(job)
    cities = get_query_city_list(job)
    insti_type = get_query_insti_type_list(job)
    valid_fosses = get_valid_fosses(job,scores)
    mdl_quiz_ids = [x.mdlquiz_id for x in FossMdlCourses.objects.filter(foss_id__in=valid_fosses)]
    test_attendance = TestAttendance.objects.filter(student_id=student.spk_student_id, 
                                                    mdlquiz_id__in=mdl_quiz_ids,
                                                    test__academic__state__in=states if states!='' else SpokenState.objects.all(),
                                                    test__academic__city__in=cities if cities!='' else SpokenCity.objects.all(),
                                                    status__gte=3,
                                                    test__academic__institution_type__in=insti_type if insti_type!='' else InstituteType.objects.all(),
                                                    test__academic__status__in=[job.activation_status] if job.activation_status else [1,3],)
    if job.from_date and job.to_date:
        test_attendance = test_attendance.filter(test__tdate__range=[job.from_date, job.to_date])
    elif job.from_date:
        test_attendance = test_attendance.filter(test__tdate__gte=job.from_date)
    if test_attendance:
        return True
    return False

def get_query_state_list(job):
    if job.state and job.state!='0':
        states = list(map(int,job.state.split(',')))
    else:
        states = ''
    return states


def get_query_city_list(job):
    if job.city and job.city!='0':
        cities = list(map(int,job.city.split(',')))
    else:
        cities = ''
    return cities

def get_query_insti_type_list(job):
    if job.institute_type and job.institute_type!='0':
        insti_type = list(map(int,job.institute_type.split(',')))
    else:
        insti_type = ''
    return insti_type

def get_valid_fosses(job,scores):
    fosses = list(map(int,job.foss.split(',')))
    # valid_fosses = [ item for item in scores if item in fosses and scores[item] >= job.grade]
    valid_fosses = []
    for item in scores:
        if item['foss'] in fosses:
            if item['grade'] >= job.grade:
                valid_fosses.append(item['foss'])
    # valid_fosses = [ item['foss'] for item in scores if item['foss'] in fosses and item['grade'] >= job.grade]
    return valid_fosses


def is_job_recommended_ilw(job,student):
    scores = fetch_ilw_scores(student)
    valid_fosses = get_valid_fosses(job,scores)
    participant = Participant.objects.get(user_id=student.spk_usr_id)
    ets = EventTestStatus.objects.filter(participant=participant,fossid__in=valid_fosses)
    return ets

def is_job_recommended_fossee(job,student):
    pass


def get_recommended_jobs(student):
    rec_jobs = []
    jobs = Job.objects.filter(last_app_date__gte=datetime.datetime.now(),status=STATUS['ACTIVE'])# All active jobs
    applied_jobs = get_applied_jobs(student)
    jobs = [x for x in jobs if x not in applied_jobs ]

    if has_spk_student_role(student):
        for job in jobs:
            if is_job_recommended_ta(job,student):
                rec_jobs.append(job)
    
    
    if has_ilw_role(student):
        for job in jobs:
            if is_job_recommended_ilw(job,student):
                rec_jobs.append(job)

    if has_fossee_role(student):
        for job in jobs:
            if is_job_recommended_fossee(job,student):
                rec_jobs.append(job)

    return rec_jobs  



