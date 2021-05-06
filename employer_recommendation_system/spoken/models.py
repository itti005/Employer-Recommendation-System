
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class User(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=75)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'
        #app_label = 'spoken'


class Student(models.Model):
    gender = models.CharField(max_length=15)
    verified = models.PositiveSmallIntegerField()
    error = models.IntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    user = models.OneToOneField(User, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'events_student'
        #app_label = 'spoken'


class TestAttendance(models.Model):
    test = models.BigIntegerField()
    mdluser_firstname = models.CharField(max_length=100)
    mdluser_lastname = models.CharField(max_length=100)
    mdluser_id = models.PositiveIntegerField()
    mdlcourse_id = models.PositiveIntegerField()
    mdlquiz_id = models.PositiveIntegerField()
    mdlattempt_id = models.PositiveIntegerField()
    password = models.CharField(max_length=100, blank=True, null=True)
    count = models.PositiveSmallIntegerField()
    status = models.PositiveSmallIntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    student_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'events_testattendance'
        unique_together = (('test', 'mdluser_id'),)
        #app_label = 'spoken'
class FossMdlCourses(models.Model):
    foss_id = models.BigIntegerField()
    mdlcourse_id = models.PositiveIntegerField()
    mdlquiz_id = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'events_fossmdlcourses'
        #app_label = 'spoken'

class FossCategory(models.Model):
    foss = models.CharField(unique=True, max_length=255)
    description = models.TextField()
    status = models.IntegerField()
    user_id = models.BigIntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    is_learners_allowed = models.IntegerField()
    show_on_homepage = models.PositiveSmallIntegerField()
    is_translation_allowed = models.IntegerField()
    available_for_nasscom = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'creation_fosscategory'
        #app = 'spoken'

    def __str__(self):
        return self.foss

class Test(models.Model):
    #organiser = models.ForeignKey('Organiser', models.DO_NOTHING)
    organiser = models.BigIntegerField()
    #test_category = models.ForeignKey('Testcategory', models.DO_NOTHING)
    test_category = models.BigIntegerField()
    #appoved_by = models.ForeignKey('AuthUser', models.DO_NOTHING, blank=True, null=True)
    appoved_by = models.BigIntegerField()
    #invigilator = models.ForeignKey('Invigilator', models.DO_NOTHING, blank=True, null=True)
    invigilator = models.BigIntegerField()
    #academic = models.ForeignKey('Academiccenter', models.DO_NOTHING)
    academic = models.BigIntegerField()
    #training = models.ForeignKey('Trainingrequest', models.DO_NOTHING, blank=True, null=True)
    training = models.BigIntegerField()
    #foss = models.ForeignKey('CreationFosscategory', models.DO_NOTHING)
    foss = models.BigIntegerField()
    test_code = models.CharField(max_length=100)
    tdate = models.DateField()
    ttime = models.TimeField()
    status = models.PositiveSmallIntegerField()
    participant_count = models.PositiveIntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'events_test'
        unique_together = (('organiser', 'academic', 'foss', 'tdate', 'ttime'),)


class TestAttendance(models.Model):
    test = models.ForeignKey('Test', models.DO_NOTHING)
   # test_id = models.BigIntegerField()
    mdluser_firstname = models.CharField(max_length=100)
    mdluser_lastname = models.CharField(max_length=100)
    mdluser_id = models.PositiveIntegerField()
    mdlcourse_id = models.PositiveIntegerField()
    mdlquiz_id = models.PositiveIntegerField()
    mdlattempt_id = models.PositiveIntegerField()
    password = models.CharField(max_length=100, blank=True, null=True)
    count = models.PositiveSmallIntegerField()
    status = models.PositiveSmallIntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    #student = models.ForeignKey('Student', models.DO_NOTHING, blank=True, null=True)
    student_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'events_testattendance'
        unique_together = (('test', 'mdluser_id'),)

class State(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    longtitude = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    img_map_area = models.TextField()
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    has_map = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'events_state'
        unique_together = (('code', 'name'),)
    def __str__(self):
        return self.name
class District(models.Model):
    state = models.ForeignKey('State', models.DO_NOTHING)
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'events_district'
        unique_together = (('state', 'code', 'name'),)


class Location(models.Model):
    district = models.ForeignKey(District, models.DO_NOTHING)
    name = models.CharField(max_length=200)
    pincode = models.PositiveIntegerField()
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'events_location'
        unique_together = (('name', 'district', 'pincode'),)


class City(models.Model):
    state = models.ForeignKey('State', models.DO_NOTHING)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'events_city'
        unique_together = (('name', 'state'),)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    confirmation_code = models.CharField(max_length=255)
    street = models.CharField(max_length=255, blank=True, null=True)
    location = models.ForeignKey('Location', models.DO_NOTHING, blank=True, null=True)
    #location_id = models.BigIntegerField()
    district = models.ForeignKey('District', models.DO_NOTHING, blank=True, null=True)
    #district_id = models.BigIntegerField()
    city = models.ForeignKey('City', models.DO_NOTHING, blank=True, null=True)
    #city_id = models.BigIntegerField()
    state = models.ForeignKey('State', models.DO_NOTHING, blank=True, null=True)
    #state_id = models.BigIntegerField()
    country = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.PositiveIntegerField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    picture = models.CharField(max_length=100, blank=True, null=True)
    thumb = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'cms_profile'

class InstituteType(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'events_institutetype'
