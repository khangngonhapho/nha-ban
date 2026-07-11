---
id: US-033
status: accepted
date: 2026-05-25
size: S
---

# US-033: Tùy chỉnh Tiêu đề trang khi tạo link chia sẻ gửi khách hàng

## User story
**As an** *Admin / PO*  
**I want** *thiết lập tiêu đề trang tùy chỉnh riêng khi tạo link gửi khách hàng, và tự động hiển thị tiêu đề đó trên tab trình duyệt của khách hàng*  
**So that** *cá nhân hóa giỏ hàng gửi đi một cách chuyên nghiệp hơn, giúp khách hàng dễ dàng nhận biết chủ đề/phân khúc của danh sách BĐS (ví dụ: "Biệt thự sân vườn Quận 3") thay vì tiêu đề mặc định chung.*  

## Acceptance
- [ ] **Bổ sung trường Tiêu đề trang trong Modal Tạo Link Gửi Khách:**
  - Trong Modal `#linkModal`, thêm một trường nhập liệu mới nằm ở giữa Tên khách hàng và Ghi chú nội bộ:
    - Nhãn: **Tiêu đề trang (hiển thị trên tab trình duyệt của khách)**
    - Ô nhập: `<input type="text" id="linkCustTitle" style="width:100%; box-sizing:border-box; padding:12px; border:1px solid #ddd; border-radius:8px; font-size:16px !important; outline:none;" placeholder="Mặc định: Giỏ hàng độc quyền - Khang Ngô Nhà Phố">`
- [ ] **Mã hóa an toàn & Đồng bộ chuỗi chia sẻ:**
  - Tích hợp giá trị Tiêu đề tùy chỉnh (`cTitle`) vào chuỗi thông tin khách hàng cá nhân hóa.
  - Chuỗi thô trước khi nén Base64 có định dạng: `[Tên khách] | [Ghi chú nội bộ] | [Tiêu đề tùy chỉnh]`.
  - Nếu Admin để trống Tiêu đề: Chuỗi thô là `[Tên khách] | [Ghi chú nội bộ] | ` hoặc `[Tên khách] | [Ghi chú nội bộ]`.
- [ ] **Giải mã & Hiển thị động phía Khách hàng:**
  - Ở đầu trang web, khi giải mã tham số `c` từ URL:
    - Nếu phần tử thứ 3 (`parts[2]`) tồn tại và có giá trị: Sử dụng JavaScript để cập nhật tiêu đề trang web động `document.title = parts[2]`.
    - Nếu `parts[2]` trống hoặc không tồn tại (bao gồm các link cũ đã chia sẻ trước đó): Giữ nguyên tiêu đề mặc định hoặc dùng `"Giỏ hàng độc quyền - Khang Ngô Nhà Phố"`.
- [ ] **Đồng bộ an toàn ngược (Backward Compatibility):**
  - Đảm bảo toàn bộ các link chia sẻ cũ (chỉ chứa 1 phần tử Tên khách hoặc 2 phần tử Tên khách | Ghi chú) vẫn hoạt động hoàn toàn bình thường mà không bị crash hay hiển thị lỗi.

## Solution

> [!note]- Input
> - Ô nhập liệu `#linkCustTitle` trong Modal Tạo Link Gửi Khách `#linkModal`.

> [!note]- Output / Format
> - Tiêu đề tab trình duyệt của khách hàng (`document.title`) tự động thay đổi động.

> [!note]- Key logic
> - Giải mã chuỗi token `c` và tách thành các phần bằng dấu phân tách ` | ` (`parts.split(" | ")`).
> - Phần tử `parts[2]` đại diện cho Tiêu đề tùy chỉnh.
> - Cập nhật `document.title` bằng giá trị `parts[2]` nếu có.

## Verification Plan

> [!check]- Manual Verification
> 1. **Kiểm tra tạo link có tiêu đề tùy chỉnh:**
>    * Đăng nhập Admin (`?pwd=trang`) $\rightarrow$ Chọn 2 căn $\rightarrow$ Bấm nút nổi `🔗`.
>    * Nhập Tên khách: `"Anh Hùng"`, Ghi chú: `"VIP Q3"`, Tiêu đề trang: `"Biệt thự sân vườn Quận 3"`.
>    * Bấm **Tạo Link** $\rightarrow$ Copy link được tạo.
> 2. **Kiểm tra phía Khách hàng (Hiển thị tiêu đề tùy chỉnh):**
>    * Truy cập link vừa tạo bằng tab ẩn danh (chế độ khách).
>    * **Xác nhận:** Tiêu đề tab trình duyệt hiển thị chính xác là **"Biệt thự sân vườn Quận 3"** thay vì "Khang Ngô Nhà Phố".
> 3. **Kiểm tra tạo link để trống tiêu đề:**
>    * Tạo link mới chỉ nhập Tên khách `"Anh Hùng"` và để trống ô Tiêu đề trang.
>    * Truy cập link bằng chế độ khách $\rightarrow$ **Xác nhận:** Tiêu đề tab trình duyệt hiển thị mặc định `"Giỏ hàng độc quyền - Khang Ngô Nhà Phố"` hoặc tiêu đề mặc định.
> 4. **Kiểm tra tương thích ngược (Backward Compatibility):**
>    * Truy cập một link chia sẻ cũ chỉ chứa token tên khách hàng.
>    * **Xác nhận:** Trang web tải bình thường, lời chào hoạt động chính xác và tiêu đề hiển thị mặc định không bị lỗi.

## Files touched
- `index.html` — Bổ sung ô nhập liệu Tiêu đề trang trong modal, JS logic mã hóa thông tin chia sẻ và JS logic giải mã hiển thị động phía Khách hàng.
- `api/index.js` — Giải mã thông tin khách hàng phía Server-side để tiêm động tiêu đề tùy chỉnh vào HTML tĩnh phục vụ Zalo Preview và hiển thị tức thời.
