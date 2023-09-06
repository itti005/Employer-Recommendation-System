# from rest_framework import serializers
# from emp.models import Company

# class CompanySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Company
#         fields = '__all__'

from rest_framework import serializers
# from emp.serializers import CompanySerializer  
# from emp.serializers import JobSerializer 
# from .models import Registration
from emp.models import Company
from emp.models import Job
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'