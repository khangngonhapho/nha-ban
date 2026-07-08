# -*- coding: utf-8 -*-
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.config import read_settings
from scratch.sync_flags import sync_flags

class TestFeatureFlagsConfig:
    def test_settings_has_feature_flags(self):
        """Xác minh settings.json có chứa khóa feature_flags và là dict."""
        settings = read_settings()
        assert "feature_flags" in settings
        assert isinstance(settings["feature_flags"], dict)
        assert "maintenance_mode" in settings["feature_flags"]

class TestFeatureFlagsSync:
    @patch("scratch.sync_flags.gspread.authorize")
    @patch("scratch.sync_flags.manager.get_google_credentials")
    @patch("scratch.sync_flags.read_settings")
    def test_sync_flags_creates_worksheet_if_not_exists(self, mock_read_settings, mock_get_creds, mock_authorize):
        """Xác minh sync_flags sẽ tạo tab mới nếu chưa tồn tại trên Sheet."""
        # Mock settings
        mock_read_settings.return_value = {
            "sheet_id": "mock_sheet_id",
            "active_pool_system": "Pool1",
            "feature_flags": {
                "maintenance_mode": False,
                "test_new_flag": True
            }
        }
        
        # Mock gspread client & spreadsheet
        mock_client = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_authorize.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        
        # Raise WorksheetNotFound to trigger creation
        import gspread
        mock_spreadsheet.worksheet.side_effect = gspread.exceptions.WorksheetNotFound()
        
        mock_worksheet = MagicMock()
        mock_spreadsheet.add_worksheet.return_value = mock_worksheet
        mock_worksheet.get_all_records.return_value = []
        
        # Run sync
        log_messages = []
        res = sync_flags(add_log_message=log_messages.append)
        
        assert res["status"] == "success"
        mock_spreadsheet.add_worksheet.assert_called_once_with(title="Feature_Flags", rows=100, cols=10)
        mock_worksheet.update.assert_called_once()
        
    @patch("scratch.sync_flags.gspread.authorize")
    @patch("scratch.sync_flags.manager.get_google_credentials")
    @patch("scratch.sync_flags.read_settings")
    def test_sync_flags_updates_existing_and_cleans_deleted_flags(self, mock_read_settings, mock_get_creds, mock_authorize):
        """Xác minh sync_flags sẽ cập nhật giá trị hiện có và đánh dấu cleaned các flag đã bị xóa khỏi code."""
        # Mock settings (only test_new_flag is in code, old_flag is removed)
        mock_read_settings.return_value = {
            "sheet_id": "mock_sheet_id",
            "active_pool_system": "Pool1",
            "feature_flags": {
                "test_new_flag": True
            }
        }
        
        # Mock gspread client & spreadsheet
        mock_client = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_authorize.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        
        mock_worksheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_worksheet
        
        # Mock existing records on sheet: old_flag is active on sheet but no longer in mock_read_settings
        mock_worksheet.get_all_records.return_value = [
            {
                "Tên Flag": "old_flag",
                "Loại Flag": "Release Flags",
                "Giá Trị Hiện Tại": "TRUE",
                "Trạng Thái": "active",
                "Ngày Release": "2026-07-01",
                "Ngày Cập Nhật": "2026-07-01",
                "Mô tả": "Flag cũ"
            }
        ]
        
        # Run sync
        log_messages = []
        res = sync_flags(add_log_message=log_messages.append)
        
        assert res["status"] == "success"
        
        # Get the call arguments of update
        call_kwargs = mock_worksheet.update.call_args[1]
        rows_written = call_kwargs.get("values")
        
        # Headers should be at index 0
        assert rows_written[0] == ["Tên Flag", "Loại Flag", "Giá Trị Hiện Tại", "Trạng Thái", "Ngày Release", "Ngày Cập Nhật", "Mô tả"]
        
        # We should have two rows written below the headers:
        # test_new_flag (active, value TRUE) and old_flag (cleaned, value FALSE)
        flag_rows = {row[0]: row for row in rows_written[1:]}
        
        assert "test_new_flag" in flag_rows
        assert flag_rows["test_new_flag"][2] == "TRUE"
        assert flag_rows["test_new_flag"][3] == "active"
        
        assert "old_flag" in flag_rows
        assert flag_rows["old_flag"][2] == "FALSE"  # Cleaned is turned off
        assert flag_rows["old_flag"][3] == "cleaned"  # Marked as cleaned
