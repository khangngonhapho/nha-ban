---
id: US-063
status: accepted
date: 2026-06-03
size: M
---

# US-063: Cào danh sách nguồn hàng từ trang Web Proptech mới

## User story
**As a** Admin
**I want** hệ thống cào được danh sách tin từ trang Web Proptech mới (`proptech.thienkhoi.com`) qua API ngầm
**So that** lấy được danh sách UUID của các căn nhà mới xuất hiện để chuẩn bị cào chi tiết

## Acceptance
- Cào danh sách thành công qua API phân trang ngầm của Thiên Khôi (`backend.thienkhoi.com/product/v1/property?page=...`).
- Tự động bóc tách và refresh token khi hết hạn để duy trì phiên đăng nhập.
- Ghi nhận thông tin cơ bản của tin và UUID vào cơ sở dữ liệu SQLite.
- Áp dụng các quy tắc None-Safety khi parse JSON để tránh lỗi crash do các trường trống (`None`).

## Solution
- Gọi API: `GET https://backend.thienkhoi.com/product/v1/property`
- Sử dụng Cookie lưu trong `thienkhoi_cookie.txt`.
- Dùng API refresh token: `POST https://backend.thienkhoi.com/auth/v1/auth/refresh-token`
- Tích hợp None-safety bằng cú pháp `(dict.get(key) or {}).get(subkey)`.

## Files touched
- `crawl_pipeline.py` — Logic cào danh sách và refresh token
- `BDS-AGENTS.md` — Quy tắc None-safety và phân loại media (Rule 11)
