# -*- coding: utf-8 -*-
"""
Unit tests for US-157: Image Comparison 3 Partitions & Input Viewer.
"""

import os
import json
import sqlite3
import pytest
from api.routes_images import normalize_street_name, normalize_house_number, parse_image_json_to_list


def test_normalize_street_name():
    assert normalize_street_name("1168/42 CMT8") == "1168/42 TTMC"
    assert normalize_street_name("489/24/39B Cách Mạng Tháng 8") == "489/24/39B TTMC"
    assert normalize_street_name("123 Đường 3/2") == "123 Đường HTB"
    assert normalize_street_name("Đường 3 Tháng 2") == "Đường HTB"
    assert normalize_street_name("Hẻm Đường số 7") == "Hẻm 7SD"


def test_normalize_house_number():
    assert normalize_house_number("1168.42+44") == "1168.42"
    assert normalize_house_number("489/24/39B") == "489/24/39B"
    assert normalize_house_number("12.34+56+78") == "12.34"


def test_parse_image_json_to_list():
    json_str = json.dumps([
        {"r2_url": "https://pub-r2.dev/img1.jpg", "role": "facade", "sequence_index": 0, "origin": "crawl", "is_hidden": 0},
        {"r2_url": "https://pub-r2.dev/img2.jpg", "role": "diagram", "sequence_index": 1, "origin": "self", "is_hidden": 1}
    ])
    
    parsed = parse_image_json_to_list(json_str)
    assert len(parsed) == 2
    assert parsed[0]["role"] == "facade"
    assert parsed[0]["url"] == "https://pub-r2.dev/img1.jpg"
    assert parsed[1]["role"] == "diagram"
    assert parsed[1]["is_hidden"] == 1

    # Test raw text URL list fallback
    raw_urls_text = "https://pub-r2.dev/img1.jpg\thttps://pub-r2.dev/img2.jpg\nhttps://pub-r2.dev/img3.jpg"
    parsed_raw = parse_image_json_to_list(raw_urls_text)
    assert len(parsed_raw) == 3
    assert parsed_raw[0]["url"] == "https://pub-r2.dev/img1.jpg"
    assert parsed_raw[2]["url"] == "https://pub-r2.dev/img3.jpg"


def test_compare_images_api(tmp_path):
    import manager
    app = manager.app
    app.testing = True
    client = app.test_client()

    # Test GET /api/databases
    resp_db = client.get('/api/databases')
    assert resp_db.status_code == 200
    data_db = resp_db.get_json()
    assert data_db["status"] == "success"
    assert isinstance(data_db["databases"], list)

    # Test GET /api/compare-images validation
    resp_invalid = client.get('/api/compare-images')
    assert resp_invalid.status_code == 400


def test_compare_images_full_flow(tmp_path):
    import manager
    app = manager.app
    app.testing = True
    client = app.test_client()

    # Create dummy database in project root
    db_file_name = "test_us157_sample.db"
    db_file_path = os.path.join(manager.PROJECT_ROOT, db_file_name)
    
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE listings_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tk_id TEXT,
            System_ID TEXT,
            Ma_Khang_Ngo_ID TEXT,
            Ngo_So_nha TEXT,
            Duong TEXT,
            Quan TEXT,
            images_admin_json TEXT,
            images_public_json TEXT
        )
    """)
    
    admin_imgs = json.dumps([
        {"r2_url": "https://pub-r2.dev/img1.jpg", "role": "facade", "sequence_index": 0, "origin": "crawl", "is_hidden": 0},
        {"r2_url": "https://pub-r2.dev/img2.jpg", "role": "interior", "sequence_index": 1, "origin": "self", "is_hidden": 0}
    ])
    pub_imgs = json.dumps(["https://pub-r2.dev/img2.jpg"])

    cursor.execute("""
        INSERT INTO listings_v2 (tk_id, System_ID, Ma_Khang_Ngo_ID, Ngo_So_nha, Duong, Quan, images_admin_json, images_public_json)
        VALUES ('c70a9eef', 'SYS-20260723-001', 'HWZOITITTN', '1168.42+44', 'Cách Mạng Tháng 8', 'Quận Tân Bình', ?, ?)
    """, (admin_imgs, pub_imgs))
    conn.commit()
    conn.close()

    try:
        # Search by address using real street name & CMT8 alias
        url = f"/api/compare-images?query=1168.42+44 CMT8&db_file={db_file_name}"
        resp = client.get(url)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert data["house_info"]["system_id"] == "SYS-20260723-001"
        assert len(data["partition_1_sqlite"]) == 2
        assert data["partition_1_sqlite"][0]["role"] == "facade"
        assert "partition_4_pool_crawl" in data
        assert "partition_5_pool_self" in data
        assert isinstance(data["partition_4_pool_crawl"]["images"], list)
        assert isinstance(data["partition_5_pool_self"]["images"], list)
    finally:
        if os.path.exists(db_file_path):
            try:
                os.remove(db_file_path)
            except Exception:
                pass
