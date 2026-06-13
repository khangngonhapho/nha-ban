import sqlite3
import os

dbs = [
    "D:/LHTBrain/01_PROJECTS/raw_archive.db",
    "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db",
    "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive_v2.db"
]

for db in dbs:
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in c.fetchall()]
        print(f"DB: {db}")
        print(f"  Tables: {tables}")
        for t in tables:
            try:
                count = c.execute(f"SELECT COUNT(*) FROM `{t}`").fetchone()[0]
                print(f"    Table `{t}` count: {count}")
            except Exception as e:
                print(f"    Table `{t}` error: {e}")
        conn.close()
    else:
        print(f"DB: {db} does not exist!")
    print()
