---
id: US-105
status: accepted
date: 2026-06-22
size: S
---

# US-105: Hiện Nút "Tự Động Điền" Cho Căn Đã Lên Sóng & Hỏi Xác Nhận Thay Thế Thông Tin AI

## User story
**As an** Admin (Môi giới quản trị)
**I want** có nút "Tự động điền" Tiêu đề/Mô tả Public bằng AI hiển thị cho cả các căn đã lên sóng (đã xuất bản) chứ không chỉ riêng các căn trong Pool thô
**So that** tôi có thể dễ dàng tối ưu, tạo lại nội dung Public bằng AI cho bất kỳ căn nhà nào, đồng thời nhận được hộp thoại cảnh báo xác nhận trước khi hệ thống ghi đè thông tin cũ để tránh mất mát dữ liệu biên tập thủ công.

## Acceptance
- [x] Nút "⚡ Tự động điền" hiển thị công khai trên giao diện chi tiết Admin Vercel đối với cả các căn chưa lên sóng (Pool thô) và các căn đã lên sóng (Source).
- [x] Khi bấm nút "Tự động điền", hệ thống hiển thị hộp thoại xác nhận (`confirm`) cảnh báo rằng hành động này sẽ xóa thông tin Tiêu đề public và Mô tả public cũ để thay bằng thông tin mới từ AI.
- [x] Chỉ khi người dùng bấm Xác nhận (OK) thì hệ thống mới gọi API AI và điền thông tin vào các trường input. Nếu người dùng hủy bỏ (Cancel), hành động bị dừng lại và không thay đổi thông tin hiện tại.
- [x] Áp dụng logic hỏi xác nhận tương tự cho nút "🤖 BIÊN TẬP AI" trên giao diện Curator Dashboard (`curator.html` / `curator_html_data.py`).

## Solution

> [!note]- Input
> Không có.

> [!note]- Output / Format
> Hộp thoại xác nhận của trình duyệt (`confirm`) xuất hiện trước khi gọi API OpenAI biên tập.

> [!note]- Key logic
> 1. Trong `static/js/lego_detail_admin.js`, loại bỏ điều kiện ràng buộc `p.isFromPoolOnly ? ... : ''` xung quanh thẻ button `#btnAutoFillCuration` để nút này luôn được render cho tất cả các căn nhà khi mở chế độ xem Admin.
> 2. Trong `static/js/lego_helpers.js`, tại hàm `window.autoFillCurationDetails`, bổ sung một hộp thoại xác nhận `confirm(...)`. Nếu kết quả trả về là `false` (hủy bỏ), lập tức `return` dừng thực thi.
> 3. Trong `curator.html` (chương trình Curator Dashboard chạy offline), tại hàm `runAiCuration()`, bổ sung tương tự một hộp thoại xác nhận `confirm(...)` trước khi gửi request POST đến `/api/ai/generate`.
> 4. Biên dịch lại `curator.html` thành `curator_html_data.py` bằng cách chạy script `scratch/sync_html_data.py`.
> 5. Cấu hình Playwright E2E test `scratch/test_e2e_curation.py` lắng nghe và tự động chấp nhận dialog cảnh báo (`page.on('dialog', lambda d: d.accept())`) để bộ test suite chạy thành công 100% không bị treo.

## 📋 Implementation Plan
- **Cách tiếp cận:** Điều chỉnh logic hiển thị button ở template HTML Detail Admin, bổ sung xác nhận confirm trực tiếp ở frontend JavaScript và cập nhật kịch bản E2E test để tương thích với hộp thoại thông báo.
- **Các bước triển khai:**
  1. Loại bỏ check `p.isFromPoolOnly` cho button `#btnAutoFillCuration` trong `static/js/lego_detail_admin.js`.
  2. Bổ sung `confirm()` trong `static/js/lego_helpers.js` and `curator.html`.
  3. Đồng bộ `curator.html` sang `curator_html_data.py`.
  4. Cấu hình Dialog listener trong `scratch/test_e2e_curation.py`.
  5. Chạy bộ test Playwright E2E để kiểm chứng tính đúng đắn và tự động bump version cache.

## Verification Plan

> [check]- Automated Tests
> Chạy E2E test Playwright:
> ```powershell
> python scratch/test_e2e_curation.py
> ```

> [check]- Manual Verification
> - Đăng nhập quyền Admin trên Vercel, chọn một căn đã lên sóng (Source), xác nhận nút "⚡ Tự động điền" hiển thị.
> - Bấm nút "⚡ Tự động điền", chọn Cancel, xác nhận thông tin không đổi. Chọn OK, xác nhận thông tin được điền bằng AI thành công.
> - Trên Curator Dashboard, chọn một căn, bấm "🤖 BIÊN TẬP AI", kiểm tra hiển thị xác nhận ghi đè tương tự.
