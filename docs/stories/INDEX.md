# Stories Index

Last updated: 2026-07-21

## Stats
- Total: 156
- backlog: 3
- draft: 7
- in-progress: 0
- done: 23
- accepted: 119
- superseded: 6

| ID     | Title                                                                  | Status   | Size | Date       | Files                                                             |
| ------ | ---------------------------------------------------------------------- | -------- | ---- | ---------- | ----------------------------------------------------------------- |
| US-157 | Tự Động Ghi Nhật Ký Lịch Sử (Audit Log) Thay Đổi Dữ Liệu Trên Sheets Pool_Log Và Source_Log | done | M | 2026-07-28 | `pool_lego.py`, `static/js/lego_detail_admin.js`, `api/index.js`, `docs/stories/_inbox/US-157.md` |
| US-156 | Khắc phục Lỗi Lệch Chỉ Số Dòng Sheet Pool & Ngăn Chặn Chép Đè Hình Ảnh Khi Lên Sóng | accepted | M | 2026-07-23 | `static/js/lego_core.js`, `static/js/lego_detail_admin.js`, `index.html`, `docs/stories/_inbox/US-156.md` |
| US-155 | Dynamic OpenGraph Link Preview từ Cloudflare R2 CDN                    | accepted | S    | 2026-07-23 | `api/index.js`, `scratch/test_us155_og_tags.py`, `docs/stories/_inbox/US-155.md` |
| US-154 | Tối ưu hóa hiệu năng hiển thị Khách hàng & Admin Preview bằng kiến trúc JSON Sharding qua Cloudflare R2 | accepted | L | 2026-07-21 | `manager.py`, `api/index.js`, `static/js/lego_detail_admin.js`, `static/js/lego_core.js`, `index.html`, `docs/stories/_inbox/US-154.md` |
| US-153 | Thêm trường custom_phuong và custom_quan trong SQLite và Google Sheets | draft    | M    | 2026-07-21 | `pool_lego.py`, `manager.py`, `static/js/lego_detail_admin.js`, `static/js/lego_core.js`, `docs/stories/_inbox/US-153.md` |
| US-152 | Đồng bộ ảnh crawl trực tiếp từ nguồn Thiên Khôi (Xóa hẳn thay vì đổi status thành deleted) | accepted | S | 2026-07-19 | `pool_lego.py`, `manager.py`, `tests/test_db.py`, `tests/test_image_sync_us152.py`, `docs/stories/_inbox/US-152.md` |
| US-151 | Tự động dò tìm dòng header và vị trí cột trên sheet Source khi đồng bộ | accepted | S | 2026-07-17 | `pool_backend_v3.gs`, `pool_lego.py`, `docs/stories/_inbox/US-151_dynamic_row_col_sync_source_sheet.md` |
| US-150 | Di chuyển cơ sở dữ liệu SQLite sang thư mục an toàn và phục hồi raw_json_full | draft | M | 2026-07-14 | `settings.json`, `core/db.py`, `scratch/recover_and_migrate_db.py`, `docs/stories/_inbox/US-150.md` |
| US-149 | Hiển thị tag "Giảm chào" trên Card Vercel Admin | done | S | 2026-07-14 | `settings.json`, `static/js/lego_render_admin.js`, `scratch/migrate_json_ui_tags.py`, `docs/stories/_inbox/US-149.md` |
| US-148 | Bổ sung cảnh báo âm thanh lớn khi cào hàng loạt bị ngắt do lỗi xác thực | draft | S | 2026-07-14 | `fetcher.py`, `docs/stories/_inbox/US-148.md` |
| US-147 | Loại bỏ bước gọi AI tự động trong luồng background worker di cư ảnh | done | S | 2026-07-14 | `background_worker.py`, `manager.py`, `docs/stories/_inbox/US-147.md` |
| US-146 | Biên tập và quản lý các ảnh có trạng thái role = 'deleted' | draft | M | 2026-07-14 | `static/js/lego_detail_admin.js`, `manager.py`, `docs/stories/_inbox/US-146.md` |
| US-145 | Xử lý chạy ngầm tác vụ nặng cào để tránh mất kết nối server | accepted | M | 2026-07-13 | `background_worker.py`, `pool_lego.py`, `api/routes_crawl.py`, `docs/stories/_inbox/US-145.md` |
| US-144 | Liên kết Facebook và sắp xếp thông tin đầu chủ trên Card Admin | accepted | S | 2026-07-13 | `static/js/lego_render_admin.js`, `docs/stories/_inbox/US-144.md` |
| US-142 | Khôi phục dữ liệu listings từ raw_json_full trong SQLite Cục bộ | accepted | M    | 2026-07-13 | `pool_lego.py`, `core/business_rules.py`, `api/routes_pool.py`, `scratch/recover_raw_json.py`, `tests/test_recovery.py`, `docs/stories/_inbox/US-142_recovery_from_raw_json.md` |
| US-141 | Tổ chức thư mục R2 theo mã căn & Cơ chế khôi phục liên kết hình ảnh | accepted | M | 2026-07-12 | `settings.json`, `manager.py`, `api/routes_images.py`, `scratch/rescue_r2_images.py`, `docs/stories/_inbox/US-141_r2_image_migration_subfolders_and_recovery.md` |
| US-140 | Quản lý Quan hệ Khách hàng (CRM) tại trang links.html di động | accepted | M | 2026-07-12 | `pool_lego.py`, `restore_db_from_sheets.py`, `api/routes_links.py`, `api/index.js`, `links.html`, `docs/stories/_inbox/US-140_customer_relationship_management.md` |
| US-139 | Nối tiếp Chuỗi Thay đổi Giá & Làm sạch Định dạng Đơn giá trên Card | accepted | S | 2026-07-12 | `index.html`, `static/js/lego_helpers.js`, `static/js/lego_render_client.js`, `static/js/lego_render_admin.js`, `docs/stories/_inbox/US-139.md` |
| US-138 | Theo dõi & Thu hồi quyền truy cập Link chia sẻ công khai cùng chặn SĐT | accepted | M | 2026-07-11 | `manager.py`, `curator.html`, `index.html`, `static/js/lego_helpers.js`, `static/js/lego_lead_capture.js`, `api/routes_links.py`, `tests/test_link_revocation.py`, `docs/stories/_inbox/US-138_link_tracking_and_revocation.md` |
| US-137 | Nâng Cấp Bộ Lọc, Sắp Xếp, Đơn Giá và Sắp Xếp Hình Trực Quan | accepted | M | 2026-07-12 | `index.html`, `static/js/lego_filters.js`, `static/js/lego_helpers.js`, `static/js/lego_render_client.js`, `static/js/lego_render_admin.js`, `static/js/lego_detail_admin.js`, `static/js/lego_detail_client.js`, `static/css/global.css`, `core/business_rules.py`, `pool_lego.py`, `api/routes_pool.py`, `tests/test_business_rules.py`, `docs/stories/_inbox/US-137.md` |
| US-136 | Tích hợp hiển thị và biên tập Tọa độ bản đồ chi tiết | accepted | S | 2026-07-11 | `settings.json`, `pool_lego.py`, `api/routes_pool.py`, `static/js/lego_detail_admin.js`, `docs/stories/_inbox/US-136.md` |
| US-135 | Tự động phát hiện thay đổi và lưu lịch sử giá cho Admin | accepted | M | 2026-07-11 | `pool_lego.py`, `api/routes_pool.py`, `api/routes_crawl.py`, `curator.html`, `BANG_DIEU_HANH.hta`, `Chrome_Ext_Crawl_TK/content.js`, `static/js/lego_render_admin.js`, `static/js/lego_detail_admin.js`, `docs/stories/_inbox/US-135.md` |
| US-134 | Cào trực tiếp tin thô từ trang danh sách Thiên Khôi về SQLite cục bộ | accepted | M | 2026-07-11 | `Chrome_Ext_Crawl_TK/content.js`, `api/routes_crawl.py`, `docs/stories/_inbox/US-134.md` |
| US-133 | Tìm kiếm và Lọc theo Loại hình (Mặt tiền / Hẻm) | done | S | 2026-07-11 | `index.html`, `static/js/lego_filters.js`, `static/js/lego_helpers.js`, `docs/stories/_inbox/US-133.md` |
| US-132 | Phân giải Đánh số Thứ tự Ảnh và Hiển thị Đồng nhất trên Trang Chi tiết Khách hàng | accepted | S | 2026-07-11 | `static/js/lego_core.js`, `static/js/lego_detail_admin.js`, `static/js/lego_detail_client.js`, `static/js/lego_render_client.js`, `docs/stories/_inbox/US-132.md` |
| US-131 | Khắc phục lệch ảnh khi cào lại và phân giải Images_Admin_JSON trên Web Vercel Admin | accepted | M | 2026-07-10 | `manager.py`, `static/js/lego_core.js`, `static/js/lego_helpers.js`, `static/js/lego_render_admin.js`, `index.html`, `sw.js`, `docs/stories/_inbox/US-131_fix_recrawl_image_mismatch.md` |
| US-126 | Nâng Cấp Trang Tải Ảnh Hàng Loạt Thành Ứng Dụng Cài Đặt (PWA) Cô Lập | accepted | M | 2026-07-09 | `manifest.json`, `sw.js`, `view-images.html`, `vercel.json`, `api/index.js`, `api/routes_curation.py`, `tests/test_api_contracts.py`, `static/img/icon-192.png`, `static/img/icon-512.png`, `docs/stories/_inbox/US-126_pwa_installable_app.md` |
| US-125 | Tự động Login và Tự động Cuộn trên trang danh sách Thiên Khôi | done | M | 2026-07-09 | `Chrome_Ext_Crawl_TK/manifest.json`, `Chrome_Ext_Crawl_TK/background.js`, `Chrome_Ext_Crawl_TK/content.js`, `docs/stories/_inbox/US-125_auto_login_and_auto_scroll_crawler.md` |
| US-124 | Trình Xem Và Tải Ảnh Hàng Loạt Từ URL | accepted | S | 2026-07-09 | `view-images.html`, `vercel.json`, `api/index.js`, `api/routes_curation.py`, `tests/test_api_contracts.py`, `docs/stories/_inbox/US-124_image_url_viewer_downloader.md` |
| US-123 | Thêm Sheet "Pool_Images" chuyên lưu hình ảnh làm Backup | draft | M | 2026-07-09 | `pool_lego.py`, `static/js/lego_detail_admin.js`, `restore_db_from_sheets.py`, `manager.py`, `fetcher.py`, `docs/stories/_inbox/US-123_pool_images_backup_tab.md` |
| US-122 | Trang thông báo bảo trì khi bật maintenance_mode | accepted | S | 2026-07-09 | `api/index.js`, `tests/test_maintenance.py`, `docs/stories/_inbox/US-122_maintenance_mode_screen.md` |
| US-121 | Quản lý và Đồng bộ Feature Flags trên Google Sheets | done | M | 2026-07-09 | `settings.json`, `scratch/sync_flags.py`, `.agents/AGENTS.md`, `tests/test_feature_flags.py`, `docs/stories/_inbox/US-121_feature_flag_management_sheets.md` |
| US-120A | Quản lý & Sắp xếp Hình ảnh Công khai dạng JSON | accepted | M | 2026-07-07 | `pool_backend_v3.gs`, `pool_lego.py`, `manager.py`, `static/js/lego_detail_client.js`, `static/js/lego_detail_admin.js`, `docs/stories/_inbox/US-120A_public_image_curation_json_sync.md` |
| US-120 | Quản lý Hình ảnh Đa Nguồn và Đồng bộ Dữ liệu Lâu dài | draft | L | 2026-07-07 | `pool_backend_v3.gs`, `pool_lego.py`, `manager.py`, `static/js/lego_detail_client.js`, `static/js/lego_detail_admin.js`, `docs/stories/_inbox/US-120_image_multi_source_and_long_term_sync.md` |
| US-119 | Quản lý và Biên tập Đường trước nhà & Độ rộng hẻm | accepted | S | 2026-07-01 | `pool_backend_v3.gs`, `manager.py`, `static/js/lego_core.js`, `static/js/lego_helpers.js`, `static/js/lego_detail_admin.js`, `docs/stories/_inbox/US-119_street_type_and_alley_width_curation.md` |
| US-118 | Tùy biến Diện tích Sổ & Diện tích Thực tế trên Sheet Source và Vercel Detail | accepted | S | 2026-07-01 | `pool_backend_v3.gs`, `pool_lego.py`, `manager.py`, `static/js/lego_detail_admin.js`, `static/js/lego_core.js`, `static/js/lego_detail_client.js`, `static/js/lego_helpers.js`, `curator.html`, `canvas.html`, `docs/stories/_inbox/US-118_custom_area_curation.md` |
| US-117 | Tự động hóa Sao lưu Định kỳ CSDL SQLite cục bộ | accepted | S | 2026-06-30 | `manager.py`, `docs/stories/_inbox/US-117_periodic_database_backup.md` |
| US-116 | Reset CSDL và Khôi phục/Vá Dữ liệu biên tập theo Địa chỉ | accepted | M | 2026-06-30 | `scratch/backup_and_map_curation.py`, `scratch/wipe_local_and_sheets.py`, `scratch/merge_curated_data.py`, `pool_lego.py` |
| US-115 | Khắc phục lỗi cơ sở dữ liệu SQLite bị hỏng (malformed) khi khởi chạy ứng dụng | done | S | 2026-06-29 | `docs/stories/_inbox/US-115_fix_malformed_sqlite_database.md`, `pool_lego.py`, `static/js/thienkhoi_list_scraper.user.js` |
| US-114 | Khắc phục lỗi cú pháp khởi chạy CHAY_APP.bat và lỗi công thức #ERROR trên Google Sheets | accepted | S | 2026-06-29 | `docs/stories/_inbox/US-114_fix_startup_syntax_and_formula_errors.md`, `manager.py`, `pool_lego.py` |
| US-113 | Sửa lỗi chớp chớp đen màn hình khi phóng to và kéo hình ảnh trên iPhone | accepted | S    | 2026-06-29 | `docs/stories/_inbox/US-113_fix_iphone_image_zoom_black_screen.md`, `static/js/lego_detail_client.js`, `static/css/global.css` |
| US-112 | Đảm bảo thực hiện prompt mới khi bấm nút "Tự động điền" trong biên tập chi tiết | accepted | S | 2026-06-29 | `docs/stories/_inbox/US-112_ensure_new_prompt_autofill.md`, `settings.json`, `api/index.js`, `manager.py` |
| US-111 | Sửa lỗi khóa panel Biên Tập sau khi vừa lên sóng và tự động tải lại trang | accepted | S | 2026-06-29 | `static/js/lego_detail_admin.js` | |
| US-110 | Quản lý và Biên tập Hướng nhà (Direction Curation & Management)        | accepted | M    | 2026-06-28 | `fetcher.py`, `manager.py`, `pool_lego.py`, `restore_db_from_sheets.py`, `static/js/lego_detail_client.js`, `static/js/lego_detail_admin.js`, `static/js/lego_filters.js` |
| US-109 | Lấy tiêu đề thô cào về lưu vào cột Nội dung chính trên Pool | accepted | M | 2026-06-27 | `fetcher.py`, `index.html`, `manager.py`, `pool_lego.py`, `static/js/thienkhoi_list_scraper.user.js` |
| US-108 | Sửa lỗi save Curation: Cannot read properties of undefined (reading 'img_mat_tien') | accepted | S | 2026-06-26 | `static/js/lego_detail_admin.js` |
| US-107 | Đồng bộ Realtime và Hiển thị Toàn bộ Căn nhà từ Pool trên Canvas | accepted | M | 2026-06-25 | `static/js/lego_core.js`, `canvas.html` |
| US-106 | Giao diện Canvas trực quan xem chi tiết căn nhà (Pool & Source)          | accepted | M | 2026-06-22 | `canvas.html`, `manager.py`, `api/index.js`, `curator.html`       |
| US-105 | Hiện nút "Tự động điền" cho cả các căn đã lên sóng & hỏi xác nhận thay thế thông tin AI | accepted | S | 2026-06-22 | `static/js/lego_detail_admin.js`, `static/js/lego_helpers.js`, `curator.html` |
| US-104 | Sửa lỗi không show carousel hình sổ trên detail admin view vercel | accepted | S | 2026-06-22 | `static/js/lego_detail_admin.js`, `static/js/lego_detail_client.js` |
| US-103 | Userscript Cào Căn Nhà Từ Trang Danh Sách Thiên Khôi | accepted | M | 2026-06-22 | `static/js/thienkhoi_list_scraper.user.js`, `curator.html`, `curator_html_data.py` |
| US-102 | Lọc các căn chưa có raw_json_full trên Curator Dashboard | done | S | 2026-06-21 | `manager.py`, `curator.html`, `curator_html_data.py` |
| US-101 | Tối ưu hóa di cư ảnh khi cào lại và bảo toàn hình ảnh tự tải lên | backlog | M | 2026-06-21 | `manager.py`, `pool_lego.py` |
| US-100 | Thiết lập cơ chế lưu trữ JSON động hai tầng và bộ lọc tìm kiếm tùy biến không cấu trúc (Unstructured JSON Filtering Framework) | accepted | M | 2026-06-20 | `fetcher.py`, `pool_lego.py`, `static/js/lego_filters.js`, `docs/stories/_inbox/US-100_dynamic_json_filtering.md` |
| US-097 | Sửa lỗi không bấm tạo được link Công Khai Nhanh để share cho khách hàng | accepted | S    | 2026-06-16 | `static/js/lego_helpers.js`, `docs/stories/_inbox/US-097_fix_quick_share_link_error.md` |
| US-095 | Khắc phục lỗi name 'listings_table' is not defined khi tự động hóa Curation & Xuất bản ở chế độ Pool1 | accepted | S | 2026-06-16 | `pool_lego.py`, `docs/stories/_inbox/US-095_fix_listings_table_undefined.md` |
| US-094 | Tái cấu trúc trang chủ index.html theo Kiến trúc Lego Frontend (Master Epic) | accepted | XL | 2026-06-15 | `docs/stories/_inbox/US-094_master_tai_cau_truc_lego_frontend.md` |
| US-094A1 | Tách biệt CSS ngoài ra global.css | accepted | S | 2026-06-15 | `static/css/global.css`, `index.html` |
| US-094A2 | Xây dựng Lego Core State Store & Tải dữ liệu | accepted | M | 2026-06-15 | `static/js/lego_core.js`, `index.html` |
| US-094A3 | Phân tách Engine Render danh sách Card BĐS | accepted | M | 2026-06-15 | `static/js/lego_render_client.js`, `static/js/lego_render_admin.js`, `index.html` |
| US-094C | Cô lập Module Chi tiết & Carousel thực tế của Khách hàng | accepted | S | 2026-06-15 | `static/js/lego_detail_client.js`, `index.html` |
| US-094B | Cô lập Module Bộ lọc & Tìm kiếm thông minh | accepted | M | 2026-06-15 | `static/js/lego_filters.js`, `index.html` |
| US-094D | Cô lập Module Bộ sưu tập & Lead Capture | accepted | S | 2026-06-15 | `static/js/lego_collections.js`, `static/js/lego_lead_capture.js`, `index.html` |
| US-094F | Cô lập Module Chi tiết, Preview & Curation dành riêng cho Admin | accepted | L    | 2026-06-15 | `static/js/lego_detail_admin.js`, `index.html` |
| US-094E | Tích hợp toàn diện, tối ưu hiệu năng và dọn dẹp index.html | accepted | M | 2026-06-16 | `docs/stories/_inbox/US-094E_lego_frontend_integration.md`, `index.html`, `static/js/lego_mock.js`, `static/js/lego_helpers.js` |
| US-093 | Kiểm tra tính khả dụng và lập báo cáo hình ảnh tự tải lên (Không phải hình từ TK) | accepted | S | 2026-06-14 | `scratch/audit_manual_images.py`, `docs/stories/_inbox/US-093_audit_manual_upload_images.md` |
| US-092 | Sửa lỗi Internal Server Error: Missing index.html khi truy cập trang chủ | accepted | S | 2026-06-13 | `vercel.json`, `api/index.js`, `docs/stories/_inbox/US-092_fix_homepage_missing_index_error.md` |
| US-091 | Khắc phục lỗi giảm chất lượng hình ảnh quá mức khi di cư sang R2 | backlog | M | 2026-06-13 | `manager.py`, `restore_r2_quality.py`, `docs/stories/_inbox/US-091_fix_r2_image_quality_degradation.md` |
| US-090 | Di cư toàn bộ kho hình ảnh sang Cloudflare R2 & Khắc phục giới hạn hạn mức Cloudinary | accepted | L | 2026-06-13 | `settings.json`, `migrate_to_r2.py`, `sync_pool_v1_sheet.py`, `list_broken_listings.py`, `docs/stories/_inbox/US-090_resolve_cloudinary_credit_limit.md` |
| US-089D | Luồng Tự động Mở rộng Schema & Đăng tải Hình ảnh Thủ công | done  | M    | 2026-06-11 | `settings.json`, `pool_lego.py`, `manager.py`, `fetcher.py`, `docs/stories/_inbox/US-089D_pool2_dynamic_schema.md` |
| US-089C | Triển khai Cơ chế Đồng bộ Hai Chiều Liên Database | done  | M    | 2026-06-11 | `pool_lego.py`, `manager.py`, `docs/stories/_inbox/US-089C_pool2_cross_pool_sync.md` |
| US-089B | Tích hợp Google Sheets Đa Quyền Hạn & Luồng Xuất bản Public Whitelist | accepted  | M    | 2026-06-11 | `settings.json`, `pool_lego.py`, `manager.py`, `docs/stories/_inbox/US-089B_pool2_cloud_publishing.md` |
| US-089A | Thiết lập CSDL Quan hệ Pool2 & Tích hợp Luồng Cào thô cục bộ | accepted  | M    | 2026-06-11 | `settings.json`, `pool_lego.py`, `fetcher.py`, `docs/stories/_inbox/US-089A_pool2_local_core.md` |
| US-089 | Thiết kế hệ thống Pool2 - Phân hệ dữ liệu mới theo kiến trúc Lego | superseded | XL   | 2026-06-11 | `docs/features/proptech_crawler_specification_v2.md`, `docs/stories/_inbox/US-089_pool2_data_system.md` |
| US-088 | Đổi tên file và di cư tính năng cũ (Pool1) sang Lego | accepted | L    | 2026-06-11 | `settings.json`, `fetcher.py`, `manager.py`, `pool_lego.py` |
| US-087 | Fix lỗi không xóa được bộ sưu tập đã tồn tại | accepted | S    | 2026-06-11 | `index.html` |
| US-086 | Fix lỗi tạo bộ sưu tập | accepted | S    | 2026-06-11 | `index.html`                                                      |
| US-085 | Sửa lỗi hiển thị và vỡ bố cục trên điện thoại Android | accepted | S    | 2026-06-10 | `index.html`                                                      |
| US-084 | Biên tập hình ảnh dạng Carousel và tối ưu hóa nút bấm trên Mobile | accepted | M    | 2026-06-09 | `index.html`                                                      |
| US-083 | Bổ sung tính năng xoay ảnh bằng chuyển đổi URL Cloudinary trực tiếp trên Web Admin | accepted | S    | 2026-06-09 | `index.html`, `curator.html`                                      |
| US-082 | Sửa lỗi xuống dòng Nội dung chính trong trang chi tiết Pool | accepted | S    | 2026-06-09 | `index.html`, `crawl_pipeline.py`, `curator_server.py`, `pool_backend_v3.gs` |
| US-081 | Sửa lỗi Carousel Mobile — Zoom tự nhảy ảnh & Chuyển ảnh thiếu animation | accepted | S    | 2026-06-08 | `index.html` |
| US-080 | Nâng cấp UX Mobile — Tải gộp 1 lần & Lưu ảnh vào Gallery điện thoại | accepted | M    | 2026-06-08 | `index.html` |
| US-079 | Tải toàn bộ hình ảnh căn nhà dạng file ảnh riêng lẻ cho Admin | accepted | S | 2026-06-08 | `index.html` |
| US-078 | Tích hợp nút Tự động điền AI trong Pool và bảo mật số nhà trên Vercel Admin | accepted | M    | 2026-06-08 | `api/index.js`, `index.html`                                      |
| US-077 | Kiểm tra sự đầy đủ, sắp xếp thứ tự ưu tiên Phường và sửa lỗi hiển thị header Source | accepted | S    | 2026-06-08 | `index.html`                                                      |
| US-076 | Nâng cấp bộ lọc thông số chi tiết nâng cao | accepted | M | 2026-06-07 | `index.html` |
| US-075 | Giải pháp duy trì phiên đăng nhập Google tối thiểu 1 ngày | accepted | M | 2026-06-07 | `index.html`, `pool_backend_v3.gs`, `api/index.js` |
| US-074 | Tối ưu hóa bố cục giao diện hiển thị trên thiết bị Laptop và màn hình lớn | accepted | M | 2026-06-07 | `index.html` |
| US-073 | Khắc phục lỗi lệch chỉ số cột ảnh nội thất 16-25 khi lưu Curation | accepted | S | 2026-06-06 | `index.html` |
| US-072 | Khắc phục lỗi xuất bản Curation ghi đè thiếu trường & lệch cột Google Sheets | accepted | S | 2026-06-03 | `curator_server.py` |
| US-071 | Khắc phục lỗi lệch cột lưu tiêu đề public và hiển thị trùng lặp giá tiền ở panel preview | accepted | S | 2026-06-04 | `index.html`                                                      |
| US-070 | Sửa trùng lặp System ID trên Sheets và khôi phục SQLite hợp nhất từ hai sheet | accepted | S | 2026-06-03 | `restore_db_from_sheets.py`, `scratch/fix_duplicate_system_ids.py` |
| US-069 | Menu sinh Mã Khang Ngô và System ID cho các căn gõ tay trên Google Sheets | accepted | S | 2026-06-03 | `pool_backend_v3.gs` |
| US-068 | Tự động sinh ID cho luồng cào từng căn lẻ | accepted | S | 2026-06-04 | `curator_server.py` |
| US-067 | Sinh ID tự động khi cào hàng loạt và luồng đẩy tin không trùng lặp dữ liệu | accepted | S | 2026-06-03 | `crawl_pipeline.py`, `curator_server.py` |
| US-066 | Đồng bộ Google Sheets Pool & Tương thích Curator UI | accepted | S | 2026-06-03 | `curator_server.py` |
| US-065 | Nghiên cứu API & Cào tab Thông tin chi tiết (Chủ nhà) + Hồ sơ pháp lý (Sổ đỏ) | accepted | L | 2026-06-03 | `crawl_pipeline.py`, `curator_server.py` |
| US-064 | Cào Thông tin chung & Giải mã ảnh Swiper trang Chi tiết | accepted | M | 2026-06-03 | `crawl_pipeline.py`, `curator_server.py` |
| US-063 | Cào danh sách nguồn hàng từ trang Web Proptech mới | accepted | M | 2026-06-03 | `crawl_pipeline.py`, `BDS-AGENTS.md` |
| US-062 | Sửa lỗi sắp xếp theo cập nhật mới nhất/cũ nhất tùy theo danh sách đang xem (Fix Sorting by Last Update depending on Active View) | accepted | S | 2026-06-03 | `index.html`                                                      |
| US-061 | Khắc phục triệt để lỗi hết hạn phiên đăng nhập Google và tự động làm mới token ngầm (Google OAuth Session Timeout Resolution with Auto Silent Refresh) | accepted | M    | 2026-06-03 | `index.html`                                                      |
| US-060 | Bỏ chọn tất cả hình ảnh trong biên tập hình Admin cho căn đã lên sóng và mặc định bỏ chọn cho căn chưa lên sóng | accepted | S    | 2026-06-02 | `index.html`                                                      |
| US-059 | Biểu mẫu Đăng ký Thông tin cho Link Công khai & Phản hồi Khách hàng qua Zalo | accepted | M    | 2026-06-02 | `index.html`                                                      |
| US-058 | Quét, xoay ảnh thẳng đứng vật lý và tự động dọn dẹp bộ nhớ ảnh lỗi cũ trên Cloudinary cho rổ hàng đã di cư | accepted | M    | 2026-06-01 | `fix_tilted_images.py`                                            |
| US-057 | Thanh tìm kiếm thông minh kết hợp nhiều điều kiện và phân tích địa chỉ (Multi-Condition Smart Search Engine with Address & Price Parser) | accepted | M    | 2026-05-31 | `index.html`                                                      |
| US-056 | Cập nhật danh sách Phường chuẩn từ SQL vào bộ lọc tìm kiếm trên giao diện Web Vercel Admin cho các Quận trọng điểm | accepted | S    | 2026-05-31 | `index.html`                                                      |
| US-055 | Khắc phục triệt để lỗi ảnh Sổ đỏ hiện làm ảnh đại diện trên danh sách Admin | accepted | S    | 2026-05-30 | `index.html`                                                      |
| US-054 | Di cư ảnh Sổ không nén lên Cloudinary và lưu link về Pool sheet | accepted | M    | 2026-05-30 | `curator_server.py`, `repair_diagrams.py`                         |
| US-053 | Admin tự upload hình ảnh local cho căn nhà và quản lý tags, public | accepted | M    | 2026-05-30 | `curator.html`, `curator_server.py` |
| US-052 | Bản đồ Tương tác Admin hiển thị các BĐS lân cận trong rổ hàng | backlog  | M    | 2026-05-30 | `index.html`, `crawl_pipeline.py`, `curator_server.py`             |
| US-051 | Tích hợp Combobox Tình trạng và Loại bỏ trường Rộng hẻm thừa tại giao diện Biên tập Admin | accepted | S    | 2026-05-30 | `index.html`                                                      |
| US-050 | Hỗ trợ lướt xem ảnh tiếp theo và thanh xem trước ảnh nhỏ khi phóng to hình | accepted | S    | 2026-05-30 | `index.html`                                                      |
| US-049 | Đồng nhất giao diện chi tiết Khách hàng với Admin Preview và bổ sung Sao chép nhanh link gửi khách | accepted | M    | 2026-05-30 | `index.html`                                                      |
| US-048 | Khắc phục lỗi lệch chỉ số cột Pool thô và trùng lặp card rỗng trên giao diện Admin | accepted | S    | 2026-05-30 | `index.html`                                                      |
| US-047 | Nâng cấp độ tin cậy và chống lỗi gọi API Cào lại căn nhà (Curator Recrawl API Safety) | accepted | S    | 2026-05-30 | `curator_server.py`, `curator.html`                               |
| US-046 | Phân loại hình ảnh sổ pháp lý và hình mặt tiền riêng biệt              | accepted | M    | 2026-05-29 | `index.html`                                                      |
| US-045 | Chọn hình mặt tiền trong web admin cho căn chưa lên sóng (Pool Curation Facade Fix) | done     | S    | 2026-05-29 | `index.html`                                                      |
| US-044 | Robustness Upgrades for AI Curation and Frontend Triggering (Khắc phục triệt độ lỗi biên tập AI trống trường và tối ưu luồng gọi) | accepted | S    | 2026-05-29 | `curator_server.py`, `curator.html`                               |
| US-043 | credentials.json Location Fallback Resolution for Google Sheet Publishing (Tự động tìm kiếm credentials.json tại nhiều vị trí thư mục) | done     | S    | 2026-05-29 | `curator_server.py`                                               |
| US-042 | Bypass Diagram Image Compression in Curator Pipeline (Bỏ qua nén ảnh Sơ đồ thửa đất) | accepted | S    | 2026-05-29 | `curator_server.py`                                               |
| US-041 | Visual Polish, Device Compatibility, & SPA History State Management (Tinh chỉnh giao diện, Tương thích di động & Điều hướng Back-button) | accepted | S    | 2026-05-29 | `index.html`                                                      |
| US-040 | Tự động hóa Luồng Curation & Dán nhãn Sơ đồ khi Cào tin đẩy thẳng về Pool | done     | L    | 2026-05-28 | `curator_server.py`                                               |
| US-039 | Admin Curation Dashboard trên Web Vercel (View Admin riêng kết nối song song Pool & Source) | accepted | L    | 2026-05-28 | `index.html`, `api/index.js`                                      |
| US-038 | Đồng bộ Cơ sở Dữ liệu Dự án & Bộ não AI (Memory) đa thiết bị           | accepted | S    | 2026-05-27 | `.gemini/antigravity-ide`, `D:\LHTBrain`                          |
| US-037 | Tích hợp AI Tools, Cấu hình System Prompt & Tự động tạo Mã Khang Ngô   | accepted | M    | 2026-05-27 | `curator.html`, `curator_server.py`, `curator_html_data.py`       |
| US-036 | Hệ thống Cấu hình Tốc độ Cào tin & Speed Presets linh hoạt              | accepted | S    | 2026-05-27 | `curator.html`, `curator_server.py`, `crawl_pipeline.py`, `curator_html_data.py` |
| US-035 | Hệ thống cào BĐS & Mini-App biên tập rổ hàng 2000 căn         | accepted | L    | 2026-05-25 | `crawl_pipeline.py`, `curator_server.py`, `curator.html`          |
| US-034 | Tối ưu hóa & Rút ngắn Tham số c khi tạo link gửi khách hàng            | accepted | S    | 2026-05-25 | `index.html`, `api/index.js`                                      |
| US-033 | Tùy chỉnh Tiêu đề trang khi tạo link chia sẻ gửi khách hàng            | accepted | S    | 2026-05-25 | `index.html`, `api/index.js`                                      |
| US-032 | Tính năng Bộ sưu tập BĐS cá nhân hóa cho Admin                         | accepted | S    | 2026-05-25 | `index.html`                                                      |
| US-031 | Tối ưu không gian hiển thị trang chủ và mở rộng hình đại diện trên Mobile | accepted | S    | 2026-05-25 | `index.html`                                                      |
| US-030 | Chỉ đồng bộ Tiêu đề hàng loạt từ Pool sang Source                      | accepted | S    | 2026-05-24 | `pool_backend_v3.gs`                                              |
| US-029 | Sắp xếp theo Sản phẩm mới thêm mặc định trên danh sách                 | accepted | S    | 2026-05-24 | `index.html`                                                      |
| US-028 | Đồng bộ cơ chế nén Bitmask gửi khách nhiều căn                         | accepted | S    | 2026-05-25 | `index.html`                                                      |
| US-027 | Di chuyển Hosting sang Vercel & Dynamic Meta Tags khi share 1 căn      | accepted | S    | 2026-05-24 | `index.html`, `vercel.json`, `package.json`, `api/index.js`       |
| US-026 | Giới hạn độ dài Tiêu đề BDS AI & Auto-Trimmer                          | accepted | S    | 2026-05-24 | `pool_backend_v3.gs`                                              |
| US-025 | Cấu trúc Tiêu đề BDS AI mới cho batdongsan.com.vn                      | accepted | S    | 2026-05-24 | `pool_backend_v3.gs`, `auto_post_server.py`                       |
| US-024 | Bảo mật hình ảnh mặt tiền Admin bằng Google OAuth2 & Silent Auto-Login | accepted | XL   | 2026-05-24 | `index.html`, `api/index.js`                                      |
| US-023 | Tự động xóa ô tìm kiếm và tích hợp nút xóa nhanh ✕                     | accepted | S    | 2026-05-24 | `index.html`                                                      |
| US-022 | Khang Ngô AI Apps Script (Lưu trữ và tài liệu hóa Custom Script)       | accepted | S    | 2026-05-22 | `source_sheet_ai.gs`                                              |
| US-021 | Tích hợp Tiêu đề BDS ngắn gọn dưới 85 ký tự và tối ưu AI               | accepted | M    | 2026-05-22 | `pool_backend_v3.gs`, `auto_post_server.py`, `source_sheet_ai.gs` |
| US-020 | Tích hợp nút Đăng tin batdongsan.com.vn vào sheet Source               | done     | M    | 2026-05-22 | `auto_post_server.py`, `pool_backend_v3.gs`                       |

| US-019 | [Legacy] Cơ chế tự động đăng tin batdongsan.com.vn cũ qua Web Admin / Hẹn giờ | superseded | unknown | 2026-05-22 | `auto_post_server.py` |
| US-018 | Tách biệt Đồng bộ Lần đầu & Đồng bộ Một phần (Smart Merge) | done | M | 2026-05-21 | `pool_backend_v3.gs` |
| US-017 | Tự động sinh và chuẩn hóa Mã Khang Ngô (ID) | done | S | 2026-05-21 | `pool_backend_v3.gs` |
| US-016 | Fix hiển thị tên quận TB/PN/BT/GV — card và modal | done | S | 2026-05-21 | `index.html` |
| US-015 | Fix ảnh đen trên mobile (root cause sai — TK CDN policy) | superseded | S | 2026-05-21 | `index.html` (reverted) |
| US-014 | Tạo Pool Sheet Schema & validate column mapping | done | M | 2026-05-20 | `pool_backend_v3.gs`, `docs/pool_sheet_schema.md` |
| US-013 | Bỏ Nội dung chính, thêm DT Trên sổ & Hướng | done | S | 2026-05-20 | `pool_backend_v3.gs` |
| US-012 | Đưa thêm Phân loại & tối ưu label userPrompt cho USP | done | S | 2026-05-20 | `pool_backend_v3.gs` |
| US-011 | Mô tả tiện ích theo đặc trưng khu vực & giao thông | done | S | 2026-05-20 | `pool_backend_v3.gs` |
| US-010 | Tiện ích trong bán kính 1km theo địa chỉ | superseded | S | 2026-05-20 | `pool_backend_v3.gs` |
| US-009 | Prompt AI liệt kê tiện ích cụ thể | superseded | S | 2026-05-20 | `pool_backend_v3.gs` |
| US-008 | Siết chặt định dạng Mô tả AI | done | S | 2026-05-20 | `pool_backend_v3.gs` |
| US-007 | Gộp chung toàn bộ logic sinh nội dung AI | done | M | 2026-05-20 | `pool_backend_v3.gs` |
| US-006 | Loại bỏ tiền tố HXH khỏi Tiêu đề | done | S | 2026-05-20 | `pool_backend_v3.gs` |
| US-005 | Cập nhật Prompt sinh Tiêu đề & Mô tả AI | done | S | 2026-05-20 | `pool_backend_v3.gs` |
| US-004 | [Legacy] Prompt cũ sinh Tiêu đề & Mô tả AI | superseded | unknown | 2026-05-20 | `pool_backend_v3.gs` |
| US-003 | Theo dõi thời gian đồng bộ dữ liệu Last Sync | done | S | 2026-05-20 | `pool_backend_v3.gs` |
| US-002 | Thuật toán Mã Khang Ngô cắt số phụ căn nhà | done | S | 2026-05-20 | `pool_backend_v3.gs` |
| US-001 | Ghi nhận mốc thời gian Last Crawl | done | S | 2026-05-20 | `pool_backend_v3.gs` |

## By Keyword

### Crawl / Sync Tracking
- [[US-152|US-152]]: Đồng bộ ảnh crawl trực tiếp từ nguồn Thiên Khôi (accepted)
- [[US-142_recovery_from_raw_json|US-142]]: Khôi phục dữ liệu listings từ raw_json_full trong SQLite Cục bộ (accepted)
- [[US-141_r2_image_migration_subfolders_and_recovery|US-141]]: Tổ chức thư mục R2 theo mã căn & Cơ chế khôi phục liên kết hình ảnh (accepted)
- [[US-132|US-132]]: Phân giải Đánh số Thứ tự Ảnh và Hiển thị Đồng nhất trên Trang Chi tiết Khách hàng (accepted)
- [[US-131_fix_recrawl_image_mismatch|US-131]]: Khắc phục lệch ảnh khi cào lại và phân giải Images_Admin_JSON trên Web Vercel Admin (accepted)
- [[US-120A_public_image_curation_json_sync|US-120A]]: Quản lý & Sắp xếp Hình ảnh Công khai dạng JSON (accepted)
- [[US-120_image_multi_source_and_long_term_sync|US-120]]: Quản lý Hình ảnh Đa Nguồn và Đồng bộ Dữ liệu Lâu dài (draft)
- [[US-119_street_type_and_alley_width_curation|US-119]]: Quản lý và Biên tập Đường trước nhà & Độ rộng hẻm trên Vercel Detail & local Python Backend (accepted)
- [[US-118_custom_area_curation|US-118]]: Tùy biến Diện tích Sổ & Diện tích Thực tế trên Sheet Source và Vercel Detail (accepted)
- [[US-115_fix_malformed_sqlite_database|US-115]]: Khắc phục lỗi cơ sở dữ liệu SQLite bị hỏng (malformed) khi khởi chạy ứng dụng (in-progress)
- [[US-114_fix_startup_syntax_and_formula_errors|US-114]]: Khắc phục lỗi cú pháp khởi chạy CHAY_APP.bat và lỗi công thức #ERROR trên Google Sheets (accepted)
- [[US-111_fix_edit_panel_lockup_after_publish|US-111]]: Sửa lỗi khóa panel Biên Tập sau khi vừa lên sóng và tự động tải lại trang (accepted)
- [[US-110_direction_curation_management|US-110]]: Quản lý và Biên tập Hướng nhà (accepted)
- [[US-109_mapping_crawled_title_to_noidungchinh|US-109]]: Lấy tiêu đề thô cào về lưu vào cột Nội dung chính trên Pool (accepted)
- [[US-107_sync_all_pool_listings_canvas|US-107]]: Đồng bộ Realtime và Hiển thị Toàn bộ Căn nhà từ Pool trên Canvas (accepted)
- [[US-106_canvas_detail_view|US-106]]: Giao diện Canvas trực quan xem chi tiết căn nhà (Pool & Source) (accepted)
- [[US-105_autofill_button_overwrite_confirmation|US-105]]: Hiện nút "Tự động điền" cho cả các căn đã lên sóng & hỏi xác nhận thay thế thông tin AI (accepted)
- [[US-103_crawl_listings_userscript|US-103]]: Userscript Cào Căn Nhà Từ Trang Danh Sách Thiên Khôi (accepted)
- [[US-102_missing_json_curator_tab|US-102]]: Lọc các căn chưa có raw_json_full trên Curator Dashboard (done)
- [[US-101_optimize_recrawl_image_handling|US-101]]: Tối ưu hóa di cư ảnh khi cào lại và bảo toàn hình ảnh tự tải lên (backlog)
- [[US-095_fix_listings_table_undefined|US-095]]: Khắc phục lỗi name 'listings_table' is not defined khi tự động hóa Curation & Xuất bản ở chế độ Pool1 (accepted)
- [[US-093_audit_manual_upload_images|US-093]]: Kiểm tra tính khả dụng và lập báo cáo hình ảnh tự tải lên (Không phải hình từ TK) (accepted)
- [[US-091_fix_r2_image_quality_degradation|US-091]]: Khắc phục lỗi giảm chất lượng hình ảnh quá mức khi di cư sang R2 (backlog)
- [[US-090_resolve_cloudinary_credit_limit|US-090]]: Di cư toàn bộ kho hình ảnh sang Cloudflare R2 & Khắc phục giới hạn hạn mức Cloudinary (accepted)
- [[US-089_pool2_data_system|US-089]]: [Decomposed] Thiết kế hệ thống Pool2 - Phân hệ dữ liệu mới theo kiến trúc Lego (superseded)
- [[US-089A_pool2_local_core|US-089A]]: Thiết lập CSDL Quan hệ Pool2 & Tích hợp Luồng Cào thô cục bộ (accepted)
- [[US-089B_pool2_cloud_publishing|US-089B]]: Tích hợp Google Sheets Đa Quyền Hạn & Luồng Xuất bản Public Whitelist (accepted)
- [[US-089C_pool2_cross_pool_sync|US-089C]]: Triển khai Cơ chế Đồng bộ Hai Chiều Liên Database (done)
- [[US-089D_pool2_dynamic_schema|US-089D]]: Luồng Tự động Mở rộng Schema & Đăng tải Hình ảnh Thủ công (done)
- [[US-088_pool1_lego_migration|US-088]]: Đổi tên file và di cư tính năng cũ (Pool1) sang Lego (accepted)
- [[US-078_admin_curation_auto_fill_ai|US-078]]: Tích hợp nút Tự động điền AI trong Pool và bảo mật số nhà trên Vercel Admin (accepted)
- [[US-073_fix_local_upload_indexing|US-073]]: Khắc phục lỗi lệch chỉ số cột ảnh nội thất 16-25 khi lưu Curation (accepted)
- [[US-071_fix_public_title_saving_and_display|US-071]]: Khắc phục lỗi lệch cột lưu tiêu đề public và hiển thị trùng lặp giá tiền ở panel preview (accepted)
- [[US-072_fix_curation_overwrite|US-072]]: Khắc phục lỗi xuất bản Curation ghi đè thiếu trường & lệch cột Google Sheets (accepted)
- [[US-070_fix_duplicates_and_restore_sqlite|US-070]]: Sửa trùng lặp System ID trên Sheets và khôi phục SQLite hợp nhất từ hai sheet (accepted)
- [[US-069_manual_crawl_sheets_menu|US-069]]: Menu sinh Mã Khang Ngô và System ID cho các căn gõ tay trên Google Sheets (accepted)
- [[US-068_single_crawl_id_generation|US-068]]: Tự động sinh ID cho luồng cào từng căn lẻ (accepted)
- [[US-067_bulk_crawl_id_generation|US-067]]: Sinh ID tự động khi cào hàng loạt và luồng đẩy tin không trùng lặp dữ liệu (accepted)
- [[US-066_sheets_sync_curator_compat|US-066]]: Đồng bộ Google Sheets Pool & Tương thích Curator UI (accepted)
- [[US-065_crawl_detail_legal_sodo|US-065]]: Nghiên cứu API & Cào tab Thông tin chi tiết (Chủ nhà) + Hồ sơ pháp lý (Sổ đỏ) (accepted)
- [[US-064_crawl_detail_swiper_images|US-064]]: Cào Thông tin chung & Giải mã ảnh Swiper trang Chi tiết (accepted)
- [[US-063_crawl_list_proptech_api|US-063]]: Cào danh sách nguồn hàng từ trang Web Proptech mới (accepted)
- [[US-058_fix_tilted_images|US-058]]: Quét, xoay ảnh thẳng đứng vật lý và tự động dọn dẹp bộ nhớ ảnh lỗi cũ trên Cloudinary cho rổ hàng đã di cư (accepted)
- [[US-055_fix_admin_avatar_sodo|US-055]]: Khắc phục triệt để lỗi ảnh Sổ đỏ hiện làm ảnh đại diện trên danh sách Admin (accepted)
- [[US-054_migrate_uncompressed_sodo_cloudinary|US-054]]: Di cư ảnh Sổ không nén lên Cloudinary và lưu link về Pool sheet (accepted)
- [[US-053_admin_upload_images_local|US-053]]: Admin tự upload hình ảnh local cho căn nhà và quản lý tags, public (accepted)
- [[US-047_recrawl_api_robustness|US-047]]: Nâng cấp độ tin cậy và chống lỗi gọi API Cào lại căn nhà (Curator Recrawl API Safety) (accepted)
- [[US-044_robust_ai_curation|US-044]]: Robustness Upgrades for AI Curation and Frontend Triggering (accepted)
- [[US-043_credentials_fallback|US-043]]: credentials.json Location Fallback Resolution for Google Sheet Publishing (done)
- [[US-042_bypass_diagram_image_compression|US-042]]: Bypass Diagram Image Compression in Curator Pipeline (Bỏ qua nén ảnh Sơ đồ thửa đất) (accepted)
- [[US-040_auto_curation_pipeline_diagram_labeling|US-040]]: Tự động hóa Luồng Curation & Dán nhãn Sơ đồ khi Cào tin đẩy thẳng về Pool (done)
- [[US-038_multi_device_sync_brain|US-038]]: Đồng bộ Cơ sở Dữ liệu Dự án & Bộ não AI (Memory) đa thiết bị qua Cloud Junction (accepted)
- [[US-036_dynamic_speed_presets|US-036]]: Hệ thống Cấu hình Tốc độ Cào tin & Speed Presets linh hoạt (accepted)
- [[US-035_crawl_bulk_to_google_drive|US-035]]: Hệ thống cào BĐS & Mini-App biên tập rổ hàng 2000 căn (accepted)
- [[US-030_sync_only_title_bulk|US-030]]: Chỉ đồng bộ Tiêu đề hàng loạt từ Pool sang Source (accepted)
- [[US-022_khangngo_ai_custom_script|US-022]]: Khang Ngô AI Apps Script (Lưu trữ và tài liệu hóa Custom Script) (accepted)
- [[US-020_autopost_bds_com_vn_inline_sheet|US-020]]: Tích hợp nút Đăng tin batdongsan.com.vn vào sheet Source (done)
- [[SUPERSEDED_US-019_stub_legacy_autopost_vercel|US-019]]: [Legacy] Cơ chế tự động đăng tin batdongsan.com.vn cũ qua Web Admin / Hẹn giờ (superseded)
- [[US-018_incremental_sync_protected_columns|US-018]]: Tách biệt Đồng bộ Lần đầu & Đồng bộ Một phần (Smart Merge) (done)
- [[US-001_last_crawl_tracking|US-001]]: Ghi nhận mốc thời gian Last Crawl (done)
- [[US-003_last_sync_tracking|US-003]]: Theo dõi thời gian đồng bộ dữ liệu Last Sync (done)

### ID Generation
- [[US-040_auto_curation_pipeline_diagram_labeling|US-040]]: Tự động hóa Luồng Curation & Dán nhãn Sơ đồ khi Cào tin đẩy thẳng về Pool (done)
- [[US-037_ai_tools_curator_integration|US-037]]: Tích hợp AI Tools, Cấu hình System Prompt & Tự động tạo Mã Khang Ngô (accepted)
- [[US-017_auto_generate_khangngo_id|US-017]]: Tự động sinh và chuẩn hóa Mã Khang Ngô (ID) (done)
- [[US-002_adjacent_houses_khangngo_id|US-002]]: Thuật toán Mã Khang Ngô cắt số phụ căn nhà (done)

### AI Content Generation
- [[US-105_autofill_button_overwrite_confirmation|US-105]]: Hiện nút "Tự động điền" cho cả các căn đã lên sóng & hỏi xác nhận thay thế thông tin AI (accepted)
- [[US-078_admin_curation_auto_fill_ai|US-078]]: Tích hợp nút Tự động điền AI trong Pool và bảo mật số nhà trên Vercel Admin (accepted)
- [[US-044_robust_ai_curation|US-044]]: Robustness Upgrades for AI Curation and Frontend Triggering (accepted)
- [[US-040_auto_curation_pipeline_diagram_labeling|US-040]]: Tự động hóa Luồng Curation & Dán nhãn Sơ đồ khi Cào tin đẩy thẳng về Pool (done)
- [[US-037_ai_tools_curator_integration|US-037]]: Tích hợp AI Tools, Cấu hình System Prompt & Tự động tạo Mã Khang Ngô (accepted)
- [[US-026_ai_title_length_constraints|US-026]]: Giới hạn độ dài Tiêu đề BDS AI & Auto-Trimmer (accepted)
- [[US-025_new_ai_title_structure|US-025]]: Cấu trúc Tiêu đề BDS AI mới cho batdongsan.com.vn (accepted)
- [[US-021_tieu_de_bds_85_chars|US-021]]: Tích hợp Tiêu đề BDS ngắn gọn dưới 85 ký tự và tối ưu AI (accepted)
- [[SUPERSEDED_US-004_stub_legacy_ai_prompt|US-004]]: [Legacy] Prompt cũ sinh Tiêu đề & Mô tả AI (superseded)
- [[US-005_ai_title_prompt_update|US-005]]: Prompt AI đóng vai môi giới, bỏ cấu trúc cứng (done)
- [[US-006_remove_hxh_prefix|US-006]]: Bỏ tiền tố HXH tự động trong tiêu đề (done)
- [[US-007_refactor_ai_generation|US-007]]: Gộp các hàm AI thành kiến trúc DRY (done)
- [[US-008_strict_ai_formatting|US-008]]: Siết định dạng Mô tả AI — cấm emoji, bắt buộc 4 đoạn (done)
- [[SUPERSEDED_US-009_specific_amenities_prompt|US-009]]: Prompt AI liệt kê tiện ích cụ thể (superseded)
- [[SUPERSEDED_US-010_amenities_1km_radius|US-010]]: Tiện ích trong bán kính 1km theo địa chỉ (superseded)
- [[US-011_neighborhood_description|US-011]]: Mô tả tiện ích theo đặc trưng khu vực & giao thông (done)
- [[US-012_usp_columns_prompt|US-012]]: Đưa thêm Phân loại & tối ưu label userPrompt cho USP (done)
- [[US-013_replace_noidungchinh|US-013]]: Bỏ Nội dung chính, thêm DT Trên sổ & Hướng (done)

### Schema & Định nghĩa
- [[US-120_image_multi_source_and_long_term_sync|US-120]]: Quản lý Hình ảnh Đa Nguồn và Đồng bộ Dữ liệu Lâu dài (draft)
- [[US-118_custom_area_curation|US-118]]: Tùy biến Diện tích Sổ & Diện tích Thực tế trên Sheet Source và Vercel Detail (accepted)
- [[US-110_direction_curation_management|US-110]]: Quản lý và Biên tập Hướng nhà (accepted)
- [[US-089_pool2_data_system|US-089]]: [Decomposed] Thiết kế hệ thống Pool2 - Phân hệ dữ liệu mới theo kiến trúc Lego (superseded)
- [[US-089A_pool2_local_core|US-089A]]: Thiết lập CSDL Quan hệ Pool2 & Tích hợp Luồng Cào thô cục bộ (accepted)
- [[US-089B_pool2_cloud_publishing|US-089B]]: Tích hợp Google Sheets Đa Quyền Hạn & Luồng Xuất bản Public Whitelist (accepted)
- [[US-089C_pool2_cross_pool_sync|US-089C]]: Triển khai Cơ chế Đồng bộ Hai Chiều Liên Database (done)
- [[US-089D_pool2_dynamic_schema|US-089D]]: Luồng Tự động Mở rộng Schema & Đăng tải Hình ảnh Thủ công (done)
- [[US-088_pool1_lego_migration|US-088]]: Đổi tên file và di cư tính năng cũ (Pool1) sang Lego (accepted)
- [[US-014_pool_sheet_schema|US-014]]: Tạo Pool Sheet Schema & validate column mapping (done)

### UI / Frontend
- [[US-139|US-139]]: Nối tiếp Chuỗi Thay đổi Giá & Làm sạch Định dạng Đơn giá trên Card (accepted)
- [[US-137|US-137]]: Nâng Cấp Bộ Lọc, Sắp Xếp, Đơn Giá và Sắp Xếp Hình Trực Quan (accepted)
- [[US-131_fix_recrawl_image_mismatch|US-131]]: Khắc phục lệch ảnh khi cào lại và phân giải Images_Admin_JSON trên Web Vercel Admin (accepted)
- [[US-126_pwa_installable_app|US-126]]: Nâng Cấp Trang Tải Ảnh Hàng Loạt Thành Ứng Dụng Cài Đặt (PWA) Cô Lập (accepted)
- [[US-124_image_url_viewer_downloader|US-124]]: Trình Xem Và Tải Ảnh Hàng Loạt Từ URL (accepted)
- [[US-120_image_multi_source_and_long_term_sync|US-120]]: Quản lý Hình ảnh Đa Nguồn và Đồng bộ Dữ liệu Lâu dài (draft)
- [[US-118_custom_area_curation|US-118]]: Tùy biến Diện tích Sổ & Diện tích Thực tế trên Sheet Source và Vercel Detail (accepted)
- [[US-113_fix_iphone_image_zoom_black_screen|US-113]]: Sửa lỗi chớp chớp đen màn hình khi phóng to và kéo hình ảnh trên iPhone (accepted)
- [[US-111_fix_edit_panel_lockup_after_publish|US-111]]: Sửa lỗi khóa panel Biên Tập sau khi vừa lên sóng và tự động tải lại trang (accepted)
- [[US-110_direction_curation_management|US-110]]: Quản lý và Biên tập Hướng nhà (accepted)
- [[US-108_fix_curation_shadowing_render|US-108]]: Sửa lỗi save Curation: Cannot read properties of undefined (reading 'img_mat_tien') (accepted)
- [[US-107_sync_all_pool_listings_canvas|US-107]]: Đồng bộ Realtime và Hiển thị Toàn bộ Căn nhà từ Pool trên Canvas (accepted)
- [[US-106_canvas_detail_view|US-106]]: Giao diện Canvas trực quan xem chi tiết căn nhà (Pool & Source) (accepted)
- [[US-105_autofill_button_overwrite_confirmation|US-105]]: Hiện nút "Tự động điền" cho cả các căn đã lên sóng & hỏi xác nhận thay thế thông tin AI (accepted)
- [[US-104_fix_admin_sodo_carousel|US-104]]: Sửa lỗi không show carousel hình sổ trên detail admin view vercel (accepted)
- [[US-097_fix_quick_share_link_error|US-097]]: Sửa lỗi không bấm tạo được link Công Khai Nhanh để share cho khách hàng (accepted)
- [[US-094_master_tai_cau_truc_lego_frontend|US-094]]: Tái cấu trúc trang chủ index.html theo Kiến trúc Lego Frontend (Master Epic) (accepted)
- [[US-094A1_lego_frontend_css|US-094A1]]: Tách biệt CSS ngoài ra global.css (accepted)
- [[US-094A2_lego_frontend_core|US-094A2]]: Xây dựng Lego Core State Store & Tải dữ liệu (accepted)
- [[US-094A3_lego_frontend_render|US-094A3]]: Phân tách Engine Render danh sách Card BĐS (accepted)
- [[US-094C_lego_frontend_preview|US-094C]]: Cô lập Module Chi tiết & Carousel thực tế của Khách hàng (accepted)
- [[US-094B_lego_frontend_filters|US-094B]]: Cô lập Module Bộ lọc & Tìm kiếm thông minh (accepted)
- [[US-094D_lego_frontend_collections|US-094D]]: Cô lập Module Bộ sưu tập & Lead Capture (accepted)
- [[US-094F_lego_frontend_curation|US-094F]]: Cô lập Module Chi tiết, Preview & Curation dành riêng cho Admin (accepted)
- [[US-094E_lego_frontend_integration|US-094E]]: Tích hợp toàn diện, tối ưu hiệu năng và dọn dẹp index.html (accepted)
- [[US-092_fix_homepage_missing_index_error|US-092]]: Sửa lỗi Internal Server Error: Missing index.html khi truy cập trang chủ (accepted)
- [[US-087_fix_xoa_bo_suu_tap|US-087]]: Fix lỗi không xóa được bộ sưu tập đã tồn tại (accepted)
- [[US-086_fix_loi_tao_bo_suu_tap|US-086]]: Fix lỗi tạo bộ sưu tập (accepted)
- [[US-085_fix_android_mobile_display_bug|US-085]]: Sửa lỗi hiển thị và vỡ bố cục trên điện thoại Android (accepted)
- [[US-084_image_editor_carousel|US-084]]: Biên tập hình ảnh dạng Carousel và tối ưu hóa nút bấm trên Mobile (accepted)
- [[US-083_rotate_image_url_admin|US-083]]: Bổ sung tính năng xoay ảnh bằng chuyển đổi URL Cloudinary trực tiếp trên Web Admin (accepted)
- [[US-082_fix_noidungchinh_line_break_pool|US-082]]: Sửa lỗi xuống dòng Nội dung chính trong trang chi tiết Pool (accepted)
- [[US-081_fix_mobile_carousel_zoom_and_transition|US-081]]: Sửa lỗi Carousel Mobile — Zoom tự nhảy ảnh & Chuyển ảnh thiếu animation (accepted)
- [[US-080_mobile_ux_save_all_images_to_gallery|US-080]]: Nâng cấp UX Mobile — Tải gộp 1 lần & Lưu ảnh vào Gallery điện thoại (accepted)
- [[US-079_admin_download_all_images|US-079]]: Tải toàn bộ hình ảnh căn nhà dạng file ảnh riêng lẻ cho Admin (accepted)
- [[US-078_admin_curation_auto_fill_ai|US-078]]: Tích hợp nút Tự động điền AI trong Pool và bảo mật số nhà trên Vercel Admin (accepted)
- [[US-077_ward_priority_and_header_fix|US-077]]: Kiểm tra sự đầy đủ, sắp xếp thứ tự ưu tiên Phường và sửa lỗi hiển thị header Source (accepted)
- [[US-076_nang_cap_bo_loc_chi_tiet|US-076]]: Nâng cấp bộ lọc thông số chi tiết nâng cao (accepted)
- [[US-075_duy_tri_session_google|US-075]]: Giải pháp duy trì phiên đăng nhập Google tối thiểu 1 ngày (accepted)
- [[US-074_laptop_ui_optimization|US-074]]: Tối ưu hóa bố cục giao diện hiển thị trên thiết bị Laptop và màn hình lớn (accepted)
- [[US-073_fix_local_upload_indexing|US-073]]: Khắc phục lỗi lệch chỉ số cột ảnh nội thất 16-25 khi lưu Curation (done)
- [[US-071_fix_public_title_saving_and_display|US-071]]: Khắc phục lỗi lệch cột lưu tiêu đề public và hiển thị trùng lặp giá tiền ở panel preview (accepted)
- [[US-062_sorting_bug_resolution|US-062]]: Sửa lỗi sắp xếp theo cập nhật mới nhất/cũ nhất tùy theo danh sách đang xem (accepted)
- [[US-061_google_auth_timeout_resolution|US-061]]: Khắc phục triệt để lỗi hết hạn phiên đăng nhập Google và tự động làm mới token ngầm (accepted)
- [[US-060_uncheck_all_images_curator|US-060]]: Bỏ chọn tất cả hình ảnh trong biên tập hình Admin cho căn đã lên sóng và mặc định bỏ chọn cho căn chưa lên sóng (accepted)
- [[US-059_lead_capture_public_share|US-059]]: Biểu mẫu Đăng ký Thông tin cho Link Công khai & Phản hồi Khách hàng qua Zalo (accepted)
- [[US-057_enhanced_search_bar_logic|US-057]]: Thanh tìm kiếm thông minh kết hợp nhiều điều kiện và phân tích địa chỉ (accepted)
- [[US-056_update_wards_filter_districts|US-056]]: Cập nhật danh sách Phường chuẩn từ SQL vào bộ lọc tìm kiếm trên giao diện Web Vercel Admin cho các Quận trọng điểm (accepted)
- [[US-053_admin_upload_images_local|US-053]]: Admin tự upload hình ảnh local cho căn nhà và quản lý tags, public (accepted)
- [[US-052_pool_listings_google_map|US-052]]: Bản đồ Tương tác Admin hiển thị các BĐS lân cận trong rổ hàng (backlog)
- [[US-051_curator_editor_status_combobox|US-051]]: Tích hợp Combobox Tình trạng và Loại bỏ trường Rộng hẻm thừa tại giao diện Biên tập Admin (accepted)
- [[US-050_lightbox_swipe_and_thumbnails|US-050]]: Hỗ trợ lướt xem ảnh tiếp theo và thanh xem trước ảnh nhỏ khi phóng to hình (accepted)
- [[US-049_unified_client_detail_view_and_quick_copy|US-049]]: Đồng nhất giao diện chi tiết Khách hàng với Admin Preview và bổ sung Sao chép nhanh link gửi khách (accepted)
- [[US-048_pool_column_shift_empty_card_fix|US-048]]: Khắc phục lỗi lệch chỉ số cột Pool thô và trùng lặp card rỗng trên giao diện Admin (accepted)
- [[US-047_recrawl_api_robustness|US-047]]: Nâng cấp độ tin cậy và chống lỗi gọi API Cào lại căn nhà (Curator Recrawl API Safety) (accepted)
- [[US-046_legal_image_classification|US-046]]: Phân loại hình ảnh sổ pháp lý và hình mặt tiền riêng biệt (accepted)
- [[US-045_facade_selection_pool_fix|US-045]]: Chọn hình mặt tiền trong web admin cho căn chưa lên sóng (done)
- [[US-044_robust_ai_curation|US-044]]: Robustness Upgrades for AI Curation and Frontend Triggering (accepted)
- [[US-041_visual_polish_enhancements_ux_compatibility|US-041]]: Visual Polish, Device Compatibility, & SPA History State Management (Tinh chỉnh giao diện, Tương thích di động & Điều hướng Back-button) (accepted)
- [[US-040_auto_curation_pipeline_diagram_labeling|US-040]]: Tự động hóa Luồng Curation & Dán nhãn Sơ đồ khi Cào tin đẩy thẳng về Pool (done)
- [[US-039_admin_curation_dashboard_vercel|US-039]]: Admin Curation Dashboard trên Web Vercel (View Admin riêng kết nối song song Pool & Source) (accepted)
- [[US-037_ai_tools_curator_integration|US-037]]: Tích hợp AI Tools, Cấu hình System Prompt & Tự động tạo Mã Khang Ngô (accepted)
- [[US-036_dynamic_speed_presets|US-036]]: Hệ thống Cấu hình Tốc độ Cào tin & Speed Presets linh hoạt (accepted)
- [[US-034_shorten_share_parameters|US-034]]: Tối ưu hóa & Rút ngắn Tham số c khi tạo link gửi khách hàng (accepted)
- [[US-033_custom_page_title_share|US-033]]: Tùy chỉnh Tiêu đề trang khi tạo link chia sẻ gửi khách hàng (accepted)
- [[US-032_property_collections|US-032]]: Tính năng Bộ sưu tập BĐS cá nhân hóa cho Admin (accepted)
- [[US-031_optimize_mobile_layout|US-031]]: Tối ưu không gian hiển thị trang chủ và mở rộng hình đại diện trên Mobile (accepted)
- [[US-029_default_newest_sorting|US-029]]: Sắp xếp theo Sản phẩm mới thêm mặc định trên danh sách (accepted)
- [[US-028_multi_share_bitmask|US-028]]: Đồng bộ cơ chế nén Bitmask gửi khách nhiều căn (accepted)
- [[US-027_vercel_deployment|US-027]]: Di chuyển Hosting sang Vercel & Dynamic Meta Tags khi share 1 căn (accepted)
- [[US-024_admin_facade_image_cover|US-024]]: Bảo mật hình ảnh mặt tiền Admin bằng Google OAuth2 & Silent Auto-Login (accepted)
- [[US-023_clear_search_on_reset|US-023]]: Tự động xóa ô tìm kiếm và tích hợp nút xóa nhanh ✕ (accepted)
- [[SUPERSEDED_US-015_fix_mobile_image_black|US-015]]: Fix ảnh đen trên mobile (superseded — TK CDN policy)
- [[US-016_fix_district_label|US-016]]: Fix hiển thị tên quận TB/PN/BT/GV (done)
