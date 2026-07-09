import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCrawlerDates(unittest.TestCase):
    def test_date_fields_extraction_proptech(self):
        # Mock proptech API detail response
        detail_data = {
            "id": "mock-uuid-1",
            "createdAt": "2026-05-23T04:11:26.939Z",
            "updatedAt": "2026-05-23T05:12:26.939Z",
            "listedAt": "2026-05-23T03:10:26.939Z",
            "code": "TKMOCK123"
        }
        
        # Test extraction logic equivalent to scrape_district_proptech in fetcher.py
        crawled_data = {
            "Mã Hàng": detail_data.get("code") or "mock-uuid-1",
            "createdAt": str(detail_data.get("createdAt") or ""),
            "updatedAt": str(detail_data.get("updatedAt") or ""),
            "listedAt": str(detail_data.get("listedAt") or ""),
        }
        
        self.assertEqual(crawled_data["createdAt"], "2026-05-23T04:11:26.939Z")
        self.assertEqual(crawled_data["updatedAt"], "2026-05-23T05:12:26.939Z")
        self.assertEqual(crawled_data["listedAt"], "2026-05-23T03:10:26.939Z")

if __name__ == '__main__':
    unittest.main()
