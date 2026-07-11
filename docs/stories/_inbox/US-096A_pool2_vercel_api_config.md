---
id: US-096A
status: accepted
date: 2026-06-16
size: S
replaces: none
---

# US-096A: API Config & SQLite Schema Upgrade

## User story
**As an** Admin  
**I want** CSDL SQLite (`raw_archive_v2.db`) và các API backend tự động cập nhật để hỗ trợ trường tùy biến `Custom_Rong_Hem` và cấu hình Spreadsheet IDs động.  
**So that** tôi có thể thiết lập hệ thống dữ liệu đồng bộ chuẩn Pool2 và đảm bảo cấu hình đúng đắn khi triển khai lên Vercel.

## Acceptance Criteria
- [ ] **Tự động di cư SQLite**: Khi khởi chạy ứng dụng, bảng `listings_custom_v2` tự động được thêm cột `Custom_Rong_Hem` (kiểu dữ liệu TEXT) nếu chưa tồn tại mà không mất dữ liệu cũ.
- [ ] **Đồng bộ Google Sheets Schema**: Thêm cột `Custom_Rong_Hem` vào danh sách `CUSTOM_HEADERS` toàn cục để hệ thống tự tạo cột mới này trên file Google Sheets Custom (Source 2) khi đồng bộ.
- [ ] **API Cấu hình động**: Endpoint `/api/config` trả về đúng 3 Spreadsheet IDs theo cấu hình đang active (Pool1 hay Pool2):
  - `active_pool_system`: Hệ thống Pool đang hoạt động.
  - `sheet_id`: File Public ID.
  - `pool_sheet_id`: File Pool 2 (Raw) ID.
  - `source_sheet_id`: File Source 2 (Custom) ID.

---

## Solution
1. **Schema Upgrade trong `pool_lego.py`:**
   - Thêm `Custom_Rong_Hem` vào danh sách `custom_cols` ở dòng 556 trong `init_db()` để kích hoạt ALTER TABLE.
   - Thêm `Custom_Rong_Hem` vào mảng `CUSTOM_HEADERS` ở dòng 162.
2. **API Endpoint `/api/config`:**
   - Cập nhật trong `api/index.js` (Serverless) trả về các Spreadsheet IDs tương ứng.
   - Cập nhật trong `manager.py` (Flask API) khớp với logic trên.

---

## 📝 Task Checklist (TODO)
- [ ] **Database Schema Upgrade**
  - [ ] Thêm `"Custom_Rong_Hem"` vào `custom_cols` trong `pool_lego.py`.
  - [ ] Thêm `"Custom_Rong_Hem"` vào `CUSTOM_HEADERS` trong `pool_lego.py`.
- [ ] **Backend Routing**
  - [ ] Cập nhật endpoint `/api/config` trong `manager.py`.
  - [ ] Cập nhật endpoint `/api/config` trong `api/index.js` cho Vercel serverless.
- [ ] **Kiểm thử**
  - [ ] Chạy server local và xác minh SQLite tạo thành công cột mới qua Pragma.

---

## Proposed Changes

### [Component: Epic Master - US-096]
#### [MODIFY] [US-096_connect_vercel_web_to_pool2.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-096_connect_vercel_web_to_pool2.md)
*   Epic Master quản lý tổng thể tiến độ và cấu trúc liên kết của phân hệ.
*   Cập nhật phần Solution và Task Checklist của Epic để theo dõi 5 story con.

---

### [Component: US-096A - API Config & SQLite Schema Upgrade]
#### [NEW] [US-096A_pool2_vercel_api_config.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-096A_pool2_vercel_api_config.md)
*   **Mục tiêu:**
    *   Thêm cột `Custom_Rong_Hem` vào mảng `CUSTOM_HEADERS` và `custom_cols` trong `pool_lego.py`.
    *   Tự động chạy SQLite migration tạo cột `Custom_Rong_Hem` trong `listings_custom_v2`.
    *   Tạo endpoint `/api/config` trong `api/index.js` và `manager.py` trả về Spreadsheet IDs động tương ứng với Pool Hệ thống được chọn (Pool1 / Pool2).
*   **Tệp thay đổi:**
    *   [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py)
    *   [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py)
    *   [api/index.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/api/index.js)

---

### [Component: US-096B - Frontend Curation Load]
#### [NEW] [US-096B_pool2_vercel_frontend_load.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-096B_pool2_vercel_frontend_load.md)
*   **Mục tiêu:**
    *   Frontend gọi `/api/config` lưu cấu hình Spreadsheet IDs động vào `LegoState.config` khi khởi động.
    *   Bóc tách cột Google Sheet theo cơ chế động (hỗ trợ cả Pool1 cũ và Pool2 mới).
    *   Load dữ liệu tùy biến (từ Source 2 Sheet / SQLite Custom) và nạp chúng vào các control hiện có trên form (Hướng, Phân loại hẻm, Số phòng ngủ, Số WC, Ngủ trệt, CHDV, Đánh giá, Tình trạng). Fallback lấy từ Pool 2 thô nếu chưa có dữ liệu custom.
*   **Tệp thay đổi:**
    *   [static/js/lego_core.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_core.js)
    *   [static/js/lego_detail_admin.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_admin.js)
    *   [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html)

---

### [Component: US-096C - Curation Save - Text & Specs Curing]
#### [NEW] [US-096C_pool2_vercel_curation_save.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-096C_pool2_vercel_curation_save.md)
*   **Mục tiêu:**
    *   Hàm `saveSourceChanges` và `saveNewListingFromPool` trong `lego_detail_admin.js` thu thập giá trị văn bản, thông số kỹ thuật, bao gồm cả Rộng hẻm m tùy biến từ control có sẵn (`#edit-duong-truoc-nha` hoặc `#editDuong`).
    *   Gửi payload cập nhật lên API `PUT /api/listings/<tk_id>` để cập nhật SQLite bảng `listings_custom_v2`.
    *   Đồng bộ dữ liệu văn bản tùy biến lên Source 2 (tab `Custom`).
*   **Tệp thay đổi:**
    *   [static/js/lego_detail_admin.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_admin.js)
    *   [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py)

---

### [Component: US-096D - Image Curation - Selection, Roles, Ordering, & Rotation]
#### [NEW] [US-096D_pool2_vercel_image_curation.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-096D_pool2_vercel_image_curation.md)
*   **Mục tiêu:**
    *   Hỗ trợ kéo thả sắp xếp, ẩn/hiện, chọn vai trò ảnh và xoay ảnh vật lý trên Web Admin.
    *   Khi lưu, đồng bộ thay đổi vào SQLite `listings_images` và tab `Images` của Pool 2 Sheet.
    *   Thực thi cơ chế Logical Delete (không xóa cứng, đổi role thành hidden/deleted) để tránh bộ recrawl cào đè.
    *   Cập nhật các chuỗi JSON cache `curated_config_json` (bảng Listings) và `images_metadata_json` (bảng Custom, đã cách ly ảnh nhạy cảm facade/diagram).
*   **Tệp thay đổi:**
    *   [static/js/lego_detail_admin.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_admin.js)
    *   [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py)
    *   [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py)

---

### [Component: US-096E - Public Whitelist Publication]
#### [NEW] [US-096E_pool2_vercel_public_publish.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-096E_pool2_vercel_public_publish.md)
*   **Mục tiêu:**
    *   Khi nhấn "Lên sóng", trích xuất dữ liệu tùy biến đã duyệt sạch, lọc bỏ các cột PII bảo mật.
    *   Đồng bộ các thuộc tính whitelist (đã bao gồm `Custom_Rong_Hem`) lên tab `Public` của Public Sheet.
    *   Rã phẳng mảng ảnh công khai an toàn (từ `images_metadata_json`) thành các cột Ảnh 1..Ảnh N nằm phía sau cột "Last updated" trên Public Sheet.
*   **Tệp thay đổi:**
    *   [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py)

---

## Verification Plan

### Automated Tests
- Chạy toàn bộ bộ kiểm thử Playwright để xác minh (bao gồm cả tệp test mới tự động được phát hiện):
  ```powershell
  python scratch/run_all_e2e.py
  ```
- Để chạy test ở chế độ có hiển thị giao diện Chrome (Headed), sử dụng:
  ```powershell
  python scratch/run_all_e2e.py --headed
  ```
- *Lưu ý:* Khi viết mới test case E2E cho Pool 2 (`scratch/test_e2e_pool2_transition.py`), script runner sẽ tự động quét, tích hợp và thực thi song song mà không cần khai báo cứng.

### Manual Verification
1. Kích hoạt chế độ Pool2, kiểm tra xem SQLite CSDL có tự sinh cột `Custom_Rong_Hem` không bằng pragma query.
2. Mở Web Admin, truy cập một căn, chỉnh sửa một số thông tin văn bản, thay đổi rộng hẻm thành `4.5` trên control có sẵn. Bấm Lưu và xác minh CSDL SQLite bảng `listings_custom_v2` và Google Sheet Custom đã lưu thành công dữ liệu mới.
3. Ẩn 2 ảnh bất kỳ và đổi thứ tự ảnh. Xác minh SQLite bảng `listings_images` và Google Sheet Pool 2 tab `Images` nhận đúng các đổi vai trò (hidden), không bị xóa cứng.
4. Kích hoạt trạng thái Active, nhấn Lên sóng, kiểm tra xem Google Sheet Public nhận đúng dữ liệu whitelist sạch (không chứa PII) và rã ảnh phẳng thành công từ cột Ảnh 1 trở đi, đặt phía sau cột "Last updated".
