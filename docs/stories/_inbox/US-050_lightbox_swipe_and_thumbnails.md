---
id: US-050
status: accepted
date: 2026-05-30
size: S
---

# US-050: Hỗ trợ lướt xem ảnh tiếp theo và thanh xem trước ảnh nhỏ khi phóng to hình (Lightbox Photo Swipe & Thumbnails Strip)

## User story
**As a** Khách hàng / Admin
**I want** to be able to swipe or click navigation buttons to view subsequent photos directly inside the enlarged lightbox view, and see a horizontal strip of small thumbnails underneath the main image
**So that** I can seamlessly browse all property images in high resolution without having to close the lightbox and reopen other photos, significantly enhancing the visual user experience and supporting KPI 1 (Chính xác thông tin & Curation).

## Acceptance
- [x] **Điều hướng hình ảnh trong chế độ phóng to (Lightbox Carousel Navigation):**
  - Khi click phóng to một bức ảnh từ carousel chi tiết, lightbox phóng to cung cấp các nút điều hướng Trái (`‹`) và Phải (`›`), hỗ trợ phím mũi tên bàn phím và hỗ trợ thao tác vuốt (swipe) để dễ dàng di chuyển mượt mà sang các ảnh trước/sau của căn nhà.
- [x] **Thanh xem trước hình ảnh nhỏ (Horizontal Thumbnails Strip):**
  - Hiển thị một hàng ngang hình ảnh xem trước thu nhỏ (thumbnails) ngay bên dưới ảnh lớn phóng to chính.
  - Hình ảnh nhỏ đang hiển thị có đường viền highlight màu vàng gold rực rỡ và độ mờ 100% để dễ phân biệt.
  - Khi click vào bất kỳ hình nhỏ nào, ảnh lớn phía trên sẽ lập tức cập nhật chuyển tiếp mượt mà sang hình ảnh đó và cuộn mượt mà hình nhỏ vào giữa thanh xem trước.
- [x] **Thiết kế tối giản và mượt mà (Clean & Premium Responsive Design):**
  - Giao diện lightbox tối giản trên nền đen mờ mượt mà, căn chỉnh tối ưu trên cả thiết bị di động (mobile-friendly) và máy tính (desktop-friendly).

## Solution
- **Chuyển đổi hoàn toàn cơ chế Zoom:** Thay thế hàm đơn lẻ `openZoomOverlay(url)` trong `setupScrollCarousel` bằng helper tích hợp `window.openLightboxForCarousel(imageUrls, idx)`.
- **Đồng bộ hóa Lightbox (`lbOverlay`):** 
  - Đặt `currentImgs` bằng danh sách ảnh của carousel tương ứng khi click.
  - Gọi hàm `openLb(index)` để mở bộ Lightbox cao cấp tích hợp đầy đủ khả năng vuốt trái/phải, phím điều hướng và danh sách ảnh nhỏ thu nhỏ (`lbThumbs`).
- **Thao tác Bàn phím nhanh:** Tích hợp bộ lắng nghe sự kiện phím toàn cục `keydown` để chuyển tiếp ảnh bằng nút mũi tên Trái/Phải và tắt nhanh bằng phím `Escape`.

## 📋 Implementation Plan & Execution
- **Bước 1:** Bổ sung helper `openLightboxForCarousel` và gắn sự kiện lắng nghe bàn phím `keydown`.
- **Bước 2:** Chỉnh sửa hàm `setupScrollCarousel` để thay thế `openZoomOverlay` bằng `openLightboxForCarousel`.
- **Bước 3:** Thử nghiệm độc lập trên cả View Admin và View khách hàng.

## Verification Plan
- **Incognito & Customer View:** Đạt. Khi click ảnh trong carousel chi tiết khách hàng, lightbox mở ra hỗ trợ lướt xem các ảnh tiếp theo và hiển thị thanh hình nhỏ cực kỳ trực quan.
- **Admin Curation View:** Đạt. Khi click ảnh trong các carousel biên tập (`carouselNha`, `carouselSo`), lightbox mở ra đồng nhất với View khách, hỗ trợ đầy đủ các phím điều hướng Trái/Phải/Esc và vuốt mượt mà.

## Files touched
- [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html)
