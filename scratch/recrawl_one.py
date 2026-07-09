import sys
import os
from flask import Flask

# Thiết lập project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.routes_crawl import recrawl_single_listing
import core.db as db_core

if len(sys.argv) < 2:
    print("Sử dụng: python scratch/recrawl_one.py <tk_id>")
    sys.exit(1)

tk_id = sys.argv[1]

# In thông tin database đang sử dụng
is_staging = os.environ.get("STAGING") == "true"
db_file = db_core.get_db_file()
print(f"==================================================")
print(f"🚀 BẮT ĐẦU CÀO LẠI TIN LẺ TỪ THIÊN KHÔI")
print(f"Mã căn (tk_id): {tk_id}")
print(f"Chế độ Staging: {is_staging}")
print(f"Database File: {db_file}")
print(f"==================================================")

app = Flask(__name__)
with app.test_request_context(json={}):
    res_val = recrawl_single_listing(tk_id)
    if isinstance(res_val, tuple):
        resp, status_code = res_val
    else:
        resp = res_val
        status_code = 200
    
    res_data = resp.get_json()
    if status_code == 200:
        print(f"[✅ SUCCESS] Cào thành công! Trạng thái phản hồi: {status_code}")
        print(f"Thông tin chi tiết: {res_data}")
    else:
        print(f"[❌ FAILED] Lỗi cào tin! Trạng thái phản hồi: {status_code}")
        print(f"Chi tiết lỗi: {res_data}")
