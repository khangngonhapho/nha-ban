# 📌 KẾ HOẠCH BÀN GIAO PHIÊN LÀM VIỆC TIẾP THEO (NEXT SESSION PLAN)

> **Mục đích:** File này lưu trữ trạng thái dừng của phiên làm việc hiện tại và định hướng chi tiết cho phiên làm việc tiếp theo.
> **Cách kích hoạt phiên mới:** Khi bắt đầu chat ở session mới, hãy gõ câu lệnh:
> `"Đọc file d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\docs\NEXT_SESSION.md để tiếp tục công việc."`

---

## 1. Trạng thái hiện tại của dự án (Current State)
*   **US-092 (Sửa lỗi Internal Server Error: Missing index.html khi truy cập trang chủ):** **[ACCEPTED - 2026-06-13]** Khắc phục lỗi thiếu index.html trên Vercel Serverless bằng cách sử dụng fallback __dirname để Vercel NFT đóng gói tệp tĩnh và cấu hình includeFiles trong vercel.json.
*   **US-090 (Di cư toàn bộ kho hình ảnh sang Cloudflare R2 & Khắc phục giới hạn hạn mức Cloudinary):** **[ACCEPTED - 2026-06-13]** Đã hoàn tất di cư toàn bộ 5.180 ảnh từ Cloudinary sang Cloudflare R2 trên SQLite và đồng bộ lên Google Sheet Pool (v1). Giải quyết triệt để lỗi chuỗi JSON mảng trên Sheets và thiết lập báo cáo danh sách 581 căn lỗi ảnh 404 (ở cả Sheets và SQLite) kèm địa chỉ thực chi tiết.
*   **US-089A (Thiết lập CSDL Quan hệ Pool2 & Tích hợp Luồng Cào thô cục bộ):** **[ACCEPTED - 2026-06-12]** Đã triển khai cấu trúc CSDL SQLite v2 sạch sẽ không chứa các cột hình ảnh phẳng, lưu trữ hình ảnh độc lập có khóa ngoại và sequence_index tuần tự trong `listings_images` và `raw_images_tk_json`. Tích hợp luồng bóc tách tiêu chí thô `parse_criteria_groups` và dynamic badges DOM fallback, đồng thời thiết lập cơ chế phân nhóm hình ảnh (nội thất trước, sơ đồ sau) tự động bảo toàn trình tự. Xây dựng công cụ `query_helper.py` tra cứu nhanh và hiển thị Premium HTML Dark Mode.
*   **US-088 (Đổi tên file và di cư tính năng cũ (Pool1) sang Lego):** **[ACCEPTED - 2026-06-11]** Phân rã toàn bộ logic nghiệp vụ (schema, SQLite write, Sheets sync) của Pool1 cũ ra một khối Lego trung tâm `pool_lego.py` và đổi tên các file cốt lõi sang tiếng Anh thân thiện dễ hiểu (`settings.json`, `fetcher.py`, `manager.py`). Đã biên dịch, chạy thử cào và xuất bản ổn định không lỗi hồi quy, đóng gói EXE và tích hợp tài liệu chi tiết vào SOT.
*   **US-087 (Fix lỗi không xóa được bộ sưu tập đã tồn tại):** **[ACCEPTED - 2026-06-11]** Khắc phục lỗi không xóa được bộ sưu tập trên di động do hiện tượng cuộn vi mô (micro-scroll) của Chrome di động hủy bỏ click trong vùng cuộn. Giải pháp: tích hợp checkbox 24px lớn bên cạnh danh sách bộ sưu tập trong modal, và tự động chuyển các nút hành động của Speed Dial nổi ở vị trí `fixed` (không bị ảnh hưởng bởi vùng cuộn) thành một nút xóa BST màu đỏ duy nhất chứa biểu tượng `🗑️` (chỉ icon không chữ).
*   **US-086 (Fix lỗi tạo bộ sưu tập):** **[ACCEPTED - 2026-06-11]** Sửa lỗi hiển thị màu chữ trắng trên nền trắng (white-on-white) của các nút chọn bộ sưu tập trên modal, tự động bỏ chọn toàn bộ checkbox chọn căn trên giao diện sau khi tạo hoặc lưu bộ sưu tập thành công, đồng thời cập nhật logic so khớp ID chỉ dùng duy nhất mã `system_id` để tránh lệch dữ liệu.

---

## 2. Kế hoạch hành động phiên tiếp theo (Action Plan)

### 🚀 Tính năng đang thực hiện (In-Progress 🛠️)
*   **US-091 (Khắc phục lỗi giảm chất lượng hình ảnh quá mức khi di cư sang R2):** **[IN-PROGRESS]** Đã hoàn tất lên phương án phục hồi chất lượng hình ảnh cao sắc nét từ TK, tối ưu hóa các tham số nén hình ảnh cào mới thành JPEG 95% và max size 2400px. Đang chờ PO duyệt kế hoạch trước khi code và chạy khôi phục thực tế.

### 🚀 Tính năng Backlog đề xuất (To-Do 📋)
*   **US-089B (Tích hợp Google Sheets Đa Quyền Hạn & Luồng Xuất bản Public Whitelist):** Tích hợp Google Sheets API v4 đồng bộ ảnh dạng dòng và metadata cho Pool2, bảo đảm các cột hình ảnh phẳng không bị đè lỗi.
*   **US-089C (Triển khai Cơ chế Đồng bộ Hai Chiều Liên Database):** Đồng bộ hai chiều giữa `listings_v2` và `listings_custom_v2` khi xuất bản hoặc update từ admin curator.
*   **US-089D (Luồng Tự động Mở rộng Schema & Đăng tải Hình ảnh Thủ công):** Cơ chế tự động chèn/mở rộng cột trong SQLite v2 khi schema có thay đổi đột xuất và hỗ trợ giao diện upload/rotate ảnh trong Pool2.
*   **Lọc theo loại hình:** Bổ sung tính năng lọc theo loại hình BĐS (Mặt tiền / Hẻm) dựa trên phân tích cấu trúc dấu `.` trong Ngõ/Số nhà.
*   **Thêm Quận mới:** Xây dựng hệ thống cấu hình động để thêm Quận mới dễ dàng khi rổ hàng mở rộng địa bàn.

### 💡 Nhiệm vụ: Bảo trì & Theo dõi UI/UX
*   Kiểm tra tính ổn định của file chạy độc lập `dist\KhangNgoCurator\KhangNgoCurator.exe` khi cào tin và xuất bản trong môi trường thực tế dưới chế độ Pool2.
*   Theo dõi tiến trình di cư hình ảnh lên Cloudinary và Zalo Crawler xem trước (og:image) khi chia sẻ link khách hàng.

---

## 3. Các file bị tác động trong phiên vừa qua

*   [vercel.json](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/vercel.json) — US-092: Cấu hình includeFiles đóng gói index.html.
*   [api/index.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/api/index.js) — US-092: Thêm cơ chế đọc file tĩnh tương đối qua __dirname.
*   [docs/stories/_inbox/US-092_fix_homepage_missing_index_error.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-092_fix_homepage_missing_index_error.md) — US-092: Đặc tả và nghiệm thu User Story.
*   [scratch/migrate_to_r2.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/migrate_to_r2.py) — US-090: Công cụ di cư tải hình ảnh từ Cloudinary và đẩy lên Cloudflare R2 đa luồng.
*   [scratch/sync_pool_v1_sheet.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/sync_pool_v1_sheet.py) — US-090: Cập nhật cơ chế đồng bộ Sheets Pool (v1) với so khớp chéo tên file và làm sạch JSON mảng.
*   [scratch/list_broken_listings.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/list_broken_listings.py) — US-090: Script lập báo cáo lỗi ảnh Cloudinary 404 có trích xuất địa chỉ thực từ Google Sheets.
*   [scratch/check_db_cloudinary.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/check_db_cloudinary.py) — US-090: Script kiểm tra lỗi di cư hình ảnh trong SQLite và nối kết quả vào báo cáo lỗi.
*   [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py) — US-089A: Thiết lập cơ chế **phân nhóm hình ảnh (Nội thất trước, Sơ đồ sau)** và lưu sequential sequence_index.
*   [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py) — US-089A: Đồng bộ database join thô/custom, trích xuất dữ liệu phường cũ và cập nhật API lưu kích thước/mặt tiền.
*   [fetcher.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/fetcher.py) — US-089A: Tích hợp `parse_criteria_groups()` và cào badges tiêu chí thô qua DOM fallback.
*   [query_helper.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/query_helper.py) — US-089A: Code mới công cụ tra cứu CSDL thô trực quan cục bộ xuất HTML Dark Mode.
*   [TRUY_VAN_CSDL.bat](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/TRUY_VAN_CSDL.bat) — US-089A: Code mới shortcut chạy CLI query_helper.
*   [curator.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator.html) — US-089A: Thêm trường nhập Chiều dài và Mặt tiền, cải tiến regex trích xuất UUID.
*   [scratch/delete_phan_tay_ho.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/delete_phan_tay_ho.py) — US-089A: Công cụ xóa căn thô/custom/images để test lại luồng cào.
*   [scratch/test_diagram_migration_mock.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_diagram_migration_mock.py) — US-089A: Script unit test kiểm thử di cư ảnh phân nhóm và sequence check.
*   [scratch/test_schema_v2_and_rich_fields.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_schema_v2_and_rich_fields.py) — US-089A: Script unit test kiểm thử schema listings_v2 sạch.

---
*Kế hoạch được lập tự động bởi Antigravity AI Assistant. Cập nhật cuối: 2026-06-13 (US-092 completed & Vercel index.html error resolved).*
