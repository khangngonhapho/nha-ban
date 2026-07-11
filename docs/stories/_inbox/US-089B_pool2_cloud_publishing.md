---
id: US-089B
status: accepted
date: 2026-06-11
size: M
replaces: US-089
---

# US-089B: Tích hợp Google Sheets Đa Quyền Hạn & Luồng Xuất bản Public Whitelist (Cloud Publishing)

## User story
**As an** Admin  
**I want** cấu hình và đồng bộ dữ liệu Pool2 lên 3 file Google Sheets độc lập khác nhau về phân quyền (Raw, Custom, Public)  
**So that** dữ liệu thô nhạy cảm được giấu kín, và dữ liệu website công khai được làm sạch hoàn toàn PII nhạy cảm thông qua trích chọn whitelist cột từ File Custom.

## Acceptance
- [ ] **Cấu hình 3 file Google Sheets độc lập**:
  - settings.json có 3 Spreadsheet ID: `"pool2_raw_sheet_id"`, `"pool2_custom_sheet_id"`, `"pool2_public_sheet_id"`.
- [ ] **Đồng bộ thô lên File 1 Raw (`Pool2_Listings_Raw`)**:
  - Ghi nhận đầy đủ thông tin cào thô văn bản và danh sách hình ảnh dạng chuỗi JSON (`raw_images_tk_json`, `raw_drive_images_json`) vào tab `Listings` (Không sinh ra dòng ảnh lặp để tránh quá tải dung lượng dòng của Google Sheets).
- [ ] **Đồng bộ dữ liệu tùy biến lên File 2 Custom (`Pool2_Custom`)**:
  - Ghi nhận thông tin tùy biến của Admin (địa chỉ thật, note nội bộ, ngủ trệt, CHDV, trạng thái KN) cùng các thuộc tính công khai mặc định và mảng ảnh an toàn (`images_metadata_json` chỉ chứa vai trò interior, alley, cover; nghiêm cấm mặt tiền và sơ đồ).
- [ ] **Xuất bản dữ liệu sạch lên File 3 Public (`Pool2_Public`)**:
  - Hàm `publish_listing()` ở mode Pool2 chỉ đọc dữ liệu từ File 2 Custom, trích xuất các cột thuộc whitelist công khai (Quận, Phường, Tên Đường, DT Trên sổ, Số Tầng, Mặt Tiền, Hướng, Độ rộng hẻm, Loại hình, Giá Public, Tiêu đề Public, Mô tả Public, Trạng thái Giao dịch).
  - Rã mảng ảnh an toàn từ `images_metadata_json` thành các cột Ảnh 1 đến Ảnh N (tự động giãn rộng).
  - Tuyệt đối không đọc trực tiếp từ File 1 Raw để loại bỏ triệt để nguy cơ rò rỉ dữ liệu nhạy cảm.

## Solution

### 1. Google Sheets Structure
- **File 1 (`Pool2_Listings_Raw`)**: tab `Listings` (Chứa metadata thô và ảnh dạng chuỗi JSON `raw_images_tk_json`, `raw_drive_images_json` gom chung trên một dòng).
- **File 2 (`Pool2_Custom`)**: tab `Custom` (đầy đủ các cột của bảng `listings_custom_v2`).
- **File 3 (`Pool2_Public`)**: tab `Public` (dữ liệu sạch công khai cho khách hàng lọc trên website).

### 2. Whitelist Columns for File 3 (Public)
Chỉ cho phép đồng bộ các cột sau từ File 2 Custom sang File 3 Public:
- `System_ID`
- `Ma_Khang_Ngo` (Mã định danh công khai gửi khách)
- `Tieu_De_Public`, `Mo_ta_Public`
- `Gia_Public`
- `Trang_Thai_Giao_Dich`
- `Ngu_Tret`
- `CHDV`
- `Trang_Thai_KN`
- `Ten_Duong`
- `Quan`
- `Phuong`
- `Duong`
- `bedrooms`
- `restrooms`
- `minimumRoadWidth`
- `DT_Thuc_te`
- `DT_Tren_so`
- `So_Tang`
- `Mat_Tien`
- `Chieu_dai`
- `Huong`
- `Criteria_Duong_truoc_nha`
- `Criteria_Noi_that`
- `Criteria_Thang_may`
- `Criteria_Loai_ngo`
- `Criteria_Khoang_cach_bai_do_xe`
- `Criteria_Kinh_doanh_Dong_tien`
- `Criteria_Huong_nha`
- `Criteria_Khoang_cach_duong_oto`
- `Last updated` (Cột ngày cập nhật cuối cùng đứng trước các cột ảnh)
- `Ảnh 1` đến `Ảnh N` (Rã từ chuỗi `images_metadata_json` của Custom ở đuôi sheet, tự động sinh thêm cột trên sheet Public)

## 📋 Proposed Changes

### [Component: Configuration (settings)]

#### [MODIFY] [settings.json](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/settings.json)
*   Bổ sung 3 Spreadsheet ID rỗng của hệ thống Pool2:
    ```json
    "pool2_raw_sheet_id": "",
    "pool2_custom_sheet_id": "",
    "pool2_public_sheet_id": "",
    ```

### [Component: Business Logic & Google Sheets Integration (pool_lego)]

#### [MODIFY] [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py)
*   **Khai báo danh sách tiêu đề chuẩn cho các sheet**:
    *   `RAW_LISTINGS_HEADERS`: Danh sách các cột thuộc `listings_v2` SQLite (bao gồm cả `raw_images_tk_json` và `raw_drive_images_json`).
    *   `CUSTOM_HEADERS`: Các cột thuộc `listings_custom_v2` SQLite.
    *   `PUBLIC_WHITELIST_HEADERS_BASE`:
        Danh sách các cột cơ bản được PO phê duyệt, đặt `Last updated` trước toàn bộ các cột ảnh:
        ```python
        PUBLIC_WHITELIST_HEADERS_BASE = [
            "System_ID",
            "Ma_Khang_Ngo",
            "Tieu_De_Public",
            "Mo_ta_Public",
            "Gia_Public",
            "Trang_Thai_Giao_Dich",
            "Ngu_Tret",
            "CHDV",
            "Trang_Thai_KN",
            "Ten_Duong",
            "Quan",
            "Phuong",
            "Duong",
            "bedrooms",
            "restrooms",
            "minimumRoadWidth",
            "DT_Thuc_te",
            "DT_Tren_so",
            "So_Tang",
            "Mat_Tien",
            "Chieu_dai",
            "Huong",
            "Criteria_Duong_truoc_nha",
            "Criteria_Noi_that",
            "Criteria_Thang_may",
            "Criteria_Loai_ngo",
            "Criteria_Khoang_cach_bai_do_xe",
            "Criteria_Kinh_doanh_Dong_tien",
            "Criteria_Huong_nha",
            "Criteria_Khoang_cach_duong_oto",
            "Last updated"
        ]
        ```
*   **Hàm helper `build_row_data(headers, data_dict)`**:
    *   Hàm phân giải chỉ số cột động: Nhận mảng headers thực tế từ sheet và `data_dict` dữ liệu, trả về mảng 1 dòng dữ liệu đã map đúng vị trí header.
*   **Hàm `publish_listing(tk_id, get_google_credentials, load_config, add_log_message, db_file=None)`**:
    *   *Nếu là Pool2*:
        1. **Tự khởi tạo dữ liệu Custom nếu chưa có**:
           - Truy vấn SQLite kiểm tra sự tồn tại của `System_ID` trong `listings_custom_v2`.
           - Nếu chưa tồn tại, tự động lấy dữ liệu thô từ `listings_v2` và lọc danh sách ảnh an toàn (loại trừ `facade` và `diagram`) để INSERT một dòng custom mặc định vào SQLite `listings_custom_v2`.
        2. **Đồng bộ File 1 Raw (`Pool2_Listings_Raw`)**:
           - **Tab Listings**: Đọc từ SQLite `listings_v2` (trong đó các cột ảnh thô đã được gom gọn dưới dạng chuỗi JSON `raw_images_tk_json` và `raw_drive_images_json`). Tìm kiếm `tk_id` ở cột `tk_id` trên sheet. Nếu thấy, cập nhật chép đè; nếu chưa, chèn dòng mới.
        3. **Đồng bộ File 2 Custom (`Pool2_Custom`)**:
           - **Tab Custom**: Đọc từ SQLite `listings_custom_v2`. Tìm kiếm `System_ID` ở cột `System_ID` trên sheet. Nếu thấy, cập nhật; nếu chưa, chèn dòng mới.
        4. **Đồng bộ File 3 Public (`Pool2_Public`)**:
           - **Tab Public**: Đọc từ dữ liệu Custom và mảng ảnh an toàn `images_metadata_json`.
           - **Tự động chèn thêm cột ảnh ở đuôi sheet**: Nếu số lượng ảnh an toàn là `N`, kiểm tra xem trong headers của sheet Public đã có đủ các cột `Ảnh 1` đến `Ảnh N` (nằm ở đuôi, sau cột `Last updated`) chưa. Nếu thiếu cột nào (ví dụ thiếu `Ảnh 16`), hệ thống sẽ tự động gửi API chèn thêm cột tiêu đề mới vào đuôi sheet và cập nhật lại mảng `headers`.
           - Ánh xạ các trường whitelist, rã ảnh thành các cột `Ảnh X`. Tìm kiếm `System_ID` ở cột `System_ID` trên sheet. Nếu thấy, cập nhật; nếu chưa, chèn dòng mới.
        5. **Cập nhật trạng thái**: Đánh dấu `status = 'published'` và cập nhật `Last_Sync` trong SQLite.
    *   *Nếu là Pool1*: Giữ nguyên luồng đồng bộ thô lên sheet Pool đơn như cũ để bảo đảm tương thích ngược 100%.

### [Component: Server Application (manager)]

#### [MODIFY] [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py)
*   **Cập nhật `DEFAULT_CONFIG`**:
    *   Bổ sung 3 Spreadsheet ID mặc định rỗng vào `DEFAULT_CONFIG` để nếu file settings.json được tạo mới hoặc reset, các khóa cấu hình này sẽ tự động xuất hiện.

---

## 📝 Task Checklist (TODO)

- [ ] **Thiết kế & Khảo sát:**
  - [ ] Đọc hiểu logic đồng bộ Google Sheets cũ trong `pool_lego.py`.
  - [ ] Chuẩn bị và tạo 3 Spreadsheet ID trống trên tài khoản Google Drive.
- [ ] **Triển khai Code:**
  - [ ] Thêm các Spreadsheet ID của Pool2 vào `settings.json`.
  - [ ] Implement luồng đồng bộ thô lên File 1 Raw trong `pool_lego.py` đọc từ `curated_config_json`.
  - [ ] Implement luồng ghi nhận Custom và ảnh an toàn lên File 2 Custom.
  - [ ] Implement luồng trích chọn whitelist cột và rã ảnh JSON sang File 3 Public.
  - [ ] Cập nhật cột `curated_config_json` (chứa toàn bộ ảnh và vai trò) để bảo toàn ảnh Admin tự thêm thủ công và phân loại vai trò.
  - [ ] Tích hợp tính năng tự động mở rộng cột ảnh `Ảnh 1..N` ở đuôi cho sheet Public (sau cột `Last updated`).
- [ ] **Kiểm thử cục bộ:**
  - [ ] Viết script test `scratch/test_pool2_publishing.py` chạy thử luồng đồng bộ 3 sheet và xác nhận dữ liệu đã được làm sạch chính xác, không chứa thông tin nhạy cảm.

---

## Verification Plan

### Automated Tests
- Chạy biên dịch kiểm tra lỗi cú pháp: `python -m py_compile pool_lego.py manager.py`.
- Viết kịch bản kiểm thử tự động tại [scratch/test_pool2_publishing.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_pool2_publishing.py) thực thi luồng publish giả lập lên 3 file Google Sheets ảo để xác minh:
  - Cấu trúc tiêu đề tự động sinh ra đầy đủ khi sheet trống.
  - Phân tách và đồng bộ thành công sang 3 Spreadsheet ID khác nhau.
  - Đồng bộ trường `curated_config_json` dạng JSON chuẩn xác trên tab Listings, không tạo ra các dòng lặp.
  - Tự động chèn thêm tiêu đề `Ảnh X` ở đuôi sheet (sau cột `Last updated`).
  - File 3 Public không chứa số nhà thật, không chứa ảnh mặt tiền/sơ đồ và rã ảnh an toàn thành các cột độc lập.

### Manual Verification
1. Cấu hình 3 Spreadsheet ID thực tế của Pool2 trong `settings.json`.
2. Bấm **Publish** một căn từ giao diện Web Admin.
3. Kiểm tra File 1 Raw: tab Listings có thông tin thô và chuỗi curated_config_json chứa toàn bộ ảnh.
4. Kiểm tra File 2 Custom: tab Custom có thông tin thô mặc định, SĐT chủ/đầu chủ, note nội bộ và `images_metadata_json` chứa ảnh nội thất/hẻm (cấm mặt tiền/sơ đồ).
5. Kiểm tra File 3 Public: chỉ chứa các trường whitelist, tên đường không có số nhà, ảnh rã từ 1 đến N ở sau cột `Last updated`, cột tự động giãn.
6. Mở link công khai khách xem và xác nhận trang web tải mượt mà danh sách ảnh an toàn từ File 3 Public.

## Files touched
- `settings.json` — Cấu hình các Spreadsheet ID.
- `pool_lego.py` — Chứa logic publish và rã cột.
- `manager.py` — API endpoint kích hoạt xuất bản.
- `docs/stories/_inbox/US-089B_pool2_cloud_publishing.md` — User Story.
