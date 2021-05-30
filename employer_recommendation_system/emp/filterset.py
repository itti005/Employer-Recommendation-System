import django_filters
from .models import Company, Job
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