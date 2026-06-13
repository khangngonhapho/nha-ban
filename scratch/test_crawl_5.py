import sys
import os
import json
import sqlite3
import requests
import time
import random
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

sys.path.append(os.path.abspath(os.getcwd()))
import crawl_pipeline

# 1. Đọc cookie thật từ file thienkhoi_cookie.txt
cookie_file = "thienkhoi_cookie.txt"
if not os.path.exists(cookie_file):
    print("❌ LỖI: Không tìm thấy file thienkhoi_cookie.txt")
    sys.exit(1)

with open(cookie_file, "r", encoding="utf-8") as f:
    cookie_str = f.read().strip()

print("[*] Đang phân tích token từ cookie...")
access_token, refresh_token, _ = crawl_pipeline.extract_tokens(cookie_str)
print(f"[*] Access Token hiện tại: {access_token[:15]}...{access_token[-15:]}")
print(f"[*] Refresh Token hiện tại: {refresh_token[:15]}...{refresh_token[-15:]}")

# Tạo Headers và kiểm tra auth
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://proptech.thienkhoi.com",
    "Referer": "https://proptech.thienkhoi.com/"
}

test_auth_url = "https://backend.thienkhoi.com/auth/v1/users/me"
print("[*] Đang gửi yêu cầu kiểm tra auth...")
r = requests.get(test_auth_url, headers=headers)
print(f"[+] Auth check status code: {r.status_code}")

if r.status_code in [401, 403]:
    print("[*] Access token hết hạn hoặc không hợp lệ. Khởi chạy Silent Refresh...")
    refreshed_cookie = crawl_pipeline.try_refresh_tokens()
    if refreshed_cookie:
        print("[🎉 THÀNH CÔNG] Đã tự động gia hạn token và cập nhật thienkhoi_cookie.txt!")
        with open(cookie_file, "r", encoding="utf-8") as f:
            cookie_str = f.read().strip()
        access_token, _, _ = crawl_pipeline.extract_tokens(cookie_str)
        headers["Authorization"] = f"Bearer {access_token}"
    else:
        print("❌ LỖI: Không thể refresh token, vui lòng copy lại cookie mới dán vào thienkhoi_cookie.txt")
        sys.exit(1)
else:
    print("[*] Token đang hoạt động tốt!")

# 2. Lấy 5 căn đầu tiên từ API danh sách
list_url = "https://backend.thienkhoi.com/product/v1/property"
params = {"page": "1", "limit": "5", "searchBy": "address"}
print(f"\n[*] Đang gọi API lấy danh sách 5 căn: {list_url}")
r_list = requests.get(list_url, headers=headers, params=params)

if r_list.status_code != 200:
    print(f"❌ LỖI: API danh sách trả về HTTP {r_list.status_code}")
    sys.exit(1)

res_json = r_list.json()
listings = (res_json.get("data") or {}).get("data", [])
print(f"[+] Đã nhận được danh sách chứa {len(listings)} căn.")

# Khởi tạo db
crawl_pipeline.init_db()

# 3. Cào chi tiết và lưu SQLite
crawled_count = 0
for idx, item in enumerate(listings):
    uuid = item.get("id")
    code = item.get("code")
    address = item.get("address")
    
    if not uuid:
        continue
        
    print(f"\n⚡ CÀO THẬT CĂN THỨ {idx + 1}/5: Mã {code} (UUID: {uuid})")
    print(f"   Địa chỉ: {address}")
    
    detail_api_url = f"https://backend.thienkhoi.com/product/v1/property/{uuid}"
    r_detail = requests.get(detail_api_url, headers=headers, timeout=20)
    
    if r_detail.status_code != 200:
        print(f"   [❌ LỖI] Không thể cào chi tiết căn này: HTTP {r_detail.status_code}")
        continue
        
    detail_json = r_detail.json()
    detail_data = detail_json.get("data") or {}
    if not detail_data:
        print("   [❌ LỖI] API chi tiết trả về dữ liệu trống")
        continue
        
    # Bóc tách None-safety
    ma_hang = detail_data.get("code") or uuid
    tinh = (detail_data.get("district") or {}).get("provinceName", "TP Hồ Chí Minh")
    quan_name = (detail_data.get("district") or {}).get("name", "")
    phuong_name = (detail_data.get("ward") or {}).get("name", "")
    duong_name = (detail_data.get("street") or {}).get("name") if detail_data.get("street") else detail_data.get("streetName", "")
    ngo_so_nha = detail_data.get("address", "")
    
    phan_loai_names = [c.get("name") for c in (detail_data.get("criteria") or []) if c and c.get("name")]
    phan_loai = ", ".join(phan_loai_names)
    
    noi_dung_chinh = f"{ngo_so_nha} {duong_name}, {detail_data.get('area', '')}m2, {detail_data.get('floors', '')} tầng, mt {detail_data.get('wide', '')}m, sâu {detail_data.get('depth', '')}m, giá {detail_data.get('offeringPrice', '')} tỷ, Phường {phuong_name} {quan_name}"
    
    mo_ta_chi_tiet = detail_data.get("description", "")
    gia_chao = str(detail_data.get("offeringPrice", ""))
    dt_thuc_te = str(detail_data.get("actualArea", ""))
    dt_tren_so = str(detail_data.get("area", ""))
    so_tang = str(detail_data.get("floors", ""))
    mat_tien = str(detail_data.get("wide", ""))
    chieu_dai = str(detail_data.get("depth", ""))
    so_phong_ngu = str(detail_data.get("bedrooms") or "")
    so_nha_ve_sinh = str(detail_data.get("restrooms") or "")
    
    huong = detail_data.get("direction", "")
    duong_truoc_nha = str(detail_data.get("minimumRoadWidth") or "")
    trang_thai = detail_data.get("status", "")
    
    ten_chu_nha = ", ".join([o.get("name") for o in (detail_data.get("homeOwner") or []) if o and o.get("name")])
    dien_thoai_1 = detail_data.get("contactPhoneNumber", "")
    dt_dau_chu = (detail_data.get("ownerSideUser") or {}).get("phone", "")
    ten_dau_chu = (detail_data.get("ownerSideUser") or {}).get("name", "")
    link_fb = (detail_data.get("ownerSideUser") or {}).get("fbLink", "")
    
    media = detail_data.get("media", [])
    property_images = []
    sodo_images = []
    
    for m in media:
        m_type = m.get("type")
        m_url = m.get("url")
        if not m_url:
            continue
        if m_type in ["parcel_map", "certificate_image"]:
            sodo_images.append(m_url)
        elif m_type in ["property_image"]:
            property_images.append(m_url)
            
    if not property_images:
        for m in media:
            if m.get("type") == "checkin_image" and m.get("url"):
                property_images.append(m.get("url"))
                
    # Dựng link gốc
    detail_url = f"https://proptech.thienkhoi.com/warehouse/sources/{uuid}"
    
    crawled_data = {
        "Mã Hàng": ma_hang,
        "Tỉnh": tinh,
        "Quận": quan_name,
        "Phường": phuong_name,
        "Đường": duong_name,
        "Ngõ/Số nhà": ngo_so_nha,
        "Phân loại": phan_loai,
        "Nội dung chính": noi_dung_chinh,
        "Mô tả chi tiết": mo_ta_chi_tiet,
        "Giá chào": gia_chao,
        "Giá Public": gia_chao,
        "DT Thực tế": dt_thuc_te,
        "DT Trên sổ": dt_tren_so,
        "Số Tầng": so_tang,
        "Mặt Tiền": mat_tien,
        "Chieu_dai": chieu_dai,
        "Số phòng ngủ": so_phong_ngu,
        "Số nhà vệ sinh": so_nha_ve_sinh,
        "Hướng": huong,
        "Đường trước nhà (m)": duong_truoc_nha,
        "Tình trạng nhà": "Bình thường",
        "Trạng thái": trang_thai,
        "Tên Chủ Nhà": ten_chu_nha,
        "Điện thoại 1": dien_thoai_1,
        "Điện thoại Đầu Chủ": dt_dau_chu,
        "Tên Đầu Chủ (Hợp đồng)": ten_dau_chu,
        "Điểm Facebook": link_fb,
        "Link Gốc": detail_url,
        "System ID": f"SYS-{datetime.now().strftime('%Y%m%d').upper()}-{random.randint(100, 999)}",
        "Last Crawl": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    
    for s_idx, url in enumerate(sodo_images[:5]):
        crawled_data[f"Sơ đồ thửa đất {s_idx+1}"] = url
        
    # Xoá căn này nếu đã có để đảm bảo ghi mới/ghi đè sạch sẽ
    conn = sqlite3.connect("raw_archive.db")
    conn.execute("DELETE FROM listings WHERE tk_id = ?", (uuid,))
    conn.commit()
    conn.close()
    
    # Ghi vào SQLite
    crawl_pipeline.save_raw_to_sqlite(uuid, crawled_data, property_images)
    print(f"   [🎉 OK] Đã ghi SQLite thành công!")
    print(f"           - Quận/Phường: {quan_name} / {phuong_name}")
    print(f"           - Giá chào: {gia_chao} tỷ")
    print(f"           - Số lượng ảnh Swiper: {len(property_images)}")
    print(f"           - Số lượng ảnh Sơ đồ: {len(sodo_images)}")
    
    crawled_count += 1
    
    # Delay nhẹ giữa các lần cào để tránh bị chặn
    time.sleep(2)

print(f"\n[🏁 HOÀN TẤT] Đã cào thật và ghi SQLite thành công {crawled_count}/5 căn từ Proptech API!")
