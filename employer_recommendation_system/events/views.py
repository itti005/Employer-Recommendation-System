from django.db.models import fields
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
    print(f"pk *************** here *************** {pk}")
    try:
        jobfair = JobFair.objects.get(id=pk)
        context['jobfair'] = jobfair
    except Exception as e:
        raise PermissionDenied()
    return render(request,'events/jobfair.html',context)