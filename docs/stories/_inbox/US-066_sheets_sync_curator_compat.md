---
id: US-066
status: accepted
date: 2026-06-03
size: S
---

# US-066: Đồng bộ Google Sheets Pool & Tương thích Curator UI

## User story
**As a** Admin
**I want** dữ liệu cào mới được đồng bộ mượt mà lên Google Sheets Pool và tương thích với Web Curator UI
**So that** quy trình quản lý rổ hàng và biên tập tin diễn ra thông suốt với UUID của hệ thống mới

## Acceptance
- Dữ liệu cào từ hệ thống Proptech mới đồng bộ thành công lên Google Sheets Pool.
- Endpoint cào lại `/api/listings/<tk_id>/recrawl` tự động phát hiện UUID 36 ký tự và định tuyến cào API chi tiết mới.
- Web Curator UI hiển thị đúng link gốc và xử lý trơn tru.

## Solution
- Nâng cấp endpoint recrawl trong `curator_server.py`.
- Tự động dựng link gốc: `https://proptech.thienkhoi.com/warehouse/sources/{UUID}`.

## Files touched
- `curator_server.py` — Chỉnh sửa endpoint recrawl tương thích hệ thống mới
