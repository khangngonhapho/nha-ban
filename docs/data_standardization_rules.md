# Data Standardization Rules (Nguyên Tắc Chuẩn Hóa Dữ Liệu)

Tài liệu này định nghĩa bộ nguyên tắc tiền xử lý và chuẩn hóa dữ liệu bắt buộc của dự án BDS Khang Ngô. AI Assistant bắt buộc phải đọc lại tài liệu này trước khi lên giải pháp kỹ thuật hoặc viết code liên quan đến dữ liệu.

---

## 🛑 1. Chuẩn Hóa Địa Chỉ & Tên Đường (Address Parsing)

Để tránh các sai lệch về địa lý và tạo mã định danh **Mã Khang Ngô** chính xác, toàn bộ dữ liệu địa chỉ đầu vào phải đi qua bộ lọc chuẩn hóa sau:

### a. Chuẩn hóa tên đường đặc biệt
Toàn bộ biến thể viết tay của tên đường phải được mã hóa thành các ký hiệu an toàn:
*   **Cách Mạng Tháng 8** (CMT8, CMT Tám, Cách mạng tháng tám...): Mã hóa thành **`TTMC`**.
*   **Ba Tháng Hai** (3/2, 3-2, Đường 3/2, 3 tháng 2...): Mã hóa thành **`HTB`**.
*   **Đường số 7** (đường đánh số có số 7): Mã hóa thành **`7SD`**.

### b. Xử lý số nhà phức hợp (Compound House Numbers)
Các số nhà chứa dấu cộng (`+`) thể hiện nhiều căn gộp hoặc số phụ:
*   **Quy tắc:** Chỉ lấy phần số đầu tiên trước dấu cộng.
*   *Ví dụ:* `1168.42+44` ➔ chỉ trích xuất `1168.42` làm input tính toán.

---

## 🔒 2. Bảo Mật Dữ Liệu Cá Nhân (PII Protection Rules)

Khi gửi dữ liệu mô tả bất động sản sang các API LLM của bên thứ ba (OpenAI, Anthropic...):
*   **Quy tắc tiền xử lý:** AI bắt buộc phải chạy bộ lọc Regex hoặc logic chuỗi để **loại bỏ 100%** thông tin định danh cá nhân:
    *   *Số điện thoại:* Định dạng 10-11 số liên tiếp.
    *   *Email:* Định dạng `@gmail.com`, `@yahoo.com`...
    *   *Tên riêng:* Tên chủ nhà hoặc đầu chủ (ví dụ: "chị Vy", "anh Huy", "đầu chủ A").
*   *Mục đích:* Tránh rò rỉ thông tin nội bộ của rổ hàng và bảo vệ quyền riêng tư khách hàng.

---

## 📈 3. Tiêu Chuẩn Đầu Ra AI (AI Output Formatting Standards)

Khi AI sinh nội dung public (`Tiêu đề Public` và `Mô tả Public`):
*   **Độ dài tiêu đề:** Phải ngắn gọn, tối ưu dưới 85 ký tự và chứa Mã Khang Ngô ở vị trí quy định.
*   **Cấu trúc mô tả:** Phải siết chặt định dạng **đúng 4 đoạn**, tuyệt đối **không sử dụng emoji**, không chứa thông tin liên hệ hay raw data gây nhiễu.

---

## 🔄 Quy Trình Cập Nhật Nguyên Tắc

Mỗi khi phát sinh một quy tắc tiền xử lý hoặc chuẩn hóa mới trong quá trình triển khai thực tế (Implementation):
1.  Lập trình viên/AI cập nhật quy tắc đó trực tiếp vào tài liệu này.
2.  Báo cáo với PO về quy tắc mới bổ sung để đưa vào kiểm thử hồi quy.

---

*Tài liệu này được cập nhật và tuân thủ bởi toàn bộ hệ thống Agent trong dự án.*
