# 💰 Quy Tắc Giá Bán (Pricing Rules)

Tài liệu này định nghĩa các quy tắc nghiệp vụ liên quan đến việc định dạng, hiển thị và tìm kiếm giá bán bất động sản trong hệ thống BDS Khang Ngô.

## 1. Đơn Vị Đo Lường & Nhập Liệu
- **Đơn vị chuẩn:** Tỷ Việt Nam Đồng (Tỷ VNĐ).
- **Cách nhập:** Trên giao diện biên tập Admin và Google Sheets, giá được nhập dạng số thực (ví dụ: `15.5` tương đương 15 tỷ 500 triệu VNĐ).
- Trên giao diện Client hiển thị, hệ thống tự động thêm hậu tố `Tỷ` (ví dụ: `15.5 Tỷ`).

---

## 2. Tìm Kiếm Khoảng Giá Thông Minh (Price Range Parsing)

Bộ máy phân tích chuỗi tìm kiếm thông minh (`Smart Search Parser`) nhận diện các yêu cầu về giá của người dùng từ thanh tìm kiếm bằng Regex:
- **Exact Match (Khớp giá chính xác):** Nhận diện định dạng `<số>.<số> tỷ` (ví dụ: `12.5 tỷ` hoặc `8.2 tỷ`) để lọc các căn nhà có giá bằng đúng giá trị tìm kiếm.
- **Prefix Match (Khớp khoảng giá chặn trên):** Nhận diện định dạng `<số> tỷ` (ví dụ: `15 tỷ`) để lọc toàn bộ các căn nhà có giá chào nhỏ hơn hoặc bằng giá trị đó (giá trị chặn trên).
  - *Ví dụ:* Tìm kiếm `dưới 10 tỷ` hoặc chỉ gõ `10 tỷ` ➔ Hệ thống sẽ lọc ra các căn từ `10 tỷ` trở xuống.

---

## 3. Sắp Xếp Mặc Định Theo Giá (Sort Order)
- Để tối ưu trải nghiệm khách hàng, danh sách rổ hàng hiển thị mặc định trên trang Client và trang chia sẻ luôn được **sắp xếp theo giá từ cao xuống thấp** (Descending Order).
- Việc sắp xếp này được thực hiện tự động sau khi tải dữ liệu từ Google Sheets về và trước khi áp dụng các bộ lọc hiển thị động.
