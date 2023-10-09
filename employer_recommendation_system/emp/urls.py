from django.urls import path
from .views import * 
from . import views
from django.urls import  include
from .views import StudentViewSet
from .views import DomainViewSet
from rest_framework.routers import DefaultRouter
from .views import DisciplineViewSet
router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'domains', DomainViewSet)
router.register(r'disciplines', DisciplineViewSet)

    
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(router.urls)),
    path('api/', include(router.urls)),
    path('',views.index,name='index'),
    path('student',views.student_homepage,name="student"),
    path('<pk>/profile/<int:job>',views.student_profile_confirm,name='student_profile_confirm'),
    path('<pk>/profile',views.student_profile,name='student_profile'),
    path('add_student_job_status',views.add_student_job_status,name='add_student_job_status'),
    path('student_profile/<int:id>/<int:job>',views.student_profile_details,name='student_profile_details'),
    path('student_profile_spk/<int:id>',views.student_profile_details_spk,name='student_profile_details_spk'),
    path('student-list',StudentListView.as_view(),name='student-list'),
    path('notify-student-profile/',views.notify_student,name='notify-student-profile'),

    
    path('manager',views.manager_homepage,name="manager"),
    path('shortlist_student',views.shortlist_student,name='shortlist_student'),
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
    path('api/jobs/<req_user>/',views.jobs,name='jobs'),
    ################### jobshortlist
    path('job_application_status/', JobAppStatusListView.as_view(), name='job-app-status'),
    path('job_application_status/<int:id>/', views.job_app_details, name='job-app-detail'),
    path('check_mail_status/<int:id>/', views.check_mail_status, name='check_mail_status'),
    path('logout', views.handlelogout, name='logout'),
    path('<pk>/document', views.document_view, name='document_view'), #resume & cover_letter as 'type' query
    ################### Degree urls : currently only accessible to MANAGER Role : Set conditions via admin
    path('add_degree/', DegreeCreateView.as_view(), name='add_degree'),
    path('<slug:slug>/update-degree/', DegreeUpdateView.as_view(), name='update-degree'),
    ################### Discipline urls : currently only accessible to MANAGER Role : Set conditions via admin
    path('add_discipline/', DisciplineCreateView.as_view(), name='add_discipline'),
    path('<slug:slug>/update-discipline/', DisciplineUpdateView.as_view(), name='update-discipline'),
    # path('discipline/<slug:slug>/', DisciplineDetailView.as_view(), name='discipline-detail'),
    ################### Domain urls : currently only accessible to MANAGER Role : Set conditions via admin
    path('add_domain/', DomainCreateView.as_view(), name='add_domain'),
    path('<slug:slug>/update-domain/', DomainUpdateView.as_view(), name='update-domain'),
    ################### Domain urls : currently only accessible to MANAGER Role : Set conditions via admin
    path('add_job_type/', JobTypeCreateView.as_view(), name='add_job_type'),
    path('<slug:slug>/update_job_type/', JobTypeUpdateView.as_view(), name='update_job_type'),

    ################### ajax
    path('ajax-state-city/', views.ajax_state_city, name='ajax_state_city'),
    path('ajax-institute-list/', views.ajax_institute_list, name='ajax_institute_list'),
    path('ajax-send-mail/', views.ajax_send_mail, name='ajax_send_mail'),
    path('ajax-get-state-city/', views.ajax_get_state_city, name='ajax_get_state_city'),
    path('ajax-contact-form/', views.ajax_contact_form, name='ajax_contact_form'),
    path('update_jobfair_student_status/', views.update_jobfair_student_status, name='update_jobfair_student_status'),


    path('student_filter',views.student_filter,name='student_filter'),

    #landing page
    path('add_image', GalleryImageCreate.as_view(),name='add_image' ),
    path('image-gallery', GalleryImageList.as_view(),name='image_gallery' ),
    # path('image_details/<int:pk>', GalleryImageDetail.as_view(),name='gallery_image_detail' ),
    path('update_image/<int:pk>', GalleryImageUpdate.as_view(),name='update_image' ),
    path('add_testimonial', TestimonialCreate.as_view(),name='add_testimonial' ),
    # path('image_details/<int:pk>', GalleryImageDetail.as_view(),name='gallery_image_detail' ),
    path('update_testimonial/<int:pk>', TestimonialUpdate.as_view(),name='update_testimonial' ),
    path('list_testimonials/', TestimonialsList.as_view(),name='list_testimonials' ),
        # Your other URL patterns
    # path('api/', include(router.urls)),
    

#     path('', include(router.urls)),


    # path('<slug:slug>/', GalleryImageDetail.as_view(), name='gallery-image-detail'),
    # path('degree/<slug:slug>/', DegreeDetailView.as_view(), name='degree-detail'),
    # path('degree/', CompanyListView.as_view(), name='company-list'),
    # path('degree/<slug:slug>/', CompanyDetailView.as_view(), name='company-detail'),
    
    ################### public urls
    path('companies',CompanyList.as_view(),name='companies'),
]
