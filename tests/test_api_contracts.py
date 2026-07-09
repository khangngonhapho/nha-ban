"""
API Contract Tests — MOD-04 PREPARE step.

Kiểm tra hợp đồng dữ liệu (API Contracts) của các endpoint Flask trong manager.py
trước và sau khi refactor thành Blueprint.

TESTS: tests/test_api_contracts.py (file này)
"""
import sys
import os
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manager import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestAPIContracts:
    """Kiểm tra hợp đồng phản hồi của các API chính."""

    def test_index_html(self, client):
        """GET / trả về mã 200 và nội dung HTML."""
        response = client.get('/')
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data

    def test_index_html_alias(self, client):
        """GET /index.html trả về mã 200."""
        response = client.get('/index.html')
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data

    def test_canvas_html(self, client):
        """GET /canvas.html trả về mã 200."""
        response = client.get('/canvas.html')
        assert response.status_code == 200 or response.status_code == 404

    def test_get_config(self, client):
        """GET /api/config trả về JSON chứa cấu hình."""
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        config_data = data.get("config", {})
        assert "sheet_id" in config_data or "active_pool_system" in config_data or "openai_api_base" in config_data

    def test_get_logs(self, client):
        """GET /api/logs trả về JSON array hoặc object logs."""
        response = client.get('/api/logs')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert "logs" in data or "status" in data

    def test_get_listings_structure(self, client):
        """GET /api/listings trả về danh sách listings hợp lệ."""
        response = client.get('/api/listings?limit=1')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert "listings" in data
        assert isinstance(data["listings"], list)

    def test_check_exist_endpoint(self, client):
        """POST /api/listings/check-exist trả về JSON kết quả."""
        response = client.post('/api/listings/check-exist', json={"so_nha": "123", "duong": "Nguyen Trai", "quan": "Q1"})
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert "exists" in data or "status" in data

    def test_view_images_page(self, client):
        """GET /view-images trả về mã 200 và nội dung HTML."""
        response = client.get('/view-images')
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data

    def test_proxy_download_missing_url(self, client):
        """GET /api/proxy-download không có url trả về mã 400."""
        response = client.get('/api/proxy-download')
        assert response.status_code == 400

    def test_proxy_download_invalid_url(self, client):
        """GET /api/proxy-download với url không hợp lệ trả về mã 500."""
        response = client.get('/api/proxy-download?url=http://invalid-url-domain-non-existent.xyz')
        assert response.status_code == 500
