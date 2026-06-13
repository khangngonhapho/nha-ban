import traceback
import gspread
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

try:
    creds = get_google_credentials()
    print("Creds loaded:", type(creds))
    client = gspread.authorize(creds)
    print("Authorized!")
    client.open_by_key(POOL_SHEET_ID)
    print("Pool opened!")
    client.open_by_key(SOURCE_SHEET_ID)
    print("Source opened!")
except Exception as e:
    traceback.print_exc()
