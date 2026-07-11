# Drive Naming Rules — Hệ thống lưu trữ hình BĐS

> **Mục đích:** Quy ước đặt tên folder, file ảnh trên Google Drive cho hệ thống quản lý nhà. Đảm bảo tìm nhanh, sync chuẩn với 2 Sheet (Raw + Public), bảo mật hình pháp lý.
>
> **Source of truth:** file này. Mọi thay đổi naming phải sync về đây.

---

## 1. Cấu trúc folder tổng

```
BDS-KhangNgo/                         ← folder gốc trên Drive
│
├── 01_HINH_NHA/                      ← hình nhà công khai (sync với Sheet Public)
│   ├── Q1/
│   ├── Q3/
│   ├── Q10/
│   │   └── MWSBIHAITOITHT/           ← tên folder = id căn nhà
│   │       ├── 01_mat-tien.jpg
│   │       ├── 02_phong-khach.jpg
│   │       ├── 03_phong-ngu.jpg
│   │       └── ...
│   ├── Q11/
│   ├── BinhThanh/                    ← quận có tên chữ thì viết liền không dấu
│   ├── TanBinh/
│   ├── PhuNhuan/
│   └── ...
│
├── 02_HINH_PHAP_LY/                  ← KHÔNG public, chỉ Trang + anh Khang
│   ├── Q10/
│   │   └── MWSBIHAITOITHT/
│   │       ├── 01_so.jpg
│   │       ├── 02_hop-dong.pdf
│   │       └── ...
│   └── ...
│
└── 99_ARCHIVE/                       ← căn đã bán hoặc tạm dừng
    ├── 01_HINH_NHA_archive/
    └── 02_HINH_PHAP_LY_archive/
```

---

## 2. Quy ước đặt tên folder

### 2.1 Folder cấp Quận (level 2)

| Quận | Tên folder |
|---|---|
| Quận 1 → 12 | `Q1`, `Q2`, ..., `Q12` |
| Bình Thạnh | `BinhThanh` |
| Tân Bình | `TanBinh` |
| Tân Phú | `TanPhu` |
| Phú Nhuận | `PhuNhuan` |
| Gò Vấp | `GoVap` |
| Bình Tân | `BinhTan` |
| Thủ Đức | `ThuDuc` |
| Nhà Bè | `NhaBe` |
| Bình Chánh | `BinhChanh` |
| Hóc Môn | `HocMon` |
| Củ Chi | `CuChi` |
| Cần Giờ | `CanGio` |

**Quy tắc:** viết liền, không dấu, viết hoa chữ đầu mỗi từ (PascalCase). Đảm bảo tên không trùng nhau.

### 2.2 Folder cấp căn nhà (level 3)

Tên folder = `id` của căn nhà (mã hash 13 ký tự, theo Quy tắc đặt mã nhà).

Vd: `MWSBIHAITOITHT`, `BWBCIBScISVL`.

**Lý do:** dùng `id` thay vì số nhà thật để (a) khớp với Sheet Public, (b) không lộ địa chỉ thật khi share folder, (c) ngắn gọn dễ search.

### 2.3 Folder hình pháp lý

Cùng cấu trúc Quận/id như folder hình nhà nhưng nằm trong nhánh `02_HINH_PHAP_LY/`. Một căn có 2 folder song song:
- `01_HINH_NHA/Q10/MWSBIHAITOITHT/` — hình nhà công khai
- `02_HINH_PHAP_LY/Q10/MWSBIHAITOITHT/` — hình sổ + HĐ riêng tư

---

## 3. Quy ước đặt tên file ảnh

### 3.1 Hình nhà (`01_HINH_NHA/`)

Format: `[STT]_[mô-tả-ngắn].jpg`

| STT | Mô tả | Ví dụ tên file |
|---|---|---|
| 01 | Mặt tiền nhà | `01_mat-tien.jpg` |
| 02 | Phòng khách | `02_phong-khach.jpg` |
| 03 | Phòng bếp | `03_phong-bep.jpg` |
| 04-06 | Phòng ngủ | `04_phong-ngu-1.jpg`, `05_phong-ngu-2.jpg`, ... |
| 07-08 | WC | `07_wc-1.jpg` |
| 09 | Sân thượng / sân vườn | `09_san-thuong.jpg` |
| 10 | Hẻm trước nhà | `10_hem.jpg` |
| 11+ | Bổ sung (góc nhìn khác, view...) | `11_view-ban-cong.jpg` |

**Quy tắc:**
- STT 2 chữ số (01, 02, ...) để sort đúng thứ tự khi liệt kê file.
- Mô tả viết thường, không dấu, dùng dấu gạch ngang `-` thay khoảng trắng.
- Đuôi file: `.jpg` (ưu tiên), `.png` (cho ảnh sơ đồ/screenshot), `.heic` đổi sang `.jpg` trước khi upload.
- Tối đa 10 ảnh/căn để khớp 10 cột `anh_1`...`anh_10` của Sheet Public. Nếu nhiều hơn, ưu tiên 10 ảnh đẹp nhất; ảnh dư để trong folder nhưng KHÔNG link vào Sheet.

### 3.2 Hình pháp lý (`02_HINH_PHAP_LY/`)

Format: `[STT]_[loại].jpg|pdf`

| STT | Loại | Ví dụ |
|---|---|---|
| 01 | Sổ hồng/đỏ — trang chính | `01_so-trang-chinh.jpg` |
| 02 | Sổ — sơ đồ vị trí | `02_so-so-do.jpg` |
| 03 | Sổ — biến động | `03_so-bien-dong.jpg` |
| 04 | Hợp đồng đặt cọc | `04_hop-dong-coc.pdf` |
| 05 | CMND/CCCD chủ nhà | `05_cmnd-chu.jpg` |
| 06+ | Giấy tờ khác | `06_giay-phep-xay-dung.pdf` |

---

## 4. Quy ước permissions (chia sẻ)

| Folder | Quyền | Ai truy cập |
|---|---|---|
| `BDS-KhangNgo/` (root) | Restricted | Trang + anh Khang |
| `01_HINH_NHA/` (cả nhánh) | **Anyone with link can view** | Public — để website render được ảnh |
| `02_HINH_PHAP_LY/` (cả nhánh) | Restricted | **CHỈ Trang + anh Khang**, không share link |
| `99_ARCHIVE/` | Restricted | Trang + anh Khang |

**Cách set:**
1. Right-click folder `01_HINH_NHA/` → Share → "Anyone with the link" → "Viewer". Quyền này tự inherit xuống tất cả folder con và file con.
2. Folder `02_HINH_PHAP_LY/` giữ default Restricted, KHÔNG share link cho ai khác Trang + anh Khang.

⚠ **Cảnh báo:** không bao giờ kéo file pháp lý vào nhánh `01_HINH_NHA/`. Nếu lỡ tay, di chuyển ngược lại NGAY và check website xem file có bị crawl không.

---

## 5. Workflow upload 1 căn mới

Khi có căn mới với `id = MWSBIHAITOITHT`, quận `q10`:

**Bước 1: Tạo folder**
- `01_HINH_NHA/Q10/MWSBIHAITOITHT/` (cho hình nhà)
- `02_HINH_PHAP_LY/Q10/MWSBIHAITOITHT/` (cho sổ + HĐ, nếu có)

**Bước 2: Đổi tên file local trước khi upload**
- 5-15 hình nhà từ máy → đổi tên theo quy ước `01_mat-tien.jpg` → `02_phong-khach.jpg` → ...
- Ảnh sổ/HĐ → tách riêng vào folder local khác trước khi upload.

**Bước 3: Upload**
- Drag-drop hình nhà vào `01_HINH_NHA/Q10/MWSBIHAITOITHT/`.
- Drag-drop hình pháp lý vào `02_HINH_PHAP_LY/Q10/MWSBIHAITOITHT/`.

**Bước 4: Lấy link**
- Mở từng file hình nhà → Get link → copy URL `https://drive.google.com/file/d/.../view?usp=drive_link`.
- Paste vào cột `anh_1`, `anh_2`, ... của dòng tương ứng trong Sheet Raw.
- Sheet Public tự sync (qua Apps Script ở Giai đoạn 2; manual ở Giai đoạn 1).

**Bước 5: Update Sheet Raw**
- `link_folder_drive`: copy link folder `01_HINH_NHA/Q10/MWSBIHAITOITHT/`.
- `link_hinh_phap_ly`: copy link folder `02_HINH_PHAP_LY/Q10/MWSBIHAITOITHT/`.

**Bước 6 (tự động hóa Giai đoạn 2):**
- Apps Script chạy mỗi giờ: list file trong folder của từng căn → tự update cột `anh_1`...`anh_10` theo thứ tự file. Trang/anh Khang chỉ cần upload đúng tên file, không phải copy link tay nữa.

---

## 6. Workflow archive khi căn đã bán / tạm dừng

Khi `trang_thai` chuyển sang `Đã bán` hoặc `Tạm dừng`:

1. Di chuyển folder của căn từ `01_HINH_NHA/Q[X]/[id]/` → `99_ARCHIVE/01_HINH_NHA_archive/Q[X]/[id]/`.
2. Tương tự cho hình pháp lý: `02_HINH_PHAP_LY/Q[X]/[id]/` → `99_ARCHIVE/02_HINH_PHAP_LY_archive/Q[X]/[id]/`.
3. Cập nhật `link_folder_drive` và `link_hinh_phap_ly` trong Sheet Raw để trỏ về folder mới.
4. Sheet Public: ẩn dòng (filter `trang_thai = Đang bán` ở Apps Script sync rule), ảnh không bị xóa link nhưng không hiện trên web.

**Lý do archive thay vì xóa:** giữ history, có thể tham chiếu lại nếu căn mở bán lại hoặc cần báo cáo.

---

## 7. Quy ước đặc biệt

### 7.1 Trùng `id` (rất hiếm)
Nếu 2 căn ra cùng `id` (vd cùng số nhà cùng tên đường — không nên xảy ra với rule encode hiện tại), thêm hậu tố `-A`, `-B` vào folder: `MWSBIHAITOITHT-A`, `MWSBIHAITOITHT-B`. Note rõ trong `ghi_chu_noi_bo` của Sheet Raw.

### 7.2 Căn ở quận đặc biệt / huyện ngoại thành
Đặt tên folder theo Mục 2.1. Nếu là khu vực mới chưa có trong bảng, bổ sung vào file này trước khi tạo folder để giữ chuẩn.

### 7.3 Hình từ chủ gửi WhatsApp/Zalo (chất lượng kém)
Vẫn upload vào `01_HINH_NHA/Q[X]/[id]/` nhưng đặt tên có hậu tố `-low`: `01_mat-tien-low.jpg`. Khi có hình chất lượng cao, replace file (giữ nguyên tên) — Drive giữ version history.

---

## 8. Checklist cho anh Khang khi có căn mới

- [ ] Đã sinh `id` đúng theo Quy tắc đặt mã nhà (chèn W/U vị trí 2)?
- [ ] Đã tạo folder `01_HINH_NHA/Q[X]/[id]/`?
- [ ] Đã tạo folder `02_HINH_PHAP_LY/Q[X]/[id]/` nếu có hình sổ?
- [ ] Đã đổi tên file ảnh nhà theo `01_`, `02_`, ...?
- [ ] Đã upload và check folder `01_HINH_NHA/` có quyền "Anyone with link can view"?
- [ ] Đã KHÔNG vô tình share link folder pháp lý ra ngoài?
- [ ] Đã paste link vào cột `anh_1`...`anh_10` của Sheet Raw?
- [ ] Đã verify website hiện ảnh đúng (mở web khách thử)?
