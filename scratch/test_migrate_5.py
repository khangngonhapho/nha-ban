import sys
import os
import sqlite3
import time
import datetime
import requests

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# 1. Đo clock skew de patch time.time (giup bypass loi invalid_grant cua Google API)
try:
    r = requests.get('https://www.google.com', timeout=5)
    google_date_str = r.headers.get('Date')
    if google_date_str:
        google_time = datetime.datetime.strptime(google_date_str, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=datetime.timezone.utc)
        local_time = datetime.datetime.now(datetime.timezone.utc)
        skew = (google_time - local_time).total_seconds()
        print(f"[*] Clock skew do duoc: {skew} giay (Google nhanh hon Local {skew} giay)")
    else:
        skew = 183.0
except Exception as e:
    skew = 183.0

# Patch time.time
original_time = time.time
time.time = lambda: original_time() + skew

sys.path.append(os.path.abspath(os.getcwd()))
import curator_server

# 2. Đọc Cookie mới nhất
cookie = ""
if os.path.exists("thienkhoi_cookie.txt"):
    try:
        with open("thienkhoi_cookie.txt", "r", encoding="utf-8") as f:
            cookie = f.read().strip()
    except Exception as e:
        print(f"[-] Khong doc duoc thienkhoi_cookie.txt: {e}")

# 3. Tạm thời hoãn di cư các căn cũ khác (chuyển status sang raw_text_hold)
print("[*] Dang tam hoan cac can cu de uu tien di cu 5 can moi...")
db_file = "raw_archive.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 5 UUID moi
target_ids = (
    '19c74ebc-e5a4-4cfb-844b-3ae5365e6318',
    '0a9dff09-fc47-4d64-a829-644673c1d056',
    'fc3f2de9-8af9-4551-b599-1e59672b1c71',
    '3d7eb275-27c5-4974-9a45-2020c729fde1',
    'a4fdb7cc-4c15-4735-9cfe-2d9e7d1e1b5b'
)

# Chuyển status các căn raw_text khác sang raw_text_hold
placeholders = ', '.join('?' for _ in target_ids)
query_hold = f"UPDATE listings SET status = 'raw_text_hold' WHERE status = 'raw_text' AND tk_id NOT IN ({placeholders})"
cursor.execute(query_hold, target_ids)
conn.commit()

# Đếm xem có bao nhiêu căn raw_text còn lại (phải là 5 căn mục tiêu)
raw_text_count = cursor.execute("SELECT COUNT(*) FROM listings WHERE status = 'raw_text'").fetchone()[0]
print(f"[+] So can muc tieu dang cho di cu: {raw_text_count} can (Ky vong: 5)")
conn.close()

# 4. Chạy di cư ảnh cho 5 căn mục tiêu
try:
    print("\n[🚀] Bat dau di cu hinh anh cho 5 can muc tieu...")
    curator_server.run_image_migration_thread(limit=5, cookie=cookie)
finally:
    # 5. Khôi phục lại trạng thái raw_text cho các căn cũ
    print("\n[*] Dang khoi phuc trang thai cho cac can cu...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("UPDATE listings SET status = 'raw_text' WHERE status = 'raw_text_hold'")
    conn.commit()
    
    # Kiểm tra xem có đúng 5 căn đã được chuyển sang raw_complete (hoặc published nếu Sheets thành công)
    target_placeholders = ', '.join('?' for _ in target_ids)
    rows = cursor.execute(f"SELECT tk_id, status FROM listings WHERE tk_id IN ({target_placeholders})", target_ids).fetchall()
    print("\n📊 Ket qua trang thai 5 can muc tieu sau di cu:")
    for r in rows:
        print(f"  - UUID: {r[0]} | Status: {r[1]}")
        
    conn.close()
    print("[🏁 HOAN TAT] Da khoi phuc va dong bo database!")
