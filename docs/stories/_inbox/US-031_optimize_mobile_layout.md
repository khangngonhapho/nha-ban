---
id: US-031
status: accepted
date: 2026-05-25
size: S
---

# US-031: Tối ưu hóa không gian hiển thị trang chủ và mở rộng hình đại diện trên Mobile

## User story
**As a** Guest / Admin
**I want** giao diện trang chủ được thu gọn tối đa các thành phần không cần thiết, header mảnh mai hơn, thanh tìm kiếm và bộ lọc thu nhỏ thành các nút icon, đồng thời card sản phẩm được mở rộng hình đại diện và click trực tiếp vào card để xem chi tiết
**So that** tối ưu hóa không gian hiển thị trên điện thoại di động, tăng lượng tin BĐS tiếp cận trong một màn hình cuộn và mang lại trải nghiệm tương tác trực quan cao cấp.

## Acceptance
- [x] **Giao diện Header siêu gọn:**
  - Loại bỏ hoàn toàn dòng chữ tiêu đề `"Khang Ngô Nhà Phố"` và hình ảnh Avatar Logo để tối giản tối đa, gom toàn bộ nút điều khiển (Badge tổng, Sort thời gian, Sort giá, Đăng nhập, Trái tim, Kính lúp, Phễu lọc) lên một hàng duy nhất siêu mỏng nhẹ.
  - Thu nhỏ chiều cao và khoảng đệm (padding) của Header để giải phóng không gian màn hình.
  - Ô nhập tìm kiếm `#searchInput` được thu gọn mặc định thành một nút icon kính lúp (`🔍`). Click vào nút kính lúp sẽ toggle (hiện/ẩn) thanh tìm kiếm bên dưới một cách mượt mà. Khi ẩn đi, ô tìm kiếm tự động xóa rỗng ký tự và cập nhật lại danh sách.
  - Nút bộ lọc của Admin được thu gọn từ chữ `"🎚 Bộ lọc"` thành nút icon dạng tròn chỉ chứa biểu tượng `🎚`.
  - Nút `"Đã lưu"` lọc yêu thích được lược bỏ chữ, chỉ hiển thị biểu tượng trái tim kèm số lượng dạng `♡ (X)` hoặc `♥ (X)`.
- [x] **Giao diện Card sản phẩm nằm ngang siêu gọn & full-height:**
  - Loại bỏ nút `"Xem chi tiết"` ở phần chân card (`.cfoot`) để tiết kiệm không gian.
  - Cho phép người dùng click vào **bất kỳ vị trí nào** trên card sản phẩm (ngoại trừ nút yêu thích `.heart` và ô chọn `.card-sel` của Admin) để mở ngay Bottom Sheet xem chi tiết BĐS.
  - **Thiết kế hình đại diện full-height nằm ngang trên Mobile:** Trả cấu trúc card về dạng nằm ngang (horizontal card layout), đưa thông tin `.info` và thanh chân card `.cfoot` vào container chung `.card-right` bên cạnh ảnh `.ibox` trong hàng `.crow` (`align-items: stretch`). Hình ảnh `.ibox` ở bên trái có chiều cao trải dài trọn vẹn từ đỉnh tới sát cạnh đáy card, bo góc mềm mại (`16px 0 0 16px`).
  - **Đồng bộ chiều cao card đều tăm tắp 100%:** Cài đặt chiều cao cố định của card trên Mobile là **`160px`** (tăng thêm 20px), loại bỏ hoàn tượng lệch chiều cao card do tên tiêu đề dài ngắn khác nhau. Trên Desktop, card tự động reset về `height: auto` với dạng grid dọc (ảnh cao 220px nằm trên, thông tin nằm dưới).
  - **Khung ảnh dạng đứng (Portrait 3:4) & Hợp nhất thông tin:** 
    - Tăng chiều rộng của khung ảnh `.ibox` lên **`120px`** (tạo tỷ lệ `120px x 160px` chân dung đúng tỷ lệ vàng nhiếp ảnh 3:4 rất premium).
    - Hợp nhất dòng hiển thị Giá (`.pr`) và Vị trí (`.loc`) thành một dòng ngang duy nhất (`.pr-loc`) ở đáy thông tin. Sử dụng `margin-top: auto` để tự động đẩy dòng này xuống sát chân card ngăn nắp.
    - Loại bỏ nhãn hiển thị `"VND"` bên cạnh giá tiền để tránh lỗi rớt dòng khi gặp tên phường quá dài (như *P. Tân Sơn Nhất*).
    - Loại bỏ hiển thị đường trước nhà, thay thế bằng **Số phòng ngủ (`🛏️ [X] PN`)** được trích xuất động từ cột `so_pn` (AD/index 29) trong Google Sheets để đảm bảo hiển thị 3 thông số vàng: Diện tích, Số tầng, Số phòng ngủ.
  - **Tăng số dòng tiêu đề:** Tăng giới hạn số dòng hiển thị của tiêu đề `.ititle` trên Mobile từ 2 dòng lên **3 dòng** (`-webkit-line-clamp: 3;`) để hiển thị đầy đủ thông tin mô tả chi tiết của căn nhà hơn.
  - **Tích hợp nút tương tác tinh tế đè lên ảnh đại diện:**
    - Di chuyển nút trái tim yêu thích `.heart` và ô chọn checkbox Admin `.card-sel` trở lại đè lên phần đáy của ảnh đại diện `.ibox` để giải phóng hoàn toàn không gian chân card `.cfoot`.
    - Thiết kế phẳng/trong suốt không viền nền, kết hợp bộ lọc bóng đổ thông minh `filter: drop-shadow(0 1px 2px rgba(0,0,0,0.5))` giúp nút hiển thị rõ nét nổi bật trên cả nền ảnh sáng và tối.
    - Tăng nhẹ kích thước để tránh bị bé trên màn hình iPhone mật độ điểm ảnh cao (Checkbox `.card-sel` rộng **`22px`**, nút `.heart` rộng **`32px`** với font chữ **`24px`**).
- [x] **Tối ưu nút Gọi & Zalo nổi:**
  - Loại bỏ hoàn toàn thanh ngang bottom bar `.sfoot` cũ.
  - **Xóa bỏ hoàn toàn cặp nút Gọi & Zalo nổi ở trang danh sách bên ngoài** để trả lại giao diện thông thoáng, tinh khiết 100% giúp rổ hàng cuộn trơn tru.
  - Giữ lại đầy đủ 2 nút tương tác Gọi ngay & Zalo tư vấn này ở phần chân (`.scta`) của popup chi tiết sản phẩm để hỗ trợ liên hệ khi khách hàng đã xem kỹ thông tin.

## Solution

> [!note]- Input
> - Tương tác click của người dùng trên toàn bộ thẻ `.card` và các nút toggle kính lúp, bộ lọc trên Header.

> [!note]- Output / Format
> - Giao diện Header mới siêu mảnh trên Mobile.
> - Card sản phẩm với ảnh cover lớn hơn, cursor trỏ vào dạng pointer trên toàn card, chân card chỉ còn ID và nút trái tim.

> [!note]- Key logic
> - **Ngăn chặn nổi bọt sự kiện (Event Propagation):**
>   Click vào `.heart` hoặc `.card-sel` bắt buộc sử dụng `event.stopPropagation()` để không kích hoạt sự kiện click mở modal chi tiết trên thẻ cha `.card`.
> - **Toggle thanh tìm kiếm:**
>   Sử dụng CSS Class `.search-bar.open` kết hợp animation mượt mà để ẩn hiện ô nhập liệu khi bấm nút 🔍.

## Verification Plan

> [!check]- Manual Verification
> 1. Truy cập giao diện chính $\rightarrow$ Xác nhận Header cực kỳ mảnh, không có chữ tiêu đề to, chỉ có avatar logo và các nút icon tròn `🔍`, `♡ (0)`.
> 2. Click vào icon kính lúp `🔍` $\rightarrow$ Thanh tìm kiếm trượt xuống. Nhập chữ tìm kiếm $\rightarrow$ Lọc danh sách bình thường. Click lại kính lúp `🔍` $\rightarrow$ Thanh tìm kiếm ẩn đi, danh sách được reset về ban đầu.
> 3. Kiểm tra card sản phẩm $\rightarrow$ Ảnh cover to rõ rệt, không có nút "Xem chi tiết".
> 4. Click vào ảnh hoặc bất kỳ phần text nào trên card $\rightarrow$ Popup chi tiết mở ra mượt mà.
> 5. Click vào nút Trái tim `♡` trên card $\rightarrow$ Trạng thái yêu thích thay đổi bình thường mà không bị nhảy mở popup chi tiết lên.

## Files touched
- `index.html` — [Cấu trúc UI & Styling Frontend]
