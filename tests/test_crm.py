# -*- coding: utf-8 -*-
import os
import sqlite3
import pytest
import hashlib
from datetime import datetime
from unittest.mock import MagicMock, patch

from pool_lego import init_db

@pytest.fixture
def temp_db(tmp_path):
    db_path = str(tmp_path / "test_raw_archive.db")
    # Khởi tạo DB sạch
    init_db(db_path)
    return db_path

def test_crm_db_table_exists(temp_db):
    """Kiểm tra bảng customer_profiles đã được tạo thành công trong SQLite"""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(customer_profiles)")
    cols = [r[1] for r in cursor.fetchall()]
    assert "raw_phone" in cols
    assert "phone_hash" in cols
    assert "name" in cols
    assert "note" in cols
    assert "lifecycle_status" in cols
    assert "updated_at" in cols
    
    conn.close()

@patch('api.routes_links.get_sheets_client')
def test_crm_api_endpoints(mock_sheets, temp_db):
    """Kiểm tra API GET/POST profiles khách hàng"""
    # Mock sheets client
    mock_client = MagicMock()
    mock_sheets.return_value = mock_client
    
    # Thiết lập mock app
    import manager
    app = manager.app
    app.config['TESTING'] = True
    
    with patch('manager.DB_FILE', temp_db):
        client = app.test_client()
        
        # 1. Ban đầu danh sách profile rỗng
        res = client.get('/api/customers/profiles')
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert len(data["profiles"]) == 0
        
        # 2. Tạo/Cập nhật profile mới (Ấm)
        payload = {
            "phone": "0987.654.321",
            "name": "Khách Test CRM",
            "note": "Nhu cầu biệt thự",
            "lifecycle_status": "Ấm"
        }
        res = client.post('/api/customers/profile', json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        assert "phone_hash" in data
        expected_hash = hashlib.sha256(b"0987654321").hexdigest()
        assert data["phone_hash"] == expected_hash
        
        # 3. Lấy lại danh sách, kiểm tra thông tin đã lưu
        res = client.get('/api/customers/profiles')
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["profiles"]) == 1
        prof = data["profiles"][0]
        assert prof["raw_phone"] == "0987654321"
        assert prof["phone_hash"] == expected_hash
        assert prof["name"] == "Khách Test CRM"
        assert prof["note"] == "Nhu cầu biệt thự"
        assert prof["lifecycle_status"] == "Ấm"
        
        # 4. Update status sang "Nóng"
        payload_update = {
            "phone": "0987.654.321",
            "lifecycle_status": "Nóng"
        }
        res = client.post('/api/customers/profile', json=payload_update)
        assert res.status_code == 200
        
        # Kiểm tra sự thay đổi trong SQLite
        res = client.get('/api/customers/profiles')
        data = res.get_json()
        prof = data["profiles"][0]
        assert prof["lifecycle_status"] == "Nóng"
        # Note cũ vẫn phải giữ nguyên
        assert prof["note"] == "Nhu cầu biệt thự"
