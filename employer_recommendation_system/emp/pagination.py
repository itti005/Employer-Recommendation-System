from rest_framework.pagination import PageNumberPagination
class CustomPagination(PageNumberPagination):
    page_size = 1#Set the number of items per page
