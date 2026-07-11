# Schema — Sheet Public

> **Mục đích:** Sheet Public là nguồn dữ liệu cho website tìm nhà của khách hàng. KHÔNG chứa thông tin nhạy cảm (số nhà thật, tên đầu chủ, SĐT, hợp đồng, sổ).
>
> **Người dùng cuối:** khách hàng cuối qua website + anh Khang khi tìm sản phẩm.
>
> **Source of truth:** file này. Mọi thay đổi cấu trúc cột phải sync về đây.

---

## Cấu trúc 43 cột của sheet Public

> ⚠️ **Quy tắc lệch chỉ số cột (Column Shift):**
> Dữ liệu được đồng bộ từ sheet **Source** sang sheet **Public** thông qua công thức `=IMPORTRANGE("Source!D3:AT1000")` đặt ở cell A3 để giấu đi 3 cột nhạy cảm đầu tiên của Source (Cột A: `Hinh_mat_tien`, Cột B: `Cu_phap`, Cột C: `Note`).
> Do đó, toàn bộ chỉ số cột trong code javascript client (`r.c[index]`) bị **dịch sang trái đúng 3 cột** so với cấu trúc cột trên sheet Source gốc:
> `Chỉ số Public = Chỉ số Source - 3`

| # | Tên cột Public | JS Index | Kiểu | Bắt buộc | Chỉ số ở Source | Mô tả |
|---|---|---|---|---|---|---|
| 1 | `id` | `r.c[0]` | text (13 ký tự) | ✅ | D (index 3) | Mã căn hash từ địa chỉ thật. Khóa chính, dùng để join với Sheet Raw. |
| 2 | `tieu_de` | `r.c[1]` | text | ✅ | E (index 4) | Tiêu đề ngắn gọn 1 dòng. KHÔNG chứa số nhà thật. |
| 3 | `dien_tich` | `r.c[2]` | number (m²) | ✅ | F (index 5) | Diện tích sàn xây dựng. |
| 4 | `so_tang` | `r.c[3]` | integer | ✅ | G (index 6) | Số tầng. |
| 5 | `mat_tien` | `r.c[4]` | number (m) | ✅ | H (index 7) | **Chiều rộng nhà** (mặt tiền căn nhà). |
| 6 | `gia` | `r.c[5]` | number (tỷ) | ✅ | I (index 8) | Giá hiện tại đang chào. Đơn vị: tỷ. |
| 7 | `quan` | `r.c[6]` | text | ✅ | J (index 9) | Tên quận đầy đủ hoặc viết tắt (VD: 3, 10, PN, TB). |
| 8 | `phuong` | `r.c[7]` | text | ✅ | K (index 10) | Tên phường thật. Giữ nguyên không ẩn. |
| 9 | `loai_hinh` | `r.c[8]` | enum | ✅ | L (index 11) | `Mặt tiền` hoặc `Hẻm`. |
| 10 | `huong_nha` | `r.c[9]` | enum | ⬜ | M (index 12) | Hướng nhà (Đông, Tây, Nam, Bắc...). |
| 11 | `duong_truoc_nha` | `r.c[10]` | enum | ✅ | N (index 13) | Phân loại đường: `Hẻm ba gác`, `Hẻm ô tô`... |
| 12 | `do_rong_hem` | `r.c[11]` | number (m) | ⬜ | O (index 14) | Độ rộng hẻm lối vào. |
| 13 | `tinh_trang_nha` | `r.c[12]` | enum | ✅ | P (index 15) | `Mới`, `Bình thường`, `Nát`. |
| 14 | `danh_gia` | `r.c[13]` | enum | ⬜ | Q (index 16) | Đánh giá phân loại: `Hàng Ngon`, `Hàng Lỗi`. |
| 15 | `ngu_tang_tret` | `r.c[14]` | text | ⬜ | R (index 17) | Có ngủ trệt hay không. |
| 16 | `chdv` | `r.c[15]` | text | ⬜ | S (index 18) | Căn hộ dịch vụ. |
| 17 | `mo_ta` | `r.c[16]` | text dài | ✅ | T (index 19) | Mô tả đã viết lại để hiển thị cho khách. |
| 18-27 | `anh_1` ... `anh_10` | `r.c[17..26]` | URL | ⬜ | U–AD (index 20–29) | Tối đa 10 link ảnh từ Google Drive. |
| 28 | `Last updated` | `r.c[27]` | datetime | ✅ | AE (index 30) | Ngày giờ cập nhật cuối cùng. |
| 29 | `phuong_cu` | `r.c[28]` | text | ⬜ | AF (index 31) | Phường cũ trước sáp nhập hành chính. |
| 30 | `so_pn` | `r.c[29]` | integer | ⬜ | AG (index 32) | Số phòng ngủ. |
| 31 | `so_wc` | `r.c[30]` | integer | ⬜ | AH (index 33) | Số nhà vệ sinh. |
| 32 | `ten_duong` | `r.c[31]` | text | ✅ | AI (index 34) | Tên đường thật phục vụ Bot đăng tin. |
| 33 | `gio_dang` | `r.c[32]` | time | ⬜ | AJ (index 35) | Giờ đăng tin theo lịch. |
| 34 | `trang_thai` | `r.c[33]` | text | ⬜ | AK (index 36) | Trạng thái đăng tin. |
| 35 | `System ID` | `r.c[34]` | text | ✅ | AL (index 37) | System ID cố định dùng để làm mỏ neo link chia sẻ. |
| 36 | `Hình Mặt Tiền` | `r.c[35]` | URL | ✅ | AM (index 38) | Link ảnh mặt tiền gốc (dùng riêng cho Admin). |
| 37 | `Tiêu đề BDS` | `r.c[36]` | text | ⬜ | AN (index 39) | Tiêu đề BDS AI phục vụ Bot đăng tin. |
| 38 | `Đăng BDS` | `r.c[37]` | checkbox | ✅ | AO (index 40) | Checkbox kích hoạt Bot đăng tin tự động. |
| 39 | `anh_11` | `r.c[38]` | URL | ⬜ | AP (index 41) | Ảnh bổ sung thứ 11. |
| 40 | `anh_12` | `r.c[39]` | URL | ⬜ | AQ (index 42) | Ảnh bổ sung thứ 12. |
| 41 | `anh_13` | `r.c[40]` | URL | ⬜ | AR (index 43) | Ảnh bổ sung thứ 13. |
| 42 | `anh_14` | `r.c[41]` | URL | ⬜ | AS (index 44) | Ảnh bổ sung thứ 14. |
| 43 | `anh_15` | `r.c[42]` | URL | ⬜ | AT (index 45) | Ảnh bổ sung thứ 15. |

---

## Ví dụ 1 dòng (căn 163.24.80 Tô Hiến Thành)

```
id              : MWSBIHAITOITHT
tieu_de         : Tô Hiến Thành (gần Trường Sơn) 50.2m2 5 tầng 4x13 - 12.9 tỷ Hẻm xe tải
dien_tich       : 50.2
so_tang         : 5
mat_tien        : 4              ← chiều rộng nhà
gia             : 12.9
quan            : q10
ten_quan        : Quận 10
phuong          : Hòa Hưng
loai_hinh       : Hẻm
huong_nha       : (để trống nếu chưa biết)
duong_truoc_nha : Hẻm ô tô
do_rong_hem     : (số mét hẻm chính, vd 5)
tinh_trang_nha  : Mới
mo_ta           : Nhà 5 tầng kiên cố, 6 phòng ngủ, 4 WC tại khu trung tâm Quận 10 gần đường Trường Sơn / Lý Thái Tổ. Sổ vuông vức, nở hậu nhẹ, phong thủy tốt. Hẻm ô tô vào tận cửa, thuận tiện di chuyển Q1, Q3, Q5. Phù hợp ở kết hợp kinh doanh hoặc cho thuê.
anh_1           : https://drive.google.com/file/d/.../view?usp=drive_link
anh_2           : https://drive.google.com/file/d/.../view?usp=drive_link
...
```

---

## Ràng buộc & quy ước

- **Khóa chính `id`**: duy nhất, không trùng. Sinh tự động theo Quy tắc đặt mã nhà.
- **`mo_ta` viết lại theo rule:** thay tên đường thật bằng tên đường lớn gần đó (vd Tô Hiến Thành → Trường Sơn / Lý Thái Tổ); giữ lại thông tin kỹ thuật (diện tích, kết cấu, pháp lý, hướng); BỎ thông tin chủ nhà / SĐT / mã hợp đồng / hoa hồng / nguồn.
- **Link ảnh giữ nguyên format `drive_link`** — KHÔNG pre-process. Website tự xử lý qua `fixImgUrl`.
- **KHÔNG có cột nào chứa**: số nhà thật, tên đường thật (chỉ trong tiêu đề/mô tả ở dạng tham chiếu gần), tên đầu chủ, SĐT, môi giới, hợp đồng, sổ pháp lý, ghi chú nội bộ, giá chào ban đầu trước thương lượng.

---

## Sync với Sheet Raw

Mỗi dòng Public tương ứng 1 dòng Raw cùng `id`. Một số tùy chọn sync:

- **`IMPORTRANGE` + công thức biến đổi** trong từng cell: nhanh setup, nhưng phức tạp khi có nhiều rule biến đổi text.
- **Apps Script trigger**: khi Raw thay đổi → script ghi lại Public. Linh hoạt, kiểm soát được. **Đây là phương án khuyến nghị.**
- **Manual**: nhập thẳng vào cả 2 sheet song song. Không khuyến nghị vì dễ lệch dữ liệu.

Chi tiết logic biến đổi xem trong [Schema Sheet Raw.md](./Schema%20Sheet%20Raw.md).
