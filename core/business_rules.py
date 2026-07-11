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


def clean_formula_prefix(val):
    """
    Loại bỏ dấu '+', '-', '=' ở đầu chuỗi văn bản để tránh lỗi công thức Google Sheets.
    Không xử lý nếu là chuỗi JSON.
    """
    if not isinstance(val, str):
        return val
    val_strip = val.strip()
    if val_strip.startswith(('[', '{')):
        return val
    if val_strip.startswith(('+', '-', '=')):
        while val_strip.startswith(('+', '-', '=')):
            val_strip = val_strip[1:].strip()
        return val_strip
    return val


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
