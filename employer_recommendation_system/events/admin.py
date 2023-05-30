from django.contrib import admin
from .models import *

# Register your models here.
class EventAdmin(admin.ModelAdmin):
    list_display = ('name','status','start_date')
    list_editable = ['status']
    list_filter = ('type',)
class BrochureAdmin(admin.ModelAdmin):
    pass
class TestimonialAdmin(admin.ModelAdmin):
    pass
class GalleryImageAdmin(admin.ModelAdmin):
    pass
class JobFairAdmin(admin.ModelAdmin):
    list_display = ('event','venue')
    exclude = ('students',)
    list_filter = ('event__status',)
    

admin.site.register(Event,EventAdmin)
admin.site.register(Brochure,BrochureAdmin)
admin.site.register(Testimonial,TestimonialAdmin)
admin.site.register(GalleryImage,GalleryImageAdmin)
admin.site.register(JobFair,JobFairAdmin)