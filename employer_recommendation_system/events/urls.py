from django.urls import path
from .views import * 
from . import views
 

urlpatterns = [
    
    path('create',EventCreateView.as_view(),name='event-create'),
    path('event-detail/<pk>',EventDetailView.as_view(),name='event-detail'),
    path('update-job/<pk>/', EventUpdateView.as_view(), name='update-event-detail'),
    path('events', EventListView.as_view(), name='event-list'),
    path('event/<pk>', EventPageView.as_view(), name='public-event'),
    path('jobfair/<pk>', views.display_jobfair, name='jobfair'),
    path('confirmation/', Confirmation.as_view(), name='confirmation'),
    path('job-fair-students/', External.as_view(), name='job-fair-students'),
    path('data/', data_stats, name='data_stats'),
    path('details/', jobfair_data, name='jobfair_data'),
    
] 
