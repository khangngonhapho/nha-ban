import sqlite3

db_path = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT tk_id, Anh_1 FROM listings WHERE Anh_1 LIKE '%r2.dev%'")
rows = c.fetchall()

print("Migrated listings in active DB:")
for row in rows:
    print(f"- {row[0]}: URL={row[1][:80]}")
    
conn.close()
