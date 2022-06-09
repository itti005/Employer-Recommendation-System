from datetime import date
from django.db import models
from django.forms import DateField
from django.urls import reverse
from django.conf import settings
from django.template.defaultfilters import slugify
from ckeditor.fields import RichTextField


from emp.models import Company, Job
# Create your models here.

EVENT_TYPE = [
    ('JOB','Job'),
    ('JOBFAIR','JobFair'),
    ('INTERN','Internship'),
    ('HACKATHON','Hackathon'),
    ('MAPATHON','Mapathon'),
    ('PILOT_WORKSHOP','Pilot Workshop')
]

JOBFAIR_VENUE_TYPE = [
    ('VIRTUAL','virtual'),
    ('PHYSICAL','physical')
]
def brochure_directory_path(instance, filename):
    return 'brochures'

class Event(models.Model):
    name = models.CharField(max_length=250)
    start_date = models.DateField()
    end_date = models.DateField()
    logo = models.FileField(upload_to='brochures',null=True,blank=True)
    type = models.CharField(max_length=200,choices=EVENT_TYPE,default="JOB")
    status = models.BooleanField(default=True) # if inactive , it will not be made public
    show_on_homepage = models.BooleanField(default=True)
    description = RichTextField(null=True,blank=True,verbose_name="Event Description")

    def get_absolute_url(self):
        print(" ****************** GETIING ABSOLUTE URL ****************** ")
        return reverse('event-detail', kwargs={'pk': self.id})

    def __str__(self):
        return self.name
    


class Brochure(models.Model):
    event = models.ForeignKey(Event,on_delete=models.CASCADE)
    location = models.FileField(upload_to=brochure_directory_path)

class Testimonial(models.Model):
    name = models.CharField(max_length=250) #name of the person giving testimonial
    about = models.CharField(max_length=250,null=True,blank=True,verbose_name='About attestant') # about person givingn testimonial
    desc = models.TextField(null=True,blank=True,verbose_name='Text Testimonial (If any)') #text testimonial
    location = models.FileField(upload_to=settings.GALLERY_TESTIMONIAL, null=True, blank=True)    #spk
    display_on_homepage = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    # slug = models.SlugField(blank=True, unique=True)
    active = models.BooleanField(default=True)
    event = models.ForeignKey(Event,blank=True,null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # return reverse('gallery-image-detail', kwargs={'pk': self.pk})
        return reverse('add_testimonial')

class GalleryImage(models.Model):
    desc = models.TextField(null=True,blank=True,verbose_name='Description about image')
    location = models.FileField(upload_to=settings.GALLERY_IMAGES)    #spk
    display_on_homepage = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(blank=True, unique=True)
    active = models.BooleanField(default=True) #If true; image will be displayed publicly (either in homepage or image gallery page)
    event = models.ForeignKey(Event,blank=True,null=True,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)
    
    def get_absolute_url(self):
        # return reverse('gallery-image-detail', kwargs={'pk': self.pk})
        return reverse('add_image')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            obj = GalleryImage.objects.get(location=self.location,date_created=self.date_created,desc=self.desc)
            obj.slug = slugify(obj.id) 
            obj.save()

class JobFair(models.Model):
    students_enrolled = models.IntegerField(null=True,blank=True)
    students_placed = models.IntegerField(null=True,blank=True)
    companies = models.ManyToManyField(Company,null=True,blank=True)
    jobs = models.ManyToManyField(Job,null=True,blank=True)
    venue = models.CharField(max_length=255)
    type = models.CharField(choices=JOBFAIR_VENUE_TYPE,max_length=100)
    student_last_registration = models.DateField(null=True,blank=True)
    emp_last_registration = models.DateField(null=True,blank=True)
    event = models.ForeignKey(Event,on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.event.name