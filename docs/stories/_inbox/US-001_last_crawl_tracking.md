---
id: US-001
status: done
date: 2026-05-20
size: S
---

# US-001: Theo dõi thời gian thu thập dữ liệu Last Crawl

## User story
**As a** Admin (Quản trị viên kho dữ liệu)
**I want** hệ thống tự động ghi nhận mốc thời gian "Last Crawl" mỗi khi dữ liệu được lưu mới hoặc cập nhật vào Pool
**So that** tôi có thể đánh giá mức độ cũ/mới của dữ liệu và lên kế hoạch rà soát các căn nhà có khả năng lỗi thời.

## Acceptance
- [x] Tính năng tự động nạp mốc thời gian (timestamp) vào cột `Last Crawl` hoạt động chính xác khi có lệnh thêm mới (insert) hoặc cập nhật (update) một căn nhà vào Pool.
- [x] Thời gian được xuất ra theo đúng định dạng `dd/MM/yyyy HH:mm:ss` (múi giờ GMT+7).

## Solution

> [!note]- Input
> - Lệnh POST gửi từ crawler chứa payload căn nhà mới hoặc cập nhật.
> - Timestamp thời gian thực của máy chủ Apps Script tại thời điểm xử lý.

> [!note]- Output / Format
> - Dữ liệu thời gian được ghi vào cột `Last Crawl` ở dạng chuỗi: `dd/MM/yyyy HH:mm:ss` (Ví dụ: `20/05/2026 15:30:45`).

> [!note]- Key logic
> - Trong Apps Script `pool_backend_v3.gs`:
>   - Mảng header được mở rộng thông qua `createHeaders()` để có cột `Last Crawl`.
>   - Cập nhật hàm `doPost()` để chèn timestamp bằng cú pháp:
>     ```javascript
>     const crawlTime = Utilities.formatDate(new Date(), "GMT+7", "dd/MM/yyyy HH:mm:ss");
>     ```

## Verification Plan

> [!check]- Manual Verification
> 1. Gửi một request cào dữ liệu (Crawl) thử nghiệm cho 1 căn nhà bất kỳ.
> 2. Mở sheet `Pool` $\rightarrow$ Xác nhận căn nhà đã được nạp thành công và cột `Last Crawl` hiển thị chính xác ngày giờ hiện tại ở múi giờ Việt Nam.

## Files touched
- `pool_backend_v3.gs` — [Apps Script Backend API]

## Notes
- Admin cần chủ động tạo thêm tiêu đề cột `Last Crawl` ở sheet Pool hiện tại để hứng dữ liệu. Cột `Last Sync` (đẩy sang Source) sẽ được triển khai ở một User Story khác.
