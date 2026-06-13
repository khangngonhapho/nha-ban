import sys
import os
import sqlite3
import json
import gspread

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

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
    
    print("Connecting SQLite...")
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
            
    print(f"Loaded {len(db_rows)} SQLite rows.")
    
    print("Loading Google Sheets Pool...")
    ss = client.open_by_key(sheet_id)
    sheet = ss.worksheet("Pool")
    all_rows = sheet.get_all_values()
    print(f"Loaded {len(all_rows)} Sheet rows.")
    
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
    
    db_match = 0
    db_miss = 0
    cloudinary_in_sheet = 0
    cloudinary_migrated_db = 0
    cloudinary_not_migrated_db = 0
    
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
                
        # Find DB record
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
            db_match += 1
            for col_idx, db_col in col_map.items():
                if col_idx < len(row):
                    val = row[col_idx].strip()
                    if "cloudinary.com" in val:
                        cloudinary_in_sheet += 1
                        db_val = db_record.get(db_col)
                        if db_val and "r2.dev" in db_val:
                            cloudinary_migrated_db += 1
                        else:
                            cloudinary_not_migrated_db += 1
        else:
            db_miss += 1
            for col_idx in col_map.keys():
                if col_idx < len(row):
                    val = row[col_idx].strip()
                    if "cloudinary.com" in val:
                        cloudinary_in_sheet += 1
                        cloudinary_not_migrated_db += 1
                        
    print(f"Matched rows: {db_match}")
    print(f"Missed rows: {db_miss}")
    print(f"Cloudinary cells in sheet: {cloudinary_in_sheet}")
    print(f"Cloudinary cells mapped to R2 in DB: {cloudinary_migrated_db}")
    print(f"Cloudinary cells NOT mapped to R2 in DB: {cloudinary_not_migrated_db}")

if __name__ == '__main__':
    main()
