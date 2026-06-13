import sqlite3

dbs = [
    "D:/LHTBrain/01_PROJECTS/raw_archive.db",
    "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
]

for db in dbs:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    total = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    live = c.execute("SELECT COUNT(*) FROM listings WHERE Duyet_Public = 'TRUE'").fetchone()[0]
    
    c.execute("PRAGMA table_info(listings)")
    cols = [col[1] for col in c.fetchall()]
    r2_count = 0
    if "Anh_1" in cols:
        r2_count = c.execute("SELECT COUNT(*) FROM listings WHERE Anh_1 LIKE '%r2.dev%'").fetchone()[0]
        
    print(f"DB: {db}")
    print(f"  Total rows: {total}")
    print(f"  Live (Duyet_Public = 'TRUE') rows: {live}")
    print(f"  R2 URLs in Anh_1: {r2_count}")
    print()
    conn.close()
