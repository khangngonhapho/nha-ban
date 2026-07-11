---
id: US-065
status: accepted
date: 2026-06-03
size: L
---

# US-065: Nghiên cứu API & Cào tab Thông tin chi tiết (Chủ nhà) + Hồ sơ pháp lý (Sổ đỏ)

## User story
**As a** Admin
**I want** lấy được thông tin chủ nhà và ảnh sổ đỏ từ các tab Thông tin chi tiết & Hồ sơ pháp lý
**So that** phục vụ lưu trữ thông tin nguồn hàng phục vụ giao dịch và đối chiếu pháp lý

## Acceptance
- Gọi các endpoint lấy thông tin chủ nhà và ảnh sơ đồ thửa đất / ảnh sổ đỏ.
- Lọc ảnh sổ đỏ từ mảng `media` với `type` là `parcel_map` hoặc `certificate_image` để phân phối tuần tự vào các cột `Sơ đồ thửa đất 1` đến `5`.
- Ghi nhận thông tin chủ nhà công khai (Tên chủ nhà, SĐT chủ nhà nếu được cấp quyền) vào SQLite.

## Solution
- Lọc các ảnh pháp lý lưu vào `So_do_thua_dat_1` đến `So_do_thua_dat_5`.
- Đảm bảo an toàn thông tin PII không gửi dữ liệu nhạy cảm sang bên thứ 3.

## Files touched
- `crawl_pipeline.py` — Bóc tách tab pháp lý và chi tiết
- `curator_server.py` — Hỗ trợ API recrawl cho tab pháp lý
