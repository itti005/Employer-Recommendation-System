from spoken.models import EventTestStatus, FossCategory, Participant, SpokenStudent
from django.contrib.auth.models import User
from emp.models import Student,Job
from django.contrib.auth.models import Group
from django.contrib import messages
import datetime
from .helper import *




# def fetch_ilw_scores(student):
#     scores = []
#     spk_user = student.spk_usr_id
#     try:
#         participant = Participant.objects.get(user_id=spk_user.id)
#         test_status = EventTestStatus.objects.filter(participant_id=participant.id)
#         for item in test_status:
#             foss_obj = FossCategory.objects.get(id=item.fossid_id)
#             scores.append({'foss':foss_obj.id,'name':foss_obj.foss,'grade':item.mdlgrade,'quiz':item.mdlquiz_id,'mdl':item})

#     except:
#         pass
#     return scores

# def get_recommended_jobs(student):
#     rec_jobs = []
#     jobs = Job.objects.filter(last_app_date__gte=datetime.datetime.now(),status=STATUS['ACTIVE'])# All active jobs
#     applied_jobs = get_applied_jobs(student)
#     jobs = [x for x in jobs if x not in applied_jobs ]
#     if has_spk_student_role(student):
#         for job in jobs:
#             if is_job_recommended_ta(job,student):
#                 rec_jobs.append(job)
#     if has_ilw_role(student):
#         if is_job_recommended_ilw(job,student):
#             rec_jobs.append(job)
#     if has_fossee_role(student):
#         if is_job_recommended_fossee(job,student):
#             rec_jobs.append(job)
#     return rec_jobs  
