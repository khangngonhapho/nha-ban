# Schema — Sheet Public

> **Mục đích:** Sheet Public là nguồn dữ liệu cho website tìm nhà của khách hàng. KHÔNG chứa thông tin nhạy cảm (số nhà thật, tên đầu chủ, SĐT, hợp đồng, sổ).
>
> **Người dùng cuối:** khách hàng cuối qua website + anh Khang khi tìm sản phẩm.
>
> **Source of truth:** file này. Mọi thay đổi cấu trúc cột phải sync về đây.

---

## Cấu trúc 27 cột

| # | Tên cột | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|---|
| 1 | `id` | text (13 ký tự) | ✅ | Mã căn hash từ địa chỉ thật. Xem [Quy tắc đặt mã nhà.md](./Quy%20t%E1%BA%AFc%20%C4%91%E1%BA%B7t%20m%C3%A3%20nh%C3%A0.md). Khóa chính, dùng để join với Sheet Raw. |
| 2 | `tieu_de` | text | ✅ | Tiêu đề ngắn gọn 1 dòng. KHÔNG chứa số nhà thật. Mẫu: `[Tên đường gần] (gần [landmark]) [DT]m2 [tầng] [mặt tiền/ngang]x[dài] - [giá] [loại đường]` |
| 3 | `dien_tich` | number (m²) | ✅ | Diện tích sàn xây dựng. Số thập phân OK. |
| 4 | `so_tang` | integer | ✅ | Số tầng. |
| 5 | `mat_tien` | number (m) | ✅ | **Chiều rộng nhà** (mặt tiền căn nhà). |
| 6 | `gia` | number (tỷ) | ✅ | Giá hiện tại đang chào. Đơn vị: tỷ. |
| 7 | `quan` | text | ✅ | Tên quận đầy đủ hoặc viết tắt (VD: 3, 10, PN, TB). |
| 8 | `phuong` | text | ✅ | Tên phường thật. Giữ nguyên không ẩn. |
| 9 | `loai_hinh` | enum | ✅ | `Mặt tiền` hoặc `Hẻm`. |
| 10 | `huong_nha` | enum | ⬜ | Một trong: `Đông`, `Tây`, `Nam`, `Bắc`, `Đông Nam`, `Đông Bắc`, `Tây Nam`, `Tây Bắc`. Để trống nếu không rõ. |
| 11 | `duong_truoc_nha` | enum | ✅ | Phân loại đường trước nhà: `Hẻm ba gác`, `Hẻm ô tô lý thuyết`, `Hẻm ô tô`. (Nếu mặt tiền: vẫn ghi loại đường tương đương.) |
| 12 | `do_rong_hem` | number (m) | ⬜ | Độ rộng hẻm chính/lối vào (≠ `mat_tien`). Để trống/0 nếu mặt tiền. |
| 13 | `tinh_trang_nha` | enum | ✅ | `Mới`, `Bình thường`, `Nát`. |
| 14 | `danh_gia` | enum | ⬜ | Đánh giá phân loại: `Hàng Ngon`, `Hàng Lỗi`. Mặc định trống. |
| 15 | `ngu_tang_tret` | text | ⬜ | Có ngủ trệt hay không. Dùng cho mục đích khác. |
| 16 | `chdv` | text | ⬜ | Căn hộ dịch vụ. Dùng cho mục đích khác. |
| 17 | `mo_ta` | text dài | ✅ | Mô tả đã viết lại để hiển thị cho khách. KHÔNG chứa tên đường thật. |
| 18-27 | `anh_1` ... `anh_10` | URL | ⬜ | Tối đa 10 link Google Drive dạng `https://drive.google.com/file/d/[ID]/view`. |

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
