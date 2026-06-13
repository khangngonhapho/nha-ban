import json

json_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/detail_TKQLMB8Q.json"
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

detail_data = data.get("data", {})

# 1. Parse Root Fields
parsed = {
    "tk_id": detail_data.get("id"),
    "code": detail_data.get("code"),
    "isSigned": detail_data.get("isSigned"),
    "status": detail_data.get("status"),
    "commissionAgent": detail_data.get("commissionAgent"),
    "ownerSideUserId": detail_data.get("ownerSideUserId"),
    "certificateSeries": detail_data.get("certificateSeries"),
    "latitude": detail_data.get("latitude"),
    "longitude": detail_data.get("longitude"),
    "placeName": detail_data.get("placeName"),
    "streetName": detail_data.get("streetName"),
    "bedrooms": detail_data.get("bedrooms"),
    "restrooms": detail_data.get("restrooms"),
    "balconies": detail_data.get("balconies"),
    "sidewalk": detail_data.get("sidewalk"),
    "behindOpenSpace": detail_data.get("behindOpenSpace"),
    "sideOpenSpace": detail_data.get("sideOpenSpace"),
    "minimumRoadWidth": detail_data.get("minimumRoadWidth"),
    "createdAt": detail_data.get("createdAt"),
    "updatedAt": detail_data.get("updatedAt"),
    "createdBy": detail_data.get("createdBy"),
    "updatedBy": detail_data.get("updatedBy"),
    "commissionType": detail_data.get("commissionType"),
    "commissionValue": detail_data.get("commissionValue"),
    "isDispute": detail_data.get("isDispute"),
    "createdAtSigned": detail_data.get("createdAtSigned"),
    "CCCD_Dau_Chu": (detail_data.get("ownerSideUser") or {}).get("numberId"),
    "Kenh_tin_TK": ", ".join([c.get("channel", {}).get("name", "") for c in (detail_data.get("channels") or []) if c]),
    "The_tags_TK": ", ".join([t.get("name", "") for t in (detail_data.get("tags") or []) if t]),
}

# 2. Parse Criteria Fields
criteria_list = detail_data.get("criteria") or []
criteria_map = {}
for c in criteria_list:
    code = c.get("groupCode")
    name = c.get("name")
    if code and name:
        if code not in criteria_map:
            criteria_map[code] = []
        criteria_map[code].append(name)

criteria_cols = {
    "Criteria_Tiem_nang_Rui_ro": ", ".join(criteria_map.get("PROPERTY_CRITERIA", [])),
    "Criteria_Duong_truoc_nha": ", ".join(criteria_map.get("ROAD_TYPE", [])),
    "Criteria_Loai_BDS": ", ".join(criteria_map.get("PROPERTY_TYPE", [])),
    "Criteria_Giay_to_phap_ly": ", ".join(criteria_map.get("LEGAL_DOCUMENT", [])),
    "Criteria_Hinh_dang_dat": ", ".join(criteria_map.get("LAND_PLOT_SHAPE", [])),
    "Criteria_Tinh_trang_xay_dung": ", ".join(criteria_map.get("CONSTRUCTION_STATUS", [])),
    "Criteria_Cau_truc_nha": ", ".join(criteria_map.get("HOUSE_STRUCTURE", [])),
    "Criteria_Noi_that": ", ".join(criteria_map.get("INTERIOR", [])),
    "Criteria_Thang_may": ", ".join(criteria_map.get("ELEVATOR", [])),
    "Criteria_Loai_ngo": ", ".join(criteria_map.get("ALLEY_TYPE", [])),
    "Criteria_Vi_tri_tinh_thue": ", ".join(criteria_map.get("TAX_CALCULATION_POSITION", [])),
    "Criteria_Mat_thoang": ", ".join(criteria_map.get("OPEN_SPACE", [])),
    "Criteria_Khoang_cach_bai_do_xe": ", ".join(criteria_map.get("DISTANCE_TO_PARKING_LOT", [])),
    "Criteria_Kinh_doanh_Dong_tien": ", ".join(criteria_map.get("PROPERTY_CRITERIA_BUSINESS_CASH_FLOW", [])),
    "Criteria_Tien_ich": ", ".join(criteria_map.get("PROPERTY_CRITERIA_FACILITIES", [])),
    "Criteria_Phong_thuy": ", ".join(criteria_map.get("PROPERTY_CRITERIA_GEOMANCY", [])),
    "Criteria_Huong_nha": ", ".join(criteria_map.get("HOUSE_DIRECTION", [])),
    "Criteria_Vi_tri_trong_ngo": ", ".join(criteria_map.get("POSITION_IN_ALLEY", [])),
    "Criteria_Khoang_cach_duong_oto": ", ".join(criteria_map.get("DISTANCE_TO_MAIN_ROAD", [])),
}

lines = []
lines.append("=== Parsed Root Fields ===")
for k, v in parsed.items():
    lines.append(f"{k}: {v}")

lines.append("\n=== Parsed Criteria Columns ===")
for k, v in criteria_cols.items():
    lines.append(f"{k}: {v}")

out_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_parser_pool2_output.txt"
with open(out_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))

print("Done! Written to scratch/test_parser_pool2_output.txt")
