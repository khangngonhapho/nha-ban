import sqlite3
conn = sqlite3.connect('raw_archive_v2.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(listings_v2)")
cols = [r[1] for r in cursor.fetchall()]
print("listings_v2 columns in raw_archive_v2.db:")
print(cols)
conn.close()
