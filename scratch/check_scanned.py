import sqlite3

db_path = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT id, tk_id, Duyet_Public, Anh_1 FROM listings WHERE Anh_1 LIKE '%r2.dev%' ORDER BY id")
rows = c.fetchall()

print(f"Total migrated listings in DB: {len(rows)}")
for r in rows[:15]:
    print(f"- id={r[0]} | tk_id={r[1]} | Duyet_Public={r[2]} | URL={r[3][:60]}...")
print("...")
for r in rows[-5:]:
    print(f"- id={r[0]} | tk_id={r[1]} | Duyet_Public={r[2]} | URL={r[3][:60]}...")

conn.close()
