# -*- coding: utf-8 -*-
import os

story_path = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-089C_pool2_cross_pool_sync.md"

# Read with errors='replace' to load safely
with open(story_path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# Let's perform replacement for implementation plan and solution details
old_segment_1 = """- [ ] **Chiều ngược: Đồng bộ và quan hệ hóa (Pool1 -> Pool2)**:
  - Hỗ trợ di chuyển dữ liệu cũ: Đọc dòng dữ liệu phẳng từ bảng `listings` của `raw_archive.db`.
  - Tách metadata thô sang `listings_v2` và thông tin custom sang `listings_custom_v2`.
  - Quét các cột ảnh phẳng (25 ảnh, 10 hẻm, 5 sơ đồ) không rỗng, tách chúng thành các dòng ảnh riêng biệt chèn vào bảng `listings_images` với sequence_index"""

new_segment_1 = """- [ ] **Chiều ngược: Đồng bộ và quan hệ hóa (Pool1 -> Pool2)**:
  - Hỗ trợ di chuyển dữ liệu cũ và khớp nối địa chỉ: Đọc dòng dữ liệu phẳng từ bảng `listings` của `raw_archive.db`.
  - Thực hiện chuẩn hóa địa chỉ (số nhà + tên đường) và gọi API tìm kiếm Thiên Khôi mới `https://backend.thienkhoi.com/product/v1/property?searchBy=address&search=[Tên Đường]` để lấy mã `tk_id` (UUID) mới.
  - So khớp số nhà đã chuẩn hóa để xác định tin chính xác trên hệ thống mới. Nếu không tìm thấy, di trú tin cũ sang dưới mã ID `LEGACY-[mã cũ]` và trạng thái `published_legacy` để bảo toàn dữ liệu.
  - Tách metadata thô sang `listings_v2` và thông tin custom sang `listings_custom_v2`.
  - Quét các cột ảnh phẳng (25 ảnh, 10 hẻm, 5 sơ đồ) không rỗng, tách chúng thành các dòng ảnh riêng biệt chèn vào bảng `listings_images` với sequence_index"""

old_segment_2 = """### 2. Quan hệ hóa ảnh phẳng (Pool1 -> Pool2)
- Truy vấn bảng `listings` ở `raw_archive.db`.
- Tách metadata thô lưu vào `listings_v2`, thông tin custom lưu vào `listings_custom_v2` (khóa chính `System_ID`).
- Quét toàn bộ các cột ảnh phẳng của dòng dữ liệu:"""

new_segment_2 = """### 2. Khớp địa chỉ & Quan hệ hóa ảnh phẳng (Pool1 -> Pool2)
- Truy vấn bảng `listings` ở `raw_archive.db`.
- Khớp nối địa chỉ: Chuẩn hóa địa chỉ của tin cũ, truy vấn danh sách tin mới bằng API `/product/v1/property?searchBy=address&search=[Tên Đường]`.
- Quét kết quả trả về, đối sánh số nhà đã chuẩn hóa để tìm mã `tk_id` (UUID) mới.
- Gọi API chi tiết của tin mới để cào thông tin mới (criteria, bedrooms, restrooms) ghi vào `listings_v2`.
- Nếu không khớp thành công, di trú dữ liệu cũ sang Pool 2 dưới mã `LEGACY-[mã cũ]` và trạng thái `published_legacy`.
- Tách metadata thô lưu vào `listings_v2`, thông tin custom lưu vào `listings_custom_v2` (khóa chính `System_ID`).
- Quét toàn bộ các cột ảnh phẳng của dòng dữ liệu:"""

if old_segment_1 in content:
    content = content.replace(old_segment_1, new_segment_1)
    print("Replaced segment 1 successfully.")
else:
    # Try fuzzy replace if exact match fails
    print("Could not find old_segment_1 exactly. Searching for matching lines...")
    
if old_segment_2 in content:
    content = content.replace(old_segment_2, new_segment_2)
    print("Replaced segment 2 successfully.")
else:
    print("Could not find old_segment_2 exactly.")

# Convert replace character (like invalid bytes) to clean UTF-8 string
content = content.replace("\ufffd", "") # remove any replacement chars

# Save in clean UTF-8
with open(story_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Saved US-089C story file in clean UTF-8 encoding.")
