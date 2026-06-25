import gspread
import sys
import re

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

print(f"Total rows in Source: {len(data)}")
if len(data) < 2:
    print("No data rows")
    sys.exit(0)

# The column headers are in row 2 (index 1)
headers = data[1]
print(f"Headers (Row 2): {headers}")

sys_id_idx = -1
link_goc_idx = -1
ma_hang_idx = -1

# Search headers dynamically in Row 2
for idx, h in enumerate(headers):
    h_clean = h.strip().lower()
    if h_clean in ["system id", "system_id", "sys id"]:
        sys_id_idx = idx
    elif h_clean in ["link gốc", "link_goc", "link goc", "link gốc", "link_goc", "link"]:
        # Let's check if there is another column. SOT.md index 44 is Link Gốc. SOT.md says index 44. Wait, the list has 'Link mặt tiền'? Let's check for 'link'
        pass
    elif h_clean in ["mã hàng", "ma_hang", "ma hang", "id"]: # In the list, column 4 (index 3) is 'id' which holds the Mã Khang Ngô ID, but where is the partner's Ma Hang? SOT.md says Column A (index 0) of Pool is Ma Hang. But in Source, let's see.
        pass

# Let's find specific headers
for idx, h in enumerate(headers):
    h_clean = h.strip().lower()
    if "system id" in h_clean:
        sys_id_idx = idx
    if "link" in h_clean:
        link_goc_idx = idx
    if "id" == h_clean:
        ma_hang_idx = idx

print(f"Indices - System ID: {sys_id_idx}, Link: {link_goc_idx}, ID: {ma_hang_idx}")

# Let's count rows having 'TK-' or 'data.thienkhoi.com' in any cell, starting from Row 3 (index 2)
old_listings_in_source = []
uuid_regex = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

for idx, row in enumerate(data[2:], start=3):
    sys_id_val = row[sys_id_idx] if sys_id_idx != -1 and sys_id_idx < len(row) else ""
    link_goc_val = row[link_goc_idx] if link_goc_idx != -1 and link_goc_idx < len(row) else ""
    ma_hang_val = row[ma_hang_idx] if ma_hang_idx != -1 and ma_hang_idx < len(row) else ""
    
    # Check if sys_id is old format (not standard 36-char UUID, and not empty, and has hyphens)
    is_old_sys_id = False
    if sys_id_val:
        sys_id_clean = sys_id_val.strip()
        # If it doesn't match standard UUID and is not a number, it's probably old
        if not uuid_regex.match(sys_id_clean) and "-" in sys_id_clean:
            is_old_sys_id = True
            
    is_old_link = False
    for cell in row:
        if "data.thienkhoi.com" in str(cell):
            is_old_link = True
            break
            
    is_old_ma_hang = False
    for cell in row:
        if str(cell).startswith("TK-"):
            is_old_ma_hang = True
            break
            
    if is_old_sys_id or is_old_link or is_old_ma_hang:
        old_listings_in_source.append({
            "row_idx": idx,
            "ma_hang": ma_hang_val,
            "sys_id": sys_id_val,
            "row_values": row[:10]  # first 10 columns for print
        })

print(f"\nFound {len(old_listings_in_source)} old listings in Source sheet:")
for item in old_listings_in_source[:15]:
    print(f"  Row {item['row_idx']}: ID={item['ma_hang']}, Sys_ID={item['sys_id']}, Vals={item['row_values']}")
if len(old_listings_in_source) > 15:
    print(f"  ... and {len(old_listings_in_source) - 15} more")
