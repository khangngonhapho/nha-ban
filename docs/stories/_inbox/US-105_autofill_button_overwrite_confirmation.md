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

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Sự cố / Khó khăn phát sinh (Incidents & Challenges)
- **Lỗi Encoding Tiếng Việt khi Tải Prompt**: Khi xuất nội dung Google Doc chứa System Prompt tiếng Việt, `requests.get` mặc định giải mã theo chuẩn ISO-8859-1 hoặc CP1252 làm xuất hiện lỗi vỡ phông chữ (garbled text). Khắc phục bằng cách gán tường minh `response.encoding = 'utf-8'`.
- **Kẹt phân quyền thư mục khi dựng EXE**: Khi build bằng PyInstaller, thư mục `dist` thỉnh thoảng bị lỗi phân quyền do tệp read-only hoặc system file khiến quá trình clean thư mục thất bại. Đã giải quyết bằng lệnh `attrib -r -s -h dist\* /s /d`.
- **Đường dẫn đóng gói PyInstaller**: Dữ liệu static đính kèm dạng `datas` khi biên dịch chế độ `onedir` sẽ được gom vào thư mục con `_internal` nhưng khi chạy runtime, PyInstaller sẽ giải nén trực tiếp vào thư mục gốc `sys._MEIPASS`. Do đó, cần kiểm tra cả hai đường dẫn fallback động để đảm bảo ứng dụng chạy mượt mà cả môi trường debug lẫn production.

### 2. Thực tiễn Tốt (Good Practices)
- **Tự động bắt Dialog trong Playwright**: Đối với các tính năng dùng hộp thoại xác nhận `confirm()`, luôn cấu hình Playwright `page.on('dialog', lambda d: d.accept())` để tránh kịch bản kiểm thử bị treo (hanging) do chờ tương tác từ người dùng.
- **Cache-Busting Tự động**: Tích hợp công cụ tự động tăng số phiên bản static resources (`?v=...`) qua pre-commit hook giúp giảm thiểu triệt để lỗi người dùng bị kẹt giao diện cũ trên thiết bị di động do cache trình duyệt.

