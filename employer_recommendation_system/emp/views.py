from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .models import *
from emp.models import Student as RecStudent
from spoken.models import TestAttendance, FossMdlCourses,FossCategory,Profile, SpokenState, SpokenCity
from moodle.models import MdlQuizGrades
from django.views.generic.edit import UpdateView
from spoken.models import SpokenStudent 
from spoken.models import SpokenUser as SpkUser 
from django.views.generic import FormView
from emp.forms import StudentGradeFilterForm, EducationForm,StudentForm,DateInput
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView,UpdateView,ModelFormMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
from .filterset import CompanyFilterSet,JobFilter
from .forms import ACTIVATION_STATUS
import numpy as np


APPLIED_SHORTLISTED = 1 # student has applied & is eligible for job
APPLIED_REJECTED = 0 # student has applied but is not eligible for job

def get_recommended_jobs(student):
    rec_jobs = []
    student_foss = set([ x['foss'] for x in fetch_student_scores(student)])
    jobs = get_awaiting_jobs(student.spk_usr_id)
    for job in jobs:
        if not student_foss.isdisjoint(set(map(int, job.foss.split(',')))):
            rec_jobs.append(job)
    return rec_jobs

#function to get student spoken test scores
def fetch_student_scores(student):  #parameter : recommendation student obj
	scores = []
	#student = Student.objects.get(id=2) #TEMPORARY
	spk_user = student.spk_usr_id
	try:
		spk_student = SpokenStudent.objects.get(user=spk_user)
		testattendance = TestAttendance.objects.values('mdluser_id').filter(student=spk_student)
		mdl_grades = MdlQuizGrades.objects.using('moodle').filter(userid=testattendance[0]['mdluser_id']) #fetch all rows with mdl_course & grade
		for item in mdl_grades: #map above mdl_course with foss from fossmdlcourse
			try:
				foss_mdl_courses = FossMdlCourses.objects.get(mdlquiz_id=item.quiz)
				foss = foss_mdl_courses.foss
				scores.append({'foss':foss.id,'name':foss.foss,'grade':item.grade,'quiz':item.quiz,'mdl':item})
			except FossMdlCourses.DoesNotExist as e:
				print(e)
	except SpokenStudent.DoesNotExist as e:
		print(e)
	except IndexError as e:
		print(e)
	return scores


def get_applied_joblist(spk_user_id):
	return JobShortlist.objects.filter(spk_user=spk_user_id,status__in=[APPLIED_SHORTLISTED,APPLIED_REJECTED])

def get_awaiting_jobs(spk_user_id):  #Jobs for which the student has not yet applied
	all_jobs = Job.objects.all()
	applied_jobs = [x.job for x in get_applied_joblist(spk_user_id)]
    # return set(all_jobs)-set(applied_jobs)
	return list(set(all_jobs)-set(applied_jobs))

def student_homepage(request):
    context={}

    # Top 5 jobs & company to display on student homepage
    company_display = Company.objects.filter(rating=5).order_by('-date_updated')[:5]
    context['company_display']=company_display
    rec_student = Student.objects.get(user=request.user)
    context['applied_jobs'] = get_applied_joblist(rec_student.spk_usr_id)
    context['awaiting_jobs'] = get_awaiting_jobs(rec_student.spk_usr_id)[:5]
    context['APPLIED_SHORTLISTED']=APPLIED_SHORTLISTED
    context['rec_jobs']=get_recommended_jobs(rec_student)

    
    try:
         spk_student = SpokenStudent.objects.using('spk').filter(user_id=rec_student.spk_usr_id).get()
         id = spk_student.id
         test_attendance_entries = TestAttendance.objects.using('spk').filter( student_id = spk_student.id)
         for ta in test_attendance_entries :
             mdl_user_id = ta.mdluser_id
             mdl_course_id = ta.mdlcourse_id
             mdl_quiz_id = ta.mdlquiz_id
             quiz_grade = MdlQuizGrades.objects.using('moodle').filter(userid=mdl_user_id , quiz=mdl_quiz_id)
             spk_mdl_course_map = FossMdlCourses.objects.using('spk').get(mdlcourse_id=mdl_course_id)
             spk_foss = FossCategory.objects.using('spk').get(id=spk_mdl_course_map.foss_id)
    except:
        print('failed')
    scores = fetch_student_scores(rec_student)
    context['scores']=scores
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

#Not required now
class StudentGradeFilter(FormView):
    template_name = 'emp/student_grade_filter.html'
    form_class = StudentGradeFilterForm
    success_url = '/student_grade_filter' 

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        if form.is_valid:
            foss = [x for x in form.cleaned_data['foss']]
            state = [s for s in form.cleaned_data['state']]
            city = [c for c in form.cleaned_data['city']]
            grade = form.cleaned_data['grade']
            activation_status = form.cleaned_data['activation_status']
            institution_type = [t for t in form.cleaned_data['institution_type']]
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            result=self.filter_student_grades(foss, state, city, grade, institution_type, activation_status, from_date, to_date)

        else:
            pass
        return self.render_to_response(self.get_context_data(form=form, result=result))

    def filter_student_grades(self, foss=None, state=None, city=None, grade=None, institution_type=None, activation_status=None, from_date=None, to_date=None):
        if grade:
            try:
                #get the moodle id for the foss
                fossmdl=FossMdlCourses.objects.using('spk').filter(foss__in=foss)
                #get moodle user grade for a specific foss quiz id having certain grade
                user_grade=MdlQuizGrades.objects.using('moodle').values_list('userid', 'quiz', 'grade').filter(quiz__in=[f.mdlquiz_id for f in fossmdl], grade__gte=int(grade))
                #convert moodle user and grades as key value pairs
                dictgrade = {i[0]:{i[1]:[i[2],False]} for i in user_grade}
                #get all test attendance for moodle user ids and for a specific moodle quiz ids
                test_attendance=TestAttendance.objects.using('spk').filter(
                    mdluser_id__in=list(dictgrade.keys()),
                    mdlquiz_id__in=[f.mdlquiz_id for f in fossmdl],
                    test__academic__state__in=state if state else SpokenState.objects.using('spk').all(),
                    test__academic__city__in=city if city else SpokenCity.objects.using('spk').all(),
                    status__gte=3, 
                    test__academic__institution_type__in=institution_type if institution_type else InstituteType.objects.using('spk').all(), 
                    test__academic__status__in=[activation_status] if activation_status else [1,3]
                    )

                if from_date and to_date:
                    test_attendance = test_attendance.filter(test__tdate__range=[from_date, to_date])
                elif from_date:
                    test_attendance = test_attendance.filter(test__tdate__gte=from_date)
                filter_ta=[]
                filter_user_id=''
                for i in range(test_attendance.count()):
                    if not dictgrade[test_attendance[i].mdluser_id][test_attendance[i].mdlquiz_id][1]:
                        dictgrade[test_attendance[i].mdluser_id][test_attendance[i].mdlquiz_id][1] = True
                        filter_ta.append(test_attendance[i])
                        filter_user_id+=str(test_attendance[i].student.user.id) +','
               
                return {'mdl_user_grade': dictgrade, 'test_attendance': filter_ta, "count":len(filter_ta),"filter_user_id":filter_user_id[:-1]}
            except FossMdlCourses.DoesNotExist:
                return None
        return None
def get_state_city_lst():
    states = SpokenState.objects.all()
    cities = SpokenCity.objects.all()
    return states, cities
#---------------- CBV for Create, Detail, List, Update for Company starts ----------------#

class CompanyCreate(PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    template_name = 'emp/employer_form.html'
    permission_required = 'emp.add_company'
    model = Company
    fields = ['name','emp_name','emp_contact','state_c','city_c','address','phone','email','logo','description','domain','company_size','website','rating','status'] 
    success_message ="%(company_name)s was created successfully"
    def get_success_url(self):
        return reverse('company-detail', kwargs={'slug': self.object.slug})
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.added_by = self.request.user
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)
    def test_func(self):
        return self.request.user.groups
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        state,city = get_state_city_lst()
        context['state']=state
        context['city']=city
        return context
    def form_invalid(self, form):
        print(f"form.errors ------------------- : {form.errors}")
        return self.render_to_response(self.get_context_data(form=form))



class CompanyDetailView(PermissionRequiredMixin,DetailView):
    template_name = 'emp/employer_detail.html'
    permission_required = 'emp.view_company'
    model = Company
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CompanyListView(PermissionRequiredMixin,ListView):
    template_name = 'emp/employer_list.html'
    permission_required = 'emp.view_company'
    model = Company
    filterset_class = CompanyFilterSet
    paginate_by = 2
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

class CompanyUpdate(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    template_name = 'emp/employer_update_form.html'
    permission_required = 'emp.change_company'
    model = Company
    fields = ['name','emp_name','emp_contact','state_c','city_c','address','phone','email','logo','description','domain','company_size','website'] 
    success_message ="%(name)s was updated successfully"
#---------------- CBV for Create, Detail, List, Update for Jobs starts ----------------#
class JobCreate(PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    template_name = 'emp/jobs_form.html'
    permission_required = 'emp.add_job'
    model = Job
    fields = ['company','title','designation','state_job','city_job','skills','description','domain','salary_range_min',
    'salary_range_max','job_type','benefits','requirements','shift_time','key_job_responsibilities','gender',
    'last_app_date','rating','foss','grade','activation_status','from_date','to_date','state','city','institute_type','status']
    success_message ="%(title)s job was created successfully"
    def get_success_url(self):
        return reverse('job-detail', kwargs={'slug': self.object.slug})
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)

    def get_form(self):
        form = super(JobCreate, self).get_form()
        form.fields['last_app_date'].widget = DateInput()
        form.fields['from_date'].widget = DateInput()
        form.fields['to_date'].widget = DateInput()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get data for filters
        filter_form = StudentGradeFilterForm()
        state,city = get_state_city_lst()
        context['state']=state
        context['city']=city
        context['filter_form']=filter_form
        return context

class JobDetailView(DetailView):
    template_name = 'emp/jobs_detail.html'
    model = Job
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class JobListView(ListView):
    template_name = 'emp/jobs_list.html'
    model = Job
    filterset_class = JobFilter
    paginate_by = 2
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['a']='ab'
        context['filterset'] = self.filterset
        return context
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

class AppliedJobListView(ListView):
    template_name = 'emp/applied_jobs_list.html'
    model = JobShortlist
    paginate_by = 2
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['APPLIED_SHORTLISTED']=APPLIED_SHORTLISTED
        return context

class JobUpdate(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    template_name = 'emp/jobs_update_form.html'
    permission_required = 'emp.change_job'
    model = Job
    fields = ['company','title','designation','state_job','city_job','skills','description','domain',
    'salary_range_min','salary_range_max','job_type','benefits','requirements','shift_time','key_job_responsibilities',
    'gender','state','city','from_date','to_date','activation_status','status']
    success_message ="%(title)s was updated successfully"

def add_education(student,degree,institute,start_year,end_year,gpa):
    degree_obj = Degree.objects.get(id=degree)
    institute_obj = AcademicCenter.objects.get(id=institute)
    ed = Education.objects.create()
    ed.degree = degree_obj
    ed.institute = institute_obj
    ed.start_year = start_year
    ed.end_year = end_year
    ed.gpa = gpa
    ed.save()
    student.education.add(ed)

def save_student_profile(request,student):
    student_form = StudentForm(request.POST)
    education_form = EducationForm(request.POST)
    if student_form.is_valid() and education_form.is_valid():
        student.about = student_form.cleaned_data['about']
        student.github = student_form.cleaned_data['github']
        student.experience = student_form.cleaned_data['experience']
        student.linkedin = student_form.cleaned_data['linkedin']
        #student.spk_institute = student_form.cleaned_data['spk_institute']
        student.save()
        skills = request.POST['skills_m']
        if skills:
            skills = skills.split(',')
            for item in skills:
                s = Skill.objects.get(name=item)
                student.skills.add(s)
        degree = request.POST['degree']
        degree_obj = Degree.objects.get(id=degree)
        institute = request.POST['institute']
        #institute_obj = AcademicCenter.objects.get(id=institute)
        start_year = education_form.cleaned_data['start_year']
        end_year = education_form.cleaned_data['end_year']
        gpa = education_form.cleaned_data['gpa']
        education = Education(degree=degree_obj,institute=institute,start_year=start_year,end_year=end_year,gpa=gpa)
        for i in range(1,6):
            try:
                degree = request.POST['degree_'+str(i)]
                institute = request.POST['institute_'+str(i)]
                start_year = request.POST['start_year_'+str(i)]
                end_year = request.POST['end_year_'+str(i)]
                gpa = request.POST['gpa_'+str(i)]
                add_education(student,degree,institute,start_year,end_year,gpa)
            except Exception as e:
                print(e)

        education.save()
        student.education.add(education)
        return student_form,education_form

def student_profile_confirm(request,pk,job):
    context = {}
    context['confirm']=True
    context['job_id']=job
    job_obj = Job.objects.get(id=job)
    context['job']=job_obj
    student = Student.objects.get(user=request.user)
    context['student']=student
    if request.method=='POST':
        student_form,education_form = save_student_profile(request,student)
    else:
        student_form = StudentForm(instance = student)
        education_form = EducationForm()
    context['form']=student_form
    context['education_form']=education_form
    return render(request,'emp/student_form.html',context)


def student_profile(request,pk):
    context = {}
    student = Student.objects.get(user=request.user)
    context['student']=student
    context['skills']=Skill.objects.all()
    if request.method=='POST':
        student_form,education_form = save_student_profile(request,student)
    else:
        student_form = StudentForm(instance = student)
        education_form = EducationForm()
    context['form']=student_form
    context['education_form']=education_form
    institutes = AcademicCenter.objects.values('id','institution_name')
    context['institutes'] = institutes
    return render(request,'emp/student_form.html',context)

def fetch_education_data(request):
    institutes = AcademicCenter.objects.all().values()
    degrees = Degree.objects.all().values()
    data = {}
    data['institutes']=list(institutes)
    data['degrees']=list(degrees)
    return JsonResponse(data)

def shortlist(request):
    data = {'msg':'success'}
    user_ids = request.GET.get('user_ids', None)
    job_id = int(request.GET.get('job_id', None))
    job = Job.objects.get(id=job_id)
    user_list = user_ids.split(',')
    l = []
    for item in user_list: 
        l.append(JobShortlist(job=job, spk_user_id=int(item),status=1))
    JobShortlist.objects.bulk_create(l)
    return JsonResponse(data) 

def update_job_app_status(spk_user_id,job,flag):
	#if flag == True : status:1 -> student eligible for job
	#if flag == False : status:0 -> student has applied & is not eligible for job
	if flag:
		job_shortlist = JobShortlist.objects.create(job=job,spk_user_id=spk_user_id,status=APPLIED_SHORTLISTED) #student has applied & is eligible for job
	else:
		job_shortlist = JobShortlist.objects.create(job=job,spk_user_id=spk_user_id,status=APPLIED_REJECTED) #student has applied & is not eligible for job
	return True
	
class JobShortlistListView(PermissionRequiredMixin,ListView):
    permission_required = 'emp.view_job'
    model = JobShortlist
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = Job.objects.get(id=self.kwargs['id'])
        context['job']=job
        return context

    def get_queryset(self):
        id = self.kwargs['id']
        l = JobShortlist.objects.filter(job_id=id)
        return l

def add_student_job_status(request):
    spk_user_id = int(request.GET.get('spk_user_id'))
    job_id = int(request.GET.get('job_id'))
    job = Job.objects.get(id=job_id)
    flag = True
    r=update_job_app_status(spk_user_id,job,flag)
    data = {'msg':True}
    return JsonResponse(data)

def check_student_eligibilty(request):
    # spk_user_id = int(request.GET.get('spk_user_id', None))
    flag = False
    spk_user_id = int(request.GET.get('spk_user_id'))
    job_id = int(request.GET.get('job_id'))
    data = {}
    spk_user = SpokenUser.objects.get(id=spk_user_id)     
    student = SpokenStudent.objects.get(user=spk_user)    
    job_id=job_id   
    
    job = Job.objects.get(id=job_id)   #get Job object
    state = list(map(lambda x : int(x),job.state.split(',')))
    city = list(map(lambda x : int(x),job.city.split(',')))
    institution_type = list(map(lambda x : int(x),job.institute_type.split(',')))
    activation_status = job.activation_status
    grade = job.grade
    foss_list = list(map(lambda x : int(x),job.foss.split(',')))
    #get quiz_list for all above fosses
    filter_quiz_ids = []
    for foss in foss_list:
    	try:
    		quiz = FossMdlCourses.objects.get(foss=foss).mdlquiz_id
    		filter_quiz_ids.append(quiz)
    	except FossMdlCourses.DoesNotExist as e:
    		print(e)
    try:
        # filter_quiz_ids = list(map(lambda x:FossMdlCourses.objects.get(foss=x).mdlquiz_id,foss_list))
        #get mdl_user from testattendance
        ta = TestAttendance.objects.values('mdluser_id','mdlcourse_id','mdlquiz_id').filter(student=student,mdlquiz_id__in=filter_quiz_ids,status__gte=3)
        # ta = TestAttendance.objects.values('mdluser_id','mdlcourse_id','mdlquiz_id').filter(student=student,mdlquiz_id__in=filter_quiz_ids)
        # print(f'type ta[0].mdlquiz_id: {type(ta[0]['mdlquiz_id'])}')
        ta_quiz_ids = [ x['mdlquiz_id'] for x in ta]
        if(set(filter_quiz_ids))==set(ta_quiz_ids):
            #check grade criteria
            mdl_user_id = TestAttendance.objects.filter(student=student)[0].mdluser_id
            mdl_quiz_grades = MdlQuizGrades.objects.using('moodle').filter(userid=mdl_user_id,grade__gte=grade,quiz__in=filter_quiz_ids)
            mdl_quiz_grades_ids = [ x.quiz for x in mdl_quiz_grades]
            if(sorted(set(mdl_quiz_grades_ids))==sorted(set(filter_quiz_ids))):
                #check other remaining criteria
                test_attendance=TestAttendance.objects.filter(
                        student=student,
                        mdlquiz_id__in=filter_quiz_ids,
                        test__academic__state__in=state if state else SpokenState.objects.using('spk').all(),
                        test__academic__city__in=city if city else SpokenCity.objects.using('spk').all(), 
                        test__academic__institution_type__in=institution_type if institution_type else InstituteType.objects.using('spk').all(), 
                        test__academic__status__in=[activation_status] if activation_status else [1,3]
                        )
                ta_quizes = [ ta.mdlquiz_id for ta in test_attendance]
                if(sorted(set(ta_quizes))==sorted(set(filter_quiz_ids))):
                    flag = True
                    data['is_eligible'] = flag
                    return JsonResponse(data)

    except IndexError as e:
        print(e)

    data['is_eligible'] = flag
    update_job_app_status(spk_user_id,job,flag)
    return JsonResponse(data)