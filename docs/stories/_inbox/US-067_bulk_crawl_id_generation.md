---
id: US-067
status: accepted
date: 2026-06-03
size: S
---

# US-067: Sinh ID tự động khi cào hàng loạt và luồng đẩy tin không trùng lặp dữ liệu

## User story
**As a** System
**I want** tự động sinh Mã Khang Ngô (ID) và System ID ngay khi cào tin thô hàng loạt lưu vào SQLite và Pool sheet, đồng thời đồng bộ thẳng dữ liệu curated sang Source sheet khi lên sóng.
**So that** dữ liệu Curation không bị trùng lặp dư thừa giữa Pool và Source, đồng thời tránh kích hoạt vòng lặp chạy ngầm Apps Script.

## Acceptance
- Trong `crawl_pipeline.py`, khi cào tin hàng loạt và lưu vào SQLite, tự động gọi hàm sinh `Mã Khang Ngô (ID)` và `System ID` để ghi nhận từ đầu.
- Khi đẩy lên sheet Pool lần đầu, dòng dữ liệu chứa đầy đủ ID và System ID.
- Khi bấm "Lên sóng", dữ liệu biên tập mới (Tiêu đề, Mô tả, Giá Public) được ghi đè trực tiếp vào sheet **Source** và SQLite.
- Trên sheet **Pool**, chỉ ghi nhận `Last Sync` (Cột BZ) và hình ảnh, không tick lại checkbox `Duyệt Public` để tránh đè ngược dữ liệu cũ.

## Solution
- Thêm logic sinh ID trong hàm `save_raw_to_sqlite` của `crawl_pipeline.py`.
- Sửa hàm `execute_publish_listing` trong `curator_server.py` để cập nhật trực tiếp sang Source và chỉ ghi nhận thời gian đồng bộ bên Pool.

## Files touched
- `crawl_pipeline.py`
- `curator_server.py`
