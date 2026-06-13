import sys
import sqlite3
import gspread

sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
import manager

def main():
    creds = manager.get_google_credentials()
    if not creds:
        print("Could not load credentials.")
        return
        
    client = gspread.authorize(creds)
    sheet_id = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
    db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
    
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    db_rows = cursor.execute("SELECT * FROM listings").fetchall()
    conn.close()
    
    db_by_tk_id = {}
    db_by_sys_id = {}
    db_by_ma_hang = {}
    db_by_ma_kn = {}
    
    for r in db_rows:
        d = dict(r)
        tk_id = d.get("tk_id")
        sys_id = d.get("System_ID")
        ma_hang = d.get("Ma_Hang")
        ma_kn = d.get("Ma_Khang_Ngo_ID")
        
        if tk_id:
            db_by_tk_id[tk_id.strip()] = d
        if sys_id:
            db_by_sys_id[sys_id.strip()] = d
        if ma_hang:
            db_by_ma_hang[ma_hang.strip()] = d
        if ma_kn:
            db_by_ma_kn[ma_kn.strip()] = d
            
    ss = client.open_by_key(sheet_id)
    sheet = ss.worksheet("Pool")
    all_rows = sheet.get_all_values()
    
    col_map = {
        1: "Hinh_Nhan_Dien",         # Col 2
        27: "So_do_thua_dat_1",      # Col 28
        28: "So_do_thua_dat_2",      # Col 29
        29: "Hinh_Mat_Tien",         # Col 30
        30: "Hinh_Hem_1",            # Col 31
        31: "Hinh_Hem_2",
        32: "Hinh_Hem_3",
        33: "Hinh_Hem_4",
        34: "Hinh_Hem_5",
        35: "Hinh_Hem_6",
        36: "Hinh_Hem_7",
        37: "Hinh_Hem_8",
        38: "Hinh_Hem_9",
        39: "Hinh_Hem_10",           # Col 40
        40: "Anh_1",                 # Col 41
        41: "Anh_2",
        42: "Anh_3",
        43: "Anh_4",
        44: "Anh_5",
        45: "Anh_6",
        46: "Anh_7",
        47: "Anh_8",
        48: "Anh_9",
        49: "Anh_10",
        50: "Anh_11",
        51: "Anh_12",
        52: "Anh_13",
        53: "Anh_14",
        54: "Anh_15",                # Col 55
        80: "So_do_thua_dat_3",      # Col 81
        81: "So_do_thua_dat_4",      # Col 82
        82: "So_do_thua_dat_5",      # Col 83
        83: "Anh_16",                # Col 84
        84: "Anh_17",
        85: "Anh_18",
        86: "Anh_19",
        87: "Anh_20",
        88: "Anh_21",
        89: "Anh_22",
        90: "Anh_23",
        91: "Anh_24",
        92: "Anh_25"                 # Col 93
    }
    
    direct_migrate_count = 0
    skip_cld_count = 0
    match_r2_count = 0
    no_match_rows = 0
    
    for r_idx, row in enumerate(all_rows[1:], start=2):
        if len(row) < 74:
            continue
            
        ma_hang = row[0].strip()
        ma_kn = row[55].strip()
        sys_id = row[72].strip()
        link_goc = row[73].strip()
        
        tk_id = ""
        if link_goc:
            parts = link_goc.split('/')
            if len(parts) > 0:
                tk_id = parts[-1].strip()
                
        db_record = None
        if tk_id and tk_id in db_by_tk_id:
            db_record = db_by_tk_id[tk_id]
        elif sys_id and sys_id in db_by_sys_id:
            db_record = db_by_sys_id[sys_id]
        elif ma_kn and ma_kn in db_by_ma_kn:
            db_record = db_by_ma_kn[ma_kn]
        elif ma_hang and ma_hang in db_by_ma_hang:
            db_record = db_by_ma_hang[ma_hang]
            
        if db_record:
            # Gather all R2 values and Cloudinary values from DB for this record
            db_r2_values = [str(val).strip() for val in db_record.values() if val and "r2.dev" in str(val)]
            db_cld_values = [str(val).strip() for val in db_record.values() if val and "cloudinary.com" in str(val)]
            
            for sheet_col_idx, db_col_name in col_map.items():
                if sheet_col_idx >= len(row):
                    continue
                sheet_val = row[sheet_col_idx].strip()
                
                if sheet_val and "cloudinary.com" in sheet_val:
                    from urllib.parse import urlparse
                    filename = urlparse(sheet_val).path.split('/')[-1]
                    file_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
                    
                    # 1. Search in all DB R2 values
                    found_r2 = None
                    for r2_val in db_r2_values:
                        if file_base in r2_val:
                            found_r2 = r2_val
                            break
                            
                    if found_r2:
                        match_r2_count += 1
                        continue
                        
                    # 2. Search in all DB Cloudinary values (if it exists, it is a dead link)
                    found_cld = False
                    for cld_val in db_cld_values:
                        if file_base in cld_val:
                            found_cld = True
                            break
                            
                    if found_cld:
                        skip_cld_count += 1
                        continue
                        
                    # 3. Direct migration
                    direct_migrate_count += 1
        else:
            no_match_rows += 1
            # Unmatched row - all Cloudinary cells go to direct migration
            for sheet_col_idx in col_map.keys():
                if sheet_col_idx < len(row):
                    sheet_val = row[sheet_col_idx].strip()
                    if sheet_val and "cloudinary.com" in sheet_val:
                        direct_migrate_count += 1
                        
    print(f"--- NEW MATCHING LOGIC RESULTS ---")
    print(f"Match R2 count: {match_r2_count}")
    print(f"Skip Cloudinary count (404s): {skip_cld_count}")
    print(f"Direct migration count (Actual network calls needed): {direct_migrate_count}")
    print(f"Unmatched rows count: {no_match_rows}")

if __name__ == '__main__':
    main()
