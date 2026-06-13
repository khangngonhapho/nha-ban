# -*- coding: utf-8 -*-
import sqlite3
import sys
import os
import json
from unittest.mock import MagicMock, patch

sys.stdout.reconfigure(encoding='utf-8')

# Import modules
import pool_lego
import fetcher
import manager

# Initialize new database
db_file = 'raw_archive_v2.db'
if os.path.exists(db_file):
    os.remove(db_file)
pool_lego.init_db()

# Mock Proptech API response detail JSON based on detail_TKQLMB8Q.json but with Phan Tay Ho values
mock_detail_data = {
    "id": "3d296527-12f8-4796-b759-c501ca421f6b",
    "isSigned": True,
    "status": "unqualified",
    "commissionAgent": None,
    "ownerSideUserId": "9e89281f-0b50-4fce-abed-2c1b1f46cfc4",
    "certificateSeries": "DG805418",
    "address": "28",
    "latitude": 10.80275847637279,
    "longitude": 106.6863344237208,
    "placeName": "7a Phan Tây Hồ, Phường 7, Phú Nhuận, Thành phố Hồ Chí Minh, Việt Nam",
    "street": {"id": 1234, "name": "Phan Tây Hồ"},
    "streetName": "Phan Tây Hồ",
    "area": 54,
    "actualArea": 54,
    "floors": 5,
    "wide": 5.5,
    "depth": 11,
    "bedrooms": 5,
    "restrooms": 5,
    "balconies": 4,
    "sidewalk": 4,
    "behindOpenSpace": 5,
    "sideOpenSpace": 5,
    "minimumRoadWidth": 6,
    "offeringPrice": 13.5,
    "description": "MÔ TẢ PHAN TÂY HỒ",
    "createdAt": "2026-01-15T14:37:05.008Z",
    "updatedAt": "2026-01-18T14:38:00.289Z",
    "criteria": [
        {
            "id": 17,
            "name": "Chính chủ",
            "groupCode": "PROPERTY_CRITERIA",
            "groupName": "Tiềm năng - Rủi ro"
        },
        {
            "id": 36,
            "name": "Ngõ 2 ô tô tránh (5 - 7m)",
            "groupCode": "ROAD_TYPE",
            "groupName": "Đường trước nhà"
        },
        {
            "id": 88,
            "name": "Lô góc 2 mặt thoáng",
            "groupCode": "OPEN_SPACE",
            "groupName": "Mặt thoáng"
        },
        {
            "id": 111,
            "name": "Dưới 100m",
            "groupCode": "DISTANCE_TO_PARKING_LOT",
            "groupName": "Khoảng cách ra bãi đỗ xe oto"
        }
    ],
    "district": {
        "id": 45,
        "name": "Phú Nhuận",
        "provinceId": 2,
        "provinceName": "TP Hồ Chí Minh"
    },
    "ward": {
        "id": 215,
        "name": "Cầu Kiệu"
    },
    "channels": [
        {"channel": {"name": "Thiên Khôi"}}
    ],
    "tags": [
        {"name": "Hiếm", "type": "property_tag"},
        {"name": "Giấy phép xây dựng", "type": "property_tag"}
    ],
    "ownerSideUser": {
        "name": "Diệp Duy Thắng",
        "numberId": "062092000016",
        "fbLink": "https://www.facebook.com/mr.thang.0904",
        "phone": "0907673831"
    },
    "homeOwner": [
        {"name": "nguyễn trường giang", "id": 45479, "index": 0}
    ],
    "media": [
        {"type": "parcel_map", "url": "http://sodo1"},
        {"type": "property_image", "url": "http://img1"}
    ]
}

# 1. Test fetcher's parsing and save logic
print("[*] Simulating crawl and save...")
crawled_count = 0

# Mock details data
crawled_data = {
    "Mã Hàng": "TKQK1W9A",
    "Tỉnh": "TP Hồ Chí Minh",
    "Quận": "Phú Nhuận",
    "Phường": "Cầu Kiệu",
    "Đường": "Phan Tây Hồ",
    "Ngõ/Số nhà": "28",
    "Phân loại": "Hiếm, Giấy phép xây dựng",
    "Nội dung chính": "Nội dung chính Phan Tây Hồ",
    "Mô tả chi tiết": "Mô tả Phan Tây Hồ",
    "Giá chào": "13.5",
    "Giá Public": "13.5",
    "DT Thực tế": "54",
    "DT Trên sổ": "54",
    "Số Tầng": "5",
    "Mặt Tiền": "5.5",
    "Chieu_dai": "11",
    "Số phòng ngủ": "5",
    "Số nhà vệ sinh": "5",
    "Hướng": "",
    "Đường trước nhà (m)": "6",
    "Tình trạng nhà": "Bình thường",
    "Trạng thái": "unqualified",
    "Tên Chủ Nhà": "nguyễn trường giang",
    "Điện thoại 1": "0123456789",
    "Điện thoại Đầu Chủ": "0907673831",
    "Tên Đầu Chủ (Hợp đồng)": "Diệp Duy Thắng",
    "Ten_Dau_Chu": "Diệp Duy Thắng",
    "Điểm Facebook": "https://www.facebook.com/mr.thang.0904",
    "Link Gốc": "https://proptech.thienkhoi.com/warehouse/sources/3d296527-12f8-4796-b759-c501ca421f6b",
    "System ID": "SYS-123",
    "Last Crawl": "11/06/2026 23:30:51",
    "bedrooms": "5",
    "restrooms": "5",
    "minimumRoadWidth": "6",
    "isSigned": "1",
    "status_nguon": "unqualified",
    "commissionAgent": "",
    "ownerSideUserId": "9e89281f-0b50-4fce-abed-2c1b1f46cfc4",
    "certificateSeries": "DG805418",
    "latitude": "10.80275847637279",
    "longitude": "106.6863344237208",
    "placeName": "7a Phan Tây Hồ...",
    "streetName": "Phan Tây Hồ",
    "balconies": "4",
    "sidewalk": "4",
    "behindOpenSpace": "5",
    "sideOpenSpace": "5",
    "createdAt": "2026-01-15T14:37:05.008Z",
    "updatedAt": "2026-01-18T14:38:00.289Z",
    "commissionType": "percentage",
    "commissionValue": "3",
    "isDispute": "0",
    "createdAtSigned": "2026-01-15T14:37:05.008Z",
    "CCCD_Dau_Chu": "062092000016",
    "Kenh_tin_TK": "Thiên Khôi",
    "The_tags_TK": "Hiếm"
}

# Parse criteria
criteria_cols = fetcher.parse_criteria_groups(mock_detail_data["criteria"])
crawled_data.update(criteria_cols)

pool_lego.save_raw_to_sqlite('3d296527-12f8-4796-b759-c501ca421f6b', crawled_data, ["http://img1"])

# 2. Verify listings_v2 table does NOT contain custom columns
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(listings_v2)")
cols = [r[1] for r in cursor.fetchall()]

custom_cols_list = ["Tieu_de_Public", "Mo_ta_Public", "Gia_Public", "Anh_Public_VD_1_3_5", "Anh_Hem_Public_VD_1_2", "Danh_gia_Admin", "Ngu_tret_Admin", "CHDV_Admin", "Duyet_Public", "Trang_thai_Public"]
for cc in custom_cols_list:
    assert cc not in cols, f"Error: Custom column {cc} should not be in listings_v2!"
print("[✅] listings_v2 table does not contain any custom/admin columns.")

# Verify saved criteria values in listings_v2
row = cursor.execute("SELECT * FROM listings_v2 WHERE tk_id = '3d296527-12f8-4796-b759-c501ca421f6b'").fetchone()
assert row is not None
d_row = dict(zip(cols, row))
assert d_row["Criteria_Tiem_nang_Rui_ro"] == "Chính chủ", "Error in Criteria_Tiem_nang_Rui_ro"
assert d_row["Criteria_Mat_thoang"] == "Lô góc 2 mặt thoáng", "Error in Criteria_Mat_thoang"
assert d_row["behindOpenSpace"] == "5", "Error in behindOpenSpace"
assert d_row["sideOpenSpace"] == "5", "Error in sideOpenSpace"
assert d_row["Ten_Dau_Chu"] == "Diệp Duy Thắng", "Error in Ten_Dau_Chu"
print("[✅] Crawled attributes and criteria values saved correctly in listings_v2.")

# 3. Simulate edit and save custom overrides to listings_custom_v2
print("[*] Simulating admin edit / save overrides...")
cursor.execute("""
    INSERT INTO listings_custom_v2 (System_ID, Ma_Khang_Ngo, Tieu_De_Public, Gia_Public, Mo_ta_Public)
    VALUES (?, ?, ?, ?, ?)
""", (d_row["System_ID"], "KHANGNGO-001", "Biệt thự Phan Tây Hồ VIP", "13.2", "Mô tả viết lại..."))
conn.commit()

# 4. Test normalize_listing_for_client with LEFT JOIN query simulation
print("[*] Simulating client GET detail query with LEFT JOIN...")
conn = sqlite3.connect(db_file)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
sql = """
    SELECT listings_v2.*, 
           listings_custom_v2.Ma_Khang_Ngo AS custom_Ma_Khang_Ngo, 
           listings_custom_v2.Gia_Public AS custom_Gia_Public, 
           listings_custom_v2.Tieu_De_Public AS custom_Tieu_De_Public, 
           listings_custom_v2.Mo_ta_Public AS custom_Mo_ta_Public, 
           listings_custom_v2.Note_Noi_Bo AS custom_Note_Noi_Bo, 
           listings_custom_v2.Trang_Thai_Giao_Dich AS custom_Trang_Thai_Giao_Dich, 
           listings_custom_v2.Ngu_Tret AS custom_Ngu_Tret, 
           listings_custom_v2.CHDV AS custom_CHDV, 
           listings_custom_v2.Trang_Thai_KN AS custom_Trang_Thai_KN, 
           listings_custom_v2.images_metadata_json AS custom_images_metadata_json, 
           listings_custom_v2.Dia_Chi_That AS custom_Dia_Chi_That, 
           listings_custom_v2.So_Nha AS custom_So_Nha, 
           listings_custom_v2.Ten_Duong AS custom_Ten_Duong,
           listings_custom_v2.bedrooms AS custom_bedrooms,
           listings_custom_v2.restrooms AS custom_restrooms,
           listings_custom_v2.minimumRoadWidth AS custom_minimumRoadWidth,
           listings_custom_v2.Noi_dung_chinh AS custom_Noi_dung_chinh,
           listings_custom_v2.Mo_ta_chi_tiet AS custom_Mo_ta_chi_tiet,
           listings_custom_v2.Gia_chao AS custom_Gia_chao,
           listings_custom_v2.DT_Thuc_te AS custom_DT_Thuc_te,
           listings_custom_v2.DT_Tren_so AS custom_DT_Tren_so,
           listings_custom_v2.So_Tang AS custom_So_Tang,
           listings_custom_v2.Mat_Tien AS custom_Mat_Tien,
           listings_custom_v2.Chieu_dai AS custom_Chieu_dai,
           listings_custom_v2.Huong AS custom_Huong,
           listings_custom_v2.Criteria_Duong_truoc_nha AS custom_Criteria_Duong_truoc_nha,
           listings_custom_v2.Criteria_Noi_that AS custom_Criteria_Noi_that,
           listings_custom_v2.Criteria_Thang_may AS custom_Criteria_Thang_may,
           listings_custom_v2.Criteria_Loai_ngo AS custom_Criteria_Loai_ngo,
           listings_custom_v2.Criteria_Khoang_cach_bai_do_xe AS custom_Criteria_Khoang_cach_bai_do_xe,
           listings_custom_v2.Criteria_Kinh_doanh_Dong_tien AS custom_Criteria_Kinh_doanh_Dong_tien,
           listings_custom_v2.Criteria_Huong_nha AS custom_Criteria_Huong_nha,
           listings_custom_v2.Criteria_Khoang_cach_duong_oto AS custom_Criteria_Khoang_cach_duong_oto
    FROM listings_v2 
    LEFT JOIN listings_custom_v2 ON listings_v2.System_ID = listings_custom_v2.System_ID
    WHERE listings_v2.tk_id = '3d296527-12f8-4796-b759-c501ca421f6b'
"""
joined_row = cursor.execute(sql).fetchone()
conn.close()

assert joined_row is not None
# Normalize for client
client_listing = manager.normalize_listing_for_client(joined_row)

print("\nVerifying normalized client listing metadata:")
print("  - Ma_Khang_Ngo_ID:", repr(client_listing.get("Ma_Khang_Ngo_ID")))
print("  - Tieu_de_Public:", repr(client_listing.get("Tieu_de_Public")))
print("  - Gia_Public:", repr(client_listing.get("Gia_Public")))
print("  - Mo_ta_Public:", repr(client_listing.get("Mo_ta_Public")))

assert client_listing["Ma_Khang_Ngo_ID"] == "KHANGNGO-001"
assert client_listing["Tieu_de_Public"] == "Biệt thự Phan Tây Hồ VIP"
assert client_listing["Gia_Public"] == "13.2"
assert client_listing["Mo_ta_Public"] == "Mô tả viết lại..."

print("[✅] Custom overrides merged into client listing dictionary successfully.")
print("[🎉 SUCCESS] Mock crawl and join override test passed perfectly!")
