---
id: US-070
status: accepted
date: 2026-06-03
size: S
---

# US-070: Sửa trùng lặp System ID trên Sheets và khôi phục SQLite hợp nhất từ hai sheet

## User story
**As an** Admin
**I want** quét sạch toàn bộ System ID bị trùng lặp trên Google Sheets và khôi phục cơ sở dữ liệu SQLite cục bộ đầy đủ bao gồm cả các căn gõ tay.
**So that** dữ liệu toàn hệ thống được chuẩn hóa sạch sẽ và đồng bộ khớp 100%.

## Acceptance
- Có một script Python `scratch/fix_duplicate_system_ids.py` để tự động phát hiện các dòng trùng lặp `System ID` trên sheet Pool/Source, sinh System ID độc nhất mới và ghi đè cập nhật lại sheet.
- Nâng cấp script `restore_db_from_sheets.py` để đọc và kết hợp dữ liệu từ cả 2 sheet Pool (ảnh thô) và Source (thông tin curated) nối bằng `System ID` để khôi phục đầy đủ SQLite.
- SQLite sau khi khôi phục phải chứa đầy đủ thông tin của các căn gõ tay và các căn cào tự động cùng thông tin public của chúng.

## Solution
- Viết mới `scratch/fix_duplicate_system_ids.py` sử dụng thư viện gspread.
- Chỉnh sửa `restore_db_from_sheets.py` để mở và kết nối dữ liệu từ 2 sheet.

## Files touched
- `scratch/fix_duplicate_system_ids.py`
- `restore_db_from_sheets.py`
