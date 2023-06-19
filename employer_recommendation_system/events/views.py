from django.db.models import Count,Case, When, Value, IntegerField
from django.shortcuts import render
from django.views.generic.edit import CreateView,ModelFormMixin,UpdateView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from .models import Event
from django.views.generic.detail import DetailView
from .models import *
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from emp.helper import is_manager
from django.core.exceptions import PermissionDenied
from django.views.generic.base import View
from spoken.models import SpokenStudent, StudentBatch, StudentMaster, TestAttendance, SpokenState, SpokenCity, FossCategory
from emp.models import Degree, Discipline
# Create your views here.
# CBVs for event

@method_decorator(user_passes_test(is_manager), name='dispatch')
class EventCreateView(CreateView):
    model = Event
    fields = '__all__'

    def get_success_url(self):
        return reverse('event-detail', kwargs={'pk': self.object.id})
    
    def form_valid(self, form):
        print('****************  form is valid **************** ')
        print(form)
        self.object = form.save(commit=False)
        self.object.added_by = self.request.user
        self.object.save()
        # messages.success(self.request, 'Company information added successfully.')
        return super(ModelFormMixin, self).form_valid(form)
    
    def test_func(self):
        return self.request.user.groups
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context
    
    def form_invalid(self, form):
        print('****************  form is valid **************** ')
        return self.render_to_response(self.get_context_data(form=form))

    # def get_form(self, form_class=None):
    #     if form_class is None:
    #         form_class = self.get_form_class()
       
    #     return form

class EventDetailView(DetailView):
    model = Event
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("************* HERE ***************")
        # context['now'] = timezone.now()
        return context

@method_decorator(user_passes_test(is_manager), name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    fields = '__all__'
    
class EventListView(ListView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['now'] = timezone.now()
        return context
    def get_queryset(self):
        queryset = Event.objects.filter(status=True)
        return queryset

class EventPageView(TemplateView):
    template_name = "events/event.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print("**************************")
        event_pk = kwargs.get('pk')
        print(event_pk)
        event = Event.objects.get(id=event_pk)
        brochures = Brochure.objects.filter(event=event)
        context['event'] = event
        context['brochures'] = brochures
        testimonials = Testimonial.objects.filter(event=event)
        context['testimonials'] = testimonials
        event_images = GalleryImage.objects.filter(event=event)
        context['event_images'] = event_images
        print("**************************")
        return context

def display_jobfair(request,pk):
    context = {}
    try:
        jobfair = JobFair.objects.get(id=pk)
        context['jobfair'] = jobfair
        if request.user.is_authenticated:
            student_lst = Student.objects.filter(user=request.user)
            if student_lst:
                active_event = Event.objects.filter(status=1,type='JOBFAIR').order_by('-start_date').first()
                # context['is_registered_for_jobfair'] = JobFair.objects.filter(event=active_event,students=student_lst[0]).exists()
                context['is_registered_for_jobfair'] = JobFairAttendance.objects.filter(event=active_event,student=student_lst[0]).exists()
            
    except Exception as e:
        raise PermissionDenied()
    return render(request,'events/jobfair.html',context)

class Confirmation(TemplateView):
    template_name = 'events/confirmation.html'
    
class External(TemplateView):
    template_name = 'events/external.html'
        
def data_stats(request):

    context = {}
    active_event = Event.objects.filter(status=1,type='JOBFAIR').order_by('-start_date').first()
    
    query_set_attendance = JobFairAttendance.objects.filter(event=active_event)
    total_students_enrolled = query_set_attendance.count()
    context['total_students_enrolled'] = total_students_enrolled
    gender_based = query_set_attendance.values('student__gender').annotate(count=Count('id')).values_list('student__gender','count')
    context['gender_based_count'] = gender_based
    attendance = query_set_attendance.filter(student__spk_usr_id__isnull=False)
    spk_student_id = [x.student.spk_student_id for x in attendance]
    state_based_count = StudentMaster.objects.filter(
        student_id__in=[x.student.spk_student_id for x in attendance]).values('batch__organiser__academic__state__name').annotate(
            count=Count('id')).values_list('batch__organiser__academic__state__name', 'count').order_by('-count')
    context['state_based_count'] = state_based_count
    city_based_count = StudentMaster.objects.filter(
        student_id__in=[x.student.spk_student_id for x in attendance]).values(
            'batch__organiser__academic__state__name','batch__organiser__academic__city__name').annotate(
                count=Count('id')).values_list('batch__organiser__academic__city__name', 'batch__organiser__academic__state__name','count').order_by('-count')
    context['city_based_count'] = city_based_count
    jrs_students_id = query_set_attendance.values_list('student_id')
    degree_based_dist = Student.objects.filter(id__in=jrs_students_id).values('education__degree__name').annotate(
        count=Count('id')
    ).values_list('education__degree__name','count').order_by('-count')
    discipline_based_dist = Student.objects.filter(id__in=jrs_students_id).values('education__acad_discipline__name').annotate(
        count=Count('id')
    ).values_list('education__acad_discipline__name','count').order_by('-count')
    context['degree_based_dist'] = degree_based_dist
    context['discipline_based_dist'] = discipline_based_dist
    
    skill_distribution = Student.objects.filter(id__in=jrs_students_id,skills__name__isnull=False).values(
        'skills__name').annotate(count=Count('id')).values_list('skills__name','count').order_by('-count')
    skillgrp_distribution = Student.objects.filter(id__in=jrs_students_id,skills__group__name__isnull=False).values(
        'skills__group__name').annotate(count=Count('id')).values_list('skills__group__name','count').order_by('-count')
    context['skill_distribution'] = skill_distribution
    context['skillgrp_distribution'] = skillgrp_distribution
    students = query_set_attendance.values('student__user__email','student__phone')
    foss_based_distribution = TestAttendance.objects.filter(student_id__in=spk_student_id,mdlgrade__gte=60).values(
        'test__foss__foss').annotate(count=Count('id')).values_list('test__foss__foss','count').order_by('-count')
    context['foss_based_distribution'] = foss_based_distribution
    context['foss_based_distribution'] = foss_based_distribution
    states_data = SpokenState.objects.all().values_list('id','name').order_by('name')
    foss_data = FossCategory.objects.all().values_list('id','foss').order_by('foss')
    degree_data = Degree.objects.values_list('id','name').order_by('name')
    discipline_data = Discipline.objects.values_list('id','name').order_by('name')
    context['states_data'] = states_data
    context['foss_data'] = foss_data
    context['degree_data'] = degree_data
    context['discipline_data'] = discipline_data
    
    if request.method == 'POST':
        context['is_post'] = True
        active_event
        type = request.POST.get('type')
        if type == 'all':
            jrs_students = Student.objects.all()
        elif type == 'jobfair':
            jrs_students = Student.objects.filter(id__in=jrs_students_id)
        states = request.POST.getlist('states')
        mdlgrade = request.POST.get('mdlgrade',0)
        ta = TestAttendance.objects.filter(mdlgrade__gte=mdlgrade)
        if not '0' in states:
            ta = TestAttendance.objects.filter(test__academic__state_id__in=states)
        fosses = request.POST.getlist('fosses')
        if not '0' in fosses:
            ta = ta.filter(test__foss__id__in=fosses)
        jrs_students = Student.objects.all()
        degrees = request.POST.getlist('degree')
        disciplines = request.POST.getlist('discipline')
        if not '0' in degrees:
            jrs_students = jrs_students.filter(education__degree_id__in=degrees)
        if not '0' in disciplines:
            jrs_students = jrs_students.filter(education__degree_id__in=disciplines)
        ta = ta.filter(student_id__in=[x.spk_student_id for x in jrs_students])
        query_students = SpokenStudent.objects.filter(id__in=[x.student_id for x in ta])
        studentmaster = StudentMaster.objects.filter(
            student_id__in=[x.id for x in query_students]).values_list('student_id',
                'student__user__email','batch__academic__institution_name','batch__academic__state__name','batch__academic__city__name')
        context['studentmaster'] = studentmaster
        context['students'] = query_students
        context['student_count'] = studentmaster.count()
        #Pivot #ToDo
        jrs_students_for_jobfair = Student.objects.filter(id__in=[x.student_id for x in query_set_attendance])
        spk_student_ids_for_jobfair = [x.spk_student_id for x in jrs_students_for_jobfair]
        ta_pivot = TestAttendance.objects.filter(student_id__in=spk_student_ids_for_jobfair).values('student_id')

        
        
    return render(request,'events/data_stats.html',context)    

