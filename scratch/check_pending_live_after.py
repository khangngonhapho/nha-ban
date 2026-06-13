import sqlite3

db_path = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
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

print("Checking pending Cloudinary URLs for live listings after migration:")
count = 0
for r in rows:
    tk_id = r[0]
    img_vals = [str(x) for x in r[1:] if x]
    cld_urls = [val for val in img_vals if 'cloudinary.com' in val]
    if cld_urls:
        count += 1
        print(f"- {tk_id}: has {len(cld_urls)} Cloudinary URLs.")

print(f"Total listings still on Cloudinary: {count}")
conn.close()
