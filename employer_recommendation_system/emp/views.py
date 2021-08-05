from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .models import *
from emp.models import Student as RecStudent
from spoken.models import TestAttendance, FossMdlCourses,FossCategory,Profile, SpokenState, SpokenCity, InstituteType
from moodle.models import MdlQuizGrades,MdlUser
from django.views.generic.edit import UpdateView
from spoken.models import SpokenStudent 
from spoken.models import SpokenUser as SpkUser 
from django.views.generic import FormView
from emp.forms import StudentGradeFilterForm, EducationForm,StudentForm,DateInput,PrevEducationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView,UpdateView,ModelFormMixin,FormMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin,UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from .filterset import CompanyFilterSet,JobFilter
from .forms import ACTIVATION_STATUS, JobSearchForm, JobApplicationForm
import numpy as np
from django.db.models import Q,F,ExpressionWrapper,CharField
from django.db.models.expressions import RawSQL
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings
from django.forms import HiddenInput
from django.template.defaultfilters import slugify
from django import forms
import pandas as pd
import json
from django.core.files.storage import FileSystemStorage
from os import listdir
import re
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.utils.functional import wraps
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied,MultipleObjectsReturned,ObjectDoesNotExist
from django.http import FileResponse, Http404
from .send_mail_students import send_mail_shortlist
import time
import itertools
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Concat
from django.db.models import Value
from .models import STATUS
# STATUS = {'ACTIVE' :1,'INACTIVE' :0}

APPLIED = 0 # student has applied but not yet shortlisted by HR Manager
APPLIED_SHORTLISTED = 1 # student has applied & shortlisted by HR Manager

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


# test functions to limit access to pages start
def is_student(user):
    b = settings.ROLES['STUDENT'][1] in [x.name for x in user.groups.all()]
    return settings.ROLES['STUDENT'][1] in [x.name for x in user.groups.all()]

def is_manager(user):
    b = settings.ROLES['MANAGER'][1] in [x.name for x in user.groups.all()]
    return settings.ROLES['MANAGER'][1] in [x.name for x in user.groups.all()]

def check_student(view_func):
    @wraps(view_func)
    def inner(request,pk, *args, **kwargs):
        if request.user.student.id!=int(pk):
            raise PermissionDenied()
        return view_func(request,pk, *args, **kwargs)
    return inner

def check_student_job(view_func):
    @wraps(view_func)
    def inner(request,pk,job, *args, **kwargs):
        student = request.user.student
        job_obj = Job.objects.get(id=job)
        jobs = get_recommended_jobs(student)
        if student.id!=int(pk) or not job_obj in jobs:
            raise PermissionDenied()
        return view_func(request,pk,job, *args, **kwargs)
    return inner

def check_user(view_func):
    @wraps(view_func)
    def inner(request,pk, *args, **kwargs):
        if request.user.id!=int(pk):
            raise PermissionDenied()
        return view_func(request,pk, *args, **kwargs)
    return inner
# test functions to limit access to pages ends
def access_profile(view_func):
    @wraps(view_func)
    def inner(request,id,job, *args, **kwargs):
        if is_manager(request.user):
            return view_func(request,id,job, *args, **kwargs)
        if is_student(request.user):
            rec_jobs = get_recommended_jobs(request.user.student)
            try:
                job_obj = Job.objects.get(id=job)
                if job_obj in rec_jobs and request.user.student.spk_usr_id==int(id):
                    return view_func(request,id,job, *args, **kwargs)
            except:
                raise PermissionDenied()
        raise PermissionDenied()
    return inner

@check_user
def document_view(request,pk):
    try:
        file_type = request.GET["type"]
        file = os.path.join('media','students',str(request.user.id),file_type+str(request.user.id)+'.pdf')
        return FileResponse(open(file, 'rb'), content_type='application/pdf')
        # return FileResponse(open('media/students/18/cover_letter18.pdf', 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()

#show job application status to HR
def get_job_app_status(job):
    job_shortlist = JobShortlist.objects.filter(job=job)



def get_recommended_jobs(student):
    #get jobs having status 0 & last app submission date greater than equal to today
    jobs = Job.objects.filter(last_app_date__gte=datetime.datetime.now(),status=STATUS['ACTIVE'])
    applied_jobs = [x.job for x in get_applied_joblist(student.spk_usr_id)]
    jobs = [x for x in jobs if x not in applied_jobs ]
    scores = fetch_student_scores(student)
    if scores:
        mdl_user_id = scores[0]['mdl'].userid
    student_foss = [d['foss'] for d in scores]  #fosses for which student grade is available
    rec_jobs = []
    spk_student = SpokenStudent.objects.get(user_id=student.spk_usr_id)
    count = 1
    for job in jobs:
        fosses = list(map(int,job.foss.split(',')))
        if job.state and job.state!='0':
            states = list(map(int,job.state.split(',')))
        else:
            states = ''
        if job.city and job.city!='0':
            cities = list(map(int,job.city.split(',')))
        else:
            cities = ''
        # cities = '' if job.city=='0' else list(map(int,job.city.split(',')))
        # insti_type = '' if job.institute_type=='0' else list(map(int,job.institute_type.split(',')))
        if job.institute_type and job.institute_type!='0':
            insti_type = list(map(int,job.institute_type.split(',')))
        else:
            insti_type = ''
        valid_fosses = [   d['foss'] for d in scores if str(d['foss']) in job.foss and int(d['grade'])>=job.grade]
        if valid_fosses:
            mdl_quiz_ids = [x.mdlquiz_id for x in FossMdlCourses.objects.filter(foss_id__in=valid_fosses)] #Student passes 1st foss & grade criteria
            mdluser_id = TestAttendance.objects.filter(student=spk_student).first().mdluser_id
            # test_attendance = TestAttendance.objects.filter(student=spk_student, 
            test_attendance = TestAttendance.objects.filter(mdluser_id=mdluser_id, 
                                                mdlquiz_id__in=mdl_quiz_ids,
                                                test__academic__state__in=states if states!='' else SpokenState.objects.all(),
                                                test__academic__city__in=cities if cities!='' else SpokenCity.objects.all(),
                                                status__gte=3,
                                                test__academic__institution_type__in=insti_type if insti_type!='' else InstituteType.objects.all(),
                                                test__academic__status__in=[job.activation_status] if job.activation_status else [1,3],
                                                )
            if job.from_date and job.to_date:
                test_attendance = test_attendance.filter(test__tdate__range=[job.from_date, job.to_date])
            elif job.from_date:
                test_attendance = test_attendance.filter(test__tdate__gte=job.from_date)
            if test_attendance:
                rec_jobs.append(job)
        else:
            pass
        count+=1
    return rec_jobs

#function to get student spoken test scores; returns list of dictionary of foss & scores
def fetch_student_scores(student):  #parameter : recommendation student obj
    scores = []
    #student = Student.objects.get(id=2) #TEMPORARY
    spk_user = student.spk_usr_id
    try:
        spk_student = SpokenStudent.objects.get(user=spk_user)
        testattendance = TestAttendance.objects.values('mdluser_id').filter(student=spk_student)
        mdl_grades = MdlQuizGrades.objects.using('moodle').filter(userid=testattendance[0]['mdluser_id']) #fetch all rows with mdl_course & grade
        count = 1
        for item in mdl_grades: #map above mdl_course with foss from fossmdlcourse
            try:
                foss_mdl_courses = FossMdlCourses.objects.get(mdlquiz_id=item.quiz)
                foss = foss_mdl_courses.foss
                scores.append({'foss':foss.id,'name':foss.foss,'grade':item.grade,'quiz':item.quiz,'mdl':item})
            except FossMdlCourses.DoesNotExist as e:
                print(e)
            except MultipleObjectsReturned:
                for foss_mdl_courses in FossMdlCourses.objects.filter(mdlquiz_id=item.quiz):
                    foss = foss_mdl_courses.foss
                    scores.append({'foss':foss.id,'name':foss.foss,'grade':item.grade,'quiz':item.quiz,'mdl':item})
            count+=1
    except SpokenStudent.DoesNotExist as e:
        print(e)
    except IndexError as e:
        print(e)
    return scores


def get_applied_joblist(spk_user_id):
    return JobShortlist.objects.filter(spk_user=spk_user_id,status__in=[APPLIED,APPLIED_SHORTLISTED])

def get_awaiting_jobs(spk_user_id):  #Jobs for which the student has not yet applied
    all_jobs = Job.objects.all().filter(rating=RATING['DISPLAY_ON_HOMEPAGE'],status=STATUS['ACTIVE'])
    if not all_jobs:
        all_jobs = Job.objects.all().filter(status=STATUS['ACTIVE'])
    applied_jobs = [x.job for x in get_applied_joblist(spk_user_id)]
    return list(set(all_jobs)-set(applied_jobs))

@user_passes_test(is_student)
def student_homepage(request):
    context={}
    # Top 5 jobs & company to display on student homepage
    company_display = Company.objects.filter(rating=RATING['DISPLAY_ON_HOMEPAGE'],status=STATUS['ACTIVE']).values('name','logo').order_by('date_updated')[:6]
    context['company_display']=company_display
    rec_student = Student.objects.get(user=request.user)
    applied_jobs = get_applied_joblist(rec_student.spk_usr_id)
    awaiting_jobs = get_awaiting_jobs(rec_student.spk_usr_id)
    rec_jobs = get_recommended_jobs(rec_student)
    context['applied_jobs'] = applied_jobs if len(applied_jobs)<4 else applied_jobs[:4]
    context['awaiting_jobs'] = awaiting_jobs if len(awaiting_jobs)<6 else awaiting_jobs[:6]
    l = awaiting_jobs if len(awaiting_jobs)<6 else awaiting_jobs[:6]
    context['APPLIED_SHORTLISTED']=APPLIED_SHORTLISTED
    context['rec_jobs'] = rec_jobs if len(applied_jobs)<3 else rec_jobs[:3]
    
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
    except Exception as e:
        print(e)
    scores = fetch_student_scores(rec_student)
    context['scores']=scores

    return render(request,'emp/student_homepage.html',context)

def employer_homepage(request):
    context={}
    return render(request,'emp/employer_homepage.html',context)

@user_passes_test(is_manager)
def manager_homepage(request):
    context={}
    return render(request,'emp/manager_homepage.html',context)

def handlelogout(request):
    logout(request)
    # return redirect('index')
    return redirect('login')

def index(request):
     context={}
     return render(request,'emp/index.html',context)

def get_state_city_lst():
    states = SpokenState.objects.all()
    cities = SpokenCity.objects.all()
    return states, cities
#---------------- CBV for Create, Detail, List, Update for Company starts ----------------#
def update_company_form(self,form):
    form.fields['name'].widget.attrs ={'placeholder': 'Company Name'}
    form.fields['domain'].queryset = Domain.objects.order_by('name')
    form.fields['rating'].widget = forms.Select(attrs=None, choices=COMPANY_RATING)
    # try:
    #     form.fields['job_type'].initial = JobType.objects.get(id=DEFAULT_JOB_TYPE)
    # except (JobType.DoesNotExist,MultipleObjectsReturned) as e:
    #     pass

    return form

class CompanyCreate(PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    template_name = 'emp/employer_form.html'
    permission_required = 'emp.add_company'
    model = Company
    fields = ['name','emp_name','emp_contact','state_c','city_c','address','email','logo','description','domain','company_size','website','rating','status'] 
    success_message ="%(name)s was created successfully"
    def get_success_url(self):
        obj = Company.objects.get(name=self.object.name,date_created=self.object.date_created)
        return reverse('company-detail', kwargs={'slug': obj.slug})
    
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.added_by = self.request.user
        self.object.save()
        messages.success(self.request, 'Company information added successfully.')
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
        return self.render_to_response(self.get_context_data(form=form))

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super(CompanyCreate, self).get_form(form_class)
        update_company_form(self,form)
        return form

class CompanyDetailView(DetailView):
    template_name = 'emp/employer_detail.html'
    model = Company
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_state = SpokenState.objects.filter(id=self.object.state_c).first()
        company_city = SpokenCity.objects.filter(id=self.object.city_c).first()
        context['company_state']=company_state.name if company_state else ''
        context['company_city']=company_city.name if company_city else ''
        return context

class CompanyListView(PermissionRequiredMixin,ListView):
    template_name = 'emp/employer_list.html'
    permission_required = 'emp.view_company'
    model = Company
    filterset_class = CompanyFilterSet
    # paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.collection
        context['form'] = self.collection.form
        context['companies'] = Company.objects.values_list('name')
        
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        self.collection = self.filterset_class(self.request.GET, queryset=queryset)
        return self.collection.qs.distinct()


class CompanyUpdate(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    template_name = 'emp/employer_update_form.html'
    permission_required = 'emp.change_company'
    model = Company
    fields = ['name','emp_name','emp_contact','state_c','city_c','address','email','logo','description','domain','company_size','website','status','rating'] 
    success_message ="%(name)s was updated successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['state']=SpokenState.objects.all()
        context['city']=SpokenCity.objects.all()
        return context

    def get_form(self):
        form = super(CompanyUpdate, self).get_form()
        form.fields['state_c'].widget = HiddenInput()
        form.fields['city_c'].widget = HiddenInput()
        update_company_form(self,form)
        return form

#---------------- CBV for Create, Detail, List, Update for Jobs starts ----------------#
def update_form_widgets(self,form):
    form.fields['last_app_date'].widget = DateInput()
    form.fields['from_date'].widget = DateInput()
    form.fields['to_date'].widget = DateInput()
    form.fields['rating'].widget = forms.Select(attrs=None, choices=JOB_RATING)
    form.fields['status'].widget = forms.Select(attrs=None, choices=JOB_STATUS)
    form.fields['company'].queryset = Company.objects.order_by('name')
    form.fields['domain'].queryset = Domain.objects.order_by('name')
    try:
        form.fields['job_type'].initial = JobType.objects.get(id=DEFAULT_JOB_TYPE)
    except (JobType.DoesNotExist,MultipleObjectsReturned) as e:
        pass

    return form

class JobCreate(PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    template_name = 'emp/jobs_form.html'
    permission_required = 'emp.add_job'
    model = Job
    fields = ['company','title','designation','state_job','city_job','skills','description','domain','salary_range_min',
    'salary_range_max','job_type','requirements','shift_time','key_job_responsibilities','gender',
    'last_app_date','rating','foss','grade','activation_status','from_date','to_date','state','city','institute_type','status','degree','discipline']
    success_message ="%(title)s job was created successfully"
    def get_success_url(self):
        obj = Job.objects.get(title=self.object.title,date_created=self.object.date_created)
        return reverse('job-detail', kwargs={'slug': obj.slug})
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # form.save()
        self.object.save()
        # self.save_degree(form)
        form.save_m2m()
        messages.success(self.request, 'Job information added successfully.')
        return super(ModelFormMixin, self).form_valid(form)

    def get_form(self):
        form = super(JobCreate, self).get_form()
        form = update_form_widgets(self,form)
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

class JobDetailView(PermissionRequiredMixin,DetailView):
    template_name = 'emp/jobs_detail.html'
    permission_required = 'emp.view_job'
    model = Job
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_url'] = settings.BASE_URL
        return context

class JobListView(FormMixin,ListView):
    template_name = 'emp/jobs_list.html'
    model = Job
    #filterset_class = JobFilter
    paginate_by = 8
    form_class = JobSearchForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_url']=settings.BASE_URL
        if self.request.user.groups.filter(name='STUDENT'):
            jobShortlist = JobShortlist.objects.filter(spk_user=self.request.user.student.spk_usr_id)
            job_short_list = get_applied_joblist(self.request.user.student.spk_usr_id)
            all_jobs = Job.objects.all()
            applied_jobs = [x.job for x in job_short_list]
            in_process_jobs = [x.job for x in job_short_list if x.status==JOB_APP_STATUS['RECEIVED_APP']]
            rejected_jobs = [x.job for x in job_short_list if x.status==JOB_APP_STATUS['REJECTED']]
            reccomended_jobs = get_recommended_jobs(self.request.user.student)
            context['applied_jobs'] = applied_jobs
            context['in_process_jobs'] = in_process_jobs
            context['rejected_jobs'] = rejected_jobs
            context['reccomended_jobs'] = reccomended_jobs
            eligible_jobs = reccomended_jobs+applied_jobs
            context['non_eligible_jobs'] = list(set(all_jobs).difference(set(eligible_jobs)))
        elif self.request.user.groups.filter(name='MANAGER'):
            context['grade_filter_url'] = settings.GRADE_FILTER
        return context
    def get_queryset(self):
        queryset = super().get_queryset()
        place = self.request.GET.get('place', '')
        keyword = self.request.GET.get('keyword', '')
        company = self.request.GET.get('company', '')
        job_id = self.request.GET.get('id', '')
        if job_id:
            queryset = Job.objects.filter(id=job_id)
            if is_manager(self.request.user):
                return queryset
            else:
                return queryset.filter(status=STATUS['ACTIVE'])
        queries =[place,keyword,company]
        if keyword or company or place:
            q_kw=q_place=q_com=Job.objects.all()
            if keyword:
                fossc = FossCategory.objects.filter(foss=keyword)
                if fossc:
                    foss_id = str(fossc[0].id)
                    l_kw = Job.objects.raw('select * from emp_job where find_in_set('+foss_id+',foss) <> 0')
                    q_kw = Job.objects.filter(id__in=[ job.id for job in l_kw])
                else:
                    q_kw = Job.objects.filter(title__icontains=keyword)
            if place:
                place = SpokenState.objects.filter(name=place) or SpokenCity.objects.filter(name=place)
                place_id = place[0].id
                q_place = Job.objects.filter(Q(state_job=place_id) | Q(city_job=place_id))
            if company:
                q_com = Job.objects.filter(company__name=company)
            queryset = (q_kw & q_place & q_com)
        if is_manager(self.request.user):
            return queryset
        else:
            return queryset.filter(status=STATUS['ACTIVE'])

class JobListingView(UserPassesTestMixin,ListView):
    template_name = 'emp/job_list_tabular.html'
    model = Job

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def test_func(self):
        return is_manager(self.request.user)

class JobUpdate(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    template_name = 'emp/jobs_update_form.html'
    permission_required = 'emp.change_job'
    model = Job
    fields = ['company','title','designation','state_job','city_job','skills','description','domain','salary_range_min',
    'salary_range_max','job_type','requirements','shift_time','key_job_responsibilities','gender',
    'last_app_date','rating','foss','grade','activation_status','from_date','to_date','state','city','institute_type','status','degree','discipline']
    success_message ="%(title)s was updated successfully"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get data for filters
        job = Job.objects.get(id=self.kwargs['slug'])
        context['state']=SpokenState.objects.all()
        context['city']=SpokenCity.objects.all()
        context['job']=job
        context['filter_foss']=list(map(int,job.foss.split(',')))
        filter_form = StudentGradeFilterForm({'foss':job.foss,'state':job.state,
            'city':job.city,'grade':job.grade,'institution_type':job.institute_type,
            'activation_status':job.activation_status,'from_date':job.from_date,'to_date':job.to_date})
        context['filter_form']=filter_form
        return context

    filter_form = StudentGradeFilterForm()

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        form.save()
        # self.object = form.save(commit=False)
        # self.object.save()
        messages.success(self.request, 'Job information updated successfully.')
        return super(ModelFormMixin, self).form_valid(form)

    def get_form(self):
        form = super(JobUpdate, self).get_form()
        form = update_form_widgets(self,form)
        return form

def add_education(student,degree,discipline,institute,start_year,end_year,gpa,order):
    def add_values(education,degree,discipline,institute,start_year,end_year,gpa,order):
        education.degree = degree if degree else None
        education.acad_discipline = discipline if discipline else None
        education.order = order
        if institute:
            print(f"institute 3 -------------- {institute}")
            education.institute = institute
        if start_year:
            education.start_year = start_year
        if end_year:
            education.end_year = end_year
        if gpa:
            education.gpa = gpa
        education.save()
        return education
    try:
        education = Education.objects.get(student=student,order=order)
        add_values(education,degree,discipline,institute,start_year,end_year,gpa,order)
    except Exception as e:
        if degree or discipline or institute or start_year or end_year or gpa:
            education = Education()
            edu=add_values(education,degree,discipline,institute,start_year,end_year,gpa,order)
            student.education.add(edu)


def save_prev_education(request,student):
    degree = request.POST.get('p_degree','')
    degree = Degree.objects.get(id=degree) if degree else None
    discipline = request.POST.get('p_discipline','')
    discipline = Discipline.objects.get(id=discipline) if discipline else None
    institute = request.POST.get('p_institute','')
    start_year = request.POST.get('p_start_year','')
    end_year = request.POST.get('p_end_year','')
    gpa = request.POST.get('p_gpa','')
    add_education(student,degree=degree,
        discipline = discipline,
        institute = institute,
        start_year = start_year, end_year = end_year,
        gpa = gpa , order=PAST_EDUCATION)


def save_education(edu_form,student):
    degree = edu_form.cleaned_data['degree']
    discipline = edu_form.cleaned_data['acad_discipline']
    institute = edu_form.cleaned_data['institute']
    start_year = edu_form.cleaned_data['start_year']
    end_year = edu_form.cleaned_data['end_year']
    gpa = edu_form.cleaned_data['gpa']
    add_education(student,degree=degree,
        discipline = discipline,
        institute = institute,
        start_year = start_year, end_year = end_year,
        gpa = gpa , order=CURRENT_EDUCATION)
    
def save_student_profile(request,student):    
    student_form = StudentForm(request.POST,request.FILES)
    c_education_form = EducationForm(request.POST)
        
    if student_form.is_valid() and c_education_form.is_valid():
        student.about = student_form.cleaned_data['about']
        student.github = student_form.cleaned_data['github']
        student.linkedin = student_form.cleaned_data['linkedin']
        student.alternate_email = student_form.cleaned_data['alternate_email']
        student.phone = student_form.cleaned_data['phone']
        student.address = student_form.cleaned_data['address']
        student.certifications = student_form.cleaned_data['certifications']
        
        # code for saving projects starts
        urls = request.POST.getlist('pr_url', '')
        descs = request.POST.getlist('pr_desc', '')
        projects = student.projects.all()
        for project in projects:
            student.projects.remove(project)
            project.delete()
        # urls = [x for x in urls if x!='']
        # descs = [x for x in descs if x!='']
        for (url,desc) in zip(urls,descs):
            if url or desc:
                project = Project.objects.create(url = url,desc = desc)
                student.projects.add(project)
        # code for saving projects ends

        # code for saving cover letter & resume starts
        try:
            location = settings.MEDIA_ROOT+'/students/'+str(request.user.id)+'/'
            os.makedirs(location)
        except:
            pass
        fs = FileSystemStorage(location=location) if location else FileSystemStorage()#defaults to   MEDIA_ROOT
        # fs = FileSystemStorage()#defaults to   MEDIA_ROOT
        l=listdir(location)
        try:
            if request.FILES['cover_letter']:
                re_c = re.compile("cover_letter.*")
                redundant_cover = list(filter(re_c.match, l))
                for file in redundant_cover :
                    os.remove(os.path.join(location,file))
                cover_letter = request.FILES['cover_letter']
                filename_cover_letter = 'cover_letter'+str(request.user.id)+'.pdf'
                filename_c = fs.save(filename_cover_letter, cover_letter)
                student.cover_letter=fs.url(os.path.join('students',str(request.user.id),filename_c))
        except MultiValueDictKeyError as e:
            print(e)
        try:
            if request.FILES['resume']:
                re_r = re.compile("resume.*")
                redundant_resume = list(filter(re_r.match, l))
                for file in redundant_resume:
                    os.remove(os.path.join(location,file))
                resume = request.FILES['resume']
                filename_resume = 'resume'+str(request.user.id)+'.pdf'
                filename_r = fs.save(filename_resume, resume)
                student.resume=fs.url(os.path.join('students',str(request.user.id),filename_r))
        except MultiValueDictKeyError as e:
            print(e)

        l = listdir(location)
        re_c = re.compile("cover_letter_.*")
        re_r = re.compile("resume_.*")
        redundant_cover = list(filter(re_c.match, l))
        redundant_resume = list(filter(re_r.match, l))
        for file in redundant_cover + redundant_resume:
            os.remove(os.path.join(location,file))
        # code for saving cover letter & resume ends
        student.save()
        save_education(c_education_form,student)
        save_prev_education(request,student)
    else:
        messages.error(request, 'Error in updating profile')
    return student_form,c_education_form
        
# @user_passes_test(is_student)
@check_student_job
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
        jobApplicationForm = JobApplicationForm()
    context['form']=student_form
    context['education_form']=education_form
    context['jobApplicationForm']=jobApplicationForm
    context['scores'] = fetch_student_scores(student)
    context['projects'] = student.projects.all()
    return render(request,'emp/student_form.html',context)

@check_student
def student_profile(request,pk):
    context = {}
    student = Student.objects.get(user=request.user)
    context['student']=student
    # context['skills']=Skill.objects.all()
    if request.method=='POST':
        student_form = StudentForm(request.POST)
        c_education_form = EducationForm(request.POST)
        if student_form.is_valid() and c_education_form.is_valid():
            student_form,education_form = save_student_profile(request,student)
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error in updating profile')
    else:
        student_form = StudentForm(instance = student)
    try:
        edu = Education.objects.get(student=student,order=CURRENT_EDUCATION)
        context['current_edu']=edu
        c_education_form = EducationForm(instance=edu)
    except:
        c_education_form = EducationForm(initial={'order': CURRENT_EDUCATION})
    try:
        p_edu = Education.objects.get(student=student,order=PAST_EDUCATION)
        context['past_edu']=p_edu
    except:
        p_education_form = EducationForm(initial={'order': PAST_EDUCATION})
    
    context['form']=student_form
    context['education_form'] = c_education_form
    context['institutes'] = AcademicCenter.objects.values('id','institution_name').order_by('institution_name')
    context['scores'] = fetch_student_scores(student)
    context['projects'] = student.projects.all()
    context['degrees'] = Degree.objects.order_by('name')
    context['acad_disciplines'] = Discipline.objects.order_by('name')
    context['CURRENT_EDUCATION'] = CURRENT_EDUCATION
    context['PAST_EDUCATION'] = PAST_EDUCATION
    context['states'] = SpokenState.objects.values('id','name').order_by('name')
    context['cities'] = SpokenCity.objects.values('id','name').order_by('name')

    return render(request,'emp/student_form.html',context)


# @user_passes_test(is_manager)
def shortlist_student(request):
    data = {}
    try:
        students = request.GET.get('students', None)
        student_ids = [ int(x) for x in students[:-1].split(',') ]
        job_id = int(request.GET.get('job_id', None))
        job = Job.objects.get(id=job_id)
        JobShortlist.objects.filter(job=job,spk_user__in=student_ids).update(status=1)
        data['updated']=True
    except:
        data['updated']=False
    return JsonResponse(data) 


def update_job_app_status(job,student,spk_user_id):
    job_shortlist = JobShortlist.objects.create(job=job,spk_user=spk_user_id,student=student,status=APPLIED)
    
class JobAppStatusListView(UserPassesTestMixin,ListView):
    template_name='emp/job_app_status_list.html'
    model = Job
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    def test_func(self):
        return is_manager(self.request.user)


@user_passes_test(is_manager)
def job_app_details1(request,id):
    context = {}
    # given : job id
    # get job 
    job = Job.objects.get(id=id)
    # get foss for that job
    foss = job.foss
    # get mdlcourse_id for fosses
    # quiz_ids = [x.mdlquiz_id for x in FossMdlCourses.objects.filter(foss_id__in=list(map(int,foss.split(','))))]
    fossMdlCourses = FossMdlCourses.objects.filter(foss_id__in=list(map(int,foss.split(',')))).values('foss_id','mdlcourse_id','mdlquiz_id')
    fossMdlCourses_df = pd.DataFrame(fossMdlCourses)
    # get students for that job from jobshortlist table
    students_emp = [x.student for x in JobShortlist.objects.filter(job=job)]
    students_spk = [x.spk_student_id for x in students_emp]
    # 1 get mdluser_id from ta table for above students
    mdluser_ids = set([x.mdluser_id for x in TestAttendance.objects.filter(student_id__in=students_spk)])
    mdluser_student = TestAttendance.objects.filter(student_id__in=students_spk).values('mdluser_id','student_id')
    mdluser_student_df = pd.DataFrame(mdluser_student)
    # now filter mdlquiz_grades on mdluser_ids & mdlquiz_ids above
    r = MdlQuizGrades.objects.using('moodle').filter(userid__in=mdluser_ids,quiz__in=fossMdlCourses_df['mdlquiz_id']).values('quiz','userid','grade')
    # change the aabove qs to df
    df = pd.DataFrame(r)
    # add student_id column based on mdluser_id see #1
    r = pd.merge(mdluser_student_df,df,left_on='mdluser_id',right_on='userid')
    r = pd.merge(r,fossMdlCourses_df,left_on='quiz',right_on='mdlquiz_id').drop_duplicates()
    r=r.drop(['mdluser_id','quiz','userid','mdlcourse_id','mdlquiz_id'], axis = 1).drop_duplicates()
    d = {}
    for index, row in r.iterrows():
        if row['student_id'] in d:
            d[row['student_id']][row['foss_id']]=row['grade']
        else:
            d[row['student_id']]={'student_id':row['student_id'],row['foss_id']:row['grade']}
    l = list(d.values())
    context['data']=l


    return render(request,'emp/job_app_status_detail.html',context)

@user_passes_test(is_manager)
def job_app_details(request,id):
    context = {}
    job = Job.objects.get(id=id)
    students_awaiting = [x.student for x in JobShortlist.objects.filter(job_id=id) if x.status==0]
    students_awaiting1 = [x.student.spk_student_id for x in JobShortlist.objects.filter(job_id=id) if x.status==0]
    ta = TestAttendance.objects.filter(student_id__in=students_awaiting1)
    ta = ta.values('student_id','mdluser_id','mdlcourse_id','mdlquiz_id')
    ta_df=pd.DataFrame(ta)
    try:
        mdl_quiz_grades = MdlQuizGrades.objects.using('moodle').filter(userid__in=ta_df['mdluser_id'])
        mdl_quiz_grades=mdl_quiz_grades.values('quiz','userid','grade')
        mdl_quiz_grades_df=pd.DataFrame(mdl_quiz_grades)
        fossmdlcourses=FossMdlCourses.objects.filter(mdlquiz_id__in=mdl_quiz_grades_df['quiz']).values('mdlcourse_id','foss_id','mdlquiz_id')
        fossmdlcourses_df=pd.DataFrame(fossmdlcourses)
        fosscategory=FossCategory.objects.filter(id__in=fossmdlcourses_df['foss_id']).values('id','foss')
        fosscategory_df=pd.DataFrame(fosscategory)
        df1 = pd.merge(fossmdlcourses_df,fosscategory_df,left_on='foss_id',right_on='id')
        df1=df1.drop(['id','foss_id'], axis = 1)
        pd.merge(fossmdlcourses_df,fosscategory_df,left_on='foss_id',right_on='id')
        df1 = pd.merge(fossmdlcourses_df,fosscategory_df,left_on='foss_id',right_on='id')
        df1=df1.drop(['id','foss_id'], axis = 1)
        d = pd.merge(ta_df,mdl_quiz_grades_df,left_on=['mdlquiz_id','mdluser_id'],right_on=['quiz','userid'])
        df = pd.merge(d,df1,on='mdlcourse_id')
        sq = Student.objects.filter(spk_student_id__in=df['student_id'])
        sq = sq.values('spk_usr_id','address','spk_institute','gender','state','city','spk_student_id')
        sq_df=pd.DataFrame(sq)
        # users = User.objects.filter(student__in=sq).values('first_name','last_name')
        # users_df = pd.DataFrame(users)
        # sq_df=sq_df.join(users_df,on='user_id')
        # sq_df['fullname']=sq_df['first_name'] + sq_df['last_name']
        df=pd.merge(df,sq_df,left_on='student_id',right_on='spk_student_id')
        df1=df.drop_duplicates().pivot(index='student_id',columns='foss',values='grade')
        context['columns']=df1.columns
        df1.reset_index(inplace=True)
        dnew=pd.merge(df1,sq_df,left_on='student_id',right_on='spk_student_id').drop(columns= ['spk_student_id'])
        cols = list(dnew.columns.values)
        cols.remove('spk_usr_id')
        cols[0]='spk_usr_id'
        dnew=dnew[cols]
        dnew.set_index('spk_usr_id', inplace=True)
        json_records = dnew.reset_index().to_json(orient ='records')
        data = []
        data = json.loads(json_records)
        context = {'d': data}
    except:
        pass
    
    # context['df']=df1.to_html()
    students_shortlisted = [x.student for x in JobShortlist.objects.filter(job_id=id) if x.status==1]
    context['job'] = job
    context['students_awaiting'] = students_awaiting
    context['students_shortlisted'] = students_shortlisted
    context['mass_mail']=settings.MASS_MAIL
    return render(request,'emp/job_app_status_detail.html',context)


class JobShortlistDetailView(DetailView):
    model = JobShortlist
    template_name='emp/job_app_status_detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = Job.objects.get(id=self.kwargs['slug'])
        context['job']=job
        return context

class JobShortlistListView(ListView):
    model = JobShortlist
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@login_required
def add_student_job_status(request):
    context={}
    form = JobApplicationForm(request.POST)
    if form.is_valid():
        job_id = form.cleaned_data['job_id']
        spk_user_id = form.cleaned_data['spk_user_id']
        student_id = form.cleaned_data['student']
        student = Student.objects.get(id=student_id)
        job = Job.objects.get(id=job_id)
        r=update_job_app_status(job,student,spk_user_id)
        messages.success(request, 'Job Application Submitted Successfully!')
        context['applied_jobs'] = [x.job for x in JobShortlist.objects.filter(student=student)]
    else:
        print(form.errors)
    return HttpResponseRedirect(reverse('student_jobs'))

@csrf_exempt
def ajax_state_city(request):
    if request.method == 'POST':
        data = {}
        state = request.POST.get('state')
        cities = SpokenCity.objects.filter(state=state).order_by('name')
        tmp = '<option value = None> --------- </option>'
        if cities:
            for i in cities:
                tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
        data['cities']=tmp
        return JsonResponse(data)
@csrf_exempt
def ajax_institute_list(request):
    if request.method == 'POST':
        data = {}
        city = request.POST.get('city')
        institutes = AcademicCenter.objects.filter(city_id=city).order_by('institution_name')
        tmp = '<option value = None> --------- </option>'
        if institutes:
            for i in institutes:
                tmp +='<option value='+str(i.id)+'>'+i.institution_name+'</option>'
        data['institutes']=tmp
        return JsonResponse(data)

@csrf_exempt
def ajax_get_state_city(request):
    # if request.method == 'POST':
    data = {}
    insti = request.POST.get('insti')
    val = AcademicCenter.objects.filter(id=insti).values('state_id','city_id')
    state_id = val[0]['state_id']
    city_id = val[0]['city_id']
    state = SpokenState.objects.filter(id=state_id)
    state = state[0].name
    city = SpokenCity.objects.filter(id=city_id)
    city = city[0].name
    data['state_id']=state_id
    data['city_id']=city_id
    data['state']=state
    data['city']=city
    data['insti_id']=insti
    return JsonResponse(data)


# @user_passes_test(is_manager)
@access_profile
def student_profile_details(request,id,job):
    context = {}
    context['spk_student_id']=id
    context['job_id']=job
    job_obj = Job.objects.get(id=job)
    context['job']=job_obj
    # student = Student.objects.get(spk_student_id=id)
    student = Student.objects.get(spk_usr_id=id)
    context['student']=student
    context['MEDIA_URL']=settings.MEDIA_URL
    context['scores']=fetch_student_scores(student)
    context['current_education'] = student.education.filter(order=CURRENT_EDUCATION)
    context['past_education'] = student.education.filter(order=PAST_EDUCATION).first()

    return render(request,'emp/student_profile.html',context)

@user_passes_test(is_student)
def student_jobs(request):
    context = {}
    #get applied jobs
    rec_student = Student.objects.get(user=request.user)
    applied_jobs = get_applied_joblist(rec_student.spk_usr_id)
    rec_jobs = get_recommended_jobs(rec_student)
    #get recommended jobs
    context['applied_jobs']=applied_jobs
    context['rec_jobs']=rec_jobs
    
    return render(request,'emp/student_jobs.html',context)

def error_404(request,exception):
    data = {}
    return render(request,'emp/error_404.html', data)

def error_500(request,exception):
    data = {}
    return render(request,'emp/error_500.html', data)

class DegreeCreateView(PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    model = Degree
    fields = ['name']
    permission_required = 'emp.add_degree'
    success_message ="\'%(name)s\' degree is added successfully"
    def get_success_url(self):
        obj = Degree.objects.get(name=self.object.name,date_created=self.object.date_created)
        # return reverse('degree-detail', kwargs={'slug': obj.slug})
        return reverse('add_degree')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        degrees = Degree.objects.values('id','name').order_by('name')
        context['degrees']=degrees
        return context

class DegreeUpdateView(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    model = Degree
    fields = ['name']
    permission_required = 'emp.add_company'
    success_message ="\'%(name)s\' degree is updated successfully"
    template_name = 'emp/degree_update_form.html'
    def get_success_url(self):
        # obj = Degree.objects.get(name=self.object.name,date_created=self.object.date_created)
        # return reverse('degree-detail', kwargs={'slug': obj.slug})
        return reverse('add_degree')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        degrees = Degree.objects.values('id','name')
        context['degrees']=degrees
        context['current_degree']=self.get_object()
        return context

class DisciplineCreateView(PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    model = Discipline
    fields = ['name']
    permission_required = 'emp.add_discipline'
    success_message ="\'%(name)s\' discipline is added successfully"
    def get_success_url(self):
        obj = Discipline.objects.get(name=self.object.name,date_created=self.object.date_created)
        # return reverse('degree-detail', kwargs={'slug': obj.slug})
        return reverse('add_discipline')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        disciplines = Discipline.objects.values('id','name').order_by('name')
        context['disciplines']=disciplines
        return context

class DisciplineUpdateView(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    model = Discipline
    fields = ['name']
    permission_required = 'emp.add_discipline'
    success_message ="\'%(name)s\' discipline is updated successfully"
    # template_name_suffix = '_update_form'
    template_name = 'emp/discipline_update_form.html'
    # template_name = 'emp/degree_update_form.html'
    def get_success_url(self):
        # obj = Degree.objects.get(name=self.object.name,date_created=self.object.date_created)
        # return reverse('degree-detail', kwargs={'slug': obj.slug})
        return reverse('add_discipline')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        disciplines = Discipline.objects.values('id','name')
        context['disciplines']=disciplines
        context['current_discipline']=self.get_object()
        return context

# class DisciplineDetailView(DetailView):
#     template_name = 'emp/employer_detail.html'
#     model = Company
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         company_state = SpokenState.objects.get(id=self.object.state_c)
#         company_city = SpokenCity.objects.get(id=self.object.city_c)
#         context['company_state']=company_state.name
#         context['company_city']=company_city.name
#         return context

class DomainCreateView(PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    model = Domain
    fields = ['name']
    permission_required = 'emp.add_domain'
    success_message ="\'%(name)s\' domain is added successfully"
    def get_success_url(self):
        obj = Domain.objects.get(name=self.object.name,date_created=self.object.date_created)
        # return reverse('degree-detail', kwargs={'slug': obj.slug})
        return reverse('add_domain')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domains = Domain.objects.values('id','name')
        context['domains']=domains
        return context

class DomainUpdateView(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    model = Domain
    fields = ['name']
    permission_required = 'emp.add_domain'
    success_message ="\'%(name)s\' domain is updated successfully"
    # template_name_suffix = '_update_form'
    template_name = 'emp/domain_update_form.html'
    # template_name = 'emp/degree_update_form.html'
    def get_success_url(self):
        # obj = Degree.objects.get(name=self.object.name,date_created=self.object.date_created)
        # return reverse('degree-detail', kwargs={'slug': obj.slug})
        return reverse('add_domain')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domains = Domain.objects.values('id','name')
        context['domains']=domains
        context['current_domain']=self.get_object()
        return context

class JobTypeCreateView(PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    model = JobType
    fields = ['jobtype']
    permission_required = 'emp.add_jobtype'
    success_message ="\'%(jobtype)s\' job type is added successfully"
    def get_success_url(self):
        obj = JobType.objects.get(jobtype=self.object.jobtype,date_created=self.object.date_created)
        # return reverse('degree-detail', kwargs={'slug': obj.slug})
        return reverse('add_job_type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_types = JobType.objects.values('id','jobtype')
        context['job_types']=job_types
        return context

class JobTypeUpdateView(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    model = JobType
    fields = ['jobtype']
    permission_required = 'emp.add_jobtype'
    success_message ="\'%(jobtype)s\' job type is updated successfully"
    # template_name_suffix = '_update_form'
    template_name = 'emp/jobtype_update_form.html'
    # template_name = 'emp/degree_update_form.html'
    def get_success_url(self):
        # obj = Degree.objects.get(name=self.object.name,date_created=self.object.date_created)
        # return reverse('degree-detail', kwargs={'slug': obj.slug})
        return reverse('add_job_type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_types = JobType.objects.values('id','jobtype')
        context['job_types']=job_types
        context['current_job_type']=self.get_object()
        return context

@csrf_exempt
def ajax_send_mail(request):
    data = {}
    if request.method == 'POST':
        subject = request.POST.get('subject')
        job = request.POST.get('job')
        message = request.POST.get('message')
        email = request.POST.get('data')
        e = json.loads(email)
        emails = [ item[0] for item in e['data']]
        date_created = datetime.datetime.now()
        
        total , sent, errors, log_file_name = send_mail_shortlist(subject,message,emails,job)
        file_path = os.path.join(settings.LOG_LOCATION, log_file_name)
        email_status = ShortlistEmailStatus(date_created=date_created,email_sequence=SECOND_SHORTLIST_EMAIL,total_mails=total,success_mails=sent,job_id=int(job),log_file=file_path)
        email_status.save()
        data['status']='success'
        data['total']=total
        data['sent']=sent
        data['errors']=errors
    
    return JsonResponse(data)

@user_passes_test(is_manager)
def student_filter(request):
    context = {}
    foss = FossCategory.objects.values_list('id','foss') #get foss list to show in drop down
    context['foss'] = foss
    context['MANDATORY_FOSS']=MANDATORY_FOSS #key to mark manndatory foss
    context['OPTIONAL_FOSS']=OPTIONAL_FOSS #key to mark optional foss
    
    
    if request.method == 'POST':
        # -------------------------------------------------------- 1. get input for single foss selection
        foss = request.POST.getlist('foss') #get mandatory / optional single foss
        grades = request.POST.getlist('grade') #get mandatory / optional single foss grade
        criteria_type = request.POST.getlist('criteria-type') #get mandatory / optional type

        grade_filter = zip(foss, grades,criteria_type)
        mandatory = {} #mandatorry fosses
        optional = [] #optional fosses
        for foss,grade,criteria_type in grade_filter:
            if int(criteria_type)==MANDATORY_FOSS:
                mandatory[int(foss)]=grade
            else:
                optional[foss]=grade
        # -------------------------------------------------------- 1. get input for  single foss selection ends

        # -------------------------------------------------------- 2. get input for multiple foss selection
        multiple_grade = request.POST.getlist('multiple_grade') #grades from any one of query
        num = request.POST.get('num') if request.POST.get('num') else 0 #key to track number of multiple foss selection
        multiple_fosses = [] #list of list of any of the fosses criteria
        for item in range(1,int(num)+2):
            # print(f"item ******************* {item}")
            multiple_fosses.append(request.POST.getlist('fosses_'+str(item)))
        # -------------------------------------------------------- 2. get input for multiple foss selection ends
        
        # -------------------------------------------------------- 3. get mdl_users satisfying the single mandatory foss criteria (mdlusers)
        mdlusers = MdlUser.objects.using('moodle').all()
        users_id = []
        # foss_mdl_courses dictionary | key : foss id| value : corresponding mdl quiz id
        foss_mdl_courses = FossMdlCourses.objects.filter(foss_id__in=mandatory).values_list('foss','mdlquiz_id')
        mdl_quizzes = list(map(lambda x: x[1], foss_mdl_courses))
        mdl_users = []
        q = []
        # print(f"foss_mdl_courses ************************ {foss_mdl_courses}")
        for item in foss_mdl_courses:
            # print(f"item --------------> {item}")
            if mdl_users:
                q = MdlUser.objects.filter(Q(mdlquizgrades__quiz=item[1]) & Q(mdlquizgrades__grade__gt=mandatory[item[0]]),id__in=mdl_users).values_list('id')
                # print(f"q1 query ------------------------------ {q.query}")
                # print(f"q1 ------------------------------ {q}")
            else:
                q = MdlUser.objects.filter(Q(mdlquizgrades__quiz=item[1]) & Q(mdlquizgrades__grade__gt=mandatory[item[0]])).values_list('id')
                # print(f"q2 query------------------------------ {q.query}")
                # print(f"q2 ------------------------------ {q}")
            mdl_users = list(itertools.chain(*q))
            # q = Q(mdlquizgrades__quiz=item[1]) & Q(mdlquizgrades__grade__gt=mandatory[item[0]])
            # mdlusers = mdlusers.filter(q)
        print(f"num ****************************** {num}")
        print(f"range(int(num)+1)*************** {list(range(int(num)+1))}")
        print(f"multiple_fosses ************************** {multiple_fosses}")
        print(f"multiple_grade ************************** {multiple_grade}")
        # for item in range(int(num)):
        #     print(f"num ---------- {num}")
        #     print(f"num ********* {num}. multiple_fosses[item] ********* {multiple_fosses[item]}. multiple_grade[item] ************** {multiple_grade[item]}")
        #     if mdl_users:
        #         q = MdlUser.objects.filter(Q(mdlquizgrades__quiz__in=multiple_fosses[item]) & Q(mdlquizgrades__grade__gt=multiple_grade[item]),id__in=mdl_users).values_list('id')
        #         # print(f"q1 query ------------------------------ {q.query}")
        #         # print(f"q1 ------------------------------ {q}")
        #     else:
        #         q = MdlUser.objects.filter(Q(mdlquizgrades__quiz__in=multiple_fosses[item]) & Q(mdlquizgrades__grade__gt=multiple_grade[item])).values_list('id')
        #         # print(f"q2 query------------------------------ {q.query}")
        #         # print(f"q2 ------------------------------ {q}")
        #     mdl_users = list(itertools.chain(*q))
            
            

        print("0 ******************************")
        mdlusers = q.values('id')
        # -------------------------------------------------------- 3. get mdl_users satisfying the single mandatory foss criteria (mdlusers) ends

        # users_id = users.values_list('id').annotate(key=F('mdlquizgrades__userid')+'_'+F('mdlquizgrades__quiz')).annotate(grade=F('mdlquizgrades__grade'))
        # users_id = users.values('id')
        # -------------------------------------------------------- 4. users_id : (user_id, user_quiz, grade) satisfying only mandatory quiz, grade criteria
        users_id = mdlusers.annotate(key=Concat(F('mdlquizgrades__userid'),Value('_'),F('mdlquizgrades__quiz'),output_field=CharField())).annotate(grade=F('mdlquizgrades__grade')).values_list('id','key','grade')
        context['users_id'] = users_id
        print(f"users_id ******************* {users_id}")
        # -------------------------------------------------------- 4. users_id : (user_id, user_quiz, grade) mdluser ids satisfying only mandatory quiz, grade criteria ends
        
        # -------------------------------------------------------- 5. d_data : mdluser ids with all selected mandatory quiz; this is to get the grade for all selected foss for selected mdlusers irrespective of grade criteria
        # d1 : dictionary of user_quiz & grades | key : mdluserid_quizid | value : grade
        unzipped = list(zip(*users_id))
        print(f"unzipped **************** {unzipped}")
        d_data = MdlUser.objects.filter(id__in=list(unzipped[0]),mdlquizgrades__quiz__in=mdl_quizzes).annotate(key=Concat(F('mdlquizgrades__userid'),Value('_'),F('mdlquizgrades__quiz'),output_field=CharField())).annotate(grade=F('mdlquizgrades__grade')).values_list('id','key','grade')
        print(f"d_data ******************* {d_data}")
        d_unzipped = list(zip(*d_data))

        d_key = d_unzipped[1] #mdluserid_quizid
        d_values = d_unzipped[2] #grade
        d1 = {}
        for elem in enumerate(d_key):
            d1[d_key[elem[0]]] = d_values[elem[0]]
        context['d_data'] = d_data
        context['d1'] = d1 #dictionary to get quiz grades
        # -------------------------------------------------------- 5. d_data : mdluser ids with all selected mandatory quiz; this is to get the grade for all selected foss for selected mdlusers irrespective of grade criteria
        # -------------------------------------------------------- ??
        key = unzipped[1] #mdluserid_quizid
        values = unzipped[2] #grade
        d = {}
        for elem in enumerate(key):
            d[key[elem[0]]] = values[elem[0]]
            # print(key[elem[0]],values[elem[0]])
        # users_id = users.values_list('id')
        # -------------------------------------------------------- ??
        # mdl_user_lst = list(itertools.chain(*users_id))
        mdl_user_lst = unzipped[0]
        context['mdl_user_lst']=mdl_user_lst
        user_subquery = SpokenUser.objects.filter(spokenstudent=OuterRef('student_id')).values('first_name')
        ta = TestAttendance.objects.filter(mdluser_id__in=mdl_user_lst).filter(mdlquiz_id__in=mdl_quizzes).values('student_id','mdlquiz_id','mdluser_id')
        ta = ta.annotate(student_name=Subquery(user_subquery))
        
        # foss_subquery = FossMdlCourses.objects.filter(mdlcourse_id=OuterRef('mdlcourse_id')).values('foss')[:1]
        foss_id_subquery = FossMdlCourses.objects.filter(mdlcourse_id=OuterRef('mdlcourse_id')).values('foss')[:1]
        # ta = ta.annotate(foss_name=FossCategory.objects.filter(id=Subquery(foss_subquery)))
        # foss_subquery = FossCategory.objects.filter(id=OuterRef('foss_id')).MdlQuizGrades.objectsvalues('foss')[:1]
        foss_subquery = FossCategory.objects.filter(id=OuterRef('foss_id')).values('foss')[:1]
        # grade_subquery = MdlQuizGrades.objects.using('moodle').filter(quiz=OuterRef('mdlquiz_id'),userid=OuterRef('mdluser_id')).values('timemodified')[:1]
        # grade_subquery = MdlQuizGrades.objects.using('moodle').filter(userid=OuterRef('mdluser_id')).values('grade')[:1]
        # ta = ta.annotate(foss_id=Subquery(foss_id_subquery)).annotate(foss_name=Subquery(foss_subquery)).annotate(grade=d1.get(Concat(F('mdluser_id'),Value('_'),F('mdlquiz_id'),output_field=CharField()),Value('0'))).values('student_name','foss_name','grade')
        ta = ta.annotate(foss_id=Subquery(foss_id_subquery)).annotate(foss_name=Subquery(foss_subquery)).annotate(grade_key=Concat(F('mdluser_id'),Value('_'),F('mdlquiz_id'),output_field=CharField())).values('student_name','foss_name','grade_key')
        print(f"ta ************ {ta}")
        students = list(map(lambda x: x['student_name'], ta))

        mdl_user_data = mdlusers.values_list('id','firstname')
        context['mdl_user_data']=mdl_user_data
        
        # spk_students = SpokenStudent.objects.filter(id__in=students).values('id','user_id')
        # users = list(map(lambda x: x[1], spk_students))
        # spk_users = SpokenUser.objects.filter(spokenstudent__in=students).values('id','first_name')
        # context['spk_users']=spk_users
        context['ta']=ta
        context['len']=len(ta)
    return render(request,'emp/student_filter.html',context)

    
    # def form_invalid(self, form):
    #     print(f"hjklkn-------------{form}")
    #     return self.render_to_response(self.get_context_data(form=form))

    # def form_valid(self, form):
    #     self.object = form.save(commit=False)
    #     print(f'slef.user ---- -------------------------------------------------')
    #     self.object.save()
    #     return super(ModelFormMixin, self).form_valid(form)
# class JobDetailView(DetailView):
#     template_name = 'emp/jobs_detail.html'
#     model = Job
#     def get_context_data(self, **kwargs):
#         print("inside job detial view *****************")
#         context = super().get_context_data(**kwargs)
#         return context
# class JobListView(ListView):
#     template_name = 'emp/jobs_list.html'
#     model = Job
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         print("************ context : ",context)
#         return context
# class JobUpdate(SuccessMessageMixin,UpdateView):
#     template_name = 'emp/jobs_update_form.html'
#     model = Job
#     fields = ['company','title','designation','state','city','skills','description','domain','salary_range_min','salary_range_max','job_type','benefits','requirements','shift_time','key_job_responsibilities','gender']
#     success_message ="%(title)s was updated successfully"
