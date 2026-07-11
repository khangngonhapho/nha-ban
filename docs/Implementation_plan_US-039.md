# Kế hoạch Triển khai US-039: Admin Curation Dashboard trên Web Vercel

> 📅 **Last Updated:** 2026-05-28 12:55:00 (GMT+7)

Tài liệu này phác thảo thiết kế chi tiết và kế hoạch triển khai tính năng **Admin Curation Dashboard** chạy trực tiếp trên Vercel của dự án BĐS Khang Ngô Nhà Phố, tích hợp tính năng **Bản đồ Google Maps tương tác định vị chính xác vị trí nhà**.

---

## 🎯 Mục tiêu Thay đổi & Nghiệp vụ

1. **Bảo mật tối đa (Privacy Shield):** Chỉ nạp dữ liệu thô (từ sheet Pool) khi Admin đã xác thực OAuth2 thành công qua Gmail. Người dùng/khách hàng thông thường tuyệt đối không tải và không thấy các thông tin thô nhạy cảm này.
2. **Giao diện Card danh sách Admin (Theo thiết kế mẫu):**
   Khi Admin đăng nhập và dữ liệu thô được nạp thành công, danh sách các căn nhà sẽ được chuyển sang giao diện chuyên nghiệp chuẩn tối ưu thực địa:
   - **Bên Trái (Media Box):**
     * **Ảnh đại diện BĐS:** Ưu tiên số 1 lấy **Ảnh mặt tiền gốc** (`img_mat_tien` đọc từ cột AM của sheet Source). Nếu không có, tự động fallback về ảnh sạch đầu tiên của BĐS.
     * Dưới ảnh hiển thị nhãn xanh lam kéo dài hết chiều rộng ảnh: **`Tình trạng nhà`** (VD: `"Chuẩn"`, `"Bình thường"`).
   - **Bên Phải (Thông tin chi tiết):**
     * **Tiêu đề màu ĐỎ đậm nổi bật:** Hiển thị **địa chỉ thật** và **cú pháp thô** (VD: `453/151 Lê Văn Sỹ 35/40 3 3.1 13.0 8 tỷ`).
     * **Dòng 1:** `📍 Quận [Tên Quận]` (VD: `Quận 3`).
     * **Dòng 2:** `👤 [Tên Đầu Chủ - Group]` (VD: `Nguyễn Triệu Đức Trung - Thiên Địa`).
     * **Dòng 3:** `📞 [Số Điện Thoại Đầu Chủ]` (Màu đỏ/đen, chạm gọi ngay `tel:`, có `event.stopPropagation()` để không bị xung đột với sự kiện click mở modal chi tiết).
     * **Góc dưới phải:** Nút Yêu thích `❤️` màu đỏ khi được chọn.
3. **Bố cục hiển thị Hình nhà & Hình sổ song song (Trọn 1 màn hình di động):**
   - **Khu vực 1: Bất động sản** (Tiêu đề chữ ĐỎ in đậm, căn giữa). Carousel vuốt ngang chứa tất cả ảnh nội thất/ngoại thất sạch của BĐS (`p.imgs`) cao **160px**, sử dụng **CSS Scroll Snap** (Native 120 FPS) hỗ trợ hiển thị slide kế bên mập mờ (Adjacent Slides peeking effect).
   - **Khu vực 2: Sơ đồ thửa đất** (Tiêu đề chữ ĐỎ in đậm, căn giữa). Carousel vuốt ngang chứa toàn bộ ảnh sơ đồ thửa đất 1 & 2 (`p.raw_sodo1` và `p.raw_sodo2`) cao **160px** có peeking.
4. **Tích hợp Bản đồ Google Maps định vị nhanh (Theo thiết kế mẫu):**
   Để môi giới có thể định vị nhanh và chính xác vị trí thực tế của căn nhà khi đang đi thực địa hoặc dẫn khách, tích hợp khu vực **BẢN ĐỒ** trực quan ngay trong thông tin Admin:
   - **Bản đồ Google Maps tương tác:** Sử dụng Iframe Google Maps nhúng trỏ thẳng theo Địa chỉ thật của căn nhà (`Số nhà thật` + `Đường thật` + `Phường` + `Quận` + `Hồ Chí Minh`).
   - Bản đồ có kích thước nhỏ gọn (`height: 240px`), bo tròn góc đẹp mắt, hỗ trợ thu phóng (zoom in/out) bằng hai ngón tay và có nút mở nhanh trong App Google Maps của điện thoại.
5. **Bố cục Grid Thông số kỹ thuật Dữ liệu thô (Theo thiết kế mẫu):**
   - **Header Card:** Trạng thái -> Badge xanh lam `"Chuẩn"`. Mã hàng -> Chữ đậm màu đen.
   - **Phần THÔNG TIN (Chữ ĐỎ, in hoa đậm):** Grid 2 cột hiển thị: Diện tích sổ (m²), Thực tế (m²), Mặt tiền (m), Chiều dài (m), Đường trước nhà (m), Số tầng. Giá chào quy đổi thành triệu VND.
   - **Phần THÔNG TIN NGUỒN (Chữ ĐỎ, in hoa đậm):** Đầu chủ / Người gửi nguồn và ĐT đầu chủ có link gọi điện, gạch dưới chấm đứt (`dotted`).
6. **Bố cục MÔ TẢ CHI TIẾT thu gọn thông minh (Theo thiết kế mẫu):**
   - **Box 1 (Nội dung chính thô):** Hộp có viền mỏng, chữ ĐỎ đậm, cỡ chữ nhỏ gọn `13px`.
   - **Box 2 (Mô tả chi tiết thô):** Hộp có viền mỏng, chữ màu xanh đen, cỡ chữ `12.5px`, hiển thị đầy đủ tin đăng gốc. Box 2 có chiều cao tối đa `160px` kèm hiệu ứng mờ dần (gradient fade-out) ở chân và nút **`Xem thêm`** để admin chạm mở rộng.
7. **Nạp dữ liệu song song (Dual-Sheet Loading):**
   - Khi chưa đăng nhập: Tải rổ hàng công khai từ sheet Public qua JSONP như hiện tại.
   - Khi Admin đăng nhập thành công: Gọi trực tiếp Google Sheets API v4 tải song song hai sheet **Pool** và **Source**, thực hiện so khớp (matching) client-side thông minh dựa trên `System ID` hoặc `Mã Hàng`.
8. **Bộ lọc thô nâng cao (Advanced Filters):** Tích hợp thêm một ô Tìm kiếm nâng cao Admin vào trong collapsible `#filterPanel` hiện có khi ở chế độ Admin, cho phép tìm kiếm client-side thời gian thực theo: `Tên đầu chủ`, `Nội dung chính`, và `Mô tả chi tiết`.
9. **Giao diện Chi tiết Accordion di động tối ưu (Toggle Headers UI):**
   Tái cấu trúc Modal Chi tiết căn nhà khi hoạt động ở chế độ Admin thành 3 vùng Accordion có thể Expand/Collapse mượt mà, sắp xếp theo tần suất sử dụng thực tế của môi giới:
   - **`[▼] 📢 THÔNG TIN THÔ - POOL` (Ưu tiên số 1 & Mở mặc định):** Chứa 2 Carousels ảnh nhà và ảnh sổ (160px), bảng Grid thông số kỹ thuật, Bản đồ Google Maps nhúng, và hai hộp văn bản thô **MÔ TẢ CHI TIẾT** dạng boxed có nút "Xem thêm" thu gọn thông minh.
   - **`[▶] ✍️ BIÊN TẬP CUSTOM - SOURCE` (Đóng mặc định):** Form chỉnh sửa các trường custom.
   - **`[▶] 📄 PREVIEW KHÁCH HÀNG` (Đóng mặc định):** Hiển thị bài đăng public sạch sẽ cho khách hàng.
10. **Cơ chế Ghi ngược An toàn (Write-Back to Source):**
    Khi bấm nút **`💾 LƯU THAY ĐỔI`** (Sticky footer ghim đáy màn hình), hệ thống sẽ cập nhật mảng dòng dữ liệu gốc từ `Source` và đẩy ngược lên mây qua Sheets API PUT request. Hiển thị Toast thông báo premium xanh lá mượt mà.

---

## 📦 Các thay đổi đề xuất trong Codebase

### [MODIFY] [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html)

#### 1. Bổ sung CSS cho Card Admin, Carousel Peeking, Grid Specs, Boxed Description, Google Map & Accordion
* Thêm style cho Card danh sách admin (`.admin-card-inner`...).
* Thêm style cho Carousels vuốt ngang peeking cao `160px`.
* Thêm style cho bảng Grid thông số kỹ thuật bo viền chấm đứt (`dotted`).
* Thêm style cho Bản đồ Google Maps nhúng (`.admin-map-container`).
* Thêm style cho phần MÔ TẢ CHI TIẾT, Accordion, Form Edit, Toast và Zoom Overlay.

#### 2. Nâng cấp hàm `loadData()` & Dual-Sheet Data Ingestion
* Cập nhật hàm `loadData()` tải dữ liệu song song qua OAuth2 API hoặc public JSONP tùy theo trạng thái đăng nhập.
* Lưu thêm các trường địa chỉ thô từ Pool (`raw_so_nha`, `raw_ten_duong`, `phuong`, `ql`).

#### 3. Tích hợp Tìm kiếm nâng cao Admin
* Thêm ô nhập liệu `#adminSearchInput` vào `#filterPanel` (bọc trong class `.admin-only`).
* Cập nhật hàm `getFiltered()` để quét và tìm kiếm theo Tên đầu chủ, Nội dung chính, và Mô tả chi tiết.

#### 4. Cập nhật cơ chế sinh thẻ Card trong hàm `render()`
* Kiểm tra và sinh HTML Card Admin tùy chỉnh, ưu tiên sử dụng ảnh mặt tiền bên trái, bọc `tel:` và bọc `stopPropagation` chống mở modal.

#### 5. Tái cấu trúc hàm `openS(id)` (Detail Modal)
* Nếu ở chế độ `is-admin` và đã nạp dữ liệu: Render giao diện 3-Accordion (Pool, Source, Preview KH).
* Ở Accordion 1, render 2 Carousels ảnh, bảng Grid Thông số kỹ thuật, Bản đồ Google Maps nhúng (`iframe` trỏ thẳng tới địa chỉ thật), sau đó render tiêu đề **"MÔ TẢ CHI TIẾT"** và 2 hộp boxed (Nội dung chính và Mô tả chi tiết thô) kèm nút "Xem thêm". Gọi kiểm tra chiều cao `checkMoTaCollapse()`.
* Thiết lập các sự kiện touch thu phóng sơ đồ thửa đất (`Pinch-to-Zoom`) khi click vào ảnh sơ đồ.
* Thiết lập giá trị mặc định cho các ô nhập liệu, hộp chọn dropdown, và checkbox từ đối tượng dữ liệu hiện tại.

#### 6. Triển khai Ghi ngược (Write-Back) & Toast Notification
* Hàm `saveSourceChanges(id)`: Lấy giá trị, cập nhật mảng dòng `original_row_data` của căn đó, gọi API PUT ghi đè lên dòng tương ứng trên Tab Source. Hiển thị Toast thông báo premium.

---

## 🧪 Kế Hoạch Việc Xác Minh & Nghiệm Thu (Verification Plan)

### Kiểm thử Thủ công (Manual Verification)
1. **Kiểm tra View Khách:** Truy cập website thông thường, xác nhận giao diện sạch sẽ, an toàn.
2. **Đăng nhập Gmail Admin:** Liên kết Gmail thành công. Xác nhận rổ hàng cập nhật giao diện Card Admin ĐỎ chuyên nghiệp.
3. **Kiểm tra Card danh sách Admin:** Xác nhận ảnh đại diện là Ảnh mặt tiền, có nhãn "Chuẩn" bên dưới, tiêu đề ĐỎ chứa Địa chỉ thật + Cú pháp, các thông tin Quận, Đầu chủ và SĐT hoạt động hoàn hảo.
4. **Kiểm tra Bố cục Chi tiết (Trọn 1 màn hình):** Click mở chi tiết căn nhà thô:
   - Accordion `📢 THÔNG TIN THÔ - POOL` mở sẵn.
   - Xác nhận có **2 Carousel** (Bất động sản & Sơ đồ thửa đất) xếp dọc, cao 160px.
   - Xác nhận dưới carousels có bảng **Grid thông số kỹ thuật**.
   - Xác nhận có khu vực **BẢN ĐỒ** hiển thị Google Map tương tác, ghim chính xác vị trí nhà dựa trên Số nhà thật + Tên đường thật. Hỗ trợ thao tác thu phóng bằng ngón tay và mở nhanh trong ứng dụng Maps.
   - Xác nhận dưới bảng thông số có tiêu đề **MÔ TẢ CHI TIẾT** và hai hộp thông tin boxed: Hộp ĐỎ (Nội dung chính) và Hộp XANH ĐEN (Mô tả chi tiết) có nút "Xem thêm" thu gọn thông minh.
5. **Kiểm tra Form Edit & Ghi ngược:** Chỉnh sửa Hướng dropdown, Đánh giá dropdown, tích chọn checkbox và bấm Lưu thay đổi ghim ở đáy. Xác nhận lưu thành công lên sheet Source.
