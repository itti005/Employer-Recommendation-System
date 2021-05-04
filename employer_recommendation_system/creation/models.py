from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Language(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    code = models.CharField(max_length=10, default='en')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        ordering = ('name',)

    def __str__(self):
        return self.name

class FossSuperCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        verbose_name = 'FOSS Category'
        verbose_name_plural = 'FOSS Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name


class FossCategory(models.Model):
    foss = models.CharField(unique=True, max_length=255)
    description = models.TextField()
    status = models.BooleanField(max_length=2)
    is_learners_allowed = models.BooleanField(max_length=2,default=0 )
    is_translation_allowed = models.BooleanField(max_length=2, default=0)
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    category = models.ManyToManyField(FossSuperCategory)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    show_on_homepage = models.PositiveSmallIntegerField(default=0, help_text ='0:Display on home page, 1:Series, 2:Archived')
    available_for_nasscom = models.BooleanField(default=True, help_text ='If unchecked, this foss will not be available for nasscom' )

    class Meta(object):
        verbose_name = 'FOSS'
        verbose_name_plural = 'FOSSes'
        ordering = ('foss', )
        db_table = "%s %s" % ("creation","fosscategory")

    def __str__(self):

        return self.foss


class FossAvailableForWorkshop(models.Model):
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    status = models.BooleanField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        unique_together = (('foss', 'language'),)


class FossAvailableForTest(models.Model):
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    status = models.BooleanField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta(object):
    	unique_together = (('foss', 'language'),)


