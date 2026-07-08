"""
Core Config Reader — BDS KhangNgo.

Cung cấp một điểm truy cập thống nhất để đọc settings.json.
Thay thế pattern đọc inline rải rác trong pool_lego.py và fetcher.py.

SCOPE:
  - read_settings(): Đọc settings.json → dict, fallback {} nếu lỗi

KHÔNG bao gồm:
  - load_config() của manager.py: Phụ thuộc DEFAULT_CONFIG quá lớn.
    Consumer của manager.py tiếp tục dùng load_config() từ manager.py.
  - get_google_credentials(): Phức tạp, side effects, global state.

PATTERN THAY THẾ:
  Thay vì inline:
    config_file = "settings.json"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
  Dùng:
    from core.config import read_settings
    cfg = read_settings()

BUSINESS RULES:
  - docs/transformation_roadmap.md (MOD-03)

RELATED FILES:
  - pool_lego.py   → Delegate 4 chỗ đọc inline (sau WIRE)
  - fetcher.py     → Delegate 3 chỗ đọc inline (sau WIRE)
  - core/db.py     → get_db_file() đã dùng pattern này, có thể migrate sau
  - manager.py     → load_config() KHÔNG migrate (quá phức tạp)

TESTS: tests/test_config.py

OWNER: MOD-03 (Architecture Modernization)
"""

import os
import json


def read_settings(config_path: str = "settings.json") -> dict:
    """
    Đọc file settings JSON và trả về dict cấu hình.

    Pure function — không có side effects, không phụ thuộc global state.
    Thay thế pattern đọc inline rải rác trong pool_lego.py và fetcher.py.

    Args:
        config_path: Đường dẫn tới file settings. Mặc định "settings.json"
                     (relative to CWD, như các file khác trong project).

    Returns:
        dict: Nội dung settings. {} nếu file không tồn tại hoặc JSON lỗi.

    Examples:
        >>> cfg = read_settings()
        >>> sheet_id = cfg.get("sheet_id", "")
        >>> pool_system = cfg.get("active_pool_system", "Pool1")

        >>> # Custom path (cho testing)
        >>> cfg = read_settings("/tmp/test_settings.json")
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}
