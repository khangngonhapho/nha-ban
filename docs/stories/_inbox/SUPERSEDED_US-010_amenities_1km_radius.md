---
id: US-010
status: superseded
date: 2026-05-20
size: S
superseded_by: US-011
---

# US-010: Giới hạn tiện ích trong bán kính 1km theo địa chỉ thực

## User story
**As a** *Admin*
**I want** *prompt AI chỉ liệt kê tiện ích nằm trong bán kính ~1km tính từ địa chỉ căn nhà, không liệt kê tiện ích ở quận khác hoặc xa hơn*
**So that** *thông tin tiện ích chính xác về mặt địa lý — tránh tình trạng AI ghi "Bệnh viện 115" (Q10) hoặc "Chợ Bến Thành" (Q1) cho nhà ở Trần Quang Diệu Q3*

## Acceptance
- [x] `systemPrompt` bổ sung ràng buộc: tiện ích phải nằm trong **bán kính ~1km tính từ vị trí cụ thể của số nhà + tên đường**, không phải tính từ tên quận hay tên phường
- [x] AI không được dùng quận/phường làm anchor (vì 1 con đường có thể trải dài qua nhiều quận — ví dụ CMT8 đi qua Q3, Q10, Q11, Tân Bình)
- [x] Test case: Trần Quang Diệu Q3 → đúng: chợ Tân Định, trường THPT Võ Thị Sáu; sai: Bệnh viện 115 (Q10), Chợ Bến Thành (Q1)
- [x] Test case: CMT8 đoạn Q3 vs CMT8 đoạn Q10 → tiện ích trả về khác nhau

## Solution

> [!note]- Key logic
> Thêm ràng buộc bán kính và anchor vào instruction `+ Kết nối & Tiện ích`:
> ```
> Chỉ liệt kê tiện ích nằm trong bán kính ~1km tính từ VỊ TRÍ CỤ THỂ của căn nhà (số nhà + đường)
> (KHÔNG tính từ tên đường - vì một con đường có thể trải dài qua nhiều quận).
> Ví dụ: CMT8 đoạn Q3 và CMT8 đoạn Q10 có tiện ích xung quanh hoàn toàn khác nhau.
> Tự kiểm tra: tiện ích đó có nằm trong bán kính đi bộ ~10-15 phút từ vị trí số nhà này không?
> ```

> [!note]- Output / Format
> Ví dụ sai (anchor sai — dùng tên quận):
> ```
> + Kết nối & Tiện ích: Gần Bệnh viện 115, Chợ Bến Thành...
> (nhà ở Trần Quang Diệu Q3, 2 tiện ích này ở Q10 / Q1)
> ```
> Ví dụ đúng (anchor đúng — tính từ số nhà):
> ```
> + Kết nối & Tiện ích: Gần chợ Tân Định, trường THPT Võ Thị Sáu, siêu thị Co.opmart Nhiêu Lộc — đầy đủ tiện ích trong tầm bộ.
> ```

## Files touched
- `pool_backend_v3.gs` — biến `systemPrompt` trong `batchGenerateContentAndWard`

## Notes
- Root cause US-009: constraint "gần địa chỉ" không đủ chặt — AI dùng tên quận làm anchor thay vì tọa độ thực của số nhà
- Một con đường trải dài qua nhiều quận (CMT8, Điện Biên Phủ, Lý Thường Kiệt...) là edge case quan trọng cần xử lý bằng ngôn ngữ prompt
