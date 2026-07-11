---
id: US-096D
status: draft
date: 2026-06-16
size: M
replaces: none
---

# US-096D: Image Curation - Selection, Roles, Ordering, & Rotation

## User story
**As an** Admin  
**I want** biên tập hình ảnh của căn nhà (thay đổi vai trò, thứ tự, ẩn/hiện, xoay ảnh vật lý) và đồng bộ an toàn xuống CSDL SQLite cục bộ và Google Sheets Pool 2.  
**So that** ảnh biên tập được tổ chức gọn gàng, cách ly ảnh nhạy cảm (mặt tiền, sơ đồ) để bảo vệ PII chủ nhà, và đảm bảo ảnh bị ẩn/xóa không bị recrawler tự động cào lại.

## Acceptance Criteria
- [ ] **Biên tập ảnh trực quan**: Cho phép thay đổi vai trò (`facade`, `cover`, `diagram`, `interior`, `alley`), kéo thả sắp xếp thứ tự, ẩn/hiện ảnh, và xoay ảnh vật lý trên Web Admin.
- [ ] **Đồng bộ ảnh SQLite (`listings_images`)**:
  - Ghi nhận đầy đủ thông số vai trò, sequence_index và R2 URL vào bảng `listings_images`.
  - **Logical Delete (Xóa logic)**: Khi Admin chọn ẩn hoặc xóa ảnh, chỉ cập nhật `role` thành `'hidden'` hoặc `'deleted'`. Không được phép xóa vật lý dòng trong CSDL để recrawler không phát hiện là ảnh thiếu và cào lại từ nguồn.
- [ ] **Đồng bộ Google Sheets Pool 2 tab `Images`**:
  - Cập nhật thông số ảnh tương ứng lên tab `Images` của Pool 2 Sheet.
  - Cập nhật chuỗi JSON `curated_config_json` trong tab `Listings` của Pool 2 Sheet làm cache vận chuyển.
  - Cập nhật chuỗi JSON `images_metadata_json` trong tab `Custom` của Source 2 Sheet (chỉ chứa ảnh an toàn: `interior`, `alley`, `cover`, cách ly tuyệt đối `facade` và `diagram` để bảo mật PII).

---

## Solution
1. **SQLite Database Update:**
   - Khi nhận JSON curated config từ client, API `PUT /api/listings/<tk_id>` thực hiện cập nhật bảng `listings_images`: chỉnh sửa cột `role`, `sequence_index`, `r2_url`.
   - Update `curated_config_json` của listings_v2 và `images_metadata_json` của listings_custom_v2.
2. **Google Sheets Images Tab Sync:**
   - Hàm `sync_listing_to_pool2_sheets` trong `pool_lego.py` đồng bộ danh sách ảnh của căn nhà lên tab `Images` của Pool 2 sheet theo đúng dòng ứng với từng URL ảnh.
3. **Logical Deletion Check:**
   - Tránh xoá cứng dòng ảnh. Khi crawl lại trong `fetcher.py`, bộ recrawler sẽ đối chiếu CSDL local, nếu ảnh đã có trong `listings_images` (kể cả với vai trò hidden/deleted) thì bỏ qua không cào lại.

---

## 📝 Task Checklist (TODO)
- [ ] **SQLite Image Sync Logic**
  - [ ] Triển khai hàm lưu thay đổi ảnh vào `listings_images` SQLite trong `manager.py`.
  - [ ] Triển khai cơ chế Logical Delete (chuyển đổi role thành `hidden`/`deleted`).
- [ ] **Google Sheets Sync Integration**
  - [ ] Đồng bộ bảng ảnh sang tab `Images` của Pool 2 sheet.
  - [ ] Đồng bộ chuỗi transport JSON `curated_config_json` và `images_metadata_json` sang các sheet tương ứng.
- [ ] **Recrawler Compatibility**
  - [ ] Xác minh bộ recrawler `fetcher.py` không cào lại các ảnh đã bị đánh dấu ẩn/xóa logic.

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
