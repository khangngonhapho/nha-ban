# -*- coding: utf-8 -*-
import os
import sys
import tempfile
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fetcher
import manager
from core.business_rules import gen_id_khang_ngo_python

def test_rule1_naming_conventions():
    """Kiểm tra Rule 1 chuẩn hóa tên đường đặc biệt (CMT8 -> TTMC, 3/2 -> HTB, 7SD)"""
    id_cmt8 = gen_id_khang_ngo_python("123", "Cách Mạng Tháng 8", "Quận 3")
    assert "TTMC" in id_cmt8

    id_bth = gen_id_khang_ngo_python("456", "3/2", "Quận 10")
    assert "HTB" in id_bth

    id_ds7 = gen_id_khang_ngo_python("789", "Đường số 7", "Quận 6")
    assert "7SD" in id_ds7

@patch("requests.get")
def test_scrape_district_proptech_ward_filter(mock_get):
    """Kiểm tra scrape_district_proptech nhận filter_ward và thêm param ward/ward_name vào api_params"""
    list_res = MagicMock()
    list_res.status_code = 200
    list_res.json.return_value = {
        "data": {
            "data": [
                {
                    "id": "mock-prop-1",
                    "code": "TK111",
                    "district": {"name": "Quận 3", "provinceName": "TP Hồ Chí Minh"},
                    "ward": {"name": "Phường 15"},
                    "streetName": "Cách Mạng Tháng 8",
                    "address": "1168",
                    "area": 50,
                    "actualArea": 50,
                    "floors": 3,
                    "wide": 4,
                    "depth": 12.5,
                    "offeringPrice": 10.5,
                    "description": "Mô tả test",
                    "criteria": [],
                    "media": []
                }
            ]
        }
    }

    detail_res = MagicMock()
    detail_res.status_code = 200
    detail_res.json.return_value = {
        "data": {
            "id": "mock-prop-1",
            "code": "TK111",
            "district": {"name": "Quận 3", "provinceName": "TP Hồ Chí Minh"},
            "ward": {"name": "Phường 15"},
            "streetName": "Cách Mạng Tháng 8",
            "address": "1168",
            "area": 50,
            "actualArea": 50,
            "floors": 3,
            "wide": 4,
            "depth": 12.5,
            "offeringPrice": 10.5,
            "description": "Mô tả test",
            "criteria": [],
            "media": []
        }
    }
    mock_get.side_effect = [list_res, detail_res]

    old_min = fetcher.DELAY_HOUSE_MIN
    old_max = fetcher.DELAY_HOUSE_MAX
    fetcher.DELAY_HOUSE_MIN = 0
    fetcher.DELAY_HOUSE_MAX = 0

    try:
        base_url = "https://proptech.thienkhoi.com/warehouse/sources?district=Qu%E1%BA%ADn+3"
        fetcher.scrape_district_proptech(
            base_url,
            session_cookie="mock_access_token=token123",
            limit=1,
            filter_district="Quận 3",
            filter_ward="Phường 15"
        )
    finally:
        fetcher.DELAY_HOUSE_MIN = old_min
        fetcher.DELAY_HOUSE_MAX = old_max

    # Inspect requests.get call arguments
    assert mock_get.called
    args, kwargs = mock_get.call_args_list[0]
    api_params = kwargs.get("params", {})
    assert api_params.get("ward") == "Phường 15"
    assert api_params.get("ward_name") == "Phường 15"

@patch("fetcher.scrape_district_proptech")
def test_scrape_keyword_support_ward(mock_scrape_proptech):
    """Kiểm tra scrape_keyword hỗ trợ tham số filter_ward / ward_name"""
    fetcher.scrape_keyword(
        keyword="Cách Mạng Tháng 8",
        session_cookie="mock_cookie",
        limit=5,
        filter_district="Quận 3",
        filter_ward="Phường 15"
    )

    assert mock_scrape_proptech.called
    kwargs = mock_scrape_proptech.call_args.kwargs
    assert kwargs.get("filter_ward") == "Phường 15"
    assert "keyword=C%C3%A1ch+M%E1%BA%A1ng+Th%C3%A1ng+8" in mock_scrape_proptech.call_args.args[0] or "keyword=C" in mock_scrape_proptech.call_args.args[0]

def test_mock_save_only_cookie_endpoint():
    """Kiểm tra endpoint /api/crawl với url == 'MOCK_SAVE_ONLY' lưu cookie file mượt mà"""
    manager.app.config['TESTING'] = True
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
        temp_cookie_file = tf.name

    old_cookie_file = manager.COOKIE_FILE
    try:
        manager.COOKIE_FILE = temp_cookie_file
        with manager.app.test_client() as client:
            res = client.post("/api/crawl", json={
                "url": "MOCK_SAVE_ONLY",
                "cookie": "mock-new-cookie-content-999"
            })
            assert res.status_code == 200
            json_resp = res.get_json()
            assert json_resp["status"] == "success"

            with open(temp_cookie_file, "r", encoding="utf-8") as f:
                saved_content = f.read().strip()
            assert saved_content == "mock-new-cookie-content-999"
    finally:
        manager.COOKIE_FILE = old_cookie_file
        if os.path.exists(temp_cookie_file):
            try:
                os.remove(temp_cookie_file)
            except Exception:
                pass
