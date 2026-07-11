---
id: US-019
status: superseded
date: 2026-05-22
size: unknown
superseded_by: US-020
backfilled: true
---

# US-019: [Legacy] Cơ chế tự động đăng tin batdongsan.com.vn cũ qua Web Admin / Hẹn giờ

## Previous behavior
Server Python local (`auto_post_server.py`) khởi chạy dịch vụ Flask lắng nghe tại cổng `8000` với endpoint `/api/post` để nhận dữ liệu từ giao diện Web Admin được host trên Vercel nhằm đẩy vào hàng đợi đăng tin qua Playwright.
Đồng thời, server tích hợp một luồng quét ngầm (Auto-Cronjob) định kỳ mỗi 5 phút quét Google Sheets nội bộ để tìm các dòng có cài đặt giờ đăng (cột Hẹn giờ `COL_GIO_DANG = 34` tức cột AH) và trạng thái trống (`COL_TRANG_THAI = 35` tức cột AI).
Khi phát hiện bài đăng đến giờ hẹn, Bot local sẽ cập nhật trạng thái tạm thời trên Google Sheets thành `"Đang xử lý"` bằng cách tìm theo tiêu đề bài viết (rất dễ bị trùng lặp hoặc sai lệch nếu cấu trúc cột bị thay đổi), sau đó đẩy bài đăng vào hàng đợi Playwright và cập nhật thành `"Đã đăng"` khi hoàn tất.

## Files (trước khi thay)
- `d:/LHTBrain/01_PROJECTS/admin-nha-ban/automation/auto_post_server.py`

## Note
Stub tạo khi US-020 replace. Acceptance gốc không có.
