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
    # 1. Fetch Pool
    pool_ss = client.open_by_key("1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw")
    pool_sheet = pool_ss.worksheet("Pool")
    pool_data = pool_sheet.get_all_values()
    pool_headers = pool_data[0]
    
    # 2. Fetch Source (Public)
    source_ss = client.open_by_key("1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0")
    source_sheet = source_ss.worksheet("Public")
    source_data = source_sheet.get_all_values()
    source_headers = source_data[1] # Row 2!
    
    # Search indexes
    pool_sys_idx = pool_headers.index("System ID")
    source_sys_idx = source_headers.index("System ID")
    
    print(f"Pool 'System ID' index: {pool_sys_idx}")
    print(f"Source 'System ID' index: {source_sys_idx}")
    
    IMAGE_HEADERS_MAP = [
        ("anh_1", "Ảnh 1"),
        ("anh_2", "Ảnh 2"),
        ("anh_3", "Ảnh 3"),
        ("anh_4", "Ảnh 4"),
        ("anh_5", "Ảnh 5"),
        ("anh_6", "Ảnh 6"),
        ("anh_7", "Ảnh 7"),
        ("anh_8", "Ảnh 8"),
        ("anh_9", "Ảnh 9"),
        ("anh_10", "Ảnh 10")
    ]
    
    # Build Pool Map by System ID
    pool_map = {}
    for i, row in enumerate(pool_data[1:]):
        if len(row) > pool_sys_idx:
            sys_id = row[pool_sys_idx].strip()
            if sys_id:
                pool_map[sys_id.upper()] = row
                
    print(f"Total entries in Pool: {len(pool_map)}")
    
    # Check Source rows (data starts from index 2, which is Row 3)
    matching_count = 0
    update_count = 0
    
    for j, row in enumerate(source_data[2:]):
        row_num = j + 3
        if len(row) > source_sys_idx:
            sys_id = row[source_sys_idx].strip()
            if not sys_id:
                continue
            
            sys_id_upper = sys_id.upper()
            if sys_id_upper in pool_map:
                matching_count += 1
                pool_row = pool_map[sys_id_upper]
                
                needs_update = False
                diffs = []
                for s_name, p_name in IMAGE_HEADERS_MAP:
                    s_col = source_headers.index(s_name)
                    p_col = pool_headers.index(p_name)
                    
                    s_val = row[s_col].strip() if s_col < len(row) else ""
                    p_val = pool_row[p_col].strip() if p_col < len(pool_row) else ""
                    
                    is_thien_khoi = 'thienkhoi' in s_val.lower() or 'data.thienkhoi' in s_val.lower()
                    if s_val != p_val and (is_thien_khoi or s_val == ""):
                        needs_update = True
                        diffs.append((s_name, s_val, p_val))
                
                if needs_update:
                    update_count += 1
                    if update_count <= 5:
                        print(f"\nRow {row_num}: System ID: {sys_id}")
                        for name, old, new in diffs:
                            print(f"  Col '{name}':")
                            print(f"    Old: {old[:50]}...")
                            print(f"    New: {new[:50]}...")
                            
    print(f"\nTotal Source rows matching Pool: {matching_count}")
    print(f"Total Source rows needing image updates: {update_count}")

except Exception as e:
    print("Error:", e)
