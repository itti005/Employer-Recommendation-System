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
from django.views.generic.edit import CreateView,UpdateView,ModelFormMixin,FormMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse, JsonResponse
from .filterset import CompanyFilterSet,JobFilter
from .forms import ACTIVATION_STATUS, JobSearchForm, JobApplicationForm
import numpy as np
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings
from django.forms import HiddenInput
from django.template.defaultfilters import slugify

APPLIED = 0 # student has applied but not yet shortlisted by HR Manager
APPLIED_SHORTLISTED = 1 # student has applied & shortlisted by HR Manager



#show job application status to HR
def get_job_app_status(job):
    job_shortlist = JobShortlist.objects.filter(job=job)



def get_recommended_jobs(student):
    #get jobs having status 0 & last app submission date greater than equal to today
    jobs = Job.objects.filter(last_app_date__gte=datetime.datetime.now(),status=1)
    applied_jobs = [x.job for x in get_applied_joblist(student.spk_usr_id)]
    jobs = [x for x in jobs if x not in applied_jobs ]
    scores = fetch_student_scores(student)
    if scores:
        mdl_user_id = scores[0]['mdl'].userid
    student_foss = [d['foss'] for d in scores]  #fosses for which student grade is available
    rec_jobs = []
    spk_student = SpokenStudent.objects.get(user_id=student.spk_usr_id)
    for job in jobs:
        fosses = list(map(int,job.foss.split(',')))
        states = '' if job.state=='0' else list(map(int,job.state.split(',')))
        cities = '' if job.city=='0' else list(map(int,job.city.split(',')))
        insti_type = '' if job.institute_type=='0' else list(map(int,job.institute_type.split(',')))
        valid_fosses = [   d['foss'] for d in scores if str(d['foss']) in job.foss and int(d['grade'])>=job.grade]
        if valid_fosses:
            mdl_quiz_ids = [x.mdlquiz_id for x in FossMdlCourses.objects.filter(foss_id__in=valid_fosses)] #Student passes 1st foss & grade criteria
            test_attendance = TestAttendance.objects.filter(student=spk_student, 
                                                mdlquiz_id__in=mdl_quiz_ids,
                                                test__academic__state__in=states if states!='' else SpokenState.objects.all(),
                                                test__academic__city__in=cities if cities!='' else SpokenCity.objects.all(),
                                                status__gte=3,
                                                test__academic__institution_type__in=insti_type,
                                                test__academic__status__in=[job.activation_status] if job.activation_status else [1,3],
                                                )
            if job.from_date and job.to_date:
                test_attendance = test_attendance.filter(test__tdate__range=[job.from_date, job.to_date])
            elif job.from_date:
                test_attendance = test_attendance.filter(test__tdate__gte=job.from_date)
            if test_attendance:
                rec_jobs.append(job)
    return rec_jobs

# def get_recommended_jobs(student):
#     rec_jobs = []
#     student_foss = set([ x['foss'] for x in fetch_student_scores(student)])
#     jobs = get_awaiting_jobs(student.spk_usr_id)
#     for job in jobs:
#         if not student_foss.isdisjoint(set(map(int, job.foss.split(',')))):
#             rec_jobs.append(job)
#     return rec_jobs

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
	return JobShortlist.objects.filter(spk_user=spk_user_id,status__in=[APPLIED,APPLIED_SHORTLISTED])

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
    applied_jobs = get_applied_joblist(rec_student.spk_usr_id)
    awaiting_jobs = get_awaiting_jobs(rec_student.spk_usr_id)[:5]
    rec_jobs = get_recommended_jobs(rec_student)
    context['applied_jobs'] = applied_jobs if len(applied_jobs)<3 else applied_jobs[:3]
    context['awaiting_jobs'] = awaiting_jobs if len(applied_jobs)<3 else awaiting_jobs[:]
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



class CompanyDetailView(PermissionRequiredMixin,DetailView):
    template_name = 'emp/employer_detail.html'
    permission_required = 'emp.view_company'
    model = Company
    def get_context_data(self, **kwargs):
        print("************ get_context_data ************")
        context = super().get_context_data(**kwargs)
        company_state = SpokenState.objects.get(id=self.object.state_c)
        company_city = SpokenCity.objects.get(id=self.object.city_c)
        context['company_state']=company_state.name
        context['company_city']=company_city.name
        print("************ get_context_data exit ************")
        return context

class CompanyListView(PermissionRequiredMixin,ListView):
    template_name = 'emp/employer_list.html'
    permission_required = 'emp.view_company'
    model = Company
    filterset_class = CompanyFilterSet
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.collection
        context['form'] = self.collection.form
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        self.collection = self.filterset_class(self.request.GET, queryset=queryset)
        return self.collection.qs.distinct()


class CompanyUpdate(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    template_name = 'emp/employer_update_form.html'
    permission_required = 'emp.change_company'
    model = Company
    fields = ['name','emp_name','emp_contact','state_c','city_c','address','phone','email','logo','description','domain','company_size','website'] 
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
        return form

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
        obj = Job.objects.get(title=self.object.title,date_created=self.object.date_created)
        return reverse('job-detail', kwargs={'slug': obj.slug})
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        messages.success(self.request, 'Job information added successfully.')
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

class JobListView(FormMixin,ListView):
    template_name = 'emp/jobs_list.html'
    model = Job
    #filterset_class = JobFilter
    paginate_by = 8
    form_class = JobSearchForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['a']='ab'
        if self.request.user.groups.filter(name='STUDENT'):
            jobShortlist = JobShortlist.objects.filter(spk_user=self.request.user.student.spk_usr_id)
            job_short_list = get_applied_joblist(self.request.user.student.spk_usr_id)
            applied_jobs = [x.job for x in job_short_list]
            accepted_jobs = [x.job for x in job_short_list if x.status==1]
            rejected_jobs = [x.job for x in job_short_list if x.status==0]
            reccomended_jobs = get_recommended_jobs(self.request.user.student)
            context['applied_jobs'] = applied_jobs
            context['accepted_jobs'] = accepted_jobs
            context['rejected_jobs'] = rejected_jobs
            context['reccomended_jobs'] = reccomended_jobs
        return context
    def get_queryset(self):
        queryset = super().get_queryset()
        place = self.request.GET.get('place', '')
        keyword = self.request.GET.get('keyword', '')
        company = self.request.GET.get('company', '')
        job_id = self.request.GET.get('id', '')
        if job_id:
            queryset = Job.objects.filter(id=job_id)
            return queryset
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
        return queryset

class AppliedJobListView(ListView):
    template_name = 'emp/applied_jobs_list.html'
    model = JobShortlist
    # paginate_by = 2
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['APPLIED_SHORTLISTED']=APPLIED_SHORTLISTED
        context['APPLIED']=APPLIED
        return context
    def get_queryset(self):
        queryset = super().get_queryset()
        return JobShortlist.objects.filter(student=self.request.user.student)

class JobUpdate(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    template_name = 'emp/jobs_update_form.html'
    permission_required = 'emp.change_job'
    model = Job
    fields = ['company','title','designation','state_job','city_job','skills','description','domain','salary_range_min',
    'salary_range_max','job_type','benefits','requirements','shift_time','key_job_responsibilities','gender',
    'last_app_date','rating','foss','grade','activation_status','from_date','to_date','state','city','institute_type','status']
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
        self.object = form.save(commit=False)
        self.object.save()
        messages.success(self.request, 'Job information updated successfully.')
        return super(ModelFormMixin, self).form_valid(form)


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
        
        try:
            e = Education.objects.filter(student=student)
            if e:
                education = e[0]
                education.degree = degree_obj
                education.institute = institute
                education.start_year = start_year
                education.end_year = end_year
                education.gpa = gpa
                education.save()
            else:
                education = Education(degree=degree_obj,institute=institute,start_year=start_year,end_year=end_year,gpa=gpa)
                education.save()
                student.education.add(education)
        except IndexError as e:
            education = Education(degree=degree_obj,institute=institute,start_year=start_year,end_year=end_year,gpa=gpa)
            education.save()
            student.education.add(education)
            print(e)
        except Exception as e:
            print(e)
        #education = Education(degree=degree_obj,institute=institute,start_year=start_year,end_year=end_year,gpa=gpa)
        # for i in range(1,6):
        #     try:
        #         degree = request.POST['degree_'+str(i)]
        #         institute = request.POST['institute_'+str(i)]
        #         start_year = request.POST['start_year_'+str(i)]
        #         end_year = request.POST['end_year_'+str(i)]
        #         gpa = request.POST['gpa_'+str(i)]
        #         add_education(student,degree,institute,start_year,end_year,gpa)
        #     except Exception as e:
        #         print(e)

        #education.save()
        #student.education.add(education)
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
        jobApplicationForm = JobApplicationForm()
    context['form']=student_form
    context['education_form']=education_form
    context['jobApplicationForm']=jobApplicationForm
    # return reverse('student_profile_confirm',kwargs={'pk':request.user.student.id,'job':job})
    # return HttpResponseRedirect(reverse('student_profile_confirm',kwargs={'pk':request.user.student.id,'job':job}))
    # return HttpResponse(str(reverse('student_profile_confirm',kwargs={'pk':request.user.student.id,'job':job})))
    return render(request,'emp/student_form.html',context)


def student_profile(request,pk):
    context = {}
    student = Student.objects.get(user=request.user)
    context['student']=student
    context['skills']=Skill.objects.all()
    if request.method=='POST':
        student_form = StudentForm(request.POST)
        education_form = EducationForm(request.POST)
        if student_form.is_valid() and education_form.is_valid():
            student_form,education_form = save_student_profile(request,student)
            messages.success(request, 'Profile uodated successfully')
        else:
            messages.danger(request, 'Error in updating profile')
    else:
        student_form = StudentForm(instance = student)
        try:
            e = Education.objects.filter(student=student).order_by('-end_year')[0]
            education_form = EducationForm(instance = e)
        except IndexError as e:
            education_form = EducationForm()
            print(e)
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

def shortlist_student(request):
    data = {'msg':'true'}
    students = request.GET.get('students', None)
    student_ids = [ int(x) for x in students[:-1].split(',') ]
    job_id = int(request.GET.get('job_id', None))
    job = Job.objects.get(id=job_id)
    try:
        JobShortlist.objects.filter(job=job,student_id__in=student_ids).update(status=1)
        data['updated']=True
    except:
        data['updated']=False
    return JsonResponse(data) 



# def update_job_app_status(spk_user_id,job,flag,student_id):
def update_job_app_status(job,student,spk_user_id):
    job_shortlist = JobShortlist.objects.create(job=job,spk_user=spk_user_id,student=student,status=APPLIED_SHORTLISTED)
    

 #    student = Student.objects.get(id=student_id)
	# if flag:
	# 	job_shortlist = JobShortlist.objects.create(job=job,spk_user=spk_user_id,student=student,status=APPLIED_SHORTLISTED) #student has applied & is eligible for job
	# else:
	# 	job_shortlist = JobShortlist.objects.create(job=job,spk_user=spk_user_id,student=student,status=APPLIED_REJECTED) #student has applied & is not eligible for job
	# return True
	
# class JobShortlistListView(PermissionRequiredMixin,ListView):
class JobAppStatusListView(ListView):
    #permission_required = 'emp.view_job'
    template_name='emp/job_app_status_list.html'
    model = Job
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # job = Job.objects.get(id=self.kwargs['id'])
        # context['job']=job
        return context

def job_app_details(request,id):
    context = {}
    job = Job.objects.get(id=id)
    students_awaiting = [x.student for x in JobShortlist.objects.filter(job_id=id) if x.status==0]
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
    return HttpResponseRedirect(reverse('applied-job-list'))

def check_student_eligibilty(request):
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

    flag = True     #Temp keep
    data['is_eligible'] = flag 

    # update_job_app_status(spk_user_id,job,flag)    #Temp remove
    return JsonResponse(data)

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

