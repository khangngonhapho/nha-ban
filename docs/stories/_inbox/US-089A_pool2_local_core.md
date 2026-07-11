---
id: US-089A
status: accepted
date: 2026-06-11
size: M
replaces: US-089
---

# US-089A: Thiết lập CSDL Quan hệ Pool2 & Tích hợp Luồng Cào thô cục bộ (Local Core)

## User story
**As an** Admin  
**I want** thiết lập cơ sở dữ liệu SQLite quan hệ cục bộ (`raw_archive_v2.db`) và cập nhật luồng cào tin thô  
**So that** dữ liệu crawler thô và danh sách hình ảnh được phân tách, lưu vết đầy đủ chuẩn quan hệ cục bộ trước khi đồng bộ lên Sheets.

## Acceptance
- [x] **Tích hợp cấu hình `"active_pool_system": "Pool2"` vào `settings.json`**:
  - Khi bật `"Pool2"`, hàm `get_db_file()` trong `pool_lego.py` trả về `raw_archive_v2.db` (không dùng chung `raw_archive.db` của Pool1).
- [x] **Khởi tạo cấu trúc CSDL cục bộ Pool2**:
  - Hàm `init_db()` trong `pool_lego.py` tự động khởi tạo 3 bảng SQLite:
    1. Bảng `listings_v2` (metadata văn bản cào thô đầy đủ trường và 19 cột tiêu chí `Criteria_...`).
    2. Bảng `listings_images` (dòng ảnh độc lập liên kết bằng khóa ngoại `tk_id`).
    3. Bảng `listings_custom_v2` (thông tin tùy biến của Admin và mảng ảnh an toàn).
- [x] **Tích hợp luồng cào dữ liệu (`fetcher.py`)**:
  - Khi cào tin, bóc tách JSON API TK chi tiết, ghi nhận dữ liệu văn bản vào `listings_v2` và phân tách danh sách ảnh dạng dòng vào `listings_images` (mặc định sequence_index và role thô).
  - Tự động sinh `System_ID` và mã hóa `Ma_Hang` cho căn mới.
  - Phân tích danh sách `criteria` từ API TK mới và điền vào 19 cột tiêu chí `Criteria_...` tương ứng của `listings_v2`.
- [x] **Xây dựng công cụ tra cứu cơ sở dữ liệu trực quan (`query_helper.py` & `TRUY_VAN_CSDL.bat`)**:
  - Thực thi qua menu lệnh `.bat` đơn giản trên màn hình.
  - Hỗ trợ xem thống kê tổng quan (phân bổ số căn theo trạng thái).
  - Tìm kiếm linh hoạt theo Mã TK/Mã Hàng hoặc kết hợp "Số nhà + Tên đường".
  - Khi xem chi tiết căn nhà: tự động biên dịch toàn bộ thuộc tính văn bản (gồm cả 19 trường tiêu chí) và mảng ảnh thành một trang HTML cục bộ đẹp mắt (Premium Dark Mode) và dùng trình duyệt mặc định mở ra để hiển thị trực quan inline hình ảnh.

## Solution

### 1. SQLite Relational Schema
Bảng `listings_v2` (Lưu thông tin metadata căn nhà thô):
- `tk_id` TEXT PRIMARY KEY (UUID đối tác)
- `status` TEXT (Trạng thái thô: `raw_text`, `raw_complete`, `published`)
- `System_ID` TEXT
- `Ma_Hang` TEXT
- `Quan` TEXT, `Phuong` TEXT, `Duong` TEXT, `Ngo_So_nha` TEXT
- `bedrooms` TEXT, `restrooms` TEXT, `minimumRoadWidth` TEXT
- `Noi_dung_chinh` TEXT, `Mo_ta_chi_tiet` TEXT
- `Gia_chao` TEXT, `DT_Thuc_te` TEXT, `DT_Tren_so` TEXT, `So_Tang` TEXT, `Mat_Tien` TEXT, `Chieu_dai` TEXT, `Huong` TEXT
- `Ten_Chu_Nha` TEXT, `Dien_thoai_1` TEXT, `Ten_Dau_Chu` TEXT, `Dien_thoai_Dau_Chu` TEXT, `Diem_Facebook` TEXT
- `Link_Goc` TEXT, `Last_Crawl` TEXT, `Last_Sync` TEXT
- 19 trường tiêu chí cào thô: `Criteria_Tiem_nang_Rui_ro`, `Criteria_Duong_truoc_nha`, `Criteria_Loai_BDS`, `Criteria_Giay_to_phap_ly`, `Criteria_Hinh_dang_dat`, `Criteria_Tinh_trang_xay_dung`, `Criteria_Cau_truc_nha`, `Criteria_Noi_that`, `Criteria_Thang_may`, `Criteria_Loai_ngo`, `Criteria_Vi_tri_tinh_thue`, `Criteria_Mat_thoang`, `Criteria_Khoang_cach_bai_do_xe`, `Criteria_Kinh_doanh_Dong_tien`, `Criteria_Tien_ich`, `Criteria_Phong_thuy`, `Criteria_Huong_nha`, `Criteria_Vi_tri_trong_ngo`, `Criteria_Khoang_cach_duong_oto` TEXT.

Bảng `listings_images` (Lưu ảnh dạng dòng):
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `tk_id` TEXT (Khóa ngoại liên kết tới `listings_v2.tk_id`)
- `image_url` TEXT (URL ảnh thô)
- `cloudinary_url` TEXT (URL ảnh CDN Cloudinary sau khi upload)
- `role` TEXT (Nhãn vai trò: `facade`, `cover`, `interior`, `alley`, `diagram`)
- `sequence_index` INTEGER (Thứ tự sắp xếp)
- `edited_by` TEXT (Email/Account Admin chỉnh sửa ảnh)

Bảng `listings_custom_v2` (Lưu thông tin tùy biến của Admin, thuộc tính công khai và ảnh an toàn):
- **Nhóm Định Danh**:
  - `System_ID` TEXT PRIMARY KEY (Khóa chính dùng để so khớp)
  - `Ma_Khang_Ngo` TEXT (Mã nhà riêng của Admin)
- **Nhóm Biên Tập Admin (Nội bộ & Public)**:
  - `Gia_Public` TEXT
  - `Tieu_De_Public` TEXT
  - `Mo_ta_Public` TEXT
  - `Note_Noi_Bo` TEXT
  - `Trang_Thai_Giao_Dich` TEXT
  - `Ngu_Tret` TEXT (Có ngủ trệt hay không: Y/N)
  - `CHDV` TEXT (Có phải CHDV hay không: Y/N)
  - `Trang_Thai_KN` TEXT
  - `images_metadata_json` TEXT
- **Nhóm Địa Chỉ (Cho phép đè thông tin cào sai - trùng tên với listings_v2)**:
  - `Dia_Chi_That` TEXT
  - `So_Nha` TEXT
  - `Ten_Duong` TEXT
  - `Quan` TEXT
  - `Phuong` TEXT
  - `Duong` TEXT
  - `Ngo_So_nha` TEXT
- **Nhóm Thông Tin Chi Tiết & Kỹ Thuật (Cho phép đè thông tin cào sai - trùng tên với listings_v2)**:
  - `bedrooms` TEXT
  - `restrooms` TEXT
  - `minimumRoadWidth` TEXT
  - `Noi_dung_chinh` TEXT
  - `Mo_ta_chi_tiet` TEXT
  - `Gia_chao` TEXT
  - `DT_Thuc_te` TEXT
  - `DT_Tren_so` TEXT
  - `So_Tang` TEXT
  - `Mat_Tien` TEXT
  - `Chieu_dai` TEXT
  - `Huong` TEXT
- **Nhóm Tiêu Chí Phân Loại (Cho phép đè thông tin cào sai - trùng tên với listings_v2)**:
  - `Criteria_Duong_truoc_nha` TEXT
  - `Criteria_Noi_that` TEXT
  - `Criteria_Thang_may` TEXT
  - `Criteria_Loai_ngo` TEXT
  - `Criteria_Khoang_cach_bai_do_xe` TEXT
  - `Criteria_Kinh_doanh_Dong_tien` TEXT
  - `Criteria_Huong_nha` TEXT
  - `Criteria_Khoang_cach_duong_oto` TEXT

## Proposed Changes

### [Component: Configuration]

#### [MODIFY] [settings.json](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/settings.json)
- Thêm hoặc điều chỉnh cấu hình `"active_pool_system": "Pool2"` để kích hoạt hệ thống Pool2.

### [Component: Data & DB Sync (pool_lego)]

#### [MODIFY] [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py)
- **Hàm `get_db_file()`**:
  - Đọc tệp `settings.json` tại thời điểm chạy.
  - Nếu `"active_pool_system"` có giá trị là `"Pool2"`, trả về `"raw_archive_v2.db"`.
  - Ngược lại, fallback về `"raw_archive.db"` để bảo toàn khả năng tương thích ngược với Pool1.
- **Hàm `init_db(db_file=None)`**:
  - Kiểm tra xem chế độ Pool2 có đang hoạt động hay không.
  - Nếu ở chế độ Pool2:
    1. Khởi tạo bảng `listings_v2` (chứa dữ liệu metadata văn bản thô đầy đủ trường tương đương `POOL_HEADERS` cùng **19 cột tiêu chí `Criteria_...`**). Sử dụng `tk_id` làm khóa chính (PRIMARY KEY).
    2. Khởi tạo bảng `listings_images` với các cột (`id` tự tăng, `tk_id` khóa ngoại, `image_url` ảnh thô, `cloudinary_url` CDN, `role` vai trò ảnh, `sequence_index` thứ tự sắp xếp, `edited_by` người sửa). Tạo chỉ mục `idx_listings_images_tk_id` trên cột `tk_id`.
    3. Khởi tạo bảng `listings_custom_v2` cho thông tin chỉnh sửa tùy biến của Admin. Loại bỏ các cột trùng lặp, chuẩn hóa đặt tên trùng khớp với `listings_v2`, sắp xếp theo thứ tự Định danh -> Admin -> Địa chỉ -> Kỹ thuật -> Tiêu chí.
    4. Thêm logic nâng cấp cột tự động (migration) cho bảng `listings_v2` và `listings_custom_v2` để đảm bảo có đầy đủ các cột mới khi schema thay đổi.
  - Nếu ở chế độ Pool1: Chạy logic khởi tạo schema cũ và di trú cột của bảng `listings`.
  - Cả hai chế độ đều khởi tạo bảng `crawl_sessions` để ghi nhật ký phiên cào.
- **Hàm `save_raw_to_sqlite(tk_id, metadata, images_tk_list, db_file=None)`**:
  - Kiểm tra xem chế độ Pool2 có hoạt động hay không.
  - Nếu hoạt động:
    1. Đảm bảo tạo sẵn trường `"System ID"` (nếu chưa có) dạng `SYS-YYYYMMDD-XXX` và `"Mã Hàng"` dạng `TK-<suffix_tk_id>` trong payload metadata của căn nhà mới.
    2. Thực hiện `INSERT` hoặc `UPDATE` dòng dữ liệu văn bản vào bảng `listings_v2`.
    3. Trích xuất danh sách ảnh sơ đồ (`Sơ đồ thửa đất 1...5`) từ `metadata` (gán role `diagram`).
    4. Trích xuất danh sách ảnh nội thất thô từ `images_tk_list` (gán role `interior`).
    5. Kiểm tra trùng lặp ảnh trong `listings_images` cho `tk_id` này. Chỉ lưu những đường dẫn ảnh thô chưa có trong cơ sở dữ liệu để tránh ghi đè hoặc nhân bản dữ liệu ảnh khi quét lại (recrawl), gán `sequence_index` tự tăng dần.
  - Nếu không hoạt động (Pool1): Thực thi luồng lưu trữ cũ vào bảng `listings`.

### [Component: Crawler (fetcher)]

#### [MODIFY] [fetcher.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/fetcher.py)
- Khai báo biến toàn cục `LISTINGS_TABLE = "listings_v2" if DB_FILE == "raw_archive_v2.db" else "listings"` ở đầu file (sau khi import `pool_lego`).
- Thay thế các truy vấn tĩnh có chứa bảng `listings` thành bảng động `f"{LISTINGS_TABLE}"`.
- **Viết hàm `parse_criteria_groups(criteria_list)`**:
  - Nhận danh sách criteria từ dữ liệu API chi tiết TK mới.
  - Ánh xạ các thuộc tính theo `groupCode` thành 19 cột `Criteria_...` (ví dụ `ROAD_TYPE` thành `Criteria_Duong_truoc_nha`, `LEGAL_DOCUMENT` thành `Criteria_Giay_to_phap_ly`...).
  - Ghép nhiều phần tử trùng nhóm bằng dấu phẩy.
- **Tích hợp luồng cào API chi tiết (`scrape_district_proptech`)**:
  - Gọi `parse_criteria_groups` với `detail_data.get("criteria", [])`.
  - Cập nhật các trường `Criteria_...` thu được vào payload `crawled_data` trước khi lưu trữ qua `save_raw_to_sqlite()`.

### [Component: local Database Viewer Utility]

#### [NEW] [query_helper.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/query_helper.py)
- Xây dựng CLI tương tác bằng Python để truy vấn CSDL cục bộ:
  - **Chức năng 1 (Thống kê tổng quan)**: In ra số căn theo phân bổ trạng thái (`raw_text`, `raw_complete`, `published`).
  - **Chức năng 2 (Tìm kiếm nâng cao)**: Cho phép tìm kiếm theo:
    - Mã TK (tk_id) / Mã Hàng.
    - Số nhà + Tên đường (sử dụng LIKE không dấu hỗ trợ tìm kiếm linh hoạt).
  - **Chức năng 3 (Xuất trang chi tiết HTML)**: Khi chọn xem chi tiết căn nhà:
    - Truy vấn toàn bộ cột trong `listings_v2` (bao gồm cả **19 cột tiêu chí `Criteria_...`**) và ảnh tương ứng trong `listings_images`.
    - Biên tập thông tin thành một file HTML tạm thời ở thư mục `temp_viewer.html` sử dụng thiết kế UI Premium Dark Mode, hiển thị toàn bộ thuộc tính văn bản thành các bảng/thẻ thông tin rõ ràng và hiển thị các hình ảnh trực tiếp dạng lưới ảnh (image grid), ảnh sơ đồ thửa đất cách biệt với ảnh nội thất.
    - Gọi thư viện `webbrowser` tự động mở file HTML này trên trình duyệt mặc định của người dùng.

#### [NEW] [TRUY_VAN_CSDL.bat](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/TRUY_VAN_CSDL.bat)
- File thực thi CMD cục bộ gọi nhanh script Python:
  ```batch
  @echo off
  chcp 65001 > nul
  python "%~dp0query_helper.py"
  pause
  ```

## Verification Plan

### Automated Tests
- Chạy kiểm tra lỗi cú pháp: `python -m py_compile pool_lego.py fetcher.py query_helper.py`.
- Viết test script giả lập tại [scratch/test_pool2_local.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_pool2_local.py) để kiểm tra việc tạo schema và lưu thô của cả hai chế độ Pool1/Pool2.

### Manual Verification
1. Cấu hình `"active_pool_system": "Pool2"` trong `settings.json`.
2. Khởi chạy thử lệnh cào tin thô một căn đơn lẻ.
3. Chạy file **`TRUY_VAN_CSDL.bat`**, chọn **`[1]`** để xem thống kê căn vừa cào.
4. Chọn **`[2]`**, tìm kiếm căn đó bằng số nhà và tên đường hoặc mã TK.
5. Xác nhận hệ thống tìm ra căn nhà, tạo file HTML và tự động bật trình duyệt hiển thị:
   - Toàn bộ thông tin chi tiết căn nhà (mã, diện tích, giá, số phòng, mô tả...).
   - **Đầy đủ 19 tiêu chí phân loại chi tiết (Criteria_...)**.
   - Hiển thị trực quan toàn bộ hình ảnh (ảnh nội thất, ảnh sơ đồ thửa đất hiển thị đầy đủ hình dạng chứ không chỉ là text link).
6. Chuyển cấu hình lại thành `"active_pool_system": "Pool1"` trong `settings.json`, chạy cào lẻ để kiểm tra tính tương thích ngược bình thường.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Đọc hiểu mã nguồn SQLite cũ trong `pool_lego.py`.
  - [x] Kiểm chứng các trường thô trả về từ API TK mới.
- [x] **Triển khai Code:**
  - [x] Cập nhật cấu hình `"active_pool_system"` trong settings.json.
  - [x] Code hàm `get_db_file()` trả về `raw_archive_v2.db`.
  - [x] Code hàm `init_db()` khởi tạo cấu trúc bảng quan hệ mới bao gồm 19 cột Criteria_...
  - [x] Code hàm `save_raw_to_sqlite()` phân tách văn bản và dòng ảnh thô.
  - [x] Khớp nối `fetcher.py`: bóc tách và phân nhóm criteria từ JSON TK API mới.
  - [x] Viết `query_helper.py` và `TRUY_VAN_CSDL.bat` hỗ trợ tìm kiếm, tra cứu chi tiết trực quan qua HTML.
- [x] **Kiểm thử cục bộ:**
  - [x] Chạy thử python pipeline để cào 1 căn và xác nhận database `raw_archive_v2.db` sinh ra đúng chuẩn, các bảng chứa đầy đủ dữ liệu và các cột tiêu chí `Criteria_...`.
  - [x] Chạy `TRUY_VAN_CSDL.bat`, tìm kiếm căn nhà và xác nhận trình duyệt bật lên hiển thị chi tiết cùng hình ảnh inline đầy đủ.

## Files touched
- `settings.json` — Cấu hình Pool active.
- `pool_lego.py` — Logic kết nối CSDL và lưu thô quan hệ.
- `fetcher.py` — Khớp nối crawler ghi nhận CSDL cục bộ.
- `query_helper.py` — CLI truy vấn và kết xuất HTML xem chi tiết.
- `TRUY_VAN_CSDL.bat` — File khởi chạy giao diện dòng lệnh.
- `docs/stories/_inbox/US-089A_pool2_local_core.md` — User Story.
