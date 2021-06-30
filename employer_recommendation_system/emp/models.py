from django.db import models
from django.conf import settings
import datetime
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.urls import reverse
from spoken.models import AcademicCenter
import os
from spoken.models import SpokenUser, SpokenState, SpokenCity


# Create your models here.
ACTIVATION_STATUS = ((None, "--------"),(1, "Active"),(3, "Deactive"))
GENDER = [('f','F-Female Candidates'),('m','M-Male Candidates'),('a','No Criteria'),]
START_YEAR_CHOICES = []
END_YEAR_CHOICES = []
for r in range(2000, (datetime.datetime.now().year+4)):
    START_YEAR_CHOICES.append((r,r))
    END_YEAR_CHOICES.append((r+1,r+1))

def profile_picture(instance, filename):
    ext = os.path.splitext(filename)[1]
    ext = ext.lower()
    return '/'.join(['user', str(instance.user.id), str(instance.user.id) + ext])

class Degree(models.Model): # eg. BTech-Mechanical, MCA, BSc 
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Domain(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class JobType(models.Model):
    type = models.CharField(max_length=200)
    def __str__(self):
        return self.type

class Skill(models.Model):
    name = models.CharField(max_length=240)

    def __str__(self):
        return self.name

class Discipline(models.Model):
    name = models.CharField(max_length=240)

    def __str__(self):
        return self.name

class Education(models.Model):
    degree = models.ForeignKey(Degree,null=True,on_delete=models.CASCADE)
    acad_discipline = models.ForeignKey(Discipline,on_delete=models.CASCADE,verbose_name='Academic Discipline',null=True)
    # institute = models.CharField(max_length=400) #Institute name
    #institute = models.ForeignKey(AcademicCenter,max_length=400,on_delete=models.CASCADE,null=True,blank=True) #Institute name
    institute = models.IntegerField(null=True,blank=True)
    start_year = models.IntegerField(choices=START_YEAR_CHOICES, null=True)
    end_year = models.IntegerField(choices=END_YEAR_CHOICES, null=True)
    gpa = models.CharField(max_length=10,null=True)
    order = models.IntegerField(default=1) #1 : Current Education 2: Pas education
    # def __str__(self):
    #     return self.degree.name+'_'+str(self.institute)


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Project(models.Model):
    url = models.URLField(null=True,blank=True)
    desc = models.TextField(null=True,blank=True)

    def __str__(self):
        return str(self.url)

class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, null=True,blank=True) #spk
    address = models.CharField(max_length=400, null=True,blank=True,verbose_name='Home Address')  #spk
    #spk_institute = models.CharField(max_length=200) #spk
    education = models.ManyToManyField(Education, null=True)
    spk_institute = models.IntegerField(null=True)  #spk
    #course = models.ForeignKey(Course,null=True,blank=True,on_delete=models.CASCADE)
    skills = models.ManyToManyField(Skill, null=True,blank=True)
    about = models.TextField(null=True,blank=True,verbose_name='About Yourself') #Short description/introduction about student profile
    projects = models.ManyToManyField(Project, null=True,blank=True)
    #photo = models.ImageField(null=True,blank=True) #profile photo
    picture = models.FileField(upload_to=profile_picture, null=True, blank=True)    #spk
    github = models.URLField(null=True,blank=True)
    linkedin = models.URLField(null=True,blank=True)
    cover_letter = models.FileField(null=True,blank=True,upload_to='')
    resume = models.FileField(null=True,blank=True,upload_to='')
    # cover_letter = models.FileField(null=True,blank=True,upload_to=user_directory_path)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    #spoken_score = 
    status = models.BooleanField(default=True) #False to restrict student from accessing
    spk_usr_id = models.IntegerField(null=True)  # spoken student id
    spk_student_id = models.IntegerField(null=True)  # spoken student id
    gender = models.CharField(max_length=10, null=True) # autopopulated spk cms profile
    location = models.CharField(max_length=400,null=True,blank=True)  #spk
    state = models.CharField(max_length=100, null=True)  #spk
    district = models.CharField(max_length=200, null=True)  #spk
    city = models.CharField(max_length=200, null=True)  #spk
    alternate_email = models.EmailField(null=True,blank=True)
    certifications = models.TextField(null=True,blank=True)
    def __str__(self):
        return self.user.username+'-'+self.user.email+'-'+str(self.id)

    
    def get_absolute_url(self):
        url = str(self.id)+'/'+'profile'
        return reverse('student_profile',kwargs={'pk':self.id}) 

class Company(models.Model):
    NUM_OF_EMPS = [
        ('< 50','< 50'),
        ('50 - 100','50 - 100'),
        ('100 - 500','100 - 500'),
        ('> 500','> 500'),]
    name = models.CharField(max_length=200)
    emp_name = models.CharField(max_length=200,verbose_name="Company HR Representative Name") #Name of the company representative
    emp_contact = models.CharField(max_length=100,verbose_name="Phone Number") #Contact of the company representative
    state_c = models.IntegerField(null=True)
    city_c = models.IntegerField(null=True)    
    # state_c = models.ForeignKey(SpokenState,on_delete=models.CASCADE,null=True,blank=True) #Company Address for correspondence
    # city_c = models.ForeignKey(SpokenCity,on_delete=models.CASCADE,null=True,blank=True) #Company Address for correspondence
    address = models.CharField(max_length=250) #Company Address for correspondence
    email = models.EmailField(null=True,blank=True) #Email for correspondence
    logo = models.ImageField(upload_to='logo/',null=True,blank=True)
    description = models.TextField(null=True,blank=True,verbose_name="Description about the company")
    domain = models.ForeignKey(Domain,on_delete=models.CASCADE) #Domain od work Eg. Consultancy, Development, Software etc
    company_size = models.CharField(max_length=25,choices=NUM_OF_EMPS) #Number of employees in company
    website = models.URLField(null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True )
    status = models.BooleanField(default=True)
    added_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    slug = models.SlugField(max_length = 250, null = True, blank = True)
    rating = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('company-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            obj = Company.objects.get(name=self.name,date_created=self.date_created)
            obj.slug = slugify(obj.id) 
            obj.save()

class Foss(models.Model):
    foss = models.IntegerField(null=True,blank=True)  #spk foss id
    mdl_course = models.IntegerField(null=True,blank=True)  #mdlcourse id
    mdl_quiz = models.IntegerField(null=True,blank=True)  #mdl quiz id

    def __str__(self):
        return self.foss


class Job(models.Model):
    title = models.CharField(max_length=250,verbose_name="Title of the job page") #filter
    designation = models.CharField(max_length=250,verbose_name='Designation (Job Position)') 
    state_job = models.IntegerField(null=True)  #spk #filter
    #state_job = models.ForeignKey(SpokenState,on_delete=models.CASCADE,null=True,blank=True) #Company Address for correspondence
    city_job = models.IntegerField(null=True)  #spk #filter
    #city_job = models.ForeignKey(SpokenCity,on_delete=models.CASCADE,null=True,blank=True) #Company Address for correspondence
    skills = models.CharField(max_length=400,null=True,blank=True) 
    description = models.TextField(null=True,blank=True,verbose_name="Job Description") 
    domain = models.ForeignKey(Domain,on_delete=models.CASCADE) #Domain od work Eg. Consultancy, Development, Software etc
    salary_range_min = models.IntegerField(null=True,blank=True)
    salary_range_max = models.IntegerField(null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True,null = True, blank = True)
    date_updated = models.DateTimeField(auto_now=True,null = True, blank = True )
    job_type = models.ForeignKey(JobType,on_delete=models.CASCADE)
    # 0: Job is inactive(added but not visible to students)
    # 1: Job is active(added & available to students for apply)
    # 2: Job Application Date is over
    # 3: Job Application is in process with HR & Company
    # 4: Student selected & job closed.
    status = models.IntegerField(default=1,blank=True)
    requirements = models.TextField(null=True,blank=True,verbose_name="Qualifications/Skills Required") #Educational qualifications, other criteria
    shift_time = models.CharField(max_length=200)
    key_job_responsibilities = models.TextField(null=True,blank=True,verbose_name="Key Job Responsibilities")
    gender = models.CharField(max_length=10,choices=GENDER)
    company=models.ForeignKey(Company,null=True,on_delete=models.CASCADE)
    slug = models.SlugField(max_length = 250, null = True, blank = True)
    last_app_date = models.DateTimeField(null=True,blank=True,verbose_name="Last Application Date")
    rating = models.IntegerField(null=True,blank=True)
    foss = models.CharField(max_length=200)
    # institute_type = models.CharField(max_length=200,null=True,blank=True)
    institute_type = models.CharField(max_length=200,blank=True)
    # state = models.CharField(max_length=200,null=True,blank=True)
    state = models.CharField(max_length=200,blank=True)
    # city = models.CharField(max_length=200,null=True,blank=True)
    city = models.CharField(max_length=200,blank=True)
    grade = models.IntegerField()
    activation_status = models.IntegerField(max_length=10,choices=ACTIVATION_STATUS)
    from_date = models.DateField(null=True,blank=True)
    to_date = models.DateField(null=True,blank=True)
    num_vacancies = models.IntegerField(default=1,blank=True)
    degree = models.ManyToManyField(Degree,blank=True)
    discipline = models.ManyToManyField(Discipline,blank=True)
    job_foss = models.ManyToManyField(Foss,null=True,blank=True)
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('job-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            obj = Job.objects.get(title=self.title,date_created=self.date_created)
            obj.slug = slugify(obj.id) 
            obj.save()

    class Meta:
        ordering = [('-date_updated')]


class JobShortlist(models.Model):
    # user=models.ForeignKey(User,on_delete=models.CASCADE)
    spk_user=models.IntegerField(null=True)  #spk
    student=models.ForeignKey(Student,on_delete=models.CASCADE)  #rec
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    date_created = models.DateField(auto_now_add=True, null=True,blank=True)
    date_updated = models.DateTimeField(auto_now=True)
    #0 : awaiting for further shortlist
    #1 : shortlisted for 2nd round
    status = models.IntegerField(null=True,blank=True)

    def __str__(self):
        return str(self.spk_user)+'-'+self.job.title


