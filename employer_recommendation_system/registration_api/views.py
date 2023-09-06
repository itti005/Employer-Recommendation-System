# from rest_framework import generics
# from emp.models import Company
# from .models import Registration
# from .serializers import RegistrationSerializer
# from .serializers import CompanySerializer

# class CompanyListCreateView(generics.ListCreateAPIView):
#     queryset = Company.objects.all()
#     serializer_class = CompanySerializer

# class RegistrationCreateView(generics.CreateAPIView):
#     queryset = Registration.objects.all()
#     serializer_class = RegistrationSerializer

# class RegistrationListView(generics.ListAPIView):
#     queryset = Registration.objects.all()
#     serializer_class = RegistrationSerializer

# class RegistrationDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Registration.objects.all()
#     serializer_class = RegistrationSerializer

# class CompanyCreateView(generics.CreateAPIView):
#     queryset = Company.objects.all()
#     serializer_class = CompanySerializer

# class CompanyListView(generics.ListAPIView):
#     queryset = Company.objects.all()
#     serializer_class = CompanySerializer

# class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Company.objects.all()
#     serializer_class = CompanySerializer
from rest_framework import viewsets
# from .models import Registration
from rest_framework import status
from rest_framework.response import Response
from emp.models import Company
from emp.models import Job
from .serializers import CompanySerializer,JobSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print(instance)
        instance.status = 0
        instance.save()
   
        return Response(status=status.HTTP_204_NO_CONTENT)
    filterset_fields = {
        'name': ['exact', 'icontains'],  # Filter by exact or case-insensitive partial match
        'state_c': ['exact'],  # Filter by exact match for state_c field
        'city_c': ['exact'],   # Filter by exact match for city_c field
        'company_size': ['exact'],  # Filter by exact match for company_size field
    }

    search_fields = ['name', 'description', 'address', 'email']  

    # Enable ordering
    ordering_fields = ['name', 'state_c', 'city_c', 'company_size', 'date_registered']  
# def get_queryset(self):
#     return Post.objects.all()
class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    filterset_fields = {
        'title': ['exact', 'icontains'],  # Filter by exact or case-insensitive partial match
        # 'location': ['exact', 'icontains'],  # Filter by exact or case-insensitive partial match
        'requirements': ['exact', 'icontains'],  # Filter by exact or case-insensitive partial match
    }

   
    search_fields = ['title', 'location', 'requirements']  
 
    ordering_fields = ['title', 'location', 'requirements', 'date_posted']  

