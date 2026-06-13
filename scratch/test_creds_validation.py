import sys
import os

# Add root folder to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Reconfigure output encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

from google.oauth2 import service_account
import google.auth.transport.requests

req = google.auth.transport.requests.Request()

files_to_test = [
    'credentials.json',
    'khangngo-admin-a96043c2f638.json'
]

print("--- STARTING OAUTH TEST ---")
for f in files_to_test:
    if os.path.exists(f):
        print(f"Testing file: {f}...")
        try:
            creds = service_account.Credentials.from_service_account_file(
                f, 
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            creds.refresh(req)
            print(f"  SUCCESS! Token prefix: {creds.token[:15]}...")
        except Exception as e:
            print(f"  FAILED! Error: {str(e)}")
    else:
        print(f"File not found: {f}")
print("--- TEST COMPLETED ---")
