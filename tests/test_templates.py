# -*- coding: utf-8 -*-
"""
Unit tests for MOD-05 HTML template rendering and components.
"""

import pytest
from query_helper import generate_html_viewer
from templates.components.header import render_header
from templates.components.criteria_grid import render_criteria_grid
from templates.components.image_grid import render_image_grid
from templates.components.specs_table import render_specs_table, render_contact_table
from templates.components.detail_view import render_detail_view

@pytest.fixture
def dummy_listing():
    return {
        "tk_id": "TEST-123",
        "System_ID": "SYS-TEST",
        "Ma_Hang": "MH-12345",
        "Ngo_So_nha": "123",
        "Duong": "Nguyen Trai",
        "Phuong": "Ben Thanh",
        "Quan": "Quan 1",
        "Gia_chao": "15",
        "DT_Thuc_te": "100",
        "DT_Tren_so": "95",
        "So_Tang": "3",
        "Mat_Tien": "5",
        "Chieu_dai": "20",
        "Huong": "Nam",
        "minimumRoadWidth": "6",
        "Ten_Chu_Nha": "Nguyen Van A",
        "Dien_thoai_1": "0901234567",
        "Ten_Dau_Chu": "Dau Chu B",
        "Dien_thoai_Dau_Chu": "0987654321",
        "Mo_ta_chi_tiet": "Nha dep, mat tien rong.",
        "Noi_dung_chinh": "Gia tot, nha dep.",
        "Link_Goc": "https://example.com/hang/123",
        "Criteria_Duong_truoc_nha": "O to tranh",
        "Criteria_Loai_ngo": "Ngo thong"
    }

@pytest.fixture
def dummy_images():
    return {
        "diagram": ["https://example.com/diagram1.jpg"],
        "facade": ["https://example.com/facade1.jpg"],
        "alley": ["https://example.com/alley1.jpg"],
        "interior": ["https://example.com/int1.jpg", "https://example.com/int2.jpg"],
        "cover": []
    }

def test_generate_html_viewer_basic(dummy_listing, dummy_images):
    html = generate_html_viewer(dummy_listing, dummy_images, "listings_v2")
    
    # Structural and content assertions
    assert "MH-12345" in html
    assert "SYS-TEST" in html
    assert "123 Nguyen Trai" in html
    assert "15 Tỷ" in html or "15" in html
    assert "100" in html
    assert "Nguyen Van A" in html
    assert "0901234567" in html
    assert "Dau Chu B" in html
    assert "0987654321" in html
    assert "Nha dep, mat tien rong." in html
    assert "Gia tot, nha dep." in html
    assert "https://example.com/hang/123" in html
    assert "O to tranh" in html
    assert "Ngo thong" in html
    assert "https://example.com/diagram1.jpg" in html
    assert "https://example.com/facade1.jpg" in html
    assert "https://example.com/alley1.jpg" in html
    assert "https://example.com/int1.jpg" in html
    assert "https://example.com/int2.jpg" in html
    assert "listings_v2" in html or "LISTINGS_V2" in html
    assert "<!DOCTYPE html>" in html
    assert "Outfit" in html

def test_render_header(dummy_listing):
    html = render_header(dummy_listing, "123 Nguyen Trai", "listings_v2")
    assert "MH-12345" in html
    assert "123 Nguyen Trai" in html
    assert "LISTINGS_V2" in html

def test_render_criteria_grid(dummy_listing):
    html = render_criteria_grid(dummy_listing)
    assert "Tiêu chí phân loại" in html
    assert "O to tranh" in html
    assert "Ngo thong" in html

def test_render_image_grid(dummy_images):
    html = render_image_grid(dummy_images)
    assert "Sơ đồ thửa đất" in html
    assert "Hình ảnh Mặt Tiền" in html
    assert "Hình ảnh Hẻm trước nhà" in html
    assert "Hình ảnh Nội thất" in html
    assert "https://example.com/diagram1.jpg" in html
    assert "https://example.com/facade1.jpg" in html
    assert "https://example.com/alley1.jpg" in html
    assert "https://example.com/int1.jpg" in html
    assert "https://example.com/int2.jpg" in html

def test_render_specs_table(dummy_listing):
    html = render_specs_table(dummy_listing)
    assert "Thông số kỹ thuật" in html
    assert "15 Tỷ" in html or "15" in html
    assert "100" in html
    assert "3 Tầng" in html

def test_render_contact_table(dummy_listing):
    html = render_contact_table(dummy_listing)
    assert "Thông tin liên hệ" in html
    assert "Nguyen Van A" in html
    assert "0901234567" in html
    assert "Dau Chu B" in html
    assert "0987654321" in html

def test_render_detail_view_equivalence(dummy_listing, dummy_images):
    html = render_detail_view(dummy_listing, dummy_images, "listings_v2")
    # Verify it matches the original output structure
    assert "MH-12345" in html
    assert "SYS-TEST" in html
    assert "123 Nguyen Trai" in html
    assert "15 Tỷ" in html or "15" in html
    assert "100" in html
    assert "Nguyen Van A" in html
    assert "0901234567" in html
    assert "Dau Chu B" in html
    assert "0987654321" in html
    assert "Nha dep, mat tien rong." in html
    assert "Gia tot, nha dep." in html
    assert "https://example.com/hang/123" in html
    assert "O to tranh" in html
    assert "Ngo thong" in html
    assert "https://example.com/diagram1.jpg" in html
    assert "https://example.com/facade1.jpg" in html
    assert "https://example.com/alley1.jpg" in html
    assert "https://example.com/int1.jpg" in html
    assert "https://example.com/int2.jpg" in html
    assert "listings_v2" in html or "LISTINGS_V2" in html
    assert "<!DOCTYPE html>" in html
    assert "Outfit" in html
