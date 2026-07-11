---
id: US-013
status: done
date: 2026-05-20
size: S
fixes: US-012-bug
---

# US-013: Bỏ "Nội dung chính", thêm DT Trên sổ & Hướng vào userPrompt

## User story
**As a** *Admin*
**I want** *bỏ cột "Nội dung chính" khỏi userPrompt (gây lỗi tên người thành tên đường) và thay bằng các cột thông số nhà rõ ràng hơn*
**So that** *AI nhận đúng dữ liệu kỹ thuật, không bị nhiễu bởi raw data lộn xộn (tên người, SĐT, mã code)*

## Acceptance
- [x] Xoá dòng `"Nội dung chính"` khỏi `userPrompt`
- [x] Xoá col mapping `noiDungChinh` (không còn dùng)
- [x] Thêm col mapping và dòng trong `userPrompt` cho: `DT Trên sổ`, `Hướng`
- [x] Cột `Mặt Tiền` giữ nguyên nhưng cập nhật label rõ hơn: "Chiều ngang (m)"
- [x] Test case: không còn xuất hiện tên người/SĐT trong phần Kết nối & Tiện ích

## Solution

> [!note]- Key logic
> **Xoá khỏi cols:**
> ```javascript
> // XOÁ: noiDungChinh: getIdx("Nội dung chính"),
> ```
> **Thêm vào cols:**
> ```javascript
> dtSo: getIdx("DT Trên sổ"), huong: getIdx("Hướng"),
> ```
> **userPrompt sau khi cập nhật:**
> ```
> - Địa chỉ: ...
> - DT Thực tế: ...m2 | DT Trên sổ: ...m2
> - Chiều ngang (mặt tiền): ...m
> - Hướng: ...
> - Kết cấu: X tầng, Y PN, Z WC
> - Hẻm: ... (Rộng: ...m)
> - Giá: ...
> - Phân loại / Tag USP: ...
> - Điểm nổi bật của căn nhà (nguồn USP chính): ...
> ```

## Files touched
- `pool_backend_v3.gs` — cols mapping, `userPrompt` construction

## Notes
- Cần xác nhận tên header chính xác trong Sheet: "DT Trên sổ" và "Hướng"
- Nếu header khác, cập nhật `getIdx(...)` cho đúng
