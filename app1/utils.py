from geopy.distance import distance, Point

from .models import Employee

def calculate_distance(id,lat, long):

    emp_loc=Point(lat,long)
    Lat=9.921584444757245 
    Long= 78.14872044418888
    dist=distance(Point(Lat,Long),emp_loc).meters
    print("Distance:",dist)

    if dist<200:
        print("Allowed Access for Distance:",dist)
        return True

    #locations=Location.objects.filter(Q(access=1) | Q(access=3))# Individually accepted and common locations
    employee=Employee.objects.get(idd=id)

    for location in employee.locations.filter(access=1):

        Allowed_lat=location.latitude
        Allowed_long=location.longtitude
        Allowed_loc=Point(Allowed_lat,Allowed_long)

        dist=distance(Allowed_loc,emp_loc).meters
        print("Distance:",dist)
        if dist<200:
            print("Allowed Access for Distance:",dist)
            return True
    return False
 

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SHEET_ID = '1ZnNV5XABRfmFbcbJsQlrcYcLXm9K2_OOZgZ3ozlDqMs'
RANGE_NAME = 'Sheet1!A:D'

# Path to your service account key file
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR,'app1','attendance','credentials.json')

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"] )
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

def update_attendance(employee_id):
    
    Res=sheet.values().get(spreadsheetId=SHEET_ID,range=RANGE_NAME).execute()
    Val=Res.get('values',[])
    
    cdatetime=datetime.now()
    date=cdatetime.strftime("%Y-%m-%d")
    time=cdatetime.strftime("%H-%M-%S")

    for row in Val:
        if int(row[0]) == int(employee_id):
            if date == row[2]:#check if attendance is already marked for that day
                return 2
            else:
                continue

    values = [
        [employee_id, "Present",date,time]
    ]
    body = {
        'values': values
    }
    
    # Call the Sheets API to append the data
    result = sheet.values().append(
        spreadsheetId=SHEET_ID,
        range=RANGE_NAME,
        valueInputOption='RAW',
        body=body
    ).execute()
    
    print(f"{result.get('updates').get('updatedCells')} cells appended.")
    return 1

def filter_data(values, start_date, end_date):
    filtered = []
    for row in values:
        #print(row)
        try:
            record_date = datetime.strptime(row[2], "%Y-%m-%d")
            #print(f"Record datetime: {record_date}, Start date: {start_date}, End date: {end_date}")
            if start_date.date() <= record_date.date()<= end_date.date():
                print('WOrked')
                filtered.append(row)
        except Exception as e:
            print(f"Error parsing date: {e}")
    return filtered

def download_attendance(employee_id, report_type):
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        return None

    # Defining the date range based on the report type
    cdatetime = datetime.now()
    if report_type == 'daily':
        print(report_type)
        start_date = cdatetime
        end_date = cdatetime
    elif report_type == 'total':
        start_date = datetime.strptime('2024-06-21','%Y-%m-%d')
        end_date = cdatetime

    elif report_type == 'weekly':
        start_date = cdatetime - timedelta(days=cdatetime.weekday())
        end_date = start_date + timedelta(days=6)
    elif report_type == 'monthly':
        start_date = cdatetime.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    elif report_type == 'custom':
        start_date = cdatetime
        end_date = cdatetime
    else:
        return None

    emp_attendance = [row for row in values if int(row[0]) == int(employee_id)]
    filtered_attendance = filter_data(emp_attendance, start_date, end_date)
    return filtered_attendance

def get_attendance(employee_id,count,start_date,end_date):
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    if count == 1:#Only employee_id filter
        emp_attendance=[row for row in values if int(row[0])==int(employee_id)]
        return emp_attendance
    
    if count == 0:
        return values
    
    if count==2:#only start_date
        start_date=datetime.strptime(start_date,"%Y-%m-%d")
        emp_attendance=[row for row in values if datetime.strptime(row[2],"%Y-%m-%d").date() > start_date.date() ]
        return emp_attendance
    
    if count==3:#start date and end date
        start_date=datetime.strptime(start_date,"%Y-%m-%d"). date()
        end_date=datetime.strptime(end_date,"%Y-%m-%d").date()
        emp_attendance=[row for row in values if end_date >= datetime.strptime(row[2],"%Y-%m-%d").date() >= start_date ]
        return emp_attendance
    
    if count==4:#start date and id
        start_date=datetime.strptime(start_date,"%Y-%m-%d"). date()
        emp_attendance=[row for row in values if (datetime.strptime(row[2],"%Y-%m-%d").date() >= start_date) and (int(row[0])==int(employee_id)) ]
        return emp_attendance


    if count == 5:#start date,end date with id
        start_date=datetime.strptime(start_date,"%Y-%m-%d"). date()
        end_date=datetime.strptime(end_date,"%Y-%m-%d").date()
        emp_attendance=[row for row in values if (end_date >= datetime.strptime(row[2],"%Y-%m-%d").date() >= start_date) and (int(row[0])==int(employee_id)) ]
        return emp_attendance
    
    if count == 6:
        end_date=datetime.strptime(end_date,"%Y-%m-%d").date()
        emp_attendance=[row for row in values if (end_date >= datetime.strptime(row[2],"%Y-%m-%d").date() ) and (int(row[0])==int(employee_id)) ]
        return emp_attendance
    

    else:
        print("NO valid Count option")
        return values


    
def mark_absent():
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    cdatetime=datetime.now()
    date=cdatetime.date()
    date_str=date.strftime("%Y-%m-%d")
    time_str=cdatetime.strftime("%H-%M-%S")
    Employees=Employee.objects.all()
    for employee in Employees:
        absent=True
        for row in values:
            record_date = datetime.strptime(row[2], "%Y-%m-%d")
            if date == record_date.date() and int(row[0]) == int(employee.idd):
                print(employee.idd)
                absent=False
                break

        if absent==True:
            values = [[employee.idd, "Absent",date_str,time_str] ]
            body = {'values': values}

            sheet.values().append(spreadsheetId=SHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body).execute()


