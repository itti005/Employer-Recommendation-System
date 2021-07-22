"""
Django settings for employer_recommendation_system project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
from .config import *
from pathlib import Path
import os
from django.contrib.messages import constants as messages
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$aq4w)c0cqre6^(_yj81@$ns7)gzyk+0f1v(9%h%@wvm87jugj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'django_crontab',
    'emp',
    'accounts',
    'crispy_forms',
    'moodle',
    'spoken',
    'ckeditor',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'employer_recommendation_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'employer_recommendation_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST':'127.0.0.1',
        'PORT':'',
    },

    'spk': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': SPOKEN_DB,
        'USER': SPOKEN_DB_USER,
        'PASSWORD': SPOKEN_DB_PASS,
        'HOST': SPOKEN_DB_HOST,
        'PORT':'',
    },

    'moodle': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': MDB,
        'USER': MDB_USER,
        'PASSWORD': MDB_PASS,
        'HOST': MDB_HOST,
        'PORT':'',
    },

    'OPTIONS': {
         "init_command": "SET foreign_key_checks = 0;",
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
#STATIC_ROOT=os.path.join(BASE_DIR,'static') # uncomment while deploying
STATICFILES_DIRS=[os.path.join(BASE_DIR,'static')] # comment while deploying
# MEDIA_ROOT=os.path.join(BASE_DIR, 'static/images')
MEDIA_ROOT=os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'
MEDIA_URL = ''
# MEDIA_URL = '/static/images/'
STUDENT_PROFILE_PIC='profile'
#Define ROLE Constants
ROLE_NAME = {
    'MANAGER':'MANAGER','STUDENT':'MANAGER','EMPLOYER_ROLE':'employer'
}
ROLE_ID = { 'MANAGER': 1,'STUDENT':2,'EMPLOYER':3}
ROLES = {'MANAGER':(1,'MANAGER'),'STUDENT':(2,'STUDENT'),'EMPLOYER':(3,'EMPLOYER')}
CRISPY_TEMPLATE_PACK = 'bootstrap4'
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
    # messages.DANGER: 'alert-danger',
    #messages.ERROR: 'danger',
}
LOGIN_URL='/login/'

DATABASE_ROUTERS = [
    'spoken.router.SpokenRouter',
    'moodle.router.MdlRouter'
]

AUTHENTICATION_BACKENDS = (
    'spoken.backends.SpokenStudentBackend',
    'django.contrib.auth.backends.ModelBackend'
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)


DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR,'backup')}
CRON_LOG=os.path.join(BASE_DIR,'backup.log')
CRONJOBS=[('*/1 * * * *', 'emp.cron.backup_closed_jobs','>> ~/cron_job.log')]

MASS_MAIL=MASS_MAIL
GRADE_FILTER=GRADE_FILTER
MASS_MAIL_PAGE=MASS_MAIL_PAGE

X_FRAME_OPTIONS = 'SAMEORIGIN'
# second shortlist email setting
# EMAIL_BACKEND = EMAIL_BACKEND
# EMAIL_HOST = EMAIL_HOST
# EMAIL_PORT = EMAIL_PORT
# EMAIL_HOST_USER = EMAIL_HOST_USER
# EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD
# EMAIL_USE_TLS = EMAIL_USE_TLS
# EMAIL_USE_SSL = EMAIL_USE_SSL
EMAIL_LOG_FILE = os.path.join(BASE_DIR, 'static','email_logs')