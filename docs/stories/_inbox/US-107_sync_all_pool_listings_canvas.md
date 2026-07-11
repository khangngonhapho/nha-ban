---
id: US-107
status: accepted
date: 2026-06-25
size: M
---

# US-107: Đồng bộ Realtime và Hiển thị Toàn bộ Căn nhà từ Pool trên Canvas

## User story
**As an** Admin (Môi giới quản trị dự án BDS)
**I want** bảng nhìn toàn cảnh trực quan Canvas (canvas.html) có khả năng đồng bộ realtime và hiển thị tất cả các căn nhà có trong rổ hàng Pool (bao gồm cả những căn chưa được đưa lên sheet Source - tức là chưa lên sóng)
**So that** tôi có thể dễ dàng quản lý, kiểm tra thông tin thô, hình ảnh, sơ đồ pháp lý và trực tiếp curation cho những căn nhà mới cào về chưa lên sóng một cách trực quan, nhanh chóng ngay trên giao diện Canvas mà không cần thao tác thủ công trên Google Sheets, từ đó đẩy nhanh KPI 1 (Tốc độ biên tập tin bài) của Value Management Plan.

## Acceptance
- [x] Giao diện Canvas hiển thị toàn bộ rổ hàng từ **Pool (Thô)**, không loại bỏ các căn chưa được đưa lên sheet **Source (Sạch)**.
- [x] Danh sách Card ở Sidebar phân biệt rõ ràng hai trạng thái của căn nhà:
  * **Đã lên sóng (Published):** Căn nhà đã tồn tại trên cả hai sheet Pool và Source (đồng bộ).
  * **Chờ biên tập (Raw/Pending Curation):** Căn nhà mới chỉ có dữ liệu ở Pool, chưa có thông tin trên Source.
- [x] Bộ lọc **Trạng thái (Status Filter)** trên Sidebar hoạt động chính xác cho cả 3 chế độ:
  * *Tất cả (All)*: Hiển thị cả căn đã lên sóng và chưa lên sóng.
  * *Đã lên sóng (Published)*: Chỉ hiển thị các căn đã được duyệt lên Source.
  * *Chờ biên tập (Raw/Pending)*: Chỉ hiển thị các căn chưa lên sóng (chỉ có dữ liệu trong Pool).
- [x] Khi chọn một căn "Chờ biên tập" (chỉ có trong Pool):
  * Phần thông tin **Pool (Thô)** hiển thị đầy đủ chi tiết (Địa chỉ thật, thông số kỹ thuật thô, giá chào, thông tin đầu chủ, hình ảnh/sổ đỏ từ cột Pool).
  * Phần thông tin **Source (Sạch)** và **Curation & AI** sẽ tự động hiển thị trạng thái trống hoặc các nhãn mặc định (Ví dụ: "Chưa biên tập", "Chưa có thông tin").
  * Tab **Raw Columns Inspector** vẫn hiển thị đầy đủ 78 cột thô của Pool, riêng tab **Source (46 cột thô)** sẽ hiển thị thông báo: "Căn nhà này chưa lên sóng, không có dữ liệu Source".
- [x] Hỗ trợ đồng bộ realtime qua cả hai chế độ:
  * **Google Sheets mode**: Nạp toàn bộ dòng dữ liệu từ sheet `Pool!A1:ZZ`, sau đó đối chiếu với sheet `Source!A2:ZZ`. Những dòng Pool không khớp với Source nào vẫn được đưa vào danh sách dữ liệu hiển thị dưới dạng căn "Chờ biên tập".
  * **SQLite mode**: Đồng bộ tương đương với danh sách listings từ local Flask API `/api/listings`.
- [x] Toàn bộ mã nguồn Javascript (`lego_core.js` và `canvas.html`) được cấu trúc sạch sẽ, hoạt động ổn định và không phát sinh lỗi hồi quy đối với các tính năng hiện tại.

## Solution

### 1. Bố cục và hiển thị dữ liệu
* Bổ dung hiển thị badge trạng thái động: "Đã lên sóng" (badge-published) cho các căn đã đồng bộ lên Source, và "Chờ biên tập" (badge-raw) cho các căn chỉ có dữ liệu Pool.
* Cấu hình tab Source thô hiển thị cảnh báo thay thế cho danh sách 46 hàng rỗng khi căn nhà chưa lên sóng.

### 2. Thiết kế logic gộp dữ liệu Sheets
* Nạp song song hai sheet Pool và Source như bình thường.
* Lặp qua sheet `Source` và dò tìm `poolRow` tương ứng để tạo đối tượng listing đã lên sóng. Lưu lại chỉ số (index) dòng Pool đã được khớp.
* Lặp qua các dòng trong sheet `Pool` chưa được khớp để tạo đối tượng listing thô chưa lên sóng.
* Gộp hai danh sách và trả về cho giao diện Canvas.

## 📋 Implementation Plan

### 1. Phân hệ dữ liệu Google Sheets (`static/js/lego_core.js`)
* Tạo biến `matchedPoolRowIndexes = new Set()` để lưu các dòng `poolRow` đã ghép nối thành công.
* Sau khi hoàn tất vòng lặp `sourceRows.map()`, lặp qua `poolDataRows` bằng `forEach` và kiểm tra nếu index không nằm trong `matchedPoolRowIndexes` thì tiến hành bóc tách thuộc tính thô từ dòng Pool đó để xây dựng listing `p` chưa lên sóng.
* Đưa danh sách chưa lên sóng vào cuối `fullList`.

### 2. Phân hệ giao diện Canvas (`canvas.html`)
* Sửa logic tính trạng thái `status` của card để dựa trên `item.source_row_index` thay vì `item.id`.
* Cập nhật hàm `renderRawInspector` để chèn HTML cảnh báo nếu `item.original_row_data` rỗng (Sheets mode) or `item.status !== 'published'` (SQLite mode).

### 3. Phân hệ kiểm thử (`scratch/test_e2e_canvas.py`)
* Sửa `artifacts_dir` trỏ về conversation ID `c3b8820b-34f3-44a0-a88a-e1cd4c29c407`.
* Bổ sung mock listing thô chưa lên sóng, click chọn và kiểm thử badge trạng thái cũng như tab Source raw inspector.

## 📝 Task Checklist (TODO)
- [x] Bổ sung cơ chế lưu vết matched indexes và gom các căn pool-only trong `static/js/lego_core.js`
- [x] Chỉnh sửa logic tính trạng thái card và hiển thị tab Source trống trong `canvas.html`
- [x] Bổ sung kịch bản mock và assertions kiểm thử căn chưa lên sóng trong `scratch/test_e2e_canvas.py`
- [x] Chạy kiểm thử E2E Playwright `test_e2e_canvas.py` đạt 100% PASS và chụp ảnh bằng chứng lưu vào `docs/workflows/assets/`
- [x] Kiểm tra chống lỗi hồi quy bằng cách chạy `test_e2e_filters.py` đạt 100% PASS

## 🛠️ Update Logic (Drafting while Doing)
*(Sẽ sử dụng để ghi nhận logic thô trong quá trình triển khai thực tế)*

## Verification Plan

### Automated Tests
- Chạy bộ script test E2E Canvas bằng Playwright để kiểm chứng tự động:
  ```powershell
  python scratch/test_e2e_canvas.py
  ```
- Chạy các test E2E khác để kiểm soát hồi quy:
  ```powershell
  python scratch/test_e2e_filters.py
  ```

### Manual Verification
1. Chạy server local bằng cách khởi động `manager.py`.
2. Truy cập `http://localhost:5000/canvas.html`.
3. Kiểm tra danh sách hiển thị, bộ lọc Quận/Phường/Trạng thái (Tất cả, Đã lên sóng, Chờ biên tập).
4. Click vào một căn "Chờ biên tập", kiểm tra hiển thị thông tin Pool thô, hình ảnh, tab Raw inspector (tab Pool đầy đủ dữ liệu, tab Source hiện cảnh báo).

## Files touched
* [static/js/lego_core.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_core.js)
* [canvas.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/canvas.html)
* [scratch/test_e2e_canvas.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_e2e_canvas.py)

## 🔄 Change Requests (Yêu cầu Thay đổi)
* **Sửa lỗi Lẫn lộn Ảnh mặt tiền (Image Mix-up Fix)**: Khắc phục lỗi rò rỉ trạng thái ảnh mặt tiền ở frontend (`lego_detail_admin.js`) bằng cách dùng `forceNew` để cô lập dữ liệu ảnh khi chuyển căn. Sửa lỗi xung đột ghi đè dữ liệu trực tuyến bằng cách bổ sung Thread Lock (`sheets_lock = threading.Lock()`) trong Python backend `pool_lego.py`. Chạy tool tự vá quét sạch 29 căn lỗi trên Google Sheets.
* **Sửa lỗi Căn thô 0 tỷ ở đầu trang (0-Billion Corrupt Listing Fix)**: Xóa dòng rác số 90 trống thông tin trên Pool Sheet và đồng bộ lại để loại bỏ căn lỗi hiển thị ở đầu trang của chế độ Admin.

## 🧠 Retro, Lessons Learned & Good Practices
* **Lessons Learned**:
  - *Concurrency Control*: Khi chạy đa luồng ghi dữ liệu trực tiếp lên Google Sheets API hoặc R2, bắt buộc phải có Thread Lock để tránh xung đột ghi đè chéo dòng (như lỗi lẫn lộn ảnh mặt tiền giữa các căn kế cận).
  - *State Isolation*: Trong các giao diện Single Page App (SPA) như Curator và Canvas, trạng thái UI của căn trước phải được reset hoàn toàn (hoặc ép nạp lại sạch) khi chuyển sang căn mới nhằm chống rò rỉ hình ảnh cũ.
  - *Google Sheets Cleanliness*: Quét và loại bỏ kịp thời các dòng trống/rác trong Google Sheets vì chúng có thể được hiển thị dưới dạng căn thô 0 tỷ gây lỗi giao diện.
