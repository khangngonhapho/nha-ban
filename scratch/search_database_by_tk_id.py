import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_file = "raw_archive.db"
backup_db_file = "Backup DB/raw_archive_pre_clean_tk.db"

uuids = {
    "a4fdb7cc-4c15-4735-9cfe-2d9e7d1e1b5b": "Row 8: TKT-4587",
    "0ceb7a3b-206b-422e-8548-5e0f1e7a3310": "Row 9: TK7UPXZI",
    "19e78de2-069a-4084-92ac-45c2a1649271": "Row 10: TK7O6RYX",
    "49a99cdb-cb05-47da-b5d5-0d8a3556b697": "Row 12: TK2L1LCP",
    "3d296527-12f8-4796-b759-c501ca421f6b": "Row 24: TKQK1W9A",
    "4f92db9e-de71-4df3-91f6-cc198e84d1d3": "Row 2: (empty Ma_Hang)"
}

def search_db_for_uuids(db_path, db_name):
    print(f"\n=== Searching by UUID in DB: {db_name} ({db_path}) ===")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    for uuid, label in uuids.items():
        row = c.execute("SELECT Ma_Hang, System_ID, Ngo_So_nha, Duong, Ma_Khang_Ngo_ID, tk_id FROM listings WHERE tk_id = ? OR link_goc LIKE ?", (uuid, f"%{uuid}%")).fetchone()
        if row:
            print(f"Found for {label} (UUID: {uuid}):")
            print(f"  -> Ma_Hang='{row[0]}' | Sys_ID='{row[1]}' | Address='{row[2]} {row[3]}' | Ma_KN='{row[4]}' | tk_id='{row[5]}'")
        else:
            print(f"NOT found for {label} (UUID: {uuid})")
            
    conn.close()

search_db_for_uuids(db_file, "Current DB")
search_db_for_uuids(backup_db_file, "Backup DB")
