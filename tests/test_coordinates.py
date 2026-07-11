import sys
import os
import unittest
import sqlite3
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pool_lego import extract_json_ui_data, init_db, CUSTOM_HEADERS
from core.config import read_settings

class TestCoordinatesFeature(unittest.TestCase):
    def test_extract_json_ui_data_from_root(self):
        # Case 1: latitude and longitude are in the root of the raw dict
        raw_data = {
            "id": "test-uuid-1",
            "latitude": "10.762622",
            "longitude": "106.660172",
            "criteria": []
        }
        res = extract_json_ui_data(raw_data)
        self.assertEqual(res.get("latitude"), "10.762622")
        self.assertEqual(res.get("longitude"), "106.660172")

    def test_extract_json_ui_data_from_coordinate_subobject(self):
        # Case 2: latitude and longitude are inside a 'coordinate' sub-object
        raw_data = {
            "id": "test-uuid-2",
            "coordinate": {
                "latitude": 10.762622,
                "longitude": 106.660172
            },
            "criteria": []
        }
        res = extract_json_ui_data(raw_data)
        # Should convert float to string
        self.assertEqual(res.get("latitude"), "10.762622")
        self.assertEqual(res.get("longitude"), "106.660172")

    def test_database_schema_has_coordinates(self):
        # Check that CUSTOM_HEADERS contains coordinate fields
        self.assertIn("latitude", CUSTOM_HEADERS)
        self.assertIn("longitude", CUSTOM_HEADERS)

        # Initialize db in a temporary file and check listings_custom_v2 schema
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            # force pool2 mode settings mock if needed, but since listings_custom_v2 is created in init_db in Pool2 mode
            # let's mock read_settings or just check listings_custom_v2 columns
            # We will force init_db to create listings_custom_v2 by setting the active system to Pool2
            
            # Save original config
            orig_read_settings = sys.modules.get('core.config').read_settings
            
            # Mock read_settings
            sys.modules['core.config'].read_settings = lambda *args, **kwargs: {
                "active_pool_system": "Pool2",
                "json_ui_fields": ["latitude", "longitude"]
            }
            
            init_db(db_path)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(listings_custom_v2)")
            cols = [row[1] for row in cursor.fetchall()]
            
            self.assertIn("latitude", cols)
            self.assertIn("longitude", cols)
            
            conn.close()
            # Restore read_settings
            sys.modules['core.config'].read_settings = orig_read_settings
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

if __name__ == '__main__':
    unittest.main()
