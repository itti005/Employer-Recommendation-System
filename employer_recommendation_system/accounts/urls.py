from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from .views import *


urlpatterns = [
    # path('', LoginViewCustom.as_view(redirect_authenticated_user=True), name='login'),
    path('login/', LoginViewCustom.as_view(redirect_authenticated_user=True), name='login'),
	# path('register/success/', LoginView.as_view(), name='register_success'),
    # path('register/', RegisterView.as_view(), name='register'), # for employer
    # path('profile/', TemplateView.as_view(template_name="profile.html")),
    # path('register_student/', register_student, name='register_student'), 
    # path('validate_student/', validate_student, name='validate_student'),
    path('forgot-password/', reset_password, name='reset_password'),
    path('accounts/change-password/', change_password, name='change_password'),

]

