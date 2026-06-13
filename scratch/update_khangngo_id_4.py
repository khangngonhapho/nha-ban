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

# Patch clock skew de authen Google Sheets
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

# 4 UUID cần cập nhật và dòng tương ứng trên Google Sheets
targets = [
    {"uuid": "19c74ebc-e5a4-4cfb-844b-3ae5365e6318", "row": 5730},
    {"uuid": "0a9dff09-fc47-4d64-a829-644673c1d056", "row": 5731},
    {"uuid": "fc3f2de9-8af9-4551-b599-1e59672b1c71", "row": 5732},
    {"uuid": "3d7eb275-27c5-4974-9a45-2020c729fde1", "row": 5733}
]

# Kết nối Google Sheets
creds = curator_server.get_google_credentials()
cfg = curator_server.load_config()
sheet_id = cfg.get("sheet_id")

if not creds or not sheet_id:
    print("❌ LỖI: Không kết nối được Google Sheets API")
    sys.exit(1)

import gspread
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(sheet_id)
try:
    sheet = spreadsheet.worksheet("Pool")
except Exception:
    sheet = spreadsheet.get_worksheet(0)

# Cột Mã Khang Ngô (ID) là cột thứ 56 (Cột BD)
COL_MA_KN = 56

conn = sqlite3.connect("raw_archive.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("[🚀] Bắt đầu tạo Mã Khang Ngô và cập nhật cho 4 căn còn lại...")

for item in targets:
    uuid = item["uuid"]
    row_num = item["row"]
    
    # 1. Đọc dữ liệu từ SQLite
    row_data = cursor.execute("SELECT * FROM listings WHERE tk_id = ?", (uuid,)).fetchone()
    if not row_data:
        print(f"[-] Không tìm thấy dữ liệu trong SQLite cho UUID: {uuid}")
        continue
        
    d = dict(row_data)
    so_nha = d.get("Ngo_So_nha", "") or d.get("Ng__S__nh_", "")
    duong = d.get("Duong", "") or d.get("___ng", "")
    quan = d.get("Quan", "") or d.get("Qu_n", "")
    
    # 2. Sinh Mã Khang Ngô bằng Python
    ma_kn = curator_server.gen_id_khang_ngo_python(so_nha, duong, quan)
    print(f"\n📦 Xử lý UUID {uuid}:")
    print(f"   - Số nhà: {so_nha} | Đường: {duong} | Quận: {quan}")
    print(f"   - Mã Khang Ngô sinh ra: {ma_kn}")
    
    # 3. Cập nhật SQLite cục bộ
    col_ma_kn_safe = curator_server.get_safe_col_name("Mã Khang Ngô (ID)")
    conn_write = sqlite3.connect("raw_archive.db")
    conn_write.execute(f"UPDATE listings SET `{col_ma_kn_safe}` = ? WHERE tk_id = ?", (ma_kn, uuid))
    conn_write.commit()
    conn_write.close()
    print("   [✓] Đã cập nhật vào SQLite cục bộ.")
    
    # 4. Cập nhật Google Sheets
    try:
        # Cập nhật ô cụ thể (dòng row_num, cột BD)
        sheet.update_cell(row_num, COL_MA_KN, ma_kn)
        print(f"   [✓] Đã cập nhật Google Sheets thành công tại dòng {row_num}, cột {COL_MA_KN}!")
    except Exception as e_sheet:
        print(f"   [❌ LỖI SHEETS] Không thể cập nhật Google Sheets: {e_sheet}")
        
    # Delay nhẹ tránh quota limit
    time.sleep(2)

conn.close()
print("\n[🏁 HOÀN TẤT] Đã tạo và đồng bộ xong Mã Khang Ngô cho 4 căn còn lại!")
