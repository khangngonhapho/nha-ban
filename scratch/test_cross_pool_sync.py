# -*- coding: utf-8 -*-
import unittest
import os
import sqlite3
import json
from unittest.mock import patch, MagicMock

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pool_lego

class TestCrossPoolSync(unittest.TestCase):
    def setUp(self):
        self.db1 = "test_raw_archive.db"
        self.db2 = "test_raw_archive_v2.db"
        
        # Clean up existing test databases
        for db in [self.db1, self.db2]:
            if os.path.exists(db):
                try:
                    os.remove(db)
                except Exception:
                    pass
                
    def tearDown(self):
        # Clean up test databases
        for db in [self.db1, self.db2]:
            if os.path.exists(db):
                try:
                    os.remove(db)
                except Exception:
                    pass
                
    def test_sync_p2_to_p1_and_anti_duplication(self):
        # Force Pool2 initialization on db2
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('builtins.open', unittest.mock.mock_open(read_data='{"active_pool_system": "Pool2"}')):
                pool_lego.init_db(self.db2)
                
        # Force Pool1 initialization on db1
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            pool_lego.init_db(self.db1)
            
        # Verify db schemas exist
        self.assertTrue(os.path.exists(self.db1))
        self.assertTrue(os.path.exists(self.db2))
        
        # Insert a listing in Pool 2
        conn2 = sqlite3.connect(self.db2)
        try:
            cursor2 = conn2.cursor()
            tk_id = "test-uuid-1234"
            system_id = "SYS-TEST-100"
            ma_hang = "TK-1234"
            
            # Insert raw listings
            cursor2.execute("""
                INSERT INTO listings_v2 (tk_id, status, System_ID, Ma_Hang, streetName, Ngo_So_nha, Quan, Phuong, Gia_chao, bedrooms, restrooms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (tk_id, "raw_text", system_id, ma_hang, "Nguyen Trai", "12/34", "Quan 1", "Ben Thanh", "10 tỷ", "3", "2"))
            
            # Insert custom listings overrides
            cursor2.execute("""
                INSERT INTO listings_custom_v2 (System_ID, Ma_Khang_Ngo, Gia_Public, Tieu_De_Public, So_Nha, Ten_Duong, Quan, Phuong)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (system_id, "test_ma_kn_id", "9.5 tỷ", "Bán nhà Nguyễn Trãi", "12/34", "Nguyen Trai", "Quan 1", "Ben Thanh"))
            
            # Insert images
            cursor2.execute("""
                INSERT INTO listings_images (tk_id, image_url, role, sequence_index, origin)
                VALUES (?, ?, ?, ?, ?)
            """, (tk_id, "http://test.com/img1.jpg", "interior", 0, "crawl"))
            cursor2.execute("""
                INSERT INTO listings_images (tk_id, image_url, role, sequence_index, origin)
                VALUES (?, ?, ?, ?, ?)
            """, (tk_id, "https://r2.dev/img2.jpg", "diagram", 1, "self"))
            conn2.commit()
        finally:
            conn2.close()
        
        # Sync Pool 2 -> Pool 1
        res = pool_lego.sync_between_databases(self.db2, self.db1, tk_id=tk_id)
        self.assertEqual(res["status"], "success")
        
        # Check that it exists in Pool 1
        p1_dict = {}
        conn1 = sqlite3.connect(self.db1)
        conn1.row_factory = sqlite3.Row
        try:
            cursor1 = conn1.cursor()
            p1_row = cursor1.execute("SELECT * FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
            if p1_row:
                p1_dict = dict(p1_row)
        finally:
            conn1.close()
            
        self.assertIsNotNone(p1_row)
        self.assertEqual(p1_dict.get("System_ID"), system_id)
        self.assertEqual(p1_dict.get("Gia_Public"), "9.5 tỷ")
        self.assertEqual(p1_dict.get("Ma_Khang_Ngo_ID"), "test_ma_kn_id")
        self.assertEqual(p1_dict.get("Anh_1"), "http://test.com/img1.jpg")
        self.assertEqual(p1_dict.get("So_do_thua_dat_1"), "https://r2.dev/img2.jpg")
        
        # Modify custom in Pool 2 and sync again to test Anti-duplication update
        conn2 = sqlite3.connect(self.db2)
        try:
            cursor2 = conn2.cursor()
            cursor2.execute("UPDATE listings_custom_v2 SET Gia_Public = '9 tỷ' WHERE System_ID = ?", (system_id,))
            conn2.commit()
        finally:
            conn2.close()
            
        # Sync again
        res = pool_lego.sync_between_databases(self.db2, self.db1, tk_id=tk_id)
        self.assertEqual(res["status"], "success")
        
        # Check that Pool 1 was updated, not duplicated
        p1_row_updated_dict = {}
        count = 0
        conn1 = sqlite3.connect(self.db1)
        conn1.row_factory = sqlite3.Row
        try:
            cursor1 = conn1.cursor()
            count = cursor1.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
            p1_row_updated = cursor1.execute("SELECT * FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
            if p1_row_updated:
                p1_row_updated_dict = dict(p1_row_updated)
        finally:
            conn1.close()
            
        self.assertEqual(count, 1) # Still 1 row
        self.assertEqual(p1_row_updated_dict.get("Gia_Public"), "9 tỷ")

    def test_sync_p1_to_p2_adhoc_by_address(self):
        # Force Pool1 schema initialization on db1
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            pool_lego.init_db(self.db1)
        
        # Force Pool2 schema initialization on db2
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('builtins.open', unittest.mock.mock_open(read_data='{"active_pool_system": "Pool2"}')):
                pool_lego.init_db(self.db2)
                
        # Insert a listing in Pool 1
        conn1 = sqlite3.connect(self.db1)
        try:
            cursor1 = conn1.cursor()
            old_tk_id = "old-tk-id-999"
            system_id = "SYS-OLD-999"
            ma_kn_id = "12IHAIRT" # Ma Khang Ngo computed from 12 Nguyễn Trãi
            
            cursor1.execute("""
                INSERT INTO listings (tk_id, System_ID, Ma_Khang_Ngo_ID, Ngo_So_nha, Duong, Quan, Phuong, Gia_chao, Gia_Public, Anh_1, So_do_thua_dat_1, Hinh_Mat_Tien)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (old_tk_id, system_id, ma_kn_id, "12", "Nguyen Trai", "Quan 1", "Ben Thanh", "5 tỷ", "4.8 tỷ", "http://test.com/anh1.jpg", "https://cloudinary.com/sodo.jpg", "https://r2.dev/mattien.jpg"))
            conn1.commit()
        finally:
            conn1.close()
            
        # Sync Pool 1 -> Pool 2 by address (Ad-hoc)
        res = pool_lego.sync_between_databases(self.db1, self.db2, so_nha="12", duong="Nguyen Trai")
        self.assertEqual(res["status"], "success")
        
        # Verify legacy listing in Pool 2
        new_tk_id = f"LEGACY-{old_tk_id}"
        v2_dict = {}
        custom_dict = {}
        img_list = []
        
        conn2 = sqlite3.connect(self.db2)
        conn2.row_factory = sqlite3.Row
        try:
            cursor2 = conn2.cursor()
            v2_row = cursor2.execute("SELECT * FROM listings_v2 WHERE tk_id = ?", (new_tk_id,)).fetchone()
            if v2_row:
                v2_dict = dict(v2_row)
                
            custom_row = cursor2.execute("SELECT * FROM listings_custom_v2 WHERE System_ID = ?", (system_id,)).fetchone()
            if custom_row:
                custom_dict = dict(custom_row)
                
            img_rows = cursor2.execute("SELECT * FROM listings_images WHERE tk_id = ? ORDER BY sequence_index ASC", (new_tk_id,)).fetchall()
            img_list = [dict(r) for r in img_rows]
        finally:
            conn2.close()
            
        self.assertTrue(bool(v2_dict))
        self.assertEqual(v2_dict["status"], "published_legacy")
        self.assertEqual(v2_dict["System_ID"], system_id)
        
        self.assertTrue(bool(custom_dict))
        self.assertEqual(custom_dict["Gia_Public"], "4.8 tỷ")
        self.assertEqual(custom_dict["Ma_Khang_Ngo"], ma_kn_id)
        
        self.assertEqual(len(img_list), 3)
        
        # Check image values, roles and origins
        mattien_img = [img for img in img_list if "mattien.jpg" in img["image_url"]][0]
        self.assertEqual(mattien_img["role"], "facade")
        self.assertEqual(mattien_img["origin"], "self")
        self.assertEqual(mattien_img["cloudinary_url"], "https://r2.dev/mattien.jpg")
        
        sodo_img = [img for img in img_list if "sodo.jpg" in img["image_url"]][0]
        self.assertEqual(sodo_img["role"], "diagram")
        self.assertEqual(sodo_img["origin"], "self")
        
        anh1_img = [img for img in img_list if "anh1.jpg" in img["image_url"]][0]
        self.assertEqual(anh1_img["role"], "interior")
        self.assertEqual(anh1_img["origin"], "crawl")
        self.assertEqual(anh1_img["cloudinary_url"], "")

    @patch('requests.get')
    def test_recrawl_all_listings_and_diff_tracking(self, mock_requests_get):
        # Initialize schema Pool2 on db2
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('builtins.open', unittest.mock.mock_open(read_data='{"active_pool_system": "Pool2"}')):
                pool_lego.init_db(self.db2)
                
        # Insert a listing in Pool 2
        conn2 = sqlite3.connect(self.db2)
        try:
            cursor2 = conn2.cursor()
            tk_id = "test-recrawl-uuid"
            system_id = "SYS-RECRAWL-100"
            
            cursor2.execute("""
                INSERT INTO listings_v2 (tk_id, status, System_ID, Ma_Hang, Gia_chao, bedrooms, restrooms, status_nguon)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (tk_id, "raw_text", system_id, "TK-99", "10 tỷ", "3", "2", "Đang bán"))
            conn2.commit()
        finally:
            conn2.close()
            
        # Write temporary cookie file
        with open("thienkhoi_cookie.txt", "w", encoding="utf-8") as f:
            f.write("TKG_accessToken=dummy_token; TKG_refreshToken=dummy_refresh")
            
        # Mock requests.get response for detail API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "code": "TK-99",
                "offeringPrice": 9.5,  # Changed from 10 to 9.5
                "bedrooms": 4,         # Changed from 3 to 4
                "restrooms": 2,        # Unchanged
                "status": "Dừng bán", # Changed from Đang bán to Dừng bán
                "description": "Mô tả mới",
                "area": 50,
                "floors": 4,
                "wide": 4,
                "depth": 12.5,
                "direction": "Đông",
                "minimumRoadWidth": 4,
                "media": []
            }
        }
        mock_requests_get.return_value = mock_response
        
        # Run recrawl passing self.db2 explicitly
        with patch('fetcher.parse_criteria_groups') as mock_parse_crit:
            mock_parse_crit.return_value = {}
            res = pool_lego.recrawl_all_listings(db_file=self.db2)
            self.assertEqual(res["status"], "success")
            
        # Check diff in db2
        d = {}
        conn2 = sqlite3.connect(self.db2)
        conn2.row_factory = sqlite3.Row
        try:
            cursor2 = conn2.cursor()
            row = cursor2.execute("SELECT * FROM listings_v2 WHERE tk_id = ?", (tk_id,)).fetchone()
            if row:
                d = dict(row)
        finally:
            conn2.close()
            
        self.assertTrue(bool(d))
        self.assertIsNotNone(d.get("pending_diff_json"))
        diff_data = json.loads(d["pending_diff_json"])
        
        # Verify diff contents
        changes = diff_data["gia_tri_thay_doi"]
        self.assertIn("Gia_chao", changes)
        self.assertEqual(changes["Gia_chao"]["old"], "10 tỷ")
        self.assertEqual(changes["Gia_chao"]["new"], "9.5")
        
        self.assertIn("bedrooms", changes)
        self.assertEqual(changes["bedrooms"]["old"], "3")
        self.assertEqual(changes["bedrooms"]["new"], "4")
        
        self.assertIn("status_nguon", changes)
        self.assertEqual(changes["status_nguon"]["old"], "Đang bán")
        self.assertEqual(changes["status_nguon"]["new"], "Dừng bán")
        
        self.assertNotIn("restrooms", changes)
        
        # Clean up thienkhoi_cookie.txt
        if os.path.exists("thienkhoi_cookie.txt"):
            try:
                os.remove("thienkhoi_cookie.txt")
            except Exception:
                pass

if __name__ == '__main__':
    unittest.main()
