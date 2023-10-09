from django import forms
from spoken.models import *
from .models import Education,Student,Job,Company,Degree,Discipline,Feedback
from django.forms import ModelForm

class DateInput(forms.DateInput):
    input_type = 'date'

ACTIVATION_STATUS = ((None, "--------"),(1, "Active"),(3, "Deactive"))

    
class StudentGradeFilterForm(forms.Form):
    # foss = forms.ModelMultipleChoiceField(queryset=FossCategory.objects.using('spk').filter(id__in=[x.foss.id for x in FossMdlCourses.objects.all()]).order_by('foss'))
    # state = forms.ModelMultipleChoiceField(queryset=SpokenState.objects.using('spk').all(), required=False)
    # city = forms.ModelMultipleChoiceField(queryset=SpokenCity.objects.using('spk').all().order_by('name'), required=False)
    # grade = forms.IntegerField(min_value=0, max_value=100)
    # institution_type = forms.ModelMultipleChoiceField(queryset=InstituteType.objects.using('spk').all().order_by('name'), required=False)
    activation_status = forms.ChoiceField(choices = ACTIVATION_STATUS, required=False)
    from_date = forms.DateField(widget=DateInput(), required=False)
    to_date = forms.DateField(widget=DateInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class JobApplicationForm(forms.Form):
    job_id = forms.IntegerField()
    student = forms.IntegerField()
    spk_user_id = forms.IntegerField()

    


class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EducationForm, self).__init__(*args, **kwargs)
        self.fields['degree'].queryset = Degree.objects.order_by('name')
        self.fields['acad_discipline'].queryset = Discipline.objects.order_by('name')
        self.fields['institute'].queryset = AcademicCenter.objects.order_by('institution_name')[:10]


class PrevEducationForm(EducationForm):
    class Meta:
        model = Education
        fields = '__all__'

class StudentForm(ModelForm):
    OPTIONS = [(True, 'Yes'),(False, 'No'),]
    REL_LOC_CHOICES = [('No', 'No'),('Within the state', 'Within the state'),
                       ('Anywhere in India', 'Anywhere in India'),('Overseas', 'Overseas'),]
    joining_immediate = forms.ChoiceField(widget=forms.RadioSelect,choices=OPTIONS,label='If offered a job, will you be able to join immediately?')
    avail_for_intern = forms.ChoiceField(widget=forms.RadioSelect,choices=OPTIONS,label='Are you interested for an internship?')
    willing_to_relocate = forms.MultipleChoiceField(choices=REL_LOC_CHOICES,widget=forms.CheckboxSelectMultiple,label='Are you willing to relocate based on job requirement?')
    class Meta:
        model = Student
        fields = ['about','github','linkedin','cover_letter','skills','resume','projects',
                  'phone','alternate_email','address','certifications',
                  'joining_immediate','avail_for_intern','willing_to_relocate']

        widgets = {
            'certifications' : forms.Textarea(attrs={'rows':2, 'cols':15,'maxlength':200}),
        }
        help_texts = {
            'certifications' : 'Please mention your certifications as comma seperated values.'
        }

class JobSearchForm(forms.Form):
    keyword = forms.ChoiceField(choices=[]) # give foss names, company names & job titles in dropdown
    place = forms.ChoiceField(choices=[])
    company = forms.ChoiceField(choices=[])
    def __init__(self, choices=(), *args, **kwargs):
        super(JobSearchForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = [x for x in SpokenState.objects.values_list('id','name')]+[x for x in SpokenCity.objects.values_list('id','name')]
        titles_foss_lst=[]
        #get job title & fosses
        self.fields['keyword'].choices = [x for x in Job.objects.values_list('id','title')] + [x for x in FossCategory.objects.values_list('id','foss')]
        self.fields['company'].choices = [x for x in Company.objects.values_list('id','name')]
        print('success')

        
        #foss

        #get company
class ContactForm(ModelForm):
    class Meta:
        model = Feedback
        fields = ['name','email','message']
        widgets = {
            'message' : forms.Textarea(attrs={'rows':3, 'cols':15,'maxlength':500}),
        }

