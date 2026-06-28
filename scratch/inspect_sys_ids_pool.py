import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('raw_archive.db')
c = conn.cursor()

# Check if there are any columns or rows containing SYS- format
sys_ids = c.execute("SELECT id, tk_id, Ma_Hang, Link_Goc, status, System_ID FROM listings WHERE System_ID LIKE 'SYS-%' LIMIT 5").fetchall()
print("=== Listings with System_ID starting with SYS- ===")
for r in sys_ids:
    print(r)
    
tk_sys_ids = c.execute("SELECT id, tk_id, Ma_Hang, Link_Goc, status, System_ID FROM listings WHERE tk_id LIKE 'SYS-%' LIMIT 5").fetchall()
print("\n=== Listings with tk_id starting with SYS- ===")
for r in tk_sys_ids:
    print(r)

# Check if there are any listings containing SYS- in any text columns
print("\nTotal listings with SYS- in System_ID:", c.execute("SELECT COUNT(*) FROM listings WHERE System_ID LIKE 'SYS-%'").fetchone()[0])
print("Total listings with SYS- in tk_id:", c.execute("SELECT COUNT(*) FROM listings WHERE tk_id LIKE 'SYS-%'").fetchone()[0])

conn.close()
