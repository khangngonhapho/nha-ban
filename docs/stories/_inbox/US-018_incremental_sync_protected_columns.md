---
id: US-018
status: done
date: 2026-05-21
size: M
---

# US-018: Tách biệt Đồng bộ Lần đầu & Đồng bộ Một phần (Smart Merge)

## User story
As *an Admin / System*
I want *hệ thống tự động phân tách chế độ đồng bộ dữ liệu từ Pool sang Source thành "Đồng bộ lần đầu" (sync toàn bộ) và "Đồng bộ một phần" (Smart Merge)*
So that *khi đồng bộ lại các cập nhật từ Pool, các hình ảnh bổ sung từ Drive/nguồn ngoài và các trường thông tin do Admin tinh chỉnh thủ công tại Source không bao giờ bị ghi đè thô bạo.*

## Acceptance criteria
- Khi Admin tick chọn `Duyệt Public` trên sheet Pool:
  - **Trường hợp 1 (Đồng bộ lần đầu):** Nếu `System ID` chưa tồn tại trên Source (hoặc cột `Last Sync` trên Pool trống) ➡️ Thực hiện đẩy mới hoàn toàn dữ liệu thô sang Source.
  - **Trường hợp 2 (Đồng bộ một phần):** Nếu `System ID` đã tồn tại trên Source ➡️ Hệ thống tự động kích hoạt cơ chế **Trộn dữ liệu thông minh (Smart Merge)**.
- **Quy tắc Trộn Dữ Liệu Thông Minh (Smart Merge Rules):**
  - Hệ thống chỉ cập nhật đè các cột thông tin thô (Diện tích thực tế, Số tầng, Mặt tiền, Giá chào/Giá public, Quận, Phường, Đường trước nhà (m), Số phòng ngủ, Số nhà vệ sinh, Phường cũ (AI), Last Crawl...).
  - Tuyệt đối bảo vệ **20 cột thông tin tinh chỉnh (Protected Columns)** trên Source không bị ghi đè nếu các ô này **đang có dữ liệu (khác trống)**:
    1. **Cú pháp** (Cột B, index 1)
    2. **Ghi chú (Note)** (Cột C, index 2)
    3. **Tiêu đề Public** (Cột E, index 4)
    4. **Hướng nhà** (Cột M, index 12)
    5. **Đường trước nhà** (Cột N, index 13 - phân loại hẻm/mặt tiền)
    6. **Tình trạng nhà** (Cột P, index 15)
    7. **Đánh giá** (Cột Q, index 16)
    8. **Ngủ trệt** (Cột R, index 17)
    9. **CHDV** (Cột S, index 18)
    10. **Mô tả Public** (Cột T, index 19)
    11. **Ảnh 1 đến Ảnh 10** (Cột U đến AD, index 20 đến 29 - các ảnh tải lên thủ công hoặc ảnh từ Drive ngoài)
- **Hỗ trợ Force Overwrite (Cưỡng bức đồng bộ đè):** Admin có thể xóa ngày ở cột `Last Sync` trên Pool và bấm Duyệt lại để ép hệ thống đồng bộ đè lại 100% dữ liệu từ Pool sang Source kể cả khi dòng đã tồn tại.

## Solution

> [!note]- Key logic
> Logic xử lý chính sẽ được bổ sung vào trigger `onAdminReview(e)` trong `pool_backend_v3.gs`:
> 1. **Khi tìm thấy dòng tương ứng ở Source (`foundRow > -1`):**
>    - Kiểm tra xem cột `Last Sync` trên Pool có trống hay không. Nếu trống ➡️ Chạy luồng ghi đè toàn bộ (Force Overwrite).
>    - Nếu `Last Sync` có dữ liệu ➡️ Tiến hành đọc dòng hiện tại từ Source:
>      `var existingRowData = publicSheet.getRange(foundRow, 1, 1, publicRowData.length).getValues()[0];`
>    - Tạo mảng đã trộn `mergedRowData` bằng cách duyệt qua 39 cột:
>      - Nếu index cột thuộc `[1, 2, 4, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]` VÀ giá trị ô ở `existingRowData` khác trống ➡️ Ghi nhận giá trị cũ của `existingRowData`.
>      - Ngược lại ➡️ Lấy giá trị mới từ `publicRowData` của Pool.
>    - Thực hiện ghi đè dữ liệu đã trộn:
>      `publicSheet.getRange(foundRow, 1, 1, mergedRowData.length).setValues([mergedRowData]);`
> 2. **Khi KHÔNG tìm thấy dòng tương ứng ở Source (`foundRow === -1`):**
>    - Thực hiện ghi mới toàn bộ dữ liệu thô bằng phương thức `appendRow(publicRowData)`.
>    - Xác định `foundRow = lastRowPublic + 1` để thực hiện ghi đè công thức hình ảnh `=IMAGE(...)` cho dòng mới.

## Verification Plan

> [!check]- Automated Tests
> Không áp dụng kiểm thử tự động, sử dụng kiểm thử thủ công trực tiếp trên Google Sheet thông qua các ca kiểm thử.

> [!check]- Manual Verification
> - **Test 1: Đồng bộ lần đầu (First Sync)**
>   - Tạo 1 dòng mới tinh trên Pool, điền đầy đủ dữ liệu thô và ảnh.
>   - Tick chọn `Duyệt Public` ➡️ Xác nhận dòng được append mới hoàn toàn sang Source với đầy đủ thông tin.
> - **Test 2: Đồng bộ một phần (Smart Merge - Không chép đè)**
>   - Tại dòng vừa sync ở Source, thay đổi tiêu đề thủ công, sửa lại hướng nhà, sửa lại phân loại hẻm, thêm link ảnh Drive vào cột `Ảnh 1` và `Ảnh 2`.
>   - Quay lại Pool, chỉnh sửa Diện tích thực tế, thêm số toilet và thay đổi ảnh thô trên Pool.
>   - Tick lại `Duyệt Public` ➡️ Xác nhận trên Source: Diện tích và số toilet được cập nhật mới; Tiêu đề, Hướng nhà, Phân loại hẻm và Ảnh 1, Ảnh 2 (ảnh Drive) vẫn được bảo toàn nguyên vẹn, không bị ảnh thô ghi đè.
> - **Test 3: Cưỡng bức đồng bộ (Force Sync)**
>   - Xóa ngày ở cột `Last Sync` trên dòng Pool.
>   - Tick lại `Duyệt Public` ➡️ Xác nhận toàn bộ thông tin trên Source bị ghi đè hoàn toàn bởi dữ liệu từ Pool.

## Files touched
- `pool_backend_v3.gs` — Bổ sung logic Smart Merge trong trigger `onAdminReview`.
