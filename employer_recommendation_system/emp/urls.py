from django.urls import path
from .views import * 
from . import views

urlpatterns = [
    # path('',views.index,name='index'),
    path('student',views.student_homepage,name="student"),
    path('<pk>/profile/<int:job>',views.student_profile_confirm,name='student_profile_confirm'),
    path('<pk>/profile',views.student_profile,name='student_profile'),
    path('add_student_job_status',views.add_student_job_status,name='add_student_job_status'),
    path('student_profile/<int:id>/<int:job>',views.student_profile_details,name='student_profile_details'),
    path('manager',views.manager_homepage,name="manager"),
    path('shortlist_student/',views.shortlist_student,name='shortlist_student'),
    ################### company urls : currently only accessible to MANAGER Role : Set conditions via admin
    path('add_company/', CompanyCreate.as_view(), name='add_company'),
    path('<slug:slug>/update-company/', CompanyUpdate.as_view(), name='update-company-detail'),
    path('company_list/', CompanyListView.as_view(), name='company-list'),
    path('company/<slug:slug>/', CompanyDetailView.as_view(), name='company-detail'),
    ################### job urls
    path('add_job/', JobCreate.as_view(), name='add_job'),
    path('<slug:slug>/update-job/', JobUpdate.as_view(), name='update-job-detail'),
    path('job_list/', JobListView.as_view(), name='job-list'),
    path('my_jobs/', views.student_jobs, name='student_jobs'),
    path('job/<slug:slug>/', JobDetailView.as_view(), name='job-detail'),
    path('job_listings/', JobListingView.as_view(), name='job-listing'),
    ################### jobshortlist
    path('job_application_status/', JobAppStatusListView.as_view(), name='job-app-status'),
    path('job_application_status/<int:id>/', views.job_app_details, name='job-app-detail'),
    path('ajax-state-city/', views.ajax_state_city, name='ajax_state_city'),
    path('logout', views.handlelogout, name='logout'),

    # path('employer',views.employer_homepage,name="employer"),
]
