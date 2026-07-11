---
id: US-111
status: accepted
date: 2026-06-29
size: S
---

# US-111: Sửa lỗi khóa panel Biên Tập sau khi vừa lên sóng và tự động tải lại trang

## User Story
**As an** Admin (Biên tập viên)
**I want** the "Biên Tập" accordion panel to expand and collapse normally after the page auto-reloads and focuses on a newly published property
**So that** I can continue editing details or adjusting images without panel lockups.

## Acceptance Criteria
- [x] After publishing a property from Pool, the page reloads and focuses on the newly created Customer Preview.
- [x] Clicking the "BIÊN TẬP" header expands the panel successfully.
- [x] Clicking the "PREVIEW KHÁCH HÀNG" header collapses the panel successfully.
- [x] No inline style overrides remain on `.accordion-content` that would interfere with class-based toggling.

## Solution
Trong file [lego_detail_admin.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_admin.js):
1. Loại bỏ các lệnh gán inline style `content.style.display = 'block'` và `content.style.display = 'none'`.
2. Sử dụng thuần túy class `.expanded` để điều khiển trạng thái hiển thị của accordion thông qua CSS rules trong `global.css`.
3. Bổ sung cơ chế dọn dẹp phòng thủ trong `toggleAdminAccordion` để xóa bỏ thuộc tính `display` inline nếu có.

## 📋 Implementation Plan
- **Cách tiếp cận:** Chuyển đổi cơ chế ẩn/hiện accordion từ can thiệp style inline JS sang quản lý CSS class thuần túy.
- **Các bước triển khai:**
  1. Cập nhật `toggleAdminAccordion` để tự động làm sạch style inline display.
  2. Sửa `validateCurationForm` và khối check `autoExpandPreview` để xóa/bỏ đặt style inline display thay vì đặt cứng `'block'` hoặc `'none'`.
  3. Đăng ký story mới vào `INDEX.md`.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:** Phát hiện lỗi Specificity CSS | Chốt phương án CSS class-based
- [x] **Triển khai Code:** Cập nhật `lego_detail_admin.js` | Tạo tài liệu User Story `US-111`
- [x] **Đồng bộ Index:** Cập nhật `INDEX.md`
- [x] **Kiểm thử & Nghiệm thu:** Chạy bộ test Playwright E2E kiểm chứng | Test thủ công luồng lên sóng và mở lại panel

## 🛠️ Update Logic (Drafting while Doing)

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:**
  - *Sự cố:* Sau khi chuyển hướng sang `autoExpandPreview`, inline CSS `style="display: none"` làm mất tác dụng của class `.expanded` do thuộc tính CSS inline có độ ưu tiên (specificity) cao hơn stylesheet.
  - *Khắc phục:* Đổi toàn bộ các lệnh `style.display = 'block'` và `style.display = 'none'` trên `.accordion-content` thành `style.removeProperty('display')`, bàn giao quyền điều khiển hiển thị hoàn toàn cho CSS thông qua `.accordion-item.expanded`.
  - *Gia cố:* Bổ sung lệnh `content.style.removeProperty('display')` trực tiếp trong hàm `toggleAdminAccordion` để tự động dọn dẹp các style lỗi thời khi click chuột.

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- **Script kiểm thử đã chạy:**
  - `python scratch/test_e2e_curation.py` -> PASS
  - `python scratch/test_e2e_filters.py` -> PASS
  - `python scratch/test_e2e_curation_save_changes.py` -> PASS
- **Kết quả:** Tất cả 3 bộ test Playwright E2E đều chạy thành công 100% PASS trên môi trường mô phỏng Local.

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** Sau khi lên sóng 1 căn từ Pool, trang reload tự động, nhưng bấm vào panel "Biên tập" không có phản hồi mở ra.
- **Nguyên nhân gốc rễ (Root Cause):** Inline style override. JS can thiệp gán cứng `display: none` làm vô hiệu hóa thuộc tính class-based `display: block` trong CSS stylesheet.
- **Giải pháp phòng ngừa:** Hạn chế tối đa việc can thiệp inline style `display` bằng JS nếu đã cấu hình chuyển đổi trạng thái bằng CSS Class (như `.expanded`). Khi muốn thay đổi trạng thái ẩn/hiện, nên ưu tiên `classList.add`/`remove`.

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **CSS Specificity:** Hãy luôn nhớ rằng Inline Styles (`style="..."`) ghi đè toàn bộ CSS Class. Luôn ưu tiên dùng `style.removeProperty('display')` hoặc xóa inline style thay vì gán đè thủ công các giá trị ngược lại.

## Verification Plan

### Automated Tests
- Chạy toàn bộ các test E2E để kiểm tra lỗi hồi quy:
  ```powershell
  python scratch/test_e2e_curation.py
  python scratch/test_e2e_filters.py
  python scratch/test_e2e_curation_save_changes.py
  ```

### Manual Verification
1. Mở Admin Curation cho một căn nhà Pool-only.
2. Bấm "Tự động điền" rồi bấm "Lên sóng & Lưu".
3. Trình duyệt tải lại trang và cuộn đến khu vực Preview.
4. Bấm vào header "BIÊN TẬP", đảm bảo accordion mở ra mượt mà và hiển thị form chỉnh sửa.
