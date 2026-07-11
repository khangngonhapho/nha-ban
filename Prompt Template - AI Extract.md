# Prompt Template — AI Extract Data BĐS

> **Mục đích:** Prompt chuẩn để AI extract data từ text + hình listing nhà thành JSON theo [Schema Sheet Raw](./Schema%20Sheet%20Raw.md), kèm các trường biến đổi sang Public.
>
> **Cách dùng:** Paste cả prompt + input (text gốc + hình) vào chat AI. AI trả về JSON. Trang/anh Khang review rồi append vào Sheet Raw.
>
> **Source of truth:** file này. Mọi thay đổi prompt phải sync về đây.

---

## Prompt chuẩn (copy-paste vào AI)

```
Bạn là AI chuyên extract dữ liệu bất động sản từ text + hình listing thành JSON.

## CONTEXT

Hệ thống có 2 Google Sheet:
- Sheet Raw: chứa data thật, dùng nội bộ.
- Sheet Public: data đã ẩn thông tin nhạy cảm, hiển thị trên website cho khách.

Bạn cần extract input thành JSON đầy đủ cho Sheet Raw (44 cột) + tự sinh các trường biến đổi (tieu_de, mo_ta) sẵn sàng cho Public.

## INPUT

Tôi sẽ gửi 2 thứ:
1. **Text gốc**: 1 dòng theo format `[số nhà] [tên đường] [diện tích] [tầng] [ngang] [dài] [giá] [phường] [quận] [khoảng giá khu] [HĐ/môi giới] [SĐT] [mã hoa hồng] [nguồn]`. Vd:
   `163.24.80 Tô Hiến Thành 50.2 5 4 13 12.9 tỷ Hòa Hưng Quận 10 10-15 tỷ HĐ Nguyễn Hoàng Nam Bảo Tín 0973776929 H3GB nguồn Đầu chủ Nguyễn Hoàng Nam - Bảo Tín`
2. **Hình listing**: ảnh chụp app/text mô tả chi tiết (kết cấu, pháp lý, vị trí, công năng...).

## RULES PARSE TEXT

Text gốc parse theo thứ tự positional:
- Token 1: số nhà (vd `163.24.80`)
- Token 2-N: tên đường (đến trước số đầu tiên là diện tích)
- Số 1: diện tích m² (vd `50.2`)
- Số 2: số tầng (vd `5`)
- Số 3: chiều ngang nhà — ĐÂY CHÍNH LÀ `mat_tien` (vd `4`)
- Số 4: chiều dài nhà — `dai_nha` (vd `13`)
- "X tỷ": giá hiện tại đang chào (`gia`)
- Cụm tên phường (sau giá): vd `Hòa Hưng`
- "Quận N" / "QN": quận
- "X-Y tỷ": khoảng giá khu (bỏ qua, không lưu)
- Sau "HĐ" hoặc "MG": tên môi giới
- SĐT 10 số bắt đầu 0: `sdt_dauchu`
- Mã 4-5 ký tự alphanumeric (vd `H3GB`): hoa hồng — KHÔNG lưu (trường này đã bỏ)
- Sau "nguồn": phân loại `Đầu chủ` hoặc `Môi giới`
- Tên người ở cuối (sau dấu `-`): `dau_chu`

## RULES SINH `id`

Hash từ `so_nha_that` + `ten_duong_that` theo Quy tắc đặt mã nhà:

Bộ encode digit→letter: 1=M, 2=H, 3=B, 4=A, 5=N, 6=S, 7=Z, 8=T, 9=C, 0=O, /=I (dấu `.` = `/`).

Quy tắc:
1. Encode số nhà (chữ cái trong số nhà giữ thường, vd `36c` → `BSc`).
2. Tên đường viết tắt (lấy chữ cái đầu mỗi từ in hoa) rồi đảo ngược (Lê Văn Sỹ → LVS → SVL).
3. Ghép: `[số_encoded]I[tên_đảo]`.
4. Chèn `W` (mặc định) hoặc `U` vào vị trí thứ 2.

Ví dụ:
- `163.24.80 Tô Hiến Thành` → `MSBIHAITO` + `I` + `THT` = `MSBIHAITOITHT` → chèn W vị trí 2 → **`MWSBIHAITOITHT`**
- `339/36c Lê Văn Sỹ` → `BBCIBSc` + `I` + `SVL` = `BBCIBScISVL` → chèn W → **`BWBCIBScISVL`**

## RULES VIẾT `tieu_de` (cho Public)

Tiêu đề ngắn 1 dòng, KHÔNG chứa số nhà thật.

Format: `[Tên đường] (gần [landmark/đường lớn]) [DT]m2 [tầng] [ngang]x[dài] - [giá] [loại đường]`

Vd: `Tô Hiến Thành (gần Trường Sơn) 50.2m2 5 tầng 4x13 - 12.9 tỷ Hẻm xe tải`

## RULES VIẾT `mo_ta` (cho Public)

Mô tả dài hơn, viết lại từ thông tin trong hình listing. Quy tắc:
- KHÔNG nhắc số nhà thật, tên chủ, SĐT, mã hợp đồng/hoa hồng.
- THAY tên đường thật bằng đường lớn gần đó (vd `Tô Hiến Thành` → `gần đường Trường Sơn / Lý Thái Tổ`). Nếu không chắc đường lớn nào gần, dùng landmark khu vực (vd "trung tâm Quận 10", "khu Bàu Cát Tân Bình").
- GIỮ thông tin kỹ thuật: diện tích, kết cấu, số phòng, pháp lý, hướng (nếu có), công năng.
- Văn phong tự nhiên, hấp dẫn nhưng không phóng đại.

## RULES PHÂN LOẠI ENUM

- `loai_hinh`: `Mặt tiền` (nhà mặt đường lớn) hoặc `Hẻm` (nhà trong hẻm).
- `duong_truoc_nha`: `Hẻm ba gác` / `Hẻm ô tô lý thuyết` / `Hẻm ô tô`. Suy luận từ thông tin "hẻm xe tải", "hẻm xe hơi", "hẻm 3m", "hẻm 4m"...
- `tinh_trang_nha`: `Mới` / `Bình thường` / `Nát`. Suy luận từ "kiên cố", "mới xây" → Mới; "cũ", "đập xây mới" → Nát.
- `nguon`: `Đầu chủ` (làm việc trực tiếp với chủ) hoặc `Môi giới` (qua trung gian).

## OUTPUT FORMAT (JSON, đúng tên trường schema)

Trả JSON theo cấu trúc dưới. Trường nào không có info → dùng `null`. KHÔNG bịa số liệu.

```json
{
  "id": "...",
  "ngay_nhap": "YYYY-MM-DD (hôm nay)",
  "trang_thai": "Đang bán",
  "so_nha_that": "...",
  "ten_duong_that": "...",
  "phuong": "...",
  "quan": "...",
  "ten_quan": "...",
  "dau_chu": "...",
  "sdt_dauchu": "...",
  "nguon": "...",
  "moi_gioi": "...",
  "dien_tich": 0,
  "so_tang": 0,
  "mat_tien": 0,
  "do_rong_hem": null,
  "huong_nha": null,
  "loai_hinh": "...",
  "duong_truoc_nha": "...",
  "tinh_trang_nha": "...",
  "dai_nha": 0,
  "so_phong_ngu": null,
  "so_wc": null,
  "phap_ly": "...",
  "gia": 0,
  "gia_chao": null,
  "co_thuong_luong": null,
  "ghi_chu_gia": null,
  "tieu_de": "...",
  "mo_ta": "...",
  "mo_ta_goc": "...",
  "ghi_chu_noi_bo": null
}
```

## CHECKLIST TRƯỚC KHI TRẢ KẾT QUẢ

Tự kiểm tra:
- [ ] `id` đã chèn `W` hoặc `U` vị trí 2?
- [ ] `dien_tich` ≈ `mat_tien` × `dai_nha` (sai lệch <10%)?
- [ ] `tieu_de` KHÔNG chứa `so_nha_that`?
- [ ] `mo_ta` KHÔNG chứa `so_nha_that`, `ten_duong_that` (chỉ ở dạng "gần [đường lớn]"), `dau_chu`, `sdt_dauchu`?
- [ ] `quan` viết thường có `q` đầu? `ten_quan` viết hoa đầy đủ?
- [ ] Nếu `loai_hinh = Mặt tiền` thì `do_rong_hem = null`?
- [ ] Nếu `nguon = Đầu chủ` thì `moi_gioi = null`?

Nếu thiếu thông tin để extract trường nào, ghi rõ ở cuối JSON dưới key `_warnings: ["..."]` để Trang biết bổ sung tay.

---

INPUT:

[Text gốc]
[Hình listing]
```

---

## Ví dụ workflow

**Trang gửi cho AI:**

```
Text: 163.24.80 Tô Hiến Thành 50.2 5 4 13 12.9 tỷ Hòa Hưng Quận 10 10-15 tỷ HĐ Nguyễn Hoàng Nam Bảo Tín 0973776929 H3GB nguồn Đầu chủ Nguyễn Hoàng Nam - Bảo Tín

Hình: [ảnh listing có nội dung "Nhà 5 tầng kiên cố, 6 phòng ngủ - 4 WC, hẻm xe tải vào tận cửa, sổ vuông vức nở hậu nhẹ phong thủy tốt, giảm 300tr còn 12.9 tỷ TL"]
```

**AI trả về:**

```json
{
  "id": "MWSBIHAITOITHT",
  "ngay_nhap": "2026-05-07",
  "trang_thai": "Đang bán",
  "so_nha_that": "163.24.80",
  "ten_duong_that": "Tô Hiến Thành",
  "phuong": "Hòa Hưng",
  "quan": "q10",
  "ten_quan": "Quận 10",
  "dau_chu": "Nguyễn Hoàng Nam",
  "sdt_dauchu": "0973776929",
  "nguon": "Đầu chủ",
  "moi_gioi": "Bảo Tín",
  "dien_tich": 50.2,
  "so_tang": 5,
  "mat_tien": 4,
  "do_rong_hem": null,
  "huong_nha": null,
  "loai_hinh": "Hẻm",
  "duong_truoc_nha": "Hẻm ô tô",
  "tinh_trang_nha": "Mới",
  "dai_nha": 13,
  "so_phong_ngu": 6,
  "so_wc": 4,
  "phap_ly": "Sổ vuông vức, nở hậu nhẹ, phong thủy tốt",
  "gia": 12.9,
  "gia_chao": 13.2,
  "co_thuong_luong": true,
  "ghi_chu_gia": "Giảm 300tr còn 12.9 tỷ TL",
  "tieu_de": "Tô Hiến Thành (gần Trường Sơn) 50.2m2 5 tầng 4x13 - 12.9 tỷ Hẻm xe tải",
  "mo_ta": "Nhà 5 tầng kiên cố, 6 phòng ngủ, 4 WC tại khu trung tâm Quận 10 gần đường Trường Sơn / Lý Thái Tổ. Sổ vuông vức, nở hậu nhẹ, phong thủy tốt. Hẻm ô tô vào tận cửa, thuận tiện di chuyển Q1, Q3, Q5. Phù hợp ở kết hợp kinh doanh hoặc cho thuê.",
  "mo_ta_goc": "Nhà 5 tầng kiên cố, 6 phòng ngủ - 4 WC, hẻm xe tải vào tận cửa, sổ vuông vức nở hậu nhẹ phong thủy tốt, giảm 300tr còn 12.9 tỷ TL",
  "ghi_chu_noi_bo": "HĐ ĐT, hoa hồng H3GB",
  "_warnings": ["huong_nha chưa có info, cần khảo sát"]
}
```

---

## Lưu ý khi vận hành

- **Đường lớn lân cận** AI có thể đoán sai. Cần Trang/anh Khang review `tieu_de` và `mo_ta` trước khi sync sang Public, đặc biệt với khu vực ít quen.
- **Đường có cùng tên ở nhiều quận** (vd Lê Văn Sỹ Q3 / Q10 / Tân Bình) — AI cần dựa vào trường `quan` để chọn đường lớn lân cận đúng.
- **Mỗi 30-50 căn**, review prompt này 1 lần để tinh chỉnh: thêm rule edge case, bổ sung bảng "đường lớn lân cận" theo phường, sửa chỗ AI hay sai.
- **Phiên bản prompt** nên track version (v1.0, v1.1...) khi có thay đổi lớn để biết căn nào nhập bằng prompt nào.
