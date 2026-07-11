---
id: US-072
status: accepted
date: 2026-06-03
size: S
---

# US-067: Khắc phục lỗi xuất bản Curation ghi đè thiếu trường & lệch cột Google Sheets

## User story
**As a** Admin
**I want** các căn nhà đã tồn tại trong Pool Sheets khi được duyệt Curation / Lên sóng sẽ ghi đè đầy đủ các trường biên tập (Public ID, Public Title, Public Price, Duyệt Public...) và các cột ảnh sơ đồ mới không làm lệch dữ liệu của sheet.
**So that** toàn bộ rổ hàng curated xuất hiện đầy đủ và chính xác trên giao diện khách hàng (Client View) mà không bị lọc bỏ hay mất ảnh.

## Acceptance
- Khi duyệt / xuất bản một căn đã tồn tại trong Google Sheets Pool, toàn bộ các trường Public và curation (đặc biệt là `Mã Khang Ngô (ID)` và `Duyệt Public`) phải được ghi đè đầy đủ từ SQLite sang Sheets.
- Chèn bổ sung 3 cột `Sơ đồ thửa đất 3`, `Sơ đồ thửa đất 4`, `Sơ đồ thửa đất 5` vào Google Sheets Pool ở các cột 78, 79, 80 để khớp hoàn hảo với 82 cột định nghĩa của Python.
- Dữ liệu `Last Crawl` và `Last Sync` không bị lệch vị trí cột sau khi chèn.
- Các căn nhà Bùi Đình Tuý, Hoà Hưng, Nhiêu Tứ sau khi đẩy lại curation sẽ xuất hiện trên Client View.

## Solution
- Sửa đổi logic `execute_publish_listing` trong `curator_server.py` để biên dịch đầy đủ 82 cột và update toàn bộ dòng dữ liệu của hàng thay vì chỉ đè hình ảnh.
- Viết một script python `scratch/align_sheet_columns.py` để chèn cột tự động qua API gspread.

## Files touched
- `curator_server.py` — Chỉnh sửa hàm `execute_publish_listing` để overwrite toàn bộ 82 cột dữ liệu.
