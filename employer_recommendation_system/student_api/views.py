# # from django.shortcuts import render
# from rest_framework import viewsets, pagination
# from emp.models import Student
# from .serializers import StudentSerializer
# from student_api.pagination import CustomPagination

# class StudentViewSet(viewsets.ModelViewSet):
#     queryset = Student.objects.all()
#     serializer_class = StudentSerializer
#     pagination_class = CustomPagination  # Set the custom pagination class


# class CustomPagination(pagination.PageNumberPagination):
#     page_size = 1 # Set the number of items per page
#     page_size_query_param = 'page_size'
#     # max_page_size = 100
