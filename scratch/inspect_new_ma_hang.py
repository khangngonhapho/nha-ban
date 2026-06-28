import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn1 = sqlite3.connect('raw_archive.db')
c1 = conn1.cursor()
rows1 = c1.execute("SELECT id, tk_id, Ma_Hang, Link_Goc, status FROM listings WHERE Ma_Hang NOT LIKE 'TK-%' LIMIT 10").fetchall()

print("=== raw_archive.db listings NOT starting with TK- ===")
for r in rows1:
    print(f"ID: {r[0]} | tk_id: {r[1]} | Ma_Hang: {r[2]} | Link_Goc: {r[3]} | status: {r[4]}")
print("-" * 50)
conn1.close()

conn2 = sqlite3.connect('raw_archive_v2.db')
c2 = conn2.cursor()
rows2 = c2.execute("SELECT tk_id, Ma_Hang, Link_Goc, status FROM listings_v2 LIMIT 10").fetchall()
print("=== raw_archive_v2.db listings_v2 ===")
for r in rows2:
    print(f"tk_id: {r[0]} | Ma_Hang: {r[1]} | Link_Goc: {r[2]} | status: {r[3]}")
conn2.close()
