from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from .models import *
from events.models import Student as SpkStudent
from emp.models import Student as RecStudent

def student_homepage(request):
    context={}
    student = RecStudent.objects.get(user_id=request.user.id)
    print("*************** request.user.RecStudent",student)
    applied_jobs = AppliedJob.objects.filter(student_id=student.id)
    return render(request,'emp/student_homepage.html',context)


def employer_homepage(request):
    context={}
    return render(request,'emp/employer_homepage.html',context)


def manager_homepage(request):
    context={}
    return render(request,'emp/manager_homepage.html',context)

def handlelogout(request):
    logout(request)
    return redirect('index')

def index(request):
     context={}
     return render(request,'emp/index.html',context)
