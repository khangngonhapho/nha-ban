---
id: US-014
status: done
date: 2026-05-20
size: M
---

# US-014: Tạo Pool Sheet Schema và validate column mapping

## User story
**As a** *Admin*
**I want** *có một tài liệu schema chính thức của sheet Pool, liệt kê tên cột chính xác, để mọi col mapping trong code đều được kiểm tra trước khi deploy*
**So that** *tránh lỗi getIdx trả -1 do sai tên header, đảm bảo dữ liệu đúng được đưa vào AI prompt*

## Acceptance
- [x] Tạo file `docs/pool_sheet_schema.md` liệt kê **tên header chính xác** của tất cả cột trong sheet Pool
- [x] PO xác nhận từng tên cột — tất cả 19 header trong code đều chính xác ✅
- [x] Sau khi PO confirm → không cần cập nhật `getIdx(...)` vì tất cả đúng
- [x] Schema file được dùng làm reference cho mọi US liên quan đến Sheet Pool
- [x] PO confirm: `Giá chào` = `Giá Public` → không cần đổi code
- [x] PO confirm: bỏ qua `Tình trạng nhà` và `Năm xây dựng`

## Danh sách cột cần PO xác nhận

> [!important]
> **PO vui lòng check từng dòng — ✅ Đúng hoặc ❌ Sai (ghi tên đúng vào)**

| STT | Tên header trong code | Dùng cho | Cần confirm |
|---|---|---|---|
| 1 | `Ngõ/Số nhà` | Số nhà | ❓ |
| 2 | `Đường` | Tên đường | ❓ |
| 3 | `Phường` | Phường (mới) | ❓ |
| 4 | `Quận` | Quận | ❓ |
| 5 | `DT Thực tế` | Diện tích thực tế (m2) | ❓ |
| 6 | `DT Trên sổ` | Diện tích trên sổ (m2) | ❓ |
| 7 | `Mặt Tiền` | Chiều ngang nhà (m) | ❓ |
| 8 | `Số Tầng` | Số tầng | ❓ |
| 9 | `Giá Public` | Giá bán (tỷ) | ❓ |
| 10 | `Số phòng ngủ` | Số phòng ngủ | ❓ |
| 11 | `Số nhà vệ sinh` | Số WC | ❓ |
| 12 | `Phân loại Hẻm` | Loại hẻm (Mặt tiền / Hẻm xe hơi...) | ❓ |
| 13 | `Đường trước nhà (m)` | Độ rộng hẻm (m) | ❓ |
| 14 | `Hướng` | Hướng nhà | ❓ |
| 15 | `Phân loại` | Tag USP (Lô góc, Hiếm...) | ❓ |
| 16 | `Mô tả chi tiết` | Điểm nổi bật từ môi giới | ❓ |
| 17 | `Phường cũ (AI)` | Output: Phường trước sáp nhập | ❓ |
| 18 | `Tiêu đề Public` | Output: Tiêu đề AI sinh | ❓ |
| 19 | `Mô tả Public` | Output: Mô tả AI sinh | ❓ |

## Files touched
- [NEW] `docs/pool_sheet_schema.md` — schema chính thức của sheet Pool
- `pool_backend_v3.gs` — cập nhật getIdx nếu phát hiện sai tên

## Notes
- Schema website (index.html) đã có ở `knowledge/khangngonhapho_web` — đây là 2 sheet **khác nhau**
- Pool sheet là sheet **nội bộ** dành cho workflow AI content generation
