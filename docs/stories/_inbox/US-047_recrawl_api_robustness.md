---
id: US-047
status: accepted
date: 2026-05-30
size: S
---

# US-047: Nâng cấp độ tin cậy và chống lỗi gọi API Cào lại căn nhà (Curator Recrawl API Robustness & Safety)

## User story
**As a** Curator / Broker Khang Ngô  
**I want** chức năng "Cào lại căn này" (Recrawl) tự động phát hiện hết hạn Cookie và hiển thị thông báo lỗi thân thiện thay vì bị crash chuỗi JSON (`Unexpected token '<'`), đồng thời ngăn chặn ghi đè làm trống dữ liệu cũ nếu Thiên Khôi chuyển hướng về trang Đăng nhập và trích xuất đúng 100% nội dung mô tả chi tiết ngay cả khi đoạn văn chứa các liên kết Zalo/Facebook.  
**So that** việc cập nhật lại dữ liệu một căn luôn ổn định, an toàn cho cơ sở dữ liệu và dễ dàng khắc phục khi Cookie hết hạn.

## Acceptance
- [x] **Kiểm tra định dạng phản hồi ở Frontend (Frontend Response Validation):**
  - Cập nhật hàm `recrawlActiveListing()` trong `curator.html`.
  - Kiểm tra `res.ok` trước khi gọi `res.json()`. Nếu không thành công (trả về mã lỗi 4xx/5xx hoặc HTML), ném lỗi thân thiện (ví dụ: `Máy chủ phản hồi mã lỗi ${res.status}`) thay vì gọi `res.json()` gây lỗi crash cú pháp `SyntaxError: Unexpected token '<'`.
- [x] **Phát hiện chuyển hướng Đăng nhập ở Backend (Detect Login Redirect in Backend):**
  - Cập nhật `recrawl_single_listing()` trong `curator_server.py`.
  - Nếu Thiên Khôi chuyển hướng yêu cầu về trang Đăng nhập (ví dụ: `Account/Login` hoặc `login` trong URL chuyển hướng `r.url`), trả về JSON lỗi `{"status": "error", "message": "Cookie Thiên Khôi đã hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại Thiên Khôi và cập nhật Cookie mới."}` với mã HTTP `401 Unauthorized` thay vì tiếp tục bóc tách bừa bãi trang HTML Đăng nhập làm ghi đè trống rỗng dữ liệu trong cơ sở dữ liệu SQLite.
- [x] **Ngăn chặn phá hủy dữ liệu (Prevent Data Destruction Guard):**
  - Nếu trang chi tiết trả về trống rỗng (không tìm thấy `#Detail_sNoiDung` và `#Detail_sDiaChi`), hủy quá trình lưu trữ để bảo vệ các cột thông tin gốc hiện tại trong cơ sở dữ liệu SQLite.
- [x] **Tránh bóc tách sai link trong Mô tả (Avoid False Link Extraction in Description):**
  - Khắc phục lỗi trong hàm `get_val_by_label` của `crawl_pipeline.py`.
  - Nếu label thuộc nhóm mô tả/nội dung (`["mô tả", "mô tả chi tiết", "nội dung", "nội dung chính"]`), cấm hành vi tự động trả về liên kết `href` khi tìm thấy thẻ `<a>` bên trong, thay vào đó bắt buộc trả về toàn bộ text văn bản gốc để không làm mất đoạn mô tả chi tiết của căn nhà.

## Solution
1. **Frontend Enhancement:** Thay đổi hàm `recrawlActiveListing()` trong `curator.html` kiểm tra `res.ok`. Nếu false, đọc nội dung dưới dạng text và trích xuất thông báo lỗi của JSON (hoặc nội dung text ngắn) để hiển thị thông báo trực tiếp qua `alert()`, giải quyết triệt để lỗi phân tích cú pháp HTML `Unexpected token '<'`.
2. **Backend Robustness:**
   - Bao bọc toàn bộ logic truy vấn và cào tin của API `/api/listings/<tk_id>/recrawl` trong `try...except` để đảm bảo lỗi phát sinh ở bất kỳ bước nào đều trả về JSON 500 thay vì traceback HTML.
   - Giải quyết lỗi `KeyError` bằng cách truy vấn dictionary an toàn `d_row.get("Link_Goc") or d_row.get("Link_Gốc")` thay vì cố định `row["Link_Gốc"]` (do cột trong SQLite thực tế là `Link_Goc`).
   - Thêm cơ chế phòng thủ phát hiện chuyển hướng trang đăng nhập `Account/Login` hoặc bị block `security.html`, trả về mã lỗi HTTP `401` kèm giải thích thân thiện.
   - Thêm lớp phòng vệ dữ liệu (Data Safety Guard) kiểm tra nếu soup bóc tách được trống thông tin cốt lõi thì hủy ghi đè database.
3. **Description Link-Extraction Fix:**
   - Sửa logic trong hàm `get_val_by_label` của `crawl_pipeline.py` để loại trừ các label mô tả/nội dung khỏi cơ chế trích xuất liên kết nhanh `find('a')`. Nhờ vậy, đoạn văn mô tả chi tiết (chứa link Facebook/Zalo của Đầu chủ) được bảo toàn nguyên vẹn 100% nội dung chữ dài thay vì bị lọc chỉ còn đúng một dòng link URL.

## 📋 Implementation Plan
- **Step 1:** Cập nhật API Server trong `curator_server.py` xử lý khóa an toàn và bắt ngoại lệ, thêm kiểm tra redirect đăng nhập.
- **Step 2:** Sửa đổi `crawl_pipeline.py` khắc phục lỗi trích xuất thẻ `<a>` đối với các trường văn bản mô tả dài.
- **Step 3:** Cập nhật UI Fetch trong `curator.html` kiểm tra `res.ok`, bắt lỗi văn bản thân thiện.
- **Step 4:** Biên dịch ứng dụng KhangNgoCuratorApp.exe duy nhất.

## 📝 Task Checklist (TODO)
- [x] Sửa KeyError `Link_Gốc` -> `Link_Goc` an toàn trong `curator_server.py`.
- [x] Bao bọc route cào lại trong `try...except` bắt lỗi đầy đủ.
- [x] Thêm kiểm tra chuyển hướng URL đăng nhập/bảo mật.
- [x] Thêm kiểm tra trống nội dung cào chi tiết để từ chối lưu đè SQLite.
- [x] Khắc phục lỗi trích xuất link `<a>` trong `get_val_by_label()` tại `crawl_pipeline.py`.
- [x] Sửa frontend `curator.html` kiểm tra `res.ok` trước khi gọi `res.json()`.
- [x] Biên dịch ứng dụng EXE bằng PyInstaller thành công.

## Verification Plan
1. **Test hết hạn Cookie / Redirect Đăng nhập:**
   - Ghi cookie lỗi vào file `thienkhoi_cookie.txt`.
   - Ấn cào lại trên UI. Xác nhận hiển thị thông báo alert: `"Không tìm thấy nội dung chi tiết căn nhà trên trang Thiên Khôi. Vui lòng cập nhật lại Cookie."` rõ ràng.
   - Kiểm tra database SQLite, đảm bảo dòng thông tin của căn nhà vẫn giữ nguyên, không bị ghi đè các cột trống.
2. **Test bóc tách Mô tả chứa Link Facebook (nhà Phan Tây Hồ 8.66 tỷ):**
   - Đưa HTML trang lưu trữ của anh Khang vào luồng kiểm thử cào.
   - Xác nhận Mô tả chi tiết lấy được toàn bộ nội dung dài của bài viết, bao gồm thông số vị trí, kết cấu, nội thất, giá bán và link Facebook liên kết ở cuối, thay vì chỉ lấy duy nhất link facebook.
3. **Test cào thành công:**
   - Ghi cookie hợp lệ, chạy cào lại. Xác nhận hiển thị banner thành công và cập nhật lại giao diện biên tập tức thì.

## Files touched
- [curator_server.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator_server.py)
- [curator.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator.html)
- [crawl_pipeline.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/crawl_pipeline.py)
