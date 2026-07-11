# Schema — Sheet Raw

> **Mục đích:** Sheet Raw là kho dữ liệu đầy đủ và thật. Chứa tất cả thông tin nhạy cảm (số nhà, đầu chủ, SĐT, sổ, hợp đồng) + thông số kỹ thuật + ghi chú nội bộ.
>
> **Người dùng cuối:** chỉ Trang (admin/thiết kế hệ thống) và anh Khang (môi giới).
>
> **KHÔNG** chia sẻ ra ngoài. **KHÔNG** kết nối website công khai.
>
> **Source of truth:** file này. Mọi thay đổi cấu trúc cột phải sync về đây.

---

## Cấu trúc cột (theo nhóm)

### Nhóm A — Khóa & metadata

| # | Tên cột | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|---|
| 1 | `id` | text (13 ký tự) | ✅ | Mã căn hash từ địa chỉ thật. Khóa chính, dùng chung với Sheet Public. Sinh tự động theo [Quy tắc đặt mã nhà](./Quy%20t%E1%BA%AFc%20%C4%91%E1%BA%B7t%20m%C3%A3%20nh%C3%A0.md). |
| 2 | `ngay_nhap` | date | ✅ | Ngày nhập vào hệ thống. Auto-fill khi thêm dòng. |
| 3 | `trang_thai` | enum | ✅ | `Đang bán` / `Đã bán` / `Tạm dừng`. |

### Nhóm B — Địa chỉ & người (KHÔNG sync sang Public)

| # | Tên cột | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|---|
| 4 | `so_nha_that` | text | ✅ | Số nhà thật. Vd: `163.24.80`, `339/36c`. |
| 5 | `ten_duong_that` | text | ✅ | Tên đường thật. Vd: `Tô Hiến Thành`, `Lê Văn Sỹ`. |
| 6 | `phuong` | text | ✅ | Tên phường (giữ thật, sync sang Public nguyên văn). Vd: `Hòa Hưng`. |
| 7 | `quan` | text | ✅ | Mã quận viết thường. Vd: `q10`. |
| 8 | `ten_quan` | text | ✅ | Tên quận đầy đủ. Vd: `Quận 10`. |
| 9 | `dau_chu` | text | ⬜ | Tên đầu chủ (chủ nhà thật). Vd: `Nguyễn Hoàng Nam`. |
| 10 | `sdt_dauchu` | text | ⬜ | SĐT đầu chủ. Vd: `0973776929`. |
| 11 | `nguon` | enum | ⬜ | `Đầu chủ` (làm việc trực tiếp) / `Môi giới` (qua trung gian). |
| 12 | `moi_gioi` | text | ⬜ | Tên người môi giới làm việc với chủ nhà (KHÔNG phải anh Khang). Vd: `Bảo Tín`. Để trống nếu nguồn = `Đầu chủ`. |

### Nhóm C — Thông số kỹ thuật (sync sang Public)

| # | Tên cột | Kiểu | Bắt buộc | Mô tả | Sync? |
|---|---|---|---|---|---|
| 13 | `dien_tich` | number (m²) | ✅ | Diện tích sàn xây dựng. | ✅ |
| 14 | `so_tang` | integer | ✅ | Số tầng. | ✅ |
| 15 | `mat_tien` | number (m) | ✅ | Chiều rộng nhà (mặt tiền căn nhà). | ✅ |
| 16 | `do_rong_hem` | number (m) | ⬜ | Độ rộng hẻm trước cửa nhà. Để trống/0 nếu loại hình = `Mặt tiền`. | ✅ |
| 17 | `huong_nha` | enum | ⬜ | 8 hướng. **Không bắt buộc lúc nhập — sẽ tự điền/cập nhật sau.** | ✅ |
| 18 | `loai_hinh` | enum | ✅ | `Mặt tiền` / `Hẻm`. | ✅ |
| 19 | `duong_truoc_nha` | enum | ✅ | `Hẻm ba gác` / `Hẻm ô tô lý thuyết` / `Hẻm ô tô`. | ✅ |
| 20 | `tinh_trang_nha` | enum | ✅ | `Mới` / `Bình thường` / `Nát`. | ✅ |

### Nhóm D — Thông số chi tiết (CHỈ Raw)

| # | Tên cột | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|---|
| 21 | `dai_nha` | number (m) | ⬜ | Chiều dài/sâu nhà. Vd: `13`. (Chiều rộng nhà đã có trong `mat_tien`.) |
| 22 | `so_phong_ngu` | integer | ⬜ | Số phòng ngủ. Vd: `6`. |
| 23 | `so_wc` | integer | ⬜ | Số WC. Vd: `4`. |
| 24 | `phap_ly` | text | ⬜ | Mô tả pháp lý. Vd: `Sổ vuông vức, nở hậu nhẹ, phong thủy tốt`. |

### Nhóm E — Giá

| # | Tên cột | Kiểu | Bắt buộc | Mô tả | Sync? |
|---|---|---|---|---|---|
| 25 | `gia` | number (tỷ) | ✅ | Giá hiện tại đang chào. | ✅ |
| 26 | `gia_chao` | number (tỷ) | ⬜ | Giá ban đầu trước khi giảm/thương lượng. | ❌ |
| 27 | `co_thuong_luong` | boolean | ⬜ | TRUE/FALSE — có thể thương lượng. | ❌ |
| 28 | `ghi_chu_gia` | text | ⬜ | Vd: `Giảm 300tr còn 12.9 tỷ TL`. | ❌ |

### Nhóm F — Mô tả

| # | Tên cột | Kiểu | Bắt buộc | Mô tả | Sync? |
|---|---|---|---|---|---|
| 29 | `tieu_de` | text | ✅ | Tiêu đề ngắn gọn 1 dòng cho Public. KHÔNG có số nhà thật. | ✅ |
| 30 | `mo_ta` | text dài | ✅ | Mô tả đã viết lại cho Public (đường thật → đường lớn gần). | ✅ |
| 31 | `mo_ta_goc` | text dài | ⬜ | Text gốc copy nguyên từ chủ/môi giới gửi. Lưu để tham chiếu. | ❌ |
| 32 | `ghi_chu_noi_bo` | text | ⬜ | Note riêng của Trang/anh Khang (vd "khách quan tâm tuần này", "chủ kẹt tiền"). | ❌ |

### Nhóm G — Ảnh & file

| # | Tên cột | Kiểu | Bắt buộc | Mô tả | Sync? |
|---|---|---|---|---|---|
| 33 | `link_folder_drive` | URL | ⬜ | Link folder Drive chứa hình của căn này. Vd: `https://drive.google.com/drive/folders/[ID]`. | ❌ |
| 34-43 | `anh_1` ... `anh_10` | URL | ⬜ | Link drive_link 10 ảnh nhà. | ✅ |
| 44 | `link_hinh_phap_ly` | URL | ⬜ | Link folder/file hình sổ + hợp đồng đặt cọc. **TUYỆT ĐỐI KHÔNG sync sang Public.** | ❌ |

**Tổng cộng: 44 cột.**

---

## Mapping Raw → Public

| Cột Public         | Lấy từ Raw         | Rule biến đổi                       |
| ------------------ | ------------------ | ----------------------------------- |
| `id`               | `id`               | copy nguyên                         |
| `tieu_de`          | `tieu_de`          | copy nguyên (đã viết lại sẵn ở Raw) |
| `dien_tich`        | `dien_tich`        | copy nguyên                         |
| `so_tang`          | `so_tang`          | copy nguyên                         |
| `mat_tien`         | `mat_tien`         | copy nguyên                         |
| `gia`              | `gia`              | copy nguyên (KHÔNG copy `gia_chao`) |
| `quan`             | `quan`             | copy nguyên                         |
| `ten_quan`         | `ten_quan`         | copy nguyên                         |
| `phuong`           | `phuong`           | copy nguyên (giữ tên thật)          |
| `loai_hinh`        | `loai_hinh`        | copy nguyên                         |
| `huong_nha`        | `huong_nha`        | copy nguyên                         |
| `duong_truoc_nha`  | `duong_truoc_nha`  | copy nguyên                         |
| `do_rong_hem`      | `do_rong_hem`      | copy nguyên                         |
| `tinh_trang_nha`   | `tinh_trang_nha`   | copy nguyên                         |
| `mo_ta`            | `mo_ta`            | copy nguyên (đã viết lại sẵn ở Raw) |
| `anh_1`...`anh_10` | `anh_1`...`anh_10` | copy nguyên                         |

**KHÔNG sync sang Public:** `ngay_nhap`, `trang_thai`, `so_nha_that`, `ten_duong_that`, `dau_chu`, `sdt_dauchu`, `nguon`, `moi_gioi`, `dai_nha`, `so_phong_ngu`, `so_wc`, `phap_ly`, `gia_chao`, `co_thuong_luong`, `ghi_chu_gia`, `mo_ta_goc`, `ghi_chu_noi_bo`, `link_folder_drive`, `link_hinh_phap_ly`.

---

## Ví dụ 1 dòng (căn 163.24.80 Tô Hiến Thành Q10)

### Input gốc

- **Text:** `163.24.80 Tô Hiến Thành 50.2 5 4 13 12.9 tỷ Hòa Hưng Quận 10 10-15 tỷ HĐ Nguyễn Hoàng Nam Bảo Tín 0973776929 H3GB nguồn Đầu chủ Nguyễn Hoàng Nam - Bảo Tín`
- **Hình listing:** mô tả "Nhà 5 tầng kiên cố, 6 phòng ngủ - 4 WC, hẻm xe tải vào tận cửa, sổ vuông vức..."

### Dòng Raw được tạo

```
id                : MWSBIHAITOITHT
ngay_nhap         : 2026-05-07
trang_thai        : Đang bán
so_nha_that       : 163.24.80
ten_duong_that    : Tô Hiến Thành
phuong            : Hòa Hưng
quan              : q10
ten_quan          : Quận 10
dau_chu           : Nguyễn Hoàng Nam
sdt_dauchu        : 0973776929
nguon             : Đầu chủ
moi_gioi          : Bảo Tín
dien_tich         : 50.2
so_tang           : 5
mat_tien          : 4              ← chiều rộng nhà
do_rong_hem       : (m hẻm trước nhà, để trống nếu mặt tiền)
huong_nha         : (để trống, sẽ tự điền sau)
loai_hinh         : Hẻm
duong_truoc_nha   : Hẻm ô tô
tinh_trang_nha    : Mới
dai_nha           : 13
so_phong_ngu      : 6
so_wc             : 4
phap_ly           : Sổ vuông vức, nở hậu nhẹ, phong thủy tốt
gia               : 12.9
gia_chao          : 13.2
co_thuong_luong   : TRUE
ghi_chu_gia       : Giảm 300tr còn 12.9 tỷ TL
tieu_de           : Tô Hiến Thành (gần Trường Sơn) 50.2m2 5 tầng 4x13 - 12.9 tỷ Hẻm xe tải
mo_ta             : Nhà 5 tầng kiên cố, 6 phòng ngủ, 4 WC tại khu trung tâm Quận 10 gần đường Trường Sơn / Lý Thái Tổ. Sổ vuông vức, nở hậu nhẹ, phong thủy tốt. Hẻm ô tô vào tận cửa, thuận tiện di chuyển Q1, Q3, Q5. Phù hợp ở kết hợp kinh doanh hoặc cho thuê.
mo_ta_goc         : (text gốc copy nguyên)
ghi_chu_noi_bo    : HĐ ĐT, hoa hồng H3GB
link_folder_drive : https://drive.google.com/drive/folders/[ID]
anh_1             : https://drive.google.com/file/d/.../view?usp=drive_link
...
link_hinh_phap_ly : https://drive.google.com/drive/folders/[ID-pháp-lý]
```

---

## Ràng buộc & validation

- **`id` duy nhất**, sinh tự động theo Quy tắc đặt mã nhà từ `so_nha_that` + `ten_duong_that`. Nếu trùng → cảnh báo.
- **`tieu_de` và `mo_ta` không được chứa `so_nha_that` hoặc `ten_duong_that`** — script kiểm tra trước khi sync sang Public.
- **`dien_tich` ≈ `mat_tien` × `dai_nha`** (sai lệch <10% là OK; nếu lệch nhiều, cảnh báo).
- **`gia` ≤ `gia_chao`** nếu cả 2 cùng có.
- **Khi `loai_hinh = Mặt tiền`**: `do_rong_hem` để trống/0, `duong_truoc_nha` vẫn ghi (vd "Đường ô tô").
- **Khi `nguon = Đầu chủ`**: `moi_gioi` để trống.
- **`huong_nha` không bắt buộc lúc nhập** — sẽ tự điền/bổ sung sau (qua khảo sát thực địa hoặc API la bàn).
- **`huong_nha` extract từ đâu**: text gốc lúc trước không có thông tin hướng. Có cần thêm trường này vào input bắt buộc, hay để trống nếu không nêu?
