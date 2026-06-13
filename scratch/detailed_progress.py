import sqlite3
import os

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
if not os.path.exists(db_path):
    print("Database not found")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get image columns
c.execute("PRAGMA table_info(listings)")
cols = [col[1] for col in c.fetchall()]
image_cols = [
    "Hinh_Nhan_Dien", "So_do_thua_dat_1", "So_do_thua_dat_2", "So_do_thua_dat_3", "So_do_thua_dat_4", "So_do_thua_dat_5",
    "Hinh_Mat_Tien", "Hinh_Hem_1", "Hinh_Hem_2", "Hinh_Hem_3", "Hinh_Hem_4", "Hinh_Hem_5",
    "Hinh_Hem_6", "Hinh_Hem_7", "Hinh_Hem_8", "Hinh_Hem_9", "Hinh_Hem_10",
    "Anh_1", "Anh_2", "Anh_3", "Anh_4", "Anh_5", "Anh_6", "Anh_7", "Anh_8", "Anh_9", "Anh_10"
]
active_cols = [col for col in image_cols if col in cols]

print("=== CHECKING ALL LISTINGS ===")
total_listings = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
print(f"Total listings in DB: {total_listings}")

# Check image URL types across all listings
has_cloudinary = 0
has_r2 = 0
has_both = 0
has_neither_but_has_img = 0
no_images = 0

c.execute(f"SELECT id, Duyet_Public, {', '.join(active_cols)} FROM listings")
rows = c.fetchall()

groups = {
    'TRUE': {'total': 0, 'cloudinary': 0, 'r2': 0, 'both': 0, 'empty': 0, 'other': 0},
    'FALSE': {'total': 0, 'cloudinary': 0, 'r2': 0, 'both': 0, 'empty': 0, 'other': 0},
    'OTHER': {'total': 0, 'cloudinary': 0, 'r2': 0, 'both': 0, 'empty': 0, 'other': 0}
}

for r in rows:
    lid = r[0]
    duyet = r[1]
    if duyet == 'TRUE':
        g = 'TRUE'
    elif duyet == 'FALSE':
        g = 'FALSE'
    else:
        g = 'OTHER'
        
    groups[g]['total'] += 1
    
    img_vals = [str(x) for x in r[2:] if x]
    if not img_vals:
        groups[g]['empty'] += 1
        continue
        
    cld_found = any('cloudinary.com' in val for val in img_vals)
    r2_found = any('r2.dev' in val for val in img_vals)
    
    if cld_found and r2_found:
        groups[g]['both'] += 1
    elif cld_found:
        groups[g]['cloudinary'] += 1
    elif r2_found:
        groups[g]['r2'] += 1
    else:
        groups[g]['other'] += 1

print("\nDetailed Status by Duyet_Public Group:")
for group_name, stats in groups.items():
    print(f"\nGroup Duyet_Public = '{group_name}':")
    print(f"  Total listings: {stats['total']}")
    print(f"  Only Cloudinary URLs: {stats['cloudinary']}")
    print(f"  Only R2 URLs: {stats['r2']}")
    print(f"  Mixed (Cloudinary & R2): {stats['both']}")
    print(f"  No images (empty/null): {stats['empty']}")
    print(f"  Other image URLs (local/etc): {stats['other']}")

conn.close()
