---
id: US-094F
status: in-progress
date: 2026-06-15
size: M
---

# US-094F: Cô lập Module Chi tiết, Preview & Curation dành riêng cho Admin

## User story
**As a** Developer  
**I want** cô lập toàn bộ logic hiển thị chi tiết của Admin (Admin preview), form biên tập (Editor), form quản lý duyệt tin (Curation), và các tabs quản lý của Admin sang tệp script độc lập `static/js/lego_detail_admin.js`  
**So that** mã nguồn trong `index.html` được tối giản hóa tối đa, phân tách rõ ràng trách nhiệm giữa giao diện Client (Khách hàng) và giao diện Admin (Quản trị), bảo đảm tính bảo mật cao, dễ bảo trì và tránh lỗi hồi quy khi cập nhật các tính năng quản trị.

## Acceptance
- [ ] Tạo mới tệp `static/js/lego_detail_admin.js` chứa module `LegoDetailAdmin`.
- [ ] Tách biệt HTML Template hiển thị chi tiết của Admin (`sbody.innerHTML = ...` khi `isAdmin` hoạt động) ra khỏi `index.html` và chuyển vào phương thức `LegoDetailAdmin.render(p, sbody)`.
- [ ] Di chuyển toàn bộ hệ thống hàm tương tác của Curation Image Editor:
  - `renderImageEditorWidget()`, `reRenderCurationEditorInPlace()`, `refreshImageEditorUI()`, `activeImageMoveOrder()`, `gotoImageEditorSlide()`, `slideImageEditorCarousel()`.
  - Các hàm toggle trạng thái ảnh: `activeImageToggleFacade()`, `activeImageToggleCover()`, `activeImageToggleSodo()`, `activeImageTogglePublic()`.
  - Các trình lắng nghe thao tác vuốt carousel: `handleCarouselTouchStart()`, `handleCarouselTouchMove()`, `handleCarouselTouchEnd()`, `handleCarouselSwipe()`.
  - Các hàm xóa ảnh khỏi danh sách: `removeImageFromPublicLists()`, `removeImageFromSodo()`, `isListingSodoUrl()`.
- [ ] Di chuyển logic tải ảnh local lên Cloudflare R2:
  - `compressImageClientSide()`, `uploadFileToR2()`, `handleLocalImageUpload()`.
- [ ] Di chuyển logic kéo dữ liệu từ rổ thô Pool về:
  - `isPoolRowOnAir()`, `pullListingFromPoolRow()`, `executePullFromPool()`, `uncheckAllCurationImages()`, `openPoolS()`, `onPoolSearchToolKeyup()`.
- [ ] Di chuyển các hàm điều khiển giao diện chi tiết Admin phụ trợ:
  - `toggleAdminAccordion()`, `getPublicImagesFromForm()`, `openZoomOverlay()`, `closeZoomOverlay()`, `checkMoTaCollapse()`, `toggleMotaGocCollapse()`.
- [ ] Di chuyển logic ghi đè/thêm mới dòng vào Google Sheets:
  - `saveSourceChanges()`, `saveNewListingFromPool()`.
- [ ] Liên kết thẻ script mới ở `<head>` của `index.html` và tích hợp alias tương thích ngược toàn diện cho tất cả các biến/hàm trên đối tượng `window`.
- [ ] Viết bộ kiểm thử E2E Playwright chuyên biệt `scratch/test_e2e_curation.py` giả lập đầy đủ luồng chỉnh sửa, lưu thay đổi của Admin đạt 100% SUCCESS.

---

## Solution

### 1. Đóng gói Module `LegoDetailAdmin` (`lego_detail_admin.js`)
- Module `LegoDetailAdmin` sẽ quản lý toàn bộ vòng đời hiển thị chi tiết & chỉnh sửa của Admin.
- Phương thức chính: `LegoDetailAdmin.render(p, sbody)`.
  - Thiết lập HTML template thô cho Admin preview, form Accordion chỉnh sửa thông tin BĐS, Accordion hình ảnh, và Accordion Preview Khách hàng.
  - Sau khi vẽ DOM, tự động thiết lập các trình lắng nghe sự kiện thay đổi dữ liệu (event listener) trên các trường nhập liệu (`editHuong`, `editDuong`, `editDanhGia`, `editTinhTrang`...) để cập nhật trực tiếp (Live Preview) sang panel Preview Khách hàng.
  - Khởi tạo bản đồ thực địa Google Maps `iframe` động dựa trên địa chỉ căn nhà.
  - Khởi tạo 2 carousels ảnh (BĐS & Sổ thửa đất) bằng cách gọi `setupScrollCarousel`.
- Đóng gói logic Image Editor Carousel để quản lý việc xoay ảnh, sửa tags (Facade, Cover, Sổ đỏ, Public) và di chuyển vị trí ảnh.

### 2. Tải ảnh & Lưu Sheets API
- Tích hợp hàm `uploadFileToR2` và trình xử lý upload file local trực tiếp trong module Admin.
- Lưu giữ nguyên vẹn logic Sheets API `saveSourceChanges` và `saveNewListingFromPool` để thực hiện cập nhật cell dữ liệu tương tự như trước.

### 3. Tương thích ngược & Tối giản `index.html`
- Nạp `static/js/lego_detail_admin.js` trong `<head>` của `index.html`.
- Định nghĩa các alias toàn cục trên `window` cho toàn bộ các hàm đã di chuyển để các inline template HTML của Admin không bị lỗi tham chiếu.
- Rút gọn hàm `openS` trong `index.html` bằng cách ủy thách render Admin cho `LegoDetailAdmin.render(p, sbody)`.

---

## 📋 Implementation Plan
Xem chi tiết tại [implementation_plan.md](file:///C:/Users/Khang%20Ngo/.gemini/antigravity/brain/595fc691-aac4-4d6b-9257-a1e94612755c/implementation_plan.md).

---

## 📝 Task Checklist (TODO)
- [ ] **Thiết kế & Khảo sát:**
  - [ ] Khảo sát toàn bộ các hàm Curation & Editor trong `index.html` và lập sơ đồ liên kết dữ liệu.
- [ ] **Triển khai Code:**
  - [ ] Tạo tệp `static/js/lego_detail_admin.js` và chuyển logic render cùng các hàm tương tác sang.
  - [ ] Tích hợp logic upload ảnh R2 và đồng bộ Google Sheets API sang tệp mới.
  - [ ] Làm sạch `index.html`, loại bỏ hơn 1200 dòng lệnh JS & HTML thô, nạp script mới ở đầu trang.
  - [ ] Đăng ký các alias tương thích ngược đầy đủ trên đối tượng `window`.
- [ ] **Kiểm thử & Bàn giao:**
  - [ ] Viết script test E2E Playwright `scratch/test_e2e_curation.py` mô phỏng hành vi của Admin (chỉnh sửa, auto-fill AI, đổi thứ tự ảnh, và lưu sheets).
  - [ ] Chạy bộ kiểm thử E2E đạt 100% PASS.
  - [ ] Merge code và deploy lên Production.

---

## Verification Plan

### Automated Tests
- **Script kiểm thử chính:** [test_e2e_curation.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_e2e_curation.py) [NEW]
- **Kịch bản test:**
  1. Đăng nhập Admin giả lập -> Xem chi tiết căn nhà của Admin.
  2. Kiểm tra hiển thị đầy đủ thông tin thô, accordion form chỉnh sửa, accordion preview khách hàng.
  3. Thay đổi các trường thông tin (Giá bán, tiêu đề, hướng...) -> Xác minh panel Preview Khách hàng cập nhật reactive.
  4. Thực hiện thay đổi tags ảnh (Facade/Sổ đỏ) trong Carousel Editor và lưu -> Kiểm tra dữ liệu đẩy lên mock API sheets chính xác.

---

## Files touched
- `docs/stories/_inbox/US-094F_lego_frontend_curation.md`
- `static/js/lego_detail_admin.js`
- `index.html`
- `docs/stories/INDEX.md`
- `docs/NEXT_SESSION.md`
- `SOURCE_OF_TRUTH.md`
