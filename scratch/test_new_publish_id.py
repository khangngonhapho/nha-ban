import sys
import os
import sqlite3
import time
import datetime
import requests
import random

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Đo clock skew de patch time.time
try:
    r = requests.get('https://www.google.com', timeout=5)
    google_date_str = r.headers.get('Date')
    if google_date_str:
        google_time = datetime.datetime.strptime(google_date_str, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=datetime.timezone.utc)
        local_time = datetime.datetime.now(datetime.timezone.utc)
        skew = (google_time - local_time).total_seconds()
    else:
        skew = 183.0
except Exception as e:
    skew = 183.0

original_time = time.time
time.time = lambda: original_time() + skew

sys.path.append(os.path.abspath(os.getcwd()))
import curator_server

# Chọn căn thứ 5: a4fdb7cc-4c15-4735-9cfe-2d9e7d1e1b5b
test_uuid = 'a4fdb7cc-4c15-4735-9cfe-2d9e7d1e1b5b'

print(f"[*] Chuan bi test chen moi tu dong gen Ma Khang Ngo cho can: {test_uuid}")

# Đổi System ID trong SQLite để hệ thống hiểu đây là một dòng mới tinh (không trùng lặp để kích hoạt chế độ Append chèn mới)
# Và đổi Mã Hàng thành một mã hoàn toàn mới (ví dụ TK-TESTNEW)
conn = sqlite3.connect("raw_archive.db")
cursor = conn.cursor()

# Tạo System ID và Mã Hàng mới tinh
new_sys_id = f"SYS-{datetime.datetime.now().strftime('%Y%M%d').upper()}-{random.randint(100, 999)}"
new_ma_hang = f"TKT-{random.randint(1000, 9999)}"
cursor.execute("UPDATE listings SET status = 'raw_complete', System_ID = ?, Ma_Hang = ?, Ma_Khang_Ngo_ID = '' WHERE tk_id = ?", (new_sys_id, new_ma_hang, test_uuid))
conn.commit()
conn.close()

print(f"[+] Da tao System ID test moi: {new_sys_id}")
print(f"[+] Da tao Ma Hang test moi: {new_ma_hang}")

# Gọi API đẩy
try:
    res = curator_server.execute_publish_listing(test_uuid)
    if res.get("status") == "success":
        print("[🎉 THÀNH CÔNG] Đã đẩy thành công lên Google Sheets!")
        
        # Đọc ngược lại SQLite xem Mã Khang Ngô đã được lưu chưa
        conn = sqlite3.connect("raw_archive.db")
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM listings WHERE tk_id = ?", (test_uuid,)).fetchone()
        conn.close()
        
        if row:
            col_ma_kn_safe = curator_server.get_safe_col_name("Mã Khang Ngô (ID)")
            print(f"   - Mã Khang Ngô vừa sinh tự động trong SQLite: {row[col_ma_kn_safe]}")
    else:
        print(f"❌ THẤT BẠI: {res.get('message')}")
except Exception as e:
    print(f"❌ LỖI: {e}")
