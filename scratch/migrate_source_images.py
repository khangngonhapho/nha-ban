import sys
import os
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
    
    # Open 'Pool' and 'Source' sheets
    print("Opening tab 'Pool'...")
    pool_sheet = spreadsheet.worksheet("Pool")
    print("Opening tab 'Source'...")
    source_sheet = spreadsheet.worksheet("Source")
    
    # Get all values
    print("Fetching all values from Pool...")
    pool_values = pool_sheet.get_all_values()
    print("Fetching all values from Source...")
    source_values = source_sheet.get_all_values()
    
    print(f"Pool: {len(pool_values)} rows (including header)")
    print(f"Source: {len(source_values)} rows (including header)")
    
    if len(pool_values) < 2 or len(source_values) < 2:
        print("Error: One of the sheets is empty.")
        sys.exit(1)
        
    pool_headers = pool_values[0]
    source_headers = source_values[0]
    
    print("\n--- Headers of 'Pool' (first 10) ---")
    print(pool_headers[:10])
    
    print("\n--- Headers of 'Source' (first 10) ---")
    print(source_headers[:10])
    
    # Map headers to indices
    pool_header_map = {name.strip(): idx for idx, name in enumerate(pool_headers)}
    source_header_map = {name.strip(): idx for idx, name in enumerate(source_headers)}
    
    # List of image headers we want to migrate
    IMAGE_HEADERS = [
        "Hình Nhận Diện",
        "Sơ đồ thửa đất 1", "Sơ đồ thửa đất 2",
        "Hình Mặt Tiền",
        "Hình Hẻm 1", "Hình Hẻm 2", "Hình Hẻm 3", "Hình Hẻm 4", "Hình Hẻm 5",
        "Hình Hẻm 6", "Hình Hẻm 7", "Hình Hẻm 8", "Hình Hẻm 9", "Hình Hẻm 10",
        "Ảnh 1", "Ảnh 2", "Ảnh 3", "Ảnh 4", "Ảnh 5", "Ảnh 6", "Ảnh 7", "Ảnh 8",
        "Ảnh 9", "Ảnh 10", "Ảnh 11", "Ảnh 12", "Ảnh 13", "Ảnh 14", "Ảnh 15",
        "Ảnh Public (VD: 1,3,5)", "Ảnh Hẻm Public (VD: 1,2)"
    ]
    
    # Verify image headers exist in both sheets
    pool_img_cols = []
    source_img_cols = []
    for h in IMAGE_HEADERS:
        if h in pool_header_map and h in source_header_map:
            pool_img_cols.append((h, pool_header_map[h]))
            source_img_cols.append((h, source_header_map[h]))
        else:
            missing = []
            if h not in pool_header_map: missing.append("Pool")
            if h not in source_header_map: missing.append("Source")
            print(f"Warning: Header '{h}' missing in {', '.join(missing)}")
            
    print(f"\nTotal image columns to migrate: {len(pool_img_cols)}")
    
    # Map Pool rows by 'Mã Hàng'
    pool_ma_hang_idx = pool_header_map.get("Mã Hàng")
    if pool_ma_hang_idx is None:
        print("Error: 'Mã Hàng' column not found in Pool sheet.")
        sys.exit(1)
        
    pool_rows_map = {}
    for idx, row in enumerate(pool_values[1:]):
        if len(row) > pool_ma_hang_idx:
            ma_hang = row[pool_ma_hang_idx].strip().upper()
            if ma_hang:
                pool_rows_map[ma_hang] = (idx + 2, row) # (row_number_1_indexed, row_data)
                
    # Search for Source rows to migrate
    source_ma_hang_idx = source_header_map.get("Mã Hàng")
    if source_ma_hang_idx is None:
        print("Error: 'Mã Hàng' column not found in Source sheet.")
        sys.exit(1)
        
    update_candidates = []
    
    for idx, row in enumerate(source_values[1:]):
        row_num = idx + 2
        if len(row) <= source_ma_hang_idx:
            continue
        ma_hang = row[source_ma_hang_idx].strip().upper()
        if not ma_hang:
            continue
            
        if ma_hang in pool_rows_map:
            pool_row_num, pool_row_data = pool_rows_map[ma_hang]
            
            # Check if this row in Source needs migration (i.e. has Thien Khoi images or mismatches)
            needs_update = False
            differences = []
            
            for h, s_col_idx in source_img_cols:
                p_col_idx = pool_header_map[h]
                
                s_val = row[s_col_idx].strip() if s_col_idx < len(row) else ""
                p_val = pool_row_data[p_col_idx].strip() if p_col_idx < len(pool_row_data) else ""
                
                # Check for Thien Khoi links
                is_thien_khoi = 'thienkhoi' in s_val.lower() or 'data.thienkhoi' in s_val.lower()
                
                # We update if it's currently a Thien Khoi link and Pool has a Cloudinary link (or is different)
                if s_val != p_val and (is_thien_khoi or s_val == ""):
                    needs_update = True
                    differences.append((h, s_val, p_val))
            
            if needs_update:
                update_candidates.append({
                    "row_num": row_num,
                    "ma_hang": ma_hang,
                    "pool_row_num": pool_row_num,
                    "diffs": differences,
                    "pool_row_data": pool_row_data
                })
                
    print(f"\nFound {len(update_candidates)} rows in Source sheet that need image migration!")
    
    # Print some samples
    for i, cand in enumerate(update_candidates[:5]):
        print(f"\nCandidate {i+1}: Mã Hàng: {cand['ma_hang']} (Source Row: {cand['row_num']}, Pool Row: {cand['pool_row_num']})")
        for h, old_val, new_val in cand['diffs'][:3]:
            print(f"  - Column '{h}':")
            print(f"    Old: {old_val[:80]}...")
            print(f"    New: {new_val[:80]}...")
        if len(cand['diffs']) > 3:
            print(f"    ... and {len(cand['diffs']) - 3} more columns")
            
    # Save candidates data to a json file for the next step
    import json
    with open('scratch/migration_candidates.json', 'w', encoding='utf-8') as f:
        json.dump([{
            "row_num": c["row_num"],
            "ma_hang": c["ma_hang"],
            "pool_row_num": c["pool_row_num"],
            "diffs": [(h, o, n) for h, o, n in c["diffs"]]
        } for c in update_candidates], f, ensure_ascii=False, indent=2)
    print("\nSaved dry-run migration candidates to 'scratch/migration_candidates.json'")
    
except Exception as e:
    print("An error occurred:", e)
