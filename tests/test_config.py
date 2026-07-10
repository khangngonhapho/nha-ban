"""
Unit tests cho Config Reader — MOD-03 PREPARE step.

Tests này lock behavior của read_settings() TRƯỚC khi tách sang core/config.py.
Tests gọi trực tiếp logic đọc settings từ pool_lego (inline) để baseline.

Scope MOD-03:
  - read_settings(): đọc settings.json, trả về dict, fallback {} nếu lỗi

RELATED FILES: pool_lego.py, fetcher.py, core/config.py (sẽ tạo)
TESTS: tests/test_config.py (file này)
"""
import sys
import os
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Helper baseline — đây là pattern hiện tại inline trong pool_lego.py
def _read_settings_inline(config_file="settings.json"):
    """Baseline logic đọc settings.json như pool_lego.py đang làm inline."""
    cfg = {}
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
    except Exception:
        pass
    return cfg


# =============================================================================
# 1. READ_SETTINGS — Baseline behavior (inline pattern hiện tại)
# =============================================================================
class TestReadSettingsBaseline:
    """Lock behavior của pattern đọc settings.json inline trong pool_lego.py."""

    def test_missing_file_returns_empty_dict(self, tmp_path, monkeypatch):
        """Không có settings.json → trả về {}."""
        monkeypatch.chdir(tmp_path)
        result = _read_settings_inline()
        assert result == {}

    def test_valid_json_returns_dict(self, tmp_path, monkeypatch):
        """settings.json hợp lệ → trả về dict."""
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "settings.json"
        settings.write_text('{"key": "value", "number": 42}', encoding="utf-8")
        result = _read_settings_inline()
        assert result == {"key": "value", "number": 42}

    def test_invalid_json_returns_empty_dict(self, tmp_path, monkeypatch):
        """settings.json lỗi JSON → fallback {}, không crash."""
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "settings.json"
        settings.write_text("{ INVALID }", encoding="utf-8")
        result = _read_settings_inline()
        assert result == {}

    def test_active_pool_system_key_readable(self, tmp_path, monkeypatch):
        """active_pool_system key đọc được."""
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "settings.json"
        settings.write_text('{"active_pool_system": "Pool2"}', encoding="utf-8")
        result = _read_settings_inline()
        assert result.get("active_pool_system") == "Pool2"

    def test_sheet_id_key_readable(self, tmp_path, monkeypatch):
        """sheet_id key đọc được."""
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "settings.json"
        settings.write_text('{"sheet_id": "abc123"}', encoding="utf-8")
        result = _read_settings_inline()
        assert result.get("sheet_id") == "abc123"

    def test_empty_json_object_returns_empty_dict(self, tmp_path, monkeypatch):
        """settings.json là {} → trả về {}."""
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "settings.json"
        settings.write_text('{}', encoding="utf-8")
        result = _read_settings_inline()
        assert result == {}

    def test_utf8_values_readable(self, tmp_path, monkeypatch):
        """Giá trị UTF-8 tiếng Việt đọc được."""
        monkeypatch.chdir(tmp_path)
        settings = tmp_path / "settings.json"
        settings.write_text('{"name": "Khang Ngô"}', encoding="utf-8")
        result = _read_settings_inline()
        assert result.get("name") == "Khang Ngô"


# =============================================================================
# 2. CORE.CONFIG — Sau khi extract, phải cho cùng kết quả
# =============================================================================
class TestCoreConfigReadSettings:
    """Sau khi EXTRACT core/config.py, phải tương thích 100% với baseline."""

    def test_missing_file_returns_empty_dict(self, tmp_path, monkeypatch):
        """read_settings() trả về {} khi không có file."""
        monkeypatch.chdir(tmp_path)
        from core.config import read_settings
        result = read_settings()
        assert result == {}

    def test_valid_json(self, tmp_path, monkeypatch):
        """read_settings() trả về dict đúng."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "settings.json").write_text('{"x": 1}', encoding="utf-8")
        from core.config import read_settings
        result = read_settings()
        assert result == {"x": 1}

    def test_invalid_json_fallback(self, tmp_path, monkeypatch):
        """read_settings() fallback {} khi JSON lỗi."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "settings.json").write_text("NOT JSON", encoding="utf-8")
        from core.config import read_settings
        result = read_settings()
        assert result == {}

    def test_utf8_support(self, tmp_path, monkeypatch):
        """read_settings() đọc được UTF-8."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "settings.json").write_text('{"tên": "giá trị"}', encoding="utf-8")
        from core.config import read_settings
        result = read_settings()
        assert result.get("tên") == "giá trị"

    def test_custom_path(self, tmp_path):
        """read_settings() hỗ trợ custom path."""
        custom = tmp_path / "custom.json"
        custom.write_text('{"custom": true}', encoding="utf-8")
        from core.config import read_settings
        result = read_settings(str(custom))
        assert result.get("custom") is True

    def test_same_output_as_baseline(self, tmp_path, monkeypatch):
        """read_settings() và baseline inline cho cùng kết quả."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "settings.json").write_text(
            '{"active_pool_system": "Pool2", "sheet_id": "xyz"}',
            encoding="utf-8"
        )
        from core.config import read_settings
        assert read_settings() == _read_settings_inline()

    def test_json_ui_fields_contains_dates(self):
        """Đảm bảo json_ui_fields chứa các trường ngày để render (US-127)."""
        from core.config import read_settings
        # Đọc thực tế settings.json của project (ở root)
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_path = os.path.join(project_dir, "settings.json")
        result = read_settings(settings_path)
        fields = result.get("json_ui_fields") or []
        assert "createdAt" in fields
        assert "updatedAt" in fields
        assert "listedAt" in fields
