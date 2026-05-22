# Schema — Sheet Source (BĐS Khang Ngô)

> **Mục đích:** Sheet Source là cơ sở dữ liệu trung gian và là bảng chứa dữ liệu đã được tùy chỉnh/duyệt của Admin trước khi đưa lên Website và phục vụ Bot Playwright đăng tin tự động lên batdongsan.com.vn.
>
> **Người dùng cuối:** Admin (anh Khang) duyệt tin, biên tập và chạy các công cụ AI SEO.
>
> **Source of truth:** file này. Mọi thay đổi cấu trúc cột của sheet Source phải được lưu trữ và đồng bộ tại đây.

---

## Cấu trúc 41 cột của sheet Source

| # | Tên cột | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|---|
| 1 | `Hinh_mat_tien` | formula | ✅ | Tự động hiển thị ảnh đại diện bằng công thức `=IMAGE(AM[row])`. |
| 2 | `Cu_phap` | text | ✅ | Cú pháp rút gọn phục vụ hiển thị nhanh. |
| 3 | `Note` | text | ⬜ | Ghi chú tùy chỉnh của Admin trên sheet Source. |
| 4 | `id` | text (13 ký tự) | ✅ | Mã căn hash từ địa chỉ thật (Mã Khang Ngô). Khóa chính. |
| 5 | `tieu_de` | text | ✅ | Tiêu đề Public phục vụ website tìm nhà. |
| 6 | `dien_tich` | number | ✅ | Diện tích thực tế (m2). |
| 7 | `so_tang` | integer | ✅ | Kết cấu số tầng. |
| 8 | `mat_tien` | number | ✅ | Chiều ngang/mặt tiền của căn nhà (m). |
| 9 | `gia` | number (tỷ) | ✅ | Giá chào của căn nhà (tỷ). |
| 10 | `quan` | text | ✅ | Tên quận đầy đủ hoặc viết tắt (VD: 3, 10, PN, TB). |
| 11 | `phuong` | text | ✅ | Tên phường thật của căn nhà. |
| 12 | `loai_hinh` | enum | ✅ | `Mặt tiền` hoặc `Hẻm`. |
| 13 | `huong_nha` | enum | ⬜ | Hướng nhà (Đông, Tây, Nam, Bắc...). |
| 14 | `duong_truoc_nha` | enum | ✅ | Phân loại hẻm: `Hẻm ba gác`, `Hẻm ô tô`... |
| 15 | `do_rong_hem` | number (m) | ⬜ | Độ rộng hẻm thực tế trước nhà (m). |
| 16 | `tinh_trang_nha` | enum | ✅ | `Mới`, `Bình thường`, `Nát`. |
| 17 | `danh_gia` | enum | ⬜ | Đánh giá nội bộ: `Hàng Ngon`, `Hàng Lỗi`... |
| 18 | `ngu_tang_tret` | text | ⬜ | Có ngủ trệt hay không. |
| 19 | `chdv` | text | ⬜ | Có căn hộ dịch vụ hay không. |
| 20 | `mo_ta` | text dài | ✅ | Mô tả tóm tắt đã viết lại cho khách (không chứa số nhà). |
| 21-30 | `anh_1` ... `anh_10` | URL | ⬜ | 10 link ảnh đã xử lý phục vụ đăng tin/website. |
| 31 | `Last updated` | datetime | ✅ | Thời gian đồng bộ/cập nhật cuối cùng. |
| 32 | `phuong_cu` | text | ⬜ | Tên phường cũ trước sáp nhập hành chính (AI sinh). |
| 33 | `so_pn` | integer | ⬜ | Số phòng ngủ. |
| 34 | `so_wc` | integer | ⬜ | Số nhà vệ sinh. |
| 35 | `ten_duong` | text | ✅ | Tên đường thật (dùng cho bot đăng tin). |
| 36 | `gio_dang` | time | ⬜ | Giờ đăng tin theo lịch. |
| 37 | `trang_thai` | text | ⬜ | Trạng thái đăng tin của Bot (VD: "🔄 Đang đăng...", "Đã đăng"). |
| 38 | `System ID` | text | ✅ | System ID để join dữ liệu và quản lý đăng tin. |
| 39 | `Hình Mặt Tiền` | URL | ✅ | Link hình ảnh mặt tiền gốc. |
| 40 | `Tiêu đề BDS` | text | ⬜ | **[NEW]** Tiêu đề tin đăng ngắn gọn dưới 85 ký tự (Admin viết tay hoặc dùng AI SEO Tools). |
| 41 | `Đăng BDS` | checkbox | ✅ | **[SHIFTED]** Checkbox kích hoạt Bot đăng tin tự động (Cột AO). |

---

## Cơ chế đồng bộ từ Pool (Smart Merge)

Khi thực hiện đồng bộ từ sheet `Pool` sang sheet `Source`, hệ thống sử dụng cơ chế bảo vệ cột **Smart Merge** để chống ghi đè dữ liệu viết tay của Admin.

* **Các cột được bảo vệ (không bao giờ bị ghi đè khi đồng bộ lần 2 trở đi):**
  - Cú pháp (Cột 2)
  - Note (Cột 3)
  - Tiêu đề Public (Cột 5)
  - Hướng nhà (Cột 13)
  - Đường trước nhà (Cột 14)
  - Tình trạng nhà (Cột 16)
  - Đánh giá (Cột 17)
  - Ngủ trệt (Cột 18)
  - CHDV (Cột 19)
  - Mô tả Public (Cột 20)
  - Ảnh 1 - Ảnh 10 (Cột 21 - Cột 30)
  - **Tiêu đề BDS** (Cột 40, index 39)
  - **Đăng BDS** (Cột 41, index 40)
