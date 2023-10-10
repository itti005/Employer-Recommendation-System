

# models.py
from django.db import models

class Company(models.Model):
    company_name = models.CharField(max_length=100)
    # Add other fields as needed

class Job(models.Model):
    job_description = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    # Add other fields as needed
