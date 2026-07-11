---
id: US-003
status: done
date: 2026-05-20
size: S
---

# US-003: Theo dõi thời gian đồng bộ dữ liệu Last Sync

## User story
**As a** Admin (Quản trị viên kho dữ liệu)
**I want** có cột "Last Sync" trên sheet Pool để theo dõi thời gian đồng bộ dữ liệu sang sheet Source
**So that** tôi có thể dễ dàng quản lý, nhận biết các dữ liệu nào đã được đẩy (public) hoặc các dữ liệu nào bị lỗi thời so với bản cập nhật mới nhất (so sánh với Last Crawl).

## Acceptance
- [x] Mảng header của Pool được mở rộng thêm cột `Last Sync` (nằm cạnh `Last Crawl`).
- [x] Khi có căn nhà mới được thêm vào Pool từ Crawler, cột `Last Sync` mặc định khởi tạo giá trị rỗng (`""`).
- [x] Hệ thống tự động ghi nhận timestamp hiện tại (`dd/MM/yyyy HH:mm:ss` - GMT+7) vào ô `Last Sync` của dòng tương ứng bất cứ khi nào:
  1. Dữ liệu được đẩy thành công sang Source thông qua script đồng bộ ngầm.
  2. Quản trị viên tick thủ công vào ô Checkbox `Duyệt Public` ngay trên sheet Pool.

## Solution

> [!note]- Input
> - Hành động tick checkbox `Duyệt Public` của Admin.
> - Lệnh đẩy tự động thành công từ script đồng bộ.

> [!note]- Output / Format
> - Ngày giờ đồng bộ ghi vào cột `Last Sync` dưới dạng chuỗi: `dd/MM/yyyy HH:mm:ss` (GMT+7).

> [!note]- Key logic
> - Trong `pool_backend_v3.gs`:
>   - Thêm cột `Last Sync` vào mảng headers trong `createHeaders()`.
>   - Chèn giá trị rỗng `""` vào `rowData` trong `doPost()` khi nạp dữ liệu mới.
>   - Sửa hàm `onAdminReview()` (hoặc hàm trigger onEdit tương ứng trên sheet Cloud) để tự động ghi nhận:
>     ```javascript
>     row.getCell(colLastSync).setValue(Utilities.formatDate(new Date(), "GMT+7", "dd/MM/yyyy HH:mm:ss"));
>     ```

## Verification Plan

> [!check]- Manual Verification
> 1. Mở sheet `Pool` $\rightarrow$ Xác nhận cột `Last Sync` đã có và các căn nhà mới bò vào từ crawler đều hiển thị trống `""` ở cột này.
> 2. Tick chọn `Duyệt Public` cho 1 dòng $\rightarrow$ Xác nhận cột `Last Sync` tự động được nạp ngày giờ hiện tại của Việt Nam sau khi đồng bộ thành công.

## Files touched
- `pool_backend_v3.gs` — [Apps Script Backend Logic]

## Notes
- Tính năng cập nhật timestamp vào cột `Last Sync` đòi hỏi thêm lệnh `setValue(Utilities.formatDate(new Date(), "GMT+7", "dd/MM/yyyy HH:mm:ss"))` vào file `dong-bo-ngam.gs` (cho luồng tự động) và vào hàm `onEdit` hoặc hàm xử lý tương ứng khi có thao tác tick `Duyệt Public` trên Google Apps Script (Cloud).
