from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from .views import *


urlpatterns = [
    path('login/', LoginViewCustom.as_view(), name='login'),
	# path('register/success/', LoginView.as_view(), name='register_success'),
    
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', TemplateView.as_view(template_name="profile.html")),
    path('register_user/', register_user, name='register_user'),
    path('validate_student/', validate_student, name='validate_student'),

]

# print("***************** urlpatterns accounts", urlpatterns)