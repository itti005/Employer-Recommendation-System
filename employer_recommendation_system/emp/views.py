from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .models import *
from emp.models import Student as RecStudent
#from moodle.models import *
from spoken.models import TestAttendance, FossMdlCourses,FossCategory,Profile
from moodle.models import MdlQuizGrades

#from events.models import TestAttendance,FossMdlCourses
from django.views.generic.edit import UpdateView
#from events.models import Student as SpkStudent 
from spoken.models import Student as SpkStudent 
#from events.models import User as SpkUser 
from spoken.models import User as SpkUser 
#from creation.models import FossCategory 
from django.views.generic import FormView
from emp.forms import StudentGradeFilterForm
class StudentUpdateView(UpdateView):
    model = Student
    fields = ['education','skills','about','experience','github','linkedin','cover_letter'] 
    
def fetch_spk_student_data():
    user = User.objects.get(id=1)
    #spk_student_id = user.student.spk_usr_id
    spk_student = SpkStudent.objects.using('spk').get(id=user.student.spk_usr_id )
    #spk_user = SpkUser.objects.using('spk').get(id=spk_student.user_id) 
    test_attendance_entries = TestAttendance.objects.using('spk').filter( student_id = spk_student_id)
    print("1")
    foss_grades_dict = {}
    for ta in test_attendance_entries :
        #mdl_user_id = ta.mdluser_id
        mdl_user_id = 317 
        #mdl_course_id = ta.mdlcourse_id
        #mdl_quiz_id = ta.mdlquiz_id
        foss_grades = {}
        print(mdl_user_id,mdl_quiz_id)
        quiz_grade = MdlQuizGrades.objects.using('moodle').filter(userid=mdl_user_id , quiz=ta.mdlquiz_id)
        print(quiz_grade.get().grade)
        spk_mdl_course_map = FossMdlCourses.objects.using('spk').get(mdlcourse_id=ta.mdlcourse_id)
        spk_foss = FossCategory.objects.using('spk').get(id=spk_mdl_course_map.foss_id)
        print(f'spk foss : {spk_foss.foss}')
        foss_grades_dict[spk_foss.foss] = quiz_grade.get().grade
        print(foss_grades_dict)
    #phone
    rec_student = RecStudent.objects.get(user_id=user.id)
    #spk_student_profile = Profile.objects.using('spk').get(user_id=spk_user.id) 
    spk_student_profile = Profile.objects.using('spk').values('city__name','location__name','district__name','state__name','phone','address').get(user_id=1054)

    #print(spk_student_profile['phone'])
    print(spk_student_profile)
    rec_student.phone = spk_student_profile['phone'] 
    rec_student.address = spk_student_profile['address'] 
    rec_student.city = spk_student_profile['city__name'] 
    rec_student.location = spk_student_profile['location__name'] 
    rec_student.district = spk_student_profile['district__name'] 
    rec_student.state = spk_student_profile['state__name'] 
    rec_student.gender = spk_student.gender
    rec_student.save()
    print(rec_student.phone)

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

#class StudentGradeFilter(UserPassesTestMixin, FormView):
class StudentGradeFilter(FormView):
    template_name = 'emp/student_grade_filter.html'
    form_class = StudentGradeFilterForm
    success_url = '/student_grade_filter' 

