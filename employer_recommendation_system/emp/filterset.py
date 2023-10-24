import django
import django_filters
from django.db import models  
from .models import Student, Company, Job ,Domain, Discipline ,Education,Skill,Project
from emp import models
class CompanyFilterSet(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Company
        fields = ['name']

    def __init__(self, data, *args, **kwargs):
        data = data.copy()
        #data.setdefault('format', 'paperback')
        data.setdefault('order', '-added')
        super().__init__(data, *args, **kwargs)


class JobFilter(django_filters.FilterSet):
	class Meta:
		model = Job
        #fields = '__all__'
		fields = {'title':['icontains',],
            'state_job':['exact'],}


class DomainFilter(django_filters.FilterSet):
    class Meta:
        model = Domain
        fields = '__all__'  # Include all fields for filtering

class DisciplineFilter(django_filters.FilterSet):
    class Meta:
        model = Discipline
        fields = '__all__'


class StudentFilter(django_filters.FilterSet):
  name = django_filters.CharFilter(lookup_expr='icontains', label='Name')  # For example, searching by name
  phone = django_filters.CharFilter(lookup_expr='icontains', label='Phone')  # For phone
  address = django_filters.CharFilter(lookup_expr='icontains', label='Address')  # For address
  education = django_filters.ModelMultipleChoiceFilter(field_name='education__name', to_field_name='name', queryset=Education.objects.all(), label='Education')  # For education
  skills = django_filters.ModelMultipleChoiceFilter(field_name='skills__name', to_field_name='name', queryset=Skill.objects.all(), label='Skills')  # For skills
  projects = django_filters.ModelMultipleChoiceFilter(field_name='projects__name', to_field_name='name', queryset=Project.objects.all(), label='Projects')  # For projects
  github = django_filters.CharFilter(lookup_expr='icontains', label='GitHub')  # For GitHub
  linkedin = django_filters.CharFilter(lookup_expr='icontains', label='LinkedIn')  # For LinkedIn

class Meta:
        model = Student