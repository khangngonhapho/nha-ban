import sys
import os
import unittest
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes_pool import parse_price_float, parse_date_text, parse_db_datetime

class TestChangeDetection(unittest.TestCase):
    def test_parse_price_float(self):
        self.assertEqual(parse_price_float("15 tỷ"), 15.0)
        self.assertEqual(parse_price_float("13.5 tỷ"), 13.5)
        self.assertEqual(parse_price_float("13,5 tỷ"), 13.5)
        self.assertEqual(parse_price_float("tỷ 12"), 12.0)
        self.assertEqual(parse_price_float(""), 0.0)
        self.assertEqual(parse_price_float(None), 0.0)

    def test_parse_date_text(self):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        three_days_ago = today - datetime.timedelta(days=3)
        
        self.assertEqual(parse_date_text("2 giờ trước"), today)
        self.assertEqual(parse_date_text("30 phút trước"), today)
        self.assertEqual(parse_date_text("Hôm nay 10:15"), today)
        self.assertEqual(parse_date_text("Hôm qua 23:10"), yesterday)
        self.assertEqual(parse_date_text("3 ngày trước"), three_days_ago)
        
        self.assertEqual(parse_date_text("10/07/2026"), datetime.date(2026, 7, 10))
        self.assertEqual(parse_date_text("2026-07-09"), datetime.date(2026, 7, 9))
        self.assertIsNone(parse_date_text("không hợp lệ"))

    def test_parse_db_datetime(self):
        self.assertEqual(parse_db_datetime("2026-07-11T09:00:00Z"), datetime.date(2026, 7, 11))
        self.assertEqual(parse_db_datetime("11/07/2026 12:00:00"), datetime.date(2026, 7, 11))
        self.assertIsNone(parse_db_datetime("None"))
        self.assertIsNone(parse_db_datetime(""))

if __name__ == '__main__':
    unittest.main()
