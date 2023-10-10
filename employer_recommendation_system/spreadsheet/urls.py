from django.urls import path
from . import views

urlpatterns = [
    path('fetch-google-sheet/<str:spreadsheet_id>/', views.fetch_google_sheet, name='fetch_google_sheet'),
]
