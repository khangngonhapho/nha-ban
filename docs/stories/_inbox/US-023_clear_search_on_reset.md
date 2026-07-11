---
id: US-023
status: accepted
date: 2026-05-24
size: S
---

# US-023: Tự động xóa ô tìm kiếm và tích hợp nút xóa nhanh ✕

## User story
**As a** Admin / Guest
**I want** ô tìm kiếm tự động trống sạch khi bấm nút Xóa lọc, đồng thời tích hợp thêm nút xóa nhanh `✕` ngay trong ô tìm kiếm
**So that** nhanh chóng xóa nhanh từ khóa tìm kiếm mà không cần phải xóa tay từng ký tự.

## Acceptance
- [x] Khi bấm nút `↺ Xóa lọc` (chỉ hiển thị ở Admin khi có lọc active), giá trị của ô `#searchInput` được reset về trống `''`.
- [x] Tích hợp nút xóa nhanh `✕` (định vị tuyệt đối ở bên phải ô tìm kiếm):
    *   Tự động hiển thị khi người dùng đang nhập từ khóa.
    *   Tự động ẩn đi khi ô tìm kiếm trống rỗng.
    *   Click vào nút `✕` sẽ xóa sạch từ khóa và render lại danh sách card.
- [x] Điều chỉnh padding-right của ô nhập liệu `#searchInput` thành `36px` để tránh chữ gõ đè lên nút `✕`.
- [x] Giao diện danh sách card được render lại đầy đủ toàn bộ BĐS.

## Solution

> [!note]- Input
> - Hành động click nút `✕` xóa nhanh `#searchClear`.
> - Hành động click nút `↺ Xóa lọc` `#resetBtn`.
> - Giá trị nhập tay vào ô `#searchInput`.

> [!note]- Output / Format
> - Ô nhập liệu được xóa sạch (`value = ''`).
> - Giao diện render danh sách BĐS được lọc và làm mới đồng bộ ngay lập tức.

> [!note]- Key logic
> - Hàm `resetFilters()` cập nhật thêm logic xóa trắng ô tìm kiếm:
>   ```javascript
>   const sInput = document.getElementById('searchInput');
>   if (sInput) sInput.value = '';
>   toggleSearchClearBtn();
>   ```
> - Hàm `toggleSearchClearBtn()` kiểm tra nếu có giá trị nhập thì hiện nút `✕`, ngược lại ẩn đi (`display: none`).

## Verification Plan

> [!check]- Manual Verification
> 1. Gõ từ khóa tìm kiếm bất kỳ (VD: "Phú Nhuận") vào ô `#searchInput` $\rightarrow$ Xác nhận nút `✕` xuất hiện ở bên phải.
> 2. Click vào nút `✕` $\rightarrow$ Xác nhận ô nhập liệu bị xóa trắng và danh sách card render lại đầy đủ.
> 3. Chọn bộ lọc và gõ tiếp từ khóa $\rightarrow$ Click nút `↺ Xóa lọc` $\rightarrow$ Xác nhận cả bộ lọc và ô tìm kiếm đều được xóa trắng đồng bộ.

## Files touched
- `index.html` — [Frontend UI & Logic]
