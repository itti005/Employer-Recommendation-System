from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .models import *
from emp.models import Student as RecStudent
from spoken.models import TestAttendance, FossMdlCourses,FossCategory,Profile
from moodle.models import MdlQuizGrades
from django.views.generic.edit import UpdateView
from spoken.models import SpokenStudent as SpkStudent 
from spoken.models import SpokenUser as SpkUser 
from django.views.generic import FormView
from emp.forms import StudentGradeFilterForm, EducationForm,StudentForm
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import CreateView,UpdateView,ModelFormMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin


def student_homepage(request):
    context={}
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
    except:
        pass
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
                    test__academic__state__in=state if state else State.objects.using('spk').all(),
                    test__academic__city__in=city if city else City.objects.using('spk').all(),
                    status__gte=3, 
                    test__academic__institution_type__in=institution_type if institution_type else InstituteType.objects.using('spk').all(), 
                    test__academic__status__in=[activation_status] if activation_status else [1,3]
                    )

                if from_date and to_date:
                    test_attendance = test_attendance.filter(test__tdate__range=[from_date, to_date])
                elif from_date:
                    test_attendance = test_attendance.filter(test__tdate__gte=from_date)
                filter_ta=[]

                for i in range(test_attendance.count()):
                    if not dictgrade[test_attendance[i].mdluser_id][test_attendance[i].mdlquiz_id][1]:
                        dictgrade[test_attendance[i].mdluser_id][test_attendance[i].mdlquiz_id][1] = True
                        filter_ta.append(test_attendance[i])
                return {'mdl_user_grade': dictgrade, 'test_attendance': filter_ta, "count":len(filter_ta)}
            except FossMdlCourses.DoesNotExist:
                return None
        return None
#---------------- CBV for Create, Detail, List, Update for Company starts ----------------#
class CompanyCreate(PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    template_name = 'emp/employer_form.html'
    permission_required = 'emp.add_company'
    model = Company
    fields = ['name','emp_name','emp_contact','state','city','address','phone','email','logo','description','domain','company_size','website'] 
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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
class CompanyUpdate(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    template_name = 'emp/employer_update_form.html'
    permission_required = 'emp.change_company'
    model = Company
    fields = ['name','emp_name','emp_contact','state','city','address','phone','email','logo','description','domain','company_size','website'] 
    success_message ="%(name)s was updated successfully"
#---------------- CBV for Create, Detail, List, Update for Jobs starts ----------------#
class JobCreate(PermissionRequiredMixin,SuccessMessageMixin,CreateView):
    template_name = 'emp/jobs_form.html'
    permission_required = 'emp.add_job'
    model = Job
    fields = ['company','title','designation','state','city','skills','description','domain','salary_range_min','salary_range_max','job_type','benefits','requirements','shift_time','key_job_responsibilities','gender']
    
    success_message ="%(title)s job was created successfully"
    def get_success_url(self):
        return reverse('job-detail', kwargs={'slug': self.object.slug})
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return super(ModelFormMixin, self).form_valid(form)

class JobDetailView(PermissionRequiredMixin,DetailView):
    template_name = 'emp/jobs_detail.html'
    permission_required = 'emp.view_job'
    model = Job
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
class JobListView(PermissionRequiredMixin,ListView):
    template_name = 'emp/jobs_list.html'
    permission_required = 'emp.view_job'
    model = Job
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
class JobUpdate(PermissionRequiredMixin,SuccessMessageMixin,UpdateView):
    template_name = 'emp/jobs_update_form.html'
    permission_required = 'emp.change_job'
    model = Job
    fields = ['company','title','designation','state','city','skills','description','domain','salary_range_min','salary_range_max','job_type','benefits','requirements','shift_time','key_job_responsibilities','gender']
    success_message ="%(title)s was updated successfully"

def student_profile(request,pk):
    context = {}
    student = Student.objects.get(user=request.user) 
    context['skills']=Skill.objects.all()
    if request.method=='POST':
        student_form = StudentForm(request.POST)
        education_form = EducationForm(request.POST)
        if student_form.is_valid() and education_form.is_valid():
            student.about = student_form.cleaned_data['about']
            student.github = student_form.cleaned_data['github']
            student.experience = student_form.cleaned_data['experience']
            student.linkedin = student_form.cleaned_data['linkedin']
            student.save()
            skills = request.POST['skills_m']
            skills = skills.split(',')
            for item in skills:
                s = Skill.objects.get(name=item)
                student.skills.add(s)
            degree = request.POST['degree']
            degree_obj = Degree.objects.get(id=degree)
            institute = request.POST['institute']
            institute_obj = AcademicCenter.objects.get(id=institute)
            start_year = education_form.cleaned_data['start_year']
            end_year = education_form.cleaned_data['end_year']
            gpa = education_form.cleaned_data['gpa']
            education = Education(degree=degree_obj,institute=institute_obj,start_year=start_year,end_year=end_year,gpa=gpa)
            education.save()
            student.education.add(education)
    else:
        student_form = StudentForm()
        education_form = EducationForm()
    context['form']=student_form
    context['student']=student
    context['education_form']=education_form
    return render(request,'emp/student_form.html',context)