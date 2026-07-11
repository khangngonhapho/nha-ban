---
id: US-055
status: accepted
date: 2026-05-30
size: S
---

# US-055: Khắc phục triệt để lỗi ảnh Sổ đỏ hiện làm ảnh đại diện trên danh sách Admin

## User story
**As an** Admin / Broker Khang Ngô
**I want** ảnh đại diện (avatar/thumbnail) của các căn nhà trên giao diện danh sách Admin tuyệt đối không bao giờ hiển thị hình ảnh Sổ đỏ (sơ đồ thửa đất/pháp lý)
**So that** rổ hàng admin trực quan, đẹp mắt và dễ rà soát nhanh qua hình ảnh thực tế (mặt tiền/nội thất), đảm bảo bảo mật thông tin pháp lý nhạy cảm đối với cả các căn đã lên sóng và chưa lên sóng.

---

## Acceptance
- [x] **Khử triệt để hình Sổ đỏ khỏi Avatar/Cover danh sách Card:**
  - Sửa lỗi trong hàm `isListingSodoUrl` và các bộ lọc cover của `index.html` để lọc bỏ tất cả hình ảnh sơ đồ thửa đất ra khỏi danh sách ảnh public hoặc ảnh bìa mặc định.
- [x] **Mở rộng hỗ trợ toàn diện cả 5 Sơ đồ thửa đất:**
  - Hỗ trợ đầy đủ `Sơ đồ thửa đất 3`, `Sơ đồ thửa đất 4`, `Sơ đồ thửa đất 5` (các cột index 77, 78, 79 trên sheet Pool) trong mọi luồng check Sổ.
  - Hiển thị đầy đủ cả 5 ảnh Sổ này trong Carousel Sơ đồ thửa đất ở chi tiết Admin và các nhãn tím `🔒 Sổ 1` đến `🔒 Sổ 5` trong Image Curation Editor.
- [x] **Giải quyết mismatch giữa link thô Thiên Khôi và link di cư Cloudinary:**
  - Cải tiến hàm `isListingSodoUrl` trên client hỗ trợ:
    - So sánh normalized của link thô Thiên Khôi và Cloudinary.
    - Nhận diện mẫu URL Cloudinary có chứa `/sodo1_` đến `/sodo5_` để gán nhãn sodo tự động.
- [x] **Chạy công cụ sửa lỗi data hàng loạt cho dữ liệu cũ:**
  - Chạy `repair_diagrams.py --publish` để rà soát toàn bộ SQLite, di cư tất cả sơ đồ thô cũ lên Cloudinary không nén và lưu đè link Cloudinary về các cột AB, AC và Sơ đồ 3, 4, 5 trên Google Sheets Pool.

---

## Solution

### 1. Chuẩn hóa & Mở rộng trường Sơ đồ trong `index.html`:
Bổ sung mapping `raw_sodo3`, `raw_sodo4`, `raw_sodo5` khi parse dữ liệu từ Google Sheets:
- Thêm `raw_sodo3: row[77] || ''`, `raw_sodo4: row[78] || ''`, `raw_sodo5: row[79] || ''` vào `MAPPED_POOL_DATA` và các hàm parse chi tiết.
- Cập nhật hidden inputs trong `renderImageEditorWidget` để lưu trữ 5 URL Sổ.

### 2. Thiết kế cơ chế so khớp sodo thông minh (`isListingSodoUrl`):
```javascript
window.isListingSodoUrl = function(url, p) {
  if (!url || !p) return false;
  const norm = normalizeImgUrl(url);
  if (norm === '') return false;
  
  // 1. Nhận diện theo mẫu tên file Cloudinary được uploader tạo ra (cực kỳ tối ưu và nhanh)
  const urlLower = String(url).toLowerCase();
  if (urlLower.includes('/sodo1_') || urlLower.includes('/sodo2_') || 
      urlLower.includes('/sodo3_') || urlLower.includes('/sodo4_') || urlLower.includes('/sodo5_')) {
    return true;
  }

  // 2. Lấy 5 giá trị sodo hiện có của căn nhà
  const sodo1Val = p.pool_row_data ? p.pool_row_data[27] : p.raw_sodo1;
  const sodo2Val = p.pool_row_data ? p.pool_row_data[28] : p.raw_sodo2;
  const sodo3Val = p.pool_row_data ? p.pool_row_data[77] : p.raw_sodo3;
  const sodo4Val = p.pool_row_data ? p.pool_row_data[78] : p.raw_sodo4;
  const sodo5Val = p.pool_row_data ? p.pool_row_data[79] : p.raw_sodo5;

  const normS1 = normalizeImgUrl(sodo1Val);
  const normS2 = normalizeImgUrl(sodo2Val);
  const normS3 = normalizeImgUrl(sodo3Val);
  const normS4 = normalizeImgUrl(sodo4Val);
  const normS5 = normalizeImgUrl(sodo5Val);

  if (norm === normS1 || norm === normS2 || norm === normS3 || norm === normS4 || norm === normS5) {
    return true;
  }
  return false;
};
```

---

## 📋 Implementation Plan
- **Bước 1**: Cập nhật logic parse row trong `index.html` để bổ sung `raw_sodo3, 4, 5` từ Google Sheets.
- **Bước 2**: Sửa đổi `window.isListingSodoUrl` để rà soát cả 5 sodo và tích hợp nhận diện pattern `/sodo[1-5]_`.
- **Bước 3**: Cập nhật Widget Biên tập hình ảnh (`renderImageEditorWidget` và `renderImageCardForEdit`) hỗ trợ cả 5 sodo, gán nhãn viền tím vàbadge `🔒 Sổ 1-5`.
- **Bước 4**: Cập nhật Detail Carousel để hiển thị đầy đủ cả 5 sodo.
- **Bước 5**: Chạy thử script `repair_diagrams.py --publish` để cập nhật dữ liệu hình ảnh Sổ trơn trên Google Sheets.

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** Mismatch giữa URL thô từ Thiên Khôi và URL Cloudinary đã di cư khiến cho client không so khớp chính xác các ảnh Sổ đỏ cũ, dẫn đến việc chúng lọt qua bộ lọc và hiển thị làm ảnh đại diện trên danh sách Admin.
- **Nguyên nhân gốc rễ (Root Cause):** Link gốc có ký tự unicode, dấu cách hoặc cấu trúc khác biệt so với Cloudinary CDN URL, trong khi hệ thống client-side so sánh trực tiếp chuỗi URL thô dẫn đến sai lệch kết quả.
- **Giải pháp phòng ngừa:**
  1. Xây dựng hàm `normalizeImgUrl` đồng nhất hóa tất cả các URL ảnh bằng cách chuyển chữ thường, loại bỏ giao thức (http/https), loại bỏ tên miền (Cloudinary/Thiên Khôi CDN) và chỉ giữ lại phần ID file duy nhất để so khớp tuyệt đối.
  2. Bổ sung nhận diện pattern tên file Cloudinary dạng `/sodo[1-5]_` để đánh nhãn Sổ ngay lập tức mà không cần so khớp mảng.

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm code & Cấu hình:** Khi thêm các cột dữ liệu mới vào Google Sheets nghiệp vụ của rổ hàng, hãy luôn chèn chúng ở đáy bảng (sau các cột cũ) thay vì chèn vào giữa, nhằm triệt tiêu hoàn toàn rủi ro column-shift phá vỡ các chỉ số mảng cứng ở client frontend.
- **Kinh nghiệm kiểm thử:** Sử dụng script `repair_diagrams.py` quét SQLite cục bộ kết hợp cờ `--publish` để đồng bộ an toàn dữ liệu hình ảnh Sổ đỏ đã di cư lên Google Sheets Pool một cách hàng loạt mà không làm trôi dữ liệu curation hiện hữu.

---

## Files touched
- `index.html` — Cập nhật luồng nhận diện Sổ 1-5, Carousel hiển thị và Editor Widget
- `docs/stories/US-055_fix_admin_avatar_sodo.md` — [NEW] Tài liệu hóa câu chuyện người dùng và bài học kinh nghiệm

