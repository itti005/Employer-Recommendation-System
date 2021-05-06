from django.urls import path
from .views import StudentUpdateView ,StudentGradeFilter

from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('student',views.student_homepage,name="student"),
    path('<pk>/profile',StudentUpdateView.as_view(),name='student_profile'),
    path('employer',views.employer_homepage,name="employer"),
    path('manager',views.manager_homepage,name="manager"),
    path('logout', views.handlelogout, name='logout'),
    path('student_grade_filter', StudentGradeFilter.as_view(), name='student_grade_filter'),

    

   # path('view_profile', views.student_profile_view, name='student_profile_view'),
        ]
