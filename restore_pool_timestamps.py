import sys
import os
import sqlite3
import re
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

import gspread
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'd:/LHTBrain/01_PROJECTS/BDS-KhangNgo/khangngo-admin-a96043c2f638.json'
POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
DB_FILE = 'd:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db'

# 1. Connect to SQLite and fetch timestamps
print("Connecting to SQLite raw_archive.db...")
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Get column names to make sure we query correctly
cursor.execute("PRAGMA table_info(listings)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Listings table columns: {len(columns)}")

# Make sure Ma_Hang, Last_Crawl, Last_Sync are there
query_cols = []
for col in ["Ma_Hang", "Last_Crawl", "Last_Sync"]:
    # Check if column exists, case-insensitive
    match = [c for c in columns if c.lower() == col.lower()]
    if match:
        query_cols.append(match[0])
    else:
        print(f"Error: column {col} not found in listings table.")
        sys.exit(1)

print(f"Querying SQLite using columns: {query_cols}")
cursor.execute(f"SELECT `{query_cols[0]}`, `{query_cols[1]}`, `{query_cols[2]}` FROM listings")
rows = cursor.fetchall()
print(f"Fetched {len(rows)} records from SQLite database.")

db_data = {}
for row in rows:
    ma_hang = str(row[0]).strip() if row[0] else ""
    last_crawl = str(row[1]).strip() if row[1] else ""
    last_sync = str(row[2]).strip() if row[2] else ""
    if ma_hang:
        db_data[ma_hang] = (last_crawl, last_sync)

conn.close()

# 2. Connect to Google Sheets Pool
print("\nConnecting to Google Sheets...")
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open_by_key(POOL_SHEET_ID)
worksheet = sh.worksheet("Pool")

print("Reading all data from sheet Pool...")
all_rows = worksheet.get_all_values()
print(f"Total rows in sheet Pool: {len(all_rows)}")

# 3. Process and prepare updates
# Col BZ is Index 77 (1-based column 78)
# Col CA is Index 78 (1-based column 79)
# Col CC is Index 80 (1-based column 81) -> check for junk datetime
# Col CD is Index 81 (1-based column 82) -> check for junk datetime

# Regex to detect datetime junk: matches "27/05/2026 05:23:48" or "2026-05-31 02:14:39"
datetime_regex = re.compile(r'(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})')

cell_list = []
updates_count = 0
cleanup_count = 0

for r_idx, row in enumerate(all_rows, 1):
    if r_idx < 3: # Skip header rows
        continue
    
    ma_hang = row[0].strip() if len(row) > 0 else ""
    if not ma_hang:
        continue
        
    # Check if we have this record in SQLite
    has_update = False
    new_crawl_val = ""
    new_sync_val = ""
    
    if ma_hang in db_data:
        db_crawl, db_sync = db_data[ma_hang]
        # Current values in sheet BZ (index 77) and CA (index 78)
        curr_crawl = row[77] if len(row) > 77 else ""
        curr_sync = row[78] if len(row) > 78 else ""
        
        # If SQLite has newer or missing info, update it
        if db_crawl and db_crawl != curr_crawl:
            new_crawl_val = db_crawl
            has_update = True
        if db_sync and db_sync != curr_sync:
            new_sync_val = db_sync
            has_update = True

    # Check for junk datetimes in Col CC (index 80) and CD (index 81)
    val_cc = row[80] if len(row) > 80 else ""
    val_cd = row[81] if len(row) > 81 else ""
    
    clear_cc = bool(datetime_regex.search(val_cc))
    clear_cd = bool(datetime_regex.search(val_cd))
    
    # Add cells to update
    if new_crawl_val:
        # Col BZ is column 78
        cell_list.append(gspread.Cell(row=r_idx, col=78, value=new_crawl_val))
        updates_count += 1
    if new_sync_val:
        # Col CA is column 79
        cell_list.append(gspread.Cell(row=r_idx, col=79, value=new_sync_val))
        updates_count += 1
        
    if clear_cc:
        # Col CC is column 81
        cell_list.append(gspread.Cell(row=r_idx, col=81, value=""))
        cleanup_count += 1
        print(f"Row {r_idx} ({ma_hang}): Found junk datetime in CC: '{val_cc}' -> will clear")
    if clear_cd:
        # Col CD is column 82
        cell_list.append(gspread.Cell(row=r_idx, col=82, value=""))
        cleanup_count += 1
        print(f"Row {r_idx} ({ma_hang}): Found junk datetime in CD: '{val_cd}' -> will clear")

# 4. Perform batch update
if cell_list:
    print(f"\nPerforming batch update of {len(cell_list)} cells...")
    print(f"- Timestamps updates: {updates_count}")
    print(f"- Junk cleanup updates: {cleanup_count}")
    
    # Split into chunks of 1000 cells to prevent API payload size limits
    chunk_size = 1000
    for i in range(0, len(cell_list), chunk_size):
        chunk = cell_list[i:i + chunk_size]
        worksheet.update_cells(chunk, value_input_option='USER_ENTERED')
        print(f"Updated chunk {i // chunk_size + 1}/{-(-len(cell_list) // chunk_size)}")
        
    print("Google Sheets Pool update finished successfully!")
else:
    print("\nNo updates or cleanups required.")
