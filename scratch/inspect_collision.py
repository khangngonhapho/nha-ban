import sys
import os
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

sys.path.append(os.path.abspath(os.getcwd()))

try:
    from curator_server import get_google_credentials, load_config
    import gspread
except Exception as e:
    print("Failed to import:", e)
    sys.exit(1)

print("Loading configurations...")
creds = get_google_credentials()
cfg = load_config()
sheet_id = cfg.get("sheet_id") or "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"

client = gspread.authorize(creds)
spreadsheet = client.open_by_key(sheet_id)
sheet = spreadsheet.worksheet("Pool")

# Find 'TK-5E5437', 'TK-3D5E5437', 'TK-485E5437'
print("\nSearching values in first column of Pool...")
col_a_values = sheet.col_values(1)

search_terms = ['TK-5E5437', 'TK-3D5E5437', 'TK-485E5437', '5E5437', '3D5E5437', '485E5437']
found_any = False
for idx, val in enumerate(col_a_values):
    val_clean = str(val).strip()
    if any(term.lower() in val_clean.lower() for term in search_terms):
        print(f"Row {idx+1}: {val_clean}")
        found_any = True
        # Let's get the entire row
        row_data = sheet.row_values(idx+1)
        print(f"  Row length: {len(row_data)}")
        # Print some interesting columns (e.g. description or address, or first 10 columns)
        print(f"  First 10 values: {row_data[:10]}")
        # Let's print any values that contain the tk_ids
        for col_idx, cell in enumerate(row_data):
            if 'fedjlr-mna1q7ua-3d5e5437' in str(cell) or 'cv5xsr-mhyaft63-485e5437' in str(cell):
                print(f"  Col {col_idx+1}: {cell}")

if not found_any:
    print("None of the search terms found in the Pool sheet.")

print("\nChecking local SQLite for details of these two listings:")
conn = sqlite3.connect('raw_archive.db')
cursor = conn.cursor()
cursor.execute("SELECT id, tk_id, Ma_Hang, status, Quan, Phuong, Duong, Ngo_So_Nha FROM listings WHERE tk_id IN ('fedjlr-mna1q7ua-3d5e5437', 'cv5xsr-mhyaft63-485e5437')")
for r in cursor.fetchall():
    print(f"SQLite -> ID: {r[0]}, tk_id: {r[1]}, Ma_Hang: {r[2]}, status: {r[3]}, Address: {r[7]} {r[6]}, {r[5]}, {r[4]}")
conn.close()
