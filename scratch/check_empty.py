import sqlite3
import sys

# Configure stdout to use utf-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect("raw_archive.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

rows = cursor.execute("SELECT tk_id, status, `Noi_dung_chinh`, `Mo_ta_chi_tiet` FROM listings ORDER BY id DESC LIMIT 5").fetchall()

print("RAW COLUMNS IN SQLite:")
for r in rows:
    raw_content = r['Noi_dung_chinh']
    raw_desc = r['Mo_ta_chi_tiet']
    print(f"ID: {r['tk_id']} | Status: {r['status']}")
    print(f"  Raw Content Length: {len(raw_content) if raw_content else 0}")
    print(f"  Raw Content Snippet: '{str(raw_content)[:100]}...'".replace('\n', ' '))
    print(f"  Raw Desc Length: {len(raw_desc) if raw_desc else 0}")
    print(f"  Raw Desc Snippet: '{str(raw_desc)[:100]}...'".replace('\n', ' '))
    print("-" * 50)

conn.close()
