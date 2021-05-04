from django.db import models
from django.conf import settings
import datetime
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.urls import reverse
import os
# Create your models here.
from events.models import AcademicCenter
GENDER = [('f','f'),('m','m'),('a','No criteria'),]
START_YEAR_CHOICES = []
END_YEAR_CHOICES = []
for r in range(2000, (datetime.datetime.now().year+1)):
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

class State(models.Model):
  name = models.CharField(max_length=50)
  latitude = models.DecimalField(
    null=True,
    max_digits=10,
    decimal_places=4,
    blank=True
  )
  longtitude = models.DecimalField(
    null=True,
    max_digits=10,
    decimal_places=4,
    blank=True
  )

  def __str__(self):
    return self.name

  
class City(models.Model):
  state = models.ForeignKey(State, on_delete=models.PROTECT )
  name = models.CharField(max_length=200)
  created = models.DateTimeField(auto_now_add = True, null=True)
  updated = models.DateTimeField(auto_now = True, null=True)

  def __str__(self):
    return self.name

  class Meta(object):
    unique_together = (("name","state"),)

class Skill(models.Model):
    name = models.CharField(max_length=240)

    def __str__(self):
        return self.name

class Education(models.Model):
    degree = models.ForeignKey(Degree,null=True,blank=True,on_delete=models.CASCADE)
    name = models.CharField(max_length=400)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    gpa = models.CharField(max_length=10,null=True,blank=True)
    def __str__(self):
        return self.degree.name+'_'+self.name

class Student(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone = models.CharField(max_length=10) #spk
    address = models.CharField(max_length=400)  #spk
    #spk_institute = models.CharField(max_length=200) #spk
    education = models.ManyToManyField(Education)
    spk_institute = models.IntegerField()  #spk
    #course = models.ForeignKey(Course,null=True,blank=True,on_delete=models.CASCADE)
    skills = models.ManyToManyField(Skill)
    about = models.TextField(null=True,blank=True) #Short description/introduction about student profile
    experience = models.TextField(null=True,blank=True) #Project/work or internship experience 
    #photo = models.ImageField(null=True,blank=True) #profile photo
    picture = models.FileField(upload_to=profile_picture, null=True, blank=True)    #spk
    github = models.URLField(null=True,blank=True)
    linkedin = models.URLField(null=True,blank=True)
    cover_letter = models.FileField(null=True,blank=True)
    date_created = models.DateTimeField(null=True,blank=True)
    date_updated = models.DateTimeField(null=True,blank=True)
    #spoken_score = 
    status = models.BooleanField(default=True) #False to restrict student from accessing
    spk_usr_id = models.IntegerField()  # spoken student id
    gender = models.CharField(max_length=10,choices=GENDER) # autopopulated spk cms profile
    def __str__(self):
        return self.user.username+'-'+self.user.email+'-'+str(self.id)

    
    def get_absolute_url(self):
        print("****************************** ABS URL*************")
        url = str(self.id)+'/'+'profile'
        return reverse('student_profile',kwargs={'pk':self.id}) 

class Company(models.Model):
    NUM_OF_EMPS = [
        ('< 50','< 50'),
        ('50 - 100','50 - 100'),
        ('100 - 500','100 - 500'),
        ('> 500','> 500'),

            ]
    name = models.CharField(max_length=200)
    emp_name = models.CharField(max_length=200) #Name of the company representative
    emp_contact = models.CharField(max_length=200) #Contact of the company representative
    state = models.ForeignKey(State,on_delete=models.CASCADE) #Company Address for correspondence
    city = models.ForeignKey(City,on_delete=models.CASCADE) #Company Address for correspondence
    address = models.CharField(max_length=250) #Company Address for correspondence
    phone = models.CharField(max_length=15) #Contact of the company representative
    email = models.EmailField(null=True,blank=True) #Email for correspondence
    logo = models.ImageField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    domain = models.CharField(max_length=400) #Domain of work . Eg : consultancy, software development, etc
    company_size = models.CharField(max_length=25,choices=NUM_OF_EMPS) #Number of employees in company
    website = models.URLField(null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True )
    status = models.BooleanField(default=True)
    added_by = models.ForeignKey(User,on_delete=models.CASCADE)
    slug = models.SlugField(max_length = 250, null = True, blank = True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('company-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        #s = '{} {}'.format(self.company_name)
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Job(models.Model):
    title = models.CharField(max_length=250)
    designation = models.CharField(max_length=250)
    state = models.ForeignKey(State,on_delete=models.CASCADE) #Company Address for correspondence
    city = models.ForeignKey(City,on_delete=models.CASCADE) #Company Address for correspondence
    skills = models.CharField(max_length=400)
    description = models.TextField(null=True,blank=True)
    domain = models.ForeignKey(Domain,on_delete=models.CASCADE) #Domain od work Eg. Consultancy, Development, Software etc
    salary_range_min = models.IntegerField(null=True,blank=True)
    salary_range_max = models.IntegerField(null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True )
    job_type = models.ForeignKey(JobType,on_delete=models.CASCADE)
    benefits = models.TextField(null=True,blank=True) # Additional benefits provided by the company to employee
    status = models.BooleanField(default=True )#To make if the job is active
    requirements = models.TextField(null=True,blank=True) #Educational qualifications, other criteria
    shift_time = models.CharField(max_length=200)
    key_job_responsibilities = models.TextField(null=True,blank=True)
    gender = models.CharField(max_length=10,choices=GENDER)
    company=models.ForeignKey(Company,null=True,on_delete=models.CASCADE)
    slug = models.SlugField(max_length = 250, null = True, blank = True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('job-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.company.name+'_'+self.title)
        super().save(*args, **kwargs)


class AppliedJob(models.Model):
    date_created = models.DateField(auto_now_add=True, null=True,blank=True)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    student=models.ForeignKey(Student,on_delete=models.CASCADE)

    def __str__(self):
        return self.student.user.username+'-'+self.job.title


