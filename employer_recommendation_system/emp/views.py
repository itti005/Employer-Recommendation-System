from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .models import *
from events.models import Student as SpkStudent
from emp.models import Student as RecStudent
from moodle.models import *
from events.models import TestAttendance,FossMdlCourses
from django.views.generic.edit import UpdateView
from events.models import Student as SpkStudent 
from events.models import User as SpkUser 
from creation.models import FossCategory 
class StudentUpdateView(UpdateView):
    model = Student
    fields = ['education','skills','about','experience','github','linkedin','cover_letter'] 
    
def fetch_spk_student_data():
    user = User.objects.get(id=1)
    spk_student_id = user.student.spk_usr_id
    spk_student = SpkStudent.objects.using('spk').get(id=spk_student_id)
    spk_user = SpkUser.objects.using('spk').get(id=spk_student.user_id) 
    test_attendance_entries = TestAttendance.objects.using('spk').filter( student_id = spk_student_id)
    for ta in test_attendance_entries :
        mdl_user_id = ta.mdluser_id
        mdl_course_id = ta.mdlcourse_id
        mdl_quiz_id = ta.mdlquiz_id
        foss_grades = {}
        quiz_grade = MdlQuizGrades.objects.using('moodle').filter(userid=mdl_user_id , quiz=mdl_quiz_id)
        spk_mdl_course_map = FossMdlCourses.objects.using('spk').get(mdlcourse_id=mdl_course_id)
        #spk_foss = FossCategory.objects.using('spk').get(id=spk_mdl_course_map.foss_id)
    #phone
    
    #address
    #academic id
    #spk user id
    #spk gender
    #spk score
def student_homepage(request):
    context={}
    #student = RecStudent.objects.get(user_id=request.user.id)
    #applied_jobs = AppliedJob.objects.filter(student_id=student.id)
    # get student grades
    #spk_student = SpkStudent.objects.filter(user_id=request.user.id) 
    spk_student = SpkStudent.objects.using('spk').filter(user_id=1055).get() 
    id = spk_student.id
    test_attendance_entries = TestAttendance.objects.using('spk').filter( student_id = spk_student.id)
    for ta in test_attendance_entries :
        mdl_user_id = ta.mdluser_id
        mdl_course_id = ta.mdlcourse_id
        mdl_quiz_id = ta.mdlquiz_id
        quiz_grade = MdlQuizGrades.objects.using('moodle').filter(userid=mdl_user_id , quiz=mdl_quiz_id)
        spk_mdl_course_map = FossMdlCourses.objects.using('spk').get(mdlcourse_id=mdl_course_id)
        spk_foss = FossCategory.objects.using('spk').get(id=spk_mdl_course_map.foss_id)
    return render(request,'emp/student_homepage.html',context)

def employer_homepage(request):
    context={}
    return render(request,'emp/employer_homepage.html',context)



def manager_homepage(request):
    context={}
    return render(request,'emp/manager_homepage.html',context)

def handlelogout(request):
    logout(request)
    return redirect('index')

def index(request):
     context={}
     return render(request,'emp/index.html',context)
