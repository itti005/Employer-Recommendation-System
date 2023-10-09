from django.shortcuts import render,redirect
from django.contrib.auth import logout

from events.models import *
from .models import *
from spoken.models import TestAttendance, FossMdlCourses,FossCategory, SpokenState, SpokenCity
from moodle.models import MdlQuizGrades,MdlUser
from django.views.generic.edit import UpdateView

from emp.forms import StudentGradeFilterForm, EducationForm,StudentForm,DateInput,ContactForm
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView,UpdateView,ModelFormMixin,FormMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin,UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from .filterset import CompanyFilterSet
from .forms import ACTIVATION_STATUS, JobSearchForm, JobApplicationForm
from django.db.models import Q,F,OuterRef, Subquery,Count, Prefetch

from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings
from django.forms import HiddenInput
from django import forms
import pandas as pd
import json
from django.core.files.storage import FileSystemStorage
from os import listdir
import re
from django.utils.datastructures import MultiValueDictKeyError

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator

from django.utils.functional import wraps
from django.core.exceptions import PermissionDenied,MultipleObjectsReturned
from django.http import FileResponse, Http404
from .send_mail_students import send_mail_shortlist
import itertools
from .models import STATUS
import datetime
from django.core.mail import send_mail
from smtplib import SMTPException
from .utility import *
from .helper import *
from collections import defaultdict
import csv
import os
from django.shortcuts import render
from rest_framework import viewsets, pagination
from emp.models import Student
from .serializers import StudentSerializer
from .pagination import CustomPagination

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = CustomPagination  # Set the custom pagination class


class CustomPagination(pagination.PageNumberPagination):
    page_size = 1 # Set the number of items per page
    page_size_query_param = 'page_size'
    # max_page_size = 100

 
from emp.models import Domain
from .serializers import DomainSerializer
# from .pagination import CustomPagination 
class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer

class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    pagination_class = CustomPagination
    page_size=2


from emp.models import Discipline
from .serializers import DisciplineSerializer

class DisciplineViewSet(viewsets.ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer


@check_user
def document_view(request,pk):
    try:
        file_type = request.GET["type"]
        file = os.path.join('media','students',str(request.user.id),file_type+str(request.user.id)+'.pdf')
        return FileResponse(open(file, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()


def get_job_app_status(job):#show job application status to HR
    pass

# def get_recommended_jobs(student):
#     #get jobs having status 0 & last app submission date greater than equal to today
#     jobs = Job.objects.filter(last_app_date__gte=datetime.datetime.now(),status=STATUS['ACTIVE'])# All active jobs
#     applied_jobs = [x.job for x in get_applied_joblist(student)]
#     jobs = [x for x in jobs if x not in applied_jobs ]
#     scores = fetch_student_scores(student)
#     if scores:
#         mdl_user_id = scores[0]['mdl'].userid
#     student_foss = [d['foss'] for d in scores]  #fosses for which student grade is available
#     rec_jobs = []
#     spk_student = SpokenStudent.objects.get(user_id=student.spk_usr_id)
#     count = 1
#     for job in jobs:
#         fosses = list(map(int,job.foss.split(',')))
#         if job.state and job.state!='0':
#             states = list(map(int,job.state.split(',')))
#         else:
#             states = ''
#         if job.city and job.city!='0':
#             cities = list(map(int,job.city.split(',')))
#         else:
#             cities = ''
#         # cities = '' if job.city=='0' else list(map(int,job.city.split(',')))
#         # insti_type = '' if job.institute_type=='0' else list(map(int,job.institute_type.split(',')))
#         if job.institute_type and job.institute_type!='0':
#             insti_type = list(map(int,job.institute_type.split(',')))
#         else:
#             insti_type = ''
#         valid_fosses = [   d['foss'] for d in scores if str(d['foss']) in job.foss and int(d['grade'])>=job.grade]
#         if valid_fosses:
#             mdl_quiz_ids = [x.mdlquiz_id for x in FossMdlCourses.objects.filter(foss_id__in=valid_fosses)] #Student passes 1st foss & grade criteria
#             mdluser_id = TestAttendance.objects.filter(student=spk_student).first().mdluser_id
#             # test_attendance = TestAttendance.objects.filter(student=spk_student, 
#             test_attendance = TestAttendance.objects.filter(mdluser_id=mdluser_id, 
#                                                 mdlquiz_id__in=mdl_quiz_ids,
#                                                 test__academic__state__in=states if states!='' else SpokenState.objects.all(),
#                                                 test__academic__city__in=cities if cities!='' else SpokenCity.objects.all(),
#                                                 status__gte=3,
#                                                 test__academic__institution_type__in=insti_type if insti_type!='' else InstituteType.objects.all(),
#                                                 test__academic__status__in=[job.activation_status] if job.activation_status else [1,3],
#                                                 )
#             if job.from_date and job.to_date:
#                 test_attendance = test_attendance.filter(test__tdate__range=[job.from_date, job.to_date])
#             elif job.from_date:
#                 test_attendance = test_attendance.filter(test__tdate__gte=job.from_date)
#             if test_attendance:
#                 rec_jobs.append(job)
#         else:
#             pass
#         count+=1
#     return rec_jobs

#function to get student spoken test scores; returns list of dictionary of foss & scores
# def fetch_student_scores(student):  #parameter : recommendation student obj
#     scores = []
#     #student = Student.objects.get(id=2) #TEMPORARY
#     spk_user = student.spk_usr_id
#     try:
#         spk_student = SpokenStudent.objects.get(user=spk_user)
#         testattendance = TestAttendance.objects.values('mdluser_id').filter(student=spk_student)
#         mdl_grades = MdlQuizGrades.objects.using('moodle').filter(userid=testattendance[0]['mdluser_id']) #fetch all rows with mdl_course & grade
#         count = 1
#         for item in mdl_grades: #map above mdl_course with foss from fossmdlcourse
#             try:
#                 foss_mdl_courses = FossMdlCourses.objects.get(mdlquiz_id=item.quiz)
#                 foss = foss_mdl_courses.foss
#                 scores.append({'foss':foss.id,'name':foss.foss,'grade':item.grade,'quiz':item.quiz,'mdl':item})
#             except FossMdlCourses.DoesNotExist as e:
#                 print(e)
#             except MultipleObjectsReturned:
#                 for foss_mdl_courses in FossMdlCourses.objects.filter(mdlquiz_id=item.quiz):
#                     foss = foss_mdl_courses.foss
#                     scores.append({'foss':foss.id,'name':foss.foss,'grade':item.grade,'quiz':item.quiz,'mdl':item})
#             count+=1
#     except SpokenStudent.DoesNotExist as e:
#         print(e)
#     except IndexError as e:
#         print(e)
#     return scores


@user_passes_test(is_student)
def student_homepage(request):
    context={}
    # Top 6 jobs & company to display on student homepage
    company_display = Company.objects.filter(rating=DISPLAY_ON_HOMEPAGE,status=ACTIVE).values('name','logo').order_by('date_updated')[:6]
    context['company_display']=company_display
    rec_student = Student.objects.get(user=request.user)
    applied_jobs = get_applied_jobs(rec_student)
    context['applied_jobs'] = applied_jobs if len(applied_jobs)<4 else applied_jobs[:4]
    jobs_to_display = get_jobs_to_display(rec_student) 
    context['jobs_to_display'] = jobs_to_display if len(jobs_to_display)<6 else jobs_to_display[:6]
    rec_jobs = get_recommended_jobs(rec_student)
    context['rec_jobs'] = rec_jobs if len(applied_jobs)<3 else rec_jobs[:3]
    active_event = Event.objects.filter(status=1,type='JOBFAIR').order_by('-start_date').first()
    if active_event:
        jobfair = JobFair.objects.get(event=active_event)
        context['active_event'] = active_event
        context['jobfair'] = jobfair
        # context['is_registered_for_jobfair'] = JobFair.objects.filter(event=active_event,students=rec_student).exists()
        context['is_registered_for_jobfair'] = JobFairAttendance.objects.filter(event=active_event,student=rec_student).exists()
    return render(request,'emp/student_homepage.html',context)

@user_passes_test(is_manager)
def manager_homepage(request):
    context={}
    response = render(request,'emp/manager_homepage.html',context)
    return response

def handlelogout(request):
    logout(request)
    return redirect('login')

def index(request):
    context={}
    context['companies'] = Company.objects.filter(rating=RATING['DISPLAY_ON_HOMEPAGE'],status=True)[:8]
    l = GalleryImage.objects.filter(display_on_homepage=True,active=True)[:8]
    context['gallery'] = GalleryImage.objects.filter(display_on_homepage=True,active=True)[:8]
    testimo_list=Testimonial.objects.filter(display_on_homepage=True,active=True)[:4]
    context['testimonials'] = testimo_list
    context['events'] = Event.objects.filter(show_on_homepage=True,status=True)[:6]
    form = ContactForm()
    context['contact_form'] = form
    return render(request,'emp/index.html',context)

#---------------- CBV for Create, Detail, List, Update for Company starts ----------------#
def update_company_form(self,form):
    form.fields['name'].widget.attrs ={'placeholder': 'Company Name'}
    form.fields['domain'].queryset = Domain.objects.order_by('name')
    form.fields['rating'].widget = forms.Select(attrs=None, choices=COMPANY_RATING)
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
        ld = obj.last_app_date.date()
        obj.last_app_date = datetime.datetime.combine(ld,datetime.time(23,59,59))
        obj.save()
        return reverse('job-detail', kwargs={'slug': obj.slug})
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        job=self.object.save()
        form.save_m2m()
        messages.success(self.request, 'Job information added successfully.')
        return super(ModelFormMixin, self).form_valid(form)

    def get_form(self):
        form = super(JobCreate, self).get_form()
        form = update_form_widgets(self,form)
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_form = StudentGradeFilterForm()# get data for filters
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
    paginate_by = 8
    form_class = JobSearchForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_url']=settings.BASE_URL
        if self.request.user.groups.filter(name='MANAGER'):
            context['grade_filter_url'] = settings.GRADE_FILTER
        else:
            try:
                if has_student_role(self.request.user.student):
                    job_short_list = get_applied_joblist(self.request.user.student)
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
            except:
                print("No student role assigend to user")
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
        if job.foss:
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
        ld = form.cleaned_data['last_app_date']
        form.cleaned_data['last_app_date'] = datetime.datetime.combine(ld.date(),datetime.time(23,59,59))
        form.instance.last_app_date = datetime.datetime.combine(ld.date(),datetime.time(23,59,59))
        form.save()
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
        student.joining_immediate = student_form.cleaned_data['joining_immediate']
        student.avail_for_intern = student_form.cleaned_data['avail_for_intern']
        student.willing_to_relocate = student_form.cleaned_data['willing_to_relocate']
        student.skills.set(student_form.cleaned_data['skills'])
        # code for saving projects starts
        urls = request.POST.getlist('pr_url', '')
        descs = request.POST.getlist('pr_desc', '')
        projects = student.projects.all()
        for project in projects:
            student.projects.remove(project)
            project.delete()
        for (url,desc) in zip(urls,descs):
            if url or desc:
                project = Project.objects.create(url = url,desc = desc)
                student.projects.add(project)
        try:
            location = settings.MEDIA_ROOT+'/students/'+str(request.user.id)+'/'
            os.makedirs(location)
        except:
            pass
        fs = FileSystemStorage(location=location) if location else FileSystemStorage()#defaults to   MEDIA_ROOT
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
        student.profile_update_date = datetime.datetime.now()
        student.save()
        save_education(c_education_form,student)
        save_prev_education(request,student)
    else:
        messages.error(request, f'Error in updating profile : {student_form.errors}')
    return student_form,c_education_form


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
    context['ilw_scores']=fetch_ilw_scores(student)
    context['projects'] = student.projects.all()
    return render(request,'emp/student_form.html',context)

@check_student
def student_profile(request,pk):
    context = {}
    student = Student.objects.get(user=request.user)
    context['student']=student
    if request.method=='POST':
        student_form = StudentForm(request.POST)
        c_education_form = EducationForm(request.POST)
        if student_form.is_valid() and c_education_form.is_valid():
            student_form,education_form = save_student_profile(request,student)
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, f'Error in updating profile - {student_form.errors} {c_education_form.errors}')
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
    context['scores'] = fetch_ta_scores(student)
    if has_ilw_role(student):
        context['ilw_scores']=fetch_ilw_scores(student)
    context['projects'] = student.projects.all()
    context['degrees'] = Degree.objects.order_by('name')
    context['acad_disciplines'] = Discipline.objects.order_by('name')
    context['CURRENT_EDUCATION'] = CURRENT_EDUCATION
    context['PAST_EDUCATION'] = PAST_EDUCATION
    context['states'] = SpokenState.objects.values('id','name').order_by('name')
    context['cities'] = SpokenCity.objects.values('id','name').order_by('name')
    # context['skill_groups'] = SkillGroup.objects.values('id', 'name')
    # context['skills'] = Skill.objects.annotate(group_name=F('group__name')).values('id', 'name', 'group_id','group_name')
    context['skill_groups'] = SkillGroup.objects.annotate(num_skills=Count('skill')).prefetch_related('skill_set')
    context['student_skills'] = Skill.objects.filter(student=student).values_list('id',flat=True)
    student_skills = Skill.objects.filter(student=student).values_list('id',flat=True)
    return render(request,'emp/student_form.html',context)


# @user_passes_test(is_manager)
def shortlist_student(request):
    data = {}
    try:
        students = request.GET.get('students', None)
        student_ids = [ int(x) for x in students[:-1].split(',') ]
        status = request.GET.get('status', 0)
        job_id = int(request.GET.get('job_id', None))
        job = Job.objects.get(id=job_id)
        JobShortlist.objects.filter(job=job,spk_user__in=student_ids).update(status=status)
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
def job_app_details(request,id):
    context = {}
    job = Job.objects.get(id=id)
    # students_awaiting = [x.student for x in JobShortlist.objects.filter(job_id=id) if x.status==0]
    students_awaiting = [(x.student,x.date_created) for x in JobShortlist.objects.filter(job_id=id) if x.status==0]
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
    students_rejected = [x.student for x in JobShortlist.objects.filter(job_id=id) if x.status==2]
    students_shortlisted_comp = [x.student for x in JobShortlist.objects.filter(job_id=id) if x.status==3] #shortlisted by company
    students_rejected_comp = [x.student for x in JobShortlist.objects.filter(job_id=id) if x.status==4] #rejected by company
    context['job'] = job
    context['students_awaiting'] = students_awaiting
    context['students_shortlisted'] = students_shortlisted
    context['students_rejected'] = students_rejected
    context['students_shortlisted_comp'] = students_shortlisted_comp
    context['students_rejected_comp'] = students_rejected_comp
    context['mass_mail']=settings.MASS_MAIL

    #stats
    
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

@csrf_exempt
def ajax_contact_form(request):
    data = {}
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            message = request.POST.get('message')
            feedback = Feedback.objects.create(name=name,email=email,message=message)
            subject = 'ERS - Job Recommendation System'
            mail_body = 'Name : ' + name +'\n' + 'Email : ' + email + '\n' + 'message : ' + message
            mail_from = settings.CONTACT_MAIL
            send_to = settings.CONTACT_MAIL
            send_mail(subject,mail_body,mail_from,[send_to],fail_silently=False)
            data['status']=1
            return JsonResponse(data)
        except SMTPException as e:
            print(e)
        except Exception as e:
            print(e)
            data['status']=0
    data['status']=0
    return JsonResponse(data)

# @user_passes_test(is_manager)
def getFieldsInfo(student):
    total_fields = 10
    empty_fields = []
    if not student.phone : empty_fields.append('Phone')
    if not student.address : empty_fields.append('Address')
    if not Education.objects.filter(student=student): empty_fields.append('education')
    if not student.about : empty_fields.append('About')
    if not student.projects : empty_fields.append('Projects')
    if not student.resume : empty_fields.append('Resume')
    if student.joining_immediate is None : empty_fields.append('Available to join immediately')
    if student.avail_for_intern is None : empty_fields.append('Available for internship')
    if student.willing_to_relocate is None : empty_fields.append('Willing to relocate')
    if not student.skills.all() : empty_fields.append('Skills')
    
    complete = round((total_fields-len(empty_fields))/total_fields*100)
    return complete,empty_fields


@access_profile
def student_profile_details(request,id,job):
    context = {}
    if job:
        context['job_id']=job
        job_obj = Job.objects.get(id=job)
        context['job']=job_obj
    student = Student.objects.get(id=id)
    context['student']=student
    context['MEDIA_URL']=settings.MEDIA_URL
    context['scores']=fetch_student_scores(student)
    context['ilw_scores']=fetch_ilw_scores(student)
    context['current_education'] = student.education.filter(order=CURRENT_EDUCATION)
    context['past_education'] = student.education.filter(order=PAST_EDUCATION).first()
    complete,empty_fields = getFieldsInfo(student)
    context['profile_completed'] = False if empty_fields else True
    context['skill_groups'] = SkillGroup.objects.prefetch_related(Prefetch('skill_set',queryset=Skill.objects.filter(student=student)))
    skill_groups = SkillGroup.objects.prefetch_related(Prefetch('skill_set',queryset=Skill.objects.filter(student=student)))
    context['complete']=complete
    context['empty_fields']=', '.join(empty_fields)
    context['notifications'] = Notifications.objects.filter(user = student.user)
    return render(request,'emp/student_profile.html',context)

def student_profile_details_spk(request,id):
    try:
        id = Student.objects.get(spk_student_id=id).id
        return redirect(reverse('student_profile_details',kwargs={'id': id,'job':0}))
    except Exception as e:
        return redirect(reverse('data_stats'))
        
@user_passes_test(is_student)
def student_jobs(request):
    context = {}
    #get applied jobs
    rec_student = Student.objects.get(user=request.user)
    applied_jobs = get_applied_joblist(rec_student)
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
        email_status = ShortlistEmailStatus(date_created=date_created,email_sequence=SECOND_SHORTLIST_EMAIL,
                                            total_mails=total,success_mails=sent,job_id=int(job),log_file=file_path,
                                            message=message,subject=subject)
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
    context['MASS_MAIL']=settings.MASS_MAIL
    
    if request.method == 'POST':
        # -------------------------------------------------------- 1. get input for single foss selection (mandatory / optional)
        foss_list = request.POST.getlist('foss') #get mandatory / optional single foss
        grades = request.POST.getlist('grade') #get mandatory / optional single foss grade
        criteria_type = request.POST.getlist('criteria-type') #get mandatory / optional type
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        all_quiz_ids = []
        grade_filter = zip(foss_list, grades,criteria_type)
        mandatory = {} #mandatorry fosses
        optional = {} #optional fosses
        for foss,grade,criteria_type in grade_filter:
            if int(criteria_type)==MANDATORY_FOSS:
                mandatory[int(foss)]=grade
            else:
                optional[int(foss)]=grade
        # -------------------------------------------------------- 1. end - get input for  single foss selection

        # -------------------------------------------------------- 2. get input for multiple foss selection
        multiple_grade = request.POST.getlist('multiple_grade') #grades from any one of query
        num = request.POST.get('num') if request.POST.get('num') else 0 #key to track number of multiple foss selection
        multiple_fosses = [] #list of list of any of the fosses criteria
        if num==0:
            multiple_fosses.append(request.POST.getlist('fosses_1'))
        else:
            for item in range(1,int(num)+1):
                multiple_fosses.append(request.POST.getlist('fosses_'+str(item)))
        # -------------------------------------------------------- 2. get input for multiple foss selection ends
        
        #save selected criteria
        selected__single_foss = FossCategory.objects.filter(id__in=foss_list).values_list('foss')
        selected__single_foss_grades = grades
        foss_grade_zip = zip(selected__single_foss,selected__single_foss_grades)
        foss_grade = {}
        for foss,grade in foss_grade_zip:
            foss_grade[foss[0]] = grade
        context['foss_grade'] = foss_grade
        context['start_date'] = start_date
        context['end_date'] = end_date
        #end save selected criteria
        # -------------------------------------------------------- 3. get mdl_users satisfying the single mandatory foss criteria (mdlusers)
        mdlusers = MdlUser.objects.using('moodle').all()
        users_id = []
        # foss_mdl_courses dictionary | key : foss id| value : corresponding mdl quiz id
        foss_mdl_courses = FossMdlCourses.objects.filter(foss_id__in=mandatory).values_list('foss','mdlquiz_id')
        mdl_quizzes = list(map(lambda x: x[1], foss_mdl_courses))
        all_quiz_ids = mdl_quizzes #used for filter in testattendance query
        mdl_users = [] #keep track of eligible students
        #get single foss quiz ids
        q1 = mdl_quizzes
        #get multiple foss quiz id
        q2 = []
        for count,elem in enumerate(multiple_fosses):
            fmc = FossMdlCourses.objects.filter(foss_id__in=elem).values_list('mdlquiz_id')
            q3 = list(map(lambda x: x[0], foss_mdl_courses)) 
            q2+=q3
        total_q = q1+q2
        merged = list(itertools.chain(*multiple_fosses))
        multi_fosses = FossCategory.objects.filter(id__in=merged).values_list('foss')
        l = []
        for item in range(len(multiple_grade)):
           l.append((item,multiple_grade[item],multiple_fosses[item])) 
        context['l']=l
        fq = FossCategory.objects.all().values('id','foss')
        fd = {}
        for item in fq:
            fd[str(item['id'])]=item['foss']
        context['fd'] = fd
        if start_date and end_date:
            mdl_users = TestAttendance.objects.filter(mdlquiz_id__in=total_q,test__tdate__range=[start_date,end_date]).values_list('mdluser_id')
            if not mdl_users:
                context['no_data'] = 'No data'
                return render(request,'emp/student_filter.html',context)
        elif start_date:
            mdl_users = TestAttendance.objects.filter(mdlquiz_id__in=total_q,test__tdate__gte=start_date).values_list('mdluser_id')
            if not mdl_users:
                context['no_data'] = 'No data'
                return render(request,'emp/student_filter.html',context)
        elif end_date:
            mdl_users = TestAttendance.objects.filter(mdlquiz_id__in=total_q,test__tdate__lte=end_date).values_list('mdluser_id')
            if not mdl_users:
                context['no_data'] = 'No data'
                return render(request,'emp/student_filter.html',context)
        if(mdl_users):
            mdl_users = list(itertools.chain(*mdl_users))
        

        q = []
        if foss_mdl_courses:
            for item in foss_mdl_courses:
                if mdl_users:
                    q = MdlUser.objects.filter(Q(mdlquizgrades__quiz=item[1]) & Q(mdlquizgrades__grade__gt=mandatory[item[0]]),id__in=mdl_users).values_list('id')
                else:
                    q = MdlUser.objects.filter(Q(mdlquizgrades__quiz=item[1]) & Q(mdlquizgrades__grade__gt=mandatory[item[0]])).values_list('id')
                mdl_users = list(itertools.chain(*q)) #To get a single list from a list of tuples (q)
        else:
            pass
        if any(multiple_fosses):
                
            # for item in range(int(num)):
            for count,elem in enumerate(multiple_fosses):
                foss_mdl_courses = FossMdlCourses.objects.filter(foss_id__in=elem).values_list('mdlquiz_id')
                mdl_quizzes = list(map(lambda x: x[0], foss_mdl_courses))
                all_quiz_ids += mdl_quizzes
                if mdl_users:
                    q = MdlUser.objects.filter(Q(mdlquizgrades__quiz__in=mdl_quizzes) & Q(mdlquizgrades__grade__gt=multiple_grade[count]),id__in=mdl_users).values_list('id')
                else:
                    q = MdlUser.objects.filter(Q(mdlquizgrades__quiz__in=mdl_quizzes) & Q(mdlquizgrades__grade__gt=multiple_grade[count])).values_list('id')
                mdl_users = list(itertools.chain(*q))
            # -------------------------------------------------------- 3. get mdl_users satisfying the single mandatory foss criteria (mdlusers) ends

            
            # -------------------------------------------------------- 4. users_id : (user_id, user_quiz, grade) satisfying only mandatory quiz, grade criteria
        mdlusers = MdlUser.objects.using('moodle').filter(id__in=mdl_users,mdlquizgrades__quiz__in=all_quiz_ids)
        n_users_id = mdlusers.annotate(quiz=F('mdlquizgrades__quiz')).annotate(grade=F('mdlquizgrades__grade')).values_list('id','firstname','lastname','email','quiz','grade')
        
        context['n_users_id']=n_users_id
        if not n_users_id:
            context['no_data'] = 'No data'
        #make a dictionary : key : quiz_id, value : foss_name
        foss_id_name = FossMdlCourses.objects.all().annotate(foss_name=Subquery(FossCategory.objects.filter(id=OuterRef('foss_id')).values('foss'))).values('foss_id','foss_name','mdlquiz_id')
        fosses = {}
        for item in foss_id_name:
            fosses[item['mdlquiz_id']] = item['foss_name']
        context['fosses']=fosses
        #end
        
    return render(request,'emp/student_filter.html',context)

# landing page views 
@method_decorator(user_passes_test(is_manager), name='dispatch')
class GalleryImageCreate(CreateView):
    model = GalleryImage
    fields = ['desc','event','location','display_on_homepage','active']
    template_name = 'emp/image_gallery.html'

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Image is added successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error in adding image.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        images = GalleryImage.objects.all()
        context['images'] = images
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class GalleryImageUpdate(UpdateView):
    model = GalleryImage
    fields = ['desc','event','location','display_on_homepage','active']
    template_name = 'emp/galleryimage_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        images = GalleryImage.objects.all()
        context['images'] = images
        context['MEDIA'] = settings.MEDIA_ROOT
        return context

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Image is updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error in updating image.')
        return self.render_to_response(self.get_context_data(form=form))

class GalleryImageList(ListView):
    model = GalleryImage
    
    def get_queryset(self):
        queryset = GalleryImage.objects.filter(active=True)
        return queryset


    

@method_decorator(user_passes_test(is_manager), name='dispatch')
class TestimonialCreate(CreateView):
    model = Testimonial
    fields = ['name','about','desc','event','location','display_on_homepage','active']
    template_name = 'emp/testimonial.html'

    def form_valid(self, form):
        try:
            self.object = form.save()
        except Exception as e:
            print(e)
        messages.success(self.request, 'Testimonial is added successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error in adding testimonial.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        testimonials = Testimonial.objects.all()
        context['testimonials'] = testimonials
        return context


@method_decorator(user_passes_test(is_manager), name='dispatch')
class TestimonialUpdate(UpdateView):
    model = Testimonial
    fields = ['name','about','desc','event','location','display_on_homepage','active']
    template_name = 'emp/testimonial_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        testimonials = Testimonial.objects.all()
        context['testimonials'] = testimonials
        context['MEDIA'] = settings.MEDIA_ROOT
        return context

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Testimonial is updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error in updating testimonial.')
        return self.render_to_response(self.get_context_data(form=form))
    

class CompanyList(ListView):
    model = Company
    template_name = 'emp/companies.html'
    
    def get_queryset(self):
        queryset = Company.objects.filter(rating=RATING['VISIBLE_TO_ALL_USERS']) | Company.objects.filter(rating=RATING['DISPLAY_ON_HOMEPAGE'])
        return queryset

class TestimonialsList(ListView):
    model = Testimonial
    template_name = 'emp/list_testimonials.html'
    
    def get_queryset(self):
        queryset = Testimonial.objects.filter(active=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events=Event.objects.filter(id__in=Testimonial.objects.filter(active=True).values('event_id'))
        context['events']=events
        return context
        

class StudentListView(PermissionRequiredMixin,ListView):
    model = Student
    permission_required = 'emp.view_student'
    paginate_by = 500
    
    def get_queryset(self):
        search = self.request.GET.get('name')
        event = self.request.GET.get('event')
        if search:
            if event:
                students_id = [x.student_id for x in JobFairAttendance.objects.filter(event_id=event)]
                return Student.objects.filter(id__in=students_id)
            return Student.objects.filter(Q(user__first_name__icontains=search)|Q(user__last_name__icontains=search)|Q(user__email__icontains=search))
        if event:
            students_id = [x.student_id for x in JobFairAttendance.objects.filter(event_id=event)]
            print(f"\033[92m count students_id ** {len(students_id)}  \033[0m")
            return Student.objects.filter(id__in=students_id).order_by('user__first_name')
        return Student.objects.all().order_by('user__first_name')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_students'] = Student.objects.count()
        event = self.request.GET.get('event')
        if event:
            context['event'] = event
            context['total_event_tudents'] = JobFairAttendance.objects.filter(event_id=event).count()
        return context

@csrf_exempt
def notify_student(request):
    mail_sent = False
    to_mail = request.POST.get('email','')
    # to_mail = 'ankitamk@gmail.com'
    empty_fields = request.POST.get('empty_fields','')
    subject = 'Notification to complete the profile in Job Recommendation System'
    # message = f"Please add below details to complete your profile in Job Recommendation System :\n\n{empty_fields}\n.\nLogin here to update profile : {settings.LOGIN_URL}"
    message = f"""
                Dear Learner,\n
                Your profile  in Job Recommendation System is incomplete and hence you are not eligible for automatic job matches.
                We request you to please add the below details to complete your profile in the Job Recommendation System at the earliest:
                Phone, Address, Education details, Skills, Project work, About, Cover Letter, Resume, Location, Alternate_email,  Phone Number, Photo.
                Login here to update your complete profile : https://jrs.spoken-tutorial.org/login/\n
                """
    try:
        send_mail(subject=subject,message=message,recipient_list=[to_mail],from_email=settings.EMAIL_HOST_USER,fail_silently=False,)
        mail_sent = True
        user = User.objects.filter(email=to_mail)[0]
        prev = Notifications.objects.filter(user=user).count()
        Notifications.objects.create(user=user,mail_order=prev+1)
        try:
            student = Student.objects.get(user__email=to_mail)
            student.notified_date = datetime.datetime.now()
            student.save()
        except Exception as e:
            print(e)
    except Exception as e:
        pass
    if mail_sent:
        try:
            f = open(settings.PROFILE_EMAIL_LOG_FILE, "a")
            f.write(f"1,{to_mail},{datetime.datetime.now()},[{empty_fields}]\n")
            f.close()
        except Exception as e:
            response = JsonResponse({"error": "Mail was sent successfully. But an error occurred while logging the data."})
            response.status_code = 403
            return response
    else:
        try:
            f = open(settings.PROFILE_EMAIL_LOG_FILE, "a")
            f.write(f"0,{to_mail},{datetime.datetime.now()},[{empty_fields}]\n")
            f.close()
            response = JsonResponse({"error": "An error occurred while sending mail."})
            response.status_code = 403
            return response
        except Exception as e:
            response = JsonResponse({"error": "An error occurred while sending mail & logging data."})
            response.status_code = 403
            return response
    return HttpResponse("Success!")

def jobs(request, req_user):
    context={}
    try:
        this_user = User.objects.get(email = req_user)
    except Exception as e:
        raise e
    foss_counter = defaultdict(int)
    if this_user.groups.filter(name='STUDENT'):
        '''
        Right now as we have less jobs data, sending all jobs.
        This will be boosting the motivation in the initial level.
        Later on we can add the filters which are commented.
        '''
        jobShortlist = JobShortlist.objects.filter(spk_user=this_user.student.spk_usr_id)
        job_short_list = get_applied_joblist(this_user.student.spk_usr_id)
        all_jobs = Job.objects.all()
        # applied_jobs = [x.job for x in job_short_list]
        # in_process_jobs = [x.job for x in job_short_list if x.status==JOB_APP_STATUS['RECEIVED_APP']]
        rejected_jobs = [x.job for x in job_short_list if x.status==JOB_APP_STATUS['REJECTED']]
        # reccomended_jobs = get_recommended_jobs(this_user.student)
        # eligible_jobs = reccomended_jobs+applied_jobs
        # non_eligible_jobs = list(set(all_jobs).difference(set(eligible_jobs)))
        eligible_jobs = list(set(all_jobs).difference(set(rejected_jobs)))
        for jobs in all_jobs:
            foss_list = get_foss(jobs.foss)
            for foss in foss_list:
                foss_counter[foss] += foss_list.count(foss)
        # take jobs content and match it with tutorials content
        context["foss_count"]= foss_counter
    tutdict = json.dumps(foss_counter)
    return HttpResponse(tutdict, content_type='application/json')


def get_foss(value):
    if value:
        foss_ids = list(map(int,value.split(',')))
        foss = [FossCategory.objects.get(id=x).foss for x in foss_ids]
        if foss:
            return foss
    return []

def check_mail_status(request,id):
    context = {}
    job = Job.objects.get(id=id)
    email_status = ShortlistEmailStatus.objects.filter(job_id=job.id)
    context['job'] = job
    context['email_status'] = email_status
    d = dict()
    for log in email_status:
        log_file_location=os.path.join(settings.BASE_DIR,log.log_file)
        try:
            file = open(log_file_location)
            csvreader = csv.reader(file)
            rows = []
            
            for row in csvreader:
                rows.append(row)
            file.close()
            d[log] = rows
        except Exception as e:
            print(f"{e}")
        context['log'] = d
    return render(request,'emp/mail_status.html',context)

@csrf_exempt
def update_jobfair_student_status(request):
    # data = {}
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            jobfair_id = data['jobfair_id']
            email = data['email']
            enrolled = data['enrolled']#ToDo - if we give unenroll option later
            student = Student.objects.get(user__email=email)
            jobfair = JobFair.objects.get(id=jobfair_id)
            JobFairAttendance.objects.create(event=jobfair.event,student=student)
            return JsonResponse({'message': 'Student enrolled successfully.'}, status=200)
        except Exception as e:
            print(f"Exception : {e}")
            return JsonResponse({'error': 'Error occured while enrolling.'}, status=400)