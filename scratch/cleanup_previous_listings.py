import sys
import sqlite3
import json
import base64
import requests
import time
import hashlib

# Force UTF-8 encoding for stdout
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

db_file = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"

# Tải cấu hình Cloudinary từ curator_config.json
with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator_config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

cloud_name = cfg.get("cloudinary_cloud_name")
api_key = cfg.get("cloudinary_api_key")
api_secret = cfg.get("cloudinary_api_secret")

if not (cloud_name and api_key and api_secret):
    print("[❌] Thiếu cấu hình Cloudinary!")
    sys.exit(1)

# Danh sách 5 căn đã sửa trước đây
previous_tk_ids = [
    "e3gsy4-mhkfviud-5073d0a3",
    "f0skuo-mhbxi27n-bafd1d1d",
    "0903158349-1653646446356-7a65f55c",
    "0988651778-1653717341697-c3f10a81",
    "0707123716-1654156168473-a809429c"
]

def extract_cloudinary_public_id(url):
    if not url or "cloudinary.com" not in url:
        return None
    try:
        parts = url.split("/image/upload/")
        if len(parts) < 2:
            return None
        path = parts[1]
        path_segments = path.split("/")
        if path_segments[0].startswith("v") and path_segments[0][1:].isdigit():
            path_segments = path_segments[1:]
        public_id_with_ext = "/".join(path_segments)
        public_id = public_id_with_ext.split(".")[0]
        return public_id
    except:
        return None

def get_active_public_ids(tk_id):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    row = cursor.execute("SELECT raw_drive_images_json FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
    conn.close()
    
    if not row or not row[0]:
        return set()
    try:
        urls = json.loads(row[0])
        active_ids = set()
        for url in urls:
            pid = extract_cloudinary_public_id(url)
            if pid:
                active_ids.add(pid)
        return active_ids
    except:
        return set()

def delete_cloudinary_image(public_id):
    timestamp = int(time.time())
    params_to_sign = {
        "public_id": public_id,
        "timestamp": timestamp
    }
    
    sorted_params = sorted([f"{k}={v}" for k, v in params_to_sign.items()])
    sign_string = "&".join(sorted_params) + api_secret
    signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()
    
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/destroy"
    data = {
        "api_key": api_key,
        "timestamp": timestamp,
        "signature": signature,
        "public_id": public_id
    }
    
    try:
        r = requests.post(url, data=data, timeout=15)
        if r.status_code == 200:
            res_data = r.json()
            if res_data.get("result") == "ok":
                print(f"    [🗑️ Cloudinary] Đã xóa thành công ảnh cũ rác: {public_id}")
                return True
            else:
                print(f"    [⚠️ Cloudinary] Phản hồi xóa ảnh không thành công: {res_data}")
        else:
            print(f"    [⚠️ Cloudinary] Lỗi API ({r.status_code}): {r.text}")
    except Exception as e:
        print(f"    [❌ Cloudinary LỖI] Lỗi khi xóa {public_id}: {str(e)}")
    return False

def clean_listing_folder(tk_id):
    print(f"\n⚡ Đang dọn dẹp thư mục Cloudinary cho căn {tk_id}...")
    
    # 1. Lấy danh sách public_id hiện đang được hiển thị thẳng đứng (active)
    active_ids = get_active_public_ids(tk_id)
    print(f"  - Số ảnh đang hoạt động (upright): {len(active_ids)}")
    
    # 2. Lấy toàn bộ tài nguyên hiện có trong thư mục Cloudinary của căn này
    prefix = f"BDS-KhangNgo/{tk_id}/"
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources/image?prefix={prefix}&type=upload&max_results=100"
    
    auth_str = f"{api_key}:{api_secret}"
    auth_bytes = auth_str.encode('utf-8')
    auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
    headers = {"Authorization": f"Basic {auth_b64}"}
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"  [❌ LỖI] Không thể đọc danh sách tài nguyên trên Cloudinary: {r.text}")
            return
            
        res = r.json()
        resources = res.get("resources", [])
        print(f"  - Số ảnh thực tế trên Cloudinary: {len(resources)}")
        
        deleted_count = 0
        for res_item in resources:
            pid = res_item.get("public_id")
            if pid and pid not in active_ids:
                # Ảnh này tồn tại trên Cloudinary nhưng không nằm trong rổ hàng hoạt động chính thức -> Ảnh lỗi cũ!
                print(f"  -> Phát hiện ảnh cũ bị nghiêng (rác): {pid}")
                if delete_cloudinary_image(pid):
                    deleted_count += 1
                time.sleep(0.5)
                
        print(f"  [✅ Xong] Đã xóa {deleted_count} ảnh lỗi cũ cho căn {tk_id}!")
    except Exception as e:
        print(f"  [❌ LỖI KẾT NỐI]: {str(e)}")

def main():
    print("🚀 Bắt đầu tiến hành dọn dẹp tự động 5 căn đã sửa trước đây...")
    for tk_id in previous_tk_ids:
        clean_listing_folder(tk_id)
    print("\n🏁 Hoàn tất dọn dẹp sạch sẽ toàn bộ 5 căn cũ!")

if __name__ == "__main__":
    main()
