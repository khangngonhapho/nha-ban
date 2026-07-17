import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import helper hoặc hàm cần test
# Chúng ta sẽ viết hàm helper phân giải động để test trực tiếp logic của nó
def resolve_source_row_and_cols(source_values, system_id):
    """
    Logic dynamic resolution tương tự như sẽ triển khai trong pool_lego.py.
    Trả về (found_row_idx, id_col_idx)
    """
    # 1. Tìm dòng header
    header_row_idx = -1
    for idx, row in enumerate(source_values):
        if "System_ID" in row or "id" in row or "Cu_phap" in row or "System ID" in row:
            header_row_idx = idx
            break
            
    if header_row_idx == -1:
        return -1, 3 # Fallback col index 3 (cột 4)
        
    headers = source_values[header_row_idx]
    
    # 2. Tìm index cột động
    sys_id_col_idx = -1
    if "System_ID" in headers:
        sys_id_col_idx = headers.index("System_ID")
    elif "System ID" in headers:
        sys_id_col_idx = headers.index("System ID")
        
    id_col_idx = -1
    if "id" in headers:
        id_col_idx = headers.index("id")
        
    if sys_id_col_idx == -1:
        sys_id_col_idx = 37 # Fallback
    if id_col_idx == -1:
        id_col_idx = 3 # Fallback
        
    # 3. Quét tìm dòng khớp
    found_row_idx = -1
    start_data_idx = header_row_idx + 1
    for s_idx in range(start_data_idx, len(source_values)):
        s_row = source_values[s_idx]
        if len(s_row) > sys_id_col_idx and s_row[sys_id_col_idx].strip() == system_id:
            found_row_idx = s_idx + 1 # 1-indexed for Sheets
            break
            
    return found_row_idx, id_col_idx + 1


def legacy_resolve_source_row_and_cols(source_values, system_id):
    """
    Logic hardcode cũ của pool_lego.py
    """
    found_source_row_idx = -1
    for s_idx, s_row in enumerate(source_values[1:], start=2):
        if len(s_row) > 37 and s_row[37].strip() == system_id:
            found_source_row_idx = s_idx
            break
    return found_source_row_idx, 4


class TestSourceSyncResolution:
    """Test case chứng minh sự ưu việt của dynamic resolution so với legacy hardcode."""
    
    def test_legacy_fails_when_columns_shifted(self):
        """Code cũ thất bại khi cột bị dịch chuyển hoặc dòng header không ở dòng 1."""
        # Giả lập sheet Source có header ở dòng 3, cột System_ID bị dịch chuyển sang cột 40 (index 39)
        mock_source_values = [
            ["", "", "", "", "", "DT", "Tầng"],
            ["", "", "", "", "", "DT", "Tầng"],
            ["Hinh_mat_tien", "Cu_phap", "Note", "id", "tieu_de", "dien_tich", "so_tang", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "System_ID"], # System_ID ở index 38 (cột 39)
            ["", "", "", "SWHIGC", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "SYS-123456"]
        ]
        
        # Chạy logic cũ: tìm ở index 37 (cột 38)
        found_row, id_col = legacy_resolve_source_row_and_cols(mock_source_values, "SYS-123456")
        
        # Do hardcode index 37 nên không tìm thấy
        assert found_row == -1
        
    def test_dynamic_succeeds_when_columns_shifted(self):
        """Code mới thành công tìm đúng dòng và cột khi cấu trúc sheet thay đổi."""
        mock_source_values = [
            ["", "", "", "", "", "DT", "Tầng"],
            ["", "", "", "", "", "DT", "Tầng"],
            ["Hinh_mat_tien", "Cu_phap", "Note", "id", "tieu_de", "dien_tich", "so_tang", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "System_ID"], # System_ID ở index 38 (cột 39)
            ["", "", "", "SWHIGC", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "SYS-123456"]
        ]
        
        found_row, id_col = resolve_source_row_and_cols(mock_source_values, "SYS-123456")
        
        # Tìm thấy ở hàng 4 (1-indexed) và cột id là cột 4 (1-indexed)
        assert found_row == 4
        assert id_col == 4
