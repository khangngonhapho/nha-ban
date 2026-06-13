import sys
import requests
import json
import base64

# Force UTF-8 encoding for stdout
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Tải credentials từ curator_config.json
with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator_config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

cloud_name = cfg.get("cloudinary_cloud_name")
api_key = cfg.get("cloudinary_api_key")
api_secret = cfg.get("cloudinary_api_secret")

# Test lấy tài nguyên trong thư mục của căn test đầu tiên: e3gsy4-mhkfviud-5073d0a3
tk_id = "e3gsy4-mhkfviud-5073d0a3"
prefix = f"BDS-KhangNgo/{tk_id}/"

url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources/image?prefix={prefix}&type=upload"

# Basic authentication
auth_str = f"{api_key}:{api_secret}"
auth_bytes = auth_str.encode('utf-8')
auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

headers = {
    "Authorization": f"Basic {auth_b64}"
}

try:
    r = requests.get(url, headers=headers, timeout=15)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        res = r.json()
        resources = res.get("resources", [])
        print(f"Tìm thấy {len(resources)} ảnh trong folder {prefix}:")
        for res_item in resources:
            print(f"- public_id: {res_item.get('public_id')}")
    else:
        print(f"Lỗi: {r.text}")
except Exception as e:
    print(f"Lỗi kết nối: {str(e)}")
