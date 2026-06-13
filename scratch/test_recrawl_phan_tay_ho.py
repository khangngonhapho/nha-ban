# -*- coding: utf-8 -*-
import sqlite3
import sys
import os
import json
import requests
import random
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Ensure raw_archive_v2.db is initialized
import pool_lego
pool_lego.init_db()

# Load cookie
cookie_file = 'thienkhoi_cookie.txt'
if not os.path.exists(cookie_file):
    print(f"Error: {cookie_file} not found!")
    sys.exit(1)

with open(cookie_file, 'r', encoding='utf-8') as f:
    cookie = f.read().strip()

import fetcher

print("Starting simulated proptech details retrieval for 3d296527-12f8-4796-b759-c501ca421f6b...")

access_token, _, _ = fetcher.extract_tokens(cookie)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://proptech.thienkhoi.com",
    "Referer": "https://proptech.thienkhoi.com/"
}

detail_api_url = "https://backend.thienkhoi.com/product/v1/property/3d296527-12f8-4796-b759-c501ca421f6b"
r = requests.get(detail_api_url, headers=headers, timeout=20)

if r.status_code in [401, 403]:
    print("Token expired. Attempting silent refresh...")
    refreshed_cookie = fetcher.try_refresh_tokens(cookie_file)
    if refreshed_cookie:
        cookie = refreshed_cookie
        _, access_token, _ = fetcher.extract_tokens(cookie)
        headers["Authorization"] = f"Bearer {access_token}"
        r = requests.get(detail_api_url, headers=headers, timeout=20)
    else:
        print("Error: Could not refresh token!")
        sys.exit(1)

if r.status_code != 200:
    print(f"Error: API returned status {r.status_code}")
    sys.exit(1)

detail_data = r.json().get("data") or {}
if not detail_data:
    print("Error: Empty response data!")
    sys.exit(1)

print("Parsed listing details successfully.")

# Map and crawl
ma_hang = detail_data.get("code") or '3d296527-12f8-4796-b759-c501ca421f6b'
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
loai_hop_dong = detail_data.get("contractType", "")
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

channels_list = detail_data.get("channels") or []
channels_str = ", ".join([str(c) for c in channels_list if c])
tags_list = detail_data.get("tags") or []
tags_str = ", ".join([t.get("name") if isinstance(t, dict) else str(t) for t in tags_list if t])

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
    "Ten_Dau_Chu": ten_dau_chu,
    "Điểm Facebook": link_fb,
    "Link Gốc": "https://proptech.thienkhoi.com/warehouse/sources/3d296527-12f8-4796-b759-c501ca421f6b",
    "System ID": f"SYS-{datetime.now().strftime('%Y%M%d').upper()}-{random.randint(100, 999)}",
    "Last Crawl": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    
    # English compatibility mapping
    "bedrooms": so_phong_ngu,
    "restrooms": so_nha_ve_sinh,
    "minimumRoadWidth": duong_truoc_nha,
    
    # Rich contract & technical fields from API
    "isSigned": "1" if detail_data.get("isSigned") else "0",
    "status_nguon": trang_thai,
    "commissionAgent": str(detail_data.get("commissionAgent") or ""),
    "ownerSideUserId": str(detail_data.get("ownerSideUserId") or ""),
    "certificateSeries": str(detail_data.get("certificateSeries") or ""),
    "latitude": str((detail_data.get("coordinate") or {}).get("latitude") or detail_data.get("latitude") or ""),
    "longitude": str((detail_data.get("coordinate") or {}).get("longitude") or detail_data.get("longitude") or ""),
    "placeName": str(detail_data.get("placeName") or ""),
    "streetName": str(detail_data.get("streetName") or ""),
    "balconies": str(detail_data.get("balconies") or ""),
    "sidewalk": str(detail_data.get("sidewalk") or ""),
    "behindOpenSpace": str(detail_data.get("behindOpenSpace") or ""),
    "sideOpenSpace": str(detail_data.get("sideOpenSpace") or ""),
    "createdAt": str(detail_data.get("createdAt") or ""),
    "updatedAt": str(detail_data.get("updatedAt") or ""),
    "commissionType": str(detail_data.get("commissionType") or ""),
    "commissionValue": str(detail_data.get("commissionValue") or ""),
    "isDispute": "1" if detail_data.get("isDispute") else "0",
    "createdAtSigned": str(detail_data.get("createdAtSigned") or ""),
    "CCCD_Dau_Chu": str((detail_data.get("ownerSideUser") or {}).get("numberId") or ""),
    "Kenh_tin_TK": channels_str,
    "The_tags_TK": tags_str
}

for idx, url in enumerate(sodo_images[:5]):
    crawled_data[f"Sơ đồ thửa đất {idx+1}"] = url

# Parse criteria groups and merge
criteria_list = detail_data.get("criteria") or []
criteria_cols = fetcher.parse_criteria_groups(criteria_list)
crawled_data.update(criteria_cols)

print("\nVerifying parsed Criteria:")
for ck, cv in criteria_cols.items():
    if cv:
        print(f"  - {ck}: {cv}")

# Save to db
pool_lego.save_raw_to_sqlite('3d296527-12f8-4796-b759-c501ca421f6b', crawled_data, property_images)
print("\nSuccessfully saved listing to raw_archive_v2.db!")

# Run image migration
import manager
print("\nRunning image migration thread...")
manager.run_image_migration_thread(limit=None, cookie=cookie, target_tk_id='3d296527-12f8-4796-b759-c501ca421f6b')
print("Image migration completed.")

# Query listing
conn = sqlite3.connect('raw_archive_v2.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
row = cursor.execute("SELECT * FROM listings_v2 WHERE tk_id = ?", ('3d296527-12f8-4796-b759-c501ca421f6b',)).fetchone()
d = dict(row)
conn.close()

print("\nVerifying saved database fields:")
print("  - status:", repr(d.get("status")))
print("  - raw_drive_images_json:", repr(d.get("raw_drive_images_json")))
print("  - behindOpenSpace:", repr(d.get("behindOpenSpace")))
print("  - sideOpenSpace:", repr(d.get("sideOpenSpace")))
print("  - Criteria_Mat_thoang:", repr(d.get("Criteria_Mat_thoang")))
print("  - Criteria_Tiem_nang_Rui_ro:", repr(d.get("Criteria_Tiem_nang_Rui_ro")))
print("  - Criteria_Duong_truoc_nha:", repr(d.get("Criteria_Duong_truoc_nha")))
print("  - Ten_Dau_Chu:", repr(d.get("Ten_Dau_Chu")))
