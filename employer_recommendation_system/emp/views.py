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
    try:
        user = User.objects.get(id=10)
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
    except Content.DoesNotExist:
        print("fetch except")

    
def student_homepage(request):
    context={}
    #student = RecStudent.objects.get(user_id=request.user.id)
    #applied_jobs = AppliedJob.objects.filter(student_id=student.id)
    # get student grades
    #spk_student = SpkStudent.objects.filter(user_id=request.user.id) 
    try:
         spk_student = SpkStudent.objects.using('spk').filter(user_id=10550).get() 
         id = spk_student.id
         test_attendance_entries = TestAttendance.objects.using('spk').filter( student_id = spk_student.id)
         for ta in test_attendance_entries :
             mdl_user_id = ta.mdluser_id
             mdl_course_id = ta.mdlcourse_id
             mdl_quiz_id = ta.mdlquiz_id
             quiz_grade = MdlQuizGrades.objects.using('moodle').filter(userid=mdl_user_id , quiz=mdl_quiz_id)
             spk_mdl_course_map = FossMdlCourses.objects.using('spk').get(mdlcourse_id=mdl_course_id)
             spk_foss = FossCategory.objects.using('spk').get(id=spk_mdl_course_map.foss_id)
    except Content.DoesNotExist:
        print("student_homepage failed")

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

    
    def test_func(self):
        print("*********** test_func ")
        return self.request.user.is_superuser

    def form_valid(self, form):
        if form.is_valid:
            print("*********** form is valid ")
            foss = [x for x in form.cleaned_data['foss']]
            state = [s for s in form.cleaned_data['state']]
            city = [c for c in form.cleaned_data['city']]
            grade = form.cleaned_data['grade']
            activation_status = form.cleaned_data['activation_status']
            institution_type = [t for t in form.cleaned_data['institution_type']]
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            result=self.filter_student_grades(foss, state, city, grade, institution_type, activation_status, from_date, to_date)
            print(f'RESULT --------- {result}')
        else:
            print("********* form is not valid ")
        return self.render_to_response(self.get_context_data(form=form, result=result))

    def filter_student_grades(self, foss=None, state=None, city=None, grade=None, institution_type=None, activation_status=None, from_date=None, to_date=None):
        print("*********** filter_student_grades ")
        if grade:
            try:
                #get the moodle id for the foss
                fossmdl=FossMdlCourses.objects.using('spk').filter(foss__in=foss)
                #get moodle user grade for a specific foss quiz id having certain grade
                user_grade=MdlQuizGrades.objects.using('moodle').values_list('userid', 'quiz', 'grade').filter(quiz__in=[f.mdlquiz_id for f in fossmdl], grade__gte=int(grade))
                #convert moodle user and grades as key value pairs
                dictgrade = {i[0]:{i[1]:[i[2],False]} for i in user_grade}
                print(list(dictgrade.keys()))
                #get all test attendance for moodle user ids and for a specific moodle quiz ids
                test_attendance=TestAttendance.objects.using('spk').filter(
                    mdluser_id__in=list(dictgrade.keys()),
                    mdlquiz_id__in=[f.mdlquiz_id for f in fossmdl],
                    test__academic__state__in=state if state else State.objects.using('spk').all(),
                    test__academic__city__in=city if city else City.objects.using('spk').all(),
                    status__gte=3, 
                    test__academic__institution_type__in=institution_type if institution_type else InstituteType.objects.using('spk').all(), 
                    test__academic__status__in=[activation_status] if activation_status else [1,3]
                    )
                print("################################")
                print(test_attendance)

                if from_date and to_date:
                    test_attendance = test_attendance.filter(test__tdate__range=[from_date, to_date])
                elif from_date:
                    test_attendance = test_attendance.filter(test__tdate__gte=from_date)
                filter_ta=[]

                for i in range(test_attendance.count()):
                    print("here")
                    if not dictgrade[test_attendance[i].mdluser_id][test_attendance[i].mdlquiz_id][1]:
                        dictgrade[test_attendance[i].mdluser_id][test_attendance[i].mdlquiz_id][1] = True
                        filter_ta.append(test_attendance[i])
                return {'mdl_user_grade': dictgrade, 'test_attendance': filter_ta, "count":len(filter_ta)}
            except FossMdlCourses.DoesNotExist:
                return None
        return None

