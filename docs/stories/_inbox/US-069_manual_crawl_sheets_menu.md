---
id: US-069
status: accepted
date: 2026-06-03
size: S
---

# US-069: Menu sinh Mã Khang Ngô và System ID cho các căn gõ tay trên Google Sheets

## User story
**As an** Admin
**I want** có một menu chức năng trên Google Sheets để tự động sinh Mã Khang Ngô (ID) và System ID không trùng lặp cho các căn được gõ tay trực tiếp trên sheet.
**So that** các căn gõ tay có đầy đủ khóa định danh chuẩn trước khi đồng bộ ngược về SQLite.

## Acceptance
- Thêm menu `🤖 AI Tools -> Tạo Mã Khang Ngô & System ID (Dòng chọn)` trên giao diện Google Sheets.
- Khi bấm chọn, hệ thống tự động sinh Mã Khang Ngô chuẩn thuật toán và System ID độc nhất dạng `SYS-Timestamp-Random` điền vào các dòng được chọn.
- Đảm bảo các mã được tạo trực tiếp trên sheet hoạt động trơn tru.

## Solution
- Chỉnh sửa file `pool_backend_v3.gs` để thêm menu và viết hàm sinh mã gộp.

## Files touched
- `pool_backend_v3.gs`
