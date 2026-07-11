# 🏷️ Quy Tắc Đặt Tên & Chuẩn Hóa Địa Chỉ (Naming Conventions)

Tài liệu này định nghĩa chi tiết các quy tắc nghiệp vụ liên quan đến việc đặt tên, chuẩn hóa địa chỉ và sinh mã ID tự động của dự án BDS Khang Ngô.

## 1. Cơ Chế Sinh Mã ID Tự Động

Mỗi căn nhà trong hệ thống được quản lý bởi hai mã ID duy nhất:

### a. Mã Khang Ngô (KhangNgo ID)
- **Mục đích:** Là mã định danh nghiệp vụ hiển thị công khai cho khách hàng và dùng làm nhãn định vị.
- **Công thức sinh:** `gen_id_khang_ngo_python(so_nha, ten_duong)`
  - Loại bỏ toàn bộ dấu tiếng Việt bằng hàm `remove_accents`.
  - Viết hoa toàn bộ.
  - Số nhà được chuẩn hóa (chỉ lấy trước dấu cộng, chuyển dấu xẹt `/` và dấu chấm `.` thành dấu gạch ngang `-`).
  - Tên đường được rút gọn (lấy ký tự đầu viết hoa của mỗi từ trong tên đường sau khi loại bỏ tiền tố như "đường").
  - Ghép số nhà đã chuẩn hóa và tên đường rút gọn.
- **Quy tắc đặc biệt:**
  - `Cách Mạng Tháng 8` -> `TTMC`
  - `Ba Tháng Hai` -> `HTB`
  - `Đường số 7` -> `7SD`
- **Ví dụ:**
  - Số nhà `1168.42+44`, Đường `Cách Mạng Tháng 8` -> Mã Khang Ngô: `1168-42TTMC`.
  - Số nhà `39/2`, Đường `Ba Tháng Hai` -> Mã Khang Ngô: `39-2HTB`.

### b. System ID
- **Mục đích:** Khóa chính kỹ thuật dùng để liên kết dữ liệu thô (Pool) và dữ liệu biên tập (Source/Public), cũng như làm tham số URL chia sẻ link sạch (`?s=SYS-YYYYMMDD-XXX`).
- **Quy tắc sinh:** Dạng `SYS-YYYYMMDD-XXX` với `YYYYMMDD` là ngày cào tin và `XXX` là số tự tăng trong ngày.
- **Quy tắc bảo toàn:** Khi cào lại (recrawl) hoặc cập nhật tin, nếu căn nhà đã có `System ID` hoặc `Mã Khang Ngô` thì **bắt buộc phải giữ nguyên**, tuyệt đối không ghi đè mã mới để tránh làm gãy các liên kết đã chia sẻ cho khách hàng.

---

## 2. Chuẩn Hóa Tên Đường Đặc Biệt

Để đồng bộ tìm kiếm và tránh sai lệch ID, toàn bộ tên đường đầu vào phải đi qua bộ chuẩn hóa sau:
- **Cách Mạng Tháng 8** (CMT8, CMT Tám, Cách mạng tháng tám...): Mã hóa thành **`TTMC`**.
- **Ba Tháng Hai** (3/2, 3-2, Đường 3/2, 3 tháng 2...): Mã hóa thành **`HTB`**.
- **Đường số 7** (đường đánh số có số 7): Mã hóa thành **`7SD`**.

---

## 3. Xử Lý Số Nhà Phức Hợp

Các số nhà chứa dấu cộng (`+`) thể hiện nhiều căn gộp hoặc số phụ:
- **Quy tắc:** Chỉ lấy phần số đầu tiên trước dấu cộng.
- **Ví dụ:** `1168.42+44` ➔ chỉ trích xuất `1168.42` làm input tính toán sinh mã ID và định dạng.

---

## 4. Quy Tắc Đặt Tên Chrome Extension

Quy định cứng đối với quy trình cào dữ liệu từ Thiên Khôi:
- **Phiên bản Chrome Extension**: Đặt chữ `v` in thường kèm số phiên bản (Ví dụ: `v10`). **TUYỆT ĐỐI KHÔNG** dùng chữ `V` in hoa (`V10`).
- **Tên file ZIP Chrome Extension**: Phải giữ nguyên cấu trúc tên thư mục gốc làm tiền tố, hậu tố là version (Ví dụ: `Chrome_Ext_Crawl_TK_v10.zip`). File ZIP này khi giải nén ra phải trực tiếp trả về một thư mục mang đúng tên `Chrome_Ext_Crawl_TK` để Chrome hiểu đây là bản cập nhật, không phải Extension mới.
