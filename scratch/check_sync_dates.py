import sys
import sqlite3
from collections import Counter

# Force UTF-8 encoding for stdout
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

db_file = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Đếm tổng số căn published
total_published = cursor.execute("SELECT COUNT(*) FROM listings WHERE status = 'published'").fetchone()[0]
print(f"Tổng số căn published: {total_published}")

# Thống kê Last_Sync
sync_dates = cursor.execute("SELECT Last_Sync FROM listings WHERE status = 'published'").fetchall()
dates = [r[0] for r in sync_dates if r[0]]
print(f"Số lượng căn có Last_Sync: {len(dates)}")

# Thống kê top các ngày Last_Sync
counter = Counter()
for d in dates:
    # Lấy phần ngày (thường có dạng dd/mm/yyyy hoặc yyyy-mm-dd)
    if ' ' in d:
        date_part = d.split(' ')[0]
    else:
        date_part = d
    counter[date_part] += 1

print("\nTop các ngày Last_Sync:")
for k, v in counter.most_common(15):
    print(f"- {k}: {v} căn")

conn.close()
