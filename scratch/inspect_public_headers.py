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
client = gspread.authorize(creds)

try:
    fid = "1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0"
    ss = client.open_by_key(fid)
    sheet = ss.worksheet("Public")
    values = sheet.get_all_values()
    headers = values[0]
    
    print("=== PUBLIC SHEET HEADERS (Total cols:", len(headers), ") ===")
    for idx, h in enumerate(headers):
        print(f"Col {idx+1} ({gspread.utils.rowcol_to_a1(1, idx+1)[:2].replace('1','')}) : '{h}'")
        
    print("\n=== SAMPLE DATA (Row 2, 3, 4) ===")
    for r_idx in range(1, min(4, len(values))):
        print(f"Row {r_idx+1}:")
        row = values[r_idx]
        for idx, h in enumerate(headers):
            val = row[idx] if idx < len(row) else ""
            if val.strip() != "":
                print(f"  Col {idx+1} ('{h}'): {val[:60]}...")
                
except Exception as e:
    print("Error:", e)
