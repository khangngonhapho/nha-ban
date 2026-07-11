---
us_id: US-035
status: completed
started: 2026-05-25
---

# Implementation Plan: US-035 Hệ thống cào BĐS & Mini-App biên tập rổ hàng 2000 căn

## Scope
- **US**: [[US-035_crawl_bulk_to_google_drive]]
- **Files sẽ tạo/sửa**:
  - `[NEW]` `crawl_pipeline.py` — Script CLI cào dữ liệu text thô & link ảnh TK lưu SQLite.
  - `[NEW]` `curator_server.py` — Flask Backend server điều phối dữ liệu SQLite, upload ảnh Drive & API Sheets.
  - `[NEW]` `curator.html` — Giao diện Web UI local hiển thị và phân loại ảnh thủ công.
  - `[MODIFY]` `docs/stories/INDEX.md` — Đăng ký US-035 mới.

---

## Checklist

### Phase 1: Xây dựng Script cào thô vào SQLite (`crawl_pipeline.py`)
- [x] Thiết lập kết nối SQLite `raw_archive.db` và khởi tạo bảng `listings` tự động có cấu trúc đồng nhất 72 cột tương tự Pool Sheet.
- [x] Viết cơ chế tải danh sách `tk_id` đã có từ SQLite vào biến `set` trong RAM để kiểm tra trùng lặp nhanh O(1).
- [x] Viết hàm parse HTML chi tiết căn nhà từ TK (lấy giá, diện tích, địa chỉ, mô tả và danh sách link ảnh TK thô).
- [x] Tích hợp bộ cấu hình **Chế độ Siêu Tàng Hình (Ultra-Stealth Mode)**:
  - [x] Nghỉ ngẫu nhiên `8.0 - 15.0` giây trước khi click cào chi tiết từng căn.
  - [x] Nghỉ ngẫu nhiên `120.0 - 240.0` giây (2-4 phút) trước khi chuyển trang danh sách.
  - [x] Hỗ trợ tham số `--district` để cào cuốn chiếu từng Quận.
- [x] Lưu dòng dữ liệu thô vào SQLite với `status = 'raw_text'`.

### Phase 2: Luồng tải ảnh & Upload Google Drive chạy ngầm
- [ ] Cấu hình xác thực Google Drive API bằng tệp `credentials.json` (Service Account).
- [ ] Viết hàm tải ảnh TK gốc về RAM, upload lên Google Drive 5TB theo thư mục con mang mã căn nhà (`tk_id`).
- [ ] Thiết lập quyền public chia sẻ cho ảnh trên Drive để lấy link nhúng trực tiếp dạng `https://lh3.googleusercontent.com/d/[file_id]`.
- [ ] Viết vòng lặp quét SQLite tìm các căn `status = 'raw_text'`, tải ảnh và upload Drive, ghi đè mảng link Drive vào SQLite và cập nhật `status = 'raw_complete'`.
- [ ] Tích hợp độ trễ an toàn **3 - 5 giây** sau mỗi căn để tránh spam băng thông và bảo vệ IP.

### Phase 3: Xây dựng Curator Mini-App (Flask + HTML/JS/CSS)
- [ ] Thiết lập Flask Server `curator_server.py` đọc dữ liệu SQLite và phục vụ API hiển thị.
- [ ] Xây dựng giao diện Web biên tập viên `curator.html` hiển thị thông tin thô và lưới ảnh Drive của từng căn nhà để lựa chọn bằng mắt.
- [ ] Viết logic click chuột chọn nhanh nhãn ảnh: Ảnh Nền (Cover), Ảnh Mặt Tiền (MT - Tuyệt mật), Ảnh Public, Ảnh Hẻm Public.
- [ ] Viết hàm API xử lý lưu: Ghép các link ảnh đã chọn vào đúng các cột nghiệp vụ chuyên biệt của hàng 72 cột, gọi API `gspread` chèn thẳng xuống đáy Google Sheet chính thức.
- [ ] Cập nhật `status = 'published'` trong SQLite và tự động tải sang căn tiếp theo.

---

## Multi-Machine Operations (Quy trình Vận hành Đa Thiết bị)

Để tối ưu hóa vận hành, bảo mật tài khoản TK và phân tách hiệu quả công việc giữa các máy tính:

### 💻 Máy Cào (Máy B - Chứa session TK đăng nhập hợp lệ)
1. **Thiết lập:** Cài đặt Python 3.7+ và chạy lệnh cài đặt thư viện: `pip install requests beautifulsoup4 httpx`.
2. **Lấy Cookie:** Đăng nhập TK trên Chrome máy B, nhấn F12 -> Network, copy chuỗi `Cookie` từ Request Headers của một request chi tiết hoặc danh sách.
3. **Cào thô (Phase 1):** Chạy script cào text thô theo từng Quận mục tiêu ở chế độ Siêu tàng hình:
   `python crawl_pipeline.py --action crawl --district Q10 --cookie "[Cookie_Máy_B]"`
4. **Bàn giao:** File SQLite `raw_archive.db` tự động sinh ra sau khi cào xong (chỉ nặng vài MB) sẽ được copy gửi về Máy A.

### 💻 Máy Lập Trình & Biên Tập (Máy A - Máy hiện tại)
1. **Tiếp nhận:** Copy file `raw_archive.db` từ máy B bỏ vào thư mục dự án của máy A.
2. **Luồng Di cư ảnh (Phase 2):** Chạy script tải ảnh và upload Google Drive 5TB chạy ngầm (không cần session/cookie TK nữa, hoàn toàn an toàn):
   `python crawl_pipeline.py --action upload`
3. **Biên tập & Xuất bản (Phase 3):** Khởi chạy local Flask Server (`python curator_server.py`) và mở giao diện `localhost:5000` tuyển chọn hình ảnh bằng mắt, bấm "Lưu lên Google Sheet" để chèn thẳng dòng 72 cột hoàn chỉnh xuống đáy Pool Sheet hoạt động.

---

## Decisions log
- [2026-05-25]: Chọn phương án cào 2 bước cục bộ (Cào text thô vào SQLite trước -> tải ảnh up Drive chạy ngầm sau) — Để bảo vệ tài khoản tối đa và tránh bị block IP do duy trì request cào kéo dài.
- [2026-05-25]: Thiết lập cấu hình trễ siêu tàng hình (8-15 giây/căn, 2-4 phút/trang) chạy cuốn chiếu từng Quận — Giả lập 100% hành vi lướt web của người thật, an toàn tuyệt đối cho tài khoản.
- [2026-05-25]: SQLite schema đồng nhất 100% cấu trúc 72 cột với Pool Sheet — Đảm bảo khi Admin chọn ảnh xong bấm Lưu sẽ chèn thẳng một dòng chuẩn chỉnh xuống đáy Sheet, kết thúc luồng nghiệp vụ an toàn.

---

## Resume checkpoint
> Đang ở: [Phase 2 / Step 1 - Khởi tạo luồng tải ảnh up Drive]
> Files đã touch: 
> * `docs/stories/INDEX.md`
> * `docs/stories/_inbox/US-035_crawl_bulk_to_google_drive.md`
> * `crawl_pipeline.py`
> * `raw_archive.db` (SQLite local)
> Cần làm tiếp: Cấu hình và lập trình kết nối Google Drive API thực tế qua credentials.json để chạy di cư ảnh ngầm.
