---
id: US-086
status: accepted
date: 2026-06-11
size: S
---

# US-086: Fix lỗi tạo bộ sưu tập

## User story
**As an** Admin / Product Owner
**I want** Các tính năng lưu, xem, sửa và xóa bộ sưu tập hoạt động chính xác tuyệt đối, có giao diện dễ đọc trên cả thiết bị di động lẫn máy tính
**So that** Quản lý phân loại rổ hàng chuyên nghiệp, nhanh chóng tạo danh sách gửi khách hàng mà không bị lỗi hiển thị hoặc lệch dữ liệu giữa tin thô (Pool) và tin đã lên sóng (Source).

## Acceptance
- [ ] **Khắc phục lỗi hiển thị màu chữ (White-on-White):**
  - Các nút chọn Bộ sưu tập hiện có trong Slide-up Sheet lưu (`#colSaveModal`) và danh sách Bộ sưu tập trong Slide-up Sheet xem (`#colViewModal`) phải hiển thị chữ màu tối rõ ràng (`#1c1c1e` hoặc `var(--text)`) trên nền sáng của Modal Sheet (`#fff`).
- [ ] **Bỏ chọn toàn bộ Checkbox sau khi lưu thành công:**
  - Khi lưu các căn nhà đã chọn vào một Bộ sưu tập mới hoặc Bộ sưu tập hiện có thành công, hệ thống phải tự động uncheck toàn bộ các checkbox chọn căn (`.card-sel`) trên giao diện danh sách.
- [ ] **So khớp ID duy nhất bằng mã `system_id`:**
  - Bộ lọc danh sách và bộ sưu tập chỉ sử dụng duy nhất mã `system_id` để so khớp dữ liệu (không sử dụng Mã Khang Ngô) để đảm bảo tính đồng nhất, ổn định và tránh lỗi lệch dữ liệu.

## Solution

### Nguyên nhân gốc rễ (Root Cause Analysis)
1. **Lỗi White-on-White trong Modal:**
   Các modal `#colSaveModal` và `#colViewModal` sử dụng lớp `.sheet` có nền màu trắng (`#fff`). Tuy nhiên, các nút lưu và các mục bộ sưu tập lại được thiết lập inline style kế thừa từ dark-theme cũ (chữ màu trắng `color: #fff`). Điều này làm cho chữ hiển thị trên modal trắng bị tàng hình.
2. **Không Uncheck UI Checkbox:**
   Trong các hàm tạo và lưu bộ sưu tập, hệ thống thực hiện xóa `SELECTED_IDS` nhưng bỏ sót việc đặt `checked = false` cho các thẻ input checkbox `.card-sel` trên DOM.
3. **So khớp trùng lặp ID:**
   Sử dụng cả Mã Khang Ngô và System ID gây ra sự không đồng nhất và dễ lỗi hiển thị khi chuyển đổi trạng thái tin. Chuyển sang so khớp duy nhất bằng `system_id` (hoặc fallback `id` nếu không có `system_id`).

### Giải pháp đề xuất (Proposed Solution)
Chúng ta thực hiện sửa đổi trong `index.html`:
1. **Sửa CSS modal buttons:**
   Thay đổi inline style của các nút chọn BST trong `openColSaveModal()` và `openColViewModal()` sang chữ màu tối (`color: #1c1c1e`) và nền xám nhạt (`background: rgba(0,0,0,0.03)`).
2. **Bổ sung Uncheck DOM Checkbox:**
   Thêm đoạn code sau vào cuối hàm `createNewCollection()` và `saveToExistingCollection()`:
   ```javascript
   document.querySelectorAll('.card-sel').forEach(cb => cb.checked = false);
   ```
3. **Logic so khớp ID duy nhất trong `getFiltered()`:**
   Cập nhật phần lọc bộ sưu tập/favorites để chỉ so khớp duy nhất bằng `system_id` (hoặc fallback là `id` nếu `system_id` trống):
   ```javascript
    if (activeCollectionName) {
      if (activeCollectionName === 'favorites') {
        a = a.filter(p => favs.has(String(p.system_id || p.id)));
      } else if (collections[activeCollectionName]) {
        const colIds = new Set(collections[activeCollectionName].map(String));
        a = a.filter(p => colIds.has(String(p.system_id || p.id)));
      }
    }
   ```

## 📋 Implementation Plan
- **Cách tiếp cận:** Chỉnh sửa trực tiếp file `index.html`.
- **Các bước triển khai:**
  1. Thay thế style và markup trong `openColSaveModal` và `openColViewModal` để sửa màu chữ hiển thị.
  2. Bổ sung logic uncheck tất cả checkbox sau khi tạo/lưu bộ sưu tập thành công.
  3. Cập nhật hàm `getFiltered` để lọc bộ sưu tập/favorites sử dụng duy nhất mã `system_id` (hoặc fallback là `id` nếu `system_id` trống).

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Lập kế hoạch:**
  - [x] Tạo US-086 và cập nhật `INDEX.md`, `NEXT_SESSION.md`.
  - [x] Đề xuất phương án thiết kế sửa lỗi lên PO/User.
- [x] **Triển khai Code:**
  - [x] Sửa giao diện màu chữ nút bấm trong Modal Sheet.
  - [x] Thêm lệnh uncheck checkbox UI khi lưu BST thành công.
  - [x] Cập nhật logic match ID duy nhất `system_id` (fallback `id` nếu trống) trong `getFiltered()`.
- [x] **Kiểm thử & Bàn giao:**
  - [x] Kiểm tra tạo mới BST, lưu đè BST hiện có xem có uncheck UI và màu sắc rõ ràng không.
  - [x] Kiểm tra lọc BST chứa tin thô và tin đã lên sóng so khớp bằng system_id duy nhất.
  - [x] Cập nhật Change Log trong `SOURCE_OF_TRUTH.md` và set status accepted.

## Verification Plan

### Manual Verification
1. Truy cập Web Admin (`?pwd=trang`).
2. Tích chọn 3 căn nhà bất kỳ.
3. Click ⚙️ (Speed Dial) -> Click 📁 (Lưu bộ sưu tập).
4. Xác nhận:
   - Form Lưu hiển thị đúng số căn.
   - Text "Tạo bộ sưu tập mới" và các nút/input hiển thị rõ ràng, không bị white-on-white.
5. Nhập tên BST là `"Test US-086"` -> Bấm **Tạo**.
6. Xác nhận:
   - Pop-up thông báo tạo thành công hiển thị.
   - Toàn bộ checkbox của 3 căn vừa chọn trên màn hình tự động uncheck hoàn toàn.
7. Click icon Tim ở Header -> Xác nhận danh sách hiện ra gồm "Căn nhà đã thích" và "Test US-086" hiển thị trực quan rõ chữ.
8. Bấm chọn `"Test US-086"` -> Xác nhận chỉ lọc hiển thị đúng 3 căn trong bộ sưu tập. Xuất hiện thanh vàng ghim động ở đầu.

## Files touched
- `index.html` — Cập nhật logic Javascript bộ sưu tập và CSS/styles modal liên quan.
