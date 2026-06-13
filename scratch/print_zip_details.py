import zipfile
import sqlite3

zip_path = r'C:\Users\Khang Ngo\Downloads\BDS-KhangNgo_2026-06-12_16_09.zip'
z = zipfile.ZipFile(zip_path)
names = z.namelist()

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("Checking first 50 files in zip:")
found_count = 0
for name in names[:50]:
    parts = name.split('/')
    if len(parts) > 1:
        folder = parts[0]
        filename = parts[-1]
        
        # Check folder in db
        c.execute("SELECT tk_id FROM listings WHERE tk_id LIKE ? OR raw_images_tk_json LIKE ?", (f'%{folder}%', f'%{filename}%'))
        res = c.fetchall()
        if res:
            print(f"- File: {name} matches db: {res}")
            found_count += 1
        else:
            # Try to search for filename only (without extension)
            base_file = filename.split('.')[0]
            c.execute("SELECT tk_id FROM listings WHERE raw_images_tk_json LIKE ?", (f'%{base_file}%',))
            res = c.fetchall()
            if res:
                print(f"- Base file: {base_file} matches db: {res}")
                found_count += 1

print(f"\nTotal matches found out of 50: {found_count}")
conn.close()
