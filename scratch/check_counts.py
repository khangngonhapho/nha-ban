import sqlite3

db_path = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

total_live = c.execute("SELECT COUNT(*) FROM listings WHERE Duyet_Public = 'TRUE'").fetchone()[0]
r2_live = c.execute("SELECT COUNT(*) FROM listings WHERE Duyet_Public = 'TRUE' AND Anh_1 LIKE '%r2.dev%'").fetchone()[0]
cld_live = c.execute("SELECT COUNT(*) FROM listings WHERE Duyet_Public = 'TRUE' AND Anh_1 LIKE '%cloudinary.com%'").fetchone()[0]

print("Database counts for Duyet_Public = TRUE:")
print(f"Total: {total_live}")
print(f"R2 (r2.dev in Anh_1): {r2_live}")
print(f"Cloudinary (cloudinary.com in Anh_1): {cld_live}")

# Print those with Cloudinary in Anh_1
c.execute("SELECT tk_id, Anh_1 FROM listings WHERE Duyet_Public = 'TRUE' AND Anh_1 LIKE '%cloudinary.com%'")
rows = c.fetchall()
print("\nListings with Cloudinary in Anh_1:")
for r in rows:
    print(f"- {r[0]}: {r[1][:80]}...")
    
conn.close()
