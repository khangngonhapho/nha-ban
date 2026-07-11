# 📖 BUSINESS RULES INDEX — Bộ Quy Tắc Nghiệp Vụ BDS Khang Ngô

Tài liệu này là mục lục trung tâm cho toàn bộ quy tắc nghiệp vụ (business rules) của dự án BDS Khang Ngô. AI Assistant bắt buộc phải đọc các tài liệu liên quan trước khi triển khai bất kỳ tính năng hoặc sửa đổi cấu trúc dữ liệu nào.

## Danh Mục Quy Tắc

1. **[Quy Tắc Đặt Tên & Chuẩn Hóa](naming_conventions.md)**
   - Cơ chế sinh mã tự động (Mã Khang Ngô, System ID).
   - Chuẩn hóa tên đường đặc biệt (CMT8 -> TTMC, 3/2 -> HTB, Đường số 7 -> 7SD).
   - Xử lý số nhà phức hợp.
   - Phiên bản Chrome Extension và file ZIP.

2. **[Quy Tắc Định Giá & Tìm Kiếm Giá](pricing_rules.md)**
   - Đơn vị giá bán (Tỷ VNĐ).
   - Quy tắc định dạng giá khi hiển thị.
   - Lọc khoảng giá thông minh qua thanh tìm kiếm.

3. **[Quy Tắc Phân Loại & Xử Lý Ảnh](image_classification.md)**
   - Phân loại ảnh Sơ đồ/Sổ đỏ, Mặt tiền, Hẻm, Nội thất.
   - Quy tắc nén ảnh & Xoay ảnh vật lý (EXIF).
   - Đồng bộ Cloudinary / Cloudflare R2 & hủy ảnh lỗi cũ (Destroy API).

4. **[Bảo Mật Dữ Liệu & PII](data_security.md)**
   - Mật khẩu đăng nhập Admin.
   - Cơ chế ẩn Số nhà & hiển thị preview riêng tư.
   - Quy tắc lọc thông tin PII (SĐT, Email, Tên) trước khi gửi LLM.

5. **[Quy Trình Biên Tập & Duyệt Tin (Curation Workflow)](curation_workflow.md)**
   - Luồng đi của dữ liệu (SQLite -> Pool Sheet -> Source Sheet -> Public Sheet).
   - Quy tắc lệch chỉ số cột (Column Shift Bug) do `IMPORTRANGE`.
   - Cơ chế Curation & Lên sóng.

6. **[Quy Tắc Tìm Kiếm & Bộ Lọc](search_filter_rules.md)**
   - Cú pháp tìm kiếm thông minh (AND phân tách dấu `+`).
   - Khớp số nhà thông minh (exact, sub-number, suffix).
   - Bản đồ Phường tĩnh (`STATIC_WARD_MAP`) cho các quận trọng điểm.
   - Cách tính `temp_id` cho sắp xếp thời gian thực.
