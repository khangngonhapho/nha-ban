import os
import sqlite3

extract_path = r'D:\LHTBrain\01_PROJECTS\BDS-KhangNgo\Temp\cloudinary_backup'
db_path = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"

conn = sqlite3.connect(db_path)
c = conn.cursor()

folders = [f for f in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, f))]
print(f"Total unique directories in zip extract: {len(folders)}")

matched_live = 0
matched_archived = 0
unmatched = 0

for folder in folders:
    # Check if folder matches a tk_id
    c.execute("SELECT Duyet_Public FROM listings WHERE tk_id = ?", (folder,))
    row = c.fetchone()
    if row:
        if row[0] == 'TRUE':
            matched_live += 1
        else:
            matched_archived += 1
    else:
        unmatched += 1

print(f"Matches in DB:")
print(f"- Live listings (Duyet_Public = 'TRUE') matched: {matched_live}")
print(f"- Archived/other listings matched: {matched_archived}")
print(f"- Unmatched folders: {unmatched}")

conn.close()
