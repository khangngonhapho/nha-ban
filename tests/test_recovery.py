import os
import sys
import json
import sqlite3
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pool_lego import init_db
from core.business_rules import recover_listing_from_raw_json

class TestListingRecovery:
    """Verify: recover_listing_from_raw_json() khôi phục chuẩn xác thông tin listings và hình ảnh."""

    def test_recover_listing_fields_and_images(self, tmp_path):
        db_path = str(tmp_path / "test_recovery.db")
        init_db(db_file=db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tk_id = "test-recovery-1"
        system_id = "SYS-20260712-999"
        ma_khang_ngo = "123-TEST"
        
        # Tạo dữ liệu giả lập có JSON_UI cũ chứa lịch sử giá
        old_json_ui = {
            "history": [{"price": "10 tỷ", "date": "01/07/2026"}],
            "bedrooms": "1"
        }
        
        # Dữ liệu raw_json_full thô từ Thiên Khôi
        raw_json_dict = {
            "id": tk_id,
            "code": "TK-999",
            "bedrooms": 3,
            "restrooms": 2,
            "area": 50,
            "actualArea": 55,
            "floors": 4,
            "wide": 4,
            "depth": 12,
            "offeringPrice": 9.5,
            "description": "Nhà đẹp hẻm xe hơi",
            "address": "123 Đường Test",
            "coordinate": {
                "latitude": 10.776,
                "longitude": 106.667
            },
            "criteria": [
                {"groupCode": "ROAD_TYPE", "name": "Hẻm xe hơi"},
                {"groupCode": "HOUSE_DIRECTION", "name": "Đông Nam"}
            ],
            "media": [
                {"type": "property_image", "url": "http://example.com/property1.jpg"},
                {"type": "property_image", "url": "http://example.com/property2.jpg"},
                {"type": "parcel_map", "url": "http://example.com/sodo.jpg"}
            ]
        }
        
        cursor.execute("""
            INSERT INTO listings (tk_id, status, System_ID, Ma_Khang_Ngo_ID, raw_json_full, JSON_UI, curated_config_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            tk_id,
            "raw_text",
            system_id,
            ma_khang_ngo,
            json.dumps(raw_json_dict, ensure_ascii=False),
            json.dumps(old_json_ui, ensure_ascii=False),
            "{}"
        ))
        conn.commit()
        
        # Chạy recovery
        res = recover_listing_from_raw_json(conn, tk_id, active_table="listings", update_type="all")
        assert res is True
        
        # Kiểm tra CSDL sau khôi phục
        row = cursor.execute("""
            SELECT So_phong_ngu, So_nha_ve_sinh, raw_images_tk_json, raw_sodo_tk_json, JSON_UI, curated_config_json, status 
            FROM listings WHERE tk_id = ?
        """, (tk_id,)).fetchone()
        
        assert row is not None
        so_phong_ngu, so_nha_ve_sinh, raw_images_tk_json, raw_sodo_tk_json, json_ui_str, curated_config_str, status = row
        
        # 1. Kiểm tra số phòng ngủ, nhà vệ sinh
        assert so_phong_ngu == "3"
        assert so_nha_ve_sinh == "2"
        
        # 2. Kiểm tra JSON_UI và bảo toàn history giá
        json_ui = json.loads(json_ui_str)
        assert json_ui["Criteria_Duong_truoc_nha"] == "Hẻm xe hơi"
        assert json_ui["latitude"] == "10.776"
        assert json_ui["longitude"] == "106.667"
        assert json_ui["history"] == [{"price": "10 tỷ", "date": "01/07/2026"}]
        
        # 3. Kiểm tra ảnh tk_json và sodo
        images_tk = json.loads(raw_images_tk_json)
        assert len(images_tk) == 3
        assert "http://example.com/property1.jpg" in images_tk
        assert "http://example.com/sodo.jpg" in images_tk
        
        sodo_tk = json.loads(raw_sodo_tk_json)
        assert len(sodo_tk) == 1
        assert sodo_tk[0] == "http://example.com/sodo.jpg"
        
        # 4. Kiểm tra listings_images vật lý
        cursor.execute("SELECT image_url, role, sequence_index FROM listings_images WHERE tk_id = ?", (tk_id,))
        img_rows = cursor.fetchall()
        assert len(img_rows) == 3
        
        roles = {r[0]: r[1] for r in img_rows}
        assert roles["http://example.com/sodo.jpg"] == "diagram"
        assert roles["http://example.com/property1.jpg"] == "facade"
        assert roles["http://example.com/property2.jpg"] == "interior"
        
        # 5. Vì ảnh R2 trống, status phải chuyển về raw_text để kích hoạt di cư ngầm
        assert status == "raw_text"
        
        conn.close()
