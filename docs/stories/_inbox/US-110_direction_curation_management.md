---
id: US-110
status: accepted
date: 2026-06-28
size: M
---

# US-110: Quản lý và Biên tập Hướng nhà (Direction Curation & Management)

## User story
**As a** Admin / Curator
**I want** thông tin Hướng nhà được tự động trích xuất chuẩn xác khi cào tin, hiển thị read-only ở mục "Thông tin" của chi tiết căn nhà trên web Vercel, đồng thời hiển thị dropdown có 8 hướng ở panel "BIÊN TẬP" để Admin có thể tùy biến và lưu thay đổi vào sheet Source (cột M - `huong_nha`).
**So that** thông tin hướng nhà được lưu trữ đầy đủ trong SQLite thô (cột `Huong`), đồng bộ lên sheet Pool (cột Hướng - R), cho phép Admin biên tập hướng nhà tùy biến riêng cho trang công khai để hiển thị đồng bộ lên website (KPI 2: Chuẩn hóa dữ liệu & Curation chất lượng cao).

## Acceptance
- [x] **Bóc tách Hướng từ API (JSON):** Khi cào lẻ hoặc cào lại qua Proptech API, trích xuất hướng trực tiếp từ mảng `criteria` của dữ liệu thô (tìm phần tử có `groupCode == "HOUSE_DIRECTION"` và lấy `"name"` của nó, ví dụ: `"Tây Nam"`), lưu vào cột `Huong` trong SQLite.
- [x] **Bóc tách Hướng từ DOM (HTML):** Khi cào tin qua DOM (HTML) của Thiên Khôi, Hướng được bóc tách bằng cách tìm nhãn `"hướng nhà"` hoặc `"hướng"` và lấy giá trị ở thẻ sibling cùng cấp kế sau nó (ví dụ: `<p>Hướng nhà</p>` -> lấy text của thẻ tiếp theo là `<p>Tây Nam</p>`).
- [x] **Nâng cấp CSDL SQLite cục bộ:** Thêm cột `custom_huong` (TEXT) vào bảng `listings` trong `raw_archive.db` (hệ thống Pool1) để lưu thông tin Hướng đã được biên tập của admin. Khi cào tin mới, khởi tạo cột này bằng hướng gốc cào được.
- [x] **Phục hồi dữ liệu (Restore):** Khi chạy `restore_db_from_sheets.py`, thông tin Hướng từ sheet Pool (cột R - index 17) được nạp vào cột `Huong` trong SQLite, và Hướng đã biên tập từ sheet Source (cột M - index 12) được nạp vào cột `custom_huong` trong SQLite cục bộ.
- [x] **API cập nhật tin:** Cập nhật endpoint `/api/listings/<tk_id>` (PUT) ở backend để nhận giá trị Hướng đã chỉnh sửa.
- [x] **Giao diện Client Web (Vercel):** Trên trang chi tiết của Web Client hiển thị Hướng nhà dạng read-only ở lưới "Thông tin" (`p.huong`).
- [x] **Giao diện Admin Web (Vercel):**
  - Hiển thị Hướng gốc từ Pool dạng read-only ở lưới "Thông tin" (`p.raw_huong` hoặc `p.pool_row_data[17]`).
  - Hiển thị dropdown combobox chọn 8 Hướng ở phần "BIÊN TẬP" để Admin có thể tùy biến và lưu trực tiếp vào sheet Source (cột M).

*(Lưu ý: Không thay đổi file `curator.html` của ứng dụng Curator cục bộ, việc chỉnh sửa hướng chỉ thực hiện trên web Vercel).*

## Solution
- **Phía Backend (`pool_lego.py` & `fetcher.py` & `manager.py`):**
  - Cập nhật hàm `init_db()` để chạy lệnh `ALTER TABLE listings ADD COLUMN custom_huong TEXT DEFAULT ''` nếu chưa tồn tại.
  - Khi lưu tin thô qua `save_raw_to_sqlite()`, ghi đè giá trị hướng cào được vào cả `Huong` và `custom_huong`.
  - Cập nhật API cập nhật tin cục bộ trong `manager.py` để hỗ trợ lưu `custom_huong` khi backend nhận request.
  - Cập nhật script `restore_db_from_sheets.py` để map đúng `Source` cột 12 vào `custom_huong` thay vì ghi đè lên `Huong` gốc.
- **Phía Frontend (`lego_detail_client.js` & `lego_detail_admin.js`):**
  - Sửa `lego_detail_client.js` để thêm hiển thị `"Hướng:"` trong lưới thông tin chi tiết.
  - Sửa `lego_detail_admin.js` hiển thị `"Hướng gốc:"` dạng read-only ở phần "Thông tin" và khởi tạo mặc định cho dropdown chỉnh sửa hướng bằng hướng đã biên tập.

## 📋 Implementation Plan
1. Nâng cấp database schema tự động bổ sung cột `custom_huong` và chạy thử `restore_db_from_sheets.py` để kiểm tra ánh xạ.
2. Cập nhật logic cào tin API/DOM thô trong `fetcher.py`, `manager.py` và `pool_lego.py`.
3. Sửa đổi backend API `/api/listings/<tk_id>` (PUT) để cập nhật cột `custom_huong`.
4. Cập nhật frontend `lego_detail_client.js` và `lego_detail_admin.js` trên Web Vercel.
5. Tạo và chạy script kiểm thử tự động `scratch/test_direction_extraction.py` để xác minh luồng cào DOM/API.

## 📝 Task Checklist (TODO)
- [x] **Database Schema:** Cập nhật `listings` table thêm cột `custom_huong` | Đã hoàn thành
- [x] **Crawler:** Bóc tách Hướng từ DOM mới và criteria API | Đã hoàn thành
- [x] **Sync & Restore:** Đồng bộ Source cột 12 về SQLite `custom_huong` | Đã hoàn thành
- [x] **Client UI:** Thêm hiển thị Hướng read-only trong chi tiết tin | Đã hoàn thành
- [x] **Admin UI:** Đồng bộ dropdown chọn hướng và hiển thị Hướng gốc | Đã hoàn thành
- [x] **Verification:** Chạy script test tự động | Đã hoàn thành

## Files touched
- `fetcher.py`
- `manager.py`
- `pool_lego.py`
- `restore_db_from_sheets.py`
- `static/js/lego_detail_client.js`
- `static/js/lego_detail_admin.js`
