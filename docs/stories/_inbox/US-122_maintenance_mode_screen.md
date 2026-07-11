---
id: US-122
status: accepted
date: 2026-07-09
size: M
---

# US-122: Trang thông báo bảo trì khi bật maintenance_mode

## User story
**As a** PO / Admin
**I want** khi cấu hình `maintenance_mode` là `true`, trang Vercel Web dành cho khách hàng (public site) sẽ hiển thị màn hình thông báo hệ thống đang bảo trì
**So that** khách hàng biết hệ thống đang nâng cấp, trong khi Admin vẫn có thể truy cập trang Curator, Canvas và các API để làm việc bình thường.

## Acceptance
- [x] Khi `maintenance_mode` trong `settings.json` là `true`:
  - Phản hồi từ endpoint `/api/config` sẽ chứa thuộc tính `maintenance_mode: true`.
  - Trên giao diện khách hàng (trang chủ `index.html`), mã nguồn frontend (JavaScript) sẽ kiểm tra cờ này. Nếu cờ là `true` và người dùng không phải là admin (`window.isAdmin !== true`), hệ thống sẽ chặn kết xuất và hiển thị màn hình thông báo bảo trì toàn màn hình.
  - Đối với admin (`window.isAdmin === true`), hoặc khi truy cập trang biên tập `/curator.html`, `/canvas.html`, hệ thống hoàn toàn bỏ qua màn hình bảo trì để admin làm việc bình thường.
- [x] Giao diện trang bảo trì cho khách hàng phải có tính thẩm mỹ cao (Dark mode, hiệu ứng glassmorphism và icon xoay nhẹ nhàng).
- [x] Khi `maintenance_mode` là `false` hoặc cấu hình không tồn tại, trang web phải hoạt động hoàn toàn bình thường cho cả khách hàng.
- [x] Viết unit test tự động để cấu hình và kiểm thử phản hồi cấu hình.
- [x] **Mở rộng: Tác động tức thời qua Google Sheets (Dynamic Toggling)**:
  - Cho phép Admin thay đổi giá trị của `maintenance_mode` trực tiếp trên tab `Feature_Flags` của Google Sheet.
  - Cả endpoint `/api/config` trên Node.js Vercel và Flask Python local phải tự động gọi Google Sheets API để lấy giá trị mới nhất.
  - Cơ chế gọi Google Sheets phải có giới hạn thời gian (Timeout 4s) và tự động fallback về giá trị trong `settings.json` nếu thất bại/hết hạn để không làm ảnh hưởng đến tốc độ tải trang.

## Solution

> [!note]- Configuration
> Đọc từ `settings.json` qua thuộc tính:
> `"feature_flags": { "maintenance_mode": true }`
> Hoặc đọc động từ tab `Feature_Flags` trên Google Sheets nếu có credentials và kết nối thành công.

## 📋 Implementation Plan
- **Cách tiếp cận:**
  - Cập nhật backend endpoint `/api/config` tại `api/index.js` để trả về cờ `maintenance_mode` từ file cấu hình.
  - Cập nhật hàm `loadData()` của `LegoState` trong `static/js/lego_core.js`. Sau khi gọi `/api/config`, nếu phát hiện `maintenance_mode` là `true` và `!this.isAdmin`:
    - Gọi phương thức `showMaintenanceScreen()` để kết xuất màn hình bảo trì toàn màn hình và dừng tải dữ liệu.
  - Viết bộ kiểm thử unit test và tích hợp để kiểm thử.
  - **Mở rộng (Dynamic Feature Flags):**
    - Mở rộng OAuth scope của Node.js backend lên `spreadsheets.readonly` để đọc dữ liệu sheet trực tiếp.
    - Triển khai logic đọc động tab `Feature_Flags` từ Sheets API v4 trên Node.js (`api/index.js`) với cơ chế `Promise.race` khống chế thời gian chờ.
    - Triển khai logic đọc tương tự qua thư viện `gspread` trên Flask Python (`api/routes_system.py`) với xử lý ngoại lệ an toàn.
    - Ghép cờ động từ Sheets đè lên cờ tĩnh của `settings.json`.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát hàm entrypoint `api/index.js`
- [x] **Triển khai Code (Static Flag):**
  - [x] Sửa đổi `api/index.js` để thêm logic bảo trì ở đầu hàm chính
- [x] **Kiểm thử & Xác minh:**
  - [x] Viết unit test bổ sung vào `tests/test_maintenance.py` hoặc `tests/test_api_contracts.py`
  - [x] Chạy kiểm thử tự động `pytest`
  - [x] Xác minh chạy offline/mock thành công
- [x] **Đồng bộ động từ Google Sheets (Dynamic Flags):**
  - [x] Nâng cấp hàm lấy token OAuth trong `api/index.js` hỗ trợ scope Sheets API.
  - [x] Triển khai hàm fetch và parse dữ liệu tab `Feature_Flags` từ Google Sheets trong `api/index.js`.
  - [x] Tích hợp cơ chế Timeout & Fallback cho `/api/config` trong Node.js backend.
  - [x] Triển khai cơ chế đồng bộ động tương đương bằng `gspread` trong `api/routes_system.py`.
  - [x] Kiểm thử E2E và thủ công (bật/tắt cờ trên Google Sheet và F5 trang).

## 🛠️ Update Logic (Drafting while Doing)
### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Thiết kế tối giản:** Thay vì chặn ở tầng Vercel server-side và xử lý các cơ chế lưu bypass cookie phức tạp, chúng tôi chuyển cơ chế chặn sang Frontend (Client-side) thông qua việc trả về cờ `maintenance_mode` trong API cấu hình `/api/config`.
- **Độc lập Admin:** Frontend chỉ chặn và kết xuất trang bảo trì khi người dùng không phải là admin (`!this.isAdmin`). Điều này giúp Admin đăng nhập bình thường và truy cập các trang `/curator.html`, `/canvas.html` hay thậm chí là admin-view của trang chủ `index.html` hoàn toàn bình thường.

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- Chạy unit tests: `python -m pytest tests/test_maintenance.py -v` đạt kết quả `2 passed`.

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)
- **Bài học thiết kế:** Luôn ưu tiên giải pháp đơn giản nhất (KISS - Keep It Simple, Stupid) để giải quyết yêu cầu nghiệp vụ thay vì tự động đề xuất các cơ chế định tuyến hay lưu cookie phức tạp.
- **Tính năng độc lập:** Việc phân định rõ ràng giữa trải nghiệm của Khách hàng và Admin giúp nâng cao khả năng quản trị và vá lỗi của hệ thống trong thời gian bảo trì.

## Verification Plan

### Automated Tests
- `pytest tests/test_maintenance.py`

### Manual Verification
- Cấu hình `maintenance_mode: true` trong `settings.json`, truy cập các trang và xác nhận giao diện bảo trì.

## Files touched
- `api/index.js` — Thêm logic chặn bảo trì
- `tests/test_maintenance.py` — Bộ kiểm thử tự động mới
- `docs/stories/_inbox/US-122_maintenance_mode_screen.md` — Tài liệu User Story gốc
