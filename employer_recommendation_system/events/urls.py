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

    
] 
