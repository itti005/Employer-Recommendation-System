from django.contrib import admin
from .models import *
# Register your models here.
class DegreeAdmin(admin.ModelAdmin):
    pass
class CourseAdmin(admin.ModelAdmin):
    pass
class DomainAdmin(admin.ModelAdmin):
    pass
class JobTypeAdmin(admin.ModelAdmin):
    pass

class StudentAdmin(admin.ModelAdmin):
    pass
class CompanyAdmin(admin.ModelAdmin):
    exclude = ('slug',)
class JobAdmin(admin.ModelAdmin):
    exclude = ('slug',)
class JobShortlistAdmin(admin.ModelAdmin):
    pass
class EducationAdmin(admin.ModelAdmin):
    pass

class SkillAdmin(admin.ModelAdmin):
    pass
class DisciplineAdmin(admin.ModelAdmin):
    pass

admin.site.register(Degree,DegreeAdmin)
admin.site.register(Course,CourseAdmin)
admin.site.register(Domain,DomainAdmin)
admin.site.register(JobType,JobTypeAdmin)
admin.site.register(Student,StudentAdmin)
admin.site.register(Company,CompanyAdmin)
admin.site.register(Job,JobAdmin)
admin.site.register(JobShortlist,JobShortlistAdmin)
admin.site.register(Education,EducationAdmin)
admin.site.register(Skill,SkillAdmin)
admin.site.register(Discipline,DisciplineAdmin)

