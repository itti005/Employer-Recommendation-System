from django.http import JsonResponse
from google.oauth2.service_account import Credentials
import gspread
from emp.models import Company,Job
from emp.views import CompanyDetailView

# from spreadsheet.models import SheetData

def fetch_google_sheet(request, spreadsheet_id):
    # Load the credentials from the JSON key file
    print(1)
    scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

    print(f"spreadsheet_id : {spreadsheet_id}")
    credentials = Credentials.from_service_account_file('/home/etti/Employee-Recommendation-System/Employer-Recommendation-System/employer_recommendation_system/Utilities/gentle-pier-398305-718461d4d2cd.json',
    scopes=scopes)
    print(2)
    # Authenticate with Google Sheets
    gc = gspread.authorize(credentials)
    print(3)
    try:
        # Open the Google Sheets spreadsheet by ID
        sheet = gc.open_by_key(spreadsheet_id)

        # Access a specific worksheet within the spreadsheet
        worksheet = sheet.get_worksheet(0)  # Change the index as needed

        # Fetch the data from the worksheet
        data = worksheet.get_all_records()
        print(type(data))
        print(data)
        # Save data to the database
        for row in data:
          company_name = row.get("Company Name")
          job_description = row.get('job_description')
          print(f"company_name : {company_name}")
          company = Company(name=company_name)
        #   CompanyDetailView.append(company)
          company.save()  


        


        # spreadsheet_id = ('1EUN10lGd7_ikNgt7pWRyt5RA5yCVorwMOQOqbDnuzrE')
        # response = fetch_google_sheet(request, spreadsheet_id)
        # Query the database to check if data is stored
         # Retrieve all records as a queryset
        # You can print or return 'stored_data' as a JSON response to verify

        return JsonResponse({'message': 'Data fetched and stored successfully.'})




        # Return the data as JSON response
        # return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
