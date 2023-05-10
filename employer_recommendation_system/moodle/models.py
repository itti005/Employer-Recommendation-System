# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class MdlQuiz(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.BigIntegerField()
    name = models.CharField(max_length=255)
    intro = models.TextField()
    introformat = models.SmallIntegerField()
    timeopen = models.BigIntegerField()
    timeclose = models.BigIntegerField()
    preferredbehaviour = models.CharField(max_length=32)
    attempts = models.IntegerField()
    attemptonlast = models.SmallIntegerField()
    grademethod = models.SmallIntegerField()
    decimalpoints = models.SmallIntegerField()
    questiondecimalpoints = models.SmallIntegerField()
    reviewattempt = models.IntegerField()
    reviewcorrectness = models.IntegerField()
    reviewmarks = models.IntegerField()
    reviewspecificfeedback = models.IntegerField()
    reviewgeneralfeedback = models.IntegerField()
    reviewrightanswer = models.IntegerField()
    reviewoverallfeedback = models.IntegerField()
    questionsperpage = models.BigIntegerField()
    shufflequestions = models.SmallIntegerField()
    shuffleanswers = models.SmallIntegerField()
    questions = models.TextField()
    sumgrades = models.DecimalField(max_digits=10, decimal_places=5)
    grade = models.DecimalField(max_digits=10, decimal_places=5)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    timelimit = models.BigIntegerField()
    overduehandling = models.CharField(max_length=16)
    graceperiod = models.BigIntegerField()
    password = models.CharField(max_length=255)
    subnet = models.CharField(max_length=255)
    browsersecurity = models.CharField(max_length=32)
    delay1 = models.BigIntegerField()
    delay2 = models.BigIntegerField()
    showuserpicture = models.SmallIntegerField()
    showblocks = models.SmallIntegerField()
    navmethod = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'mdl_quiz'
        app_label = 'mdl'



class MdlUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    auth = models.CharField(max_length=60)
    confirmed = models.IntegerField()
    #policyagreed = models.IntegerField()
    #deleted = models.IntegerField()
    #suspended = models.IntegerField()
    mnethostid = models.BigIntegerField(unique=True)
    username = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=96)
    idnumber = models.CharField(max_length=765)
    firstname = models.CharField(max_length=300)
    lastname = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    #emailstop = models.IntegerField()
    icq = models.CharField(max_length=45)
    skype = models.CharField(max_length=150)
    yahoo = models.CharField(max_length=150)
    aim = models.CharField(max_length=150)
    msn = models.CharField(max_length=150)
    phone1 = models.CharField(max_length=60)
    phone2 = models.CharField(max_length=60)
    institution = models.CharField(max_length=120)
    department = models.CharField(max_length=90)
    address = models.CharField(max_length=210)
    city = models.CharField(max_length=360)
    country = models.CharField(max_length=6)
    #lang = models.CharField(max_length=90)
    theme = models.CharField(max_length=150)
    timezone = models.CharField(max_length=300)
    #firstaccess = models.BigIntegerField()
    #lastaccess = models.BigIntegerField()
    #lastlogin = models.BigIntegerField()
    #currentlogin = models.BigIntegerField()
    lastip = models.CharField(max_length=135)
    secret = models.CharField(max_length=45)
    #picture = models.BigIntegerField()
    url = models.CharField(max_length=765)
    description = models.TextField(blank=True)
    #descriptionformat = models.IntegerField()
    #mailformat = models.IntegerField()
    #maildigest = models.IntegerField()
    #maildisplay = models.IntegerField()
    #htmleditor = models.IntegerField()
    #autosubscribe = models.IntegerField()
    #trackforums = models.IntegerField()
    #timecreated = models.BigIntegerField()
    #timemodified = models.BigIntegerField()
    #trustbitmask = models.BigIntegerField()
    imagealt = models.CharField(max_length=765, blank=True)
    class Meta(object):
        db_table = 'mdl_user'

class MdlQuizGrades(models.Model):
    id = models.BigAutoField(primary_key=True)
    quiz = models.BigIntegerField()
    # userid = models.BigIntegerField()
    userid = models.ForeignKey(MdlUser,null=True,on_delete=models.CASCADE,db_column='userid')
    grade = models.DecimalField(max_digits=10, decimal_places=5)
    timemodified = models.BigIntegerField()

    class Meta:
        # managed = False
        db_table = 'mdl_quiz_grades'
        # app_label = 'mdl'
