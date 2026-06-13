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
    
    matched_count = 0
    unmatched_count = 0
    unmatched_cld_cells = 0
    
    # Column indices for images
    col_map_keys = [
        1, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
        40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54,
        80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92
    ]
    
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
            matched_count += 1
        else:
            unmatched_count += 1
            for col_idx in col_map_keys:
                if col_idx < len(row):
                    cell_val = row[col_idx].strip()
                    if cell_val and "cloudinary.com" in cell_val:
                        unmatched_cld_cells += 1
                        
    print(f"Total rows in sheet (excluding header): {len(all_rows) - 1}")
    print(f"Matched rows in DB: {matched_count}")
    print(f"Unmatched rows in DB: {unmatched_count}")
    print(f"Cloudinary cells in unmatched rows: {unmatched_cld_cells}")

if __name__ == '__main__':
    main()
