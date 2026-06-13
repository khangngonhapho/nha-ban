import sqlite3

db_path = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get max ID of migrated archived listings
row_max = c.execute("SELECT MAX(id) FROM listings WHERE Anh_1 LIKE '%r2.dev%' AND (Duyet_Public IS NULL OR Duyet_Public != 'TRUE')").fetchone()
max_id = row_max[0] if row_max else None

# Count how many archived listings have been migrated
count_archived = c.execute("SELECT COUNT(*) FROM listings WHERE Anh_1 LIKE '%r2.dev%' AND (Duyet_Public IS NULL OR Duyet_Public != 'TRUE')").fetchone()[0]

print(f"Max ID of migrated archived listings: {max_id}")
print(f"Total migrated archived listings: {count_archived}")

# Let's count how many listings have Cloudinary URLs and ID <= max_id (if max_id exists)
if max_id:
    cld_below_max = c.execute("SELECT COUNT(*) FROM listings WHERE id <= ? AND Anh_1 LIKE '%cloudinary.com%'", (max_id,)).fetchone()[0]
    print(f"Listings below or at ID {max_id} still having Cloudinary URLs: {cld_below_max}")

conn.close()
