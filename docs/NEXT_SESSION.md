# 📌 KẾ HOẠCH BÀN GIAO PHIÊN LÀM VIỆC TIẾP THEO (NEXT SESSION PLAN)

> **Mục đích:** File này lưu trữ trạng thái dừng của phiên làm việc hiện tại và định hướng chi tiết cho phiên làm việc tiếp theo.
> **Cách kích hoạt phiên mới:** Khi bắt đầu chat ở session mới, hãy gõ câu lệnh:
> `"Đọc file d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\docs\NEXT_SESSION.md để tiếp tục công việc."`

---

## 1. Trạng thái hiện tại của dự án (Current State)
*   **US-157 (Nâng cấp Trình Xem & Tải Ảnh: Thêm Tab Đối Chiếu Ảnh 5 Phân Vùng (Thu Gọn / Mở Rộng) & Hỗ Trợ Input JSON / URLs):** **[ACCEPTED - 2026-07-23]** Hoàn tất công cụ đối chiếu hình ảnh đa phân vùng độc lập (`view-images.html` và `/api/compare-images`): 5 phân vùng độc lập 100% (SQLite, Sheet Pool, Sheet Source, Sheet Pool_Images Crawl, Sheet Pool_Images Self), hỗ trợ thu gọn/mở rộng linh hoạt (mặc định thu gọn), nút Mở rộng tất cả, nút Tải tất cả ảnh 5 phân vùng và bypass CORS server-side proxy download.
*   **US-156 (Khắc phục Lỗi Lệch Chỉ Số Dòng Sheet Pool & Ngăn Chặn Chép Đè Hình Ảnh Khi Lên Sóng):** **[ACCEPTED - 2026-07-23]** Xử lý dứt điểm sự cố chép đè dữ liệu ảnh nhầm dòng khi Admin thao tác Lên sóng. Phát hiện và khắc phục lỗi lệch toán học Off-by-One Row Index Bug do Dòng 2 trống trên Sheet Pool làm mảng `POOL_ROWS` bị filter lùi 1 index (`lego_core.js`, `lego_detail_admin.js`), lưu trực tiếp `raw_sheet_row_index` tuyệt đối. Xóa bỏ hoàn toàn đoạn code copy rác các cột ảnh L3744-L3754. Khôi phục thành công 100% dữ liệu ảnh chuẩn của 6 căn từ SQLite Production `D:\02. CONG VIEC\khangngonhapho.com\raw_archive.db` sang Sheet Pool, Sheet Source và Rebuild Cloudflare R2 CDN Shards `20260723-113910`.
*   **US-155 (Dynamic OpenGraph Link Preview từ Cloudflare R2 CDN):** **[ACCEPTED - 2026-07-23]** Nâng cấp Serverless Function `api/index.js` bóc tách dữ liệu từ Cloudflare R2 CDN (`public_data/current.json` ➔ `index.json`) với tốc độ <50ms và header `User-Agent` browser chuẩn. Tiêm động `<title>`, `og:title`, `og:description` và `og:image` chuẩn format (`#Mã - Diện tích: [DT]m², [X] tầng, P.[Phường]. Giá bán: [Giá] tỷ VNĐ. Liên hệ ngay!`) cho link xem trước chi tiết căn nhà (`?s=SYS-XXXXXX`), loại bỏ 100% việc fetch `/gviz` gây timeout rơi vào khung tĩnh.
*   **US-154 (Tối ưu hóa hiệu năng hiển thị Khách hàng & Admin Preview bằng kiến trúc JSON Sharding qua Cloudflare R2):** **[ACCEPTED - 2026-07-22]** Chuyển đổi 100% luồng đọc danh sách/chi tiết Khách hàng và Admin Preview từ IMPORTRANGE/gviz sang Cloudflare R2 CDN JSON Sharding (200 shards, `current.json`, `index.json`) đạt tốc độ <100ms. Thêm Node.js Serverless Rebuilder `/api/public/listings/rebuild` (BigInt SHA-256 modulo 200) và Python `generate_and_upload_public_shards`. Khử trùng lặp URL ảnh public trên cả Frontend (`lego_detail_admin.js`), Backend Serverless (`api/index.js`), và Python (`manager.py`). Tự động gọi `reloadPreviewIframe()` khi Lên sóng (`autoExpandPreview`) với cơ chế tự ẩn loader khẩn cấp 4s, loại bỏ triệt để lỗi treo màn hình đen `0.0s`.

---

## 2. Kế hoạch hành động phiên tiếp theo (Action Plan)

### 🚀 Tính năng Backlog đề xuất (To-Do 📋)
*   **US-153 (Thêm trường custom_phuong và custom_quan trong SQLite và Google Sheets):** **[DRAFT]** Biên tập và override Phường/Quận custom cho từng căn nhà.
*   **US-091 (Khắc phục lỗi giảm chất lượng hình ảnh quá mức khi di cư sang R2):** **[BACKLOG]** Phục hồi chất lượng hình ảnh cao sắc nét từ TK.
*   **US-101 (Tối ưu hóa di cư ảnh khi cào lại và bảo toàn hình ảnh tự tải lên):** **[BACKLOG]** Tránh cào lại và nén/upload lại ảnh đã di cư.

---

## 3. Các file bị tác động trong phiên vừa qua

*   [api/index.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/api/index.js) — Loại bỏ hardcode R2 prefix, nạp động từ process.env.R2_MIGRATION_PREFIX.
*   [core/business_rules.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/core/business_rules.py) — Nạp động R2 prefix từ os.environ/cfg mà không fallback hardcode v3.
*   [tests/test_business_rules.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/tests/test_business_rules.py) — Bổ sung unit test khóa behavior test_dynamic_r2_migration_prefix_from_env.
*   [docs/stories/_inbox/US-156.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-156.md) — Cập nhật nhật ký nghiệm thu Test Pass.

---
*Kế hoạch được lập tự động bởi Antigravity AI Assistant. Cập nhật cuối: 2026-07-24 (US-156 accepted & Test Pass completed).*
