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

c.execute(f"SELECT id, tk_id, Duyet_Public, {', '.join(active_cols)} FROM listings WHERE id <= 50")
rows = c.fetchall()

print("Status of first 50 listings:")
for r in rows:
    lid = r[0]
    tk_id = r[1]
    duyet = r[2]
    img_vals = [str(x) for x in r[3:] if x]
    
    cld_count = sum(1 for val in img_vals if 'cloudinary.com' in val)
    r2_count = sum(1 for val in img_vals if 'r2.dev' in val)
    other_count = len(img_vals) - cld_count - r2_count
    
    print(f"id={lid:2d} | tk_id={tk_id} | Duyet={duyet:5s} | Images: total={len(img_vals)}, Cloudinary={cld_count}, R2={r2_count}, Other={other_count}")

conn.close()
