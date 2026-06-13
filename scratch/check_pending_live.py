import sqlite3
import os

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("PRAGMA table_info(listings)")
cols = [col[1] for col in c.fetchall()]
image_cols = [
    "Hinh_Nhan_Dien", "So_do_thua_dat_1", "So_do_thua_dat_2", "So_do_thua_dat_3", "So_do_thua_dat_4", "So_do_thua_dat_5",
    "Hinh_Mat_Tien", "Hinh_Hem_1", "Hinh_Hem_2", "Hinh_Hem_3", "Hinh_Hem_4", "Hinh_Hem_5",
    "Hinh_Hem_6", "Hinh_Hem_7", "Hinh_Hem_8", "Hinh_Hem_9", "Hinh_Hem_10",
    "Anh_1", "Anh_2", "Anh_3", "Anh_4", "Anh_5", "Anh_6", "Anh_7", "Anh_8", "Anh_9", "Anh_10"
]
active_cols = [col for col in image_cols if col in cols]

c.execute(f"SELECT tk_id, {', '.join(active_cols)} FROM listings WHERE Duyet_Public = 'TRUE'")
rows = c.fetchall()

print("Listings in Duyet_Public = TRUE with Cloudinary URLs:")
count = 0
for r in rows:
    tk_id = r[0]
    img_vals = [str(x) for x in r[1:] if x]
    cld_found = any('cloudinary.com' in val for val in img_vals)
    if cld_found:
        count += 1
        cld_urls = [val for val in img_vals if 'cloudinary.com' in val]
        print(f"- {tk_id}: has {len(cld_urls)} Cloudinary URLs. First: {cld_urls[0][:80]}...")
        
print(f"Total: {count}")

conn.close()
