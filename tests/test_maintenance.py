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
    @patch("manager.load_config")
    def test_config_returns_maintenance_mode_false_by_default(self, mock_load_config, client):
        """Mặc định khi không có cờ, /api/config trả về maintenance_mode = False."""
        mock_load_config.return_value = {
            "sheet_id": "test_sheet_id",
            "active_pool_system": "Pool1"
        }
        
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["config"]["maintenance_mode"] is False

    @patch("manager.load_config")
    def test_config_returns_maintenance_mode_true(self, mock_load_config, client):
        """Khi cờ maintenance_mode = True trong settings, /api/config trả về True."""
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
