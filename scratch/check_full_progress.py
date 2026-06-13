import sqlite3

db_path = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

total = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
r2_count = c.execute("SELECT COUNT(*) FROM listings WHERE Anh_1 LIKE '%r2.dev%'").fetchone()[0]
cld_count = c.execute("SELECT COUNT(*) FROM listings WHERE Anh_1 LIKE '%cloudinary.com%'").fetchone()[0]

print("=== GLOBAL DATABASE PROGRESS ===")
print(f"Total rows in DB: {total}")
print(f"Migrated to R2 (in Anh_1): {r2_count} / {total} ({(r2_count/total)*100:.2f}%)")
print(f"Remaining on Cloudinary (in Anh_1): {cld_count} / {total} ({(cld_count/total)*100:.2f}%)")

# Check counts specifically for live listings
live_total = c.execute("SELECT COUNT(*) FROM listings WHERE Duyet_Public = 'TRUE'").fetchone()[0]
live_r2 = c.execute("SELECT COUNT(*) FROM listings WHERE Duyet_Public = 'TRUE' AND Anh_1 LIKE '%r2.dev%'").fetchone()[0]
print(f"\nLive listings progress (Duyet_Public = TRUE): {live_r2} / {live_total} ({(live_r2/live_total)*100:.2f}%)")

conn.close()
