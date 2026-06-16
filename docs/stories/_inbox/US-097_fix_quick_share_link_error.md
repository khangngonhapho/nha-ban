---
id: US-097
status: draft
date: 2026-06-16
size: S
---

# US-097: Sửa lỗi không bấm tạo được link Công Khai Nhanh để share cho khách hàng

## User story
**As an** Admin / Người curation rổ hàng
**I want** Khi bấm vào nút "⚡ Tạo Link Công Khai Nhanh" trong Modal Tạo Link Gửi Khách, link được tạo ra chính xác và tự động sao chép vào clipboard thành công
**So that** Tôi có thể gửi link rổ hàng nhanh chóng cho khách hàng mà không gặp lỗi Javascript làm đứng giao diện hoặc không phản hồi.

## Acceptance
- [ ] **Khắc phục lỗi ReferenceError:**
  - Nút "⚡ Tạo Link Công Khai Nhanh (Khách tự nhập SĐT)" trong `#linkModal` khi click không còn báo lỗi `ReferenceError: executeGenerateQuickLink is not defined`.
- [ ] **Phục hồi hàm `executeGenerateQuickLink`:**
  - Định nghĩa lại hàm `executeGenerateQuickLink` và gán lên đối tượng `window` (`window.executeGenerateQuickLink`) trong module `static/js/lego_helpers.js`.
- [ ] **Tính năng của hàm hoạt động đúng:**
  - Khi chỉ chọn 1 căn: Tạo link có dạng `${baseUrl}?s=${systemId}`.
  - Khi chọn nhiều căn: Mã hoá danh sách các `system_id` bằng Base64URL-safe và tạo link dạng `${baseUrl}?b=${encodedIds}`.
  - Đóng modal `#linkModal` (xóa class `open`).
  - Tự động copy link vào clipboard và hiển thị thông báo alert/toast thành công: `Đã copy link Công Khai Nhanh thành công!...`.

## Solution

### Nguyên nhân gốc rễ (Root Cause Analysis)
Trong quá trình tái cấu trúc giao diện trang chủ theo kiến trúc Lego Frontend (US-094E / US-094), các hàm Javascript thô đã được tách biệt và di chuyển từ file [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html) sang [static/js/lego_helpers.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_helpers.js). 
Tuy nhiên, hàm `executeGenerateQuickLink` đã bị bỏ sót và không được sao chép vào `static/js/lego_helpers.js`. Do nút bấm trong file HTML vẫn gọi `executeGenerateQuickLink()` inline nên xảy ra lỗi crash Javascript do hàm này không tồn tại.

### Giải pháp đề xuất (Proposed Solution)
1. Khôi phục logic của hàm `executeGenerateQuickLink` từ file nháp trích xuất [scratch/index_extracted.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/index_extracted.js).
2. Định nghĩa hàm này làm thuộc tính toàn cục trên `window` trong tệp [static/js/lego_helpers.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_helpers.js):
   ```javascript
   window.executeGenerateQuickLink = function() {
     if (SELECTED_IDS.size === 0) {
       alert('Vui lòng chọn ít nhất 1 căn nhà để tạo link!');
       return;
     }
     try {
       const baseUrl = window.location.origin + window.location.pathname;
       const count = SELECTED_IDS.size;
       let shareUrl = '';

       if (count === 1) {
         const singleId = [...SELECTED_IDS][0];
         const house = DATA.find(p => String(p.id) === String(singleId));
         const systemId = house ? house.system_id : singleId;
         shareUrl = `${baseUrl}?s=${systemId}`;
       } else {
         // Mã hoá trực tiếp danh sách System ID bằng Base64URL safe
         const sysIdList = Array.from(SELECTED_IDS).map(id => {
           const house = DATA.find(p => String(p.id) === String(id));
           return house && house.system_id ? house.system_id : id;
         }).join(',');
         const encodedIds = window.btoa(unescape(encodeURIComponent(sysIdList)))
           .replace(/=/g, '')
           .replace(/\+/g, '-')
           .replace(/\//g, '_');
         shareUrl = `${baseUrl}?b=${encodedIds}`;
       }

       // Đóng Modal
       document.getElementById('linkModal').classList.remove('open');

       // Sao chép link vào clipboard
       const ta = document.createElement('textarea');
       ta.value = shareUrl;
       ta.style.cssText = 'position:fixed;left:0;top:0;opacity:0;';
       document.body.appendChild(ta);
       ta.focus(); ta.select();
       document.execCommand('copy');
       document.body.removeChild(ta);
       
       alert(`Đã copy link Công Khai Nhanh thành công!\n(Gồm ${count} căn)\n\nKhách mở link này sẽ tự nhập Tên và Số điện thoại để mở khóa xem nhà.`);
     } catch (e) {
       alert('Có lỗi xảy ra: ' + e.message);
     }
   };
   ```

## 📋 Implementation Plan
- **Cách tiếp cận:** Thêm hàm `executeGenerateQuickLink` vào file [static/js/lego_helpers.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_helpers.js).
- **Các bước triển khai:**
  1. Thêm code hàm `executeGenerateQuickLink` vào cuối phần Share Link Generation trong [static/js/lego_helpers.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_helpers.js).
  2. Test click nút "⚡ Tạo Link Công Khai Nhanh" trên giao diện Admin để kiểm tra xem link có được copy vào clipboard và modal có đóng lại không.

## 📝 Task Checklist (TODO)
- [ ] **Thiết kế & Lập kế hoạch:**
  - [x] Tạo US-097 và cập nhật `INDEX.md`, `NEXT_SESSION.md`.
  - [ ] Đề xuất phương án thiết kế sửa lỗi lên PO/User.
- [ ] **Triển khai Code:**
  - [ ] Khôi phục và bổ sung hàm `executeGenerateQuickLink` vào `static/js/lego_helpers.js`.
- [ ] **Kiểm thử & Bàn giao:**
  - [ ] Kiểm tra tạo link Công Khai Nhanh với 1 căn nhà.
  - [ ] Kiểm tra tạo link Công Khai Nhanh với nhiều căn nhà (danh sách ID mã hóa Base64).
  - [ ] Xác nhận không còn lỗi ReferenceError trong Console.
  - [ ] Cập nhật Change Log trong `SOURCE_OF_TRUTH.md` và chuyển trạng thái thành `accepted`.

## Verification Plan

### Manual Verification
1. Truy cập Web Admin (`?pwd=trang`).
2. Tích chọn ít nhất 1 căn nhà (ví dụ 1 hoặc 3 căn).
3. Click ⚙️ (Speed Dial) -> Click 🔗 (Tạo link gửi khách).
4. Click nút **⚡ Tạo Link Công Khai Nhanh (Khách tự nhập SĐT)**.
5. Xác nhận:
   - Modal biến mất.
   - Pop-up thông báo copy thành công hiển thị.
   - Khi dán vào trình duyệt/text editor, link có dạng `http://.../?s=...` (nếu chọn 1 căn) hoặc `http://.../?b=...` (nếu chọn nhiều căn).
   - Console của trình duyệt không báo lỗi đỏ `executeGenerateQuickLink is not defined`.

## Files touched
- [static/js/lego_helpers.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_helpers.js)
