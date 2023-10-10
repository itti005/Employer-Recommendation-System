from django.shortcuts import render
from emp.models import Company
from emp.models import Job
# Create your views here.
def project():
    import gspread
    # from oauth2client.service_account import ServiceAccountCredentials
    from google.oauth2.service_account import Credentials

    import numpy as np
    import pandas as pd

 

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

 

    credentials = Credentials.from_service_account_file(
        '/home/etti/Employee-Recommendation-System/Employer-Recommendation-System/employer_recommendation_system/Utilities/gentle-pier-398305-718461d4d2cd.json',
        scopes=scopes
    )

 

    gc = gspread.authorize(credentials)
    sh = gc.open_by_key('1EUN10lGd7_ikNgt7pWRyt5RA5yCVorwMOQOqbDnuzrE')
    worksheet = sh.worksheets()[0]
    print(worksheet.get('A1'))
    values_list = worksheet.col_values(1)
    print(values_list)
    array = np.array([["Etty", "Student" , "F" , "Karnataka"], ["Rohini" ,"Student" ,"F" ,"Maharashtra"]])
    worksheet.update('A2', array.tolist())

    # Access and print data
    data = worksheet.get_all_values()
    for row in data:
        
        print(len(Company.objects.all()))

        company = Company()
        company.company_name = row[2]
        company.save()

        print(len(Company.objects.all()))

      


# from utilities.views import project
# from emp.models import Company