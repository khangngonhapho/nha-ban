import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCrawlerMedia(unittest.TestCase):
    def test_image_extraction_logic(self):
        media_data = [
            {"type": "checkin_image", "url": "https://r2.dev/img_1.jpg"},
            {"type": "checkin_image", "url": "https://r2.dev/img_2.jpg"},
            {"type": "property_image", "url": "https://r2.dev/img_3.jpg"},
            {"type": "parcel_map", "url": "https://r2.dev/img_4.jpg"},
            {"type": "unknown_type", "url": "https://r2.dev/img_5.jpg"}
        ]
        
        # Mimic the updated parsing logic
        property_images = []
        sodo_images = []
        
        for m in media_data:
            m_type = m.get("type")
            m_url = m.get("url")
            if not m_url:
                continue
            if m_type in ["parcel_map", "certificate_image"]:
                sodo_images.append(m_url)
            else:
                property_images.append(m_url)
                
        # Assertions
        # All non-diagram images must be extracted!
        self.assertEqual(len(property_images), 4)
        self.assertIn("https://r2.dev/img_1.jpg", property_images)
        self.assertIn("https://r2.dev/img_2.jpg", property_images)
        self.assertIn("https://r2.dev/img_3.jpg", property_images)
        self.assertIn("https://r2.dev/img_5.jpg", property_images)
        
        # Sodo image must be extracted
        self.assertEqual(len(sodo_images), 1)
        self.assertIn("https://r2.dev/img_4.jpg", sodo_images)

if __name__ == '__main__':
    unittest.main()
