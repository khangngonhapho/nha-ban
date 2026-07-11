---
id: US-094A3
status: accepted
date: 2026-06-15
size: M
---

# US-094A3: Phân tách Engine Render danh sách Card BĐS

## User story
**As a** Developer  
**I want** phân tách logic render danh sách Card BĐS (dành cho Khách hàng và Admin) từ index.html ra các tệp module js độc lập  
**So that** làm sạch tệp index.html, tăng tính mô-đun hóa, dễ dàng bảo trì và tối ưu hóa hiệu năng vẽ lại DOM bằng DocumentFragment.

## Acceptance
- [x] Tạo tệp `static/js/lego_render_client.js` chịu trách nhiệm render Card cho giao diện Khách hàng.
- [x] Tạo tệp `static/js/lego_render_admin.js` chịu trách nhiệm render Card cho giao diện Admin.
- [x] Phân tách hoàn toàn hàm `render()` gốc trong `index.html` thành các lời gọi tương ứng đến hai engine render mới.
- [x] Đảm bảo 100% tương thích ngược, không làm gãy các tính năng hiện tại: Lọc, Sắp xếp, Phân trang, Xem chi tiết, Đánh dấu yêu thích, Checkbox chọn nhiều, và Thao tác trên Bộ sưu tập.
- [x] Chạy bộ kiểm thử E2E tự động Playwright và đạt 100% PASS trên cả PC và Mobile viewports.

## Solution

### 1. LegoRenderClient Module (`lego_render_client.js`)
*   Định nghĩa đối tượng toàn cục `window.LegoRenderClient`.
*   Phương thức `createCard(p, options)` sẽ chịu trách nhiệm tạo ra card hiển thị cho khách hàng vãng lai.
*   Cơ chế lọc ảnh sodo (`window.isListingSodoUrl`) và chỉnh sửa ảnh Cloudinary (`window.fixImgUrl`) được gọi toàn cục để lấy ảnh cover public an toàn.

### 2. LegoRenderAdmin Module (`lego_render_admin.js`)
*   Định nghĩa đối tượng toàn cục `window.LegoRenderAdmin`.
*   Phương thức `createCard(p, curatedListing, options)` sẽ chịu trách nhiệm tạo ra card hiển thị cho admin quản trị.
*   Hiển thị đầy đủ thông tin nhạy cảm: Tên/SĐT đầu chủ, tag Badges trạng thái Pool (`🟢 Đã lên sóng` / `⚪ Chưa lên sóng`).
*   Bao gồm nút checkbox đồng bộ trạng thái `SELECTED_IDS` của Admin Dashboard.

### 3. Đấu nối trong `index.html`
*   Nạp cả 2 tệp script render mới ở head.
*   Di chuyển hàm `formatPhone` sang `lego_core.js` và gọi qua `window.formatPhone`.
*   Hàm `render()` trong `index.html` sẽ phân loại theo `isAdmin` để gọi `LegoRenderAdmin.createCard(...)` hoặc `LegoRenderClient.createCard(...)` tương ứng, append vào `DocumentFragment`.

---

## 📋 Implementation Plan
Tham khảo kế hoạch triển khai chi tiết tại [implementation_plan.md](file:///C:/Users/Khang%20Ngo/.gemini/antigravity/brain/595fc691-aac4-4d6b-9257-a1e94612755c/implementation_plan.md).

---

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát toàn bộ template thẻ Card trong hàm `render()` gốc
  - [x] Thống nhất API cho `LegoRenderClient` và `LegoRenderAdmin`
- [x] **Triển khai Code:**
  - [x] Di chuyển `formatPhone` sang `lego_core.js` và đăng ký toàn cục
  - [x] Tạo tệp `static/js/lego_render_client.js` và triển khai `LegoRenderClient.createCard`
  - [x] Tạo tệp `static/js/lego_render_admin.js` và triển khai `LegoRenderAdmin.createCard`
  - [x] Sửa đổi mã nguồn `index.html`: nạp script mới và đấu nối trong hàm `render()`
- [x] **Kiểm thử & Bàn giao:**
  - [x] Chạy bộ kiểm thử E2E Playwright đa thiết bị local đạt 100% PASS
  - [x] Merge code vào `main` và push deploy Live lên Production
  - [x] Bàn giao PO kiểm thử giao diện Card trên môi trường Live

---

## 🧠 Retro, Lessons Learned & Good Practices
- **Khởi tạo DOM Node thay vì Interpolate chuỗi HTML**: Việc tự sinh ra các phần tử DOM (`document.createElement`) giúp kiểm soát các sự kiện inline (như click, checkbox change, heart toggle) an toàn, bọc gọn gàng ngữ cảnh mà không bị vỡ giao diện so với ghép chuỗi HTML thuần.
- **Bảo toàn hiệu năng qua DocumentFragment**: Tiếp tục duy trì kỹ thuật gom Card Element vào `DocumentFragment` trước khi append hàng loạt vào DOM giúp tránh Reflow liên tục và hiện tượng nhấp nháy màn hình.
- **Tách biệt vai trò (Separation of Concerns)**: Module Render chỉ làm nhiệm vụ vẽ giao diện (Presenter), không lưu trữ State hay tự tính toán lọc. Toàn bộ State và hàm xử lý nghiệp vụ đều do `LegoState` và các hàm global của `index.html` cung cấp.

---

## Verification Plan

### Automated Tests (BẮT BUỘC - Desktop & Mobile)
- **Script kiểm thử chính:** [test_e2e_curator.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_e2e_curator.py)
- **Lệnh chạy test:** `python scratch/test_e2e_curator.py`
- **Kịch bản test:**
  1. Load trang chủ trên cả PC và Mobile để kiểm tra danh sách BĐS hiển thị đầy đủ, phân trang đúng.
  2. Xác minh không có lỗi Javascript xuất hiện ở tab Console liên quan đến việc nạp render module.

### Manual Verification
- Đăng nhập Admin: Xác nhận hiển thị thông tin Admin Card (Checkboxes, đầu chủ, SĐT, tags).
- Đăng xuất: Xác nhận hiển thị Client Card công khai bảo mật.
- Kiểm tra các bộ lọc và sắp xếp hoạt động chính xác.

---

## Files touched
- `docs/stories/_inbox/US-094A3_lego_frontend_render.md`
- `static/js/lego_render_client.js`
- `static/js/lego_render_admin.js`
- `static/js/lego_core.js`
- `index.html`
