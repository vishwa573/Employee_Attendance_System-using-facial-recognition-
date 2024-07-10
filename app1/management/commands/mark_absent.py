from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from app1.models import Employee
from app1.utils import mark_absent

SHEET_ID = '1ZnNV5XABRfmFbcbJsQlrcYcLXm9K2_OOZgZ3ozlDqMs'
RANGE_NAME = 'Sheet1!A:D'

# Path to your service account key file
from pathlib import Path
import os

'''BASE_DIR = Path(__file__).resolve().parent.parent
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR,'app1','attendance','credentials.json')

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"] )
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()'''

class Command(BaseCommand):
    help = 'Mark employees as absent if they did not mark attendance for the day'

    def handle(self, *args, **kwargs):
        mark_absent()
        self.stdout.write(self.style.SUCCESS('Successfully marked absentees.'))