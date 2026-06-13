import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import DB_FILE

def check_db():
    print(f"Connecting to SQLite database: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(listings)")
    cols = [col[1] for col in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM listings")
    all_rows = cursor.fetchall()
    
    target_ids = {'HWOISCIBZIBC', 'MWOBIHTILHT', 'BBIHBIKV'}
    
    print("\n--- SQLITE RESULTS FOR THE 3 MERGED PROPERTIES ---")
    for r in all_rows:
        ma_kn = ""
        # Find column indices for Ma_Khang_Ngo_ID, Duong, Ngo_So_nha, status, System_ID
        ma_kn_idx = cols.index("Ma_Khang_Ngo_ID")
        duong_idx = cols.index("Duong")
        ngo_idx = cols.index("Ngo_So_nha")
        status_idx = cols.index("status")
        sys_id_idx = cols.index("System_ID")
        ma_hang_idx = cols.index("Ma_Hang")
        
        db_ma_kn = r[ma_kn_idx]
        if db_ma_kn in target_ids:
            print(f"Match found:")
            print(f"  Mã Hàng = {r[ma_hang_idx]}")
            print(f"  Số nhà = {r[ngo_idx]}")
            print(f"  Đường = {r[duong_idx]}")
            print(f"  Mã KN = {r[ma_kn_idx]}")
            print(f"  Status = {r[status_idx]}")
            print(f"  System ID = {r[sys_id_idx]}")
            print("-" * 40)

if __name__ == "__main__":
    check_db()
