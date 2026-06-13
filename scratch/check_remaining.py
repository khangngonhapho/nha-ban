import sqlite3

db_path = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("--- CLOUDINARY REMAINING LISTINGS ---")
cld_rows = c.execute("SELECT id, Duyet_Public, Anh_1 FROM listings WHERE Anh_1 LIKE '%cloudinary.com%'").fetchall()
for r in cld_rows:
    print(f"ID: {r[0]}, Duyet_Public: {r[1]}, Anh_1: {r[2][:100]}")

print("\n--- OTHER/EMPTY REMAINING LISTINGS ---")
other_rows = c.execute("SELECT id, Duyet_Public, Anh_1 FROM listings WHERE Anh_1 NOT LIKE '%r2.dev%' AND Anh_1 NOT LIKE '%cloudinary.com%'").fetchall()
print(f"Total other/empty: {len(other_rows)}")
for r in other_rows[:20]:
    print(f"ID: {r[0]}, Duyet_Public: {r[1]}, Anh_1: {repr(r[2])[:100]}")

conn.close()
