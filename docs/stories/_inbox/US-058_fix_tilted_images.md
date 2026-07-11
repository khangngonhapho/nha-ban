---
id: US-058
status: accepted
date: 2026-06-01
size: M
---

# US-058: Quét, xoay ảnh thẳng đứng vật lý và tự động dọn dẹp bộ nhớ ảnh lỗi cũ trên Cloudinary cho rổ hàng đã di cư

## User story
**As an** Admin / Broker Khang Ngô
**I want** hệ thống tự động phát hiện, tải lại ảnh gốc từ Thiên Khôi, xoay đứng thẳng vật lý (EXIF Orientation), nén tối ưu dung lượng và dọn dẹp sạch sẽ các ảnh lỗi cũ nghiêng 90 độ trên Cloudinary cho toàn bộ 5.714 căn published cũ đã di cư
**So that** rổ hàng hiển thị ảnh thẳng đứng 100% chuyên nghiệp trên giao diện Web Admin, đồng thời giải phóng hoàn toàn dung lượng lưu trữ Cloudinary bị chiếm dụng bởi các tập tin rác cũ.

---

## Acceptance
- [x] **Quét nhanh EXIF đa luồng song song (Early Stopping Batch Scanner):**
  - Quét 5.714 căn published cũ trong SQLite database, kiểm tra thẻ EXIF Orientation của ảnh gốc Thiên Khôi để lọc ra các căn bị lỗi nghiêng 90 độ.
  - Sử dụng cơ chế phân lô quét dừng sớm (Early Stopping) để tối ưu hóa hiệu suất mạng.
- [x] **Xóa ảnh cũ chủ động trên Cloudinary (Signed Destroy API):**
  - Tích hợp gọi API Signed Destroy của Cloudinary (`/image/destroy`) bằng chữ ký bảo mật SHA-1.
  - Tự động trích xuất `public_id` từ các liên kết cũ và xóa sạch toàn bộ ảnh cũ bị nghiêng trước khi upload ảnh mới lên.
- [x] **Xoay đứng thẳng vật lý & Nén tối ưu:**
  - Tự động cào lại trang chi tiết gốc của Thiên Khôi bằng cookie mới nếu mảng ảnh thô bị mất.
  - Thực hiện xoay thẳng đứng vật lý dựa trên EXIF qua Pillow (`ImageOps.exif_transpose`) và nén JPEG giảm dung lượng từ 40% đến 80% mà vẫn giữ nguyên độ nét.
- [x] **Đồng bộ chép đè Google Sheets Pool:**
  - Định vị chính xác dòng BĐS trong Sheets Pool (ví dụ dòng 807 cho 17 Vũ Tùng, dòng 2147...).
  - Thực hiện đồng bộ chép đè không phá hủy chỉ riêng cột hình ảnh và thời gian cập nhật thông tin (`Last_Sync`).

---

## Solution Implemented

### 1. File xử lý cốt lõi `fix_tilted_images.py`:
- Tạo script [fix_tilted_images.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/fix_tilted_images.py) hỗ trợ đầy đủ các tham số `--dry-run`, `--limit`, `--all`, và `--tk-id`.
- Tích hợp cơ chế dọn dẹp Cloudinary Signed Destroy API:
  - `extract_cloudinary_public_id(url)`: Trích xuất `public_id` từ URL CDN của Cloudinary.
  - `delete_cloudinary_image(public_id, cfg)`: Sinh chữ ký SHA-1 và gọi API destroy để xóa ảnh.
  - `delete_old_cloudinary_images_for_listing(old_images_json, cfg)`: Vòng lặp dọn dẹp sạch sẽ toàn bộ danh sách ảnh cũ.

---

## 📋 Implementation Plan & Execution Summary
- **Bước 1**: Triển khai các hàm trích xuất và xóa ảnh Cloudinary trong `fix_tilted_images.py`.
- **Bước 2**: Chạy thử nghiệm thành công 5 căn test cũ và căn 17 Vũ Tùng (`ey4mbj-lvcjwvqn-41094ab3` dòng 807).
- **Bước 3**: Viết thêm script dọn dẹp hồi tố [cleanup_previous_listings.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/cleanup_previous_listings.py) dọn sạch 31 ảnh rác cũ của 5 căn test đầu tiên.
- **Bước 4**: Chạy ngầm hàng loạt cho toàn rổ hàng qua đêm (`python fix_tilted_images.py --all`) hoàn thành sửa đổi và dọn dẹp 893/893 căn bị ảnh hưởng trong vòng 12 tiếng.

---

## Files touched
- `fix_tilted_images.py` — [NEW] Script quét và sửa ảnh xoay hàng loạt + xóa ảnh Cloudinary cũ
- `scratch/cleanup_previous_listings.py` — [NEW] Script dọn dẹp hồi tố 5 căn test cũ
- `docs/stories/US-058_fix_tilted_images.md` — [NEW] Tài liệu hóa câu chuyện người dùng hoàn thành
- `docs/stories/INDEX.md` — Cập nhật thống kê nghiệm thu cho US-058
- `docs/NEXT_SESSION.md` — Ghi nhận nhật ký nâng cấp và dọn dẹp phiên tiếp theo

---

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** Quá trình quét hàng loạt 5.714 căn đòi hỏi lượng lớn kết nối HTTP để kiểm tra EXIF của Thiên Khôi, dễ bị tường lửa (WAF) chặn IP tạm thời hoặc hết hạn Cookie giữa chừng (chuyển hướng 302 về `security.html`).
- **Giải pháp khắc phục:** 
  1. Sử dụng thuật toán quét đa luồng phân lô dừng sớm (Early Stopping) giúp thu hẹp phạm vi quét tức thì.
  2. Triển khai cơ chế 2 Pha: Tách biệt hoàn toàn pha Cào EXIF (cần Cookie xác thực) và pha Download/Upload/Sync (chỉ cần tải từ CDN công khai `tk-assets.spms2.com` không cần Cookie). Điều này giúp script chạy mượt mà đến cuối cùng ngay cả khi session cookie hết hạn giữa chừng!

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm lập trình:** Khi tích hợp các tác vụ dọn dẹp Cloudinary hàng loạt, luôn bọc trong cơ chế try-except độc lập và xử lý ngoại lệ cẩn thận để các lỗi mạng Cloudinary không bao giờ làm gián đoạn tiến trình đồng bộ Sheets và SQLite chính.
