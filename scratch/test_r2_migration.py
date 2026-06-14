import os
import sys
import sqlite3
import unittest

# Thêm thư mục dự án vào sys.path để import pool_lego
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pool_lego

class TestR2Migration(unittest.TestCase):
    def setUp(self):
        self.db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_temp_migration.db"))
        self.cleanup()

    def tearDown(self):
        self.cleanup()

    def cleanup(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_auto_migration_renames_column(self):
        # 1. Khởi tạo một cơ sở dữ liệu giả lập có bảng listings_images theo cấu trúc cũ
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tạo bảng listings_images với cột cũ cloudinary_url
        cursor.execute("""
        CREATE TABLE listings_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tk_id TEXT,
            image_url TEXT,
            cloudinary_url TEXT,
            role TEXT,
            sequence_index INTEGER,
            edited_by TEXT,
            origin TEXT DEFAULT 'crawl'
        )
        """)
        
        # Chèn dữ liệu mẫu
        sample_url_cloudinary = "https://res.cloudinary.com/deru9p712/image/upload/v1779916713/BDS-KhangNgo/fihx7t/img1.jpg"
        sample_url_r2 = "https://pub-e92603c36c8d4789917d05d1eba12a7e.r2.dev/BDS-KhangNgo/fihx7t/img2.jpg"
        
        # Dòng 1: Chứa link Cloudinary cũ ở cột cloudinary_url
        cursor.execute("""
        INSERT INTO listings_images (tk_id, image_url, cloudinary_url, role, origin)
        VALUES (?, ?, ?, ?, ?)
        """, ("TK-MIGRATION-TEST-1", "http://original.com/1.jpg", sample_url_cloudinary, "interior", "crawl"))
        
        # Dòng 2: Chứa link R2 (được di cư ở US-090 nhưng vẫn nằm ở cột cloudinary_url cũ)
        cursor.execute("""
        INSERT INTO listings_images (tk_id, image_url, cloudinary_url, role, origin)
        VALUES (?, ?, ?, ?, ?)
        """, ("TK-MIGRATION-TEST-2", "http://original.com/2.jpg", sample_url_r2, "diagram", "self"))
        
        conn.commit()
        conn.close()
        
        # 2. Khởi chạy hàm init_db() của hệ thống để kích hoạt bộ di trú tự động
        pool_lego.init_db(self.db_path)
        
        # 3. Kết nối lại và kiểm tra schema mới
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(listings_images)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Xác minh cột cloudinary_url đã bị xóa/đổi tên
        self.assertNotIn("cloudinary_url", columns, "Cột cloudinary_url vẫn tồn tại trong bảng listings_images!")
        
        # Xác minh cột r2_url mới đã xuất hiện
        self.assertIn("r2_url", columns, "Cột r2_url không được tạo ra sau khi di trú!")
        
        # 4. Xác minh dữ liệu được bảo toàn nguyên vẹn tại cột r2_url mới
        cursor.execute("SELECT tk_id, image_url, r2_url, role, origin FROM listings_images ORDER BY tk_id")
        rows = cursor.fetchall()
        
        self.assertEqual(len(rows), 2, "Số bản ghi hình ảnh bị thay đổi sau di trú!")
        
        # Dòng 1
        row1 = rows[0]
        self.assertEqual(row1[0], "TK-MIGRATION-TEST-1")
        self.assertEqual(row1[1], "http://original.com/1.jpg")
        self.assertEqual(row1[2], sample_url_cloudinary, "Dữ liệu cột r2_url dòng 1 không khớp với link cũ!")
        self.assertEqual(row1[3], "interior")
        self.assertEqual(row1[4], "crawl")
        
        # Dòng 2 (Link R2 cũ)
        row2 = rows[1]
        self.assertEqual(row2[0], "TK-MIGRATION-TEST-2")
        self.assertEqual(row2[1], "http://original.com/2.jpg")
        self.assertEqual(row2[2], sample_url_r2, "Dữ liệu cột r2_url dòng 2 không khớp với link R2 cũ!")
        self.assertEqual(row2[3], "diagram")
        self.assertEqual(row2[4], "self")
        
        conn.close()
        print("Test di trú SQLite R2 thành công tốt đẹp!")

if __name__ == "__main__":
    unittest.main()
