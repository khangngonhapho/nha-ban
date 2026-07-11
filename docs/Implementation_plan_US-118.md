# Implementation Plan - US-118: Tùy biến Diện tích Sổ & Diện tích Thực tế trên Sheet Source và Vercel Detail

Yêu cầu này bổ sung khả năng biên tập, tùy chỉnh diện tích thực tế (DT Thực tế) và diện tích sổ (DT Trên sổ) trên sheet Source. Dữ liệu mặc định kế thừa từ thông số gốc của Pool nhưng cho phép Admin điều chỉnh độc lập và lưu trữ đồng bộ trên Google Sheets, SQLite local, giao diện Biên tập (Vercel) và Canvas so sánh.

**Phương án điều chỉnh:** 
- Giữ nguyên ý nghĩa của cột F làm **DT Thực tế** (trùng khớp với thiết kế hiện tại của hệ thống), và thêm cột mới ở cuối làm **DT Trên sổ** (thứ tự này tương ứng với sheet Pool).
- **Lược bỏ việc cập nhật Curator Dashboard (`curator.html`)** theo mong muốn của người dùng (chỉ tập trung biên tập trên Web Vercel).
- **Vẫn cập nhật Canvas View (`canvas.html`)** để hỗ trợ đối chiếu thông tin diện tích thô và sạch.

**Đặc biệt:** 
1. Trên trang xem chi tiết dành cho Khách hàng (Vercel Client View), hệ thống sẽ hiển thị đồng thời cả **DT Trên sổ** và **DT Thực tế** lấy từ dữ liệu đã biên tập (Source), ẩn chữ "Custom" trên toàn bộ giao diện người dùng.
2. Công thức tính **Đơn giá (tr/m²)** (`giabq`) được tính toán bằng `(Giá bán * 1000) / DT Trên sổ`.

## User Review Required

> [!IMPORTANT]
> **Phương án bố trí cột trên Sheet Source để tối ưu độ an toàn, tránh lỗi lệch cột (Column Shift Bug):**
> - **Cột F (index 5 - `dien_tich`)**: Giữ nguyên ý nghĩa đại diện cho **DT Thực tế** (mặc định lấy giá trị `DT Thực tế` của Pool).
> - **Cột AV (index 47 - cột mới ở cuối sheet)**: Sẽ được thêm mới với tiêu đề **DT Trên sổ** (mặc định lấy giá trị `DT Trên sổ` của Pool).
>
> **Lý do chọn Column AV thay vì chèn vào cạnh cột F:**
> Nếu chèn cột mới ở vị trí G, toàn bộ 40+ cột phía sau trên Sheet Source sẽ bị dịch chuyển index. Việc đặt cột mới ở cuối bảng (AV) giúp bảo toàn 100% độ ổn định của hệ thống hiện tại.

> [!IMPORTANT]
> **Cập nhật công thức IMPORTRANGE trên tab Public:**
> Để website hiển thị được cột mới này, sau khi deploy, anh cần cập nhật lại công thức IMPORTRANGE ở cell A3 trên tab `Public` của Google Sheet thành:
> `=IMPORTRANGE("Source!D3:AV1000")` (thay vì `:AT1000` hoặc `:AU1000` cũ) để kéo được thêm dữ liệu của cột AV mới.

---

## Proposed Changes

### 1. Google Sheets & Apps Script Sync

#### [pool_backend_v3.gs](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_backend_v3.gs)
- Cập nhật hàm `onAdminReview` (Smart Merge từ Pool sang Source):
  - Ánh xạ cột F (index 5) nhận giá trị của cột `DT Thực tế` (Pool) làm mặc định cho **DT Thực tế** (giữ nguyên logic hiện tại).
  - Append thêm giá trị cột `DT Trên sổ` (Pool) vào cuối hàng dữ liệu làm mặc định cho **DT Trên sổ** (cột AV - index 47).
  - Khai báo thêm các cột ảnh mở rộng (`anh_11`..`anh_15`) và `JSON_UI` vào mảng `publicRowData` của Apps Script để hoàn thiện cấu trúc đồng bộ 48 cột, tránh lỗi bỏ sót cột khi Apps Script chạy sync lần đầu hoặc chép đè.
  - Đưa chỉ số cột `5` (DT Thực tế) và `47` (DT Trên sổ) vào danh sách bảo vệ `protectedIndices` để tránh bị đồng bộ đè khi chạy sync các lần tiếp theo.

---

### 2. SQLite Database & Python Backend

#### [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py)
- Cập nhật hàm `init_db`:
  - Khai báo thêm 2 cột mới `custom_dt_thuc_te TEXT DEFAULT ''` và `custom_dt_so TEXT DEFAULT ''` trong cấu trúc bảng `listings`.
  - Bổ sung logic tự động chạy lệnh `ALTER TABLE` nâng cấp cơ sở dữ liệu SQLite local nếu phát hiện bảng `listings` thiếu 2 cột này.

#### [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py)
- Cập nhật hàm `normalize_listing_for_client`:
  - Thêm ánh xạ `custom_dt_thuc_te` và `custom_dt_so` từ SQLite row sang JSON response để trả về cho client.
- Cập nhật endpoint `PUT /api/listings/<tk_id>`:
  - Thêm trường `custom_dt_thuc_te` và `custom_dt_so` vào từ điển `fields_to_update` để lưu cấu hình biên tập xuống SQLite.

---

### 3. Vercel Web Dashboard (Google Sheets Direct Access)

#### [static/js/lego_detail_admin.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_admin.js)
- Tại HTML Template của Panel **BIÊN TẬP** (Accordion `accSource`):
  - Thêm một hàng Grid gồm 2 ô nhập số (nhãn hiển thị là **DT Thực tế** trước, **DT Trên sổ** sau):
    - **DT Thực tế (m²)** (`#editDtThucTeCustom`): giá trị ban đầu lấy từ `p.dt` (Source) hoặc fallback về `p.raw_dt_thuc_te` (Pool).
    - **DT Trên sổ (m²)** (`#editDtSoCustom`): giá trị ban đầu lấy từ `p.dt_tren_so_custom` hoặc fallback về `p.raw_dt_tren_so` (Pool).
- Tại hàm `saveSourceChanges` (lưu cập nhật của căn đã có trên Source):
  - Đọc trị số từ 2 ô nhập trên.
  - Pad độ dài của mảng `p.original_row_data` lên ít nhất 48 phần tử để chứa cột mới.
  - Gán `p.original_row_data[5] = editDtThucTeCustom` và `p.original_row_data[47] = editDtSoCustom`.
  - Cập nhật biến client-side `p.dt = editDtThucTeCustom` và `p.dt_tren_so_custom = editDtSoCustom` để hiển thị đồng bộ ngay lập tức.
- Tại hàm `saveNewListingFromPool` (đồng bộ căn mới từ Pool lên Source):
  - Đọc trị số từ 2 ô nhập trên.
  - Cập nhật mảng `publicRowData` khi ghi mới lên sheet Source:
    - Vị trí index 5 nhận `editDtThucTeCustom` (giữ nguyên như thiết kế cũ).
    - Append thêm `editDtSoCustom` vào cuối mảng (index 47).
- Cập nhật phần tính toán đơn giá `giabq` khi nạp chi tiết căn hộ:
  - Tính toán bằng: `(Giá bán * 1000) / DT Trên sổ` (sử dụng `p.dt_tren_so_custom || p.raw_dt_tren_so`).

#### [static/js/lego_core.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_core.js)
- Tại luồng nạp dữ liệu `loadData()` (khi map dữ liệu thô từ Google Sheets sang object BĐS):
  - Đối với các căn đã có trên Source:
    - `p.dt` (DT Thực tế) = `sr[5]` (Column F).
    - `p.dt_tren_so_custom` = `sr[47]` (Column AV) (nếu có, fallback về `p.raw_dt_tren_so`).
    - Tính toán đơn giá `giabq` = `(gia * 1000) / p.dt_tren_so_custom`.
  - Đối với các căn chỉ mới có ở Pool (`isFromPoolOnly`):
    - `p.dt` = `poolRow[13]` (DT Thực tế).
    - `p.dt_tren_so_custom` = `poolRow[14]` (DT Trên sổ).
    - Tính toán đơn giá `giabq` = `(gia * 1000) / p.dt_tren_so_custom`.

#### [static/js/lego_detail_client.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_client.js)
- Tại phần render Diện tích trên giao diện chi tiết của Khách hàng (Vercel View Customer):
  - Thay thế trường "Diện tích" cũ thành 2 dòng hiển thị riêng biệt trong thông số kỹ thuật (bỏ chữ "Custom" trên nhãn):
    - **DT Trên sổ:** `${p.dt_tren_so_custom || p.raw_dt_tren_so || '-'} m²`
    - **DT Thực tế:** `${p.dt || p.raw_dt_thuc_te || '-'} m²`
  - Đảm bảo hiển thị Đơn giá `giabq` đã được chia cho **DT Trên sổ**.

#### [static/js/lego_helpers.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_helpers.js)
- Tại hàm mapping Pool rows `getMappedPoolData`:
  - Ưu tiên tính đơn giá `giabq` bằng cách chia cho `row[14]` (DT Trên sổ).

---

### 4. Canvas View

#### [canvas.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/canvas.html)
- Cập nhật khối so sánh 📐 diện tích đất:
  - Phân tách thành 2 dòng so sánh đối chiếu rõ ràng:
    - **Diện tích Thực tế (m2)**: so sánh `Pool (Thực tế)` vs `Source (Thực tế)`.
    - **Diện tích Trên sổ (m2)**: so sánh `Pool (Trên sổ)` vs `Source (Sổ)`.
- Cập nhật JavaScript map dữ liệu tương ứng.

---

## Verification Plan

### Automated Tests
- Chạy bộ kiểm thử Playwright E2E hiện có để đảm bảo không xảy ra lỗi gián đoạn giao diện (no regression):
  `powershell -Command "python -m pytest scratch/test_e2e_curation_save_changes.py"`
  `powershell -Command "python -m pytest scratch/test_e2e_filters.py"`

### Manual Verification
1. Mở Web Admin Vercel, chọn 1 căn thô chờ biên tập từ rổ Pool.
2. Kiểm tra phần **BIÊN TẬP**, xem 2 ô nhập diện tích mới đã mặc định hiển thị đúng Diện tích thực tế và Diện tích trên sổ chưa (Nhãn là **DT Thực tế** và **DT Trên sổ**).
3. Thay đổi số liệu ở 2 ô này, bấm **LÊN SÓNG**.
4. Kiểm tra Google Sheets tab Source để xác nhận:
   - Cột F lưu đúng giá trị DT Thực tế mới.
   - Cột AV lưu đúng giá trị DT Trên sổ mới.
5. Mở xem chi tiết căn nhà vừa lưu ở Client View, xác nhận:
   - Thông tin diện tích hiển thị rõ 2 dòng **DT Thực tế** và **DT Trên sổ** với giá trị tương ứng từ Source.
   - Đơn giá hiển thị được tính toán chính xác bằng `Giá bán / DT Trên sổ`.
6. Thử chỉnh sửa căn đã lên sóng và xác nhận dữ liệu được lưu đè chính xác trên Source.
7. Chạy Apps Script sync thủ công trên Google Sheets và kiểm tra không bị đồng bộ đè đè mất dữ liệu custom đã sửa.
