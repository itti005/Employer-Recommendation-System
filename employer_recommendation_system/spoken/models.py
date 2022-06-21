
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from datetime import datetime, date, timedelta


class SpokenUser(models.Model):
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

    def __str__(self):
        return self.first_name + ' ' + self.last_name

class SpokenGroup(models.Model):
    name = models.CharField(max_length=200)
    class Meta:
        managed = False
        db_table = 'auth_group'

class SpokenUserGroup(models.Model):
    user = models.ForeignKey(SpokenUser, on_delete=models.PROTECT )
    group = models.ForeignKey(SpokenGroup, on_delete=models.PROTECT )
    class Meta:
        managed = False
        db_table = 'auth_user_groups'

class SpokenStudent(models.Model):
    gender = models.CharField(max_length=15)
    verified = models.PositiveSmallIntegerField()
    error = models.IntegerField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    user = models.OneToOneField(SpokenUser, models.DO_NOTHING, db_column='user_id')

    class Meta:
        db_table = 'events_student'
        #app_label = 'spoken'
        managed = False


class SpokenState(models.Model):
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
        # unique_together = (('code', 'name'),)
    def __str__(self):
        return self.name
class District(models.Model):
    state = models.ForeignKey(SpokenState, models.DO_NOTHING)
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


class SpokenCity(models.Model):
    state = models.ForeignKey(SpokenState, models.DO_NOTHING)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'events_city'
        unique_together = (('name', 'state'),)

    def __str__(self):
        return self.name


class InstituteType(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'events_institutetype'

class AcademicCenter(models.Model):
    user = models.ForeignKey(SpokenUser, on_delete=models.PROTECT , db_column='user_id')
    state = models.ForeignKey(SpokenState, on_delete=models.PROTECT )
    institution_type = models.ForeignKey(InstituteType, on_delete=models.PROTECT )
    #institute_category = models.ForeignKey(InstituteCategory, on_delete=models.PROTECT )
    #university = models.ForeignKey(University, on_delete=models.PROTECT )
    academic_code = models.CharField(max_length=100, unique = True)
    institution_name = models.CharField(max_length=200)
    district = models.ForeignKey(District, on_delete=models.PROTECT )
    location = models.ForeignKey(Location, null=True, on_delete=models.PROTECT )
    city = models.ForeignKey(SpokenCity, on_delete=models.PROTECT )
    address = models.TextField()
    pincode = models.PositiveIntegerField()
    resource_center = models.BooleanField()
    rating = models.PositiveSmallIntegerField()
    contact_person = models.TextField()
    remarks = models.TextField()
    status = models.PositiveSmallIntegerField()

    class Meta:
        managed = False
        db_table = 'events_academiccenter'

    def __str__(self):
        return self.institution_name

class Organiser(models.Model):
    user = models.OneToOneField(SpokenUser, related_name = 'organiser', on_delete=models.PROTECT )
    appoved_by = models.ForeignKey(SpokenUser,related_name = 'organiser_approved_by',blank=True,
    null=True, on_delete=models.PROTECT )
    academic = models.ForeignKey(AcademicCenter, blank=True, null=True, on_delete=models.PROTECT )
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.user.username

    class Meta:
        managed = False
        db_table = 'events_organiser'


class TestCategory(models.Model):
    name = models.CharField(max_length=200)
    status = models.BooleanField(default = 0)
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'events_testcategory'

class Invigilator(models.Model):
    user = models.OneToOneField(SpokenUser, on_delete=models.PROTECT )
    appoved_by = models.ForeignKey(SpokenUser,related_name = 'invigilator_approved_by',blank=True,null=True,  on_delete=models.PROTECT )
    # appoved_by = models.ForeignKey(SpokenUser, on_delete=models.PROTECT)
    academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.user.username

    class Meta:
        managed = False
        db_table = 'events_invigilator'

class Department(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        managed = False
        db_table = 'events_department'

class TrainingRequest(models.Model):
    training_planner = models.BigIntegerField()
    # training_planner = models.ForeignKey(TrainingPlanner, on_delete=models.PROTECT )
    department = models.ForeignKey(Department, on_delete=models.PROTECT )
    sem_start_date = models.DateField()
    training_start_date = models.DateField(default=datetime.now)
    training_end_date = models.DateField(default=datetime.now)
    # course = models.ForeignKey(CourseMap, on_delete=models.PROTECT )
    course = models.BigIntegerField()
    # batch = models.ForeignKey(StudentBatch, null = True, on_delete=models.PROTECT )
    batch = models.BigIntegerField()
    participants = models.PositiveIntegerField(default=0)
    course_type = models.PositiveIntegerField(default=None)
  #status = models.BooleanField(default=False)
    status = models.PositiveSmallIntegerField(default=0)
    cert_status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        managed = False
        db_table = 'events_trainingrequest'

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
    organiser = models.ForeignKey(Organiser, models.DO_NOTHING)
    # organiser = models.BigIntegerField()
    test_category = models.ForeignKey(TestCategory, models.DO_NOTHING)
    # test_category = models.BigIntegerField()
    appoved_by = models.ForeignKey(SpokenUser, models.DO_NOTHING, blank=True, null=True)
    # appoved_by = models.BigIntegerField()
    invigilator = models.ForeignKey(Invigilator, models.DO_NOTHING, blank=True, null=True)
    # invigilator = models.BigIntegerField()
    #academic = models.ForeignKey('Academiccenter', models.DO_NOTHING)
    academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT ) 
    training = models.ForeignKey(TrainingRequest, models.DO_NOTHING, blank=True, null=True)
    # training = models.BigIntegerField()
    #foss = models.ForeignKey('CreationFosscategory', models.DO_NOTHING)
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
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


class FossMdlCourses(models.Model):
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT ) 
    mdlcourse_id = models.PositiveIntegerField()
    mdlquiz_id = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'events_fossmdlcourses'
        #app_label = 'spoken'


class TestAttendance(models.Model):
    test = models.ForeignKey(Test, models.DO_NOTHING)
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
    student = models.ForeignKey(SpokenStudent, models.DO_NOTHING, blank=True, null=True, db_column='student_id')
    mdlgrade = models.DecimalField(max_digits=12, decimal_places=5, default=0.00)

    class Meta:
        managed = False
        db_table = 'events_testattendance'
        unique_together = (('test', 'mdluser_id'),)


class Profile(models.Model):
    user = models.ForeignKey(SpokenUser, models.DO_NOTHING, db_column='user_id')
    confirmation_code = models.CharField(max_length=255)
    street = models.CharField(max_length=255, blank=True, null=True)
    location = models.ForeignKey(Location, models.DO_NOTHING, blank=True, null=True)
    #location_id = models.BigIntegerField()
    district = models.ForeignKey(District, models.DO_NOTHING, blank=True, null=True)
    #district_id = models.BigIntegerField()
    city = models.ForeignKey(SpokenCity, models.DO_NOTHING, blank=True, null=True)
    #city_id = models.BigIntegerField()
    state = models.ForeignKey(SpokenState, models.DO_NOTHING, blank=True, null=True)
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

class Language(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # user = models.ForeignKey(SpokenUser, on_delete=models.PROTECT )
    code = models.CharField(max_length=10, default='en')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'creation_language'


class Participant(models.Model):
    GENDER_CHOICES = (
		('', '--- Gender ---'),
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', "Don't wish to disclose")
    )
    REGISTRATION_TYPE_CHOICES =(
    ('', '-----'),  (1, 'Subscribed College'),(2, 'Manual Registration')
    )
    name = models.CharField(max_length=255,null=True)
    email = models.EmailField(max_length=255,null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6,null=True)
    amount = models.DecimalField(max_digits=10,decimal_places=2,null=True)	
    # event = models.ForeignKey(TrainingEvents, on_delete=models.PROTECT)
    user = models.ForeignKey(SpokenUser, on_delete=models.PROTECT)
    state = models.ForeignKey(SpokenState, on_delete=models.PROTECT )
    college = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True)
    registartion_type = models.PositiveSmallIntegerField(choices= REGISTRATION_TYPE_CHOICES, default=1)
    created = models.DateTimeField(auto_now_add = True)
    foss_language = models.ForeignKey(Language, on_delete=models.PROTECT, null=True )
    # payment_status = models.ForeignKey(Payee, on_delete=models.PROTECT, null=True)
    reg_approval_status = models.PositiveSmallIntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'training_participant'
    

class EventTestStatus(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.PROTECT)
    # event = models.ForeignKey(TrainingEvents, on_delete=models.PROTECT)
    mdlemail = models.EmailField(max_length=255,null=True)
    fossid = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    mdlcourse_id = models.PositiveIntegerField(default=0)
    mdlquiz_id = models.PositiveIntegerField(default=0)
    mdlattempt_id = models.PositiveIntegerField(default=0)
    part_status = models.PositiveSmallIntegerField(default=0)
    mdlgrade= models.DecimalField(max_digits = 10, decimal_places = 5, default=0.00)
    cert_code= models.CharField(max_length = 100, null=True)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    class Meta:
        managed = False
        db_table = 'training_eventteststatus'

