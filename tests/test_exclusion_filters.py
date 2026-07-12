# -*- coding: utf-8 -*-
import os
import sqlite3
import pytest
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pool_lego import init_db

@pytest.fixture
def temp_db(tmp_path):
    db_path = str(tmp_path / "test_raw_archive.db")
    init_db(db_path)
    return db_path

def test_exclusions_db_table_exists(temp_db):
    """Kiểm tra bảng exclusion_filters đã được tạo thành công trong SQLite"""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(exclusion_filters)")
    cols = [r[1] for r in cursor.fetchall()]
    assert "id" in cols
    assert "field" in cols
    assert "operator" in cols
    assert "value" in cols
    assert "status" in cols
    assert "note" in cols
    
    conn.close()

@patch('api.routes_links.get_sheets_client')
def test_exclusions_api_endpoints(mock_sheets, temp_db):
    """Kiểm tra API GET/POST exclusions loại trừ"""
    # Mock sheets client
    mock_client = MagicMock()
    mock_sheets.return_value = mock_client
    
    # Thiết lập mock app
    import manager
    app = manager.app
    app.config['TESTING'] = True
    
    with patch('manager.DB_FILE', temp_db):
        client = app.test_client()
        
        # 1. Ban đầu danh sách rules rỗng
        res = client.get('/api/exclusions/list')
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert len(data["exclusions"]) == 0
        
        # 2. Thêm rule loại trừ mới
        payload = {
            "field": "gia",
            "operator": "gte",
            "value": "25",
            "note": "Loại trừ nhà trên 25 tỷ"
        }
        res = client.post('/api/exclusions/add', json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "id" in data
        added_id = data["id"]
        
        # 3. Lấy lại danh sách, kiểm tra thông tin đã lưu
        res = client.get('/api/exclusions/list')
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["exclusions"]) == 1
        rule = data["exclusions"][0]
        assert rule["id"] == added_id
        assert rule["field"] == "gia"
        assert rule["operator"] == "gte"
        assert rule["value"] == "25"
        assert rule["status"] == "Active"
        assert rule["note"] == "Loại trừ nhà trên 25 tỷ"
        
        # 4. Gỡ bỏ rule loại trừ (đổi status sang Inactive)
        payload_remove = {
            "id": added_id
        }
        res = client.post('/api/exclusions/remove', json=payload_remove)
        assert res.status_code == 200
        
        # 5. Kiểm tra danh sách rules hoạt động rỗng trở lại
        res = client.get('/api/exclusions/list')
        data = res.get_json()
        assert len(data["exclusions"]) == 0

@patch('manager.get_google_credentials')
def test_config_endpoint_includes_exclusions(mock_creds, temp_db):
    """Kiểm tra config endpoint trả về exclusions"""
    mock_creds.return_value = None
    
    import manager
    app = manager.app
    app.config['TESTING'] = True
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO exclusion_filters (id, field, operator, value, status, note)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("crit_test_123", "phuong", "contains", "Phường 15", "Active", "Note test"))
    conn.commit()
    conn.close()
    
    with patch('manager.DB_FILE', temp_db):
        client = app.test_client()
        
        res = client.get('/api/config')
        assert res.status_code == 200
        data = res.get_json()
        assert "config" in data
        cfg = data["config"]
        assert "exclusions" in cfg
        assert len(cfg["exclusions"]) == 1
        rule = cfg["exclusions"][0]
        assert rule["id"] == "crit_test_123"
        assert rule["field"] == "phuong"
        assert rule["operator"] == "contains"
        assert rule["value"] == "Phường 15"
