# -*- coding: utf-8 -*-
import sys
import os
import json
import sqlite3
import tempfile
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manager
from pool_lego import init_db

@pytest.fixture
def temp_db():
    # 1. Tạo tệp cơ sở dữ liệu tạm thời
    fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    # 2. Lưu trữ DB_FILE gốc và gán tạm thời sang tệp db mới
    old_db_file = manager.DB_FILE
    manager.DB_FILE = temp_db_path
    
    # 3. Khởi tạo schema cho database tạm thời
    init_db(temp_db_path)
    
    # 4. Chèn một căn nhà giả lập
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    
    tk_id = "test-tk-id-123"
    cursor.execute(f"""
        INSERT INTO {manager.LISTINGS_TABLE} (tk_id, Link_Goc, status, raw_images_tk_json)
        VALUES (?, ?, ?, ?)
    """, (tk_id, "https://proptech.thienkhoi.com/warehouse/sources/test-tk-id-123", "raw_text", "[]"))
    conn.commit()
    conn.close()
    
    yield temp_db_path
    
    # Khôi phục DB_FILE cũ và dọn dẹp file db tạm thời
    manager.DB_FILE = old_db_file
    if os.path.exists(temp_db_path):
        try:
            os.remove(temp_db_path)
        except Exception:
            pass

@pytest.fixture
def client(temp_db):
    manager.app.config['TESTING'] = True
    with manager.app.test_client() as client:
        yield client

@patch('requests.get')
def test_async_recrawl_success(mock_get, client):
    # Mock phản hồi requests.get giả lập API Thiên Khôi
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "code": "TEST-MA-HANG",
            "district": {"provinceName": "TP Hồ Chí Minh", "name": "Quận 1"},
            "ward": {"name": "Bến Nghé"},
            "streetName": "Nguyễn Huệ",
            "address": "123",
            "area": 50,
            "actualArea": 50,
            "floors": 3,
            "offeringPrice": 10.5,
            "description": "Nhà đẹp trung tâm Quận 1",
            "criteria": [],
            "media": []
        }
    }
    mock_get.return_value = mock_response
    
    tk_id = "test-tk-id-123"
    payload = {
        "cookie": "mock-cookie-data",
        "title": "Mock Title Text"
    }
    
    # Gửi request recrawl
    response = client.post(f"/api/listings/{tk_id}/recrawl", json=payload)
    
    # 1. Xác nhận API trả về HTTP 200 thành công nhanh chóng
    assert response.status_code == 200
    res_data = response.get_json()
    assert res_data["status"] == "success"
    
    # 2. Xác nhận trạng thái SQLite được cập nhật thành 'raw_text' để background_worker quét xử lý
    conn = sqlite3.connect(manager.DB_FILE)
    cursor = conn.cursor()
    row = cursor.execute(f"SELECT status FROM {manager.LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
    conn.close()
    assert row is not None
    assert row[0] == "raw_text"

