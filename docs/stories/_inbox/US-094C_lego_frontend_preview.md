---
id: US-094C
status: accepted
date: 2026-06-15
size: S
---

# US-094C: Cô lập Module Chi tiết & Carousel thực tế của Khách hàng

## User story
**As a** Developer  
**I want** cô lập module render chi tiết modal dành cho Khách hàng, Swiper image carousel, và lightbox phóng to ảnh từ index.html ra static/js/lego_detail_client.js  
**So that** làm gọn index.html, mô-đun hóa giao diện xem chi tiết của Khách hàng và đảm bảo hiệu năng hoạt động mượt mà cho trải nghiệm vuốt chạm/zoom ảnh.

## Acceptance
- [x] Tạo tệp `static/js/lego_detail_client.js` để đóng gói toàn bộ logic xem chi tiết và carousel của Khách hàng.
- [x] Tách biệt phần render chi tiết cho Khách hàng từ hàm `openS` gốc và di chuyển vào `LegoDetailClient.render(p, sbodyElement)`.
- [x] Di chuyển hàm `setupScrollCarousel` và `openLightboxForCarousel` cùng toàn bộ cơ chế lightbox (zoom, swipe, keydown, thumbnails, drag) sang `lego_detail_client.js`.
- [x] Di chuyển các hàm gallery phụ trợ (`buildG`, `gm`, `ua`) sang `lego_detail_client.js` hoặc làm sạch nếu không còn sử dụng nhưng đảm bảo không gây lỗi runtime.
- [x] Đấu nối an toàn vào `index.html`, kiểm soát bằng module nạp ở đầu trang và duy trì 100% khả năng tương thích ngược cho cả giao diện Khách hàng lẫn Admin.
- [x] Đạt tỷ lệ 100% PASS cho bộ kiểm thử E2E Playwright trên cả giao diện Desktop và Mobile.

## Solution

### 1. LegoDetailClient Module (`lego_detail_client.js`)
*   Định nghĩa đối tượng toàn cục `window.LegoDetailClient`.
*   Phương thức `LegoDetailClient.render(p, container)`: Dựng HTML chi tiết của Khách hàng, bao gồm carousel hiển thị ảnh nhà (`#carouselClientDetail`), lưới thông số kỹ thuật (giá bán, diện tích, đơn giá, quận, phường, kết cấu...), phần mô tả public, và khung tương tác phản hồi (gửi yêu cầu Zalo, hẹn xem nhà).
*   Đóng gói hàm `setupScrollCarousel` và `openLightboxForCarousel` làm các phương thức nội bộ hoặc xuất bản qua global `window` để Admin view vẫn gọi được (vì Admin vẫn cần dùng lightbox và setup carousel cho ảnh nhà/sổ đỏ).
*   Đóng gói toàn bộ biến trạng thái của lightbox (`lbIdx`, `currentImgs`, `lbCw`, `lbImgScale`, v.v.) và các hàm điều hướng (`lbMove`, `goToLb`, `renderLbThumbs`, `updateLbThumbsUI`, `isLbVideo`).
*   Bảo toàn các bộ lắng nghe sự kiện (event listeners) của lightbox: `touchstart`, `touchmove`, `touchend` trên `#lbMain`, và `keydown` điều hướng bằng phím mũi tên trái/phải, phím Escape.

### 2. Tương thích ngược & Liên kết trong `index.html`
*   Nạp tệp script `static/js/lego_detail_client.js` ở thẻ `<head>` của `index.html`.
*   Hàm `openS` trong `index.html` khi kiểm tra `isAdmin` là `false` sẽ gọi `LegoDetailClient.render(p, sbody)`.
*   Giữ nguyên các thẻ HTML overlay (`#ov`, `#lbOverlay`) trong `index.html` làm khung chứa để module Javascript thao tác DOM.

---

## 📋 Implementation Plan
Tham khảo kế hoạch triển khai chi tiết tại [implementation_plan.md](file:///C:/Users/Khang%20Ngo/.gemini/antigravity/brain/595fc691-aac4-4d6b-9257-a1e94612755c/implementation_plan.md).

---

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát cấu trúc HTML và các sự kiện click trong phần view Khách hàng của `openS`
  - [x] Khảo sát các biến toàn cục liên quan đến lightbox (`lbIdx`, `currentImgs`, v.v.) và các hàm phụ trợ
- [x] **Triển khai Code:**
  - [x] Tạo tệp `static/js/lego_detail_client.js`
  - [x] Di chuyển và đóng gói logic lightbox và carousel vào `lego_detail_client.js`
  - [x] Triển khai `LegoDetailClient.render` để sinh giao diện chi tiết cho Khách hàng
  - [x] Sửa đổi `index.html`: nạp script mới, lược bỏ các hàm đã di chuyển và cấu trúc lại `openS`
- [x] **Kiểm thử & Bàn giao:**
  - [x] Chạy kiểm thử tự động Playwright E2E đa thiết bị local
  - [x] Tạo pull request / merge nhánh `feature/US-094C` vào `main`
  - [x] Bàn giao PO kiểm duyệt tính năng trên môi trường live

---

## 🧠 Retro, Lessons Learned & Good Practices
1. **Lego Frontend Separation**: Việc cô lập giao diện xem chi tiết của Khách hàng, Swiper image carousel, và lightbox ra `lego_detail_client.js` đã làm gọn `index.html` và tăng tính mô-đun hóa của dự án.
2. **Đảm bảo tương thích ngược**: Xuất các hàm điều khiển và các biến lightbox cốt lõi qua `window` giúp màn hình quản trị Admin và các thư viện cũ hoạt động hoàn hảo không lỗi runtime.
3. **Kinh nghiệm viết E2E Playwright**: Chú ý phân biệt trạng thái ẩn/hiện của các phần tử DOM. Những phần tử ẩn bằng `opacity: 0` (như `#lbOverlay`) vẫn được tính là hiển thị trong layout, do đó cần chờ qua điều kiện lớp `:not(.open)`. Những phần tử ẩn bằng `display: none` (như `#ov`) cần dùng `state="hidden"`.

---

## Verification Plan

### Automated Tests (BẮT BUỘC - Desktop & Mobile)
- **Script kiểm thử chính:** [test_e2e_curator.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_e2e_curator.py)
- **Lệnh chạy test:** `python scratch/test_e2e_curator.py`
- **Kịch bản test:**
  1. Click xem chi tiết một căn nhà từ giao diện Client, xác nhận modal hiển thị đầy đủ thông tin, ảnh và có carousel trượt hoạt động.
  2. Click phóng to ảnh để mở lightbox, kiểm tra các phím điều hướng và thao tác vuốt chạm.

### Manual Verification
- Kiểm tra tính tương thích của lightbox khi nhấp vào ảnh từ giao diện Admin.
- Xác nhận các nút hành động phản hồi Zalo/hẹn xem hoạt động đúng đường link.

---

## Files touched
- `docs/stories/_inbox/US-094C_lego_frontend_preview.md`
- `static/js/lego_detail_client.js`
- `index.html`
