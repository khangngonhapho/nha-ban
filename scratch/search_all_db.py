import sqlite3

db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive_v2.db"
conn = sqlite3.connect(db_file)
c = conn.cursor()

tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables in raw_archive_v2.db:", tables)

found = False
for t in tables:
    cols = [col[1] for col in c.execute(f"PRAGMA table_info({t})").fetchall()]
    for col in cols:
        try:
            count = c.execute(f"SELECT COUNT(*) FROM `{t}` WHERE CAST(`{col}` AS TEXT) LIKE '%AWOIZTIDQT%'").fetchone()[0]
            if count > 0:
                print(f"Match found in Table: {t}, Column: {col}, Count: {count}")
                found = True
        except Exception as e:
            pass

if not found:
    print("No matches found for AWOIZTIDQT in raw_archive_v2.db.")

found = False
for t in tables:
    cols = [col[1] for col in c.execute(f"PRAGMA table_info({t})").fetchall()]
    for col in cols:
        try:
            count = c.execute(f"SELECT COUNT(*) FROM `{t}` WHERE CAST(`{col}` AS TEXT) LIKE '%mje3mfrc%'").fetchone()[0]
            if count > 0:
                print(f"Match found in Table: {t}, Column: {col}, Count: {count}")
                rows = c.execute(f"SELECT * FROM `{t}` WHERE CAST(`{col}` AS TEXT) LIKE '%mje3mfrc%'").fetchall()
                for r in rows:
                    print(r)
                found = True
        except Exception as e:
            pass

if not found:
    print("No matches found for mje3mfrc in the database.")
    
conn.close()
