from django import forms
from spoken.models import *
from .models import Education,Student
from django.forms import ModelForm

class DateInput(forms.DateInput):
    input_type = 'date'

ACTIVATION_STATUS = ((None, "--------"),(1, "Active"),(3, "Deactive"))

class StudentGradeFilterForm(forms.Form):
    foss = forms.ModelMultipleChoiceField(queryset=FossCategory.objects.using('spk').all())
    state = forms.ModelMultipleChoiceField(queryset=SpokenState.objects.using('spk').all(), required=False)
    city = forms.ModelMultipleChoiceField(queryset=SpokenCity.objects.using('spk').all().order_by('name'), required=False)
    grade = forms.IntegerField(min_value=0, max_value=100)
    institution_type = forms.ModelMultipleChoiceField(queryset=InstituteType.objects.using('spk').all(), required=False)
    activation_status = forms.ChoiceField(choices = ACTIVATION_STATUS, required=False)
    from_date = forms.DateField(widget=DateInput(), required=False)
    to_date = forms.DateField(widget=DateInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = '__all__'

class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['about','experience','github','linkedin','cover_letter','skills']

class DateInput(forms.DateInput):
    input_type = 'date'
