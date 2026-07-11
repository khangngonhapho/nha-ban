---
id: US-096
status: draft
date: 2026-06-16
size: M
replaces: none
---

# US-096: Kết nối Web Vercel với hệ thống dữ liệu Pool2 (Epic Master)

## User story
**As an** Admin  
**I want** ứng dụng web Vercel kết nối đồng bộ với hệ thống 3 file Google Sheets của Pool2:
- File **Pool 2** (Raw - `pool2_raw_sheet_id`): Lưu thông tin thô (`Listings`) và kho ảnh thô (`Images`).
- File **Source 2** (Custom - `pool2_custom_sheet_id`): Lưu thông tin chỉnh sửa tùy biến (`Custom`).
- File **Public** (Public - `pool2_public_sheet_id`): Lưu thông tin sạch phục vụ web public (`Public`).  
**So that** tôi có thể biên tập các căn nhà (kể cả căn chưa lên sóng) dựa trên dữ liệu tùy biến mà không làm ảnh hưởng đến dữ liệu cào thô gốc, đồng thời quản lý hình ảnh tập trung an toàn, và cập nhật được thông tin hẻm tùy chọn `Custom_Rong_Hem`.

## Acceptance Criteria
- [ ] **Biên tập căn chưa lên sóng**: Cho phép Admin mở form curation và chỉnh sửa thông tin của các căn nhà đang ở trạng thái thô (chưa xuất bản / chưa lên sóng trên Public sheet).
- [ ] **Lấy dữ liệu biên tập từ Custom (Source 2)**:
  - Thông tin hiển thị trên form biên tập được load từ bảng Custom (Source 2 sheet - `listings_custom_v2`).
  - Khi cào căn mới về, hệ thống tự động khởi tạo dòng tương ứng bên Custom (Source 2) với các cột thuộc tính giống hệt bên Raw (Pool 2).
  - Bảng Raw (Pool 2) hoàn toàn ở chế độ Read-only (không bao giờ bị Admin sửa đổi trực tiếp) để bảo toàn dữ liệu gốc cào về. Mọi thao tác chỉnh sửa của Admin chỉ cập nhật vào Custom (Source 2).
  - Bổ sung trường dữ liệu `Custom_Rong_Hem` (đơn vị mét) trên form biên tập, cho phép sửa đổi và lưu đúng xuống SQLite bảng `listings_custom_v2` và sheet Custom.
- [ ] **Quản lý hình ảnh tập trung**:
  - Toàn bộ hình ảnh (gồm URL, vai trò `role`, thứ tự `sequence_index`, trạng thái ẩn/hiện, tài khoản biên tập) được lưu trữ tập trung tại bảng `listings_images` trong SQLite local và tab `Images` của File Pool 2 (Raw sheet).
- [ ] **Tải dữ liệu public chuẩn Pool2**: Client Web public chỉ tải dữ liệu sạch từ File Public (`pool2_public_sheet_id` - tab `Public`) và hiển thị cho khách hàng.
- [ ] **Tương thích ngược**: Bảo đảm hệ thống hoạt động bình thường ở chế độ Pool1 khi `active_pool_system` được cấu hình là `"Pool1"`.

---

## Solution

### 1. Phân chia vai trò 3 File Google Sheets trong Pool2
- **File Pool 2 (Raw - `pool2_raw_sheet_id`)**:
  - Tab `Listings`: Ánh xạ bảng `listings_v2` (Dữ liệu thô cào về, read-only).
  - Tab `Images`: Ánh xạ bảng `listings_images` (Lưu thông tin tất cả hình ảnh, vai trò, thứ tự, ẩn hiện).
- **File Source 2 (Custom - `pool2_custom_sheet_id`)**:
  - Tab `Custom`: Ánh xạ bảng `listings_custom_v2` (Dữ liệu tùy biến do Admin chỉnh sửa). Đây là nguồn dữ liệu chính được Web Admin nạp lên form biên tập và cập nhật lại khi lưu.
- **File Public (Public - `pool2_public_sheet_id`)**:
  - Tab `Public`: Dữ liệu sạch đã whitelist và rã ảnh từ Custom, phục vụ trang chủ khách hàng.

### 2. Thiết lập API Cấu hình `/api/config`
API trên serverless Vercel (`api/index.js`) trả về cấu hình Sheet IDs tương ứng:
```json
{
  "active_pool_system": "Pool2",
  "sheet_id": "1U2lEH07GIyiO3YY3_jzCk_09DErd9a6r8cjZhioE_5g", // Public sheet ID
  "pool_sheet_id": "1fwMeR_UyfABoZ-IWRDYwEU9rlbPXZENOgXaiEw2cbmg", // Pool 2 (Raw) sheet ID
  "source_sheet_id": "11BZxVYP7Xsv6JVvWMK9VpPipT91Ue5wfNuhO3rbZe7U" // Source 2 (Custom) sheet ID
}
```

### 3. Logic Nạp dữ liệu trong Web Admin (`lego_core.js` & `lego_detail_admin.js`)
- Khi khởi tạo ở chế độ Pool2, Web Admin sẽ tải song song:
  - Dữ liệu tùy biến từ tab `Custom` của **Source 2** (`source_sheet_id`).
  - Dữ liệu thô của các căn chưa lên sóng từ tab `Listings` của **Pool 2** (`pool_sheet_id`).
- Khớp nối dữ liệu qua khóa chính `System_ID`.
- Form curation hiển thị thông tin lấy từ bản ghi Custom. Nếu căn nhà chưa có bản ghi Custom (mới cào về chưa từng được mở), hệ thống sẽ tự động khởi tạo bản ghi Custom kế thừa các thuộc tính từ bản ghi Raw (Pool 2).

### 4. Logic Lưu Curation và Quản lý Hình ảnh
Khi Admin thực hiện **Lưu chỉnh sửa** hoặc **Lên sóng**:
- Cập nhật thông tin text (Giá public, tiêu đề public, mô tả, note nội bộ, địa chỉ...) và `Custom_Rong_Hem` vào tab `Custom` của **Source 2** (`source_sheet_id`).
- Cập nhật thông tin hình ảnh (thêm mới, xoay ảnh, đổi vai trò, ẩn/hiện) vào tab `Images` của **Pool 2** (`pool_sheet_id`).
- Nếu trạng thái là `Đang bán` (Active), đẩy dữ liệu sạch (whitelist các cột từ Custom + rã danh sách ảnh an toàn) sang tab `Public` của file **Public** (`sheet_id`).

---

## 📋 Implementation Plan

Do phạm vi tích hợp lớn bao gồm cả thay đổi Schema DB SQLite/Google Sheets và giao diện Frontend biên tập của Admin, công việc được phân rã thành 3 User Story con độc lập:

### 1. US-096A: API Config & SQLite Schema Upgrade
*   **Mục tiêu:** Thêm cột `Custom_Rong_Hem` vào schema tùy biến, tự nâng cấp DB SQLite bảng `listings_custom_v2`, và cấu hình `/api/config` trả về Spreadsheet IDs động.
*   **Tệp tác động:** `pool_lego.py`, `manager.py`, `api/index.js`.

### 2. US-096B: Frontend Load & Detail View Admin
*   **Mục tiêu:** Nạp config động khi khởi tạo web admin, thêm ô nhập liệu `Custom_Rong_Hem` trên Form Admin Detail View và hiển thị dữ liệu đã lưu từ bảng Custom.
*   **Tệp tác động:** `static/js/lego_core.js`, `static/js/lego_detail_admin.js`, `index.html`.

### 3. US-096C: Curation Save & Image Sync Logic
*   **Mục tiêu:** Khi Admin nhấn Lưu, ghi nhận giá trị hẻm tùy biến vào SQLite & Google Sheets Custom. Đồng bộ trạng thái ảnh vào tab `Images` của Pool 2 sheet và đẩy bản ghi sạch sang Public sheet.
*   **Tệp tác động:** `static/js/lego_detail_admin.js`, `manager.py`.

---

## 📝 Task Checklist (TODO)
- [ ] **US-096A: API Config & SQLite Schema Upgrade**
  - [ ] Thêm `Custom_Rong_Hem` vào mảng `custom_cols` và `CUSTOM_HEADERS` trong `pool_lego.py`.
  - [ ] Triển khai `/api/config` trên Serverless (`api/index.js`) & Flask (`manager.py`).
  - [ ] Kiểm chứng SQLite tự sinh cột `Custom_Rong_Hem` trên môi trường phát triển local.
- [ ] **US-096B: Frontend Load & Detail View Admin**
  - [ ] Nhận config động qua `LegoState.config` và phân tách parser Pool1 / Pool2.
  - [ ] Bổ sung ô nhập liệu `Custom_Rong_Hem` trên giao diện Curation Form (`index.html`).
  - [ ] Map và hiển thị giá trị `Custom_Rong_Hem` từ Custom data khi tải chi tiết căn.
- [ ] **US-096C: Curation Save & Image Sync Logic**
  - [ ] Cập nhật API PUT `/api/listings/<tk_id>` lưu `Custom_Rong_Hem` vào SQLite.
  - [ ] Cập nhật `saveSourceChanges` gửi dữ liệu hẻm lên Google Sheets Custom.
  - [ ] Ghi nhận vai trò ảnh vào tab `Images` và xuất bản bản ghi sạch sang Public khi Active.
- [ ] **Kiểm thử & Bàn giao:**
  - [ ] Viết bộ test E2E Playwright `tests/test_e2e_pool2_transition.py` kiểm định toàn bộ luồng.
  - [ ] Chạy kiểm thử tự động 100% PASS và triển khai Production Vercel.

---

## 🔍 Verification Plan

### Automated Tests
*   Chạy toàn bộ bộ kiểm thử Playwright để xác minh (bao gồm cả kịch bản test mới tự động được phát hiện):
    ```powershell
    python scratch/run_all_e2e.py
    ```
    Để chạy test ở chế độ có hiển thị trình duyệt Chrome (Headed), sử dụng:
    ```powershell
    python scratch/run_all_e2e.py --headed
    ```
    Bộ test này sẽ giả lập Admin đăng nhập, mở căn thô, nhập giá trị vào trường Rộng hẻm mới, nhấn Lưu và xác minh SQLite + mock Sheets lưu đúng giá trị.

### Manual Verification
1.  Bật chế độ `"active_pool_system": "Pool2"` trong `settings.json`.
2.  Mở Web Admin local, kiểm tra xem CSDL tự động sinh thêm cột `Custom_Rong_Hem` trong `listings_custom_v2`.
3.  Truy cập chi tiết căn bất kỳ, nhập thử giá trị hẻm (ví dụ `5.2`) và lưu lại.
4.  Xác minh dữ liệu được cập nhật đúng xuống SQLite bảng `listings_custom_v2` và dòng tương ứng trên Google Sheets **Source 2** (Custom).
5.  Xác minh hình ảnh đồng bộ đúng với tab `Images` của Pool 2 và dữ liệu được đẩy thành công sang Public khi đổi trạng thái thành Active.
