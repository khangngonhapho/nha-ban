# Project Glossary & Terminology (Bảng Thuật Ngữ Dự Án)

Tài liệu này đóng vai trò là **Từ điển Thuật ngữ (Jargon Dictionary)** của dự án, định nghĩa rõ ràng các thuật ngữ chuyên môn và nghiệp vụ đặc thù được sử dụng trong hệ sinh thái BDS Khang Ngô Nhà Phố. 

---

## 📋 Danh mục Thuật ngữ Nghiệp vụ (Domain Glossary)

| Thuật ngữ | Định nghĩa nghiệp vụ | Phạm vi ảnh hưởng / Ví dụ |
|---|---|---|
| **Mã Khang Ngô (ID)** | Mã định danh duy nhất của mỗi căn nhà công khai trên website. Được sinh tự động từ thuật ngữ viết tắt của Quận, Phường, Đường và Hẻm. | Ví dụ: `MWMSTIAHIST` (dựa trên địa chỉ Trường Sa) |
| **Pool (Kho dữ liệu thô)** | Trang tính (tab) nội bộ chứa toàn bộ danh sách bất động sản cào được từ các nguồn, bao gồm dữ liệu thô, ảnh gốc, và thông tin cá nhân của chủ nhà/đầu chủ. | Cần bảo mật cao, không public. |
| **Source (Rổ hàng public)** | Trang tính chứa các bất động sản đã được lọc, curation sạch và sẵn sàng đồng bộ để hiển thị lên trang chủ website. | Nguồn cấp dữ liệu cho `index.html`. |
| **Curator App** | Ứng dụng mini-app (Flask backend + HTML frontend) dùng để duyệt tin, chỉnh sửa hàng loạt, nén ảnh sơ đồ, và quản lý luồng dữ liệu từ Pool sang Source. | Biên dịch thành `KhangNgoCuratorApp.exe`. |
| **Junction Link** | Cơ chế liên kết ảo (virtual link) thư mục NTFS giúp đồng bộ hóa thời gian thực 2 chiều giữa mã nguồn cục bộ (`D:\LHTBrain`) và thư mục bộ não của AI. | Phục vụ đồng bộ hóa đa thiết bị. |

---

## 🛠️ Danh mục Từ viết tắt Kỹ thuật (Technical Abbreviations)

| Từ viết tắt | Thuật ngữ đầy đủ | Định nghĩa và Quy tắc xử lý |
|---|---|---|
| **TTMC** | Tuyến Trục Minh Châu | Tên đường mã hóa đặc biệt thay thế cho đường **Cách Mạng Tháng 8** (CMT8/CMT Tám...) để tránh các lỗi logic khớp chuỗi. |
| **HTB** | Hẻm Thương Binh | Tên đường mã hóa đặc biệt thay thế cho đường **Ba Tháng Hai** (3/2, 3 Tháng 2...) để tối ưu hóa việc phân tách địa lý. |
| **7SD** | 7 Song Đường | Tên đường mã hóa đặc biệt thay thế cho **Đường số 7** để phân biệt với hẻm số hoặc các đường đánh số khác. |
| **PII** | Personally Identifiable Information | Thông tin định danh cá nhân (tên chủ nhà, số điện thoại, số tài khoản...). Bắt buộc phải mã hóa/loại bỏ trước khi gửi qua API bên thứ ba. |
| **DoR** | Definition of Ready | Định nghĩa Sẵn sàng: Tiêu chuẩn tối thiểu để một yêu cầu (Backlog) đủ điều kiện đưa vào lập kế hoạch (Planning). |
| **DoD** | Definition of Done | Định nghĩa Hoàn thành: Tiêu chuẩn bắt buộc phải đạt để một User Story được đánh dấu là hoàn thành (`done`). |

---

*Tài liệu này được cập nhật liên tục bởi AI và PO tại mỗi phiên làm việc khi phát sinh thuật ngữ mới.*
