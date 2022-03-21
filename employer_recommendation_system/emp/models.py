from django.db import models
from django.conf import settings
import datetime
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.urls import reverse
from spoken.models import AcademicCenter
import os
from spoken.models import SpokenUser, SpokenState, SpokenCity
from django.core.validators import RegexValidator
from ckeditor.fields import RichTextField

ACTIVATION_STATUS = ((None, "--------"),(1, "Active"),(3, "Deactive"))
GENDER = [('a','No Criteria'),('f','F-Female Candidates'),('m','M-Male Candidates'),]
START_YEAR_CHOICES = []
END_YEAR_CHOICES = []
DEFAULT_NUM_EMP = '100_500'
NUM_OF_EMPS = [('less_than_50','< 50'),('50_100','50 - 100'),('100_500','100 - 500'),('greater_than_500','> 500'),]
STATUS = {'ACTIVE' :1,'INACTIVE' :0}

phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Invalid.")

for r in range(2000, (datetime.datetime.now().year+4)):
    START_YEAR_CHOICES.append((r,r))
    END_YEAR_CHOICES.append((r+1,r+1))

def profile_picture(instance, filename):
    ext = os.path.splitext(filename)[1]
    ext = ext.lower()
    return '/'.join(['user', str(instance.user.id), str(instance.user.id) + ext])

class CustomDegreeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('name')

class Degree(models.Model): # eg. BTech-Mechanical, MCA, BSc 
    objects = CustomDegreeManager()
    name = models.CharField(max_length=200,verbose_name='Degree',unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True )
    slug = models.SlugField(max_length = 250, null = True, blank = True)
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('degree-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            obj = Degree.objects.get(name=self.name,date_created=self.date_created)
            obj.slug = slugify(obj.id) 
            obj.save()

class Course(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Domain(models.Model):
    name = models.CharField(max_length=200,unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True )
    slug = models.SlugField(max_length = 250, null = True, blank = True)
    
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('domain-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            obj = Domain.objects.get(name=self.name,date_created=self.date_created)
            obj.slug = slugify(obj.id) 
            obj.save()
    
    # def get_queryset(self):
    #     print("******************************* get queryset")
    #     return super().get_queryset().order_by('name')

class CustomJobTypeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('jobtype')

class JobType(models.Model):
    objects = CustomJobTypeManager()
    jobtype = models.CharField(max_length=200,unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True )
    slug = models.SlugField(max_length = 250, null = True, blank = True)
    def __str__(self):
        return self.jobtype

    def get_absolute_url(self):
        return reverse('job-type-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            obj = JobType.objects.get(jobtype=self.jobtype,date_created=self.date_created)
            obj.slug = slugify(obj.id) 
            obj.save()

    # def get_absolute_url(self):
    #     return reverse('degree-detail', kwargs={'slug': self.slug})

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     if not self.slug:
    #         obj = Degree.objects.get(name=self.name,date_created=self.date_created)
    #         obj.slug = slugify(obj.id) 
    #         obj.save()

class Skill(models.Model):
    name = models.CharField(max_length=240)

    def __str__(self):
        return self.name

class CustomDisciplineManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('name')

class Discipline(models.Model):
    objects = CustomDisciplineManager()
    name = models.CharField(max_length=200,unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True )
    slug = models.SlugField(max_length = 250, null = True, blank = True)
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # return reverse('update-discipline', kwargs={'slug': self.slug})
        return reverse('update-discipline', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            obj = Discipline.objects.get(name=self.name,date_created=self.date_created)
            obj.slug = slugify(obj.id) 
            obj.save()

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
    phone = models.CharField(validators=[phone_regex], max_length=17)
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
    name = models.CharField(max_length=200)
    emp_name = models.CharField(max_length=200,verbose_name="Company HR Representative Name") #Name of the company representative
    emp_contact = models.CharField(validators=[phone_regex], max_length=17,verbose_name="Phone Number")
    state_c = models.IntegerField(null=True,verbose_name='State (Company Headquarters)',blank=True)
    city_c = models.IntegerField(null=True,verbose_name='City (Company Headquarters)',blank=True)    
    # state_c = models.ForeignKey(SpokenState,on_delete=models.CASCADE,null=True,blank=True) #Company Address for correspondence
    # city_c = models.ForeignKey(SpokenCity,on_delete=models.CASCADE,null=True,blank=True) #Company Address for correspondence
    address = models.CharField(max_length=250) #Company Address for correspondence
    email = models.EmailField(null=True,blank=True) #Email for correspondence
    logo = models.ImageField(upload_to='logo/',null=True,blank=True)
    description = models.TextField(null=True,blank=True,verbose_name="Description about the company")
    # domain = models.ForeignKey(Domain,on_delete=models.CASCADE) 
    domain = models.ManyToManyField(Domain,blank=True,related_name='domains') #Domain of work Eg. Consultancy, Development, Software etc
    company_size = models.CharField(max_length=25,choices=NUM_OF_EMPS,default=DEFAULT_NUM_EMP) #Number of employees in company
    website = models.URLField(null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True )
    status = models.BooleanField(default=True)
    added_by = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    slug = models.SlugField(max_length = 250, null = True, blank = True)
    rating = models.IntegerField(null=True,blank=True,verbose_name="Visibility")

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
    state_job = models.IntegerField(null=False,blank=False)  #spk #filter
    #state_job = models.ForeignKey(SpokenState,on_delete=models.CASCADE,null=True,blank=True) #Company Address for correspondence
    city_job = models.IntegerField(null=False,blank=False)  #spk #filter
    #city_job = models.ForeignKey(SpokenCity,on_delete=models.CASCADE,null=True,blank=True) #Company Address for correspondence
    skills = models.CharField(max_length=400,null=True,blank=True) 
    description = RichTextField(null=True,blank=True,verbose_name="Job Description")
    domain = models.ForeignKey(Domain,on_delete=models.CASCADE,verbose_name='Job Sector') #Domain od work Eg. Consultancy, Development, Software etc
    salary_range_min = models.IntegerField(null=True,blank=True,verbose_name='Annual Salary (Minimum)')
    salary_range_max = models.IntegerField(null=True,blank=True,verbose_name='Annual Salary (Maximum)')
    date_created = models.DateTimeField(auto_now_add=True,null = True, blank = True)
    date_updated = models.DateTimeField(auto_now=True,null = True, blank = True )
    job_type = models.ForeignKey(JobType,on_delete=models.CASCADE)
    # 0: Job is inactive(added but not visible to students)
    # 1: Job is active(added & available to students for apply)
    # 2: Job Application Date is over
    # 3: Job Application is in process with HR & Company
    # 4: Student selected & job closed.
    status = models.IntegerField(default=1,blank=True)
    requirements = RichTextField(null=True,blank=True,verbose_name="Qualifications/Skills Required") #Educational qualifications, other criteria
    shift_time = models.CharField(max_length=200,blank=True)
    key_job_responsibilities = RichTextField(null=True,blank=True,verbose_name="Key Job Responsibilities")
    gender = models.CharField(max_length=10,choices=GENDER,default='a')
    company=models.ForeignKey(Company,null=True,on_delete=models.CASCADE)
    slug = models.SlugField(max_length = 250, null = True, blank = True)
    last_app_date = models.DateTimeField(verbose_name="Last Application Date")
    rating = models.IntegerField(null=True,blank=True,verbose_name="Visibility")
    foss = models.CharField(max_length=200)
    # institute_type = models.CharField(max_length=200,null=True,blank=True)
    institute_type = models.CharField(max_length=200,blank=True)
    # state = models.CharField(max_length=200,null=True,blank=True)
    state = models.CharField(max_length=200,blank=True)
    # city = models.CharField(max_length=200,null=True,blank=True)
    city = models.CharField(max_length=200,blank=True)
    grade = models.IntegerField()
    activation_status = models.IntegerField(max_length=10,choices=ACTIVATION_STATUS,blank=True,null=True)
    from_date = models.DateField(null=True,blank=True,verbose_name='Test Date From')
    to_date = models.DateField(null=True,blank=True,verbose_name='Test Date Upto')
    num_vacancies = models.IntegerField(default=1,blank=True)
    degree = models.ManyToManyField(Degree,blank=True,related_name='degrees')
    discipline = models.ManyToManyField(Discipline,blank=True,related_name='disciplines')
    job_foss = models.ManyToManyField(Foss,null=True,blank=True,related_name='fosses')
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

class ShortlistEmailStatus(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    email_sequence = models.IntegerField(null=True,blank=True)
    total_mails = models.IntegerField()
    success_mails = models.IntegerField()
    job_id = models.IntegerField()
    log_file = models.CharField(max_length=250)

# landing page models
# class GalleryImage(models.Model):
#     desc = models.TextField(null=True,blank=True,verbose_name='Description about image')
#     location = models.FileField(upload_to=settings.GALLERY_IMAGES)    #spk
#     display_on_homepage = models.BooleanField(default=False)
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_updated = models.DateTimeField(auto_now=True)
#     slug = models.SlugField(blank=True, unique=True)
#     active = models.BooleanField(default=True)

#     def __str__(self):
#         return self.desc
    
#     def get_absolute_url(self):
#         # return reverse('gallery-image-detail', kwargs={'pk': self.pk})
#         return reverse('add_image')

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         if not self.slug:
#             obj = GalleryImage.objects.get(location=self.location,date_created=self.date_created,desc=self.desc)
#             obj.slug = slugify(obj.id) 
#             obj.save()


# class Testimonial(models.Model):
#     name = models.CharField(max_length=250) #name of the person giving testimonial
#     about = models.CharField(max_length=250,null=True,blank=True,verbose_name='About attestant') # about person givingn testimonial
#     desc = models.TextField(null=True,blank=True,verbose_name='Text Testimonial (If any)') #text testimonial
#     location = models.FileField(upload_to=settings.GALLERY_TESTIMONIAL, null=True, blank=True)    #spk
#     display_on_homepage = models.BooleanField(default=False)
#     date_created = models.DateTimeField(auto_now_add=True)
#     date_updated = models.DateTimeField(auto_now=True)
#     # slug = models.SlugField(blank=True, unique=True)
#     active = models.BooleanField(default=True)
    

#     def __str__(self):
#         return self.name

#     def get_absolute_url(self):
#         # return reverse('gallery-image-detail', kwargs={'pk': self.pk})
#         return reverse('add_testimonial')

class Feedback(models.Model):
    name = models.CharField(max_length=250,verbose_name='Your Name')
    email = models.EmailField(null=True,blank=True)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

