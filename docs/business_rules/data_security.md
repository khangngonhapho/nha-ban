# 🔒 Bảo Mật Dữ Liệu & PII (Data Security)

Tài liệu này quy hoạch các nguyên tắc bảo mật thông tin nội bộ, quyền riêng tư khách hàng và an toàn mã nguồn trong dự án BDS Khang Ngô.

## 1. Mật Khẩu Đăng Nhập & Quyền Admin
- **Mật khẩu truy cập Admin hiện tại:** `trang`.
- **Cơ chế xác thực:**
  - Qua tham số URL: `?pwd=trang`. Khi Admin truy cập link này, trình duyệt sẽ lưu trạng thái `isAdminSession = 'true'` vào `localStorage` thiết bị.
  - Tải trang và tự động đăng nhập ngầm (Silent Auto-Login): Nếu có trạng thái Admin trong `localStorage`, hệ thống sẽ kích hoạt giao diện biên tập Admin và cho phép tải dữ liệu bảo mật (như Sổ đỏ, Số nhà thật).
- Khách hàng thông thường khi truy cập link chia sẻ không chứa tham số `pwd` sẽ không thấy nút đăng nhập và hoàn toàn bị chặn truy cập các thông tin nhạy cảm.

---

## 2. Bảo Mật Số Nhà Trên Client View
- **Nguyên tắc cốt lõi:** Số nhà thật (`Ngo_So_nha` / `Ng__S__nh_`) và Tên đường thật (`ten_duong` / `Duong`) là thông tin nội bộ bảo mật của rổ hàng.
- **Quy định hiển thị:**
  - Đối với khách hàng thường (Client View): Ẩn hoàn toàn số nhà thật. Địa chỉ chỉ hiển thị mức độ đường/phường/quận (ví dụ: `Đường Nguyễn Trãi, Phường Bến Thành, Quận 1`).
  - Đối với Admin (Admin Curation/Preview): Hiển thị đầy đủ số nhà và tên đường thật để phục vụ đi khảo sát thực tế và đối soát.

---

## 3. Loại Bỏ Thông Tin Nhạy Cảm (PII Filtering)
- Trước khi gửi nội dung mô tả bất động sản gốc cào từ Thiên Khôi sang các LLM API bên thứ ba (như OpenAI, Anthropic) để tự động viết lại tiêu đề/mô tả public:
  - **Quy tắc tiền xử lý:** AI / backend bắt buộc phải lọc sạch **100%** thông tin định danh cá nhân (Personally Identifiable Information - PII).
  - **Bộ lọc bao gồm:**
    - Số điện thoại: Định dạng số liên tục (ví dụ: `090...`, `098...`).
    - Email: Các định dạng email cá nhân.
    - Tên riêng chủ nhà / đầu chủ: Tên riêng (ví dụ: `chị Vy`, `anh Nam`, `đầu chủ A`).
  - **Mục đích:** Ngăn ngừa rò rỉ thông tin liên hệ trực tiếp của chủ nhà ra môi trường công cộng.

---

## 4. Bảo Mật File Cấu Hình & Git
- Các file chứa thông tin kết nối nhạy cảm như `credentials.json` (Google Sheets OAuth key) và file `SOURCE_OF_TRUTH.md` (chứa các link nháp mật, password) **TUYỆT ĐỐI KHÔNG** được push lên Git công khai. Các file này phải được đưa vào danh sách `.gitignore` và chỉ lưu trữ bảo mật cục bộ.
- Dự án duy trì cơ chế tự phục hồi credentials cục bộ trong thư mục Home Directory (`~/.bds_khangngo/credentials.json`) để khôi phục tự động trong trường hợp vô tình bị dọn dẹp Git.
