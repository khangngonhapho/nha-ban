---
id: US-008
status: done
date: 2026-05-20
size: S
---

# US-008: Siết định dạng Mô tả AI — cấm emoji, bắt buộc 4 đoạn

## User story
**As a** *Admin*
**I want** *buộc AI luôn xuất mô tả theo đúng 4 đoạn cố định (Vị trí, Kết cấu, Kết nối & Tiện ích, Pháp lý) bắt đầu bằng dấu "+", không dùng emoji*
**So that** *các bài đăng nhất quán về định dạng, dễ copy-paste lên các nền tảng mà không phải sửa tay*

## Acceptance
- [x] `systemPrompt` cấm AI dùng emoji/icon trong phần Mô tả
- [x] Mô tả bắt buộc gồm đúng 4 đoạn: `+ Vị trí`, `+ Kết cấu`, `+ Kết nối & Tiện ích`, `+ Pháp lý`
- [x] Mỗi đoạn cách nhau bằng 1 dòng trống
- [x] Mỗi đoạn bắt đầu bằng ký tự `+ `

## Solution

> [!note]- Output / Format
> Template mô tả bắt buộc:
> ```
> + Vị trí: Quận X, Phường Y. Hẻm Zm, [đặc điểm]. KHÔNG ghi số nhà.
>
> + Kết cấu: [tầng], [PN], [WC], [chi tiết nổi bật].
>
> + Kết nối & Tiện ích: [trục đường, tiện ích gần].
>
> + Pháp lý: Sổ hồng chính chủ, hoàn công đầy đủ.
> ```

## Files touched
- `pool_backend_v3.gs` — biến `systemPrompt` trong `batchGenerateContentAndWard`
