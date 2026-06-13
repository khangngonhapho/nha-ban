import sqlite3

dbs = [
    "D:/LHTBrain/01_PROJECTS/raw_archive.db",
    "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
]

for db in dbs:
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), Duyet_Public FROM listings WHERE tk_id = '0845116146-1676363762621-7b6cad79'")
    row = c.fetchone()
    print(f"DB: {db} | Count: {row[0]} | Duyet_Public: {row[1]}")
    conn.close()
