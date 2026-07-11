---
id: US-030
status: accepted
date: 2026-05-24
size: S
---

# US-030: Chỉ đồng bộ Tiêu đề hàng loạt từ Pool sang Source

## User story
**As an** Admin
**I want** chỉ đồng bộ cột "Tiêu đề Public" từ Pool sang cột "tieu_de" (Cột E) bên Source hàng loạt theo dòng bôi đen chọn
**So that** cập nhật hàng loạt tiêu đề chuẩn SEO mới rất nhanh mà không làm đè hay ảnh hưởng đến hình ảnh, mô tả, hoặc pháp lý cũ đã bảo vệ trên Source.

## Acceptance
- [x] Thêm nút menu **`Chỉ đồng bộ Tiêu đề sang Source (hàng loạt)`** trong nhóm menu `🤖 AI Tools`.
- [x] Cho phép bôi đen chọn nhiều dòng (Active Range) trên Pool.
- [x] Chỉ tìm dòng tương ứng bên Source qua `System ID` (Cột AL/38) và cập nhật duy nhất cột `tieu_de` (Cột E/5).
- [x] Hiển thị thông báo toast chạy ngầm và alert thông kê số dòng thành công/thất bại sau khi chạy xong.

## Solution

> [!note]- Input
> - Nhiều dòng được bôi đen trên sheet Pool đã có sẵn `System ID` và `Tiêu đề Public` mới.

> [!note]- Output / Format
> - Chỉ duy nhất cột E (`tieu_de`) của các dòng tương ứng bên Source được cập nhật. Các thông tin khác giữ nguyên.

> [!note]- Key logic
> - Hàm `batchSyncTitleToSource()` trong `pool_backend_v3.gs` đọc mảng chọn, tối ưu tốc độ bằng cách tải trước toàn bộ System ID bên Source để so khớp `indexOf` cực nhanh trong RAM, rồi ghi nhận thẳng vào cột E bằng `sourceSheet.getRange(foundRow, 5).setValue(tieuDeVal)`.

## Verification Plan

> [!check]- Manual Verification
> 1. Thay đổi cột `Tiêu đề Public` của 2 dòng bất kỳ đã đồng bộ trước đó trên Pool sheet.
> 2. Bôi đen chọn 2 dòng này $\rightarrow$ Click chạy menu `🤖 AI Tools` $\rightarrow$ `Chỉ đồng bộ Tiêu đề sang Source (hàng loạt)`.
> 3. Mở file Source $\rightarrow$ Xác nhận chỉ có đúng 2 tiêu đề được cập nhật mới kịch trần, còn lại hình ảnh, mô tả và check đăng tin hoàn toàn giữ nguyên vẹn.

## Files touched
- `pool_backend_v3.gs` — [Apps Script Backend Pool]
