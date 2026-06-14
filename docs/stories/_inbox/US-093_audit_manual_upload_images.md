---
id: US-093
status: done
date: 2026-06-14
size: S
replaces: none
---

# US-093: Kiểm tra tính khả dụng và lập báo cáo hình ảnh tự tải lên (Không phải hình từ TK)

## User story
**As an** Admin  
**I want** quét toàn bộ cơ sở dữ liệu để tìm ra danh sách các căn có chứa hình ảnh do người dùng tự tải lên (local upload / custom upload, không phải từ nguồn TK) và kiểm tra tính khả dụng (xem được hay không) của các hình ảnh này  
**So that** tôi có thể phát hiện và sửa các liên kết hình ảnh bị lỗi hoặc tệp bị thiếu, đảm bảo trải nghiệm xem nhà của khách hàng luôn ổn định.

## Acceptance Criteria
- [ ] **Nhận diện đúng hình ảnh tự tải lên**:
  - Chỉ quét trên cơ sở dữ liệu Pool1 (tệp `raw_archive.db` bảng `listings`), hoàn toàn bỏ qua phiên bản 2 (`raw_archive_v2.db`).
- [ ] **Kiểm tra trạng thái lỗi/không xem được của ảnh**:
  - Đối với đường dẫn cục bộ (Local paths `/static/images/...`): Kiểm tra sự tồn tại vật lý của tệp trên máy chủ.
  - Đối với đường dẫn URL đám mây (Cloudinary, Cloudflare R2, Google Drive, v.v.): Thực hiện kiểm tra HTTP HEAD/GET (streamed) và xác thực mã trạng thái (chấp nhận 200 OK, gắn cờ lỗi cho 404, 403, 500, lỗi DNS, hoặc timeout).
- [ ] **Xuất báo cáo chi tiết hợp nhất (3 danh sách có đề mục `##`)**:
  - Cấu trúc lại tệp `broken_listings_report.md` thành 3 đề mục `##` riêng biệt để dễ dàng collapse trên trình soạn thảo.
  - **Danh sách 1 (`##`):** Các căn lỗi ảnh Cloudinary 404 trên Google Sheets Pool (v1) (đọc và cập nhật/bảo toàn từ tệp cũ).
  - **Danh sách 2 (`##`):** Các căn lỗi ảnh Cloudinary 404 trong SQLite `raw_archive.db` (đọc và cập nhật/bảo toàn từ tệp cũ).
  - **Danh sách 3 (`##`):** Các căn có hình ảnh tự tải lên (Local, Drive, R2, Custom Cloudinary) và tình trạng hình ảnh tương ứng (liệt kê rõ tình trạng: `✅ OK Hết` hoặc chi tiết `❌ Lỗi ảnh tự tải` với nguyên nhân lỗi).
  - Ghi đè báo cáo hợp nhất hoàn chỉnh vào tệp `broken_listings_report.md` tại thư mục gốc của dự án.

## Solution

### 1. Phân loại hình ảnh tự tải lên (Manual Upload vs TK)
Hình ảnh trong hệ thống gồm các nguồn:
- **Ảnh thô từ TK**: Có URL chứa các host của TK như `data.thienkhoi.com`, `assets.spms2.com`, `tk-assets.spms2.com`.
- **Ảnh di cư tự động từ TK sang R2/Cloudinary**: Có tên tệp theo định dạng `{tk_id}_img_{tk_id}_{idx}.jpg` hoặc chứa `/BDS-KhangNgo/{tk_id}_img_`.
- **Ảnh tự tải lên của Admin**:
  - Lưu cục bộ (khi không cấu hình R2/Cloudinary): `/static/images/{tk_id}/{filename}` (với filename dạng `img_{tk_id}_{idx}.jpg` hoặc các ảnh upload tự do).
  - Upload lên R2/Cloudinary qua Web Admin: tên tệp chứa `_interior_` hoặc `_sodo` kèm timestamp (Ví dụ: `SYS-MP7634YK-9F_sodo1_1780258510.jpg`, `SYS-MP7634YK-9F_interior_1780258510.jpg`).
  - Đường dẫn chia sẻ Google Drive được nhập thủ công: chứa `drive.google.com` hoặc `google.com/drive`.

Do đó, các mẫu URL được phân loại là **Tự tải lên (Manual Upload)** bao gồm:
- URL chứa `/static/images/`
- URL chứa `drive.google.com`
- URL chứa `_interior_` hoặc `_sodo`
- Các URL Cloudinary/R2 không khớp định dạng ảnh di cư của TK (`_img_`).

### 2. Thiết kế kịch bản kiểm toán (`audit_manual_images.py`)
Viết script Python `audit_manual_images.py` thực hiện:
- **Bước 1**: Xác định đường dẫn CSDL `raw_archive.db` của Pool1.
- **Bước 2**: Quét và truy vấn CSDL Pool1: Đọc bảng `listings` trong `raw_archive.db`, duyệt qua các cột hình ảnh (`Hinh_Mat_Tien`, `So_do_thua_dat_1..5`, `Hinh_Hem_1..10`, `Anh_1..25`). Hoàn toàn bỏ qua tệp `raw_archive_v2.db`.
- **Bước 3**: Lọc ra các URL hình ảnh tự tải lên theo các tiêu chí nhận diện trên.
- **Bước 4**: Kiểm thử từng URL tự tải lên được tìm thấy (hoàn toàn bỏ qua ảnh TK gốc và ảnh di cư chuẩn `_img_` đã được quản lý trong `broken_listings_report.md`):
  - Nếu là đường dẫn cục bộ (bắt đầu bằng `/static/`): Kiểm tra sự tồn tại của tệp trên đĩa cứng cục bộ.
  - Nếu là URL từ xa (bắt đầu bằng `http://` hoặc `https://`): Thực hiện HTTP HEAD/GET với thư viện `requests` kèm `timeout=5` và `stream=True`. Ghi nhận mã trạng thái phản hồi.
- **Bước 5**: Đọc và phân tích tệp `broken_listings_report.md` hiện có để trích xuất danh sách các căn lỗi ảnh di cư Cloudinary cũ (~581 căn).
- **Bước 6**: Hợp nhất danh sách ảnh tự tải lên bị lỗi mới phát hiện vào danh sách này (cập nhật thông tin cột "Cột bị lỗi ảnh" nếu trùng căn, hoặc tạo dòng mới nếu là căn mới).
- **Bước 7**: Ghi đè báo cáo hợp nhất hoàn chỉnh vào tệp `broken_listings_report.md` tại thư mục gốc của dự án.

---

## 📋 Proposed Changes

### 1. Thêm công cụ kiểm toán (`audit_manual_images.py`)
#### [NEW] [audit_manual_images.py](file:///d:/01_PROJECTS/BDS-KhangNgo/scratch/audit_manual_images.py)
* Viết script Python quét CSDL, kiểm tra ảnh cục bộ/HTTP và xuất file báo cáo Markdown.

---

## 🔍 Verification Plan

### Automated Tests
- Chạy lệnh:
  ```powershell
  python scratch/audit_manual_images.py
  ```
- Kiểm toán hoạt động của script, kiểm tra mã trạng thái trả về và đảm bảo tạo ra file báo cáo `manual_uploads_audit_report.md` đầy đủ thông tin.

### Manual Verification
- Mở xem file báo cáo `manual_uploads_audit_report.md` được sinh ra.
- Lấy ngẫu nhiên một vài liên kết bị báo lỗi để kiểm tra thực tế trên trình duyệt xem có đúng là bị lỗi (404, 403...) không.
