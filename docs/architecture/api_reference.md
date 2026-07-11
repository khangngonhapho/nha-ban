# 🔌 Tài Liệu API Tích Hợp (API Reference)

Tài liệu này cung cấp danh mục chi tiết tất cả API endpoints hoạt động trên Python Backend cục bộ phục vụ cho Chrome Extension và Vercel Admin Panel.

## 1. api/routes_config.py
Quản lý cấu hình toàn cục của hệ thống.

### GET `/api/config`
- **Mô tả:** Lấy thông tin cấu hình hiện tại từ file `settings.json`.
- **Response:**
  ```json
  {
    "active_pool_system": 2,
    "sheet_id_public_v2": "1fDe5nrllgXBdGmYXlIhlYp0sJ_BPuarpD1DjsK_7JWw",
    ...
  }
  ```

---

## 2. api/routes_pool.py
Quản lý dữ liệu rổ hàng thô (Pool).

### GET `/api/listings/structure`
- **Mô tả:** Lấy cấu trúc schema, tên cột của cơ sở dữ liệu để vẽ bảng biên tập.

### POST `/api/listings/check-exist`
- **Mô tả:** Đối soát xem một danh sách các mã Thiên Khôi `tk_id` đã tồn tại trong SQLite database cục bộ chưa.
- **Request Payload:** `{"ids": ["12345", "67890"]}`
- **Response:** `{"exist_ids": ["12345"]}`

---

## 3. api/routes_curation.py
Thực hiện các thao tác biên tập nâng cao và duyệt đăng căn nhà.

### POST `/api/curation/save-changes`
- **Mô tả:** Lưu các thay đổi biên tập của một căn đã duyệt trở lại Google Sheets Source.
- **Request Payload:** `{"id": "MH-12345", "changes": {...}}`

### POST `/api/curation/save-new-listing`
- **Mô tả:** Duyệt đăng một căn mới từ Pool sang Source Sheet, đồng thời tự động gọi OpenAI để sinh mô tả.

---

## 4. api/routes_sync.py
Đồng bộ dữ liệu cục bộ lên đám mây.

### POST `/api/sync/all-listings`
- **Mô tả:** Đồng bộ toàn bộ dữ liệu SQLite đã cập nhật (như link ảnh Cloudinary mới, Mã Khang Ngô tự sinh) lên Google Sheets Pool/Source.

---

## 5. api/routes_images.py
Quản lý hình ảnh và tích hợp Cloudinary CDN.

### POST `/api/images/upload`
- **Mô tả:** Tải một ảnh cục bộ lên Cloudinary thông qua Signed REST API.

### POST `/api/images/destroy`
- **Mô tả:** Xóa ảnh rác cũ khỏi Cloudinary bằng public_id sử dụng Destroy API có chữ ký bảo mật.

---

## 6. api/routes_crawl.py
Nhận dữ liệu từ Chrome Extension.

### POST `/api/listings/<tk_id>/recrawl`
- **Mô tả:** Ra lệnh cào mới hoặc cào lại chi tiết một căn nhà từ Thiên Khôi bằng cookie hiện hành.
