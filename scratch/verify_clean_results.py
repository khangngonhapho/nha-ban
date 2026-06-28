import sqlite3
import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_file = "raw_archive.db"
temp_db_file = "raw_archive_temp_read.db"
pool_sid = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
source_sid = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"

def main():
    print("=== STARTING VERIFICATION SYSTEM ===")
    
    # 1. Verify SQLite database
    print("\n[Step 1] Verifying SQLite databases...")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    old_tk_db_count = c.execute("SELECT COUNT(*) FROM listings WHERE Ma_Hang LIKE 'TK-%' OR Link_Goc LIKE '%data.thienkhoi.com%'").fetchone()[0]
    total_db_count = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    
    print(f"  raw_archive.db:")
    print(f"    Old TK- listings remaining: {old_tk_db_count} (Expected: 0)")
    print(f"    Total listings remaining  : {total_db_count} (Expected: 88)")
    
    # Load SQLite mapping for Source alignment checks
    sqlite_map = {}
    for r in c.execute("SELECT System_ID, Ma_Khang_Ngo_ID, Ma_Hang, Link_Goc FROM listings").fetchall():
        sys_id, ma_kn, ma_hang, link_goc = r
        if sys_id:
            sqlite_map[sys_id.strip()] = {
                "ma_kn": ma_kn.strip() if ma_kn else "",
                "ma_hang": ma_hang.strip() if ma_hang else "",
                "link_goc": link_goc.strip() if link_goc else ""
            }
    conn.close()
    
    if old_tk_db_count != 0 or total_db_count != 88:
        print("    [❌ FAIL] raw_archive.db verification failed!")
    else:
        print("    [✅ PASS] raw_archive.db verified successfully.")
        
    # Verify temp database
    conn_temp = sqlite3.connect(temp_db_file)
    c_temp = conn_temp.cursor()
    old_tk_temp_count = c_temp.execute("SELECT COUNT(*) FROM listings WHERE Ma_Hang LIKE 'TK-%' OR Link_Goc LIKE '%data.thienkhoi.com%'").fetchone()[0]
    total_temp_count = c_temp.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    conn_temp.close()
    
    print(f"  raw_archive_temp_read.db:")
    print(f"    Old TK- listings remaining: {old_tk_temp_count} (Expected: 0)")
    print(f"    Total listings remaining  : {total_temp_count} (Expected: 88)")
    
    if old_tk_temp_count != 0 or total_temp_count != 88:
        print("    [❌ FAIL] raw_archive_temp_read.db verification failed!")
    else:
        print("    [✅ PASS] raw_archive_temp_read.db verified successfully.")

    # 2. Connect to Google Sheets
    print("\n[Step 2] Fetching Google Sheets data...")
    try:
        gc = gspread.service_account(filename='credentials.json')
    except Exception as e:
        print(f"  [❌ ERROR] Google Sheets authentication failed: {e}")
        sys.exit(1)

    # 3. Verify Pool Sheet
    print("\n[Step 3] Verifying Google Sheet Pool...")
    try:
        pool_sh = gc.open_by_key(pool_sid)
        pool_sheet = pool_sh.worksheet("Pool")
        pool_data = pool_sheet.get_all_values()
        
        total_pool_rows = len(pool_data)
        pool_headers = pool_data[0]
        
        # Check Link Gốc column
        link_goc_idx = -1
        for idx, h in enumerate(pool_headers):
            if "link" in h.lower():
                link_goc_idx = idx
                break
                
        old_tk_pool_count = 0
        for row in pool_data[1:]:
            ma_hang = row[0].strip()
            link_goc = row[link_goc_idx].strip() if (link_goc_idx != -1 and len(row) > link_goc_idx) else ""
            if ma_hang.startswith("TK-") or "data.thienkhoi.com" in link_goc:
                old_tk_pool_count += 1
                
        print(f"  Pool Sheet:")
        print(f"    Old TK- listings remaining: {old_tk_pool_count} (Expected: 0)")
        print(f"    Total rows remaining      : {total_pool_rows} (Expected: 96 - includes 1 header row)")
        
        if old_tk_pool_count != 0 or total_pool_rows != 96:
            print("    [❌ FAIL] Pool sheet verification failed!")
        else:
            print("    [✅ PASS] Pool sheet verified successfully.")
            
    except Exception as e:
        print(f"  [❌ ERROR] Pool verification failed: {e}")

    # 4. Verify Source Sheet
    print("\n[Step 4] Verifying Google Sheet Source...")
    try:
        source_sh = gc.open_by_key(source_sid)
        source_sheet = source_sh.worksheet("Source")
        source_data = source_sheet.get_all_values()
        
        total_source_rows = len(source_data)
        source_headers = source_data[1]
        
        sys_id_idx = source_headers.index("System ID") if "System ID" in source_headers else 37
        ma_kn_idx = source_headers.index("id") if "id" in source_headers else 3
        
        old_tk_source_count = 0
        inconsistent_source_count = 0
        mismatched_id_count = 0
        
        for idx, row in enumerate(source_data[2:], start=3):
            if len(row) <= sys_id_idx:
                continue
            sys_id = row[sys_id_idx].strip()
            ma_kn_source = row[ma_kn_idx].strip() if len(row) > ma_kn_idx else ""
            
            if not sys_id:
                inconsistent_source_count += 1
                continue
                
            db_info = sqlite_map.get(sys_id)
            if not db_info:
                inconsistent_source_count += 1
                continue
                
            ma_hang = db_info["ma_hang"]
            link_goc = db_info["link_goc"]
            ma_kn_sqlite = db_info["ma_kn"]
            
            # Check old listing
            if ma_hang.startswith("TK-") or "data.thienkhoi.com" in link_goc:
                old_tk_source_count += 1
                
            # Check alignment mismatch
            if ma_kn_source != ma_kn_sqlite:
                mismatched_id_count += 1
                print(f"      Mismatch row {idx}: Sys_ID={sys_id} | Source ID={ma_kn_source} vs SQLite ID={ma_kn_sqlite}")
                
        print(f"  Source Sheet:")
        print(f"    Old TK- listings remaining  : {old_tk_source_count} (Expected: 0)")
        print(f"    Inconsistent/not-found rows : {inconsistent_source_count} (Expected: 0)")
        print(f"    Mismatched ID rows          : {mismatched_id_count} (Expected: 0)")
        print(f"    Total rows remaining        : {total_source_rows} (Expected: 61 - includes 2 header rows)")
        
        if old_tk_source_count != 0 or inconsistent_source_count != 0 or mismatched_id_count != 0 or total_source_rows != 61:
            print("    [❌ FAIL] Source sheet verification failed!")
        else:
            print("    [✅ PASS] Source sheet verified successfully.")
            
    except Exception as e:
        print(f"  [❌ ERROR] Source verification failed: {e}")

    print("\n=== VERIFICATION SYSTEM COMPLETED ===")

if __name__ == "__main__":
    main()
