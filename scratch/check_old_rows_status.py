import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('raw_archive.db')
c = conn.cursor()

# Get counts by status for listings where Ma_Hang LIKE 'TK-%'
rows = c.execute("SELECT status, COUNT(*) FROM listings WHERE Ma_Hang LIKE 'TK-%' GROUP BY status").fetchall()

print("=== Status breakdown for old TK- listings ===")
for r in rows:
    print(f"  Status: {r[0]:<30} | Count: {r[1]}")
    
# Let's check how many total listings there are and how many are new
total = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
new_tk = c.execute("SELECT COUNT(*) FROM listings WHERE Ma_Hang NOT LIKE 'TK-%'").fetchone()[0]
print(f"\nTotal listings in DB: {total}")
print(f"Old TK- listings in DB: {total - new_tk}")
print(f"New listings in DB: {new_tk}")

conn.close()
