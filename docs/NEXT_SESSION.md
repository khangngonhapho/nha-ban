# 📌 KẾ HOẠCH BÀN GIAO PHIÊN LÀM VIỆC TIẾP THEO (NEXT SESSION PLAN)

> **Mục đích:** File này lưu trữ trạng thái dừng của phiên làm việc hiện tại và định hướng chi tiết cho phiên làm việc tiếp theo.
> **Cách kích hoạt phiên mới:** Khi bắt đầu chat ở session mới, hãy gõ câu lệnh:
> `"Đọc file d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\docs\NEXT_SESSION.md để tiếp tục công việc."`

---

## 1. Trạng thái hiện tại của dự án (Current State)
*   **US-094A3 (Phân tách Engine Render danh sách Card BĐS):** **[DONE - 2026-06-15]** Tạo mới module `static/js/lego_render_client.js` và `static/js/lego_render_admin.js` tách biệt hoàn toàn phần render dữ liệu Card (`DocumentFragment`) ra khỏi `index.html` cho cả giao diện Khách hàng và Admin, bảo đảm tương thích ngược 100% và không làm gãy các tính năng tương tác. Đã chạy E2E Playwright test đạt 100% PASS.
*   **US-094A2 (Xây dựng Lego Core State Store & Tải dữ liệu):** **[ACCEPTED - 2026-06-15]** Tạo mới module `static/js/lego_core.js` định nghĩa `window.LegoState` để đóng gói toàn bộ trạng thái lõi, logic xác thực Google OAuth (GSI Auth), tự động refresh token ngầm và luồng nạp dữ liệu Sheets API (Admin secure + public fallback). Thiết lập cơ chế Event-Driven (Pub/Sub) và liên kết các getters/setters toàn cục tương thích ngược 100% không gây lỗi hồi quy. Kiểm thử Playwright E2E đạt 100% PASS trên Desktop & Mobile.
*   **US-094A1 (Tách biệt CSS ngoài ra global.css):** **[ACCEPTED - 2026-06-15]** Di chuyển toàn bộ ~3,650 dòng CSS trong `index.html` sang `static/css/global.css`, liên kết qua thẻ `<link>` và cấu hình static serving trên Vercel với tiêu đề `Cache-Control`. Đã chạy kiểm thử Playwright E2E đạt 100% PASS, nghiệm thu giao diện hiển thị mượt mà trên môi trường Production.
*   **US-089D (Luồng Tự động Mở rộng Schema & Đăng tải Hình ảnh Thủ công):** **[DONE - 2026-06-15]** Loại bỏ hoàn toàn Cloudinary khỏi dự án. Đổi tên cột CSDL `cloudinary_url` thành `r2_url` và di cư an toàn. Triển khai API/UI thêm thuộc tính động (Dynamic Schema) tự động chèn cột settings/CSDL/Sheets/Tài liệu và API tải ảnh thủ công cách ly ảnh nhạy cảm bảo mật PII.
*   **US-089C (Triển khai Cơ chế Đồng bộ Hai Chiều Liên Database):** **[DONE - 2026-06-14]** Triển khai cơ chế đồng bộ hai chiều dữ liệu SQLite local giữa rổ hàng cũ Pool1 (`raw_archive.db`) và hệ thống mới Pool2 (`raw_archive_v2.db`). Tích hợp recrawl định kỳ và lưu log khác biệt vào cột `pending_diff_json`, sẵn sàng APIs áp dụng chọn lọc.
*   **US-089B (Tích hợp Google Sheets Đa Quyền Hạn & Luồng Xuất bản Public Whitelist):** **[ACCEPTED - 2026-06-14]** Đồng bộ dữ liệu sạch và rã mảng hình ảnh an toàn thành các cột Ảnh 1..Ảnh N lên sheet Public. Giữ cột Last updated trước toàn bộ cột ảnh. Khắc phục triệt để lỗi quota API 429 bằng cơ chế gộp cập nhật thêm cột và dòng tiêu đề. Tự động đồng bộ link R2 mới vào custom metadata.
*   **US-093 (Kiểm tra tính khả dụng và lập báo cáo hình ảnh tự tải lên):** **[ACCEPTED - 2026-06-14]** Đã hoàn tất công cụ kiểm toán `scratch/audit_manual_images.py` quét 23 căn chứa 98 ảnh tự tải lên trong Pool1 (`raw_archive.db`), phát hiện và báo cáo 2 căn bị lỗi HTTP 503 đối với link R2. Cấu trúc lại báo cáo hợp nhất `broken_listings_report.md` thành 3 đề mục `##` collapsible.
*   **US-092 (Sửa lỗi Internal Server Error: Missing index.html khi truy cập trang chủ):** **[ACCEPTED - 2026-06-13]** Khắc phục lỗi thiếu index.html trên Vercel Serverless bằng cách sử dụng fallback __dirname để Vercel NFT đóng gói tệp tĩnh và cấu hình includeFiles trong vercel.json.
*   **US-090 (Di cư toàn bộ kho hình ảnh sang Cloudflare R2 & Khắc phục giới hạn hạn mức Cloudinary):** **[ACCEPTED - 2026-06-13]** Đã hoàn tất di cư toàn bộ 5.180 ảnh từ Cloudinary sang Cloudflare R2 trên SQLite và đồng bộ lên Google Sheet Pool (v1). Giải quyết triệt để lỗi chuỗi JSON mảng trên Sheets và thiết lập báo cáo danh sách 581 căn lỗi ảnh 404 (ở cả Sheets và SQLite) kèm địa chỉ thực chi tiết.
*   **US-089A (Thiết lập CSDL Quan hệ Pool2 & Tích hợp Luồng Cào thô cục bộ):** **[ACCEPTED - 2026-06-12]** Đã triển khai cấu trúc CSDL SQLite v2 sạch sẽ không chứa các cột hình ảnh phẳng, lưu trữ hình ảnh độc lập có khóa ngoại và sequence_index tuần tự trong `listings_images` và `raw_images_tk_json`. Tích hợp luồng bóc tách tiêu chí thô `parse_criteria_groups` và dynamic badges DOM fallback, đồng thời thiết lập cơ chế phân nhóm hình ảnh (nội thất trước, sơ đồ sau) tự động bảo toàn trình tự. Xây dựng công cụ `query_helper.py` tra cứu nhanh và hiển thị Premium HTML Dark Mode.
*   **US-088 (Đổi tên file và di cư tính năng cũ (Pool1) sang Lego):** **[ACCEPTED - 2026-06-11]** Phân rã toàn bộ logic nghiệp vụ (schema, SQLite write, Sheets sync) của Pool1 cũ ra một khối Lego trung tâm `pool_lego.py` và đổi tên các file cốt lõi sang tiếng Anh thân thiện dễ hiểu (`settings.json`, `fetcher.py`, `manager.py`). Đã biên dịch, chạy thử cào và xuất bản ổn định không lỗi hồi quy, đóng gói EXE và tích hợp tài liệu chi tiết vào SOT.
*   **US-087 (Fix lỗi không xóa được bộ sưu tập đã tồn tại):** **[ACCEPTED - 2026-06-11]** Khắc phục lỗi không xóa được bộ sưu tập trên di động do hiện tượng cuộn vi mô (micro-scroll) của Chrome di động hủy bỏ click trong vùng cuộn. Giải pháp: tích hợp checkbox 24px lớn bên cạnh danh sách bộ sưu tập trong modal, và tự động chuyển các nút hành động của Speed Dial nổi ở vị trí `fixed` (không bị ảnh hưởng bởi vùng cuộn) thành một nút xóa BST màu đỏ duy nhất chứa biểu tượng `🗑️` (chỉ icon không chữ).
*   **US-086 (Fix lỗi tạo bộ sưu tập):** **[ACCEPTED - 2026-06-11]** Sửa lỗi hiển thị màu chữ trắng trên nền trắng (white-on-white) của các nút chọn bộ sưu tập trên modal, tự động bỏ chọn toàn bộ checkbox chọn căn trên giao diện sau khi tạo hoặc lưu bộ sưu tập thành công, đồng thời cập nhật logic so khớp ID chỉ dùng duy nhất mã `system_id` để tránh lệch dữ liệu.

---

## 2. Kế hoạch hành động phiên tiếp theo (Action Plan)

### 🚀 Tính năng đang thực hiện (In-Progress 🛠️)
*   **US-094C (Cô lập Module Chi tiết & Carousel thực tế của Khách hàng):** **[IN-PROGRESS]** Triển khai module `static/js/lego_detail_client.js` tách biệt hoàn toàn phần modal chi tiết, Swiper carousel hiển thị ảnh công khai, và logic copy link/chia sẻ nhanh ra khỏi `index.html`.

### 🚀 Tính năng Backlog đề xuất (To-Do 📋)
*   **Các US con tiếp theo của Epic US-094:**
    *   US-094B: Cô lập Module Bộ lọc & Smart Search.
    *   US-094D: Cô lập Module Bộ sưu tập & Lead Capture.
    *   US-094F: Cô lập Module Chi tiết & Curation của Admin.
    *   US-094E: Tích hợp toàn diện và cấu hình Cache Headers.
*   **US-091 (Khắc phục lỗi giảm chất lượng hình ảnh quá mức khi di cư sang R2):** **[BACKLOG]** Đã hoàn tất lên phương án phục hồi chất lượng hình ảnh cao sắc nét từ TK. Tạm dừng để ưu tiên refactoring Frontend.

### 💡 Nhiệm vụ: Bảo trì & Theo dõi UI/UX
*   Tiếp tục chạy bộ test E2E Playwright sau mỗi US con để kiểm soát hồi quy giao diện.

---

## 3. Các file bị tác động trong phiên vừa qua

*   [static/js/lego_render_client.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_render_client.js) — US-094A3: Module render card hiển thị cho khách hàng công khai.
*   [static/js/lego_render_admin.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_render_admin.js) — US-094A3: Module render card hiển thị cho quản trị viên (Admin).
*   [static/js/lego_core.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_core.js) — US-094A3: Chuyển hàm `formatPhone` sang core để dùng chung cho render và admin.
*   [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html) — US-094A3: Tích hợp script render mới, xóa `formatPhone` cũ và rút gọn hàm `render()` gốc qua Event-Delegated rendering.
*   [docs/stories/_inbox/US-094A3_lego_frontend_render.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-094A3_lego_frontend_render.md) — US-094A3: Tài liệu nghiệm thu US con.
*   [docs/stories/INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md) — Cập nhật bảng mục lục user stories.
---
*Kế hoạch được lập tự động bởi Antigravity AI Assistant. Cập nhật cuối: 2026-06-15 (US-094A3 completed & E2E tests 100% passed).*
