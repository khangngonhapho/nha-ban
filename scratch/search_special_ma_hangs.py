import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

def search_db(db_path, name):
    print(f"\n=== Searching in DB: {name} ({db_path}) ===")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Search for TKQLMB8Q in Ma_Hang
    res = c.execute("SELECT Ma_Hang, System_ID, Ngo_So_nha, Duong, Ma_Khang_Ngo_ID, link_goc FROM listings WHERE Ma_Hang = ? OR Ma_Khang_Ngo_ID = ?", ("TKQLMB8Q", "TKQLMB8Q")).fetchall()
    if res:
        for r in res:
            print(f"Found 'TKQLMB8Q': Ma_Hang='{r[0]}' | Sys_ID='{r[1]}' | Address='{r[2]} {r[3]}' | Ma_KN='{r[4]}' | Link='{r[5]}'")
    else:
        print("NOT found 'TKQLMB8Q' by Ma_Hang or Ma_Khang_Ngo_ID.")
        
    # 2. Search for 4f92db9e-de71-4df3-91f6-cc198e84d1d3 in link_goc
    res = c.execute("SELECT Ma_Hang, System_ID, Ngo_So_nha, Duong, Ma_Khang_Ngo_ID, link_goc FROM listings WHERE link_goc LIKE '%4f92db9e-de71-4df3-91f6-cc198e84d1d3%'").fetchall()
    if res:
        for r in res:
            print(f"Found UUID '4f92db9e-de71-4df3-91f6-cc198e84d1d3' in link_goc: Ma_Hang='{r[0]}' | Sys_ID='{r[1]}' | Address='{r[2]} {r[3]}' | Ma_KN='{r[4]}' | Link='{r[5]}'")
    else:
        print("NOT found UUID '4f92db9e-de71-4df3-91f6-cc198e84d1d3' in link_goc.")
        
    # 3. Search for MHIM4IADD in Ma_Khang_Ngo_ID
    res = c.execute("SELECT Ma_Hang, System_ID, Ngo_So_nha, Duong, Ma_Khang_Ngo_ID, link_goc FROM listings WHERE Ma_Khang_Ngo_ID = ?", ("MHIM4IADD",)).fetchall()
    if res:
        for r in res:
            print(f"Found 'MHIM4IADD': Ma_Hang='{r[0]}' | Sys_ID='{r[1]}' | Address='{r[2]} {r[3]}' | Ma_KN='{r[4]}' | Link='{r[5]}'")
    else:
        print("NOT found 'MHIM4IADD' by Ma_Khang_Ngo_ID.")
        
    conn.close()

search_db("raw_archive.db", "Current DB")
search_db("Backup DB/raw_archive_pre_clean_tk.db", "Backup DB")
