---
id: US-032
status: accepted
date: 2026-05-25
size: S
---

# US-032: Tính năng Bộ sưu tập BĐS cá nhân hóa cho Admin

## User story
**As an** *Admin / PO*  
**I want** *tạo các bộ sưu tập BĐS tùy chỉnh có tên riêng (như tên khách hàng hoặc phân khúc), xem danh sách lọc và chỉnh sửa chúng trực tiếp trên giao diện*  
**So that** *quản lý phân loại rổ hàng chuyên nghiệp, dễ dàng tái sử dụng và nhân bản danh sách gửi cho nhiều khách hàng có nhu cầu tương tự mà không mất thời gian chọn lại.*  

## Acceptance
- [ ] **Lưu vào Bộ sưu tập (Save to Collection):**
  - Khi Admin chọn 1 hoặc nhiều căn bằng checkbox Admin, hệ thống hiển thị thêm nút nổi hình chiếc cặp tài liệu **`📁`** (cạnh nút tạo link `🔗`).
  - Click `📁` mở ra một Slide-up Sheet (Modal `#colSaveModal`) cho phép:
    - **Tạo mới bộ sưu tập:** Nhập tên bộ sưu tập tùy chỉnh (ví dụ: "Anh Hùng Q3") và nhấn "Tạo".
    - **Lưu vào bộ sưu tập hiện có:** Liệt kê các BST hiện có dạng `📁 [Tên BST] ([X] căn)`, click dòng nào sẽ nạp thêm (merge) các căn đang chọn vào BST đó (không trùng lặp).
  - Dữ liệu BST được lưu trữ an toàn trong `localStorage.adminCollections`.
- [ ] **Gộp cổng truy cập danh sách qua icon Tim trên Header:**
  - Nút Yêu thích (Tim) trên Header được dùng chung làm cổng truy cập:
    - **Với Khách:** Nhấn icon Tim $\rightarrow$ Chạy thẳng lọc danh sách thả tim cá nhân như cũ.
    - **Với Admin:** Nhấn icon Tim $\rightarrow$ Trượt mở Slide-up Sheet (Modal `#colViewModal`) liệt kê:
      - Bộ sưu tập mặc định đầu tiên: `❤️ Căn nhà đã thích (${favs.size} căn)`.
      - Các bộ sưu tập tùy chỉnh của Admin: `📁 [Tên BST] ([X] căn)`.
      - Click dòng nào sẽ chuyển sang chế độ xem bộ sưu tập/danh sách thích tương ứng.
- [ ] **Chế độ xem Bộ sưu tập (View Collection Mode):**
  - **Mặc định không check:** Khi bật xem bộ sưu tập, toàn bộ checkbox Admin `.card-sel` đều để trống (không tự động checked). Checkbox chỉ dùng khi Admin muốn tích chọn các căn để tạo link chia sẻ mới gửi khách.
  - **Thanh ghim động:** Xuất hiện thanh ghim động màu vàng dưới Header: **"📂 Xem bộ sưu tập: [Tên BST] ([X] căn)"** kèm nút `✕ Hủy xem` để trở lại rổ hàng đầy đủ.
- [ ] **Nút "Bỏ khỏi BST" nhỏ gọn riêng biệt:**
  - Trong chế độ xem bộ sưu tập, dưới chân mỗi card sản phẩm kế bên Mã số `#ID` xuất hiện một nút **`✕ Bỏ`** nhỏ gọn bằng chữ xám mờ tinh tế.
  - Click nút **`✕ Bỏ`** sẽ xóa ngay căn nhà đó ra khỏi bộ sưu tập thời gian thực (đối với BST tự tạo) hoặc bỏ thích (đối với BST yêu thích) mà không làm ảnh hưởng đến các checkbox chọn căn của bạn.
- [ ] **Bảo mật và an toàn dữ liệu:**
  - Giao diện của Khách hàng hoàn toàn trong sạch, không nhìn thấy bất kỳ nút nổi `📁`, nút `✕ Bỏ` hay modal danh sách BST nào.

## Solution

> [!note]- Input
> - Tương tác click của Admin chọn các căn bằng checkbox `.card-sel`.
> - Dữ liệu dán/nhập tên BST mới trong modal lưu, hoặc click chọn BST trong modal xem.
> - Sự kiện click nút `✕ Bỏ` trên card sản phẩm.

> [!note]- Output / Format
> - Modal Lưu bộ sưu tập (`#colSaveModal`) và Modal Xem bộ sưu tập (`#colViewModal`) hiển thị dưới dạng Slide-up Bottom Sheet.
> - Thanh ghim động màu vàng ghim dưới Header khi bật chế độ xem bộ sưu tập.
> - Nút `✕ Bỏ` xuất hiện cạnh mã `#ID` ở chân card.

> [!note]- Key logic
> - **Lưu trữ LocalStorage:** Sử dụng `localStorage.adminCollections` lưu đối tượng map: `{ "[Tên BST]": ["Mã ID 1", "Mã ID 2"] }`.
> - **Lọc danh sách động:** Khi `activeCollectionName` khác null, hàm `getFiltered()` tự động lọc danh sách `DATA` theo mảng các ID của BST đó.
> - **Đồng bộ DOM:** Hàm `removeFromCol()` xóa ID khỏi BST trong LocalStorage, tự động cập nhật thống kê, render lại danh sách card, và đóng/mở thanh ghim vàng động tương ứng.

## Verification Plan

> [!check]- Manual Verification
> 1. **Kiểm tra Khách hàng:** Truy cập chế độ khách, click icon Tim trên Header $\rightarrow$ Xác nhận lọc thẳng tới các căn đã thích cá nhân (không hiện danh sách BST).
> 2. **Kiểm tra Admin mở danh sách BST:** Truy cập chế độ Admin (`?pwd=trang`), click icon Tim trên Header $\rightarrow$ Xác nhận trượt mở Modal xem BST chứa Yêu thích và các BST tùy chọn.
> 3. **Kiểm tra Lưu bộ sưu tập:** Chọn 3 căn nhà $\rightarrow$ Click nút nổi `📁` $\rightarrow$ Nhập tên `"Khách Hùng Q3"` và bấm **`Tạo`** $\rightarrow$ Xác nhận tạo BST thành công.
> 4. **Kiểm tra Chế độ xem & Mặc định không check:** Bấm xem BST `"Khách Hùng Q3"` $\rightarrow$ Xác nhận chỉ lọc đúng 3 căn trong BST đó, các checkbox của 3 căn đều để trống (không checked), xuất hiện thanh ghim vàng động báo hiệu và nút **`✕ Bỏ`** bên cạnh mã `#ID` của mỗi card.
> 5. **Kiểm tra nút "Bỏ khỏi BST":** Bấm nút **`✕ Bỏ`** trên card $\rightarrow$ Căn nhà biến mất ngay lập tức khỏi chế độ xem BST, số lượng trên thanh ghim vàng giảm về 2.

## Files touched
- `index.html` — Bổ sung layout modal lưu/xem, thanh ghim động, nút Bỏ khỏi BST trên card, nút nổi `📁` và JS logic quản lý lưu trữ LocalStorage collections.
