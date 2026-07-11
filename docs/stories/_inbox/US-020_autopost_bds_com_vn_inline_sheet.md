---
id: US-020
status: done
date: 2026-05-22
size: M
replaces: US-019
---

# US-020: Tích hợp nút Đăng tin batdongsan.com.vn vào sheet Source

## User story
**As an** *Admin của Khang Ngô Nhà Phố*
**I want** *đăng tin tự động lên batdongsan.com.vn bằng một Checkbox inline trực tiếp trên dòng trong sheet Source*
**So that** *tôi có thể dễ dàng quản lý bài đăng, tiết kiệm thời gian vận hành và tránh được các lỗi thao tác thủ công phức tạp*

## Acceptance
- [x] Cột Checkbox `Đăng BDS` (Cột AN - Cột thứ 40) xuất hiện và được cấu hình định dạng Hộp kiểm trên tab `Source` của file Public `BDS_KhangNgo_Source`.
- [x] Khi Admin tick chọn vào checkbox `Đăng BDS` ở một dòng:
  - Bot local phát hiện lập tức, gọi Google Sheets API để reset checkbox đó về `FALSE` (trả về trạng thái trống) ngay lập tức nhằm chống click đúp.
  - Cập nhật ô Trạng thái (`trang_thai` - Cột AK - Cột thứ 37) của dòng đó thành `"🔄 Đang đăng..."`.
- [x] Bot local (`auto_post_server.py`) quét Google Sheets thông qua Sheets API định kỳ mỗi 10 giây (nâng cấp từ chu kỳ 5 phút cũ) để phát hiện sự kiện tick đăng tin.
- [x] Bot local trích xuất chính xác, đầy đủ các trường thông số của dòng đó (Diện tích, Giá, hướng, số tầng, số phòng ngủ, số toilet, mô tả, tiêu đề, và 10 ảnh) để nạp vào Playwright.
- [x] Khắc phục triệt để lỗi lệch cột (Align Schema) trong script Python `auto_post_server.py` hiện tại (đổi index COL_GIO_DANG từ 34 -> 36, COL_TRANG_THAI từ 35 -> 37, và thêm COL_DANG_BDS = 40) để khớp 100% với schema 39 cột thực tế của Sheet Source.
- [x] Định vị chính xác dòng cần cập nhật trạng thái bằng **System ID** (Cột thứ 38 - Cột AL) thay vì tìm theo tiêu đề bài viết cũ để tránh trùng lặp hoặc sai sót.
- [x] Sau khi Bot Playwright chạy xong và xác nhận thanh toán/đăng tin thành công:
  - Nếu thành công: Cập nhật cột `trang_thai` (Cột AK) thành `"✅ Đã đăng lúc [HH:MM]"` (hoặc link bài đăng).
  - Nếu thất bại: Cập nhật cột `trang_thai` (Cột AK) thành `"❌ Thất bại: [Lý do]"` để Admin nắm được thông tin.

## Solution

> [!note]- Configuration
> Thay đổi tần suất quét và cấu hình cột trong Bot local Python (`auto_post_server.py`) để tối ưu hóa tốc độ nhận diện:
> ```python
> SPREADSHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0'
> COL_GIO_DANG = 36      # Cột AJ (Index 35)
> COL_TRANG_THAI = 37    # Cột AK (Index 36)
> COL_DANG_BDS = 40      # Cột AN (Index 39 - Checkbox trigger)
> ```

> [!note]- Input
> Payload dữ liệu của một dòng được Bot đọc lên qua Google Sheets API và chuyển giao cho Playwright:
> ```json
> {
>   "id": "Mã Khang Ngô",
>   "title": "Tiêu đề Public",
>   "area": "DT Thực tế",
>   "floors": "Số Tầng",
>   "mat_tien": "Mặt Tiền",
>   "price": "Giá Public",
>   "district": "Quận",
>   "ward": "Phường",
>   "loai_hinh": "Loại hình",
>   "huong": "Hướng",
>   "rong_hem": "Đường trước nhà (m)",
>   "description": "Mô tả Public",
>   "images": ["Link ảnh 1", "Link ảnh 2", "..."],
>   "phuong_cu": "Phường cũ (AI)",
>   "so_pn": "Số phòng ngủ",
>   "so_wc": "Số nhà vệ sinh",
>   "ten_duong": "Tên đường",
>   "system_id": "System ID"
> }
> ```

> [!note]- Output / Format
> Trạng thái được cập nhật trực tiếp tại cột Trạng thái (Cột AK - Cột thứ 37) theo các dạng:
> - Đang xử lý: `"🔄 Đang đăng..."`
> - Đăng thành công: `"✅ Đã đăng lúc HH:MM"` hoặc trỏ hyperlink trực tiếp đến URL bài đăng.
> - Đăng thất bại: `"❌ Thất bại: [Lý do]"`

> [!note]- Key logic
> - **Cơ chế Polling 10 giây:** Thay đổi chu kỳ schedule từ 5 phút xuống 10 giây trong luồng chạy ngầm của Python Flask server.
> - **Reset Checkbox tức thì:** Ngay sau khi phát hiện dòng có `Đăng BDS` = `TRUE`, Bot local lập tức gọi API update ô Checkbox đó về `FALSE` và set Trạng thái thành `"🔄 Đang đăng..."` trước khi chạy Playwright. Việc này đảm bảo chống spam click và loại bỏ nguy cơ deadlock/chạy đúp.
> - **Định vị theo System ID:** Thay vì tìm kiếm dòng cập nhật dựa trên tiêu đề bài đăng (dễ trùng và sai lệch cột), Bot lưu System ID và quét cột AL của sheet Source để cập nhật chính xác dòng đó.
> - **Align Schema 100%:** Ánh xạ lại toàn bộ index các trường dữ liệu cào trong code Python để khớp chính xác tuyệt đối với cấu trúc cột trên tab `Source`.

## Verification Plan

> [!check]- Automated Tests
> - Chạy kiểm tra kết nối Google Sheets bằng cách in danh sách hàng đợi ra Console của Python xem có nhận diện đúng Checkbox = TRUE và reset Checkbox = FALSE hay không.
> - Chạy thử Playwright với chế độ `headless=True` (nếu cần test ngầm) hoặc `headless=False` (xem thực tế) để xác nhận việc điền form và login batdongsan.com.vn không bị lỗi selector.

> [!check]- Manual Verification
> - **Bước 1:** Khởi động Bot Python local trên máy tính cá nhân bằng cách chạy file `.bat` hoặc lệnh `python auto_post_server.py`.
> - **Bước 2:** Mở file Google Sheets Public `BDS_KhangNgo_Source` (tab `Source`), chọn một dòng đã được duyệt và tick chọn checkbox tại cột `Đăng BDS` (Cột AN).
> - **Bước 3:** Quan sát xem trong vòng 10 giây, ô Checkbox có tự động uncheck về trống và ô trạng thái tại cột AK chuyển sang `"🔄 Đang đăng..."` hay không.
> - **Bước 4:** Quan sát Chrome tự động bật lên, điền đầy đủ các thông tin Diện tích, Giá, hướng, số tầng, số phòng ngủ, số toilet, mô tả, tiêu đề, và tiến hành upload ảnh lên hệ thống batdongsan.com.vn.
> - **Bước 5:** Sau khi Bot hoàn tất giao dịch thanh toán và đăng tin thành công, kiểm tra xem ô trạng thái tại cột AK trên Sheet có tự động chuyển thành `"✅ Đã đăng lúc [Giờ]"` hay không.

## Files touched
- `d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/pool_sheet_schema.md` — Cấu trúc cột hệ thống
- `d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/SOURCE_OF_TRUTH.md` — Ghi nhận thay đổi dự án
- `d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_backend_v3.gs` — Apps Script Backend
- `d:/LHTBrain/01_PROJECTS/admin-nha-ban/automation/auto_post_server.py` — Script Bot local đăng tin
