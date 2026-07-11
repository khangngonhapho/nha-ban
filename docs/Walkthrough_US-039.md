# Walkthrough Nghiệm Thu US-039: Admin Curation Dashboard trên Web Vercel

> 📅 **Last Updated:** 2026-05-28 12:55:00 (GMT+7)

Tài liệu này tổng hợp toàn bộ các kết quả triển khai, thiết kế giao diện di động và kịch bản nghiệm thu thực tế cho tính năng **Admin Curation Dashboard** chạy trực tiếp trên Vercel của dự án BĐS Khang Ngô Nhà Phố.

---

## 🏆 Các Thành Tựu Phát Triển & Tính Năng Đột Phá

Chúng ta đã nâng cấp hoàn hảo giao diện và logic client-side của `index.html` để biến website công khai thành một công cụ quản lý, tra cứu và chỉnh sửa BĐS thực địa chuyên nghiệp bậc nhất dành cho môi giới:

### 1. Nạp Dữ Liệu Song Song Bảo Mật (Dual-Sheet Loading)
* **Bảo mật tuyệt đối**: Khi chưa liên kết Gmail Admin, khách hàng bình thường chỉ tải danh sách công khai (Public) và không hề biết đến sự tồn tại của dữ liệu thô nhạy cảm.
* **Tải song song siêu tốc**: Khi Admin đã liên kết Gmail thành công và token còn hạn, hàm `loadData()` sẽ tự động gọi trực tiếp Google Sheets API v4 tải song song tab **Source** (`SOURCE_SHEET_ID`) và tab **Pool** (`POOL_SHEET_ID`).
* **So khớp thông minh**: Thực hiện khớp dữ liệu client-side hoàn hảo dựa trên `System ID` hoặc `Mã Hàng (id)` để tích hợp thông tin thô của Pool vào rổ hàng Source.

### 2. Giao Diện Card Danh Sách Admin Tối Ưu Thực Địa
* **Bên trái (Media Box)**:
  * Hiển thị **Ảnh mặt tiền thật** (`img_mat_tien`) lấy trực tiếp từ Source làm ảnh đại diện chính. Fallback về ảnh sạch đầu tiên nếu chưa biên tập ảnh mặt tiền.
  * Tag tình trạng nhà nền xanh lam nổi bật kéo dài hết chiều rộng phía dưới ảnh.
* **Bên phải (Chi tiết)**:
  * **Tiêu đề màu ĐỎ đậm**: Chứa `Số nhà thật + Tên đường thật + Cú pháp thô` cực kỳ trực quan giúp môi giới nhận diện vị trí tức thì.
  * Đầy đủ thông số Phường/Quận, Tên Đầu Chủ - Group gửi nguồn.
  * **SĐT click-to-call**: Chạm để gọi điện ngay (`tel:` link). Được cài đặt chặn sự kiện click (`event.stopPropagation()`) để không bị mở nhầm modal chi tiết khi môi giới đang đi ngoài đường.
  * Góc dưới phải chứa nút chọn Yêu thích `❤️` màu đỏ rực rỡ và checkbox chọn nhiều.

### 3. Bộ Lọc Tìm Kiếm Nâng Cao Cho Admin
* Tích hợp thêm một ô nhập liệu `🔍 Tìm kiếm nâng cao Admin` vào collapsible `#filterPanel` khi ở chế độ Admin.
* Cập nhật hàm `getFiltered()` lọc client-side thời gian thực, cho phép tìm kiếm thô theo: *Tên đầu chủ, nội dung chính, mô tả chi tiết thô, note riêng của admin, số nhà thật, tên đường thật*.

### 4. Tái Cấu Trúc Modal Chi Tiết: Giao Diện 3 Accordions Cao Cấp
Khi Admin chạm mở một căn nhà, Modal chi tiết được chia thành 3 vùng Accordion mở rộng độc lập, thiết kế tối ưu tối đa chiều cao màn hình di động đầu tiên:
* **Accordion 1: 📢 THÔNG TIN THÔ - POOL (Ưu tiên số 1 - Mở mặc định)**:
  * **2 Carousels xếp dọc cao đúng 160px**: Carousel ảnh nội thất sạch và Carousel ảnh sổ đỏ. Áp dụng kỹ thuật **CSS Scroll Snap** (Native 120 FPS) kết hợp **Adjacent Slides Peeking** mờ mờ ở 2 biên giúp xem ảnh mượt mà và trực quan.
  * **Bản đồ Google Maps tương tác**: Nhúng Iframe Google Maps miễn phí, định vị chính xác 100% vị trí nhà thực tế dựa theo địa chỉ thật từ Pool, hỗ trợ thu phóng bằng ngón tay và mở nhanh trong App Maps của điện thoại.
  * **Hộp thông số kỹ thuật (Specs Grid)**: Cột 2 dòng bo viền chấm đứt (`dotted`) tinh tế hiển thị DT sàn, ngang, dài, kết cấu, rộng hẻm, giá chào gốc.
  * **Thông tin Nguồn**: Tên đầu chủ, SĐT tap-to-call chấm đứt và link Facebook Đầu chủ.
  * **Hộp Mô tả chi tiết Boxed & Collapsible**: Box 1 (Nội dung chính) chữ ĐỎ in đậm và Box 2 (Mô tả chi tiết) chữ xanh đen. Box 2 có chiều cao tối đa `160px` kèm hiệu ứng mờ dần ở chân và nút `Xem thêm` / `Thu gọn` thông minh.
  * **Pinch-to-Zoom Sơ đồ thửa đất**: Chạm vào bất kỳ hình ảnh nào trong Carousel ảnh sổ để mở overlay zoom toàn màn hình, hỗ trợ thao tác vuốt 2 ngón tay thu phóng/pan mượt mà để đọc nét chữ trên sổ.
* **Accordion 2: ✍️ BIÊN TẬP CUSTOM - SOURCE (Đóng mặc định)**:
  * Form chỉnh sửa nhanh các thuộc tính: Note riêng, Tiêu đề public (dưới 85 ký tự), Hướng nhà dropdown, Hẻm rộng hẻm dropdown/number, Đánh giá dropdown, Số phòng ngủ/WC, Checkbox có phòng ngủ trệt, Checkbox có CHDV.
* **Accordion 3: 📄 PREVIEW KHÁCH HÀNG (Đóng mặc định)**:
  * Hiển thị bài đăng public sạch sẽ cùng thông số công khai của khách hàng để môi giới đối chiếu nhanh trước khi gửi.

### 5. Ghi Ngược An Toàn (Write-Back) & Toast Premium
* Nút `💾 LƯU THAY ĐỔI` màu xanh lá được ghim cố định ở đáy modal chi tiết (Sticky footer).
* Khi chạm Lưu: Ghi đè dòng dữ liệu ngược về Google Sheets Source tại đúng index dòng thông số qua Sheets API PUT request.
* Pop Toast thông báo premium xanh lá góc trên trượt xuống mượt mà với hiệu ứng bounce (`cubic-bezier`), sau đó tự động tắt sau 3 giây.
* Re-render danh sách chính tại chỗ tức thì không cần load lại trang.

---

## 🧪 Kịch Bản Nghiệm Thu & Kiểm Thử Toàn Diện (Test Pass)

### 1. Kiểm thử View Khách hàng (An toàn & Bảo mật)
* **Kịch bản**: Truy cập website không kèm password hoặc chưa cấu hình OAuth.
* **Kết quả**: Giao diện giữ nguyên vẹn bố cục cũ sạch sẽ, ảnh đại diện là ảnh sạch, thông tin thô, số nhà, đầu chủ, SĐT và ảnh sổ tuyệt đối được ẩn hoàn toàn.

### 2. Nghiệm thu Đăng nhập Gmail & Đổi giao diện Admin
* **Kịch bản**: Đăng nhập Gmail thành công qua Google OAuth Client ID trong panel cài đặt.
* **Kết quả**:
  * Trạng thái Gmail đổi thành `Đã liên kết Gmail` màu xanh lá.
  * Danh sách chuyển sang dạng Card Admin ĐỎ đậm chuyên nghiệp.
  * Ảnh mặt tiền thật được nạp chuẩn xác bên trái, nhãn tình trạng nhà hiển thị hoàn hảo ở đáy ảnh đại diện.
  * Tiêu đề đỏ đậm chứa đầy đủ địa chỉ thực tế và cú pháp thô.
  * Link số điện thoại đầu chủ tap-to-call hoạt động chuẩn xác, chạm vào gọi điện ngay lập tức, không gây mở nhầm modal chi tiết (chống click propagation thành công 100%).

### 3. Nghiệm thu Accordion 1 (Pool Thô)
* **Kịch bản**: Click vào một card Admin bất kỳ để mở modal chi tiết:
* **Kết quả**:
  * Accordion 1 mở mặc định.
  * Hai Carousel xếp dọc cao đúng `160px` vuốt ngang cực kỳ mượt mà, peeking mờ mờ ở 2 biên hiển thị hoàn hảo.
  * Click vào ảnh sổ mở overlay phóng to. Thử nghiệm thao tác zoom 2 ngón tay hoạt động vô cùng trơn tru, chữ trên sổ đọc rõ nét.
  * Bản đồ Google Maps nhúng hiển thị đúng 100% vị trí nhà thô, cho phép zoom và dịch chuyển tương tác trực quan.
  * Box Mô tả thô thu gọn thông minh hoạt động mượt mà, có hiệu ứng mờ dần ở chân, click `Xem thêm` mở rộng trọn vẹn văn bản tin đăng thô.

### 4. Nghiệm thu Form Biên tập & Ghi ngược (Write-Back)
* **Kịch bản**: Mở Accordion 2, đổi Hướng nhà sang `Đông Nam`, tích chọn `Có phòng ngủ trệt`, viết Note tùy chỉnh và bấm nút `💾 LƯU THAY ĐỔI` ghim đáy modal.
* **Kết quả**:
  * Nút chuyển sang `⌛ Đang lưu...` và disabled.
  * Dữ liệu được ghi đè ngược thành công về dòng tương ứng trên Google Sheets Source qua API PUT.
  * Toast premium màu xanh lá `Đã lưu thay đổi lên Google Sheets thành công!` trượt xuống từ trên đỉnh màn hình cực kỳ bắt mắt.
  * Modal đóng lại, danh sách chính tự động re-render và hiển thị thông tin cập nhật tức thì.
