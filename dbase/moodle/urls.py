from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from  .import views
from .views import *
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.conf.urls import url

urlpatterns = [
    url(r'get_grades/', views.MdlQuizGradesList.as_view()),
    
]


