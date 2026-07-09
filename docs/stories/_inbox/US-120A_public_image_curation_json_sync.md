---
id: US-120A
status: accepted
date: 2026-07-07
size: M
---

# US-120A: Quản lý & Sắp xếp Hình ảnh Công khai dạng JSON

## User Story
**As an** Admin / Product Owner
**I want** to curate, reorder, change roles (both public and private), and logically hide images on the Vercel Admin Curation Dashboard
**And** save these changes into a unified `Images_Admin_JSON` column on Pool sheet and `Images_Public_JSON` column on Source sheet (SQLite SQL v1), while maintaining full parallel write to existing flat columns
**And** render public images sorted by `sequence_index` and filter out hidden images on Vercel Client View (falling back to flat columns if JSON is missing)
**So that** I can customize the public photo gallery dynamically and scale to 5,000+ listings without Sheets quota limit errors.

## Acceptance Criteria

### 1. SQLite Relational Database (SQL v1) & Schema Update
- [ ] Khởi tạo bảng `listings_images` trong SQLite local (CSDL SQL bản 1: `raw_archive.db`) với các trường:
  - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
  - `tk_id` (TEXT, khóa ngoại)
  - `system_id` (TEXT, mã ID của hệ thống)
  - `image_url` (TEXT)
  - `r2_url` (TEXT)
  - `role` (TEXT: `facade`, `diagram`, `alley`, `interior`, `background`, `deleted`)
  - `sequence_index` (INTEGER)
  - `origin` (TEXT: `crawl`, `self`)
  - `is_hidden` (INTEGER DEFAULT 0)
  - `uploaded_at` (TEXT)
  - FOREIGN KEY(tk_id) REFERENCES listings(tk_id) ON DELETE CASCADE
- [ ] Thêm 2 trường lưu trữ JSON mới vào bảng **`listings`** trong SQLite (CSDL SQL bản 1):
  - `images_admin_json TEXT`: Lưu toàn bộ kho ảnh thô + metadata của Admin (bao gồm ảnh ẩn, ảnh private mặt tiền, sơ đồ).
  - `images_public_json TEXT`: Lưu danh sách mảng chỉ chứa các link ảnh public sạch dành cho khách hàng xem (đã sắp xếp và lọc bỏ ảnh ẩn/private).

### 2. Google Sheets Schema & Apps Script Sync
- [ ] **Giữ nguyên toàn bộ cột phẳng hiện tại:** 
  - Tab **Pool:** Giữ nguyên 10 cột `Hình Hẻm 1-10` và 25 cột `Ảnh 1-25`.
  - Tab **Source:** Giữ nguyên 15 cột ảnh public (`anh_1` đến `anh_15`) phục vụ hiển thị client cũ.
- [ ] **Khởi tạo các cột JSON mới:** 
  - Tab **Pool:** Tạo cột mới tên là **`Images_Admin_JSON`** ở cuối bảng.
  - Tab **Source:** Tạo cột mới tên là **`Images_Public_JSON`** ở cuối bảng.
- [ ] Cập nhật Apps Script `pool_backend_v3.gs`:
  - Đồng bộ cột `Images_Admin_JSON` từ Pool sang `Images_Public_JSON` của Source thông qua bộ lọc bảo mật:
    - Apps Script khi sync sẽ lọc chuỗi JSON, chỉ giữ lại các ảnh hoạt động có role Public (`interior`, `alley`, `background`) và `is_hidden = 0`.
    - Sắp xếp tăng dần theo `sequence_index` và xuất ra mảng URL phẳng rút gọn: `["url1.jpg", "url2.jpg", ...]`.
    - Ghi chuỗi mảng URL sạch này vào cột `Images_Public_JSON` trên Source.
- [ ] Vẫn duy trì Smart Merge các cột phẳng bình thường (`anh_1` đến `anh_15` trên Source).
- [ ] **Đồng bộ tự động từ Sheets về SQLite local (`restore_db_from_sheets.py`):** Khi khôi phục database SQLite từ Google Sheets, script `restore_db_from_sheets.py` phải tự động dựng lại (reconstruct) trường `curated_config_json` và đồng bộ đầy đủ dữ liệu ảnh vào bảng `listings_images`:
  - Đọc và phân giải từ trường `Images_Admin_JSON` (nếu có dữ liệu JSON admin hợp lệ trên Sheets).
  - Nếu trường `Images_Admin_JSON` rỗng hoặc lỗi, tự động dựng lại từ các cột phẳng thô và danh sách chỉ mục công khai (`Ảnh Public (VD: 1,3,5)` / `Ảnh Hẻm Public (VD: 1,2)`) để xác định đúng ảnh nào bị ẩn/hiện và giữ vai trò ảnh tương ứng.

### 3. Vercel Admin UI Curation
- [ ] Cho phép Admin thay đổi vai trò (role) của bất kỳ ảnh nào trên giao diện (cả Public: `alley`, `interior`, `background` và Private: `facade`, `diagram`). Tính năng đổi các role này đã có trên giao diện, cần nâng cấp phần lưu JSON và bỏ giới hạn 15 ảnh được chọn.
- [ ] **Bảo toàn Vai trò Ảnh ẩn:** Khi Admin click nút **Ẩn** trên giao diện Curation Panel, giữ nguyên vai trò gốc của hình ảnh (ví dụ: `"Nội thất"`, `"Hẻm"`) và đặt `visible = false` thay vì chuyển đổi vai trò thành `"Ẩn"` / `"hidden"`.
- [ ] **Lọc Ảnh ẩn khỏi Chỉ mục Công khai:** Đảm bảo hàm tổng hợp payload (`compileListingPayload`) loại bỏ hoàn toàn các ảnh bị ẩn (`visible === false` hoặc `role` thuộc nhóm ẩn/đã xóa) ra khỏi danh sách chỉ mục công khai (`Anh_Public_VD_1_3_5` và `Anh_Hem_Public_VD_1_2`) để không hiển thị lên Vercel Client View.
- [ ] Loại bỏ giới hạn tối đa 15 ảnh khi lưu trữ. Cho phép lưu trữ và sắp xếp toàn bộ danh sách ảnh.
- [ ] Kéo thả hoặc di chuyển thứ tự trên UI là tương tác client-side thuần túy (chưa gọi backend).
- [ ] **Hành động Lưu (Con người bấm nút):** Khi Admin click nút "Lưu thay đổi" (hoặc "Lên sóng"):
  - API `/api/listings/save` được gọi gửi mảng JSON ảnh curated.
  - Backend cập nhật bảng `listings_images` và 2 trường JSON (`images_admin_json`, `images_public_json`) của bảng `listings`.
  - **Ghi song song lên Sheets Pool & Source:** Backend đồng thời:
    - Ghi chuỗi JSON admin vào cột **`Images_Admin_JSON`** trên tab Pool.
    - Ghi chuỗi JSON public sạch vào cột **`Images_Public_JSON`** trên tab Source.
    - Ghi song song đầy đủ vào 35 cột phẳng thô của tab Pool (`Hinh_Hem_1-10`, `Anh_1-25`).
    - Cập nhật ảnh đại diện mặt tiền và ảnh sơ đồ vào các cột xem trước trực quan (`Hình Mặt Tiền` công thức `=IMAGE()` và `Sơ đồ thửa đất 1-5` trên Sheets).
    - Phân rã mảng ảnh curated, lọc bỏ ảnh ẩn/private và ghi tối đa 15 ảnh public đầu đã sắp xếp vào 15 cột phẳng public (`anh_1` đến `anh_15`) trên tab Source.

### 4. Vercel Client View (Guest)
- [ ] Trang chi tiết Khách hàng (`lego_detail_client.js`) đọc trực tiếp cột **`Images_Public_JSON`** từ Source để hiển thị đầy đủ hình ảnh (không giới hạn 15 ảnh).
- [ ] **Logic Fallback:** Nếu cột `Images_Public_JSON` chưa tồn tại hoặc rỗng, Client tự động chuyển sang đọc và render ảnh từ 15 cột phẳng public cũ (`anh_1` đến `anh_15`) để bảo đảm tương thích ngược.

---

## Sơ đồ Quy trình Hoạt động (System Architecture Sequence Diagram)

```mermaid
sequenceDiagram
    actor Admin as Admin (Người biên tập)
    participant AdminUI as Vercel Admin UI (Browser)
    participant Backend as FastAPI Server (Local Python)
    database SQLite as CSDL SQLite (listings & listings_images)
    participant SheetsPool as Google Sheets (Tab Pool)
    participant AppsScript as Google Apps Script
    participant SheetsSource as Google Sheets (Tab Source)
    actor Guest as Khách hàng cuối (Client Viewer)
    participant GuestUI as Vercel Client UI (Browser)

    %% Luồng 1: Biên Tập Ảnh (Vercel Admin Curation)
    Note over Admin, AdminUI: Admin biên tập ảnh trên giao diện Curation
    Admin->>AdminUI: Kéo thả xếp thứ tự, ẩn/hiện, chọn role (mặt tiền, sơ đồ, hẻm, nội thất)
    Note over AdminUI: Thao tác Client-side thuần túy (Chưa gọi server)
    
    Admin->>AdminUI: Bấm nút "Lưu thay đổi" (hoặc "Lên sóng")
    AdminUI->>Backend: 1. POST /api/listings/save (payload JSON: system_id, images list)
    
    Backend->>Backend: Xác thực token & lọc dữ liệu
    Backend->>SQLite: Ghi bảng listings_images (system_id, tk_id, url, role, seq, is_hidden)
    Backend->>SQLite: UPDATE listings SET images_admin_json = ?, images_public_json = ? WHERE tk_id = ?
    
    Backend->>Backend: Ghi song song dữ liệu Pool & Source
    Backend->>SheetsPool: 2a. Ghi cột Images_Admin_JSON mới + 35 Cột phẳng thô cũ (Anh_1-25, Hinh_Hem_1-10)
    Backend->>SheetsSource: 2b. Ghi cột Images_Public_JSON mới + 15 Cột phẳng public (anh_1 đến anh_15) + Cột preview mặt tiền/sơ đồ
    Backend-->>AdminUI: Phản hồi Success
    AdminUI-->>Admin: Hiển thị thông báo thành công

    %% Luồng 2: Đồng bộ ngầm Sheets
    Note over SheetsPool, SheetsSource: Đồng bộ ngầm (Smart Merge)
    AppsScript->>SheetsPool: Đọc dữ liệu
    AppsScript->>SheetsSource: 3. smartMerge() ghi đè 15 cột phẳng và cột Images_Public_JSON (đã lọc ảnh Private)

    %% Luồng 3: Hiển thị Khách hàng cuối
    Guest->>GuestUI: Truy cập trang chi tiết nhà
    GuestUI->>SheetsSource: 4. gviz Query lấy dữ liệu (Images_Public_JSON + 15 Cột phẳng)
    GuestUI->>GuestUI: Đọc cột Images_Public_JSON
    alt Có Images_Public_JSON
        GuestUI->>GuestUI: Render Carousel đầy đủ từ JSON (Đã sắp xếp)
    else Không có Images_Public_JSON (Fallback)
        GuestUI->>GuestUI: Render Carousel giới hạn từ 15 cột phẳng (anh_1 đến anh_15)
    end
    GuestUI-->>Guest: Hiển thị ảnh công khai đúng thứ tự
```

> [!NOTE]
> **Quy ước đánh số hành động trên sơ đồ:**
> - **Các bước có đánh số (1., 2a., 2b., 3., 4.):** Biểu diễn **Tác vụ kích hoạt chính hoặc Trao đổi dữ liệu liên hệ thống** (Giao tiếp HTTP API hoặc liên kết đồng bộ giữa Client - Python Server - Google Sheets Cloud).
> - **Các bước không đánh số (Tương tác UI, Gọi hàm, Ghi SQLite...):** Biểu diễn **Thao tác UI Client-side hoặc Xử lý logic nội bộ**.

---

## Thiết Kế Logic Cấp Thấp (Technical Design)

### 1. Hộp đen dữ liệu (I/O Contracts)
*   **Hàm `update_listing_curation(listing_id, images_payload)`:**
    *   **Input:** Payload từ Frontend gửi lên API `/api/listings/save`:
        ```json
        {
          "system_id": "MWMSTIAHIST",
          "tk_id": "TK-12345",
          "images": [
            {"image_url": "url1.jpg", "role": "interior", "sequence_index": 0, "is_hidden": 0},
            {"image_url": "url2.jpg", "role": "alley", "sequence_index": 1, "is_hidden": 0},
            {"image_url": "url3.jpg", "role": "facade", "sequence_index": 2, "is_hidden": 0},
            {"image_url": "url4.jpg", "role": "interior", "sequence_index": 3, "is_hidden": 1}
          ]
        }
        ```
    *   **Process:**
        1. Duyệt qua mảng `images` trong payload.
        2. Chạy lệnh SQL `INSERT OR REPLACE INTO listings_images (tk_id, system_id, image_url, role, sequence_index, is_hidden) VALUES (?, ?, ?, ?, ?, ?)`.
        3. Compile toàn bộ mảng ảnh thành chuỗi `images_admin_json`.
        4. Lọc bỏ ảnh ẩn/private (`facade`, `diagram`) và compile các ảnh public sắp xếp thành `images_public_json`: `["url1.jpg", "url2.jpg"]`.
        5. Cập nhật trường `images_admin_json` và `images_public_json` của bảng **`listings`** trong SQLite (SQL v1).
        6. Đồng bộ lên Sheets Pool:
           - Ghi chuỗi JSON admin vào cột `Images_Admin_JSON`.
           - Phân rã mảng ảnh (tối đa 25 ảnh `interior` và 10 ảnh `alley` thô) ghi đè song song vào 35 cột phẳng cũ trên Pool sheet.
        7. Đồng bộ lên Sheets Source:
           - Ghi chuỗi JSON public sạch vào cột `Images_Public_JSON`.
           - Ghi song song danh sách tối đa 15 ảnh public đầu đã sắp xếp vào 15 cột phẳng public (`anh_1` đến `anh_15`) trên Source sheet.
           - Ghi ảnh đại diện mặt tiền và ảnh sơ đồ vào các cột xem trước trực quan (`Hình Mặt Tiền` công thức `=IMAGE()` và `Sơ đồ thửa đất 1-5` trên Sheets).
    *   **Output:** Trả về trạng thái `success: true`.

### 2. State Machine (Trạng thái ảnh Public & Private)
| Trạng thái hiện tại | Hành động từ Admin | Trạng thái mới trong SQLite/JSON | Hiển thị phía Khách hàng (Source JSON) |
| :--- | :--- | :--- | :--- |
| `is_hidden = 0`, `role: 'interior'` | Bấm nút "Ẩn" | `is_hidden = 1` | Loại bỏ hoàn toàn khỏi `Images_Public_JSON` |
| `is_hidden = 1` | Bấm nút "Hiện" | `is_hidden = 0` | Được thêm lại vào `Images_Public_JSON` |
| `role = 'interior'` (Public) | Đổi vai trò sang "Mặt Tiền" (Private) | `role = 'facade'` | Loại bỏ hoàn toàn khỏi `Images_Public_JSON` |
| `seq = 2`, `seq = 1` | Kéo thả hoán đổi | `seq = 1`, `seq = 2` | Thứ tự các phần tử trong `Images_Public_JSON` thay đổi |

### 3. Thực thi Bảo mật dữ liệu (Security Enforcement)
- **Xác thực API (Google OAuth2 verification):** Endpoint API `/api/listings/save` bắt buộc kiểm tra header `Authorization` chứa token hợp lệ. Hàm `verify_google_token()` phân tích token, nếu email không khớp whitelist của Admin sẽ trả về lỗi `403 Forbidden`.
- **Ngăn chặn rò rỉ hình ảnh:**
  - Tab Pool chứa cột `Images_Admin_JSON` (chứa toàn bộ ảnh mặt tiền/sơ đồ và ảnh ẩn). Tab này tuyệt đối bảo mật và không bao giờ chia sẻ công khai.
  - Tab Source chỉ chứa cột `Images_Public_JSON` (đã lọc sạch, chỉ gồm các URLs ảnh public, không có metadata ẩn/role/private). Khách hàng xem trang web chỉ nhận được danh sách ảnh sạch này, đảm bảo an toàn tuyệt đối.

---

## 📋 Kế hoạch triển khai & Chuẩn hóa Rule 6

### 1. Tầng Tiện ích Frontend (Utility Helpers)
- Khai báo và xuất các hàm trợ giúp phân giải chỉ số/ký tự cột động lên đối tượng toàn cục `window` trong `lego_helpers.js`.

### 2. Tầng Admin Frontend (Admin Detail & Curation)
- Xóa bỏ các khai báo hàm cục bộ trùng lặp bên trong IIFE của `lego_detail_admin.js`, chuyển sang gọi trực tiếp các hàm toàn cục từ `window`.

### 3. Tầng Trạng thái Lõi Frontend (Core State & Loading)
- Thay thế toàn bộ chỉ số gán cứng trong logic ánh xạ dòng `loadData()` của `lego_core.js` sang phân giải động tại runtime bằng các hàm toàn cục.

---

## 📝 Danh sách nhiệm vụ (Checklist)
- [ ] **Bước 1: Utility Helpers:** Cập nhật `lego_helpers.js` khai báo và xuất 5 hàm trợ giúp cột động lên `window`.
- [ ] **Bước 2: Admin UI:** Cập nhật `lego_detail_admin.js` sử dụng các hàm toàn cục của `window`.
- [ ] **Bước 3: Core Client:** Cập nhật `lego_core.js` chuyển đổi hơn 30 vị trí index tĩnh sang động hoàn toàn.
- [ ] **Bước 4: Kiểm thử:** Chạy unit tests và kiểm tra giao diện trên staging.

---

## 🧪 Kế hoạch kiểm thử & Nghiệm thu
- **Kiểm thử tự động**: Chạy `python -m pytest -s`.
- **Kiểm thử thủ công**: Deploy staging, F5 trang và verify các căn nhà hiển thị đầy đủ, đúng thứ tự ảnh.
