---
id: US-089
status: superseded
date: 2026-06-11
size: XL
---

> [!IMPORTANT]
> **US-089 đã được phân rã thành 4 User Story con để kiểm soát tốt hơn và giảm thiểu rủi ro tích hợp:**
> *   [US-089A: Thiết lập CSDL Quan hệ Pool2 & Tích hợp Luồng Cào thô cục bộ](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-089A_pool2_local_core.md) (Size M)
> *   [US-089B: Tích hợp Google Sheets Đa Quyền Hạn & Luồng Xuất bản Public Whitelist](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-089B_pool2_cloud_publishing.md) (Size M)
> *   [US-089C: Triển khai Cơ chế Đồng bộ Hai Chiều Liên Database](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-089C_pool2_cross_pool_sync.md) (Size M)
> *   [US-089D: Luồng Tự động Mở rộng Schema & Đăng tải Hình ảnh Thủ công](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-089D_pool2_dynamic_schema.md) (Size M)

# US-089: Thiết kế hệ thống Pool2 - Phân hệ dữ liệu mới cho SQLite và Google Sheets v2 theo kiến trúc Lego

## User story
**As an** Admin  
**I want** thiết kế và cấu trúc lại hệ thống cơ sở dữ liệu SQLite và Google Sheets phiên bản 2 (Pool2) độc lập và bảo mật nhiều lớp (sử dụng tệp SQLite `raw_archive_v2.db` riêng biệt, và phân tách 3 tệp Google Spreadsheet riêng biệt cho Raw, Custom và Public) cùng cơ chế đồng bộ dữ liệu liên database với Pool1  
**So that** dữ liệu được bảo mật tuyệt đối theo quyền truy cập, đồng nhất thông tin giữa hai phân hệ cũ và mới để tránh phải nhập liệu hai lần, tải danh sách siêu tốc, và hoàn toàn độc lập theo đúng kiến trúc Lego.

## Acceptance Criteria
- [ ] **Tích hợp cấu hình `"active_pool_system": "Pool2"` vào `settings.json`**:
  - Hỗ trợ chuyển đổi linh hoạt cơ chế xử lý dữ liệu giữa `"Pool1"` (cũ, phẳng) và `"Pool2"` (mới, quan hệ) mà không cần can thiệp mã nguồn.
  - Cấu hình 3 Spreadsheet ID độc lập cho Pool2: `"pool2_raw_sheet_id"`, `"pool2_custom_sheet_id"`, `"pool2_public_sheet_id"` trong `settings.json` để chia tách quyền truy cập.
- [ ] **Thiết kế & Khởi tạo SQLite Version 2 Độc Lập (`raw_archive_v2.db`)**:
  - Tạo tệp database riêng biệt `raw_archive_v2.db` dành riêng cho Pool2.
  - Bảng `listings_v2`: Lưu trữ trọn vẹn thông tin metadata cào được từ backend API của Proptech Thiên Khôi mới (đầy đủ các trường liên quan đến chủ nhà, đầu chủ, hướng, các tiêu chí `criteria` phân tách, diện tích thực tế, diện tích trên sổ, giá chào gốc, độ rộng hẻm, điện thoại, v.v., theo đặc tả [proptech_crawler_specification_v2.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/features/proptech_crawler_specification_v2.md)).
  - Bảng `listings_images`: Lưu trữ danh sách hình ảnh độc lập dạng dòng, liên kết bằng khóa ngoại `tk_id` với các cột: `id` (Primary Key), `tk_id` (Foreign Key), `image_url` (gốc), `cloudinary_url` (CDN link sau khi upload), `role` (vai trò: `facade`, `cover`, `interior`, `alley`, `diagram`), `sequence_index` (thứ tự hiển thị), và `edited_by` (lưu vết tài khoản sửa đổi).
  - Bảng `listings_custom_v2`: Lưu trữ thông tin tùy biến của Admin (địa chỉ thật, giá public, note nội bộ, tình trạng giao dịch, ngủ trệt, CHDV, trạng thái hệ thống KN), cùng các thuộc tính công khai mặc định được sao chép (Quận, Phường, Đường, v.v. để cho phép Admin chỉnh sửa ghi đè thông tin sai từ API gốc) và mảng ảnh an toàn (`images_metadata_json` chỉ chứa vai trò `interior`, `alley`, `cover`; loại bỏ hoàn toàn `facade` và `diagram`). Hỗ trợ thêm hình ảnh thủ công từ Web Admin (tự động append ảnh an toàn vào `images_metadata_json` trên cả File 1 Listings và File 2 Custom).
- [ ] **Thiết kế Google Sheets Version 2 trên 3 Bảng Tính Riêng Biệt**:
  - File 1: `Pool2_Listings_Raw` (Private - chỉ Admin/API): Chứa tab `Listings` (chứa metadata thô cùng trường `images_metadata_json` an toàn) và tab `Images` (danh sách ảnh dạng dòng đầy đủ có cột `Edited By`).
  - File 2: `Pool2_Custom` (Nội bộ team - Restricted): Chứa tab `Custom` để Admin tự ghi chú, chỉnh sửa địa chỉ thật, SĐT, cùng với các thuộc tính công khai mặc định và mảng ảnh an toàn `images_metadata_json` (chỉ chứa ảnh nội thất, hẻm, nền).
  - File 3: `Pool2_Public` (Công khai - Public): Chứa tab `Public` tổng hợp dữ liệu đã làm sạch PII nhạy cảm phục vụ hiển thị lên Web Client, được xây dựng **chỉ bằng cách trích chọn các cột whitelist từ File 2 Custom** và rã mảng ảnh an toàn (không đọc/gộp trực tiếp từ File Raw).
- [ ] **Cơ chế phân giải chỉ số cột động và Tự động nâng cấp SQLite (Dynamic Columns & Auto-migration)**:
  - Cấm hardcode index cột Google Sheets. Sử dụng HeaderMap để tính toán index cột dựa trên tên tiêu đề ở runtime, đảm bảo không lỗi khi thêm cột mới.
  - Sử dụng mảng cấu hình `PUBLIC_METADATA_WHITELIST` để tự động đối chiếu và nâng cấp cấu trúc cột SQLite local (`init_db()` tự động gọi `ALTER TABLE ADD COLUMN` khi cấu hình mở rộng).
- [ ] **Cơ chế Đồng bộ Dữ liệu Liên Database (Cross-Pool DB Synchronization)**:
  - Triển khai cơ chế đồng bộ dựa trên khóa so khớp `tk_id`/`System_ID` giữa hai tệp `raw_archive_v2.db` and `raw_archive.db` để giữ dữ liệu local luôn đồng nhất.
  - **Đồng bộ xuôi (Pool2 -> Pool1 - Làm phẳng)**: Khi cập nhật hoặc xuất bản ở Pool2, tự động lấy dữ liệu và làm phẳng danh sách ảnh (lọc theo role để gán vào các cột `Ảnh 1-25`, `Hình Hẻm 1-10`, `Sơ đồ 1-5`) ghi nhận vào bảng `listings` của Pool1.
  - **Đồng bộ ngược (Pool1 -> Pool2 - Quan hệ hóa)**: Cho phép chuyển đổi dữ liệu phẳng cũ sang cấu trúc quan hệ, phân tách ảnh theo vai trò và thứ tự vào bảng `listings_images` và các trường tương ứng vào bảng `listings_custom_v2`.
- [ ] **Nâng cấp Module Lego `pool_lego.py`**:
  - Hàm `get_db_file()`: Trả về `raw_archive_v2.db` nếu `"active_pool_system"` là `"Pool2"`.
  - Hàm `init_db()`: Tự động phát hiện cấu hình active pool và khởi tạo các bảng tương ứng cho Pool2 (`listings_v2`, `listings_images`, `listings_custom_v2`) trên database `raw_archive_v2.db` nếu chưa tồn tại.
  - Hàm `save_raw_to_sqlite()`: Khi chạy mode Pool2, thực hiện phân tích cú pháp JSON cào được từ API chi tiết theo đặc tả mới, lưu đầy đủ các trường văn bản vào bảng `listings_v2` và ghi nhận danh sách ảnh vào bảng `listings_images` dạng dòng (ghi nhận tài khoản thực hiện vào cột `edited_by`).
  - Hàm `publish_listing()`: Khi ở mode Pool2, sử dụng các Spreadsheet ID độc lập để đồng bộ dữ liệu metadata văn bản lên tab `Listings` của File Raw, đồng bộ dữ liệu tùy biến và ảnh an toàn lên tab `Custom` của File Custom, sau đó thực hiện trích chọn cột whitelist từ File Custom và rã mảng ảnh để ghi trực tiếp sang tab `Public` của File Public.
- [ ] **Tương thích ngược & Khớp nối Hệ thống**:
  - Đảm bảo khi `"active_pool_system"` là `"Pool1"`, hệ thống chạy hoàn toàn bình thường trên database cũ `raw_archive.db` và spreadsheet ID cũ theo schema phẳng mà không có bất kỳ lỗi hồi quy nào.
  - Khớp nối mượt màng với [fetcher.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/fetcher.py) (luồng cào) và [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py) (luồng Flask server/API hiển thị cho Curator Web App).
- [ ] **Triển khai tính năng tự động mở rộng Schema (Dynamic Schema Extension Pipeline)**:
  - Xây dựng API endpoint `POST /api/schema/add-column` (và lệnh CLI tương đương) thực hiện đồng bộ 4 bước:
    1. Tự động chèn cột mới vào mảng whitelist và schema trong `settings.json`.
    2. Chạy câu lệnh `ALTER TABLE` tự thêm cột trênSQLite `listings_v2` và `listings_custom_v2`.
    3. Sử dụng Google Sheets API tự động chèn cột tiêu đề tương ứng ở dòng 1 của File 1 Raw, File 2 Custom, và File 3 Public (nếu thuộc whitelist).
    4. Tự động append dòng mô tả thuộc tính mới vào file tài liệu [docs/pool_sheet_schema.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/pool_sheet_schema.md) và [docs/data_dictionary.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/data_dictionary.md).
  - Loại bỏ hoàn toàn rủi ro thao tác thủ công thiếu bước gây lệch dữ liệu.

## Solution
### 1. SQLite Relational Schema
Bảng `listings_v2` (Lưu thông tin metadata căn nhà):
- `tk_id` TEXT UNIQUE (Mã căn UUID đối tác)
- `status` TEXT (Trạng thái xử lý thô: `raw_text`, `raw_complete`, `published`)
- `System_ID` TEXT (System ID của Khang Ngô)
- `Ma_Hang` TEXT (Mã hàng hiển thị)
- `Quan` TEXT, `Phuong` TEXT, `Duong` TEXT, `Ngo_So_nha` TEXT
- `Noi_dung_chinh` TEXT, `Mo_ta_chi_tiet` TEXT
- `Gia_chao` TEXT, `DT_Thuc_te` TEXT, `DT_Tren_so` TEXT, `So_Tang` TEXT, `Mat_Tien` TEXT, `Chieu_dai` TEXT
- `So_phong_ngu` TEXT, `So_nha_ve_sinh` TEXT, `Huong` TEXT, `Duong_truoc_nha_m` TEXT
- `Ten_Chu_Nha` TEXT, `Dien_thoai_1` TEXT
- `Ten_Dau_Chu_Hop_dong` TEXT, `Dien_thoai_Dau_Chu` TEXT, `Diem_Facebook` TEXT
- `Link_Goc` TEXT, `Last_Crawl` TEXT, `Last_Sync` TEXT, `Phan_loai` TEXT (Criteria list join), `Trang_thai_nguon` TEXT, `Loai_Hop_dong` TEXT, v.v.

Bảng `listings_images` (Lưu thông tin ảnh dạng dòng):
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `tk_id` TEXT (Khóa ngoại liên kết tới `listings_v2.tk_id`)
- `image_url` TEXT (URL ảnh gốc của Thiên Khôi)
- `cloudinary_url` TEXT (URL ảnh sau khi upload lên CDN Cloudinary)
- `role` TEXT (Nhãn vai trò: `'facade'`, `'cover'`, `'interior'`, `'alley'`, `'diagram'`)
- `sequence_index` INTEGER (Chỉ số thứ tự sắp xếp)
- `edited_by` TEXT (Email/Google Account của Admin chỉnh sửa ảnh)

Bảng `listings_custom_v2` (Lưu thông tin tùy biến của Admin, thuộc tính công khai và ảnh an toàn):
- `System_ID` TEXT PRIMARY KEY (Khóa chính so khớp)
- `Ma_Khang_Ngo` TEXT
- `Dia_Chi_That` TEXT
- `So_Nha` TEXT, `Ten_Duong` TEXT
- `Gia_Public` TEXT
- `Tieu_De_Public` TEXT, `Mo_ta_Public` TEXT
- `Note_Noi_Bo` TEXT
- `Trang_Thai_Giao_Dich` TEXT
- `Quan` TEXT, `Phuong` TEXT
- `DT_Tren_so` TEXT
- `So_Tang` TEXT
- `Mat_Tien` TEXT
- `Huong` TEXT
- `Duong_truoc_nha_m` TEXT
- `Loai_BDS` TEXT
- `Ngu_Tret` TEXT (Có ngủ trệt hay không: Y/N)
- `CHDV` TEXT (Có phải CHDV hay không: Y/N)
- `Trang_Thai_KN` TEXT (Trạng thái hiển thị nội bộ hệ thống Khang Ngô: Active/Sold/Invisible/v.v.)
- `images_metadata_json` TEXT (JSON mảng ảnh an toàn: chỉ chứa interior, alley, cover; không chứa facade, diagram)

### 2. Google Sheets Structure
- File 1 (`Pool2_Listings_Raw`): tab `Listings` (các cột tương đương `listings_v2`) và tab `Images` (`System ID`, `Mã Hàng`, `Image URL`, `Role`, `Sequence`, `Edited By`).
- File 2 (`Pool2_Custom`): tab `Custom` (các cột tương đương `listings_custom_v2` để lưu trữ thông tin tùy biến, note nội bộ, địa chỉ thật, cùng các thuộc tính công khai và mảng ảnh an toàn).
- File 3 (`Pool2_Public`): tab `Public` (dữ liệu làm sạch PII nhạy cảm. Chỉ lấy các cột chọn lọc trong tab `Custom` của File 2 và rã chuỗi `images_metadata_json` thành các cột Ảnh 1-15).

### 3. Đồng bộ hóa giữa hai CSDL
- Sử dụng hàm `pool_lego.sync_between_databases(source_pool, target_pool, tk_id=None)` để đồng bộ:
  - Khi cào tin hoặc edit trong Pool2, tự động ghi đè bản ghi đã làm phẳng tương ứng sang `raw_archive.db` (Pool1) để tương thích ngược.
  - Hỗ trợ CLI commands chạy đồng bộ hàng loạt (Bulk Sync) phục vụ nhu cầu chuyển đổi dữ liệu.

## Verification Plan
### Automated Tests
- Chạy biên dịch kiểm tra lỗi cú pháp: `python -m py_compile pool_lego.py fetcher.py manager.py`.
- Viết Unit Test giả lập cào dữ liệu từ API Proptech Thiên Khôi, ghi nhận vào SQLite `raw_archive_v2.db` và xuất bản lên 3 tệp Google Sheets độc lập ở chế độ Pool2 để xác minh tính bảo mật và độc lập của từng file.
- Viết test case xác minh cơ chế đồng bộ dữ liệu hai chiều: đảm bảo dữ liệu gộp từ Pool2 khi ghi sang `raw_archive.db` được làm phẳng hình ảnh chính xác; và dữ liệu từ Pool1 khi đồng bộ sang Pool2 được phân tách ảnh và metadata đúng chuẩn quan hệ.

### Manual Verification
1. Cấu hình `"active_pool_system": "Pool2"` và các khóa ID của 3 tệp Google Sheet riêng biệt trong `settings.json`.
2. Khởi chạy server biên tập, thực hiện cào thử một vài căn từ API `proptech.thienkhoi.com` mới.
3. Xác nhận tệp `raw_archive_v2.db` được sinh ra độc lập, dữ liệu được phân chia chính xác vào bảng `listings_v2`, `listings_images` (ghi vết email trong `edited_by`) và `listings_custom_v2`.
4. Bấm **Xuất bản (Publish)** trên giao diện Admin, kiểm tra tab `Public` trên file `Pool2_Public` xem thông tin đã được làm sạch và đồng bộ chính xác, không chứa thông tin nhạy cảm. Kiểm tra File 1 và File 2 xem dữ liệu thô và custom được lưu giữ riêng tư chính xác.
5. Kiểm tra tệp `raw_archive.db` (Pool1) xem bản ghi đó đã tự động được đồng bộ và làm phẳng hình ảnh tương ứng hay chưa.
6. Chuyển lại `"active_pool_system": "Pool1"` và xác nhận luồng cũ vẫn chạy mượt mà trên database cũ `raw_archive.db` và spreadsheet ID cũ.

## 📋 Implementation Plan
> [!plan]- Kế hoạch Triển khai (Bắt buộc cho Size M/L/XL)
> - **Cách tiếp cận:** Xây dựng cấu trúc dữ liệu quan hệ cho Pool2 trên SQLite `raw_archive_v2.db` độc lập, đồng thời cài đặt các cơ chế phân tách và chọn lọc dữ liệu (whitelist) khi đẩy lên 3 file Google Sheets. Triển khai logic ghi đè dữ liệu sai (như Phường, Quận, Tên Đường) và upload hình ảnh tự chọn trên Web Admin thông qua API trung gian.
> - **Các bước triển khai dự kiến:**
>   1. **Thiết kế Cấu trúc CSDL Local (SQLite Pool2):** Khởi tạo `listings_v2` (chứa toàn bộ metadata cào thô), `listings_images` (chứa ảnh dòng, vai trò, thứ tự, edited_by), và `listings_custom_v2` (chứa các trường custom: địa chỉ thật, note nội bộ, ngủ trệt, CHDV, trạng thái KN, các thuộc tính công khai có thể chỉnh sửa ghi đè, và chuỗi JSON `images_metadata_json`).
>   2. **Triển khai Logic cào dữ liệu (`fetcher.py`):** Khi ở mode Pool2, bóc tách API Thiên Khôi chi tiết, ghi nhận dữ liệu thô vào `listings_v2` và `listings_images`. Sau đó đẩy dữ liệu thô lên File 1 `Pool2_Listings_Raw`. Đồng thời, tự động khởi tạo dòng tương ứng bên File 2 `Pool2_Custom` và bảng `listings_custom_v2` (copy mặc định các thuộc tính công khai và trích chọn danh sách ảnh an toàn `interior`, `alley`, `cover`).
>   3. **Triển khai Logic biên tập trên Web Admin (`manager.py`):**
>      - Cho phép Admin cập nhật các trường tùy biến trong `listings_custom_v2` bao gồm cả việc tự gõ đè tên Phường, Quận, Đường nếu API cào thô bị sai.
>      - Cho phép upload ảnh thủ công qua Web Admin: ảnh được Cloudinary lưu, chèn vào `listings_images` (SQLite local) và cột `curated_config_json` trên File 1 Raw, nếu có role an toàn thì đồng thời cập nhật vào `images_metadata_json` của Custom.
>   4. **Triển khai Logic xuất bản File Public (`pool_lego.py`):** Khi Admin nhấn Publish ở chế độ Pool2, hệ thống chỉ đọc dữ liệu từ File 2 `Pool2_Custom`, trích xuất các cột thuộc whitelist công khai (loại trừ địa chỉ thật, số nhà, note nội bộ), rã `images_metadata_json` thành các cột Ảnh 1-15 và ghi đè sang File 3 `Pool2_Public`.
>   5. **Triển khai Cơ chế đồng bộ Cross-Pool:** Triển khai hàm `sync_between_databases()` đồng bộ dữ liệu hai chiều giữa `raw_archive_v2.db` và `raw_archive.db` để tương thích ngược 100% khi người dùng bật tắt cấu hình `"active_pool_system"`.

## 📝 Task Checklist (TODO)
> [!todo]- Danh sách việc cần làm để theo dõi tiến độ
> - [ ] **Thiết kế & Khảo sát:**
>   - [ ] Cập nhật Settings trong `settings.json` cho 3 file Google Sheets của Pool2.
>   - [ ] Thiết lập cấu trúc các bảng quan hệ cục bộ trong SQLite `raw_archive_v2.db`.
> - [ ] **Triển khai Code:**
>   - [ ] Implement hàm `init_db()` khởi tạo bảng quan hệ cho Pool2 trong `pool_lego.py`.
>   - [ ] Cấu hình cào dữ liệu và ghi nhận thô + khởi tạo dữ liệu Custom mặc định trong `fetcher.py`.
>   - [ ] Cài đặt các API endpoint cập nhật Custom (bao gồm sửa tên Quận/Phường/Đường, toggle Ngủ trệt/CHDV/Trạng thái KN) và upload ảnh tự thêm trên Web Admin trong `manager.py`.
>   - [ ] Cài đặt logic Publish trích lọc cột whitelist từ File Custom sang File Public trong `pool_lego.py`.
>   - [ ] Triển khai hàm `sync_between_databases()` đồng bộ hai chiều phẳng-quan hệ giữa Pool1 và Pool2.
> - [ ] **Kiểm thử sơ bộ & Retro:**
>   - [ ] Viết script unit test kiểm tra luồng cào, lưu SQLite, đồng bộ Sheets, lọc ảnh, và ghi đè tên Phường/Quận/Đường.
>   - [ ] Kiểm tra tương thích ngược hoàn chỉnh khi đổi về mode Pool1.

## 🛠️ Update Logic (Drafting while Doing)
### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:** *[Chưa triển khai]*
- **Phát kiến ngoài kế hoạch / Điểm tối ưu phát hiện khi code:** *[Chưa triển khai]*

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- **Script kiểm thử thô / nháp đã chạy:** *[Chưa triển khai]*

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)
### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** *[Chưa]*

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm code & Cấu hình:** *[Chưa]*

## Files touched
- `docs/features/proptech_crawler_specification_v2.md` — Cập nhật đặc tả bảo mật hình ảnh và hiệu chỉnh dữ liệu sai.
- `docs/stories/_inbox/US-089_pool2_data_system.md` — Cập nhật thiết kế schema listings_custom_v2 và Acceptance Criteria.
- `BDS-AGENTS.md` — Cập nhật Luật 16 về an toàn dữ liệu và đồng bộ whitelist.
