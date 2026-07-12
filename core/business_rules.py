"""
Core Business Rules — BDS KhangNgo.

Tập trung toàn bộ logic nghiệp vụ thuần túy (pure functions, không I/O).
Được tách từ pool_lego.py và query_helper.py trong MOD-01.

BUSINESS RULES:
  - docs/transformation_roadmap.md (MOD-01)
  - docs/sustainable_development_strategy.md

RELATED FILES:
  - pool_lego.py       → File gốc (sẽ import từ module này sau WIRE)
  - query_helper.py    → Chứa duplicate remove_accents (sẽ import từ đây)
  - manager.py         → Consumer của gen_id_khang_ngo_python

TESTS: tests/test_business_rules.py

OWNER: MOD-01 (Architecture Modernization)
"""

import re
from typing import Optional


# =============================================================================
# 1. VIETNAMESE TEXT PROCESSING
# =============================================================================

def remove_accents(input_str: Optional[str]) -> str:
    """
    Khử toàn bộ dấu tiếng Việt từ chuỗi đầu vào.

    Sử dụng bảng ánh xạ 134 ký tự có dấu → không dấu,
    bao gồm cả đ/Đ → d/D.

    Args:
        input_str: Chuỗi tiếng Việt cần khử dấu.

    Returns:
        Chuỗi không dấu tương ứng. Trả về "" nếu rỗng hoặc None.

    Examples:
        >>> remove_accents("Cách Mạng Tháng Tám")
        'Cach Mang Thang Tam'
        >>> remove_accents("Đường số 7")
        'Duong so 7'
        >>> remove_accents(None)
        ''
    """
    if not input_str:
        return ""
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỊịỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
    s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
    res = []
    for c in input_str:
        idx = s1.find(c)
        if idx != -1:
            res.append(s0[idx])
        else:
            res.append(c)
    return "".join(res)


def get_safe_col_name(header: Optional[str]) -> str:
    """
    Chuyển đổi nhãn cột tiếng Việt có dấu thành tên cột SQLite hợp lệ.

    Pipeline: khử dấu → thay ký tự đặc biệt bằng _ → gom __ → strip _.

    Args:
        header: Nhãn tiêu đề tiếng Việt (ví dụ: "Số Nhà").

    Returns:
        Tên cột SQLite an toàn dạng snake_case (ví dụ: "So_Nha").
        Trả về "" nếu rỗng hoặc None.

    Examples:
        >>> get_safe_col_name("Số Nhà")
        'So_Nha'
        >>> get_safe_col_name("Giá (tỷ đồng)")
        'Gia__ty_dong_'  # special chars → _
    """
    if not header:
        return ""
    no_accent = remove_accents(header)
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', no_accent)
    cleaned = re.sub(r'_+', '_', cleaned)
    cleaned = cleaned.strip('_')
    return cleaned


# =============================================================================
# 2. KHANGNGO ID GENERATION
# =============================================================================

# Bảng mã hóa số nhà → ký tự
_DIGIT_MAP = {
    '1': 'M', '2': 'H', '3': 'B', '4': 'A', '5': 'N',
    '6': 'S', '7': 'Z', '8': 'T', '9': 'C', '0': 'O',
    '/': 'I', '.': 'I'
}


def gen_id_khang_ngo_python(
    so_nha: Optional[str],
    duong: Optional[str],
    quan: Optional[str]
) -> str:
    """
    Tự động sinh mã ID Khang Ngô độc nhất dựa trên số nhà, tên đường, tên quận.

    Algorithm:
    1. Số nhà: strip phần sau dấu +, encode mỗi ký tự qua _DIGIT_MAP
    2. Đường: normalize tên đặc biệt (CMTT, BTH, DSx), hoặc lấy chữ cái đầu
    3. Đảo ngược tên đường viết tắt
    4. Nối: mã_số_nhà + "I" + đường_reversed
    5. Chèn "W" sau ký tự đầu tiên

    Args:
        so_nha: Số nhà thô (ví dụ: "1168.42+44").
        duong: Tên đường thô (ví dụ: "Cách Mạng Tháng Tám").
        quan: Tên quận thô (ví dụ: "Quận 3").

    Returns:
        Mã ID Khang Ngô tự sinh (ví dụ: "MWHBIT").

    Examples:
        >>> gen_id_khang_ngo_python("123", "Test", "Q1")
        'MWHBIT'
        >>> gen_id_khang_ngo_python("42+44", "Test", "Q1")  # +44 bị bỏ
        'MWHBIT'  # same as gen_id("42", ...)
    """
    so_nha = str(so_nha or "").strip()
    if '+' in so_nha:
        so_nha = so_nha.split('+')[0].strip()
    duong = str(duong or "").strip()
    quan = str(quan or "").strip()

    # Encode số nhà
    ma_so_nha = ""
    for char in so_nha:
        if char in _DIGIT_MAP:
            ma_so_nha += _DIGIT_MAP[char]
        elif re.match(r'[a-zA-Z]', char):
            ma_so_nha += char.lower()

    # Normalize tên đường đặc biệt
    normalized_duong = duong
    if re.search(r'cách mạng tháng (tám|8)|cmt8', normalized_duong, re.I):
        normalized_duong = "CMTT"
    elif re.search(r'ba tháng hai|3 tháng 2|3/2|3-2', normalized_duong, re.I):
        normalized_duong = "BTH"
    elif re.search(r'đường số (\d+)', normalized_duong, re.I):
        match = re.search(r'đường số (\d+)', normalized_duong, re.I)
        normalized_duong = "DS" + match.group(1)

    # Viết tắt tên đường
    abbr_duong = ""
    if normalized_duong in ["CMTT", "BTH"] or normalized_duong.startswith("DS"):
        abbr_duong = normalized_duong
    else:
        no_tones = remove_accents(normalized_duong)
        words = no_tones.split()
        for word in words:
            if len(word) > 0:
                abbr_duong += word[0].upper()

    # Đảo ngược + nối + chèn W
    reversed_duong = abbr_duong[::-1]
    combined = ma_so_nha + "I" + reversed_duong
    if len(combined) > 1:
        combined = combined[0] + "W" + combined[1:]
    else:
        combined = combined + "W"
    return combined


# =============================================================================
# 3. ADDRESS NORMALIZATION
# =============================================================================

def normalize_address(
    so_nha: Optional[str],
    duong: Optional[str]
) -> tuple[str, str]:
    """
    Chuẩn hóa số nhà và tên đường phục vụ so khớp địa chỉ giữa hai Pool.

    Pipeline:
    - Số nhà: strip, lowercase, lấy phần trước dấu +, collapse /
    - Đường: strip, khử dấu, lowercase, bỏ prefix (đường/phố/hẻm/ngõ/ngách),
      abbreviate tên đặc biệt (cmtt, bth, dsX)

    Args:
        so_nha: Số nhà thô.
        duong: Tên đường thô.

    Returns:
        Tuple (so_nha_normalized, duong_normalized).

    Examples:
        >>> normalize_address("42+44", "Cách Mạng Tháng Tám")
        ('42', 'cmtt')
        >>> normalize_address("123", "Nguyễn Trãi")
        ('123', 'nguyen trai')
    """
    so_nha = str(so_nha or "").strip().lower()
    if '+' in so_nha:
        so_nha = so_nha.split('+')[0].strip()
    # collapse slashes
    so_nha = re.sub(r'\s*/\s*', '/', so_nha)

    duong = str(duong or "").strip()
    duong_no_accent = remove_accents(duong).lower()
    # remove prefixes
    duong_no_accent = re.sub(r'^(duong|pho|hem|ngo|ngach)\s+', '', duong_no_accent)

    # abbreviation map
    if re.search(r'cach mang thang (tam|8)|cmt8', duong_no_accent):
        duong_no_accent = "cmtt"
    elif re.search(r'ba thang hai|3 thang 2|3/2|3-2', duong_no_accent):
        duong_no_accent = "bth"
    elif re.search(r'duong so (\d+)', duong_no_accent):
        match = re.search(r'duong so (\d+)', duong_no_accent)
        duong_no_accent = "ds" + match.group(1)

    duong_no_accent = re.sub(r'\s+', ' ', duong_no_accent).strip()
    return so_nha, duong_no_accent


# =============================================================================
# 4. GOOGLE SHEETS SAFETY
# =============================================================================

def escape_sheets_value(val):
    """
    Tránh lỗi công thức khi ghi lên Google Sheets bằng USER_ENTERED.

    Nếu nội dung bắt đầu bằng '-', '+', hoặc '=' và không phải là công thức
    hệ thống tự tạo (=IMAGE(), tự động thêm dấu nháy đơn (') ở đầu để ép
    kiểu text thô.

    Args:
        val: Giá trị cần escape. Chỉ xử lý string, non-string trả về nguyên.

    Returns:
        Giá trị đã escape (nếu cần).

    Examples:
        >>> escape_sheets_value("-100")
        "'-100"
        >>> escape_sheets_value('=IMAGE("url")')
        '=IMAGE("url")'  # không escape
        >>> escape_sheets_value(123)
        123  # non-string, unchanged
    """
    if not isinstance(val, str):
        return val
    if val.startswith('-') or val.startswith('+') or val.startswith('='):
        if val.upper().startswith('=IMAGE('):
            return val
        return "'" + val
    return val


def clean_sheet_formula_prefix(val):
    """
    Loại bỏ các ký tự bắt đầu công thức Google Sheets (+, -, =) ở đầu chuỗi text
    để tránh lỗi #ERROR! khi publish lên sheet. Không loại bỏ nếu là số hợp lệ.
    """
    if val is None:
        return ""
    val_str = str(val)
    val_strip = val_str.strip()
    if val_strip and val_strip[0] in ('+', '-', '='):
        try:
            float(val_strip)
            return val_str
        except ValueError:
            cleaned = re.sub(r'^[+\-=]+', '', val_strip).strip()
            return cleaned
    return val_str


# =============================================================================
# 5. CRITERIA CLASSIFICATION
# =============================================================================

# Mapping TK groupCode → tên cột Tiếng Việt
_CRITERIA_GROUP_MAPPING = {
    'PROPERTY_CRITERIA': 'Criteria_Tiem_nang_Rui_ro',
    'ROAD_TYPE': 'Criteria_Duong_truoc_nha',
    'PROPERTY_TYPE': 'Criteria_Loai_BDS',
    'LEGAL_DOCUMENT': 'Criteria_Giay_to_phap_ly',
    'LAND_PLOT_SHAPE': 'Criteria_Hinh_dang_dat',
    'CONSTRUCTION_STATUS': 'Criteria_Tinh_trang_xay_dung',
    'HOUSE_STRUCTURE': 'Criteria_Cau_truc_nha',
    'INTERIOR': 'Criteria_Noi_that',
    'ELEVATOR': 'Criteria_Thang_may',
    'ALLEY_TYPE': 'Criteria_Loai_ngo',
    'TAX_CALCULATION_POSITION': 'Criteria_Vi_tri_tinh_thue',
    'OPEN_SPACE': 'Criteria_Mat_thoang',
    'DISTANCE_TO_PARKING_LOT': 'Criteria_Khoang_cach_bai_do_xe',
    'PROPERTY_CRITERIA_BUSINESS_CASH_FLOW': 'Criteria_Kinh_doanh_Dong_tien',
    'PROPERTY_CRITERIA_FACILITIES': 'Criteria_Tien_ich',
    'PROPERTY_CRITERIA_GEOMANCY': 'Criteria_Phong_thuy',
    'HOUSE_DIRECTION': 'Criteria_Huong_nha',
    'POSITION_IN_ALLEY': 'Criteria_Vi_tri_trong_ngo',
    'DISTANCE_TO_MAIN_ROAD': 'Criteria_Khoang_cach_duong_oto'
}


def parse_criteria_groups(criteria_list: Optional[list]) -> dict[str, str]:
    """
    Phân loại các đặc tính (criteria) theo groupCode của TK thành 19 nhóm
    Tiếng Việt tương ứng.

    Args:
        criteria_list: Danh sách dicts từ TK API, mỗi dict có 'groupCode' và 'name'.

    Returns:
        Dict mapping 19 tên cột Criteria → chuỗi giá trị (join bằng ", ").
        Các cột không có giá trị sẽ là "".

    Examples:
        >>> parse_criteria_groups([{"groupCode": "ROAD_TYPE", "name": "Hẻm xe hơi"}])
        {'Criteria_Duong_truoc_nha': 'Hẻm xe hơi', ...}
    """
    result = {col: "" for col in _CRITERIA_GROUP_MAPPING.values()}
    grouped = {}
    for item in criteria_list or []:
        if not item:
            continue
        g_code = item.get("groupCode")
        name = item.get("name")
        if g_code and name:
            if g_code not in grouped:
                grouped[g_code] = []
            grouped[g_code].append(name)

    for g_code, names in grouped.items():
        col_name = _CRITERIA_GROUP_MAPPING.get(g_code)
        if col_name:
            result[col_name] = ", ".join(names)

    return result


# =============================================================================
# 6. DATA ROW BUILDING
# =============================================================================

def build_row_data(headers: list[str], data_dict: dict) -> list[str]:
    """
    Phân giải chỉ số cột động: nhận mảng headers thực tế từ sheet và data_dict,
    trả về mảng 1 dòng dữ liệu đã map đúng vị trí header.

    Thử match theo: header gốc → safe_col_name → custom_safe → custom_header.

    Args:
        headers: Danh sách header từ Google Sheets (thứ tự cột).
        data_dict: Dict dữ liệu cần map vào các cột.

    Returns:
        List[str] — 1 dòng dữ liệu đã escape, đúng thứ tự headers.
    """
    row = []
    for h in headers:
        val = ""
        safe_h = get_safe_col_name(h)
        keys_to_try = [h, safe_h, f"custom_{safe_h}", f"custom_{h}"]
        for k in keys_to_try:
            if k in data_dict:
                val = data_dict[k]
                break
        if val is None:
            val = ""
        row.append(escape_sheets_value(str(val)))
    return row


def recover_listing_from_raw_json(conn, tk_id, active_table="listings", update_type="all"):
    """
    Khôi phục thông tin chi tiết căn nhà từ cột raw_json_full trong SQLite.
    Bảo toàn lịch sử thay đổi giá trong JSON_UI và ánh xạ ảnh đã có.
    """
    import json
    cursor = conn.cursor()
    
    # Đọc cấu trúc các cột để tránh lỗi
    cursor.execute(f"PRAGMA table_info({active_table})")
    db_cols = {r[1] for r in cursor.fetchall()}
    
    select_cols = ["raw_json_full", "JSON_UI", "curated_config_json", "status", "System_ID", "Ma_Khang_Ngo_ID"]
    has_mapping_col = "images_mapping_json" in db_cols
    if has_mapping_col:
        select_cols.append("images_mapping_json")
        
    cols_str = ", ".join([f"`{c}`" for c in select_cols])
    row = cursor.execute(f"SELECT {cols_str} FROM {active_table} WHERE tk_id = ?", (tk_id,)).fetchone()
    
    if not row or not row[0]:
        return False
        
    raw_json_full = row[0]
    old_json_ui_str = row[1]
    old_curated_config_str = row[2]
    status = row[3]
    system_id = row[4]
    ma_khang_ngo_id = row[5]
    old_images_mapping_str = row[6] if has_mapping_col else None
    
    try:
        detail_data = json.loads(raw_json_full)
    except Exception:
        return False
        
    # 1. Khôi phục JSON_UI (bảo toàn lịch sử giá)
    if update_type in ("all", "json_ui"):
        from pool_lego import extract_json_ui_data
        new_json_ui = extract_json_ui_data(detail_data)
        
        old_json_ui = {}
        if old_json_ui_str:
            try:
                old_json_ui = json.loads(old_json_ui_str)
            except Exception:
                pass
                
        # Bảo toàn lịch sử thay đổi giá
        new_json_ui["history"] = old_json_ui.get("history") or []
        new_json_ui_str = json.dumps(new_json_ui, ensure_ascii=False)
        cursor.execute(f"UPDATE {active_table} SET JSON_UI = ? WHERE tk_id = ?", (new_json_ui_str, tk_id))

    # 2. Khôi phục các cột phẳng (số phòng ngủ, số vệ sinh, và 19 cột tiêu chí)
    if update_type in ("all", "columns"):
        so_phong_ngu = str(detail_data.get("bedrooms") or "")
        so_nha_ve_sinh = str(detail_data.get("restrooms") or "")
        criteria_list = detail_data.get("criteria") or []
        criteria_cols = parse_criteria_groups(criteria_list)
        
        cursor.execute(f"PRAGMA table_info({active_table})")
        db_cols = {r[1] for r in cursor.fetchall()}
        
        update_vals = {}
        if "So_phong_ngu" in db_cols:
            update_vals["So_phong_ngu"] = so_phong_ngu
        if "So_nha_ve_sinh" in db_cols:
            update_vals["So_nha_ve_sinh"] = so_nha_ve_sinh
            
        for col, val in criteria_cols.items():
            if col in db_cols:
                update_vals[col] = val
                
        if update_vals:
            set_clause = ", ".join([f"`{k}` = ?" for k in update_vals.keys()])
            cursor.execute(
                f"UPDATE {active_table} SET {set_clause} WHERE tk_id = ?",
                list(update_vals.values()) + [tk_id]
            )

    # 3. Khôi phục danh sách hình ảnh (listings_images, curated_config_json)
    if update_type in ("all", "images"):
        media = detail_data.get("media") or []
        property_images = []
        sodo_images = []
        for m in media:
            m_type = m.get("type")
            m_url = m.get("url")
            if not m_url:
                continue
            if m_type in ["parcel_map", "certificate_image"]:
                sodo_images.append(m_url)
            else:
                property_images.append(m_url)
                
        grouped_urls = property_images + sodo_images
        raw_images_tk_json_val = json.dumps(grouped_urls, ensure_ascii=False)
        raw_sodo_tk_json_val = json.dumps(sodo_images, ensure_ascii=False)
        
        images_mapping = {}
        if old_images_mapping_str:
            try:
                images_mapping = json.loads(old_images_mapping_str)
            except Exception:
                pass

        # NẾU images_mapping đang trống hoặc thiếu ánh xạ, ta sẽ dùng cơ chế R2 Precheck để khôi phục mapping (tham khảo US-141)
        try:
            from manager import load_config
            cfg = load_config()
            has_r2_creds = cfg.get("r2_access_key_id") and cfg.get("r2_secret_access_key") and cfg.get("r2_bucket_name") and cfg.get("cloudflare_account_id")
        except Exception:
            has_r2_creds = False

        if not images_mapping and has_r2_creds:
            try:
                from manager import list_r2_objects, get_r2_subfolder
                r2_public_url = cfg.get("r2_public_url")
                r2_migration_prefix = cfg.get("r2_migration_prefix", "BDS-KhangNgo-v2") or "BDS-KhangNgo-v2"
                
                addr_cols = ["Ngo_So_nha", "Duong", "Quan", "Phuong"]
                addr_valid = [c for c in addr_cols if c in db_cols]
                if addr_valid:
                    addr_clause = ", ".join([f"`{c}`" for c in addr_valid])
                    addr_row = cursor.execute(f"SELECT {addr_clause} FROM {active_table} WHERE tk_id = ?", (tk_id,)).fetchone()
                    if addr_row:
                        addr_dict = {addr_valid[i]: (addr_row[i] or "") for i in range(len(addr_valid))}
                        r2_subfolder = get_r2_subfolder(tk_id, addr_dict)
                        prefix = f"{r2_migration_prefix}/{r2_subfolder}/"
                        r2_keys = list_r2_objects(prefix)
                        
                        if not r2_keys:
                            old_prefixes = [
                                f"BDS-KhangNgo/img_{tk_id}",
                                f"BDS-KhangNgo/sodo",
                                f"BDS-KhangNgo/SYS-{tk_id.upper()}",
                                f"BDS-KhangNgo/SYS-{tk_id.lower()}",
                                f"BDS-KhangNgo/SYS-{tk_id.replace('-', '').upper()}",
                                f"BDS-KhangNgo/SYS-{tk_id.replace('-', '').lower()}"
                            ]
                            for op in old_prefixes:
                                res_keys = list_r2_objects(op)
                                if res_keys:
                                    if op == "BDS-KhangNgo/sodo":
                                        res_keys = [k for k in res_keys if tk_id in k]
                                    r2_keys.extend(res_keys)
                            r2_keys = list(set(r2_keys))
                            
                        if r2_keys and r2_public_url:
                            for key in r2_keys:
                                filename = key.split("/")[-1]
                                r2_url = f"{r2_public_url}/{key}"
                                
                                # 1. Ảnh thường: img_{tk_id}_{idx}.jpg
                                if filename.startswith(f"img_{tk_id}_") and filename.endswith(".jpg"):
                                    try:
                                        idx_str = filename[len(f"img_{tk_id}_"):-4]
                                        idx = int(idx_str)
                                        if 1 <= idx <= len(property_images):
                                            img_url = property_images[idx - 1]
                                            images_mapping[img_url] = r2_url
                                    except Exception:
                                        pass
                                        
                                # 2. Sơ đồ: sodo{sodo_num}_{tk_id}.jpg
                                elif filename.startswith("sodo") and filename.endswith(f"_{tk_id}.jpg"):
                                    try:
                                        sodo_num = filename[4:filename.find(f"_{tk_id}")]
                                        sodo_idx = int(sodo_num) - 1
                                        if 0 <= sodo_idx < len(sodo_images):
                                            img_url = sodo_images[sodo_idx]
                                            images_mapping[img_url] = r2_url
                                    except Exception:
                                        pass
            except Exception as e_precheck:
                print(f"[⚠️ WARNING] R2 precheck recovery failed: {str(e_precheck)}")

        old_curated_config = {}
        if old_curated_config_str:
            try:
                old_curated_config = json.loads(old_curated_config_str)
            except Exception:
                pass
                
        old_images_map = {
            img.get("image_url") or img.get("r2_url"): img 
            for img in old_curated_config.get("images", [])
        }
        
        images_list = []
        # Nạp ảnh sơ đồ
        for idx, url in enumerate(sodo_images):
            img_item = old_images_map.get(url) or {}
            r2_url = images_mapping.get(url) or img_item.get("r2_url") or ""
            images_list.append({
                "image_url": url,
                "r2_url": r2_url,
                "role": img_item.get("role") or "diagram",
                "sequence_index": img_item.get("sequence_index") if img_item.get("sequence_index") is not None else (100 + idx),
                "is_hidden": img_item.get("is_hidden") or 0,
                "origin": img_item.get("origin") or "crawl",
                "url": r2_url if r2_url else url
            })
            
        # Nạp ảnh thường
        for idx, url in enumerate(property_images):
            img_item = old_images_map.get(url) or {}
            r2_url = images_mapping.get(url) or img_item.get("r2_url") or ""
            role = img_item.get("role")
            if not role:
                role = "facade" if idx == 0 else "interior"
            images_list.append({
                "image_url": url,
                "r2_url": r2_url,
                "role": role,
                "sequence_index": img_item.get("sequence_index") if img_item.get("sequence_index") is not None else idx,
                "is_hidden": img_item.get("is_hidden") or 0,
                "origin": img_item.get("origin") or "crawl",
                "url": r2_url if r2_url else url
            })
            
        # Giữ lại các ảnh upload thủ công (SYS-...)
        for img in old_curated_config.get("images", []):
            img_url = img.get("image_url") or ""
            if img_url.startswith("SYS-") or "SYS-" in img_url or img.get("origin") == "local":
                if img_url not in [x.get("image_url") for x in images_list]:
                    # Đảm bảo ảnh thủ công cũng có url
                    if isinstance(img, dict) and not img.get("url"):
                        img["url"] = img.get("r2_url") or img_url
                    images_list.append(img)
                    
        new_curated_config = {
            "images": images_list,
            "Ma_Khang_Ngô__ID_": ma_khang_ngo_id or ""
        }
        new_curated_config_str = json.dumps(new_curated_config, ensure_ascii=False)
        
        # Tạo Images_Admin_JSON và images_public_json
        cover_urls = []
        other_urls = []
        for img in images_list:
            if img.get("is_hidden") == 0 and img.get("role") not in ["facade", "diagram", "deleted", "hidden"]:
                url = img.get("r2_url") or img.get("image_url")
                if img.get("role") == "cover":
                    cover_urls.append(url)
                else:
                    other_urls.append(url)
        public_urls = cover_urls + other_urls
        images_public_json_val = json.dumps(public_urls, ensure_ascii=False)
        
        # Images_Admin_JSON phải là danh sách đối tượng ảnh đầy đủ
        images_admin_json_val = json.dumps(images_list, ensure_ascii=False)
        
        # Dựng lại các cột phẳng hình ảnh trong database
        flat_img_vals = {}
        sodo_list = []
        facade_list = []
        alley_list = []
        interior_list = []
        
        for img in images_list:
            if img.get("is_hidden") == 1 or img.get("role") in ["deleted", "hidden"]:
                continue
            url = img.get("r2_url") or img.get("image_url")
            if not url:
                continue
            role = img.get("role")
            if role == "diagram":
                sodo_list.append(url)
            elif role == "facade":
                facade_list.append(url)
            elif role == "alley":
                alley_list.append(url)
            else:
                interior_list.append(url)
                
        for i in range(5):
            col_name = f"So_do_thua_dat_{i+1}"
            if col_name in db_cols:
                flat_img_vals[col_name] = sodo_list[i] if i < len(sodo_list) else ""
                
        if "Hinh_Mat_Tien" in db_cols:
            flat_img_vals["Hinh_Mat_Tien"] = facade_list[0] if facade_list else ""
            
        for i in range(10):
            col_name = f"Hinh_Hem_{i+1}"
            if col_name in db_cols:
                flat_img_vals[col_name] = alley_list[i] if i < len(alley_list) else ""
                
        for i in range(25):
            col_name = f"Anh_{i+1}"
            if col_name in db_cols:
                flat_img_vals[col_name] = interior_list[i] if i < len(interior_list) else ""
                
        if flat_img_vals:
            set_clause = ", ".join([f"`{k}` = ?" for k in flat_img_vals.keys()])
            cursor.execute(
                f"UPDATE {active_table} SET {set_clause} WHERE tk_id = ?",
                list(flat_img_vals.values()) + [tk_id]
            )

        if has_mapping_col:
            cursor.execute(
                f"UPDATE {active_table} SET raw_images_tk_json = ?, raw_sodo_tk_json = ?, curated_config_json = ?, Images_Admin_JSON = ?, images_public_json = ?, images_mapping_json = ? WHERE tk_id = ?",
                (raw_images_tk_json_val, raw_sodo_tk_json_val, new_curated_config_str, images_admin_json_val, images_public_json_val, json.dumps(images_mapping, ensure_ascii=False), tk_id)
            )
        else:
            cursor.execute(
                f"UPDATE {active_table} SET raw_images_tk_json = ?, raw_sodo_tk_json = ?, curated_config_json = ?, Images_Admin_JSON = ?, images_public_json = ? WHERE tk_id = ?",
                (raw_images_tk_json_val, raw_sodo_tk_json_val, new_curated_config_str, images_admin_json_val, images_public_json_val, tk_id)
            )
        
        # Đồng bộ bảng listings_images vật lý
        cursor.execute("DELETE FROM listings_images WHERE tk_id = ?", (tk_id,))
        for img in images_list:
            cursor.execute("""
                INSERT INTO listings_images (tk_id, system_id, image_url, r2_url, role, sequence_index, origin, is_hidden)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tk_id,
                system_id,
                img.get("image_url"),
                img.get("r2_url"),
                img.get("role"),
                img.get("sequence_index"),
                "local" if (img.get("image_url") or "").startswith("SYS-") else "crawled",
                img.get("is_hidden")
            ))
            
        # Cập nhật trạng thái tin để kích hoạt di cư ngầm nếu thiếu ảnh R2
        has_missing_r2 = any(
            not img.get("r2_url") 
            for img in images_list 
            if img.get("role") not in ["deleted", "hidden"] and not (img.get("image_url") or "").startswith("SYS-")
        )
        if has_missing_r2 and status != "published":
            cursor.execute(f"UPDATE {active_table} SET status = 'raw_text' WHERE tk_id = ?", (tk_id,))
        elif not has_missing_r2 and status in ["raw_text", "crawl_failed"]:
            cursor.execute(f"UPDATE {active_table} SET status = 'raw_complete' WHERE tk_id = ?", (tk_id,))

    conn.commit()
    return True

