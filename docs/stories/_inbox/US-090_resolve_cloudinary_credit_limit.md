---
id: US-090
status: accepted
date: 2026-06-13
size: L
replaces: none
---

# US-090: Di cư toàn bộ kho hình ảnh sang Cloudflare R2 & Khắc phục giới hạn hạn mức Cloudinary

## User story
**As an** Admin  
**I want** di cư toàn bộ kho hình ảnh và sơ đồ thửa đất của danh sách bất động sản từ tài khoản Cloudinary đã hết hạn mức sang **Cloudflare R2**  
**So that** toàn bộ hệ thống web client và file Google Sheets công khai hoạt động bình thường, không còn bị lỗi tải hình ảnh, và hoàn toàn loại bỏ sự phụ thuộc vào chi phí/hạn mức băng thông của Cloudinary.

## Acceptance Criteria
- [x] **Di cư dữ liệu SQLite sang Cloudflare R2**:
  - Viết và thực thi script di cư tải ảnh từ Cloudinary cũ và đẩy trực tiếp lên Cloudflare R2.
  - Cập nhật lại liên kết R2 vào các cột hình ảnh phẳng trong bảng `listings` (`Anh_1` đến `Anh_25`, `So_do_thua_dat_1` đến `5`, `Hinh_Mat_Tien`, `Hinh_Hem_1` đến `10`).
- [x] **Đồng bộ liên kết R2 lên Google Sheet Pool (v1)**:
  - Cập nhật toàn bộ các ô ảnh và sơ đồ thửa đất trên Google Sheet thành địa chỉ link R2 công khai.
- [x] **Giải quyết triệt để lỗi chuỗi JSON mảng trên Sheets**:
  - Nhận diện và loại bỏ hoàn toàn các chuỗi định dạng mảng JSON `["https://..."]` tại các ô ảnh và sơ đồ trên Google Sheets, thay thế bằng định dạng URL đơn chuẩn.
- [x] **Báo cáo danh sách căn bị lỗi ảnh (Cloudinary 404)**:
  - Lập báo cáo chi tiết các căn bị lỗi ảnh cũ đã bị xóa trên Cloudinary gốc (không thể di cư).
  - Báo cáo phải được phân tách thành 2 phần (Danh sách trên Google Sheet & Danh sách trong SQLite) và đi kèm đầy đủ thông tin địa chỉ (`Ngõ/Số nhà`, `Đường`, `Phường`, `Quận`) và `Nội dung chính` để admin tiện cập nhật thủ công.

---

## Solution Architecture

1. **Cấu hình lưu trữ Cloudflare R2**:
   - Thiết lập thông tin xác thực R2 (Access Key, Secret Key, Bucket Name, Account ID, Public URL) trong tệp [settings.json](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/settings.json).
2. **Script di cư CSDL (`migrate_to_r2.py`)**:
   - Sử dụng cơ chế tải/đẩy ảnh đa luồng (`ThreadPoolExecutor`) để di cư ảnh hàng loạt sang R2.
   - Nhận diện các ảnh 404 (không tồn tại trên Cloudinary) để bỏ qua, giữ nguyên link Cloudinary cũ dạng URL đơn thay vì làm hỏng ô dữ liệu.
3. **Script đồng bộ Sheet (`sync_pool_v1_sheet.py`)**:
   - Sử dụng thuật toán so khớp chéo tên file (Cross-column Matching) để đối chiếu link Cloudinary trên Sheet với bất kỳ cột ảnh R2 nào tương ứng trong SQLite.
   - Chuẩn hóa chuỗi JSON mảng sang URL đơn ngay trong lúc đọc dữ liệu bằng JSON parser.
   - Ghi đè hàng loạt (Batch Update) lên Sheets API để tránh nghẽn/timeout.
4. **Script báo cáo lỗi (`list_broken_listings.py` & `check_db_cloudinary.py`)**:
   - Quét qua Sheets và SQLite để lọc ra các dòng còn chứa chuỗi `cloudinary.com` (là các link 404 chết), trích xuất địa chỉ thực tế và nội dung chính, xuất bảng Markdown ra [broken_listings_report.md](file:///C:/Users/Khang%20Ngo/.gemini/antigravity/brain/72b4b200-2519-4411-8d37-dabef40b9ed0/broken_listings_report.md).

---

## 🛠️ Effective Implementation Steps (Các bước thực hiện hiệu quả)

1. **Tải/Đẩy ảnh Đa luồng (Multi-threading)**:
   - Sử dụng `concurrent.futures.ThreadPoolExecutor` với quy mô 10-20 threads để thực hiện tải ảnh từ Cloudinary và đẩy lên R2 song song. Giúp tăng tốc độ di cư toàn bộ 5.180 ảnh chỉ trong vòng chưa đầy 15 phút.
2. **So khớp chéo tên file (Cross-column Matching)**:
   - Thay vì so khớp tĩnh theo vị trí cột (Ví dụ: cột `Anh_1` trên Sheets khớp với `Anh_1` trong CSDL) gây ra tỷ lệ lệch rất cao, thuật toán so khớp đã bóc tách tên tệp gốc (filename base) trong link Cloudinary của Sheets, tìm kiếm xem nó đã tồn tại trong **bất kỳ cột R2 nào** của căn đó trong database hay chưa. Nếu đã có, lấy luôn link R2 đó.
   - **Hiệu quả:** Giảm số lượng request tải/đẩy ảnh từ **17.200 requests** xuống chỉ còn **191 requests** (tiết kiệm 99% tài nguyên mạng và thời gian).
3. **Ghi đè hàng loạt (Batch Update) trên Google Sheets API**:
   - Gom các ô cần cập nhật thành các khối 1.000 ô và đẩy lên thông qua hàm `batch_update()` của thư viện `gspread`.
   - **Hiệu quả:** Cập nhật 61.872 ô dữ liệu lên Google Sheets chỉ trong ~3 phút mà không gặp lỗi nghẽn đường truyền hoặc vượt hạn mức API quota của Google.
4. **Tối ưu hóa SQLite (WAL mode & synchronous=OFF)**:
   - Cấu hình database sang chế độ ghi trước nhật ký (WAL) và tắt đồng bộ vật lý ổ đĩa tạm thời trong phiên cập nhật dữ liệu hàng loạt. Giúp giảm tải đĩa cứng và tăng tốc độ commit dữ liệu đa luồng từ 10 dòng/giây lên hơn 200 dòng/giây.
5. **Nhận diện & Chuẩn hóa JSON mảng tự động**:
   - Viết bộ lọc regex và JSON parser để bóc tách URL đơn đầu tiên trong chuỗi mảng JSON dán nhầm của người dùng trên Sheets, giúp làm sạch 100% định dạng cột ảnh.

---

## ⚠️ Lessons Learned & Ineffective Steps (Bài học kinh nghiệm từ các bước không hiệu quả)

1. **Thực hiện di cư tuần tự (Single-thread Migration) - KHÔNG HIỆU QUẢ**:
   - Khi mới bắt đầu, script di cư ảnh chạy tuần tự từng căn một. Do độ trễ mạng khi tải ảnh từ Cloudinary về máy và đẩy lên Cloudflare R2 quá lớn, script chỉ xử lý được vài chục căn sau nhiều phút.
   - *Bài học rút ra:* Luôn luôn sử dụng lập trình đa luồng (Multi-threading) khi xử lý các tác vụ I/O mạng hàng loạt.
2. **So khớp tĩnh theo vị trí cột (Column-to-Column Sync) - KHÔNG HIỆU QUẢ**:
   - Script đồng bộ cũ so khớp cột theo chỉ số tĩnh. Tuy nhiên, do thực tế thứ tự ảnh lưu trữ trong CSDL của crawler và thứ tự ảnh hiển thị trên Google Sheet của người dùng bị lệch nhau, cơ chế này đánh giá sai toàn bộ các ảnh đã di cư là "chưa khớp". Hệ thống cố gắng tải lại hơn 17.000 bức ảnh từ Cloudinary, gây nghẽn mạng nghiêm trọng.
   - *Bài học rút ra:* Khi đồng bộ hình ảnh giữa 2 nguồn dữ liệu không đồng nhất cấu trúc, bắt buộc phải dùng thuộc tính định danh duy nhất của tệp tin (tên file gốc/hash MD5) để so khớp thay vì vị trí cột vật lý.
3. **Ghi đè trực tiếp mảng JSON R2 lên Sheets - KHÔNG HIỆU QUẢ**:
   - Khi cập nhật link R2 tương ứng cho các ô chứa mảng JSON gốc, script ghi đè lại định dạng mảng JSON `["https://pub-e92..."]` lên ô. Việc này làm lỗi chức năng hiển thị ảnh trên web client và làm lỗi công thức xử lý chuỗi của Sheets.
   - *Bài học rút ra:* Dữ liệu lưu trữ trên Google Sheet phục vụ hiển thị cần được chuẩn hóa về định dạng URL đơn sạch sẽ, các cấu trúc mảng phức tạp chỉ nên lưu trong CSDL SQLite dưới dạng JSON Text.
4. **Cố gắng tải lại các liên kết Cloudinary đã bị xóa (HTTP 404) - KHÔNG HIỆU QUẢ**:
   - Script di cư cố gắng thực hiện tải đi tải lại các link ảnh Cloudinary đã chết từ lâu, gây lãng phí tài nguyên và làm treo luồng xử lý do hết thời gian chờ (timeout).
   - *Bài học rút ra:* Ghi nhận trạng thái lỗi 404 ngay lập tức, bỏ qua việc tải lại và đưa vào danh sách báo cáo lỗi thủ công để giữ nguyên trạng thái cũ thay vì làm trống ô dữ liệu trên Sheets.
