import sqlite3
import zipfile

zip_path = r'C:\Users\Khang Ngo\Downloads\BDS-KhangNgo_2026-06-12_16_09.zip'
z = zipfile.ZipFile(zip_path)
names = z.namelist()

dbs = [
    "D:/LHTBrain/01_PROJECTS/raw_archive.db",
    "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
]

for db in dbs:
    print(f"\nChecking database: {db}")
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    # Check if listings table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings'")
    if not c.fetchone():
        print("listings table not found in this DB")
        conn.close()
        continue
        
    c.execute("PRAGMA table_info(listings)")
    cols = [col[1] for col in c.fetchall()]
    
    found = 0
    for name in names[:30]:
        parts = name.split('/')
        if len(parts) > 1:
            folder = parts[0]
            filename = parts[-1]
            base_file = filename.split('.')[0]
            
            c.execute("SELECT tk_id FROM listings WHERE tk_id LIKE ? OR raw_images_tk_json LIKE ? OR raw_images_tk_json LIKE ?", (f'%{folder}%', f'%{filename}%', f'%{base_file}%'))
            res = c.fetchall()
            if res:
                print(f"  Match: {name} -> {res[0][0]}")
                found += 1
                
    print(f"Total matches in {db}: {found} out of 30")
    conn.close()
