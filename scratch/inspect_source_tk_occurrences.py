import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

sid = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"

try:
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open_by_key(sid)
    w = sh.worksheet("Source")
    data = w.get_all_values()
except Exception as e:
    print(f"Error loading sheet: {e}")
    sys.exit(1)

tk_count = 0
link_count = 0
both_count = 0

for idx, row in enumerate(data[2:], start=3):
    row_str = " ".join(str(cell) for cell in row)
    has_tk = any(str(cell).startswith("TK-") or "TK-" in str(cell) for cell in row)
    has_link = "data.thienkhoi.com" in row_str
    
    if has_tk:
        tk_count += 1
    if has_link:
        link_count += 1
    if has_tk and has_link:
        both_count += 1
        
    if has_tk or has_link:
        print(f"Row {idx}: has_tk={has_tk}, has_link={has_link}, row_id={row[3] if len(row) > 3 else ''}")
        # Print cells that contain them
        for c_idx, cell in enumerate(row):
            if "TK-" in str(cell) or "data.thienkhoi.com" in str(cell):
                print(f"  Col {c_idx} ('{data[1][c_idx]}'): {cell}")

print(f"\nSummary:")
print(f"  Rows with 'TK-': {tk_count}")
print(f"  Rows with 'data.thienkhoi.com': {link_count}")
print(f"  Rows with both: {both_count}")
