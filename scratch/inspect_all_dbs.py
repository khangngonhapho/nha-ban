import sqlite3
import os

dbs = [
    ".\\raw_archive.db",
    ".\\scratch\\raw_archive_pre_merge.db",
    ".\\scratch\\raw_archive_stash.db",
    ".\\Backup DB\\raw_archive.db"
]

for db in dbs:
    if os.path.exists(db):
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            total = cursor.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
            print(f"Database: {db}")
            print(f"  Total records: {total}")
            
            # Print count by status
            cursor.execute("SELECT status, COUNT(*) FROM listings GROUP BY status")
            rows = cursor.fetchall()
            for r in rows:
                print(f"    - {r[0]}: {r[1]}")
            conn.close()
        except Exception as e:
            print(f"Error querying {db}: {e}")
    else:
        print(f"Database {db} does not exist!")
