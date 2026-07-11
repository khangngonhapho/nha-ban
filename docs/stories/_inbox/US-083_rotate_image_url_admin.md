---
id: US-083
status: accepted
date: 2026-06-09
size: S
---

# US-083: Bổ sung tính năng xoay ảnh bằng chuyển đổi URL Cloudinary trực tiếp trên Web Admin

## User story
**As an** Admin biên tập rổ hàng bất động sản
**I want** có công cụ xoay ảnh nhanh (Rotate 90° / 180° / 270°) ngay trên giao diện Quản lý hình ảnh của Web Admin
**So that** tôi có thể khắc phục ngay lập tức các ảnh bị ngược, nghiêng bằng cách biến đổi URL Cloudinary mà không cần tải lại, sửa ảnh thủ công hoặc chạy các script cào lại phức tạp.

## Acceptance
- [x] **Bổ sung UI xoay ảnh:**
  - Trên các panel hiển thị hình ảnh trong Web Admin (Biên tập hình ảnh, preview, quản lý tags), dưới mỗi ảnh hoặc khi rê chuột vào ảnh sẽ xuất hiện nút/icon xoay ảnh (ví dụ: biểu tượng xoay `🔄` hoặc nút "Xoay 90°").
- [x] **Chuyển đổi URL Cloudinary động:**
  - Khi người dùng click nút xoay:
    - Nếu ảnh là ảnh Cloudinary (`cloudinary.com`): Tự động chèn/cập nhật tham số `a_90`, `a_180`, `a_270` (hoặc `a_-90`) vào ngay sau phân đoạn `/upload/` của URL.
    - Xoay lũy tiến: Mỗi lần click sẽ xoay thêm 90 độ (Mặc định -> 90° -> 180° -> 270° -> Mặc định).
    - Cập nhật lập tức ảnh hiển thị (Preview) trên giao diện để người dùng thấy kết quả xoay trực quan.
  - Nếu ảnh là ảnh gốc chưa di cư (không phải Cloudinary): Nút xoay bị mờ (disabled) hoặc hiển thị thông báo cần di cư ảnh trước khi xoay.
- [x] **Đồng bộ về CSDL:**
  - URL ảnh sau khi xoay (có chứa tham số `a_xx`) sẽ được lưu vào danh sách ảnh khi admin bấm "Lưu Curation" hoặc "Xuất bản", đồng bộ xuống SQLite database và Google Sheets Pool.

## Solution

> [!note]- Hướng tiếp cận kỹ thuật
> **1. Biến đổi URL Cloudinary:**
> Một URL Cloudinary có dạng:
> `https://res.cloudinary.com/deru9p712/image/upload/v1779917190/BDS-KhangNgo/.../neqs6we9lcjdxpc7bhpu.jpg`
> Khi xoay 90 độ, URL mới sẽ là:
> `https://res.cloudinary.com/deru9p712/image/upload/a_90/v1779917190/BDS-KhangNgo/.../neqs6we9lcjdxpc7bhpu.jpg`
>
> Thuật toán JS để xử lý biến đổi góc xoay trong URL Cloudinary:
> ```javascript
> function rotateCloudinaryUrl(url, angleOffset = 90) {
>   if (!url || !url.includes("cloudinary.com/")) return url;
>   
>   // Tìm vị trí của /upload/
>   const uploadMarker = "/upload/";
>   const index = url.indexOf(uploadMarker);
>   if (index === -1) return url;
>   
>   const prefix = url.substring(0, index + uploadMarker.length);
>   let remaining = url.substring(index + uploadMarker.length);
>   
>   // Kiểm tra xem đã có sẵn cấu hình xoay chưa (ví dụ: a_90, a_180, a_270, a_-90)
>   const rotationRegex = /^a_(-?\d+)\//;
>   const match = remaining.match(rotationRegex);
>   
>   let currentAngle = 0;
>   if (match) {
>     currentAngle = parseInt(match[1], 10);
>     remaining = remaining.replace(rotationRegex, ""); // Loại bỏ tham số xoay cũ
>   }
>   
>   // Tính toán góc xoay mới
>   let newAngle = (currentAngle + angleOffset) % 360;
>   if (newAngle < 0) newAngle += 360;
>   
>   if (newAngle === 0) {
>     return prefix + remaining; // Không xoay (trở về gốc)
>   } else {
>     return prefix + `a_${newAngle}/` + remaining;
>   }
> }
> ```
>
> **2. Tích hợp UI trong `index.html`:**
> - Trong phần quản lý danh sách hình ảnh biên tập (`#admin-image-list` hoặc tương đương), thêm một wrapper hoặc overlay chứa button xoay nhanh.
> - Khi nhấn nút, thực hiện cập nhật mảng URL ảnh của căn nhà đang biên tập và reload lại danh sách ảnh xem trước.

## 📋 Implementation Plan
- **Bước 1:** Bổ sung hàm tiện ích `rotateCloudinaryUrl` vào thẻ `<script>` trong [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html).
- **Bước 2:** Định vị vùng render danh sách ảnh trong modal biên tập admin (hàm render danh sách ảnh trong `index.html`).
- **Bước 3:** Thêm nút xoay ảnh bên cạnh hoặc đè lên trên mỗi thumbnail ảnh.
- **Bước 4:** Lập trình sự kiện click để gọi hàm `rotateCloudinaryUrl`, cập nhật thuộc tính `src` của thumbnail xem trước và gán lại URL mới vào mảng ảnh của căn nhà để khi lưu sẽ gửi lên server lưu vào SQLite/Sheets.

## 📋 Task Checklist (TODO)
- [x] **Nghiên cứu & Thiết kế:**
  - [x] Xác định vị trí code hiển thị ảnh trong Web Admin ở [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html).
  - [x] Test thử nghiệm giải pháp xoay ảnh bằng Cloudinary URL transformation trực tiếp trên browser.
- [x] **Phát triển UI/UX:**
  - [x] Thêm nút xoay (icon rotate) vào giao diện quản lý ảnh ở trang Admin.
  - [x] Thêm hiệu ứng hover đẹp mắt, chỉ hiển thị nút khi rê chuột vào ảnh.
- [x] **Phát triển Logic:**
  - [x] Triển khai hàm `rotateCloudinaryUrl` trong file `index.html`.
  - [x] Ràng buộc sự kiện click để cập nhật danh sách ảnh đang được lưu giữ trong form biên tập.
- [x] **Kiểm thử & Nghiệm thu:**
  - [x] Kiểm tra tính năng xoay ảnh hoạt động đúng cho ảnh Cloudinary (URL đổi thành `/upload/a_90/...`).
  - [x] Xác nhận ảnh sau khi lưu được đồng bộ chính xác xuống Google Sheets Pool và SQLite.
  - [x] Kiểm tra khả năng tương thích hiển thị trên Mobile và Laptop.

## Files touched
- `index.html` — Thêm UI nút xoay ảnh và logic biến đổi URL Cloudinary
- `curator.html` — Thêm nút xoay hình ảnh riêng lẻ trong Tab Biên tập & Xuất bản của Curation App
- `docs/stories/INDEX.md` — Cập nhật mục lục story INDEX.md

## 🧠 Retro, Lessons Learned & Good Practices

### Incidents & Root Causes
- **Incident:** Khi nhấn "Xoay tất cả +90°", ảnh hiển thị bị xoay đúng góc nhưng khi nhấn vào nút kính lúp `🔍` ở trung tâm để xem full-size, ảnh mở ra vẫn là ảnh gốc (chưa xoay).
- **Root Cause:** Hàm `window.rotateAllListingImages` không cập nhật lại thuộc tính `onclick` của `.view-full-center-btn` để trỏ tới `newUrl`.
- **Resolution:** Thêm logic tìm kiếm `.view-full-center-btn` và dùng `.setAttribute('onclick', ...)` để cập nhật link động tương tự như hàm `rotateSingleCurationImage`.

### Good Practices
- Sử dụng `event.stopPropagation()` trên các nút hành động nằm chồng trên một card có thể click (như chọn vai trò, xem full-size) để tránh kích hoạt sự kiện click của thẻ cha (tránh chọn sai/tự động toggle trạng thái).
- Xử lý Cloudinary URL bằng regex giúp giữ nguyên phiên bản ảnh (`v1779917190/...`) và chỉ chỉnh sửa tham số `a_XX` động ngay sau `/upload/` một cách sạch sẽ.
