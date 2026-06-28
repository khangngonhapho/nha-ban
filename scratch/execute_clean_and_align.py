import sqlite3
import gspread
import sys
import os
import shutil
import re

sys.stdout.reconfigure(encoding='utf-8')

# Constants
db_file = "raw_archive.db"
temp_db_file = "raw_archive_temp_read.db"
backup_dir = "Backup DB"
pool_sid = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
source_sid = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"

def main():
    print("=== STARTING CLEAN & ALIGN OPERATION ===")

    # 1. Backing up SQLite files
    print("\n[Step 1] Backing up SQLite databases...")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")
        
    if os.path.exists(db_file):
        db_backup = os.path.join(backup_dir, "raw_archive_pre_clean_tk.db")
        shutil.copy2(db_file, db_backup)
        print(f"  Backup of raw_archive.db saved to {db_backup}")
    else:
        print("  [❌ ERROR] raw_archive.db not found!")
        sys.exit(1)
        
    if os.path.exists(temp_db_file):
        temp_db_backup = os.path.join(backup_dir, "raw_archive_temp_read_pre_clean_tk.db")
        shutil.copy2(temp_db_file, temp_db_backup)
        print(f"  Backup of raw_archive_temp_read.db saved to {temp_db_backup}")
        
    # 2. Loading mapping data from SQLite before deletion
    print("\n[Step 2] Reading listings from SQLite for classification mapping...")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    # Store complete metadata map: System_ID -> (Ma_Hang, Link_Goc, Correct_Ma_Khang_Ngo)
    sqlite_map = {}
    all_rows = c.execute("SELECT System_ID, Ma_Hang, Link_Goc, Ma_Khang_Ngo_ID FROM listings").fetchall()
    for row in all_rows:
        sys_id, ma_hang, link_goc, ma_kn = row
        if sys_id:
            sqlite_map[sys_id.strip()] = {
                "ma_hang": ma_hang.strip() if ma_hang else "",
                "link_goc": link_goc.strip() if link_goc else "",
                "ma_kn": ma_kn.strip() if ma_kn else ""
            }
            
    print(f"  Loaded {len(sqlite_map)} records from SQLite.")
    conn.close()

    # 3. Authenticate with Google Sheets
    print("\n[Step 3] Connecting to Google Sheets API...")
    try:
        gc = gspread.service_account(filename='credentials.json')
        print("  Authenticated successfully with Google Sheets API.")
    except Exception as e:
        print(f"  [❌ ERROR] Google Sheets authentication failed: {e}")
        sys.exit(1)

    # 4. Backing up and cleaning Google Sheet Pool
    print("\n[Step 4] Processing Google Sheet Pool...")
    try:
        pool_sh = gc.open_by_key(pool_sid)
        print(f"  Opened spreadsheet: {pool_sh.title}")
        
        # 4a. Create backup sheet of Pool
        worksheets = [w.title for w in pool_sh.worksheets()]
        if "Backup_Pool_Old_TK" not in worksheets:
            pool_sheet = pool_sh.worksheet("Pool")
            pool_sh.duplicate_sheet(source_sheet_id=pool_sheet.id, new_sheet_name="Backup_Pool_Old_TK")
            print("  Created backup worksheet tab 'Backup_Pool_Old_TK'.")
        else:
            print("  Backup tab 'Backup_Pool_Old_TK' already exists. Skipping backup sheet creation.")
            
        # 4b. Clean live Pool worksheet
        pool_sheet = pool_sh.worksheet("Pool")
        pool_data = pool_sheet.get_all_values()
        print(f"  Current Pool sheet rows: {len(pool_data)}")
        
        pool_headers = pool_data[0]
        # Find Link Gốc column index
        link_goc_idx = -1
        for idx, h in enumerate(pool_headers):
            if "link" in h.lower():
                link_goc_idx = idx
                break
                
        filtered_pool_rows = [pool_headers]
        deleted_pool_count = 0
        
        for r_idx, row in enumerate(pool_data[1:], start=2):
            if not row or len(row) == 0:
                continue
            ma_hang = row[0].strip()
            link_goc = row[link_goc_idx].strip() if (link_goc_idx != -1 and len(row) > link_goc_idx) else ""
            
            is_old = ma_hang.startswith("TK-") or "data.thienkhoi.com" in link_goc
            if is_old:
                deleted_pool_count += 1
            else:
                filtered_pool_rows.append(row)
                
        print(f"  Filtered: Keeping {len(filtered_pool_rows)} rows. Removing {deleted_pool_count} old rows.")
        
        # Clear and rewrite Pool - use ZZ range to handle large column counts
        pool_sheet.clear()
        pool_sheet.update(range_name=f"A1:ZZ{len(filtered_pool_rows)}", values=filtered_pool_rows, value_input_option='USER_ENTERED')
        print("  Google Sheet Pool cleaned successfully.")
        
    except Exception as e:
        print(f"  [❌ ERROR] Failed processing Pool Sheet: {e}")
        sys.exit(1)

    # 5. Backing up, cleaning and aligning Google Sheet Source
    print("\n[Step 5] Processing Google Sheet Source...")
    try:
        source_sh = gc.open_by_key(source_sid)
        print(f"  Opened spreadsheet: {source_sh.title}")
        
        # 5a. Create backup sheet of Source
        worksheets = [w.title for w in source_sh.worksheets()]
        if "Backup_Source_Old_TK" not in worksheets:
            source_sheet = source_sh.worksheet("Source")
            source_sh.duplicate_sheet(source_sheet_id=source_sheet.id, new_sheet_name="Backup_Source_Old_TK")
            print("  Created backup worksheet tab 'Backup_Source_Old_TK'.")
        else:
            print("  Backup tab 'Backup_Source_Old_TK' already exists. Skipping backup sheet creation.")
            
        # 5b. Clean and Align live Source worksheet
        source_sheet = source_sh.worksheet("Source")
        source_data = source_sheet.get_all_values()
        print(f"  Current Source sheet rows: {len(source_data)}")
        
        source_row1 = source_data[0] # empty/label row
        source_headers = source_data[1] # actual headers
        
        sys_id_idx = source_headers.index("System ID") if "System ID" in source_headers else 37
        ma_kn_idx = source_headers.index("id") if "id" in source_headers else 3
        
        filtered_source_rows = [source_row1, source_headers]
        deleted_source_old_count = 0
        deleted_source_inconsistent_count = 0
        aligned_count = 0
        
        for r_idx, row in enumerate(source_data[2:], start=3):
            if not row or len(row) <= sys_id_idx:
                continue
            sys_id = row[sys_id_idx].strip()
            ma_kn_source = row[ma_kn_idx].strip() if len(row) > ma_kn_idx else ""
            
            if not sys_id:
                deleted_source_inconsistent_count += 1
                continue
                
            db_info = sqlite_map.get(sys_id)
            if not db_info:
                # Inconsistent (not found in SQLite) - clean it!
                deleted_source_inconsistent_count += 1
                continue
                
            ma_hang = db_info["ma_hang"]
            link_goc = db_info["link_goc"]
            
            is_old = ma_hang.startswith("TK-") or "data.thienkhoi.com" in link_goc
            if is_old:
                deleted_source_old_count += 1
            else:
                # It is a new system listing! Let's align its Mã Khang Ngô
                correct_ma_kn = db_info["ma_kn"]
                if correct_ma_kn and ma_kn_source != correct_ma_kn:
                    row[ma_kn_idx] = correct_ma_kn
                    aligned_count += 1
                filtered_source_rows.append(row)
                
        print(f"  Filtered: Keeping {len(filtered_source_rows) - 2} rows.")
        print(f"  Removing {deleted_source_old_count} old TK rows.")
        print(f"  Removing {deleted_source_inconsistent_count} inconsistent/not-found rows.")
        print(f"  Aligned {aligned_count} Mã Khang Ngô IDs.")
        
        # Clear and rewrite Source - use ZZ range
        source_sheet.clear()
        source_sheet.update(range_name=f"A1:ZZ{len(filtered_source_rows)}", values=filtered_source_rows, value_input_option='USER_ENTERED')
        print("  Google Sheet Source cleaned and aligned successfully.")
        
    except Exception as e:
        print(f"  [❌ ERROR] Failed processing Source Sheet: {e}")
        sys.exit(1)

    # 6. Cleaning SQLite Database
    print("\n[Step 6] Cleaning SQLite databases...")
    try:
        # 6a. Clean primary database
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        
        c.execute("DELETE FROM listings WHERE Ma_Hang LIKE 'TK-%' OR Link_Goc LIKE '%data.thienkhoi.com%'")
        deleted_db_count = c.rowcount
        conn.commit()
        
        # Run VACUUM to reduce file size
        c.execute("VACUUM")
        conn.close()
        print(f"  Deleted {deleted_db_count} old rows from raw_archive.db and vacuumed.")
        
        # 6b. Clean temp database if it exists
        if os.path.exists(temp_db_file):
            conn_temp = sqlite3.connect(temp_db_file)
            c_temp = conn_temp.cursor()
            c_temp.execute("DELETE FROM listings WHERE Ma_Hang LIKE 'TK-%' OR Link_Goc LIKE '%data.thienkhoi.com%'")
            deleted_temp_count = c_temp.rowcount
            conn_temp.commit()
            c_temp.execute("VACUUM")
            conn_temp.close()
            print(f"  Deleted {deleted_temp_count} old rows from raw_archive_temp_read.db and vacuumed.")
            
    except Exception as e:
        print(f"  [❌ ERROR] Failed cleaning SQLite: {e}")
        sys.exit(1)

    print("\n=== CLEAN & ALIGN OPERATION COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
