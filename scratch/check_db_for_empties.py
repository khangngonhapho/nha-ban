import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_file = "raw_archive.db"
backup_db_file = "Backup DB/raw_archive_pre_clean_tk.db"

def check_db(db_path, name):
    print(f"\n=== Checking in DB: {name} ({db_path}) ===")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    ids = ['SYS-20261929-300', 'SYS-20261929-136']

    for sys_id in ids:
        row = c.execute("SELECT Ma_Hang, System_ID, Ngo_So_nha, Duong, Ma_Khang_Ngo_ID, link_goc FROM listings WHERE System_ID = ?", (sys_id,)).fetchone()
        if row:
            print(f"Found Sys_ID '{sys_id}': Ma_Hang='{row[0]}' | Address='{row[2]} {row[3]}' | Ma_KN='{row[4]}' | Link='{row[5]}'")
        else:
            print(f"NOT found Sys_ID '{sys_id}'")
            
    conn.close()

check_db(db_file, "Current DB")
check_db(backup_db_file, "Backup DB")

# Let's search by address/road too
print("\nSearching by street 'Phạm Văn Hai' or 'Đào Duy Anh':")
res = c.execute("SELECT Ma_Hang, System_ID, Ngo_So_nha, Duong FROM listings WHERE Duong LIKE '%Phạm Văn Hai%' OR Duong LIKE '%Đào Duy Anh%'").fetchall()
for r in res:
    print(f"  -> Ma_Hang='{r[0]}' | Sys_ID='{r[1]}' | Address='{r[2]} {r[3]}'")

conn.close()
