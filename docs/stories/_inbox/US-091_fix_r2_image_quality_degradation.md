---
id: US-091
status: backlog
date: 2026-06-13
size: M
replaces: none
---

# US-091: Khắc phục lỗi giảm chất lượng hình ảnh quá mức khi di cư sang R2

## User story
**As an** Admin  
**I want** tìm giải pháp khắc phục hiện tượng suy giảm chất lượng hình ảnh và sơ đồ quá mức (bị mờ, vỡ hạt) trên các căn đã di cư sang R2 và các căn cào mới  
**So that** hình ảnh hiển thị trên website client sắc nét như ảnh gốc của TK, đem lại trải nghiệm xem nhà cao cấp cho khách hàng.

## Acceptance Criteria
- [ ] **Bảo toàn chất lượng cho các căn cào mới**:
  - Không nén hoặc nén tối thiểu ảnh Sơ đồ (bypass 100% việc nén, giữ nguyên độ chi tiết).
  - Đối với ảnh thông thường (Nội thất / Hẻm / Mặt tiền): Áp dụng **Thuật toán Nén Động** (nhận diện dung lượng và độ phân giải gốc để đặt quality phù hợp 95 / 85 / 82, giới hạn kích thước tối đa 1600px để đạt đích 180 KB - 200 KB).
- [ ] **Khôi phục chất lượng hình ảnh cho các căn đã di cư sang R2**:
  - Viết script quét các căn đã di cư sang R2, lấy thông tin `tk_id`, gọi API TK để lấy liên kết hình ảnh gốc chất lượng cao chưa nén.
  - Tải ảnh gốc từ TK, áp dụng đúng tỷ lệ nén phân loại (Sơ đồ: không nén; Nội thất/Hẻm: nén động 95 / 85 / 82 với max size 1600px) và ghi đè (overwrite) lên R2.
- [ ] **Không làm thay đổi cấu trúc URL trên Sheets & CSDL**:
  - Giữ nguyên các liên kết R2 hiện tại (tên file R2 không đổi) để tránh lỗi lệch link hoặc phải đồng bộ lại từ đầu trên Google Sheets.

## Solution

### 1. Nguyên nhân gốc rễ (Root Cause)
*   **Quá trình Cào cũ:** Khi cào dữ liệu, script `manager.py` tự động nén toàn bộ hình ảnh thông thường về chất lượng JPEG 75 và kích thước tối đa 1600x1600 bằng hàm `compress_image()` để tiết kiệm hạn mức biến đổi (credits) của Cloudinary cũ.
*   **Quá trình Di cư:** Script di cư `migrate_to_r2.py` tải các hình ảnh đã bị nén sẵn từ Cloudinary về và đẩy lên R2, dẫn đến chất lượng ảnh trên R2 bị giảm sút nghiêm trọng so với ảnh gốc trên trang TK.
*   **Sự khác biệt R2 vs Cloudinary:** Cloudflare R2 là kho lưu trữ đối tượng S3 tiêu chuẩn, băng thông tải (egress) miễn phí 100% và chi phí dung lượng cực kỳ rẻ. Do đó, việc nén ảnh chặt chẽ là không cần thiết đối với R2.

### 2. Thiết kế giải pháp kỹ thuật
*   **Tối ưu hóa luồng cào mới (`manager.py`):**
    *   Tích hợp bộ quy tắc **Nén Động Nhận diện Chất lượng** để đạt mốc dung lượng mục tiêu 180 KB - 200 KB:
        1. Ảnh nhỏ pre-compressed (< 200KB và <= 1200px): Nén tối thiểu Quality 95 / không resize.
        2. Ảnh tiêu chuẩn (200KB - 1.5MB): Nén Quality 85, max size 1600px.
        3. Ảnh siêu nặng (> 1.5MB): Nén Quality 82, max size 1600px.
*   **Script khôi phục ảnh cũ (`restore_r2_quality.py`):**
    *   Gọi API TK details `https://backend.thienkhoi.com/product/v1/property/<tk_id>` lấy link ảnh gốc chưa nén.
    *   Tải ảnh gốc về, áp dụng luật nén động phân loại để đưa dung lượng về 180-200KB và tải lên R2 dưới dạng ghi đè (Overwrite) lên chính tên file R2 cũ.

---

## 📋 Proposed Changes

### 1. Phân hệ Cào mới (`manager.py`)

#### [MODIFY] [manager.py](file:///D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py)
* Cập nhật hàm `compress_image` để nâng cao độ nét và nén động đạt đích 180-200KB:
  ```python
  def compress_image(image_bytes, max_size=(1600, 1600), quality=85):
      img = Image.open(io.BytesIO(image_bytes))
      width, height = img.size
      orig_len = len(image_bytes)
      
      if max(width, height) <= 1200 and orig_len < 200 * 1024:
          quality = 95
          max_size = (width, height)
      elif orig_len > 1.5 * 1024 * 1024:
          quality = 82
          max_size = (1600, 1600)
      else:
          quality = 85
          max_size = (1600, 1600)
      # ... tiếp tục xử lý nén bằng Pillow
  ```
* Giữ nguyên cơ chế bypass nén cho ảnh sơ đồ thửa đất (`is_diagram = True`).

### 2. Viết Script khôi phục chất lượng ảnh cũ (`restore_r2_quality.py`)

#### [NEW] [restore_r2_quality.py](file:///D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/restore_r2_quality.py)
* Tạo script Python chạy một lần (one-time recovery utility):
  1. Đọc danh sách listings từ `raw_archive.db`.
  2. Lọc danh sách `tk_id` cần khôi phục (theo phương án A hoặc B được duyệt).
  3. Sử dụng Cookie từ `thienkhoi_cookie.txt` để gọi API TK: `https://backend.thienkhoi.com/product/v1/property/{tk_id}`.
  4. Nếu gặp lỗi 401/403, tự động gọi `try_refresh_tokens` từ `fetcher.py` để lấy Token mới.
  5. Trích xuất danh sách liên kết ảnh gốc từ trường `media` (bảo toàn trình tự nội thất và sơ đồ).
  6. So khớp thứ tự 1-to-1 với danh sách R2 URLs hiện có của căn nhà đó trong SQLite `raw_images_tk_json`.
  7. Tải ảnh chất lượng cao chưa nén từ TK, xoay đứng vật lý (nếu cần):
     * Nếu là ảnh Sơ đồ (`is_diagram = True`): Giữ nguyên bytes gốc không nén.
     * Nếu là ảnh Nội thất/Hẻm: Áp dụng **Thuật toán Nén Động** để đưa dung lượng về mốc **180 KB - 200 KB** (quality 82 - 85, max size 1600px).
  8. Thực hiện tải lên (PUT) ghi đè trực tiếp lên R2 với đúng tên file cũ (ví dụ: `BDS-KhangNgo/{tk_id}_img_{tk_id}_{idx}.jpg`), tự động xác định `Content-Type` chuẩn.
  9. Sử dụng cơ chế đa luồng `ThreadPoolExecutor` (khoảng 8-10 workers) để thực thi tải và upload song song, tối đa hóa băng thông.

---

## 🔍 Verification Plan

### Kiểm thử Tự động (Script Dry-run)
* Viết kịch bản chạy thử nghiệm trên **3 căn nhà mẫu**:
  * Tải ảnh gốc từ TK, so sánh dung lượng và kích thước ảnh tải về.
  * Tải lên R2 thành công và in ra logs xác nhận.
  * Đọc kiểm tra trực tiếp từ R2 URL xem hình ảnh đã được cập nhật file mới chưa.

### Kiểm thử Thủ công (Visual QA)
* Mở trình duyệt, truy cập trực tiếp vào 3 URL ảnh R2 trước và sau khi khôi phục để so sánh độ nét trực quan (ví dụ: zoom kỹ chữ viết trên sơ đồ thửa đất, hoặc các chi tiết gạch, rèm cửa của ảnh nội thất).

