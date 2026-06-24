---
id: US-106
status: accepted
date: 2026-06-22
size: M
---

# US-106: Giao Diện Canvas Trực Quan Xem Chi Tiết Căn Nhà (Pool & Source)

## User Story
**As an** Admin (Môi giới quản trị dự án BDS)
**I want** có một trang web (giao diện dạng Canvas/Dashboard) để xem chi tiết căn nhà từ cả hai danh sách Pool (Thô) và Source (Sạch) dưới dạng các thẻ thông tin trực quan được gom nhóm khoa học
**So that** tôi không phải mất thời gian lướt ngang/dọc qua hàng chục cột (78 cột Pool, 46 cột Source) trên giao diện Google Sheets hoặc các bảng dữ liệu thô, giúp nắm bắt nhanh địa chỉ thực, thông tin kỹ thuật, giá chào/chốt, thông tin đầu chủ/chủ nhà và bài đăng public cùng lúc.

## Acceptance Criteria
- [ ] Có trang web tĩnh độc lập tại tệp [canvas.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/canvas.html) hỗ trợ hiển thị thông tin trực quan.
- [ ] Giao diện được thiết kế theo chuẩn Dark Mode Premium của dự án (phông chữ Inter & Outfit, Glassmorphism, hiệu ứng màu vàng gold, viền mỏng tinh tế, tối ưu hóa không gian).
- [ ] Hỗ trợ chế độ xem song song / đối chiếu các trường dữ liệu tương ứng giữa **Pool (Thô)** và **Source (Sạch)** (Ví dụ: Số nhà thực tế vs. Tiêu đề public ẩn số nhà, Giá chào vs. Giá bán, DT thực tế vs. Diện tích sổ).
- [ ] Hỗ trợ 2 chế độ nạp dữ liệu (Dual-mode Loading):
  * **Chế độ Google Sheets (Mặc định khi chạy Live):** Đăng nhập thông qua Google OAuth2, nạp trực tiếp dữ liệu realtime từ 2 tệp Sheets API, hiển thị đầy đủ thông tin bảo mật (PII).
  * **Chế độ SQLite (Mặc định khi chạy Local):** Khi chạy ở `localhost`, tự động phát hiện và cho phép tải dữ liệu trực tiếp từ SQLite backend Flask thông qua API `/api/listings` và `/api/listings/<tk_id>`.
- [ ] Tích hợp Tab **Raw Columns Inspector** tự động (Dynamic Mapping) hiển thị danh sách dọc tất cả các cột thô của sheet Pool (78 cột) và Source (46 cột):
  * Tự động đọc hàng tiêu đề đầu tiên (`poolRows[0]`) để làm nhãn (label).
  * Nếu sheet Pool/Source được cập nhật thêm/bớt cột trên Google Drive trong tương lai, tab này vẫn hiển thị đúng mà không cần sửa mã nguồn (Future-proof).
  * Hỗ trợ thanh tìm kiếm (Filter) nhanh tên cột trong tab thô để lọc nhanh các cột mong muốn.
- [ ] Hiển thị trực quan **Thư viện Hình ảnh & Pháp lý**:
  * Phân loại ảnh thành các nhóm: Sơ đồ thửa đất (Sổ đỏ), Ảnh mặt tiền, Ảnh hẻm, Ảnh nội thất.
  * Hỗ trợ bộ phóng to ảnh (Lightbox) có tính năng xoay ảnh và tải ảnh xuống thiết bị.
- [ ] Bảo mật thông tin cá nhân (PII): Thông tin liên hệ của chủ nhà và đầu chủ (Tên chủ nhà, SĐT 1, SĐT 2, SĐT đầu chủ, Facebook) chỉ được hiển thị ở chế độ xem Admin bảo mật, không lộ ra ngoài.
- [ ] Tích hợp liên kết mở nhanh Canvas View trên thanh Header của `curator.html` và trong menu Admin của `index.html`.

## Solution Design

### 1. Bố cục Giao diện (Layout)
* **Sidebar (380px):**
  * Hộp tìm kiếm thông minh (Search by ID, Address, Price, Street).
  * Bộ chọn chế độ: 🌐 Google Sheets (realtime) vs. 💾 SQLite (local).
  * Nút đăng nhập Google OAuth2 (nếu dùng chế độ Sheets và chưa đăng nhập).
  * Bộ lọc Quận/Phường, bộ lọc Trạng thái.
  * Danh sách cuộn các card căn nhà.
* **Canvas Panel (Main detail view):**
  * **Tab 1: 📊 Nhìn Toàn Cảnh (Canvas):** Gồm các card phân khu:
    * *📍 Vị trí & Địa lý:* Số nhà thô vs. Địa chỉ sạch, đường, phường, quận, toạ độ.
    * *📐 Thông số kỹ thuật:* Diện tích thực tế vs. DT sổ, ngang, dài, số tầng, phòng ngủ, vệ sinh.
    * *💰 Giá cả:* Giá chào, giá chốt, giá public, đơn giá/m2.
    * *🤝 Đầu chủ & Pháp lý (Bảo mật PII):* Tên/SĐT chủ nhà, Tên/SĐT đầu chủ, facebook, hợp đồng.
    * *🤖 Curation & AI:* Tiêu đề public, mô tả public, note nội bộ, phân loại hẻm, độ rộng hẻm, tình trạng nhà, đánh giá.
    * *⚙️ Thông tin Hệ thống:* Mã hàng, System ID, ngày cào, ngày đồng bộ, link gốc.
  * **Tab 2: 🖼️ Thư viện hình ảnh:** Hiển thị ảnh phân loại theo tabs nhỏ (Tất cả, Sổ đỏ, Mặt tiền, Hẻm, Nội thất).
  * **Tab 3: 📝 Chi tiết Pool (78 cột thô):** Danh sách dọc tất cả các cột của Pool với ô tìm kiếm tiêu đề cột.
  * **Tab 4: 🚀 Chi tiết Source (46 cột thô):** Danh sách dọc tất cả các cột của Source với ô tìm kiếm tiêu đề cột.

### 2. Tệp tin tác động (Impacted Files)
* [canvas.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/canvas.html) `[NEW]` — Giao diện chính của Canvas Detail View.
* [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py) `[MODIFY]` — Route backend `/canvas` và `/canvas.html`.
* [api/index.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/api/index.js) `[MODIFY]` — Route Vercel serverless proxy cho `/canvas.html`.
* [curator.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator.html) `[MODIFY]` — Thêm liên kết mở Canvas trên Header.
* [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html) `[MODIFY]` — Thêm liên kết mở Canvas cho Admin.
* [docs/stories/INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md) `[MODIFY]` — Cập nhật mục lục User Story.

---

## Verification Plan

### Automated Tests
- Chạy toàn bộ các kịch bản kiểm thử E2E hiện tại để kiểm tra hồi quy:
  ```powershell
  python scratch/test_e2e_curation.py
  ```

### Manual Verification
1. Chạy ứng dụng local: `python manager.py` hoặc nhấp đúp `CHAY_APP.bat`.
2. Truy cập `http://localhost:5000/canvas.html`.
3. Kiểm tra danh sách hiển thị đầy đủ, chọn một căn và xem thông tin đối chiếu Pool vs. Source.
4. Chuyển sang Tab "Chi tiết Pool", nhập thử "Điện thoại" vào ô tìm kiếm cột để kiểm tra lọc nhanh SĐT chủ nhà.
5. Chuyển sang Tab "Thư viện hình ảnh", click vào một hình ảnh bất kỳ để phóng to xem chi tiết.
6. Đăng nhập Google OAuth, chuyển sang chế độ Google Sheets và xác nhận dữ liệu được đồng bộ realtime.

---

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Issues & Root Causes
* **Lệch dòng Tiêu đề Pool**: Lỗi cache/offset khi dùng Sheets API khiến hàng tiêu đề Pool bị nhận dạng nhầm thành một dòng dữ liệu thực tế. Điều này dẫn tới tab hiển thị cột thô hiển thị sai tên cột Việt hóa (lấy giá trị dữ liệu làm tên tiêu đề).
* **Giải pháp khắc phục**: Khai báo danh sách hardcode `HARDCODED_POOL_HEADERS` làm fallback tĩnh ở phía client khi chạy chế độ Google Sheets realtime.

### 2. Lessons Learned & Good Practices
* **Đồng bộ hóa cấu trúc Inspector**: Mọi tab hiển thị cột thô (Pool & Source) nên có cấu trúc trực quan giống nhau (Mã cột Excel, Số thứ tự, Tên tiêu đề Việt hóa, Giá trị) để giảm tải nhận thức của người dùng.
* **Bảo vệ PII**: Đảm bảo lọc kỹ thông tin liên hệ nhạy cảm và chỉ render trong giao diện khi có session Admin.

