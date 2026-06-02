import sqlite3
import os

conn = sqlite3.connect('raw_archive.db')
cursor = conn.cursor()
cursor.execute("SELECT tk_id, Ma_Hang FROM listings WHERE Ma_Hang IS NOT NULL AND Ma_Hang != ''")
rows = cursor.fetchall()

mismatch_count = 0
for tk_id, ma_hang in rows:
    parts = tk_id.split('-')
    suffix = parts[-1].upper() if parts else ""
    # Check if ma_hang is 'TK-' + last 6 chars of suffix
    expected_6 = f"TK-{suffix[-6:]}"
    expected_8 = f"TK-{suffix}"
    if ma_hang.upper() != expected_6 and ma_hang.upper() != expected_8:
        print(f"Mismatch: tk_id={tk_id}, Ma_Hang={ma_hang}, expected_6={expected_6}")
        mismatch_count += 1

print(f"Total checked: {len(rows)}")
print(f"Total mismatches with 6-char suffix: {mismatch_count}")
conn.close()
