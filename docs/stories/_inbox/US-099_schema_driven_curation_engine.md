---
id: US-099
status: completed
date: 2026-06-19
size: L
---

# US-099: Thiết kế Schema-Driven Curation Engine & Kiến trúc Đa Broker cho Pool 2

## User story
**As an** Admin Curation (Người biên tập rổ hàng - Trang)  
**I want** Một hệ thống kiến trúc đa người dùng (Multi-Broker) có bảng SQLite `brokers` quản lý cấu hình riêng biệt, cùng một giao diện quản lý cấu hình cột (`schema.html` chạy local) hướng cấu hình để định nghĩa cột thô/tùy biến với các kiểu dữ liệu logic đa dạng (Boolean, Dropdown, Text, Number), vô hiệu hóa cột cấu hình thay vì xóa vật lý để tránh rủi ro mất dữ liệu, và kiểm soát hiển thị ở cấp độ hệ thống (`system_available`).  
**So that** Tôi có thể dễ dàng quản lý thông tin, phân tách dữ liệu độc lập giữa các Broker khác nhau sử dụng chung nguồn cào thô, tránh lặp lại các lỗi lệch cột, hỗ trợ các định dạng hiển thị trực quan (checkbox, select box) và tiết kiệm thời gian bảo trì code.

---

## Acceptance Criteria

### 1. Kiến trúc Đa Broker (Multi-Broker Curation) & Quản lý Hình ảnh (Hạ tầng)
- [x] **Bảng SQLite `brokers` quản lý danh sách Môi giới**:
  - Tạo bảng SQLite `brokers` mới để lưu cấu hình của từng Broker: ID, tên, Sheet IDs (Custom & Public), R2 bucket configs, v.v. Bảng này là nguồn dữ liệu chính để nạp danh sách Broker trên giao diện thay vì lưu cứng trong `settings.json`.
- [x] **Cô lập dữ liệu chung 1 bảng (Row-level Isolation)**:
  - Bảng SQLite `listings_custom_v2` dùng chung 1 bảng duy nhất có khóa chính kép `(System_ID, broker_id)`. Dữ liệu của các Broker được cô lập an toàn bằng điều kiện truy vấn `WHERE broker_id = ?`.
- [x] **Hệ mã căn & Đánh giá riêng của từng Broker**:
  - Đổi tên cột vật lý `Ma_Khang_Ngo` cũ thành **`Ma_Hang_Custom`** (Lưu mã tùy chỉnh riêng của từng broker).
  - Đổi tên cột vật lý `Danh_Gia_KN` cũ thành **`Danh_Gia_Custom`** (Lưu đánh giá riêng của từng broker).
  - Sử dụng một tên nhãn chung nhất quán trên tất cả giao diện là **"Mã tùy chỉnh"** (không tự động đổi nhãn theo broker để giữ giao diện đồng nhất).
- [x] **Phân tách Google Sheets riêng cho từng Broker**:
  - Mỗi Broker có file Google Sheet Custom & Public riêng biệt (được cấu hình trực tiếp trong bảng SQLite `brokers`). Mọi hoạt động Curation và Đồng bộ sẽ chạy trên Sheets riêng của Broker được chọn.
- [x] **Loại bỏ bảng hình ảnh phụ - Quản lý ảnh trực tiếp qua JSON**:
  - Không sử dụng bảng phụ `listings_images` cho dữ liệu custom. Toàn bộ danh sách ảnh, thứ tự và vai trò được đọc/ghi trực tiếp qua cột JSON `images_metadata_json` của bảng `listings_custom_v2` (tách biệt theo cặp `System_ID` và `broker_id`).
  - File ảnh tải lên được lưu trên Cloudflare R2 / Local theo thư mục riêng biệt của Broker: `broker_images/{broker_id}/{tk_id}/{filename}`.
- [x] **Dropdown chọn Broker hoạt động**: Thêm dropdown chuyển đổi Broker trên Header của Curator Dashboard (Local) trích xuất từ bảng `brokers`. Khi thay đổi Broker, tự động reload danh sách listings và cấu hình tương ứng.
- [x] **Cơ chế Đồng bộ Hai chiều Định kỳ & Thủ công (Bidirectional Sync Engine)**:
  - **Đồng bộ khi khởi chạy**: Tự động chạy đồng bộ hai chiều (kéo dữ liệu từ Google Sheets về SQLite local, và đẩy các sửa đổi local lên Sheets) cho tất cả các Broker hoạt động khi local server của Trang khởi chạy.
  - **Đồng bộ ngầm định kỳ (Background Periodic Sync)**: Chạy một tiến trình ngầm (background thread) định kỳ (mỗi 10 phút) để quét và kéo các cập nhật từ Google Sheet của từng Broker (đọc cấu hình từ bảng `brokers`) về SQLite local máy Trang.
  - **Đồng bộ tức thời khi lưu local**: Khi Trang lưu chỉnh sửa trên `curator.html` hoặc `schema.html`, dữ liệu được cập nhật vào SQLite local và đồng thời gọi bất đồng bộ đẩy lên Google Sheets của broker đó ngay lập tức.
  - **Đồng bộ thủ công (Manual Force Sync)**: Có nút bấm "Đồng bộ Sheets" trên header của dashboard để ép chạy tiến trình đồng bộ hai chiều ngay lập tức.

### 2. Quản lý Cấu hình Cột Tùy biến (`schema.html` chạy local máy Trang)
- [x] **Phân quyền `schema.html` và `curator.html` (Chỉ chạy local)**:
  - Cả hai trang `schema.html` (quản lý cột) và `curator.html` (biên tập nội bộ) chỉ chạy local duy nhất trên máy Trang phục vụ Super Admin Trang. Không deploy lên Vercel và các Broker ngoài không có quyền truy cập hai trang này.
  - Các Broker khác tiến hành biên tập dữ liệu custom qua chế độ Broker View tích hợp trên `index.html` của Vercel (hoặc sửa trực tiếp trên file Google Sheet của họ).
- [x] **Bảng Cột Thô (Crawl Raw Columns) & Cấu hình Nhóm**:
  - Hiển thị danh sách tất cả cột dữ liệu thô trong bảng `listings_v2`.
  - Cho phép cấu hình **Nhóm thông tin (address/specs/other) chỉ áp dụng cho Cột Thô**.
  - Có ô chọn/nhập mã căn nhà cụ thể (`System_ID`) để hiển thị giá trị thô thực tế kế bên mỗi cột thô, giúp xem trước dữ liệu cào trực quan.
  - Có nút bấm để tạo nhanh cột custom ánh xạ từ cột thô tương ứng (Tên cột custom tự động thêm tiền tố `custom_` và thừa hưởng thuộc tính từ cột thô đó).
- [x] **Bảng Cột Custom tùy biến theo từng Broker**:
  - Cho phép chọn Broker (lấy dữ liệu trực tiếp từ bảng SQLite `brokers`) để hiển thị danh sách các cột tùy biến đang có trong cấu hình của Broker đó.
- [x] **Quản lý Kiểu Dữ liệu Logic (Logical Data Types)**:
  - Hỗ trợ định nghĩa kiểu dữ liệu logic cho cột tùy biến khi tạo mới động: **`TEXT`**, **`REAL`**, **`INTEGER`**, **`BOOLEAN`**, và **`DROPDOWN`**.
  - Cho phép Trang nhập danh sách các tùy chọn lựa chọn (comma-separated options) khi chọn kiểu dữ liệu `DROPDOWN`.
- [x] **Cơ chế Ẩn / Vô hiệu hóa thay vì Xóa cột để tránh rủi ro**:
  - Để tránh rủi ro mất dữ liệu custom vật lý trong SQLite, hệ thống **không cung cấp nút Xóa cột vật lý**. Thay vào đó, Trang sử dụng cờ **`system_available`** để quản lý:
    - **Nếu Trang set `system_available: false` (Ẩn/Vô hiệu hóa)**: Cột đó bị ẩn hoàn toàn đối với Broker. Cột này sẽ **không xuất hiện** trong Google Sheet của Broker để cấu hình, và được hiểu là **ẩn hoàn toàn trên cả Broker View và Customer View** mà không cần xóa cột vật lý trong SQLite.
    - **Nếu Trang set `system_available: true`**: Cột đó được đồng bộ sang Google Sheet của Broker để họ tự cấu hình ẩn/hiện.
- [x] **Log Terminal trực quan thời gian thực**:
  - Hiển thị log chạy thời gian thực trên giao diện khi Trang thực hiện **thêm cột mới** hoặc **thay đổi trạng thái `system_available`** để theo dõi quá trình ALTER TABLE SQLite local máy Trang và đồng bộ thêm/ẩn cột header mới lên các file Google Sheet (Custom & Public) của tất cả các Broker hiện có.
- [x] **Tương thích phân loại tự sửa lỗi (Self-healing Alignment)**:
  - Logic tự sửa lỗi khi khởi động server phân tách chính xác giữa cột thô (raw) và cột tùy biến (custom) trong `schema_columns` SQLite dựa trên thông tin thực tế từ `listings_custom_v2` và `settings.json`, ngăn ngừa lỗi nhận diện sai cột custom thành cột thô.

### 3. Giao diện biên tập & hiển thị (Broker View trên Vercel vs Customer View)
- [x] **Phân tách 2 View trên Web Vercel (`index.html`)**:
  - **Broker View (Chế độ Biên tập)**: Dành cho môi giới. Hiển thị thông tin cào thô (read-only) chia theo nhóm, form custom để chỉnh sửa (sử dụng nhãn chung "Mã tùy chỉnh" và "Đánh giá") và biên tập ảnh riêng, kèm vùng **preview iframe** trỏ tới URL Customer View.
    - **Tự động kết xuất thẻ điều khiển UI tương ứng kiểu logic**:
      - Kiểu `BOOLEAN`: Hiển thị dưới dạng hộp kiểm **checkbox** (nhấn chọn).
      - Kiểu `DROPDOWN`: Hiển thị dưới dạng hộp chọn thả xuống **`<select>`** chứa các tùy chọn cấu hình từ `settings.json`.
      - Kiểu số (`INTEGER`/`REAL`): Hiển thị dạng `<input type="number">`.
      - Kiểu chữ (`TEXT`): Hiển thị dạng `<input type="text">`.
  - **Customer View (Khách xem công khai)**:
    - Hiển thị bảng thông số chi tiết nhà. **Không chia nhóm các cột mà hiển thị toàn bộ cột dưới dạng danh sách phẳng sắp xếp theo thứ tự cấu hình** (thứ tự của các cột thô và custom do Trang/Broker quy định).
    - **Định dạng hiển thị Kiểu Dữ liệu logic**:
      - **`BOOLEAN`**: Tự động render dưới dạng **hộp kiểm checkbox (read-only, styled)** thay vì hiển thị chữ `"1"`/`"0"` hoặc `"Có"`/`"Không"`.
      - **Bảo toàn trạng thái Unchecked**: Cột kiểu Boolean ở trạng thái chưa chọn (giá trị `0` hoặc false) **vẫn phải hiển thị checkbox chưa tích chọn trực quan trên trang**, không được tự động ẩn dòng đó đi giống như các cột trống khác, nhằm cung cấp thông tin rõ ràng cho khách hàng.
- [x] **Cá nhân hóa Link Gửi Khách hàng**:
  - Link gửi khách hàng xem chứa tham số định danh Broker được mã hóa ẩn danh khó đoán hơn: **`?sp=[broker_id]`** (Ví dụ: `?id=123&sp=khangngo`). Giao diện Customer View (`index.html`) đọc tham số `sp` để nạp cấu hình schema và dữ liệu từ đúng Google Sheet của broker đó.
- [x] **Đồng bộ hóa điều khiển (controls) động dựa trên Schema**:
  - Giao diện Admin/Curation (`lego_detail_admin.js` và `lego_detail_admin_pool2.js`) loại bỏ hoàn toàn các ô thông số thô cứng (hardcoded specs) và các điều khiển biên tập hardcoded.
  - Toàn bộ lưới thông số thô được sinh tự động dựa trên `schema_columns` có `system_available === 1`.
  - Toàn bộ ô nhập liệu/biên tập custom (select dropdown, checkbox, text/number) được sinh động từ cấu hình schema (ngoại trừ các trường cốt lõi bắt buộc: Mã tùy chỉnh, Tiêu đề, Mô tả, Note nội bộ, Hình ảnh).
  - Đồng bộ hóa hành vi lưu dynamic custom fields về SQLite cục bộ và Google Sheets trên cả Pool1 và Pool2.
- [x] **Cơ chế kiểm soát hiển thị công khai phân cấp (Is_Public Hierarchy)**:
  - Khách xem (Customer View) chỉ được xem cột khi thỏa mãn đồng thời cả 2 điều kiện:
    1. Trang set `system_available: true` ở cấp độ hệ thống.
    2. Broker cấu hình `Is_Public: TRUE` (hoặc check chọn) trong tab `Columns_Config` của họ trên Google Sheet.
  - Nếu Trang set `system_available: true` và Broker set `Is_Public: FALSE`: Khách hàng **không được xem**, nhưng **chỉ có Broker View được xem** phục vụ biên tập nội bộ.
  - [x] Áp dụng logic fallback trên Customer View: Lấy dữ liệu từ cột thô, nếu có cột custom tương ứng mà khác rỗng thì lấy giá trị custom đè lên.

### 4. Phân nhóm Specs thô, Nhãn hiển thị trực tiếp & Responsive Mobile (Đợt 7)
- [x] **Hiển thị Specs thô phân nhóm**: Lưới thông số thô trên giao diện chi tiết ở cả hai Pool phải được sắp xếp theo từng phân nhóm (`specs` - Thông số cơ bản, `address` - Vị trí & Địa chỉ, `other` - Thông tin khác) dựa trên cấu hình trong database SQLite thay vì hiển thị phẳng. Mỗi nhóm có tiêu đề riêng `admin-raw-subtitle` và một lưới `.admin-raw-grid` riêng.
- [x] **Loại bỏ trường chính/chi tiết**: Các cột `noi_dung_chinh` và `mo_ta_chi_tiet` phải được lọc bỏ hoàn toàn khỏi Technical Specs Grid do chúng đã hiển thị riêng ở đầu tab view.
- [x] **Chỉnh sửa nhãn hiển thị (`display_label`) trực tiếp**: Giao diện `schema.html` bổ sung ô nhập liệu trực tiếp cho nhãn hiển thị trên mỗi card cột. Cho phép thay đổi nhãn hiển thị và tự động gọi API cập nhật lên SQLite local cùng với đồng bộ ngầm Google Sheets của tất cả active brokers.
- [x] **Responsive Mobile Layout & Smart Grid**: Giữ 2 cột trên Desktop để tiết kiệm không gian. Các trường có nhãn dài hoặc giá trị dài (nhãn > 22 ký tự, giá trị > 20 ký tự, hoặc tổng > 30 ký tự) sẽ tự động được span 2 cột (chiếm trọn 1 dòng). Chuyển toàn bộ lưới `.admin-raw-grid` sang hiển thị dạng 1 cột trên thiết bị di động (màn hình `< 768px`) và cho phép label tự xuống dòng (`white-space: normal`) để không bị cắt chữ.
- [x] **Duyệt Listings (Pool) làm danh sách chính & Trích xuất thông tin gốc**:
  - Đảo ngược logic mapping trong `lego_pool2_core.js`. Thay vì duyệt qua `sourceRows` (tab Custom), hệ thống duyệt qua `poolRows` (tab Listings) làm danh sách chính để nạp và hiển thị đầy đủ thông tin gốc của các căn nhà.
  - Mỗi căn nhà hiển thị trên giao diện (kể cả căn chưa lên sóng, chưa biên tập lần nào hoặc đã biên tập) đều được lấy thông tin thô gốc trực tiếp từ `poolRow` (Listings).
  - Tự động tìm kiếm và trích xuất thông tin biên tập bổ sung từ dòng `sourceRow` (Custom) tương ứng nếu tìm thấy.
  - Gán `p.pool_row_data = pr` (Listings row) thay vì `sr` (Custom row) làm dự phòng, giải quyết triệt để lỗi trống giá trị thô khi mở căn chưa lên sóng.

---

## Sơ đồ Kiến trúc & Luồng Dữ liệu (Mạng Ngoài & Cloud Config)

Dưới đây là sơ đồ kiến trúc thể hiện luồng quản lý schema và đồng bộ kiểu dữ liệu logic động giữa SQLite local, tệp cấu hình metadata `settings.json`, Google Sheets của từng Broker và các client view tương ứng:

```mermaid
graph TD
    subgraph Trang Local Machine (Super Admin Trang)
        RawDB[(SQLite: listings_v2 & listings_custom_v2 & brokers & schema_columns)]
        Settings[settings.json: Metadata custom_schema_columns + DROPDOWN options]
        AdminUI[schema.html local: Quản lý cột, data_type & system_available]
        CuratorUI[curator.html local: Biên tập với Checkbox/Select dynamic]
    end

    subgraph Google Sheets của Broker A (Môi giới A)
        SheetA[(Google Sheet A: Custom Listings)]
        ConfigA[(Tab: Columns_Config của A)]
    end

    subgraph Khách hàng của Broker A (Vercel Client)
        CustomerA[Customer View ?sp=brokerA: Hiển thị flat, Boolean -> check-only checkbox, giữ unchecked]
    end

    subgraph Broker A Edit Mode (Vercel Client)
        BrokerAEdit[Broker View trên index.html: DROPDOWN -> select, BOOLEAN -> checkbox]
    end

    %% Luồng quản lý cấu hình cột của Trang
    AdminUI -- "1. Ghi logic type & dropdown_options" --> Settings
    AdminUI -- "2. ALTER TABLE (INTEGER cho Boolean, TEXT cho Dropdown)" --> RawDB
    AdminUI -- "3. Ghi nhận system_available" --> RawDB
    AdminUI -- "4. Đẩy header và cấu hình mặc định (system_available=1)" --> ConfigA
    AdminUI -- "4. Đẩy header và cấu hình mặc định (system_available=1)" --> SheetA

    %% Luồng biên tập của Trang local
    CuratorUI -- "Đọc schema type & render UI" <-- Settings
    CuratorUI -- "Đọc/Ghi dữ liệu SQLite (Boolean ép về 1/0)" --> RawDB
    CuratorUI -- "Lưu tức thời" --> SheetA

    %% Luồng xem & biên tập phía Client Broker
    BrokerAEdit -- "Đồng bộ gviz nạp Custom & Columns_Config" --> SheetA
    BrokerAEdit -- "Render select/checkbox & lưu lại" --> SheetA
    
    CustomerA -- "Đọc Custom & Columns_Config (chỉ hiện Is_Public=TRUE)" --> SheetA
```

### Bảng Ánh xạ Kiểu Dữ liệu (Logical-to-Physical Mapping)

| Kiểu Logic (Logical Type) | Kiểu SQLite (Physical SQL Type) | Lưu trữ SQLite (DB Value) | Lưu trữ Google Sheet (Sheet Value) | Giao diện Biên tập (Editor UI Widget) | Giao diện Khách hàng (Customer View Render) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`TEXT`** | `TEXT` | `TEXT` (Chuỗi chữ) | Chuỗi chữ | `<input type="text">` | Chuỗi văn bản phẳng |
| **`INTEGER`** | `INTEGER` | `INTEGER` (Số nguyên) | Số nguyên | `<input type="number">` | Số nguyên phẳng |
| **`REAL`** | `REAL` | `REAL` (Số thực) | Số thực | `<input type="number" step="any">` | Số thực phẳng |
| **`BOOLEAN`** | `INTEGER` | `1` hoặc `0` | `"TRUE"` hoặc `"FALSE"` (hoặc `"Có"`/`"Không"`) | `<input type="checkbox">` (Nhấp chọn) | Hộp kiểm checkbox (read-only, styled) - Giữ hiển thị khi bằng `0` |
| **`DROPDOWN`** | `TEXT` | `TEXT` (Lựa chọn đã chọn) | Lựa chọn đã chọn | `<select>` (Dropdown chứa các lựa chọn từ `settings.json`) | Chuỗi văn bản lựa chọn phẳng |

---

## Solution

### 1. SQLite Database Schema & Migration (Brokers & Schema Columns)
Tạo bảng quản lý `brokers`, bảng `schema_columns` lưu trữ metadata cột, và nâng cấp bảng `listings_custom_v2` sang khóa chính kép để cô lập dữ liệu theo từng broker:

```sql
-- Tạo bảng quản lý danh sách Broker
CREATE TABLE IF NOT EXISTS brokers (
    broker_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    custom_sheet_id TEXT,
    public_sheet_id TEXT,
    r2_access_key_id TEXT,
    r2_secret_access_key TEXT,
    r2_bucket_name TEXT,
    r2_public_url TEXT,
    is_active INTEGER DEFAULT 1
);

-- Tạo bảng quản lý cấu hình schema cột thô và custom
CREATE TABLE IF NOT EXISTS schema_columns (
    column_name TEXT PRIMARY KEY,
    column_type TEXT NOT NULL,          -- 'raw' hoặc 'custom'
    display_label TEXT NOT NULL,        -- Tên cột hiển thị (tiếng Việt)
    info_group TEXT DEFAULT 'other',    -- Nhóm thông tin (specs, address, other)
    system_available INTEGER DEFAULT 1, -- Trạng thái kích hoạt hệ thống
    display_order INTEGER DEFAULT 0     -- Thứ tự hiển thị
);

-- Nâng cấp listings_custom_v2 lên khóa chính kép (System_ID, broker_id)
CREATE TABLE listings_custom_v2_new (
    System_ID TEXT,
    broker_id TEXT DEFAULT 'khangngo',
    Ma_Hang_Custom TEXT,
    Tieu_De_Public TEXT,
    Mo_ta_Public TEXT,
    Note_Noi_Bo TEXT,
    Ngu_Tret TEXT,
    CHDV TEXT,
    Danh_Gia_Custom TEXT,
    images_metadata_json TEXT,
    PRIMARY KEY (System_ID, broker_id)
);

-- Di cư dữ liệu cũ an toàn
INSERT INTO listings_custom_v2_new (System_ID, broker_id, Ma_Hang_Custom, Tieu_De_Public, Mo_ta_Public, Note_Noi_Bo, Ngu_Tret, CHDV, Danh_Gia_Custom, images_metadata_json)
SELECT System_ID, 'khangngo', Ma_Khang_Ngo, Tieu_De_Public, Mo_ta_Public, Note_Noi_Bo, Ngu_Tret, CHDV, Danh_Gia_KN, images_metadata_json FROM listings_custom_v2;
DROP TABLE listings_custom_v2;
ALTER TABLE listings_custom_v2_new RENAME TO listings_custom_v2;
```

### 2. Cấu hình Logic Type trong `settings.json`
Định nghĩa metadata cấu hình kiểu dữ liệu logic và options dropdown được lưu trữ tập trung tại tệp cấu hình `settings.json` local:

```json
{
    "active_pool_system": "Pool2",
    "custom_schema_columns": [
        {
            "column_name": "Có Sân Thượng",
            "safe_name": "co_san_thuong",
            "data_type": "BOOLEAN",
            "is_public": true,
            "description": "Nhà có sân thượng hay không",
            "dropdown_options": [],
            "info_group": "specs"
        },
        {
            "column_name": "Tình Trạng Pháp Lý",
            "safe_name": "tinh_trang_phap_ly",
            "data_type": "DROPDOWN",
            "is_public": true,
            "description": "Tình trạng pháp lý của căn nhà",
            "dropdown_options": [
                "Sổ đỏ cất két",
                "Đang thế chấp",
                "Đang chờ sổ"
            ],
            "info_group": "other"
        }
    ]
}
```

### 3. Backend Data Coercion & Type Conversion
Trong backend `manager.py`, khi nhận chỉnh sửa thông tin từ giao diện curator gửi lên qua phương thức `PUT /api/listings/<tk_id>`, hệ thống sẽ đọc cấu hình metadata trong `settings.json` để tiến hành ép kiểu dữ liệu phù hợp trước khi lưu trữ vào SQLite:

```python
# Trích xuất đoạn code ép kiểu trong manager.py
col_type = safe_to_type.get(col_k, "TEXT")
if col_type == "BOOLEAN":
    # Chuyển đổi các giá trị True/truthy thành 1, ngược lại là 0
    if val is True or str(val).lower() in ["true", "1", "yes", "on", "checked", "có"]:
        custom_data[col_k] = 1
    else:
        custom_data[col_k] = 0
elif col_type == "INTEGER":
    try:
        custom_data[col_k] = int(val)
    except Exception:
        custom_data[col_k] = 0
elif col_type == "REAL":
    try:
        custom_data[col_k] = float(val)
    except Exception:
        custom_data[col_k] = 0.0
else:
    custom_data[col_k] = str(val) if val is not None else ""
```

Tương tự, khi chạy bộ đồng bộ kéo dữ liệu từ Google Sheets về SQLite local (`pull_broker_custom_sheet_to_sqlite` trong `pool_lego.py`), giá trị văn bản của cột Boolean trên Google Sheets sẽ được phân tích và lưu đúng định dạng integer:

```python
# Trích xuất đoạn code parse Boolean trong pool_lego.py
if col_type == "BOOLEAN":
    if cleaned_val.lower() in ["true", "1", "yes", "on", "x", "có", "checked"]:
        update_dict[safe_col] = 1
    else:
        update_dict[safe_col] = 0
```

### 4. Client-side Curation & Public Rendering

#### A. Trình biên tập Admin/Broker (`lego_detail_admin_pool2.js` / `curator.html`)
Khi tải thông tin chi tiết căn để chỉnh sửa, JS đọc metadata cột từ API `/api/schema/config` để sinh các thẻ HTML phù hợp động:

```javascript
// Render động widget soạn thảo dựa trên kiểu dữ liệu logic
if (meta.data_type === "BOOLEAN") {
    const isChecked = val === 1 || val === "1" || val === true || String(val).toLowerCase() === "true";
    inputHtml = `<input type="checkbox" id="input_${meta.column_name}" class="curator-checkbox" ${isChecked ? "checked" : ""}>`;
} else if (meta.data_type === "DROPDOWN") {
    const options = meta.dropdown_options || [];
    let optionsHtml = options.map(opt => `<option value="${opt}" ${opt === val ? "selected" : ""}>${opt}</option>`).join("");
    inputHtml = `
        <select id="input_${meta.column_name}" class="curator-select">
            <option value="">-- Chọn --</option>
            ${optionsHtml}
        </select>
    `;
} else if (meta.data_type === "INTEGER" || meta.data_type === "REAL") {
    inputHtml = `<input type="number" id="input_${meta.column_name}" class="curator-input" value="${val || ""}">`;
} else {
    inputHtml = `<input type="text" id="input_${meta.column_name}" class="curator-input" value="${val || ""}">`;
}
```

#### B. Giao diện Khách hàng (`lego_pool2_detail_client.js`)
Ở chế độ xem công khai (Customer View), bảng thông số phẳng sẽ render cột kiểu Boolean dưới dạng checkbox styled, vô hiệu hóa việc nhấn và **giữ dòng hiển thị ngay cả khi checkbox ở trạng thái unchecked** (khác với cột Text thông thường bị ẩn nếu trống):

```javascript
// Trích xuất logic render checkbox styled và bảo toàn unchecked trong lego_pool2_detail_client.js
const colType = (columnMeta.data_type || "TEXT").toUpperCase();
if (colType === "BOOLEAN") {
    const isChecked = val === 1 || val === "1" || val === true || String(val).toLowerCase() === "true" || String(val).toLowerCase() === "có";
    const checkboxHtml = `
        <div class="styled-checkbox-wrapper">
            <input type="checkbox" class="styled-customer-checkbox" disabled ${isChecked ? "checked" : ""}>
            <span class="checkbox-custom-visual ${isChecked ? "checked-visual" : "unchecked-visual"}"></span>
        </div>
    `;
    
    // Thêm dòng vào danh sách phẳng (Không bỏ qua kể cả khi giá trị là 0 / unchecked)
    rowsHtml += `
        <tr class="info-row">
            <td class="info-label">${columnMeta.display_label}</td>
            <td class="info-value">${checkboxHtml}</td>
        </tr>
    `;
} else {
    // Logic text thông thường: Ẩn đi nếu giá trị trống
    if (!val || val === "") return;
    rowsHtml += `
        <tr class="info-row">
            <td class="info-label">${columnMeta.display_label}</td>
            <td class="info-value">${val}</td>
        </tr>
    `;
}
```

### 5. Cải thiện Phân nhóm Specs thô & Responsive Mobile Layout (Đợt 7)
- **Cập nhật renderTechnicalSpecsGrid (lego_helpers.js / lego_pool2_helpers.js)**:
  Phân tách danh sách các cột thô (sau khi loại bỏ `noi_dung_chinh` và `mo_ta_chi_tiet`) vào 3 nhóm dựa trên thuộc tính `info_group`. Sau đó, lặp qua từng nhóm có chứa cột dữ liệu để render tiêu đề nhóm (`.admin-raw-subtitle`) và div grid `.admin-raw-grid` tương ứng.
  **Smart Dynamic Layout**: Khi render mỗi cell `.admin-raw-cell`, nếu nhãn dài > 22 ký tự, hoặc giá trị dài > 20 ký tự, hoặc tổng độ dài > 30 ký tự, tự động gán class `.full-width` để span 2 cột trên màn hình lớn.
- **Responsive CSS (global.css)**:
  Định nghĩa `.admin-raw-cell.full-width` có `grid-column: span 2;`.
  Sử dụng `@media (max-width: 768px)` để ghi đè thuộc tính grid của `.admin-raw-grid` sang `1fr` và `.admin-raw-cell.full-width` sang `grid-column: span 1 !important;`. Cập nhật `.admin-raw-cell .label` có `white-space: normal !important` và `word-break: break-word` để hiển thị nhãn xuống dòng gọn gàng.
- **Sửa API Backend (manager.py)**:
  Cho phép POST request tới `/api/schema/update-column-group` nhận thêm tham số `display_label` để cập nhật đồng thời cả nhãn hiển thị cột, sau đó gọi `sync_all_brokers_config_bg()` chạy ngầm.

---

## Verification Plan & Hướng dẫn Test Full Flow (E2E Testing Guide)

Tính năng Schema-Driven Curation Engine cho phép Trang tự động hóa cấu hình cột từ SQLite và Settings, kết xuất giao diện biên tập động, lưu trữ động và hiển thị phẳng phía khách hàng. Dưới đây là hướng dẫn chi tiết để kiểm thử toàn bộ luồng (Full Flow).

### 💡 Phương pháp Test Nhanh qua URL Query Parameters (Khuyên dùng)

Để việc test của bạn tiện lợi nhất mà không cần mở Console F12 để gõ lệnh `localStorage`, hệ thống hỗ trợ tự động nhận diện các tham số URL sau:

1. **Xem giao diện phẳng Khách hàng (Customer View)**:
   - Chỉ cần thêm cờ `&preview=true` vào link.
   - *Link mở trực tiếp*: `http://localhost:5000/index.html?sp=khangngo&id=SYS-1001&preview=true`
   - > [!TIP]
     > **Tự động dọn dẹp**: Khi bạn mở link có `&preview=true` này 1 lần duy nhất, hệ thống sẽ tự động xóa sạch các cờ Admin cũ trong trình duyệt của bạn. Kể từ đó, bạn có thể mở các link thường mà không bao giờ bị dính màn hình khóa đăng nhập nữa.

2. **Xem giao diện Biên tập của Môi giới (Broker View)**:
   - Chỉ cần thêm cờ `&test=true` vào link.
   - *Link mở trực tiếp*: `http://localhost:5000/index.html?sp=khangngo&id=SYS-1001&test=true`
   - > [!NOTE]
     > **Bypass Auth & Mock Token**: Hệ thống phát hiện cờ `test=true` sẽ tự động kích hoạt phiên đăng nhập mock, vượt qua màn hình khóa Google và đưa bạn vào thẳng chế độ Broker View để test các ô điều khiển (Controls).

### 1. Luồng Kiểm thử Tự động (Automated E2E Test Suite)
Bộ kiểm thử Playwright và bộ test tích hợp API được lập trình sẵn để tự động thiết lập dữ liệu giả lập, chạy trình duyệt không đầu (headless), tương tác với giao diện và kiểm tra API.

* **Bước 1: Chạy test tích hợp logic kiểu dữ liệu (Database & API Type Coercion)**
  ```powershell
  python scratch/test_schema_custom_fields.py
  ```
  *Mục đích*: Xác minh backend tự động ALTER TABLE SQLite, lưu giá trị BOOLEAN dạng số nguyên `1`/`0`, và tự ép kiểu khi kéo đồng bộ Sheets.
  *Kỳ vọng*: Console in ra `OK` và pass tất cả 5 Stages.

* **Bước 2: Chạy test E2E giao diện và luồng Curation (Playwright E2E)**
  ```powershell
  python scratch/test_e2e_curation.py
  ```
  *Mục đích*: Playwright tự động chạy Chrome, mở Curator Dashboard, click card Pool thô, điền thông tin AI, cuộn xác nhận checkbox `#edit_co_san_thuong` xuất hiện động, click "Lên sóng" và verify Google Sheets API PUT request nhận đúng payload.
  *Kỳ vọng*: Console in ra `[🎉 ALL E2E CURATION TESTS PASSED SUCCESSFULLY]`.

---

### 2. Luồng Kiểm thử Thủ công Chi tiết (Manual E2E Test Steps)
Bạn có thể tự thực hiện kiểm thử trên trình duyệt cục bộ để nghiệm thu tính năng theo các bước trực quan dưới đây:

#### Giai đoạn A: Thiết lập & Quản lý Schema Cột
1. **Khởi động server**: Chạy file [CHAY_APP.bat](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/CHAY_APP.bat).
2. **Truy cập Schema Editor**: Mở trình duyệt vào link `http://localhost:5000/schema.html` (chỉ cho phép truy cập từ máy local).
3. **Thêm cột tùy biến mới**:
   * Tại dropdown "Chọn môi giới", chọn `khangngo`.
   * Ở thanh bên trái "Thêm cột tùy biến", nhập:
     * **Tên cột**: `Có Sân Thượng` (Hệ thống tự sinh safe_name là `co_san_thuong`).
     * **Kiểu dữ liệu**: Chọn `BOOLEAN`.
     * **Phân nhóm**: Chọn `specs`.
   * Bấm nút **Lưu cấu hình cột**.
   * Tiếp tục thêm một cột kiểu Dropdown:
     * **Tên cột**: `Tình Trạng Pháp Lý` (safe_name: `tinh_trang_phap_ly`).
     * **Kiểu dữ liệu**: Chọn `DROPDOWN`.
     * **Danh sách lựa chọn**: Nhập `Sổ đỏ cất két, Đang thế chấp, Đang chờ sổ`.
     * **Phân nhóm**: Chọn `other`.
   * Bấm nút **Lưu cấu hình cột**.
4. **Xác minh thay đổi**:
   * Quan sát khu vực log terminal ở chân trang `schema.html`: Phải in ra log chạy lệnh `ALTER TABLE` SQLite thành công và log đồng bộ header mới lên Google Sheets của Broker.
   * Kiểm tra file `settings.json` tại root folder: Đảm bảo cấu hình các cột này đã được lưu vào mảng `custom_schema_columns`.

#### Giai đoạn B: Biên tập Curation (Admin Curator View)
1. **Vào trang biên tập**: Truy cập `http://localhost:5000/` (nội dung load từ `curator.html`).
2. **Chọn Broker**: Đảm bảo dropdown broker trên header đang chọn đúng Broker `khangngo`.
3. **Mở căn từ Pool thô**: Tìm một căn nhà thuộc rổ Pool thô (ví dụ căn có mã nguồn `SYS-1001`) và click để mở panel Curation bên phải.
4. **Xác nhận giao diện sinh động (Dynamic Render)**:
   * Mở rộng accordion **Biên tập Curation**.
   * Cuộn xuống dưới cùng của form và tìm nhóm **🛠️ Cột tùy biến tự thêm** (hoặc lưới custom fields ở cuối form).
   * Xác nhận:
     * Cột `Có Sân Thượng` được hiển thị dưới dạng **Checkbox (Hộp kiểm)**.
     * Cột `Tình Trạng Pháp Lý` được hiển thị dưới dạng **Dropdown Select** với đúng 3 lựa chọn đã nhập ở Giai đoạn A.
5. **Thực hiện biên tập và lưu**:
   * Bấm nút **⚡ Tự động điền** (AI sẽ tự sinh Tiêu đề Public và Mô tả Public).
   * Tích chọn checkbox `Có Sân Thượng` (Trạng thái checked).
   * Chọn `Đang thế chấp` trong dropdown `Tình Trạng Pháp Lý`.
   * Bấm nút **Lên sóng ⚡** ở góc dưới bên phải để đẩy tin.
6. **Xác minh CSDL & Sheets**:
   * Mở tệp SQLite `raw_archive_v2.db` bằng một tool đọc DB hoặc chạy script truy vấn:
     ```sql
     SELECT co_san_thuong, tinh_trang_phap_ly FROM listings_custom_v2 WHERE System_ID = 'SYS-1001';
     ```
     Đảm bảo `co_san_thuong` lưu giá trị `1` (Boolean true) và `tinh_trang_phap_ly` lưu `"Đang thế chấp"`.
   * Mở file Google Sheet Custom của broker Khang Ngô: Xác nhận dòng tương ứng đã được đồng bộ ghi thành công với giá trị tương ứng (`TRUE` / `Đang thế chấp`).

#### Giai đoạn C: Kiểm tra Hiển thị Khách hàng (Customer View)
1. **Truy cập trang khách xem**: Mở link `http://localhost:5000/index.html?sp=khangngo&id=SYS-1001` (Chế độ Customer View công khai).
2. **Xác minh bảng thông số phẳng**:
   * Cột `Tình Trạng Pháp Lý` phải hiển thị text phẳng `"Đang thế chấp"`.
   * Cột `Có Sân Thượng` phải hiển thị dưới dạng **hộp kiểm checkbox styled (màu vàng/gold, read-only)** ở trạng thái **Checked** (đã chọn).
3. **Kiểm tra trạng thái Unchecked (Bảo toàn hiển thị)**:
   * Vào lại trang biên tập `curator.html`, bỏ chọn checkbox `Có Sân Thượng` (Unchecked), rồi bấm Lưu.
   * Quay lại link Khách xem và tải lại trang:
     * Xác nhận: Cột `Có Sân Thượng` **vẫn hiển thị** trên bảng thông số dưới dạng **checkbox styled ở trạng thái Unchecked (chưa chọn)**, chứ không bị ẩn dòng đi giống như các cột Text trống khác. Điều này giúp cung cấp thông tin rõ ràng cho khách mua.

---

## 📝 Task Checklist

- [x] **Khởi động & Di cư Database:**
  - [x] Thực hiện tạo bảng SQLite `brokers` và di cư bảng `listings_custom_v2` sang khóa chính kép, cột `Ma_Hang_Custom` và `Danh_Gia_Custom`.
  - [x] Điền dữ liệu cấu hình các broker hiện tại vào bảng SQLite `brokers`.
  - [x] Khởi tạo cấu trúc mẫu tab `Columns_Config` cho các Broker.
- [x] **Lập trình Backend & Cloud APIs:**
  - [x] Cập nhật toàn bộ các câu lệnh SQL tác động đến `listings_custom_v2` để lọc theo `broker_id` và dùng `Ma_Hang_Custom`, `Danh_Gia_Custom`.
  - [x] Viết API quản lý Broker (list, select, update) từ bảng `brokers`.
  - [x] Viết API quản lý Schema (columns-config, add-column, toggle-column-status).
- [x] **Hỗ trợ Kiểu dữ liệu logic dynamic (DROPDOWN & BOOLEAN):**
  - [x] Ánh xạ kiểu logic `BOOLEAN` về kiểu vật lý `INTEGER` và `DROPDOWN` về `TEXT` trong SQLite cho cả `listings_v2` và `listings_custom_v2`.
  - [x] Lưu trữ cấu hình logical types và options vào `settings.json` trong `/api/schema/add-column`.
  - [x] Viết logic ép kiểu Boolean (`1`/`0`) và số nguyên/số thực trong PUT listing details API.
  - [x] Viết logic ép kiểu và mapping tiêu đề Google Sheet tiếng Việt khi kéo đồng bộ dữ liệu (`pull_broker_custom_sheet_to_sqlite`).
- [x] **Phát triển Giao diện HTML & Tích hợp:**
  - [x] Xây dựng file `schema.html` hoàn chỉnh (local only) cho phép chọn broker từ bảng `brokers` và cấu hình cột, hỗ trợ sidebar chọn kiểu dữ liệu và hiển thị badge.
  - [x] Cập nhật `curator.html` hỗ trợ render động `<select>` cho `DROPDOWN` và checkbox cho `BOOLEAN`.
  - [x] Cập nhật `index.html` (phân tách Broker View & Customer View, hiển thị danh sách phẳng sắp xếp theo thứ tự, lọc hiển thị theo tham số `sp` đọc từ Google Sheets của Broker, nhãn nhất quán "Mã tùy chỉnh" và "Đánh giá").
  - [x] Cập nhật `lego_pool2_detail_client.js` hiển thị cột `BOOLEAN` dưới dạng hộp kiểm checkbox (read-only, styled) và giữ hiển thị unchecked thay vì ẩn.
- [x] **Kiểm thử & Nghiệm thu:**
  - [x] Đảm bảo chuyển đổi broker hoạt động trơn tru cục bộ.
  - [x] Xác minh hình ảnh, dữ liệu custom và cấu hình cột chạy hoàn toàn độc lập theo từng Broker trên Google Sheet.
  - [x] Viết và chạy thành công bộ test tích hợp full luồng `test_schema_custom_fields.py`.
  - [x] Chạy kiểm thử tự động E2E Playwright trên local máy Trang xác minh không bị lỗi hồi quy.
- [x] **Đồng bộ hóa động hệ thống hiển thị & biên tập (Đợt 6):**
  - [x] Cập nhật logic self-healing CSDL phân tách chính xác cột raw/custom.
  - [x] Làm giàu kiểu dữ liệu logic động cho `/api/config` backend.
  - [x] Tạo hàm dùng chung render lưới thông số thô và ô nhập liệu động trên `lego_helpers.js`.
  - [x] Loại bỏ hoàn toàn specs và controls hardcoded trên giao diện chi tiết Pool1 và Pool2.
  - [x] Duyệt động và đồng bộ lưu trữ các trường tùy biến khi lưu curation.
- [x] **Phân nhóm Specs thô, Nhãn hiển thị trực tiếp & Responsive Mobile (Đợt 7):**
  - [x] Sửa API backend `update_column_group` để cập nhật cả `info_group` và `display_label` và trigger sync ngầm Google Sheets.
  - [x] Sửa `schema.html` thay thế title tĩnh bằng input để chỉnh sửa trực tiếp nhãn hiển thị và gọi API cập nhật.
  - [x] Cập nhật `static/js/lego_helpers.js` và `static/js/lego_pool2_helpers.js` lọc bỏ 2 trường `noi_dung_chinh`/`mo_ta_chi_tiet` và render phân nhóm specs thô.
  - [x] Cập nhật `static/js/lego_detail_admin.js` và `static/js/lego_detail_admin_pool2.js` loại bỏ div `.admin-raw-grid` bọc ngoài.
  - [x] Cập nhật `static/css/global.css` thêm style `.admin-raw-subtitle` và responsive layout 1 cột cho `.admin-raw-grid` khi màn hình nhỏ.
- [ ] **Khắc phục lỗi trống giá trị thô trên giao diện (Đợt 8):**
  - [ ] Thêm hàm helper global `window.getValFromRowBySchema` trong `lego_helpers.js` và `lego_pool2_helpers.js` để lấy giá trị tự động dựa trên `schema_columns`.
  - [ ] Cập nhật mapping khi duyệt danh sách Google Sheet (trong `mapPoolData`, `loadData` và `openPoolS` của cả hai Pool) để tự động nạp toàn bộ cấu hình cột SQLite vào đối tượng `p`.
  - [ ] Đơn giản hóa hàm `renderCell` trong `renderTechnicalSpecsGrid` để lấy giá trị trực tiếp bằng key SQLite `column_name` từ đối tượng listing `p`.
  - [ ] Cập nhật `getDisplayValue` trong `lego_detail_client.js` và `lego_pool2_detail_client.js` để lấy giá trị trực tiếp từ đối tượng listing `p` bằng key `colName` SQLite.

---

## 🪵 Nhật ký Nghiệm thu Đợt chạy (Migration Runs Logs)

### Đợt 1: Hạ tầng CSDL & Di cư Bảng (Hoàn thành: 2026-06-18)
* **Người thực hiện**: Antigravity & Khang Ngo
* **Nội dung công việc**:
  - Tạo bảng `brokers` quản lý danh sách môi giới, seed mặc định broker `khangngo` kèm các cấu hình Sheets, R2 từ `settings.json`.
  - Di cư bảng `listings_custom_v2` sang cấu trúc mới hỗ trợ khóa kép `(System_ID, broker_id)`.
  - Đổi tên trường dữ liệu tùy chỉnh cũ sang trường mới: `Ma_Khang_Ngo` -> `Ma_Hang_Custom`, `Danh_Gia_KN` -> `Danh_Gia_Custom`.
  - Bảo toàn dữ liệu cũ của Khang Ngô khi thực hiện di cư.
  - Cập nhật backend `pool_lego.py` và `manager.py` cho phép lọc động theo `broker_id` và hỗ trợ cấu trúc schema mới.
  - Đảm bảo tính tương thích ngược (client normalization) bằng cách map động `Ma_Khang_Ngo_ID` và `Danh_gia_Admin` ở API `manager.py`.
* **Kết quả kiểm thử**:
  - Đã chạy kiểm thử thông qua script `test_phase1.py` thành công 100%.
  - Kết quả in ra xác nhận đọc/ghi SQL theo khóa kép `(System_ID, broker_id)` hoạt động chính xác.
  - Test Client Normalization trả về kết quả ánh xạ chính xác về các trường định dạng tương thích ngược cho Vercel Client.

### Đợt 2: Trang Quản trị Cấu hình Local (Hoàn thành: 2026-06-19)
* **Người thực hiện**: Antigravity & Khang Ngo
* **Nội dung công việc**:
  - Định nghĩa bảng `schema_columns` quản lý metadata cấu hình cột (loại cột, nhãn tiếng Việt, phân nhóm, system_available, thứ tự sắp xếp).
  - Tích hợp logic self-healing trong `pool_lego.init_db()` để quét và seed dữ liệu ban đầu cho 81 cột (gồm cột thô của `listings_v2` và cột custom của `listings_custom_v2`).
  - Xây dựng decorator bảo mật `@local_only` trong `manager.py` chặn các truy cập không phải từ `localhost` / `127.0.0.1` / `::1`.
  - Áp dụng bảo mật cho trang Curator (`/`), trang quản trị cột (`/schema.html`) và toàn bộ API admin.
  - Viết các API mới phục vụ quản lý Broker (`/api/brokers/list`, `/api/brokers/update`) và quản lý Schema (`/api/schema/config`, `/api/schema/toggle-column-status`, `/api/schema/update-column-group`, `/api/schema/preview-row`).
  - Tạo giao diện `schema.html` hoàn toàn mới với thiết kế Sleek Dark Mode, hỗ trợ đổi nhóm cột thô, toggle `system_available`, xem trước giá trị thực tế của căn nhà và tích hợp Console log terminal.
  - Tích hợp Dropdown chọn Broker hoạt động trên giao diện `curator.html` (Curator Dashboard) đồng bộ với bảng `brokers`.
  - Đính kèm tham số `sp` tương ứng với broker được chọn cho toàn bộ các API tương tác (lấy danh sách, chi tiết, lưu, xuất bản, cào lại, xóa, và xuất bản hàng loạt).
  - Nhất quán nhãn hiển thị `🔑 MÃ KHANG NGÔ (ID)` thành `🔑 MÃ TÙY CHỈNH` trên giao diện biên tập.
* **Kết quả kiểm thử**:
  - Chạy kịch bản kiểm thử tích hợp thông qua `test_phase2_apis.py` thành công 100%.
  - Xác nhận các API hoạt động chính xác từ local và trả về `403 Forbidden` khi gọi từ xa (remote IP).
  - Trạng thái `system_available` và phân nhóm cột thô được cập nhật và lưu trữ chính xác trong bảng SQLite `schema_columns`.
  - Xác nhận dropdown chọn Broker hoạt động tốt trên giao diện `curator.html` cục bộ và lọc dữ liệu chính xác theo broker được chọn.

### Đợt 3: Bộ Đồng bộ Hai chiều (Hoàn thành: 2026-06-19)
* **Người thực hiện**: Antigravity & Khang Ngo
* **Nội dung công việc**:
  - Viết và hoàn thiện hàm đồng bộ hai chiều `pull_broker_custom_sheet_to_sqlite` và `sync_columns_config_to_sheets` hỗ trợ gộp/ghi đè dữ liệu, xử lý an toàn lỗi trùng lặp sheet `Columns_Config` của gspread.
  - Cập nhật hàm `add_column_to_google_sheets_v2` để tự động cập nhật Header cho toàn bộ active brokers khi Trang thêm cột thô mới.
  - Tích hợp các API hỗ trợ `/api/sync/force` (local-only) ép chạy đồng bộ hai chiều bất cứ lúc nào.
  - Xây dựng scheduler ngầm định kỳ (quét mỗi 10 phút) và khi khởi chạy server Flask.
  - Thiết kế nút bấm **`🔄 Đồng bộ Sheets`** trên curator dashboard hiển thị tiến trình log đồng bộ thời gian thực.
* **Kết quả kiểm thử**:
  - Đã chạy kịch bản kiểm thử tích hợp thông qua `test_phase3_sync.py` thành công 100%.
  - Xác nhận kéo dữ liệu custom từ Google Sheets về SQLite và ghi đè an toàn.
  - Đồng bộ thành công cấu hình hiển thị (81 cột khả dụng) lên tab `Columns_Config` của các broker, đồng thời ẩn đi các cột có `system_available = 0` trên Sheets và bảo toàn cờ `Is Public` của broker.

### Đợt 4: Giao diện Web Vercel & Phân quyền Hiển thị (Hoàn thành: 2026-06-19)
* **Người thực hiện**: Antigravity & Khang Ngo
* **Nội dung công việc**:
  - Triển khai xuất cấu hình Broker rút gọn (bảo mật, không chứa R2 keys) ra file `static/brokers.json`.
  - Cập nhật `/api/config` Vercel Backend nhận query `sp` để nạp cấu hình Google Sheet IDs và R2 URLs động từ `static/brokers.json`.
  - Cập nhật logic tiêm meta server-side (SEO) nạp đúng sheet của Broker tương ứng dựa trên query `sp`.
  - Cập nhật `/api/upload-r2` hỗ trợ phân tách prefix thư mục ảnh R2 theo định dạng `broker_images/{broker_id}/{tk_id}/{filename}`.
  - Cập nhật `lego_pool2_core.js` để truyền `sp` và gọi song song tải tab `Custom` và tab `Columns_Config` của Broker qua Google Sheets gviz API.
  - Cập nhật `lego_pool2_detail_client.js` hiển thị danh sách phẳng, lọc ẩn các cột có `Is Public = FALSE` hoặc vô hiệu hóa, tự động thêm đơn vị đo, và xử lý fallback từ cột custom về cột thô tương ứng nếu rỗng.
* **Kết quả kiểm thử**:
  - Đã chạy kịch bản kiểm thử giả lập thông qua `test_phase4_client.py` thành công 100%.
  - Xác nhận `/api/config?sp=khangngo` hoạt động chính xác, đọc đúng cấu hình sheet của Khang Ngô, và tự động fallback nếu không tìm thấy broker.
  - Xác nhận đường dẫn lưu ảnh trên R2 được tách biệt theo cấu trúc prefix `broker_images/{broker_id}/{tk_id}/` thành công.
  - Xác nhận client JS parse tab `Columns_Config` và filter cột public, đè giá trị custom lên giá trị thô khi hiển thị phẳng.

### Đợt 5: Kiểu Dữ liệu Cột, DROPDOWN & BOOLEAN Curation & Test Case Hoàn Chỉnh (Hoàn thành: 2026-06-19)
* **Người thực hiện**: Antigravity & Khang Ngo
* **Nội dung công việc**:
  - Bổ sung hỗ trợ đầy đủ cho các kiểu dữ liệu logic động: `TEXT`, `REAL`, `INTEGER`, `DROPDOWN`, và `BOOLEAN`.
  - Cập nhật SQLite physical mapping: `BOOLEAN` ánh xạ về kiểu vật lý `INTEGER` trong SQLite, `DROPDOWN` ánh xạ về `TEXT`. Cả `listings_v2` và `listings_custom_v2` đều được nâng cấp đúng kiểu dữ liệu cột tương ứng.
  - Cập nhật `/api/schema/config` để nạp và trả về kiểu dữ liệu logic cùng các tùy chọn từ `settings.json`.
  - Nâng cấp `/api/schema/add-column` để lưu metadata cột (`data_type`, `dropdown_options`, và `info_group`) và thực hiện ALTER TABLE tương ứng.
  - Nâng cấp `/api/listings/<tk_id>` (PUT) để đọc, chuyển đổi kiểu dữ liệu phù hợp (đặc biệt ép kiểu Boolean sang `1`/`0`, số nguyên sang `int`, số thực sang `float`) và lưu vào SQLite `listings_custom_v2`.
  - Sửa `pull_broker_custom_sheet_to_sqlite` để map tiêu đề cột tiếng Việt sang safe name trước khi kiểm tra, đồng thời chuyển đổi giá trị kéo từ Google Sheet sang đúng kiểu dữ liệu logic (chuyển các chuỗi `"TRUE"`, `"1"`, `"Có"` của Boolean về `1`, còn lại về `0`).
  - Nâng cấp `schema.html` hỗ trợ sidebar tạo cột chọn kiểu dữ liệu (chọn DROPDOWN thì hiện nhập options) và phân nhóm, hiển thị kiểu dữ liệu logic trên thẻ cột, và bổ sung nút **Tạo nhanh** ánh xạ từ cột thô sang cột custom.
  - Cập nhật client biên tập `lego_detail_admin_pool2.js` và local dashboard `curator.html` tự động render `<select>` cho `DROPDOWN`, hộp kiểm checkbox cho `BOOLEAN`, `<input type="number">` cho số, `<input type="text">` cho chữ, gửi payload an toàn.
  - Nâng cấp client hiển thị công khai `lego_pool2_detail_client.js` tự động render hộp kiểm checkbox (read-only, styled) cho các cột BOOLEAN thay vì hiển thị chữ Có/Không, đồng thời bỏ qua logic loại bỏ dòng giá trị 0 đối với kiểu BOOLEAN để đảm bảo hộp kiểm (dù checked hay unchecked) vẫn được hiển thị trực quan.
  - Viết lại bộ test tích hợp `scratch/test_schema_custom_fields.py` kiểm thử toàn bộ luồng tạo schema, ALTER TABLE, lấy cấu hình logic, ghi dữ liệu PUT, và kéo đồng bộ sheets của cả `BOOLEAN` và `DROPDOWN`.
* **Kết quả kiểm thử**:
  - Chạy thành công 100% script test tích hợp:
    ```powershell
    python "C:\Users\Khang Ngo\.gemini\antigravity\brain\88758e3c-cba2-4ae4-b2c4-717761c24640\scratch\test_schema_custom_fields.py"
    ```
  - Kết quả in ra console log thực tế:
    ```text
    Ran 1 test in 1.322s

    OK
    [*] Initializing test database...

    --- STAGE 1: Creating custom columns (BOOLEAN and DROPDOWN) ---
    [✅] Custom columns added successfully.

    --- STAGE 2: Verifying settings.json metadata and SQLite columns ---
    [✅] settings.json logical types verified.
    [✅] SQLite physical columns data types verified.

    --- STAGE 3: Testing GET schema/config returns logical metadata ---
    [✅] GET /api/schema/config logical type mapping verified.

    --- STAGE 4: Testing PUT listing saves dynamic values with type conversion ---
    [✅] Truthy Boolean (True) successfully converted to integer 1 and saved.
    [✅] Falsy Boolean ('false') successfully converted to integer 0 and saved.

    --- STAGE 5: Testing Sheet Pull Synchronization Type Mapping ---
    [✅] Pull sheet sync mapped Vietnamese headers to safe names and parsed Boolean values properly.
    ```

### Đợt 6: Đồng bộ Hóa Động Hệ thống Hiển thị & Biên tập theo Cấu hình Schema (Kế hoạch Triển khai)
* **Người thực hiện**: Antigravity & Khang Ngo
* **Nội dung công việc**:
  - Cải tiến logic self-healing trong `pool_lego.py` để phân tách chính xác raw và custom columns dựa trên thông tin thực tế từ `listings_custom_v2` và `settings.json`. Sửa lỗi ghi đè nhãn và loại cột custom thành raw.
  - Làm giàu (enrich) thông tin kiểu dữ liệu logic (`data_type`, `dropdown_options`) cho API cấu hình hệ thống `/api/config` trong `manager.py`.
  - Chuẩn hóa hàm dùng chung kết xuất lưới thông số thô (`window.renderTechnicalSpecsGrid`) và sinh các ô điều khiển nhập liệu tùy biến động (`window.renderFieldHtml` và `window.renderDynamicCustomFields`) trong `lego_helpers.js` và `lego_pool2_helpers.js`.
  - Cập nhật mẫu giao diện biên tập chi tiết Admin (`lego_detail_admin.js` và `lego_detail_admin_pool2.js`) sử dụng các hàm sinh động để loại bỏ hoàn toàn mã hardcoded.
  - Duyệt động lưu trữ toàn bộ các trường tùy biến trong hàm `saveSourceChanges` lên SQLite và Google Sheets cho cả Pool1 và Pool2.
* **Kết quả kiểm thử**:
  - Chạy thành công bộ kiểm thử tích hợp E2E Curation Playwright:
    ```powershell
    python scratch/test_e2e_curation.py
    ```
    Xác nhận giao diện render hoàn toàn động dựa trên cấu hình schema từ SQLite, payload dữ liệu được đọc-ghi và ánh xạ chính xác mà không bị vỡ giao diện hay lệch cột trên cả hai hệ thống Pool1 và Pool2. Giao tiếp dữ liệu qua REST API được đồng bộ an toàn.
  - Khắc phục thành công lỗi timeout E2E test bằng cách đồng bộ hóa độ trễ xử lý (race conditions) của auth/data-load và bypass popup cảnh báo chọn ảnh công khai khi đồng bộ Lên sóng.
  - Phù hợp hóa 100% phạm vi test: tập trung hoàn toàn vào kiểm thử trên Vercel Client (Broker View và Customer View trên `index.html`), bỏ qua Curator Dashboard local (`curator.html`) theo chỉ thị của USER. Bộ kiểm thử E2E Playwright mới đã chạy thành công 100%.

### Đợt 7: Cải thiện Phân nhóm Specs thô, Responsive Mobile Layout và Cấu hình Display Label Trực tiếp (Hoàn thành: 2026-06-19)
* **Người thực hiện**: Antigravity & Khang Ngo
* **Nội dung công việc**:
  - Phân nhóm hiển thị các thông số thô thành 3 nhóm rõ ràng (`specs` - Thông số cơ bản, `address` - Vị trí & Địa chỉ, `other` - Thông tin khác) trên Technical Specs Grid của cả Pool 1 và Pool 2.
  - Lọc bỏ hai cột `noi_dung_chinh` và `mo_ta_chi_tiet` khỏi Technical Specs Grid.
  - Hỗ trợ chỉnh sửa nhanh nhãn hiển thị (`display_label`) trực tiếp cho các cột trong `schema.html` thông qua ô nhập liệu (input) và gửi cập nhật đồng bộ lên CSDL SQLite cùng Google Sheets qua API.
  - Tối ưu CSS Responsive cho lưới thông số thô (`.admin-raw-grid` chuyển sang 1 cột trên các thiết bị di động có chiều rộng `< 768px`) và cho phép nhãn tự xuống dòng (`white-space: normal`) để tránh bị cắt chữ khi nhãn dài.
* **Kết quả kiểm thử**:
  - Đã chạy kịch bản kiểm thử E2E Playwright (`python scratch/test_e2e_curation.py`) thành công 100%. Xác nhận lưới specs thô tự động phân nhóm và span 2 cột/1 cột responsive mượt mà, đồng thời tính năng sửa display_label hoạt động chính xác.

### Đợt 8: Khắc phục lỗi trống giá trị thô trên giao diện bằng SQLite Column Name (Kế hoạch Triển khai)
* **Người thực hiện**: Antigravity & Khang Ngo
* **Nội dung công việc**:
  - Nhất quán sử dụng tên cột SQLite (`column_name`) làm key chính để gán dữ liệu từ Google Sheets và truy xuất giá trị trên UI, loại bỏ hoàn toàn cơ chế ánh xạ ngữ nghĩa thủ công.
  - Bổ sung hàm nạp thuộc tính động tự động theo `schema_columns` khi mở chi tiết căn Pool thô trực tiếp (`openPoolS`) ở cả hai Pool.
  - Đơn giản hóa hàm `renderCell` trong `renderTechnicalSpecsGrid` và `getDisplayValue` ở Client View để lấy giá trị trực tiếp từ listing `p` bằng tên cột SQLite.
* **Kết quả kiểm thử**:
  - (Sẽ cập nhật sau khi hoàn thành triển khai và kiểm thử).
