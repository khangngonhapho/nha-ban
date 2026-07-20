# 📌 KẾ HOẠCH BÀN GIAO PHIÊN LÀM VIỆC TIẾP THEO (NEXT SESSION PLAN)

> **Mục đích:** File này lưu trữ trạng thái dừng của phiên làm việc hiện tại và định hướng chi tiết cho phiên làm việc tiếp theo.
> **Cách kích hoạt phiên mới:** Khi bắt đầu chat ở session mới, hãy gõ câu lệnh:
> `"Đọc file d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\docs\NEXT_SESSION.md để tiếp tục công việc."`

---

## 1. Trạng thái hiện tại của dự án (Current State)
*   **US-152 (Đồng bộ ảnh crawl trực tiếp từ nguồn Thiên Khôi (Xóa hẳn thay vì đổi status thành deleted)):** **[ACCEPTED - 2026-07-19]** Loại bỏ logic phòng vệ lưu giữ ảnh cũ khi số ảnh cào mới ít hơn trong `pool_lego.py`. Sửa đổi Smart Merge trong `manager.py` duyệt qua ảnh cũ theo thứ tự vật lý gốc để bảo toàn thứ tự tương đối, đồng thời so khớp danh sách tệp R2 vật lý và gọi `delete_r2_object(key)` xóa vĩnh viễn tệp rác trên Cloud R2.
*   **US-151 (Tự động dò tìm dòng header và vị trí cột trên sheet Source khi đồng bộ):** **[ACCEPTED - 2026-07-17]** Triển khai cơ chế tự động tìm dòng header chính thức và vị trí cột (`System ID`, `id`...) động tại runtime trên sheet Source trong cả Apps Script và Python. Khắc phục lỗi lệch dòng khi chèn mới, bảo vệ dòng 1 trống. Tích hợp cơ chế truyền Google OAuth token từ Admin dashboard vào iframe Preview Khách hàng để load dữ liệu realtime từ sheet Source dưới Secure Mode, bỏ qua lỗi và độ trễ của IMPORTRANGE trên sheet Public.
*   **US-142 (Khôi phục dữ liệu listings từ raw_json_full trong SQLite Cục bộ):** **[ACCEPTED - 2026-07-13]** Triển khai cơ chế khôi phục CSDL master cục bộ từ trường gói thô `raw_json_full` của Thiên Khôi. Tái tạo `JSON_UI` (bảo toàn lịch sử giá), điền lại các cột tiêu chí phẳng và bảng `listings_images`. Nâng cấp logic `pool_lego.py` tự động phát hiện và dọn dẹp các link R2 cũ lệch `tk_id` của căn nhà khác trên Google Sheets. Tích hợp nút cứu hộ trực quan trên HTA và API endpoint `/api/listings/recover-raw`.
*   **US-141 (Tổ chức thư mục R2 theo mã căn & Cơ chế khôi phục liên kết hình ảnh):** **[ACCEPTED - 2026-07-12]** Triển khai Prefix R2 động (`BDS-KhangNgo-v2`), gom ảnh theo cấu trúc subfolder `{uuid} - {so_nha} {duong}` không dấu an toàn, rút gọn số nhà trước dấu `+` và chuẩn hóa tên đường đặc biệt (Cách Mạng Tháng 8 ➔ TTMC, Ba Tháng Hai ➔ HTB, Đường số 7 ➔ 7SD). Hiện thực cơ chế precheck sử dụng Signature V4 REST API `ListObjectsV2` để khôi phục mapping tự động tránh tải lại. Bổ sung cơ chế auto-move di chuyển ảnh cũ dạng on-the-fly, hỗ trợ ghi đè file DB chỉ định và tích hợp HTA panel.
*   **US-140 (Quản lý Quan hệ Khách hàng (CRM) tại trang links.html di động):** **[ACCEPTED - 2026-07-12]** Triển khai giao diện CRM khách hàng trực tiếp trên `/links.html` (tab Nhật ký) với ô ghi chú Note tự động lưu và 5 trạng thái vòng đời khách hàng (LẠNH, ẤM, NÓNG, CỌC, DONE) phối màu sắc viền card. Tích hợp phím liên hệ nhanh qua Zalo và Call, cùng hiển thị thời gian tương tác cuối tương đối (ví dụ "7 ngày trước"). Triển khai API serverless Node.js (Vercel) và API Flask local sử dụng phương pháp Cập nhật ô đơn lẻ (Targeted Cell Update) để loại bỏ race condition.
*   **US-138 (Theo dõi & Thu hồi quyền truy cập Link chia sẻ công khai cùng chặn SĐT):** **[ACCEPTED - 2026-07-12]** Triển khai Web Admin di động độc lập `/links.html` (Mobile-First) hỗ trợ Bottom Navigation 4 tab: Nhật ký (gom nhóm khách hàng, mặc định mở rộng), Chặn SĐT (hiển thị thông tin ngày chặn/lý do chặn, mặc định mở rộng), Whitelist (quản lý riêng SĐT admin test, mặc định thu gọn), và Liên kết (Copy/Thu hồi link trực tuyến). Tích hợp Google OAuth2, cơ chế đóng/mở (Collapse/Expand) card mượt mà, và chuẩn hóa so khớp SĐT `cleanPhoneForCompare` khắc phục lỗi lệch card.
*   **US-139 (Nối tiếp Chuỗi Thay đổi Giá & Làm sạch Định dạng Đơn giá trên Card):** **[ACCEPTED - 2026-07-12]** Hiển thị chuỗi các mốc thay đổi giá cũ của Admin Card ở một dòng riêng biệt, canh lề trái dưới thông tin ngày tháng, cùng tone màu xám gạch ngang và font normal bình thường. Tự động ẩn mốc giá hiện tại để tránh lặp với phần hiển thị giá ở footer card. Làm sạch phần thập phân `.0` của đơn giá (ví dụ `300.0tr` ➔ `300tr`) cho cả Client Card và Admin Card.
*   **US-137 (Nâng Cấp Bộ Lọc, Sắp Xếp, Đơn Giá và Sắp Xếp Hình Trực Quan):** **[ACCEPTED - 2026-07-12]** Tách biệt hiển thị đơn giá `95.5tr/m²` màu xám và tổng giá màu xanh lá lề phải, loại hình BĐS lề trái. Ẩn hoàn toàn thông tin trạng thái nhà ở giao diện khách hàng. Áp dụng quy chuẩn viết tắt Trạng thái (`Đ.Bán`, `Đ.Cọc`, `Đã bán`) và Loại hình (`M.Tiền`, `CC`) trên Admin Card. Tích hợp lọc khoảng ngày cập nhật/ký nhà, dropdown sắp xếp mới đồng bộ desktop/mobile, persistent bộ lọc/sắp xếp qua LocalStorage. Vá lỗi 15 ảnh công khai bằng `Images_Public_JSON`, swap ảnh và sort thứ tự ảnh trực quan trong Image Editor. Đồng thời thêm hàm nghiệp vụ `clean_sheet_formula_prefix` tự động trim tiền tố công thức Google Sheets (`+`, `-`, `=`) trước khi ghi SQLite.
*   **US-136 (Tích hợp hiển thị và biên tập Tọa độ bản đồ chi tiết):** **[ACCEPTED - 2026-07-11]** Tích hợp hiển thị và biên tập tọa độ vĩ độ/kinh độ trong trang chi tiết Vercel Admin (được lưu tại JSON_UI ở Pool1 và listings_custom_v2 ở Pool2). Thay thế iframe bản đồ nhúng bằng liên kết ngoài click dẫn trực tiếp đến Google Maps (nút Xem định vị trên Google Maps ↗ nằm ở lề phải). Đồng bộ ảnh R2.
*   **US-135 (Tự động phát hiện thay đổi và lưu lịch sử giá cho Admin):** **[ACCEPTED - 2026-07-11]** Triển khai cơ chế quét so sánh giá chào và ngày cập nhật cho các căn đã có trong SQLite cục bộ.
*   **US-134 (Cào trực tiếp tin thô từ trang danh sách Thiên Khôi về SQLite cục bộ - Hybrid Model):** **[ACCEPTED - 2026-07-11]** Tích hợp thành công mô hình cào lai (Hybrid Scraper).
*   **US-132 (Phân giải Đánh số Thứ tự Ảnh và Hiển thị Đồng nhất trên Trang Chi tiết Khách hàng):** **[ACCEPTED - 2026-07-11]** Giải quyết triệt để lỗi mất số thứ tự sequence ID hiển thị trên slide ảnh lớn và thumbnail strip trong Curator Editor.
*   **US-131 (Khắc phục lệch ảnh khi cào lại và phân giải Images_Admin_JSON trên Web Vercel Admin):** **[ACCEPTED - 2026-07-11]** Khắc phục triệt để lỗi lệch/thiếu ảnh khi cào lại, tự động phân loại vai trò Mặt tiền và Sơ đồ ở backend.
*   **US-126 (Nâng Cấp Trang Tải Ảnh Hàng Loạt Thành Ứng Dụng Cài Đặt (PWA) Cô Lập):** **[ACCEPTED - 2026-07-09]** Triển khai cấu hình PWA manifest.json và Service Worker sw.js.
*   **US-124 (Trình Xem Và Tải Ảnh Hàng Loạt Từ URL & Nâng Cấp Bộ Giải Mã JSON Siêu Bền Bỉ):** **[ACCEPTED - 2026-07-09]** Triển khai giao diện tải ảnh hàng loạt /view-images.
*   **US-120A (Quản lý & Sắp xếp Hình ảnh Công khai dạng JSON):** **[ACCEPTED - 2026-07-09]** Quản lý và sắp xếp hình ảnh công khai dạng JSON trên trang Curation Admin.
*   **US-123 (Thêm Sheet "Pool_Images" chuyên lưu hình ảnh làm Backup):** **[DRAFT - 2026-07-09]** Triển khai phân hệ hình ảnh độc lập.
*   **US-122 (Trang thông báo bảo trì khi bật maintenance_mode):** **[ACCEPTED - 2026-07-09]** Triển khai màn hình thông báo bảo trì kính mờ (glassmorphism).
*   **US-121 (Quản lý và Feature Flags):** **[ACCEPTED - 2026-07-09]** Triển khai feature flags.
*   **US-119 (Quản lý và Biên tập Đường trước nhà & Độ rộng hẻm):** **[ACCEPTED - 2026-07-01]** Tách biệt custom street type (dropdown) và custom alley width (text input).
*   **US-118 (Tùy biến Diện tích Sổ & Diện tích Thực tế trên Sheet Source và Vercel Detail):** **[ACCEPTED - 2026-07-01]** Tách biệt và tùy biến lưu trữ DT Thực tế (Cột F) và DT Trên sổ (Cột AV mới thêm).
*   **US-117 (Tự động hóa Sao lưu Định kỳ CSDL SQLite cục bộ):** **[ACCEPTED - 2026-07-01]** Tạo script chạy ngầm độc lập scratch/run_backup_only.py.
*   **US-116 (Reset CSDL và Khôi phục/Vá Dữ liệu biên tập theo Địa chỉ):** **[ACCEPTED - 2026-06-30]** Tiến hành sao lưu 9,231 ảnh R2 cũ.
*   **US-115 (Khắc phục lỗi cơ sở dữ liệu SQLite bị hỏng (malformed)):** **[ACCEPTED - 2026-06-30]** Kích hoạt SQLite WAL Mode.
*   **US-114 (Khắc phục lỗi cú pháp bat và ERROR Sheets):** **[ACCEPTED - 2026-06-29]** Khắc phục lỗi bat và ERROR Sheets.
*   **US-113 (Sửa lỗi chớp chớp đen màn hình trên iPhone):** **[ACCEPTED - 2026-06-29]** Sửa lỗi chớp chớp đen màn hình trên iPhone.
*   **US-112 (Đồng bộ siêu cấu trúc Master Prompt mới):** **[ACCEPTED - 2026-06-29]** Đồng bộ siêu cấu trúc Master Prompt mới.
*   **US-111 (Sửa lỗi khóa panel Biên Tập):** **[ACCEPTED - 2026-06-29]** Sửa lỗi khóa panel Biên Tập.
*   **US-110 (Quản lý và Biên tập Hướng nhà):** **[ACCEPTED - 2026-06-28]** Tự động bóc tách Hướng từ DOM/API Thiên Khôi.
*   **US-109 (Lấy tiêu đề thô cào về lưu vào cột Nội dung chính):** **[ACCEPTED - 2026-06-27]** Lưu trực tiếp trường title từ userscript.
*   **US-108 (Sửa lỗi save Curation):** **[ACCEPTED - 2026-06-26]** Sửa lỗi save Curation.
*   **US-107 (Đồng bộ Realtime và Hiển thị Toàn bộ Căn nhà):** **[ACCEPTED - 2026-06-26]** Đồng bộ realtime và hiển thị toàn bộ căn nhà.
*   **US-106 (Giao diện Canvas trực quan):** **[ACCEPTED - 2026-06-24]** Thiết lập bảng nhìn toàn cảnh trực quan Canvas Detail View.
*   **US-105 (Hiện nút Tự động điền AI):** **[ACCEPTED - 2026-06-22]** Hiện nút Tự động điền AI.
*   **US-104 (Carousel sodo detail):** **[ACCEPTED - 2026-06-22]** Carousel sodo detail.
*   **US-103 (Userscript Cào Căn Nhà):** **[ACCEPTED - 2026-06-22]** Userscript cào căn nhà.
*   **US-102 (Thiếu JSON):** **[ACCEPTED - 2026-06-21]** Thiếu JSON.
*   **US-100 (JSON 2 tầng):** **[ACCEPTED - 2026-06-21]** JSON 2 tầng.
*   **US-097 (Fix quick share link):** **[ACCEPTED - 2026-06-16]** Fix quick share link.
*   **US-094E (Tái cấu trúc Lego Frontend):** **[ACCEPTED - 2026-06-16]** Tái cấu trúc Lego Frontend.
*   **US-094F (Module chi tiết admin):** **[ACCEPTED - 2026-06-16]** Module chi tiết admin.
*   **US-094D (Module bộ sưu tập & lead capture):** **[ACCEPTED - 2026-06-15]** Module bộ sưu tập & lead capture.
*   **US-094B (Module bộ lọc):** **[ACCEPTED - 2026-06-15]** Module bộ lọc.
*   **US-094C (Module chi tiết khách hàng):** **[ACCEPTED - 2026-06-15]** Module chi tiết khách hàng.
*   **US-094A3 (Engine Render Card):** **[ACCEPTED - 2026-06-15]** Engine Render Card.
*   **US-094A2 (Core State Store):** **[ACCEPTED - 2026-06-15]** Core State Store.
*   **US-089D (Schema R2 upload):** **[ACCEPTED - 2026-06-15]** Schema R2 upload.
*   **US-089C (Đồng bộ hai chiều SQLite):** **[ACCEPTED - 2026-06-14]** Đồng bộ hai chiều SQLite.
*   **US-089B (Sync sheets public):** **[ACCEPTED - 2026-06-14]** Sync sheets public.
*   **US-093 (Kiểm toán ảnh tự upload):** **[ACCEPTED - 2026-06-14]** Kiểm toán ảnh tự upload.
*   **US-092 (Fix missing index.html vercel):** **[ACCEPTED - 2026-06-13]** Fix missing index.html vercel.
*   **US-090 (R2 migration Cloudinary):** **[ACCEPTED - 2026-06-13]** R2 migration Cloudinary.
*   **US-089A (SQLite v2):** **[ACCEPTED - 2026-06-12]** SQLite v2.
*   **US-088 (Lego backend refactoring):** **[ACCEPTED - 2026-06-11]** Lego backend refactoring.

---

## 2. Kế hoạch hành động phiên tiếp theo (Action Plan)

### 🚀 Tính năng Backlog đề xuất (To-Do 📋)
*   **US-091 (Khắc phục lỗi giảm chất lượng hình ảnh quá mức khi di cư sang R2):** **[BACKLOG]** Phục hồi chất lượng hình ảnh cao sắc nét từ TK. Tạm dừng để ưu tiên refactoring Frontend.
*   **US-101 (Tối ưu hóa di cư ảnh khi cào lại và bảo toàn hình ảnh tự tải lên):** **[BACKLOG]** Tránh cào lại và nén/upload lại ảnh đã di cư, bảo vệ và loại trừ ảnh tự tải lên khi recrawl.

### 💡 Nhiệm vụ: Bảo trì & Theo dõi UI/UX
*   Chạy bộ test E2E Playwright để kiểm soát hồi quy giao diện sau mỗi đợt cập nhật.

---

## 3. Các file bị tác động trong phiên vừa qua

*   [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py) — Loại bỏ phòng vệ ảnh thô Thiên Khôi; Sửa lỗi mapping chữ hoa/thường cho custom_huong.
*   [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py) — Sửa thuật toán Smart Merge bảo toàn thứ tự tương đối, tích hợp gọi delete_r2_object(key) dọn dẹp file R2; Sửa lỗi mapping chữ hoa/thường cho custom_huong.
*   [query_helper.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/query_helper.py) — Sửa lỗi mapping chữ hoa/thường cho custom_huong.
*   [static/js/lego_render_admin.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_render_admin.js) — Bỏ icon ghim vị trí, thay đổi nhãn hiển thị nút lên sóng từ SONG/CHƯA thành ON/OFF, ẩn Quận khi không có quận.
*   [static/js/lego_render_client.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_render_client.js) — Bỏ icon ghim vị trí, ẩn Quận khi không có quận.
*   [tests/test_db.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/tests/test_db.py) — Cập nhật các test case ghi đè ảnh cào cũ.
*   [tests/test_image_sync_us152.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/tests/test_image_sync_us152.py) — Chạy unit test kiểm thử smart merge và xóa R2.
*   [DF-004_image_migration.md](file:///d:/LHTBrain/.agents/truth_cards/DF-004_image_migration.md) — Nâng cấp Truth Card lên v9.
*   [docs/stories/_inbox/US-152.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-152.md) — Tài liệu User Story US-152.
*   [thienkhoi_cookie.txt](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/thienkhoi_cookie.txt) — Cập nhật cookie mới.

---
*Kế hoạch được lập tự động bởi Antigravity AI Assistant. Cập nhật cuối: 2026-07-21 (US-152 accepted & custom_huong mapping fix deployed).*


