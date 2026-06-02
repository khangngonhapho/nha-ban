import sys
import os
import sqlite3
from collections import defaultdict

# Configure encoding for Windows terminal
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Add the project root to sys.path to allow imports from curator_server
sys.path.append(os.path.abspath(os.getcwd()))

try:
    from curator_server import get_google_credentials, load_config
    import gspread
except Exception as e:
    print("Failed to import libraries/functions:", e)
    sys.exit(1)

print("Loading configurations...")
creds = get_google_credentials()
cfg = load_config()
sheet_id = cfg.get("sheet_id") or "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"

if not creds:
    print("Error: Could not retrieve google credentials.")
    sys.exit(1)

print(f"Connecting to Google Sheets ID: {sheet_id}...")
try:
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    print("Successfully opened spreadsheet!")
    print("Sheets in spreadsheet:")
    for s in spreadsheet.worksheets():
         print(f"  - {s.title}")
    
    # Open tab 'Pool'
    print("Opening sheet 'Pool'...")
    sheet = spreadsheet.worksheet("Pool")
    print("Reading first column ('Mã Hàng')...")
    col_a_values = sheet.col_values(1)
    print(f"Read {len(col_a_values)} rows from column 1.")
    
    # Analyze duplicates
    ma_hang_map = defaultdict(list)
    for idx, val in enumerate(col_a_values):
        row_num = idx + 1
        if not val:
            continue
        val_clean = str(val).strip()
        val_lower = val_clean.lower()
        if val_lower.startswith('tk-') or 'tk' in val_lower:
            ma_hang_map[val_clean].append(row_num)
            
    # Filter only duplicates
    duplicates = {k: v for k, v in ma_hang_map.items() if len(v) > 1}
    
    print("\n=== RESULTS FOR SHEET 'Pool' ===")
    if duplicates:
        print(f"Found {len(duplicates)} duplicate item codes (tk-...) in the 'Pool' sheet:")
        for code, rows in duplicates.items():
            print(f"  - Code: '{code}' is present {len(rows)} times on rows: {rows}")
    else:
        print("No duplicate item codes (tk-...) found in the 'Pool' sheet! All codes are unique.")
        
except Exception as e:
    print("An error occurred during sheet operations:", e)

print("\n--- Let's also check the local SQLite db (raw_archive.db) ---")
if os.path.exists('raw_archive.db'):
    try:
        conn = sqlite3.connect('raw_archive.db')
        cursor = conn.cursor()
        
        # Let's check tk_id and Ma_Hang
        cursor.execute("SELECT tk_id, COUNT(*) as c FROM listings GROUP BY tk_id HAVING c > 1;")
        dup_tk_ids = cursor.fetchall()
        print(f"Duplicates of tk_id in SQLite listings: {len(dup_tk_ids)}")
        for tk_id, count in dup_tk_ids[:10]:
            cursor.execute("SELECT id, status, Ma_Hang FROM listings WHERE tk_id = ?;", (tk_id,))
            rows = cursor.fetchall()
            print(f"  - tk_id: {tk_id} (count: {count})")
            for r in rows:
                print(f"    * ID: {r[0]}, status: {r[1]}, Ma_Hang: {r[2]}")
                
        cursor.execute("SELECT Ma_Hang, COUNT(*) as c FROM listings WHERE Ma_Hang IS NOT NULL AND Ma_Hang != '' GROUP BY Ma_Hang HAVING c > 1;")
        dup_ma_hang = cursor.fetchall()
        print(f"Duplicates of Ma_Hang in SQLite listings: {len(dup_ma_hang)}")
        for ma_hang, count in dup_ma_hang[:10]:
            cursor.execute("SELECT id, tk_id, status FROM listings WHERE Ma_Hang = ?;", (ma_hang,))
            rows = cursor.fetchall()
            print(f"  - Ma_Hang: {ma_hang} (count: {count})")
            for r in rows:
                print(f"    * ID: {r[0]}, tk_id: {r[1]}, status: {r[2]}")
                
        conn.close()
    except Exception as e:
        print("Error checking SQLite database:", e)
