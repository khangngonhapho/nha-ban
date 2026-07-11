# Tài liệu Đặc tả Kỹ thuật - Phân hệ dữ liệu Next.js Proptech Thiên Khôi (Phiên bản 2 - Pool2)

Tài liệu này ghi nhận đặc tả kỹ thuật, cấu trúc API mới và sơ đồ ánh xạ dữ liệu quan hệ hoàn chỉnh của hệ thống **Pool2** (SQLite và Google Sheets Version 2) nhằm lưu trữ trọn vẹn thông tin cào được từ backend API Next.js Proptech Thiên Khôi mới (`backend.thienkhoi.com`).

---

## 🌐 1. Hệ thống Endpoint API
Dữ liệu được lấy trực tiếp thông qua các REST API của Thiên Khôi:
- **Xác thực**: `GET https://backend.thienkhoi.com/auth/v1/users/me`
- **Gia hạn token**: `POST https://backend.thienkhoi.com/auth/v1/auth/refresh-token`
- **Lấy chi tiết căn**: `GET https://backend.thienkhoi.com/product/v1/property/<UUID>`

---

## 💾 2. Độc lập Lưu trữ và Bảo mật Nhiều Lớp (Secure Storage & Isolation)

Để đáp ứng chính sách bảo mật thông tin tối nghiêm của dự án và ngăn ngừa tuyệt đối mọi rủi ro rò rỉ dữ liệu định danh nhạy cảm (PII) hoặc địa chỉ thật ra môi trường công khai, hệ thống Pool2 thiết lập cơ chế lưu trữ phân tách nhiều lớp:

### 2.1. Phân tách CSDL SQLite Local
*   **CSDL SQLite riêng**: Sử dụng tệp tin database riêng biệt **`raw_archive_v2.db`** (không dùng chung `raw_archive.db` của Pool1).

### 2.2. Phân tách Google Sheets Đa Quyền Hạn (3 Tệp Tin Độc Lập)
Tuyệt đối không gộp chung dữ liệu nhạy cảm và dữ liệu công khai trên cùng một tệp bảng tính. Hệ thống sử dụng **3 file Google Spreadsheet hoàn toàn riêng biệt** với các Spreadsheet ID và quyền chia sẻ (Sharing Permissions) khác nhau:

1.  **File 1: `Pool2_Listings_Raw` (Lưu trữ thô)**
    *   *Mục đích*: Lưu trữ thông tin thô cào về và catalog ảnh thô đầy đủ (kể cả mặt tiền, sơ đồ).
    *   *Phân quyền*: **Riêng tư (Private)**. Chỉ chủ tài khoản Admin và ứng dụng Python được truy cập.
    *   *ID cấu hình*: `"pool2_raw_sheet_id"` (trong `settings.json`).
    *   *Các Tab bên trong*: `Listings` (metadata văn bản) và `Images` (danh sách ảnh dạng dòng).
2.  **File 2: `Pool2_Custom` (Bản biên tập tùy biến)**
    *   *Mục đích*: Nơi anh Khang Ngô trực tiếp chỉnh sửa địa chỉ thật, số nhà, giá public, note nội bộ, v.v., đồng thời lưu giữ thông tin thuộc tính công khai và danh sách ảnh an toàn đã lọc.
    *   *Phân quyền*: **Nội bộ giới hạn (Restricted)**. Chỉ chia sẻ cho nhóm cộng sự quản lý giỏ hàng của Khang Ngô Nhà Phố.
    *   *ID cấu hình*: `"pool2_custom_sheet_id"` (trong `settings.json`).
    *   *Các Tab bên trong*: `Custom` (chứa dữ liệu tùy biến bao gồm cả `images_metadata_json` chỉ chứa ảnh nội thất, hẻm, ảnh nền, loại bỏ mặt tiền và sơ đồ).
3.  **File 3: `Pool2_Public` (Bản hiển thị công khai)**
    *   *Mục đích*: Làm kho dữ liệu sạch đã làm sạch PII hiển thị trực tiếp lên trang Web Client cho khách hàng.
    *   *Phân quyền*: **Công khai (Anyone with link can view)** để Web Client load được dữ liệu JSONP.
    *   *ID cấu hình*: `"pool2_public_sheet_id"` (trong `settings.json`).
    *   *Các Tab bên trong*: `Public` (chứa dữ liệu an toàn đã lọc sạch số nhà thật, SĐT chủ/đầu chủ, note nội bộ. Tab này **chỉ được đồng bộ bằng cách trích chọn các cột công khai được chỉ định từ File 2 Custom** và rã chuỗi ảnh an toàn thành các cột Ảnh 1-15).

---

## 🗃️ 3. Sơ đồ Cấu trúc SQLite Version 2 (Relational Database Schema)

### Bảng 1: `listings_v2` (Lưu thông tin căn hộ và các trường thuộc tính/metadata)
Bảng này chứa toàn bộ trường thô cào được từ API gốc cùng với các trường phân tích tiêu chí chi tiết (`criteria`):

| Cột SQLite | Kiểu dữ liệu | Đường dẫn JSON gốc / Ghi chú |
| :--- | :--- | :--- |
| `tk_id` | TEXT PRIMARY KEY | ID UUID của Thiên Khôi (ví dụ: `4f92db9e-...`) |
| `status` | TEXT | Trạng thái xử lý trong hệ thống (`raw_text`, `raw_complete`, `published`) |
| `System_ID` | TEXT | Mã System ID tự sinh (ví dụ: `SYS-20260611-123`) |
| `Ma_Hang` | TEXT | Mã hàng hiển thị Thiên Khôi (`code`, ví dụ: `TKQLMB8Q`) |
| `isSigned` | TEXT | Trạng thái ký hợp đồng (`true` / `false`) |
| `status_nguon` | TEXT | Trạng thái nguồn (`status`, ví dụ: `qualified`) |
| `commissionAgent` | TEXT | Hoa hồng chia cho đại lý |
| `ownerSideUserId` | TEXT | ID của Đầu chủ |
| `certificateSeries` | TEXT | Ký hiệu bản vẽ/sổ đỏ (`certificateSeries`) |
| `latitude` | TEXT | Vĩ độ định vị GPS |
| `longitude` | TEXT | Kinh độ định vị GPS |
| `placeName` | TEXT | Địa chỉ đầy đủ từ hệ thống (`placeName`) |
| `streetName` | TEXT | Tên đường thật (`streetName`) |
| `Quan` | TEXT | Tên quận (`district.name`) |
| `Phuong` | TEXT | Tên phường (`ward.name`) |
| `Ngo_So_nha` | TEXT | Số nhà / ngõ hẻm (`address`) |
| `bedrooms` | TEXT | Số phòng ngủ (`bedrooms`) |
| `restrooms` | TEXT | Số nhà vệ sinh (`restrooms`) |
| `balconies` | TEXT | Số ban công |
| `sidewalk` | TEXT | Có vỉa hè hay không |
| `behindOpenSpace` | TEXT | Khoảng trống phía sau |
| `sideOpenSpace` | TEXT | Khoảng trống bên hông |
| `minimumRoadWidth` | TEXT | Độ rộng đường trước nhà (`minimumRoadWidth`) |
| `createdAt` | TEXT | Ngày tạo nguồn hàng |
| `updatedAt` | TEXT | Ngày cập nhật nguồn hàng |
| `commissionType` | TEXT | Loại hoa hồng (`percentage` / `fixed`) |
| `commissionValue` | TEXT | Giá trị hoa hồng |
| `isDispute` | TEXT | Tranh chấp hay không |
| `createdAtSigned` | TEXT | Ngày ký hợp đồng chính thức |
| `CCCD_Dau_Chu` | TEXT | CCCD của Đầu chủ (`ownerSideUser.numberId`) |
| `Kenh_tin_TK` | TEXT | Danh sách kênh đăng tin (`channels`) |
| `The_tags_TK` | TEXT | Danh sách thẻ tag (`tags`) |
| `Noi_dung_chinh` | TEXT | Nội dung tóm tắt tự động |
| `Mo_ta_chi_tiet` | TEXT | Bài mô tả chi tiết của đầu chủ |
| `Gia_chao` | TEXT | Giá chào gốc (`offeringPrice` đơn vị tỷ) |
| `DT_Thuc_te` | TEXT | Diện tích thực tế (`actualArea`) |
| `DT_Tren_so` | TEXT | Diện tích trên sổ (`area`) |
| `So_Tang` | TEXT | Số tầng (`floors`) |
| `Mat_Tien` | TEXT | Độ rộng mặt tiền (`wide`) |
| `Chieu_dai` | TEXT | Chiều sâu của đất (`depth`) |
| `Huong` | TEXT | Hướng nhà (`direction`) |
| `Ten_Chu_Nha` | TEXT | Tên chủ nhà (ghép từ `homeOwner`) |
| `Dien_thoai_1` | TEXT | SĐT chủ nhà công khai (`contactPhoneNumber`) |
| `Ten_Dau_Chu` | TEXT | Tên Đầu chủ (`ownerSideUser.name`) |
| `Dien_thoai_Dau_Chu` | TEXT | SĐT Đầu chủ (`ownerSideUser.phone`) |
| `Diem_Facebook` | TEXT | FB của Đầu chủ (`ownerSideUser.fbLink`) |
| `Link_Goc` | TEXT | Link gốc trên Proptech |
| `Last_Crawl` | TEXT | Thời gian cào cuối cùng |
| `Last_Sync` | TEXT | Thời gian xuất bản cuối cùng |
| `Criteria_Tiem_nang_Rui_ro` | TEXT | Nhóm tiêu chí `PROPERTY_CRITERIA` |
| `Criteria_Duong_truoc_nha` | TEXT | Nhóm tiêu chí `ROAD_TYPE` |
| `Criteria_Loai_BDS` | TEXT | Nhóm tiêu chí `PROPERTY_TYPE` |
| `Criteria_Giay_to_phap_ly` | TEXT | Nhóm tiêu chí `LEGAL_DOCUMENT` |
| `Criteria_Hinh_dang_dat` | TEXT | Nhóm tiêu chí `LAND_PLOT_SHAPE` |
| `Criteria_Tinh_trang_xay_dung`| TEXT | Nhóm tiêu chí `CONSTRUCTION_STATUS` |
| `Criteria_Cau_truc_nha` | TEXT | Nhóm tiêu chí `HOUSE_STRUCTURE` |
| `Criteria_Noi_that` | TEXT | Nhóm tiêu chí `INTERIOR` |
| `Criteria_Thang_may` | TEXT | Nhóm tiêu chí `ELEVATOR` |
| `Criteria_Loai_ngo` | TEXT | Nhóm tiêu chí `ALLEY_TYPE` |
| `Criteria_Vi_tri_tinh_thue` | TEXT | Nhóm tiêu chí `TAX_CALCULATION_POSITION` |
| `Criteria_Mat_thoang` | TEXT | Nhóm tiêu chí `OPEN_SPACE` |
| `Criteria_Khoang_cach_bai_do_xe` | TEXT | Nhóm tiêu chí `DISTANCE_TO_PARKING_LOT` |
| `Criteria_Kinh_doanh_Dong_tien` | TEXT | Nhóm tiêu chí `PROPERTY_CRITERIA_BUSINESS_CASH_FLOW` |
| `Criteria_Tien_ich` | TEXT | Nhóm tiêu chí `PROPERTY_CRITERIA_FACILITIES` |
| `Criteria_Phong_thuy` | TEXT | Nhóm tiêu chí `PROPERTY_CRITERIA_GEOMANCY` |
| `Criteria_Huong_nha` | TEXT | Nhóm tiêu chí `HOUSE_DIRECTION` |
| `Criteria_Vi_tri_trong_ngo` | TEXT | Nhóm tiêu chí `POSITION_IN_ALLEY` |
| `Criteria_Khoang_cach_duong_oto` | TEXT | Nhóm tiêu chí `DISTANCE_TO_MAIN_ROAD` |

### Bảng 2: `listings_images` (Lưu thông tin danh sách hình ảnh)
Mỗi hàng đại diện cho một bức ảnh liên kết bằng khóa ngoại và lưu vết tài khoản thực hiện biên tập:

| Cột SQLite | Kiểu dữ liệu | Ghi chú |
| :--- | :--- | :--- |
| `id` | INTEGER | Khóa chính tự tăng |
| `tk_id` | TEXT | Khóa ngoại liên kết tới `listings_v2.tk_id` |
| `image_url` | TEXT | URL hình ảnh thô trên CDN của Thiên Khôi |
| `cloudinary_url` | TEXT | URL hình ảnh sau khi upload CDN Cloudinary của Khang Ngô |
| `role` | TEXT | Vai trò: `facade` (mặt tiền), `cover` (ảnh nền), `interior` (nội thất), `alley` (hẻm), `diagram` (sổ/sơ đồ) |
| `sequence_index` | INTEGER | Thứ tự hiển thị sắp xếp |
| `edited_by` | TEXT | Email/Google Account của Admin thực hiện biên tập ảnh này (Nhật ký sửa đổi) |

### Bảng 3: `listings_custom_v2` (Lưu thông tin tùy biến của Admin)
Bảng này lưu trữ dữ liệu tùy biến hoặc ghi chú đặc thù do anh Khang tự ghi nhận/nhập form, đồng thời lưu giữ thông tin thuộc tính công khai và ảnh an toàn để làm nguồn xuất bản trực tiếp cho File Public:

| Cột SQLite | Kiểu dữ liệu | Ý nghĩa |
| :--- | :--- | :--- |
| `System_ID` | TEXT PRIMARY KEY | Khóa chính (so khớp đồng bộ) |
| `Ma_Khang_Ngo` | TEXT | Mã số nhà riêng của Khang Ngô |
| `Dia_Chi_That` | TEXT | Địa chỉ thật (số nhà + đường thật) |
| `So_Nha` | TEXT | Số nhà thật |
| `Ten_Duong` | TEXT | Tên đường thật |
| `Gia_Public` | TEXT | Giá bán công khai hiển thị cho khách |
| `Tieu_De_Public` | TEXT | Tiêu đề tùy biến hiển thị trên web |
| `Mo_ta_Public` | TEXT | Bài mô tả tùy biến hiển thị trên web |
| `Note_Noi_Bo` | TEXT | Ghi chú nội bộ nhạy cảm (ẩn đối với khách) |
| `Trang_Thai_Giao_Dich` | TEXT | Tình trạng (`Đang bán`, `Đặt cọc`, `Đã bán`, `Invisible`) |
| `Quan` | TEXT | Tên quận công khai |
| `Phuong` | TEXT | Tên phường công khai |
| `DT_Tren_so` | TEXT | Diện tích công nhận trên sổ |
| `So_Tang` | TEXT | Số tầng của nhà |
| `Mat_Tien` | TEXT | Chiều ngang/Mặt tiền (m) |
| `Huong` | TEXT | Hướng nhà |
| `Duong_truoc_nha_m` | TEXT | Độ rộng hẻm trước nhà (m) |
| `Loai_BDS` | TEXT | Loại hình bất động sản / Phân loại hẻm |
| `Ngu_Tret` | TEXT | Có ngủ trệt hay không (`Y` / `N`) |
| `CHDV` | TEXT | Có phải CHDV hay không (`Y` / `N`) |
| `Trang_Thai_KN` | TEXT | Trạng thái hiển thị nội bộ trên hệ thống Khang Ngô (`Active`, `Sold`, `Invisible`, v.v.) |
| `images_metadata_json` | TEXT | Chuỗi JSON chứa mảng các đối tượng ảnh an toàn. **Chỉ được phép chứa ảnh có vai trò `interior`, `alley`, hoặc `cover` (nội thất, hẻm, nền). Nghiêm cấm ảnh `facade` (mặt tiền) và `diagram` (sổ/sơ đồ).** |

---

## 📊 4. Cấu trúc Google Sheets Version 2 (3 File Tách Biệt)

### File 1: `Pool2_Listings_Raw` (ID: `"pool2_raw_sheet_id"`)
*   **Tab `Listings`**: Gồm các cột metadata văn bản tương đương bảng `listings_v2`.
*   **Tab `Images`**: Gồm các cột: `System ID`, `Mã Hàng`, `Image URL`, `Role`, `Sequence`, `Edited By` (lưu vết tài khoản).

### File 2: `Pool2_Custom` (ID: `"pool2_custom_sheet_id"`)
*   **Tab `Custom`**: Gồm các cột tương đương bảng `listings_custom_v2` để anh Khang tự chỉnh sửa địa chỉ và ghi chú.

### File 3: `Pool2_Public` (ID: `"pool2_public_sheet_id"`)
*   **Tab `Public`**: Gồm các cột thông tin đã làm sạch hoàn chỉnh, gộp và đồng bộ ở phía server-side để phục vụ Web Client.

---

## 🔒 5. Quy định Bảo mật Hình ảnh và Lọc Cột (Image Isolation & Column Filtering)

### 5.1. Bộ lọc hình ảnh trong File Custom (`Pool2_Custom`)
Để bảo vệ tối đa hình ảnh nhạy cảm pháp lý (sổ đỏ) và nhận diện căn nhà (mặt tiền) khỏi nhân viên vận hành thông thường hoặc các luồng truy cập chưa phân quyền:
*   Ô `images_metadata_json` trên **File 2 (`Pool2_Custom`)** **CHỈ** được phép chứa danh sách các ảnh có vai trò là:
    -   `interior` (Ảnh nội thất)
    -   `alley` (Ảnh ngõ hẻm xung quanh)
    -   `cover` (Ảnh nền/ảnh đại diện)
*   **CẤM TUYỆT ĐỐI** đưa ảnh có vai trò là `facade` (Mặt tiền thật) hoặc `diagram` (Sơ đồ thửa đất/Sổ đỏ) vào trường dữ liệu của File Custom này.
*   *Vị trí lưu trữ duy nhất của ảnh mặt tiền và sơ đồ thô*: Chỉ nằm trong SQLite local (`listings_images`) và File 1 (`Pool2_Listings_Raw` - Private).

### 5.2. Nguyên tắc lọc cột an toàn cho File Public (`Pool2_Public`)
Để đảm bảo tính bảo mật tối đa, File Public **chỉ được phép trích xuất dữ liệu từ các cột của File Custom (`Pool2_Custom`)** dựa trên nguyên tắc **White-list (Chỉ cho phép các cột an toàn)**. Hệ thống tuyệt đối không thực hiện gộp trực tiếp từ File Raw (`Pool2_Listings_Raw`) sang File Public để ngăn chặn triệt để mọi rủi ro rò rỉ dữ liệu thô.
*   **Các cột ĐƯỢC PHÉP đồng bộ sang `Pool2_Public` (lấy từ `Pool2_Custom`)**:
    -   `System_ID` (Khóa định danh hệ thống)
    -   `Mã Khang Ngô (ID)` (Mã định danh công khai gửi khách)
    -   `Tiêu đề Public`, `Mô tả Public` (Đã được biên tập AI/Admin sạch sẽ)
    -   `Giá Public` (Giá bán công khai hiển thị cho khách)
    -   `Quận`, `Phường`, `Tên Đường` (Thông tin quận phường đường công khai - CẤM số nhà)
    -   `Diện tích` (lấy từ cột `DT_Tren_so` của Custom)
    -   `Số Tầng` (lấy từ cột `So_Tang` của Custom)
    -   `Mặt Tiền` (lấy từ cột `Mat_Tien` của Custom)
    -   `Hướng` (lấy từ cột `Huong` của Custom)
    -   `Đường trước nhà (m)` (lấy từ cột `Duong_truoc_nha_m` của Custom)
    -   `Loại hình` (lấy từ cột `Loai_BDS` của Custom)
    -   `Ảnh 1` đến `Ảnh 15` (Rã từ chuỗi `images_metadata_json` của Custom. Do Custom đã được lọc sạch ảnh mặt tiền và sơ đồ, nên danh sách ảnh này tuyệt đối an toàn).
    -   `Last updated` (Thời điểm cập nhật cuối)
*   **Các cột trong Custom CẤM TUYỆT ĐỐI xuất hiện trên `Pool2_Public`**:
    -   `Số Nhà` (Số nhà thật của căn nhà)
    -   `Địa Chỉ Thật` (Số nhà + tên đường thật)
    -   `Note Nội Bộ` (Ghi chú riêng tư)

### 5.3. Thêm hình ảnh tùy biến từ Web Admin
Hệ thống cho phép Admin trực tiếp đăng tải hoặc thêm hình ảnh tùy biến vào kho hình của căn nhà thông qua giao diện Web Admin. Quy trình lưu trữ và cách ly như sau:
1.  **Tải lên & Lưu kho gốc (Raw storage)**: Ảnh upload từ Web Admin sẽ được đưa lên Cloudinary để lấy CDN URL. Bản ghi ảnh chi tiết được thêm trực tiếp vào bảng `listings_images` trong SQLite cục bộ (với nhãn `role` tương ứng và ghi vết tài khoản thực hiện trong `edited_by`) và đẩy vào tab `Images` của **File 1 (`Pool2_Listings_Raw`)** (chứa trọn vẹn toàn bộ kho hình gốc).
2.  **Đồng bộ có lọc vào File Custom (File 2) và File 1 Raw**:
    -   Nếu ảnh tự thêm có vai trò là ảnh an toàn (`interior`, `alley`, `cover`), hệ thống tự động cập nhật, append liên kết ảnh mới vào chuỗi `images_metadata_json` trong SQLite (cả bảng `listings_custom_v2` và `listings_v2`), đồng thời cập nhật ghi nhận trực tiếp vào ô tương ứng trên tab Custom của **File 2 (`Pool2_Custom`)** và tab Listings của **File 1 (`Pool2_Listings_Raw`)**.
    -   Nếu ảnh tự thêm có vai trò là ảnh nhạy cảm (`facade` hoặc `diagram`), ảnh **chỉ** được lưu tại kho gốc (SQLite `listings_images` và File 1 tab `Images`), tuyệt đối không chèn vào `images_metadata_json` của File 2 và File 1 Listings.

### 5.4. Giải pháp hiệu chỉnh thông tin cào thô bị sai (ví dụ: Tên Phường)
Khi thông tin cào thô từ API gốc bị sai lệch (ví dụ: tên Phường, Quận, Đường bị sai trên hệ thống Thiên Khôi):
1.  **Cơ chế Override (Ghi đè bảo vệ)**:
    -   Admin chỉnh sửa trực tiếp thông tin bị sai trên giao diện Web Admin hoặc trên tab Custom của **File 2 (`Pool2_Custom`)** (cột `Phuong`, `Quan`, `Ten_Duong`, v.v.).
    -   Các hiệu chỉnh này sẽ được lưu đè vào bảng `listings_custom_v2` trong SQLite cục bộ và tab Custom của File 2.
2.  **Xuất bản dữ liệu sạch**:
    -   Vì File 3 Public (`Pool2_Public`) được xuất bản bằng cách trích chọn các cột whitelist **chỉ từ File 2 Custom**, nên thông tin đúng đã hiệu chỉnh sẽ tự động được đưa lên File Public phục vụ website hiển thị cho khách hàng.
    -   Mọi hành động recrawl (cào lại) dữ liệu sau đó sẽ chỉ cập nhật vào File 1 Raw, hoàn toàn **không bao giờ ghi đè** lên các thông tin đã được sửa đổi thủ công trên File 2 Custom, đảm bảo an toàn tuyệt đối và bảo toàn vết sửa đổi của Admin.

### 5.5. Giải pháp chống lệch chỉ số cột và lỗi hồi quy khi mở rộng schema trong tương lai
Để giải quyết triệt để rủi ro nhầm index cột khi bổ sung/thay đổi cấu trúc cột Google Sheets trong tương lai, hệ thống áp dụng thiết kế động hoàn toàn:
1.  **Cấm tuyệt đối hardcode chỉ số cột (Dynamic Index Mapping)**:
    -   Trong mã nguồn Python (`pool_lego.py`) và Apps Script, mọi thao tác đọc/ghi cột đều không dùng số thứ tự cố định (như `row[15]`). Hệ thống sử dụng dòng tiêu đề đầu tiên để xây dựng bản đồ chỉ số động `HeaderMap` theo thời gian thực (ví dụ: `idx = header_row.index("Phường")`).
    -   Nếu người dùng chèn thêm cột, đổi chỗ cột hoặc xóa cột không dùng, bản đồ này tự động tính toán lại chỉ số tại runtime, ngăn ngừa 100% lỗi hồi quy ghi lệch dữ liệu.
2.  **Whitelist thuộc tính công khai có thể ghi đè (Public Metadata Whitelist)**:
    -   Hệ thống định nghĩa danh sách các trường thông tin cào thô được phép sao chép sang Custom dưới dạng mảng cấu hình: `PUBLIC_METADATA_WHITELIST = ["Quận", "Phường", "Đường", "DT Trên sổ", "Số Tầng", "Mặt Tiền", "Hướng", "Đường trước nhà (m)", "Loại hình"]`.
    -   Trong tương lai, nếu cần cho phép sửa đổi thêm cột mới (ví dụ: "Năm xây dựng" hoặc "Pháp lý"), Admin chỉ cần:
        1. Thêm cột tương ứng vào Google Sheet File 1 (Raw Listings) và File 2 (Custom).
        2. Thêm tên tiêu đề cột đó vào mảng `PUBLIC_METADATA_WHITELIST` trong file cấu hình.
    -   Hệ thống sẽ tự động nhận diện, sao chép mặc định từ Raw sang Custom, cho phép Admin sửa đổi trên Custom và xuất bản sang Public mà không cần viết lại bất kỳ dòng logic gộp cột nào.
3.  **Tự động nâng cấp SQLite (SQLite Auto-Migration)**:
    -   Hàm khởi tạo database `init_db()` trong `pool_lego.py` sử dụng mảng `PUBLIC_METADATA_WHITELIST` để đối chiếu với cấu trúc bảng SQLite cục bộ hiện tại.
    -   Nếu phát hiện whitelist bổ sung trường mới chưa có trong SQLite, hệ thống tự động sinh và chạy câu lệnh `ALTER TABLE ADD COLUMN` để nâng cấp database local ngay khi khởi động app, bảo trì tính đồng bộ hoàn hảo giữa SQLite và Google Sheets.

### 5.6. Luồng Tự động Mở rộng Schema (Dynamic Schema Extension Pipeline)
Để tránh rủi ro người dùng thực hiện không đồng bộ (ví dụ: chỉ sửa trên Google Sheet mà quên cấu hình whitelist hoặc SQLite, dẫn đến lỗi hệ thống), hệ thống cung cấp một tính năng tự động hóa trọn gói để mở rộng thuộc tính mới:
1.  **API/CLI Endpoint**: Cung cấp API `POST /api/schema/add-column` (hoặc lệnh CLI `python pool_lego.py --action add-column`).
    -   *Tham số đầu vào*:
        ```json
        {
          "column_name": "Tên Cột Mới",
          "data_type": "TEXT",
          "is_public_whitelist": true,
          "description": "Mô tả ngắn"
        }
        ```
2.  **Quy trình Thực thi Tự động hóa (Atomic Execution Flow)**:
    -   **Bước 1: Cập nhật cấu hình**: Tự động chèn `"Tên Cột Mới"` vào mảng `PUBLIC_METADATA_WHITELIST` trong file cấu hình `settings.json`.
    -   **Bước 2: Nâng cấp SQLite cục bộ**: Tự động kết nối `raw_archive_v2.db` và thực hiện `ALTER TABLE listings_v2 ADD COLUMN ...` cùng `ALTER TABLE listings_custom_v2 ADD COLUMN ...`.
    -   **Bước 3: Mở rộng Google Sheets trực tuyến**: Gọi API Google Sheets chèn thêm cột mới vào cuối cùng của dòng tiêu đề trên:
        -   File 1 Raw (`Pool2_Listings_Raw` tab Listings)
        -   File 2 Custom (`Pool2_Custom` tab Custom)
        -   File 3 Public (`Pool2_Public` tab Public - nếu `is_public_whitelist` là `true`).
    -   **Bước 4: Cập nhật tài liệu**: Tự động append dòng mô tả thuộc tính mới vào file tài liệu [docs/pool_sheet_schema.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/pool_sheet_schema.md) và [docs/data_dictionary.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/data_dictionary.md).
3.  **Lợi ích**: Toàn bộ quy trình mở rộng cột diễn ra đồng thời chỉ sau 1 click hoặc 1 câu lệnh CLI, loại bỏ hoàn toàn khả năng bất đồng bộ và lỗi vận hành.

---

## 🔄 6. Luồng Ghi nhận & Xuất bản An toàn
1.  **Cào tin**: `fetcher.py` cào từ API, lưu thô vào SQLite `listings_v2` và `listings_images` tại file `raw_archive_v2.db`, sau đó đẩy lên Google Sheet **File 1 (`Pool2_Listings_Raw`)** (chứa đầy đủ thông tin thô và toàn bộ ảnh thô bao gồm mặt tiền, sơ đồ).
2.  **Đồng bộ sang Custom**: Hệ thống tự động sao chép các thông tin metadata công khai mặc định (Quận, Phường, Tên Đường, Diện tích, Số tầng, Mặt tiền, Hướng, Độ rộng hẻm, Loại hình) và danh sách ảnh an toàn đã lọc (chỉ lấy vai trò nội thất, hẻm, nền; loại trừ mặt tiền, sơ đồ) sang bảng `listings_custom_v2` trong SQLite và tab Custom của **File 2 (`Pool2_Custom`)**.
3.  **Biên tập Custom**: Anh Khang hoặc team Admin thực hiện gõ địa chỉ thật, số nhà, note nội bộ, giá public, tiêu đề public, mô tả public và duyệt thông tin trên Google Sheet **File 2 (`Pool2_Custom`)** (hoặc thông qua giao diện Web Admin).
4.  **Xuất bản Public**: Khi bấm **Publish**, `manager.py` đọc dữ liệu từ File 2 (`Pool2_Custom`), lọc lấy các cột thuộc White-list, rã mảng ảnh an toàn từ `images_metadata_json` thành các cột từ `Ảnh 1` đến `Ảnh 15`, sau đó ghi đè trực tiếp dòng dữ liệu sạch này sang Google Sheet **File 3 (`Pool2_Public`)**. Web Client của khách hàng chỉ đọc dữ liệu từ File 3, đảm bảo an toàn tuyệt đối.

---

## 🔄 7. Cơ chế Đồng bộ Dữ liệu Liên Database (Cross-Pool DB Synchronization)

Để đảm bảo tính nhất quán dữ liệu, tránh việc nhập liệu lặp lại và cho phép chạy song song hai phân hệ Pool1 và Pool2, hệ thống triển khai cơ chế đồng bộ hai chiều (hoặc chuyển đổi dữ liệu một chiều tự động) giữa hai tệp SQLite:

### 7.1. Nguyên tắc So khớp
Khóa so khớp chính giữa hai database là trường **`tk_id`** (UUID của Thiên Khôi) hoặc **`System_ID`** (Mã hệ thống Khang Ngô).

### 7.2. Luồng Đồng bộ Chi tiết

#### Chiều A: Từ Pool2 (Relational) sang Pool1 (Flattened)
Kích hoạt tự động khi một căn hộ được cập nhật hoặc xuất bản thành công trong Pool2.
1.  **Đọc dữ liệu Pool2**: Đọc metadata từ `listings_v2` và thông tin tùy biến từ `listings_custom_v2` tại file `raw_archive_v2.db`.
2.  **Đọc danh sách ảnh**: Truy vấn danh sách ảnh từ `listings_images` liên kết với căn nhà.
3.  **Làm phẳng dữ liệu ảnh (Flattening)**:
    *   Lọc ảnh có role là `interior` (tối đa 25 ảnh) và điền lần lượt vào các cột `Ảnh 1` đến `Ảnh 25` của Pool1.
    *   Lọc ảnh có role là `alley` (tối đa 10 ảnh) và điền lần lượt vào các cột `Hình Hẻm 1` đến `Hình Hẻm 10` của Pool1.
    *   Lọc ảnh có role là `diagram` (tối đa 5 ảnh) và điền lần lượt vào các cột `Sơ đồ thửa đất 1` đến `Sơ đồ thửa đất 5` của Pool1.
4.  **Ghi đè/Chèn mới**: Thực hiện câu lệnh SQL `INSERT OR REPLACE` hoặc `UPDATE` ghi dữ liệu đã làm phẳng vào bảng `listings` của file **`raw_archive.db`** (Pool1).

#### Chiều B: Từ Pool1 (Flattened) sang Pool2 (Relational)
Phục vụ di chuyển dữ liệu cũ từ Pool1 sang Pool2 hoặc đồng bộ ngược các căn gõ tay trên hệ thống Pool1.
1.  **Đọc dữ liệu Pool1**: Đọc dòng thông tin từ bảng `listings` của file `raw_archive.db`.
2.  **Ánh xạ metadata & Custom**:
    *   Tách các trường thông tin cào thô và đưa vào bảng `listings_v2` trong file `raw_archive_v2.db`.
    *   Tách các trường tùy biến (`Mã Khang Ngô`, `Tiêu đề Public`, `Mô tả Public`, `Giá Public`, `Note nội bộ`, `Trạng thái Public`) đưa vào bảng `listings_custom_v2` trong file `raw_archive_v2.db`.
3.  **Quan hệ hóa danh sách ảnh (Relationalization)**:
    *   Quét qua 25 cột ảnh, 10 cột hẻm, 5 cột sơ đồ của dòng dữ liệu Pool1.
    *   Với mỗi URL ảnh tìm thấy (không null/rỗng), tạo một bản ghi tương ứng chèn vào bảng `listings_images` trong file `raw_archive_v2.db` với nhãn `role` tương ứng (`interior`, `alley`, `diagram`) và chỉ số thứ tự `sequence_index`.

### 7.3. Công cụ Điều phối (Execution & Trigger)
*   **Đồng bộ ngầm (Background Sync)**: Tự động chạy trong hàm `pool_lego.publish_listing()` khi ở chế độ Pool2, tự cập nhật sang DB Pool1 để giữ dữ liệu local luôn đồng nhất.
*   **Lệnh đồng bộ hàng loạt (Bulk Sync CLI)**: Hỗ trợ lệnh chạy CLI qua python:
    ```bash
    python pool_lego.py --action sync-pool2-to-pool1
    python pool_lego.py --action sync-pool1-to-pool2
    ```
    Hoặc qua API endpoint `/api/sync-databases` trong `manager.py` để đồng bộ toàn bộ cơ sở dữ liệu khi cần thiết.
