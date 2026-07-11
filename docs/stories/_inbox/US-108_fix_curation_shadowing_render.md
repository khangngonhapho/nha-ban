---
id: US-108
status: accepted
date: 2026-06-26
size: S
---

# US-108: Sửa lỗi save Curation: Cannot read properties of undefined (reading 'img_mat_tien')

## User story
**As an** Admin
**I want** the listing cards to refresh successfully in-place when saving curation changes
**So that** I don't see JavaScript undefined reference errors and the UI remains responsive.

## Acceptance
- [x] Curation saving (floppy disk button 💾) succeeds without throwing any JavaScript errors.
- [x] The listing cards are updated/rendered in-place successfully.

## Solution

> [!note]- Key logic
> Trong file `static/js/lego_detail_admin.js`, cuộc gọi `render()` sau khi lưu thành công (dòng 2711) bị tranh chấp scope với hàm cục bộ `render(p, sbody)`. Việc đổi thành `window.render()` giải quyết triệt để lỗi này.

## 📋 Implementation Plan
- **Cách tiếp cận:** Đổi cuộc gọi `render()` cục bộ thành `window.render()` rõ ràng.
- **Các bước triển khai dự kiến:**
  1. Thay đổi dòng 2711 trong `static/js/lego_detail_admin.js`.
  2. Chạy bộ E2E tests kiểm chứng.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:** Khảo sát code cũ | Chốt giải pháp
- [x] **Triển khai Code:** Sửa shadowing render() thành window.render() | Tạo file US-108
- [x] **Kiểm thử sơ bộ:** Chạy E2E tests | Verify in-place refresh

## 🛠️ Update Logic (Drafting while Doing)

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:** 
  - *Sự cố:* Khi chạy E2E lần đầu, Playwright báo lỗi timeout 5000ms chờ `#editTieuDeBds` do form chỉnh sửa nằm trong accordion `#accSource` mặc định bị đóng.
  - *Khắc phục:* Bổ sung hành động click vào `#accSource .accordion-header` để mở rộng panel trước khi tương tác với các input bên trong.
  - *Sự cố:* Gặp lỗi `TypeError: 'dict' object is not callable` khi đọc payload request qua `route.request.post_data_json()`.
  - *Khắc phục:* Sửa đổi thành truy cập thuộc tính `route.request.post_data_json` (không có dấu ngoặc đơn).

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- **Script kiểm thử thô / nháp đã chạy:** `python scratch/test_e2e_curation_save_changes.py`
- **Output kết quả nháp & Điểm nghẽn đã vượt qua:** Đã chạy thành công 100% PASS trên cả hai viewports Desktop và Mobile, chụp ảnh bằng chứng lưu vào `docs/workflows/assets/`.


## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** Gặp lỗi JavaScript `Cannot read properties of undefined (reading 'img_mat_tien')` khi bấm nút Lưu 💾 trong detailed curation view của Admin, khiến danh sách card không được làm mới và giao diện bị đơ.
- **Nguyên nhân gốc rễ (Root Cause):** Scope shadowing. Hàm `render(p, sbody)` nội bộ của module `lego_detail_admin.js` che khuất hàm `window.render()` toàn cục (dùng để vẽ lại danh sách listing cards). Khi lưu thành công, lời gọi `render()` (dòng 2711) không có tham số đã gọi hàm cục bộ thay vì hàm toàn cục, dẫn đến `p` bị `undefined` và crash.
- **Giải pháp phòng ngừa:** Sử dụng namespace tường minh `window.render()` khi gọi hàm toàn cục từ bên trong các Lego modules để tránh bị shadowing bởi các hàm module cục bộ cùng tên.

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm code & Cấu hình:** Luôn phân định rõ ràng giữa các hàm module cục bộ (private) và các callback handler toàn cục trên `window`. Tránh gọi hàm không chỉ định namespace nếu có hàm cục bộ trùng tên trong file.
- **Kinh nghiệm kiểm thử:** Khi viết kịch bản Playwright E2E cho form chỉnh sửa, cần lưu ý:
  - Nếu phần tử nằm trong Accordion panel (ví dụ: `#accSource`), phải click để mở rộng panel trước khi điền thông tin (tránh lỗi element not interactable/timeout).
  - Phải giả lập và bắt gói tin HTTP PUT Payload để verify dữ liệu gửi đi khớp hoàn toàn với schema Google Sheets.

## Verification Plan

### Automated Tests
- Chạy bộ test Playwright E2E:
  ```powershell
  python scratch/run_all_e2e.py
  ```

### Manual Verification
- Mở chi tiết Admin, chỉnh sửa thông tin bất kỳ rồi bấm lưu, xác nhận không hiển thị toast đỏ báo lỗi và danh sách được render lại bình thường.

## Files touched
- `static/js/lego_detail_admin.js` — Sửa cuộc gọi render() sang window.render()
