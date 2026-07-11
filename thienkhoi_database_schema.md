# THIÊN KHÔI REAL ESTATE - DATABASE & SHEET SCHEMA
*(Last Updated: 2026-06-05)*

> **LƯU Ý:** File schema này là cơ sở tham chiếu (Source of Truth) cho AI và Developer khi lập trình. KHÔNG chứa các khóa bảo mật và thông tin cá nhân của khách hàng.

---

## 1. FILE POOL (KHO CHỨA DỮ LIỆU THÔ)
- **ID File:** `1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw`
- **Tên Sheet (Tab):** `Pool`
- **Mục đích:** Nơi hứng dữ liệu trực tiếp từ Chrome Extension (Cào từ web hệ thống nội bộ Thiên Khôi). Chứa cả thông tin nhạy cảm (SĐT, Tên đầu chủ, Địa chỉ chính xác).
- **Tổng số cột:** 93 cột (Col A đến Col CO, index 0 đến 92).

### Cấu trúc Cột (Columns) Chi Tiết

| Ký tự | Index | Tên Cột | Mô tả & Kiểu dữ liệu |
| :---: | :---: | :--- | :--- |
| **A** | 0 | Mã Hàng | Text (Mã Thiên Khôi, VD: TK-534B8B) |
| **B** | 1 | Hình Nhận Diện | Image URL |
| **C** | 2 | Tỉnh | Text |
| **D** | 3 | Quận | Text |
| **E** | 4 | Phường | Text |
| **F** | 5 | Đường | Text |
| **G** | 6 | Ngõ/Số nhà | Text (Có chứa dấu `.` là Hẻm, không có là Mặt tiền) |
| **H** | 7 | Phân loại | Text tags |
| **I** | 8 | Năm xây dựng | Number |
| **J** | 9 | Nội dung chính | Text (Nội dung thô từ đầu chủ/nguồn tin) |
| **K** | 10 | Mô tả chi tiết | Text dài |
| **L** | 11 | Giá chào | Number |
| **M** | 12 | Giá chốt | Number |
| **N** | 13 | DT Thực tế | Number (m²) |
| **O** | 14 | DT Trên sổ | Number |
| **P** | 15 | Số Tầng | Number |
| **Q** | 16 | Mặt Tiền | Number (m) |
| **R** | 17 | Hướng | Enum |
| **S** | 18 | Tên Chủ Nhà | Text (Nhạy cảm) |
| **T** | 19 | Điện thoại 1 | Text (Nhạy cảm) |
| **U** | 20 | Điện thoại 2 | Text (Nhạy cảm) |
| **V** | 21 | Loại Hợp đồng | Text |
| **W** | 22 | Số ngày ký | Number |
| **X** | 23 | Ngày bắt đầu | Date |
| **Y** | 24 | Ngày kết thúc | Date |
| **Z** | 25 | Người ký | Text |
| **AA** | 26 | Trạng thái | Text |
| **AB** | 27 | Sơ đồ thửa đất 1 | Image URL |
| **AC** | 28 | Sơ đồ thửa đất 2 | Image URL |
| **AD** | 29 | Hình Mặt Tiền | Image URL |
| **AE-AN**| 30-39 | Hình Hẻm 1 -> 10 | Image URLs (10 ảnh ngõ hẻm lối vào) |
| **AO-BC**| 40-54 | Ảnh 1 -> Ảnh 15 | Image URLs (15 ảnh nội thất public công khai) |
| **BD** | 55 | Mã Khang Ngô (ID) | Tự sinh bằng hàm Hash bảo mật |
| **BE** | 56 | Tiêu đề Public | Tiêu đề hiển thị cho Khách |
| **BF** | 57 | Mô tả Public | Mô tả đã viết lại (ẩn số nhà thật) |
| **BG** | 58 | Giá Public | Giá hiển thị cho khách |
| **BH** | 59 | Phân loại Hẻm | `Mặt tiền` hoặc `Hẻm ba gác`, `Hẻm ô tô`... |
| **BI** | 60 | Đường trước nhà (m) | Số mét độ rộng hẻm trước nhà |
| **BJ** | 61 | Tình trạng nhà | `Mới`, `Bình thường`, `Nát` |
| **BK** | 62 | Ảnh Public (VD: 1,3,5)| Danh sách chỉ số ảnh nội thất được chọn hiển thị |
| **BL** | 63 | Ảnh Hẻm Public (VD: 1,2)| Danh sách chỉ số ảnh hẻm được chọn hiển thị |
| **BM** | 64 | Số phòng ngủ | Number |
| **BN** | 65 | Số nhà vệ sinh | Number |
| **BO** | 66 | Phường cũ (AI) | Phường cũ trước sáp nhập hành chính |
| **BP** | 67 | Đánh giá (Admin) | Hàng Ngon / Lỗi |
| **BQ** | 68 | Ngủ trệt (Admin) | Có / Không |
| **BR** | 69 | CHDV (Admin) | Có / Không |
| **BS** | 70 | Duyệt Public | Checkbox `TRUE`/`FALSE` |
| **BT** | 71 | Trạng thái Public | `Chờ duyệt` -> `Đã đẩy Public` / `Đã đồng bộ` |
| **BU** | 72 | System ID | System ID cố định làm khóa chia sẻ |
| **BV** | 73 | Link Gốc | Link gốc bài đăng trên hệ thống nội bộ |
| **BW** | 74 | Điện thoại Đầu Chủ | Text (Nhạy cảm) |
| **BX** | 75 | Tên Đầu Chủ (Hợp đồng)| Text (Nhạy cảm) |
| **BY** | 76 | Điểm Facebook | Link Facebook của đầu chủ |
| **BZ** | 77 | Last Crawl | Thời gian cào tin cục bộ |
| **CA** | 78 | Last Sync | Thời gian đồng bộ tin lên Source/Public |
| **CB** | 79 | Mã TK Mới | Mã tài khoản mới của đầu chủ |
| **CC** | 80 | Sơ đồ thửa đất 3 | Image URL |
| **CD** | 81 | Sơ đồ thửa đất 4 | Image URL |
| **CE** | 82 | Sơ đồ thửa đất 5 | Image URL |
| **CF-CO**| 83-92 | Ảnh 16 -> Ảnh 25 | Image URLs (10 ảnh nội thất bổ sung mới) |

---

## 2. FILE SOURCE & PUBLIC (ĐỒNG BỘ HIỂN THỊ WEB KHÁCH HÀNG)

- **Source ID:** `1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE` (Tab `Source` - 46 cột)
- **Public ID:** `1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0` (Tab `Public` - 43 cột)
- **Mối tương quan:**
  - Ô A3 của Public chứa công thức: `=IMPORTRANGE("Source!D3:AT1000")`
  - Bỏ qua 3 cột nhạy cảm đầu tiên của Source: Col A (`Hinh_mat_tien` formula), Col B (`Cu_phap`), Col C (`Note`).
  - Do đó: `JS Index trong Client = Chỉ số ở Source - 3`

### Danh sách mapping cột Public (Index 0 đến 42):
- **Index 0 - 16:** id, tieu_de, dien_tich, so_tang, mat_tien, gia, quan, phuong, loai_hinh, huong_nha, duong_truoc_nha, do_rong_hem, tinh_trang_nha, danh_gia, ngu_tang_tret, chdv, mo_ta
- **Index 17 - 26:** `anh_1` -> `anh_10` (Public Col R -> AA)
- **Index 27 - 34:** Last updated, phuong_cu, so_pn, so_wc, ten_duong, gio_dang, trang_thai, System ID
- **Index 35:** `Hình Mặt Tiền` (`hinh_mat_tien`) (Public Col AJ, Source Col AM)
- **Index 36:** `Tiêu đề BDS` (`tieu_de_bds`) (Public Col AK, Source Col AN)
- **Index 37:** `Đăng BDS` (`dang_bds` checkbox) (Public Col AL, Source Col AO)
- **Index 38 - 42:** `anh_11` -> `anh_15` (Public Col AM -> AQ, Source Col AP -> AT)

---

## 3. CƠ SỞ DỮ LIỆU SQLITE CỤC BỘ (`raw_archive.db`)

Dùng để lưu trữ toàn bộ lịch sử cào tin từ extension, làm cache cho Curator App trước khi đẩy lên Google Sheets.

### A. Bảng `listings` (100 cột)
Chứa đầy đủ:
- **6 cột hệ thống riêng:** `id` (INTEGER AUTOINCREMENT), `tk_id` (TEXT UNIQUE - mã tin gốc), `status` (TEXT - raw_text / raw_complete / published), `raw_images_tk_json` (JSON danh sách ảnh gốc), `raw_drive_images_json` (JSON danh sách ảnh up drive), `curated_config_json` (cấu hình crop/tagging của admin).
- **1 cột kỹ thuật thêm:** `Chieu_dai` (TEXT).
- **93 cột nghiệp vụ:** Ánh xạ 1:1 từ `POOL_HEADERS` của sheet Pool (đã được sanitize tiếng Việt và ký tự đặc biệt thành safe column name dạng `Ma_Hang`, `Anh_1`, `Anh_16`, `Last_Crawl`, `Last_Sync`, `So_do_thua_dat_3`...).

### B. Bảng `crawl_sessions`
Lưu trữ thông tin lịch sử các phiên cào tin để đo lường hiệu suất và trạng thái cookie.
- `id` (INTEGER PRIMARY KEY)
- `cookie_sig` (TEXT)
- `start_time` (TEXT)
- `end_time` (TEXT)
- `duration` (REAL)
- `crawled_count` (INTEGER)
- `status` (TEXT)
