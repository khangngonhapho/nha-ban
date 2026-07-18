# -*- coding: utf-8 -*-
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from manager import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestMaintenanceModeAPI:
    @patch("manager.get_google_credentials")
    @patch("api.routes_system.manager.load_config")
    def test_config_returns_maintenance_mode_false_by_default(self, mock_load_config, mock_get_creds, client):
        """Mặc định khi không có cờ, /api/config trả về maintenance_mode = False."""
        mock_get_creds.return_value = None
        mock_load_config.return_value = {
            "sheet_id": "test_sheet_id",
            "active_pool_system": "Pool1"
        }
        
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["config"]["maintenance_mode"] is False

    @patch("manager.get_google_credentials")
    @patch("api.routes_system.manager.load_config")
    def test_config_returns_maintenance_mode_true(self, mock_load_config, mock_get_creds, client):
        """Khi cờ maintenance_mode = True trong settings, /api/config trả về True."""
        mock_get_creds.return_value = None
        mock_load_config.return_value = {
            "sheet_id": "test_sheet_id",
            "active_pool_system": "Pool1",
            "feature_flags": {
                "maintenance_mode": True
            }
        }
        
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["config"]["maintenance_mode"] is True

    @patch("gspread.authorize")
    @patch("manager.get_google_credentials")
    @patch("api.routes_system.manager.load_config")
    def test_config_returns_maintenance_mode_from_google_sheets(self, mock_load_config, mock_get_creds, mock_authorize, client):
        """Khi có cờ maintenance_mode = True trên Google Sheets, /api/config trả về True."""
        mock_load_config.return_value = {
            "sheet_id": "test_sheet_id",
            "active_pool_system": "Pool1",
            "feature_flags": {
                "maintenance_mode": False
            }
        }
        mock_get_creds.return_value = MagicMock()
        
        # Mock gspread client, spreadsheet, worksheet
        mock_gc = MagicMock()
        mock_authorize.return_value = mock_gc
        mock_sh = MagicMock()
        mock_gc.open_by_key.return_value = mock_sh
        mock_wks = MagicMock()
        mock_sh.worksheet.return_value = mock_wks
        mock_wks.get_all_records.return_value = [
            {"Tên Flag": "maintenance_mode", "Giá Trị Hiện Tại": "TRUE", "Trạng Thái": "active"},
            {"Tên Flag": "enable_new_search_engine", "Giá Trị Hiện Tại": "FALSE", "Trạng Thái": "active"}
        ]
        
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["config"]["maintenance_mode"] is True

    @patch("gspread.authorize")
    @patch("manager.get_google_credentials")
    @patch("api.routes_system.manager.load_config")
    def test_config_falls_back_on_google_sheets_error(self, mock_load_config, mock_get_creds, mock_authorize, client):
        """Khi kết nối Google Sheets lỗi, /api/config rơi về fallback cấu hình local settings.json."""
        mock_load_config.return_value = {
            "sheet_id": "test_sheet_id",
            "active_pool_system": "Pool1",
            "feature_flags": {
                "maintenance_mode": True
            }
        }
        mock_get_creds.return_value = MagicMock()
        mock_authorize.side_effect = Exception("Sheets API Error")
        
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["config"]["maintenance_mode"] is True
