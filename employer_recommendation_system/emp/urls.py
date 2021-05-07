from django.urls import path
from .views import * 
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('student',views.student_homepage,name="student"),
    path('<pk>/profile',StudentUpdateView.as_view(),name='student_profile'),
    path('employer',views.employer_homepage,name="employer"),
    path('manager',views.manager_homepage,name="manager"),
    path('logout', views.handlelogout, name='logout'),
    path('student_grade_filter', StudentGradeFilter.as_view(), name='student_grade_filter'),
    ################### company urls
    path('add_company/', CompanyCreate.as_view(), name='add_company'),
    path('<slug:slug>/update-company/', CompanyUpdate.as_view(), name='update-company-detail'),
    path('company_list/', CompanyListView.as_view(), name='company-list'),
    path('company/<slug:slug>/', CompanyDetailView.as_view(), name='company-detail'),
    ################### job urls
    path('add_job/', JobCreate.as_view(), name='add_job'),
    path('<slug:slug>/update-job/', JobUpdate.as_view(), name='update-job-detail'),
    path('job_list/', JobListView.as_view(), name='job-list'),
    path('job/<slug:slug>/', JobDetailView.as_view(), name='job-detail'),

    

   # path('view_profile', views.student_profile_view, name='student_profile_view'),
        ]
