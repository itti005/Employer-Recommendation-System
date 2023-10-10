# from rest_framework import serializers
# from .models import Company
# from .models import Job

# class CompanySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Company
#         fields = '__all__'


# class JobSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Job
#         fields = '__all__'
from rest_framework import serializers
from emp.models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'

from emp.models import Domain

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = '__all__'


from emp.models import Discipline

class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = '__all__'
