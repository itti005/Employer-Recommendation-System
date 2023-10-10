from emp.models import Job
from datetime import date  

def project_two():
            print("Hello World")
            job = Job(
            title="Software Engineer",
            # location="New York",
            requirements="Python, Django, SQL",
            job_type_id= 1,
            last_app_date= date(2023, 8, 30),
            foss ="",
            institute_type=""
        )

            job.save()
            print(" World")