---
id: US-029
status: accepted
date: 2026-05-24
size: S
---

# US-029: Sắp xếp theo Sản phẩm mới thêm mặc định trên danh sách

## User story
**As an** Admin / Guest
**I want** danh sách BĐS mặc định hiển thị các sản phẩm mới thêm (nằm cuối Google Sheet) lên hàng đầu, đồng thời bổ sung thêm nút sắp xếp theo thời gian kế bên nút sắp xếp theo giá
**So that** nhanh chóng tiếp cận rổ hàng mới nhất mà không cần cuộn tìm, dễ dàng chuyển đổi qua lại giữa sắp xếp theo Giá và Thời gian.

## Acceptance
- [x] Mặc định khi tải trang, danh sách được sắp xếp theo **Sản phẩm mới thêm lên trước** (giảm dần theo thứ tự dòng trong Google Sheet, tức là `temp_id` giảm dần).
- [x] Bổ sung nút Sắp xếp theo Thời gian (Mới thêm) `#sortNewBtn` kế bên nút Sắp xếp theo Giá `#sortPriceBtn`.
- [x] Trực quan hóa nút active/inactive:
    *   Nút sắp xếp đang được chọn sẽ hiển thị trạng thái active (nền trắng, icon màu đỏ).
    *   Hiển thị mũi tên chỉ hướng sắp xếp ngay cạnh icon (VD: `⏱️⬇` cho Mới nhất, `⏱️⬆` cho Cũ nhất, `💰⬇` cho Giá cao $\rightarrow$ thấp, `💰⬆` cho Giá thấp $\rightarrow$ cao).
    *   Nút không chọn sẽ hiển thị ở trạng thái mờ tĩnh (`⏱️` hoặc `💰`).
- [x] Đồng bộ hóa việc lưu trạng thái sắp xếp vào `localStorage` của Admin để giữ nguyên trải nghiệm trong phiên tiếp theo.

## Solution

> [!note]- Configuration
> - **Biến trạng thái sắp xếp**:
>   `currentSortType` ('newest' hoặc 'price'), `currentSortDir` ('desc' hoặc 'asc').
> - Lưu trữ LocalStorage:
>   Key: `adminState` (Lưu trạng thái sắp xếp và bộ lọc của Admin).
> - CSS Class active: `.sort-icon-btn.active` (nền trắng `#fff`, chữ đỏ `var(--red)`).

> [!note]- Input
> - Click vào nút sắp xếp thời gian `#sortNewBtn` hoặc nút sắp xếp giá `#sortPriceBtn`.

> [!note]- Output / Format
> - Thay đổi ký tự và hướng mũi tên trên nút tương ứng:
>   *   Thời gian: `⏱️⬇` (Mới nhất), `⏱️⬆` (Cũ nhất).
>   *   Giá bán: `💰⬇` (Cao $\rightarrow$ Thấp), `💰⬆` (Thấp $\rightarrow$ Cao).
>   *   Nút không active hiển thị mờ tĩnh không mũi tên: `⏱️` hoặc `💰`.

> [!note]- Key logic
> - **Logic sắp xếp trong `render()`:**
>   Sắp xếp mảng DATA trước khi tạo DocumentFragment:
>   ```javascript
>   const arr = DATA.slice().sort((a, b) => {
>     if (currentSortType === 'newest') {
>       const ta = parseInt(a.temp_id, 10) || 0;
>       const tb = parseInt(b.temp_id, 10) || 0;
>       return currentSortDir === 'asc' ? ta - tb : tb - ta;
>     } else {
>       const ga = parseFloat(a.gia) || 0, gb = parseFloat(b.gia) || 0;
>       return currentSortDir === 'asc' ? ga - gb : gb - ga;
>     }
>   });
>   ```
> - **Logic toggle chuyển đổi:**
>   Hàm `toggleSortNew()` và `toggleSortPrice()` chuyển đổi loại và hướng sắp xếp, lưu trạng thái thông qua `saveState()` và gọi `render()` cập nhật giao diện.

## Verification Plan

> [!check]- Manual Verification
> 1. Mở trang web $\rightarrow$ Xác nhận rổ hàng hiển thị các căn mới thêm (dòng cuối cùng trên Google Sheet) lên hàng đầu, nút `⏱️⬇` sáng trắng active.
> 2. Click nút sắp xếp Giá `💰` $\rightarrow$ Xác nhận danh sách sắp xếp theo Giá cao $\rightarrow$ thấp, nút đổi thành `💰⬇` sáng trắng, nút thời gian chuyển thành mờ tĩnh `⏱️`.
> 3. Click tiếp nút Giá `💰⬇` $\rightarrow$ Đổi chiều thành `💰⬆` (Giá tăng dần).
> 4. Click tiếp nút Thời gian `⏱️` $\rightarrow$ Đổi trở lại xếp Thời gian mới nhất `⏱️⬇` sáng trắng.

## Files touched
- `index.html` — [Frontend Sorting UI & Logic]
