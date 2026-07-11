---
id: US-064
status: accepted
date: 2026-06-03
size: M
---

# US-064: Cào Thông tin chung & Giải mã ảnh Swiper trang Chi tiết

## User story
**As a** Admin
**I want** cào được thông tin chung và hình ảnh mô tả từ Swiper ở trang chi tiết căn nhà mới
**So that** hiển thị đầy đủ hình ảnh và nội dung mô tả của căn nhà cho khách xem

## Acceptance
- Gọi API chi tiết: `GET https://backend.thienkhoi.com/product/v1/property/<UUID>`
- Trích xuất thông tin: mã hàng, giá chào, mô tả chi tiết, diện tích thực tế, diện tích sổ, số tầng, số phòng ngủ/WC, đầu chủ, v.v.
- Lọc ảnh mô tả / ảnh nội thất từ mảng `media` với `type` là `property_image` (dự phòng `checkin_image`).
- Ghi nhận thông tin vào SQLite database.

## Solution
- Lấy ảnh nội thất/mặt tiền lưu vào `raw_images_tk_json`.
- Phục hồi thông tin Đầu chủ từ các thuộc tính JSON API lồng nhau.

## Files touched
- `crawl_pipeline.py` — Phân tích chi tiết và bóc tách Swiper images
- `curator_server.py` — Chỉnh sửa endpoint recrawl tương thích
