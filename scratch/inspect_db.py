import sqlite3
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect("raw_archive.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get column names to ensure we query correct columns
cursor.execute("PRAGMA table_info(listings)")
cols = [c[1] for c in cursor.fetchall()]

query_cols = []
for c in ["id", "tk_id", "status", "Tieu_de_Public", "Mo_ta_Public", "Phuong_cu_AI", "Phuong_cu_AI_"]:
    if c in cols:
        query_cols.append(c)

print(f"Querying columns: {query_cols}")

rows = cursor.execute(f"SELECT {', '.join(query_cols)} FROM listings ORDER BY id DESC LIMIT 20").fetchall()

print("\nRECENT LISTINGS IN SQLite:")
for r in rows:
    d_row = dict(r)
    print(f"ID: {d_row['id']} | TK_ID: {d_row['tk_id']} | Status: {d_row['status']}")
    print(f"  Tieu_de_Public: '{d_row.get('Tieu_de_Public')}'")
    print(f"  Mo_ta_Public length: {len(d_row.get('Mo_ta_Public')) if d_row.get('Mo_ta_Public') else 0}")
    print(f"  Phuong_cu_AI: '{d_row.get('Phuong_cu_AI_') or d_row.get('Phuong_cu_AI')}'")
    print("-" * 50)

conn.close()
