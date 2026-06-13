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

# Đo clock skew de patch time.time (tránh clock skew lệch 3 phút)
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

original_time = time.time
time.time = lambda: original_time() + skew

sys.path.append(os.path.abspath(os.getcwd()))
import curator_server

# Danh sách 5 UUID vừa cào
tk_ids = [
    '19c74ebc-e5a4-4cfb-844b-3ae5365e6318',
    '0a9dff09-fc47-4d64-a829-644673c1d056',
    'fc3f2de9-8af9-4551-b599-1e59672b1c71',
    '3d7eb275-27c5-4974-9a45-2020c729fde1',
    'a4fdb7cc-4c15-4735-9cfe-2d9e7d1e1b5b'
]

print(f"[🚀] Bắt đầu đẩy 5 căn vừa cào lên Google Sheets Pool...")

success_count = 0
for idx, tk_id in enumerate(tk_ids):
    print(f"\n📦 [{idx+1}/5] Đang đẩy căn {tk_id}...")
    try:
        res = curator_server.execute_publish_listing(tk_id)
        if res.get("status") == "success":
            success_count += 1
            print(f"[✅ THÀNH CÔNG] Đã đẩy thành công {tk_id}!")
        else:
            print(f"[⚠️ THẤT BẠI] Căn {tk_id} đẩy thất bại: {res.get('message')}")
    except Exception as e:
        print(f"[❌ LỖI] Lỗi hệ thống khi đẩy căn {tk_id}: {str(e)}")
    
    # Delay 2.5 giây để tránh vượt quota giới hạn của Google Sheets API
    time.sleep(2.5)

print(f"\n[🏁 HOÀN TẤT] Hoàn thành đồng bộ! Đã đẩy thành công {success_count}/5 căn lên Google Sheets Pool.")
