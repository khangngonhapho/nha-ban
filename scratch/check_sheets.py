import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.append(os.path.abspath(os.getcwd()))

try:
    from curator_server import get_google_credentials
    import gspread
except Exception as e:
    print("Failed to import:", e)
    sys.exit(1)

creds = get_google_credentials()
if not creds:
    print("No credentials found.")
    sys.exit(1)

client = gspread.authorize(creds)

ids_to_check = [
    "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw",
    "1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0",
    "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
]

for fid in ids_to_check:
    print(f"\nChecking ID: {fid}")
    try:
        ss = client.open_by_key(fid)
        print(f"Opened successfully! Title: {ss.title}")
        print("Tabs in spreadsheet:")
        for s in ss.worksheets():
            print(f"  - {s.title} (rows: {s.row_count}, cols: {s.col_count})")
    except Exception as e:
        print(f"Failed to open: {str(e)}")
