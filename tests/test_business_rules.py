"""
Unit tests cho business rules — MOD-01 PREPARE step.

Tests này lock behavior hiện tại của các functions nghiệp vụ trong pool_lego.py
và manager.py TRƯỚC khi tách code. Nếu refactor phá hỏng logic → tests sẽ FAIL.

BUSINESS RULES: docs/transformation_roadmap.md (MOD-01)
RELATED FILES: pool_lego.py (functions gốc), query_helper.py (duplicate remove_accents)
"""
import sys
import os
import re

# Thêm project root vào path để import trực tiếp từ file gốc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pool_lego import (
    remove_accents,
    get_safe_col_name,
    gen_id_khang_ngo_python,
    normalize_address,
    escape_sheets_value,
)


# =============================================================================
# 1. REMOVE_ACCENTS — Khử dấu tiếng Việt
# =============================================================================
class TestRemoveAccents:
    """Lock behavior: remove_accents() khử dấu tiếng Việt."""

    def test_basic_vietnamese(self):
        assert remove_accents("Cách Mạng Tháng Tám") == "Cach Mang Thang Tam"

    def test_lowercase_vietnamese(self):
        assert remove_accents("đường số bảy") == "duong so bay"

    def test_uppercase_d(self):
        assert remove_accents("Đông") == "Dong"
        assert remove_accents("đ") == "d"

    def test_mixed_accents(self):
        assert remove_accents("Phú Nhuận") == "Phu Nhuan"
        assert remove_accents("Bình Thạnh") == "Binh Thanh"

    def test_empty_string(self):
        assert remove_accents("") == ""

    def test_none_input(self):
        assert remove_accents(None) == ""

    def test_no_accents_unchanged(self):
        assert remove_accents("Hello World 123") == "Hello World 123"

    def test_special_chars_preserved(self):
        assert remove_accents("Đường 3/2") == "Duong 3/2"


# =============================================================================
# 2. GEN_ID_KHANG_NGO_PYTHON — Sinh mã ID KhangNgo
# =============================================================================
class TestGenIdKhangNgo:
    """Lock behavior: gen_id_khang_ngo_python() sinh mã nhà."""

    # --- House number encoding ---
    def test_simple_number(self):
        """Số nhà đơn giản: 123 → MHB, W chèn vị trí 1 → MWHBIT"""
        result = gen_id_khang_ngo_python("123", "Test", "Q1")
        # Mã số nhà: M(1)H(2)B(3), đường "Test" → T → reversed = T
        # combined = MHBIT, insert W at pos 1 → MWHBIT
        assert result == "MWHBIT"

    def test_house_number_with_plus(self):
        """Số nhà có dấu + → lấy phần trước dấu +"""
        result_with_plus = gen_id_khang_ngo_python("42+44", "Test", "Q1")
        result_without_plus = gen_id_khang_ngo_python("42", "Test", "Q1")
        assert result_with_plus == result_without_plus

    def test_house_number_with_slash(self):
        """Dấu / trong số nhà → encode thành I"""
        result = gen_id_khang_ngo_python("12/3", "Test", "Q1")
        assert "I" in result  # / → I

    def test_house_number_with_dot(self):
        """Dấu . trong số nhà → encode thành I"""
        result = gen_id_khang_ngo_python("1168.42", "Test", "Q1")
        # 1→M, 1→M, 6→S, 8→T, .→I, 4→A, 2→H → MMSTIAH
        # đường "Test" → T → reversed = T, combined = MMSTIAHIT
        # insert W at pos 1 → MWMSTIAHIT
        assert result == "MWMSTIAHIT"

    def test_empty_house_number(self):
        """Số nhà rỗng → không crash"""
        result = gen_id_khang_ngo_python("", "Test", "Q1")
        assert isinstance(result, str)

    def test_none_inputs(self):
        """None inputs → không crash"""
        result = gen_id_khang_ngo_python(None, None, None)
        assert isinstance(result, str)

    # --- Street name abbreviation ---
    def test_cach_mang_thang_tam_special(self):
        """Cách Mạng Tháng Tám → CMTT"""
        r1 = gen_id_khang_ngo_python("1", "Cách Mạng Tháng Tám", "Q1")
        r2 = gen_id_khang_ngo_python("1", "Cách Mạng Tháng 8", "Q1")
        r3 = gen_id_khang_ngo_python("1", "CMT8", "Q1")
        # Tất cả phải cho cùng kết quả vì đều normalize thành CMTT
        assert r1 == r2
        assert r2 == r3

    def test_ba_thang_hai_special(self):
        """Ba Tháng Hai → BTH"""
        r1 = gen_id_khang_ngo_python("1", "Ba Tháng Hai", "Q1")
        r2 = gen_id_khang_ngo_python("1", "3 Tháng 2", "Q1")
        r3 = gen_id_khang_ngo_python("1", "3/2", "Q1")
        assert r1 == r2
        assert r2 == r3

    def test_duong_so_x_special(self):
        """Đường số X → DSX"""
        r1 = gen_id_khang_ngo_python("1", "Đường số 7", "Q1")
        r2 = gen_id_khang_ngo_python("1", "Đường số 12", "Q1")
        # DS7 và DS12 → khác nhau
        assert r1 != r2

    def test_normal_street_abbreviation(self):
        """Đường bình thường → viết tắt chữ cái đầu"""
        # "Nguyễn Văn Cừ" → remove_accents → "Nguyen Van Cu" → N + V + C = NVC
        result = gen_id_khang_ngo_python("1", "Nguyễn Văn Cừ", "Q1")
        assert isinstance(result, str)
        assert len(result) > 0

    # --- Deterministic output ---
    def test_same_input_same_output(self):
        """Cùng input → luôn ra cùng output (deterministic)"""
        r1 = gen_id_khang_ngo_python("123", "Lý Thường Kiệt", "Q10")
        r2 = gen_id_khang_ngo_python("123", "Lý Thường Kiệt", "Q10")
        assert r1 == r2

    def test_different_houses_different_ids(self):
        """Khác số nhà → khác ID"""
        r1 = gen_id_khang_ngo_python("1", "Test", "Q1")
        r2 = gen_id_khang_ngo_python("2", "Test", "Q1")
        assert r1 != r2


# =============================================================================
# 3. NORMALIZE_ADDRESS — Chuẩn hóa địa chỉ để so khớp
# =============================================================================
class TestNormalizeAddress:
    """Lock behavior: normalize_address() chuẩn hóa để match giữa 2 Pool."""

    def test_basic_normalization(self):
        so_nha, duong = normalize_address("123", "Nguyễn Trãi")
        assert so_nha == "123"
        assert duong == "nguyen trai"  # lowercase, no accents

    def test_house_number_plus_sign(self):
        """Số nhà 42+44 → lấy 42"""
        so_nha, _ = normalize_address("42+44", "Test")
        assert so_nha == "42"

    def test_house_number_lowercase(self):
        """Số nhà lowercase"""
        so_nha, _ = normalize_address("12A", "Test")
        assert so_nha == "12a"

    def test_street_prefix_removed(self):
        """Bỏ prefix 'Đường', 'Phố', 'Hẻm'"""
        _, duong = normalize_address("1", "Đường Nguyễn Huệ")
        assert not duong.startswith("duong ")

    def test_cach_mang_thang_tam_normalized(self):
        """CMTT special case"""
        _, duong = normalize_address("1", "Cách Mạng Tháng Tám")
        assert duong == "cmtt"

    def test_ba_thang_hai_normalized(self):
        """BTH special case"""
        _, duong = normalize_address("1", "Ba Tháng Hai")
        assert duong == "bth"

    def test_duong_so_normalized(self):
        """Đường số X → dsX"""
        _, duong = normalize_address("1", "Đường Đường số 7")
        assert "ds7" in duong

    def test_none_inputs(self):
        """None → không crash"""
        so_nha, duong = normalize_address(None, None)
        assert so_nha == ""
        assert duong == ""

    def test_whitespace_collapsed(self):
        """Khoảng trắng thừa được gom"""
        _, duong = normalize_address("1", "  Nguyễn   Trãi  ")
        assert "  " not in duong


# =============================================================================
# 4. GET_SAFE_COL_NAME — Chuyển header tiếng Việt → SQLite column name
# =============================================================================
class TestGetSafeColName:
    """Lock behavior: get_safe_col_name() tạo column name an toàn."""

    def test_basic_conversion(self):
        result = get_safe_col_name("Số Nhà")
        assert result == "So_Nha"

    def test_special_chars_replaced(self):
        result = get_safe_col_name("Giá (tỷ đồng)")
        assert "(" not in result
        assert ")" not in result

    def test_multiple_underscores_collapsed(self):
        result = get_safe_col_name("A---B___C")
        assert "__" not in result  # No double underscores

    def test_empty_string(self):
        assert get_safe_col_name("") == ""

    def test_none_input(self):
        assert get_safe_col_name(None) == ""


# =============================================================================
# 5. ESCAPE_SHEETS_VALUE — Tránh lỗi công thức Google Sheets
# =============================================================================
class TestEscapeSheetsValue:
    """Lock behavior: escape_sheets_value() ngăn injection công thức."""

    def test_normal_text_unchanged(self):
        assert escape_sheets_value("Hello") == "Hello"

    def test_minus_prefix_escaped(self):
        assert escape_sheets_value("-100") == "'-100"

    def test_plus_prefix_escaped(self):
        assert escape_sheets_value("+84123") == "'+84123"

    def test_equals_prefix_escaped(self):
        assert escape_sheets_value("=SUM(A1)") == "'=SUM(A1)"

    def test_image_formula_not_escaped(self):
        """=IMAGE( là công thức hệ thống → KHÔNG escape"""
        val = '=IMAGE("https://example.com/img.jpg")'
        assert escape_sheets_value(val) == val

    def test_non_string_unchanged(self):
        assert escape_sheets_value(123) == 123
        assert escape_sheets_value(None) is None


# =============================================================================
# 6. REMOVE_ACCENTS DUPLICATE CHECK — So sánh 2 bản
# =============================================================================
class TestRemoveAccentsDuplicate:
    """Verify: remove_accents trong query_helper.py cho cùng kết quả."""

    def test_same_output_as_query_helper(self):
        from query_helper import remove_accents as remove_accents_qh
        test_cases = [
            "Cách Mạng Tháng Tám",
            "Đường số 7",
            "Phú Nhuận",
            "Bình Thạnh",
            "",
            "Hello World",
        ]
        for text in test_cases:
            assert remove_accents(text) == remove_accents_qh(text), \
                f"Mismatch for '{text}': pool_lego={remove_accents(text)}, query_helper={remove_accents_qh(text)}"
