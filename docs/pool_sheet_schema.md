# Pool Sheet Schema — Khang Ngô Nhà Phố

> Source of Truth cho sheet nội bộ Pool (Google Sheets)  
> Khác với sheet công khai dùng cho website (index.html)  
> Last updated: 2026-05-20

---

## Cấu trúc cột

| STT | Tên Header (chính xác) | Alias trong code | Dùng trong AI prompt | Ghi chú |
|---|---|---|---|---|
| 1 | `Mã Hàng` | — | ❌ | Mã định danh nội bộ |
| 2 | `Hình Nhận Diện` | — | ❌ | Ảnh nhận diện |
| 3 | `Tỉnh` | — | ❌ | Mặc định TP.HCM |
| 4 | `Quận` | `quan` | ✅ | Quận (3, 10, Phú Nhuận...) |
| 5 | `Phường` | `phuong` | ✅ | Phường (mới sau sáp nhập) |
| 6 | `Đường` | `duong` | ✅ | Tên đường |
| 7 | `Ngõ/Số nhà` | `soNha` | ✅ | Số nhà (ẩn trong tiêu đề, chỉ dùng để AI suy bán kính địa lý) |
| 8 | `Phân loại` | `phanLoai` | ✅ | Tag USP: Lô góc, Hiếm, Nội thất đẹp, Để ở... |
| 9 | `Năm xây dựng` | `namXay` | ❌ Bỏ qua | PO quyết định không dùng |
| 10 | `Nội dung chính` | ~~noiDungChinh~~ | ❌ Đã bỏ (US-013) | Raw data lộn xộn, gây hallucinate tên đường |
| 11 | `Mô tả chi tiết` | `moTaGoc` | ✅ | Điểm nổi bật USP từ môi giới/đầu chủ |
| 12 | `Giá chào` | `giaChao` | ⚠️ Chuẩn xác nhận | **Giá chính thức** (PO xác nhận). Cần check có khác `Giá Public` không |
| 13 | `Giá chốt` | — | ❌ | Giá chốt thực tế (nội bộ) |
| 14 | `DT Thực tế` | `dt` | ✅ | Diện tích thực (m2) |
| 15 | `DT Trên sổ` | `dtSo` | ✅ | Diện tích sổ (m2) |
| 16 | `Số Tầng` | `tang` | ✅ | Số tầng |
| 17 | `Mặt Tiền` | `ngang` | ✅ | Chiều ngang nhà (m) |
| 18 | `Hướng` | `huong` | ✅ | Hướng nhà (Đông Nam, Tây...) |
| 19 | `Tên Chủ Nhà` | — | ❌ | Thông tin cá nhân |
| 20 | `Điện thoại 1` | — | ❌ | Thông tin cá nhân |
| 21 | `Điện thoại 2` | — | ❌ | Thông tin cá nhân |
| 22 | `Loại Hợp đồng` | — | ❌ | Nội bộ |
| 23 | `Số ngày ký` | — | ❌ | Nội bộ |
| 24 | `Ngày bắt đầu` | — | ❌ | Nội bộ |
| 25 | `Ngày kết thúc` | — | ❌ | Nội bộ |
| 26 | `Người ký` | — | ❌ | Nội bộ |
| 27 | `Trạng thái` | — | ❌ | Nội bộ |
| 28-37 | `Sơ đồ thửa đất 1-2`, `Hình Mặt Tiền`, `Hình Hẻm 1-10` | — | ❌ | Ảnh nội bộ |
| 38-52 | `Ảnh 1–15` | — | ❌ | Ảnh sản phẩm |
| 53 | `Mã Khang Ngô (ID)` | — | ❌ | ID public |
| 54 | `Tiêu đề Public` | `tieuDeOut` | ✅ OUTPUT | AI ghi vào đây |
| 55 | `Mô tả Public` | `moTaOut` | ✅ OUTPUT | AI ghi vào đây |
| 56 | `Giá Public` | `gia` | ✅ | Giá hiển thị công khai |
| 57 | `Phân loại Hẻm` | `hem` | ✅ | Mặt tiền / Hẻm xe hơi / Hẻm 3 bánh... |
| 58 | `Đường trước nhà (m)` | `rongHem` | ✅ | Độ rộng đường trước nhà (m) |
| 59 | `Tình trạng nhà` | — | ⚠️ Chưa dùng | Mới / Cũ / Đang cho thuê...? (cần confirm) |
| 60 | `Ảnh Public (VD: 1,3,5)` | — | ❌ | Chọn ảnh public |
| 61 | `Ảnh Hẻm Public (VD: 1,2)` | — | ❌ | Chọn ảnh hẻm public |
| 62 | `Số phòng ngủ` | `phongNgu` | ✅ | Số phòng ngủ |
| 63 | `Số nhà vệ sinh` | `wc` | ✅ | Số WC |
| 64 | `Phường cũ (AI)` | `phuongCuOut` | ✅ OUTPUT | AI ghi vào đây |
| 65 | `Đánh giá (Admin)` | — | ❌ | Hàng Ngon / Hàng Lỗi (nội bộ) |
| 66 | `Ngủ trệt (Admin)` | — | ❌ | Có / Không (nội bộ) |
| 67 | `CHDV (Admin)` | — | ❌ | Có / Không (nội bộ) |
| 68 | `Duyệt Public` | — | ❌ | Nội bộ |
| 69 | `Trạng thái Public` | — | ❌ | Nội bộ |
| 70 | `System ID` | — | ❌ | Hệ thống |
| 71 | `Link Gốc` | — | ❌ | Nguồn crawl |
| 72 | `Điện thoại Đầu Chủ` | — | ❌ | Thông tin cá nhân |
| 73 | `Tên Đầu Chủ (Hợp đồng)` | — | ❌ | Thông tin cá nhân |
| 74 | `Điểm Facebook` | — | ❌ | Nội bộ |
| 75 | `Last Crawl` | — | ❌ | Hệ thống |
| 76 | `Last Sync` | — | ❌ | Hệ thống |
| 77 | `Phường Custom` | `custom_phuong` | ❌ | Cột ánh xạ nhanh từ cột thô Phường |
| 78 | `Hướng Custom` | `custom_huong` | ❌ | Cột ánh xạ nhanh từ cột thô Hướng |

---

## Mapping hiện tại trong pool_backend_v3.gs

```javascript
// INPUT — đọc từ sheet
soNha:      getIdx("Ngõ/Số nhà")
duong:      getIdx("Đường")
phuong:     getIdx("Phường")
quan:       getIdx("Quận")
dt:         getIdx("DT Thực tế")
dtSo:       getIdx("DT Trên sổ")
ngang:      getIdx("Mặt Tiền")
tang:       getIdx("Số Tầng")
gia:        getIdx("Giá Public")
phongNgu:   getIdx("Số phòng ngủ")
wc:         getIdx("Số nhà vệ sinh")
hem:        getIdx("Phân loại Hẻm")
rongHem:    getIdx("Đường trước nhà (m)")
huong:      getIdx("Hướng")
phanLoai:   getIdx("Phân loại")
moTaGoc:    getIdx("Mô tả chi tiết")

// OUTPUT — AI ghi vào
tieuDeOut:  getIdx("Tiêu đề Public")
moTaOut:    getIdx("Mô tả Public")
phuongCuOut: getIdx("Phường cũ (AI)")
```

---

## Các cột tiềm năng chưa dùng (cần PO quyết định)

| Cột | Ghi chú |
|---|---|
| `Giá chào` | **Giá chính thức** theo PO. Cần xác nhận có khác `Giá Public` không — nếu khác thì nên dùng `Giá chào` thay cho `Giá Public` trong prompt |
| `Năm xây dựng` | ❌ Đã quyết định bỏ qua |
| `Tình trạng nhà` | ❌ Đã quyết định bỏ qua |
