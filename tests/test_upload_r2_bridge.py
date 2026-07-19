import sys
import os
import json
import base64
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manager import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_upload_r2_bridge_missing_fields(client):
    """Kiểm tra báo lỗi khi thiếu tham số đầu vào."""
    response = client.post('/api/upload-r2', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_upload_r2_bridge_invalid_base64(client):
    """Kiểm tra báo lỗi khi chuỗi base64 không hợp lệ."""
    response = client.post('/api/upload-r2', json={
        "file": "not-a-valid-base64-string!!!",
        "filename": "test.jpg",
        "type": "interior"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

@patch('manager.upload_image_to_r2')
@patch('manager.compress_image')
def test_upload_r2_bridge_success_local(mock_compress, mock_upload, client):
    """Kiểm tra tải ảnh lên thành công (mock R2 và nén)."""
    mock_compress.return_value = b"compressed-data"
    mock_upload.return_value = "https://r2.dev/BDS-KhangNgo-v3/123/SYS-test.jpg"
    
    # 1x1 transparent GIF base64
    gif_b64 = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
    
    response = client.post('/api/upload-r2', json={
        "file": gif_b64,
        "filename": "test.jpg",
        "type": "interior"
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("status") == "success" or "url" in data
    assert "url" in data
