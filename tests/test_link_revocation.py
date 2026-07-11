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

def test_db_tables_exist(temp_db):
    """Kiểm tra các bảng shared_links và phone_blacklist đã được tạo thành công"""
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    
    # Check shared_links
    cursor.execute("PRAGMA table_info(shared_links)")
    cols = [r[1] for r in cursor.fetchall()]
    assert "link_id" in cols
    assert "customer_name" in cols
    assert "shared_house_ids" in cols
    assert "bound_phone_hash" in cols
    assert "status" in cols
    
    # Check phone_blacklist
    cursor.execute("PRAGMA table_info(phone_blacklist)")
    cols_bl = [r[1] for r in cursor.fetchall()]
    assert "raw_phone" in cols_bl
    assert "phone_hash" in cols_bl
    assert "status" in cols_bl
    
    conn.close()

@patch('api.routes_links.get_sheets_client')
def test_register_and_bind_link(mock_sheets, temp_db):
    """Kiểm tra API tạo và bind SĐT vào link chia sẻ"""
    # Mock sheets client
    mock_client = MagicMock()
    mock_sheets.return_value = mock_client
    
    # Thiết lập mock app
    import manager
    app = manager.app
    app.config['TESTING'] = True
    
    # Patch DB file to temp_db
    with patch('manager.DB_FILE', temp_db):
        client = app.test_client()
        
        # 1. Register Link
        payload = {
            "customer_name": "Nguyễn Văn A",
            "customer_note": "Khách VIP xem biệt thự",
            "shared_house_ids": "SYS-20262401-1,SYS-20262401-2",
            "expires_in_days": 10
        }
        res = client.post('/api/links/register', json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "success"
        link_id = data["link_id"]
        assert link_id.startswith("LNK-")
        
        # Kiểm tra SQLite đã lưu đúng
        conn = sqlite3.connect(temp_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shared_links WHERE link_id = ?", (link_id,))
        row = cursor.fetchone()
        assert row is not None
        assert row["customer_name"] == "Nguyễn Văn A"
        assert row["status"] == "Active"
        assert row["bound_phone_hash"] == ""
        conn.close()
        
        # 2. Bind Phone to Link
        phone = "0901234567"
        phone_hash = hashlib.sha256(phone.encode('utf-8')).hexdigest()
        
        bind_payload = {
            "link_id": link_id,
            "phone_hash": phone_hash
        }
        res_bind = client.post('/api/links/bind', json=bind_payload)
        assert res_bind.status_code == 200
        assert res_bind.get_json()["status"] == "success"
        
        # Kiểm tra SQLite đã cập nhật bound_phone_hash
        conn = sqlite3.connect(temp_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT bound_phone_hash FROM shared_links WHERE link_id = ?", (link_id,))
        row = cursor.fetchone()
        assert row["bound_phone_hash"] == phone_hash
        conn.close()
        
        # Thử bind lại với SĐT khác (phải báo lỗi)
        phone2 = "0988888888"
        phone_hash2 = hashlib.sha256(phone2.encode('utf-8')).hexdigest()
        bind_payload2 = {
            "link_id": link_id,
            "phone_hash": phone_hash2
        }
        res_bind2 = client.post('/api/links/bind', json=bind_payload2)
        assert res_bind2.status_code == 400
        assert "được khóa" in res_bind2.get_json()["message"]

@patch('api.routes_links.get_sheets_client')
def test_revoke_link(mock_sheets, temp_db):
    """Kiểm tra API thu hồi link của Admin"""
    mock_sheets.return_value = MagicMock()
    
    import manager
    app = manager.app
    app.config['TESTING'] = True
    
    with patch('manager.DB_FILE', temp_db):
        client = app.test_client()
        
        # Tạo link sẵn trong DB
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO shared_links (link_id, customer_name, shared_house_ids, created_at, status)
            VALUES ('LNK-TEST-REVOKE', 'Khách B', 'SYS-100', '2026-07-12', 'Active')
        """)
        conn.commit()
        conn.close()
        
        # Gọi API thu hồi
        res = client.post('/api/links/revoke', json={"link_id": "LNK-TEST-REVOKE"})
        assert res.status_code == 200
        
        # Kiểm tra SQLite
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM shared_links WHERE link_id = 'LNK-TEST-REVOKE'")
        status = cursor.fetchone()[0]
        assert status == "Revoked"
        conn.close()

@patch('api.routes_links.get_sheets_client')
def test_blacklist_add_and_remove(mock_sheets, temp_db):
    """Kiểm tra API thêm và xóa SĐT chặn trong blacklist"""
    mock_sheets.return_value = MagicMock()
    
    import manager
    app = manager.app
    app.config['TESTING'] = True
    
    with patch('manager.DB_FILE', temp_db):
        client = app.test_client()
        
        # 1. Thêm SĐT vào blacklist
        phone = "0909999999"
        phone_hash = hashlib.sha256(phone.encode('utf-8')).hexdigest()
        
        res = client.post('/api/blacklist/add', json={"phone": phone, "reason": "Spam"})
        assert res.status_code == 200
        
        # Kiểm tra SQLite
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT status, reason FROM phone_blacklist WHERE phone_hash = ?", (phone_hash,))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "Active"
        assert row[1] == "Spam"
        conn.close()
        
        # 2. Xóa/Gỡ chặn SĐT
        res_remove = client.post('/api/blacklist/remove', json={"phone_hash": phone_hash})
        assert res_remove.status_code == 200
        
        # Kiểm tra SQLite
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM phone_blacklist WHERE phone_hash = ?", (phone_hash,))
        status = cursor.fetchone()[0]
        assert status == "Inactive"
        conn.close()
