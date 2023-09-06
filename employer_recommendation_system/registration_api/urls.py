# from django.urls import path
# from .views import CompanyListCreateView
# from .views import RegistrationCreateView
# from .views import (
#     RegistrationCreateView, RegistrationListView, RegistrationDetailView,
#     CompanyCreateView, CompanyListView, CompanyDetailView
# )
# urlpatterns = [
#     path('api/companies/', CompanyListCreateView.as_view(), name='company-list-create'),
#     # path('api/registrations/create/', RegistrationCreateView.as_view(), name='registration-create'),

#     path('api/registrations/', RegistrationListView.as_view(), name='registration-list'),
#     path('api/registrations/create/', RegistrationCreateView.as_view(), name='registration-create'),
#     path('api/registrations/<int:pk>/', RegistrationDetailView.as_view(), name='registration-detail'),

#     path('api/companies/', CompanyListView.as_view(), name='company-list'),
#     path('api/companies/create/', CompanyCreateView.as_view(), name='company-create'),
#     path('api/companies/<int:pk>/', CompanyDetailView.as_view(), name='company-detail'),
# ]
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import  CompanyViewSet
from .views import  JobViewSet
router = DefaultRouter()
# router.register(r'registrations', RegistrationViewSet)
router.register(r'companies', CompanyViewSet)
router.register(r'Jobs', JobViewSet)
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/Jobs/', include(router.urls)),
]









