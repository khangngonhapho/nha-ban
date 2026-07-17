---
id: US-151
status: accepted
date: 2026-07-17
size: S
---

# US-151: Tự động dò tìm dòng header và vị trí cột trên sheet Source khi đồng bộ

## User story
**As an** Admin
**I want** hệ thống tự động dò tìm dòng header và vị trí các cột (`System ID`, `id`, `Hình_mat_tien`...) trên sheet `Source` tại runtime
**So that** đồng bộ chính xác dữ liệu căn nhà lên sóng vào đúng dòng cuối cùng (khi chèn mới) hoặc đúng dòng cũ khớp `System ID` (khi cập nhật), tránh hoàn toàn việc ghi đè sai lệch dữ liệu lên dòng 1 của sheet `Source`.

## Acceptance
- [x] **Dò tìm Header động (Apps Script):** Quét qua các dòng đầu của sheet `Source` để tự động xác định dòng chứa tiêu đề (ví dụ dòng 2 hoặc dòng 3) thay vì mặc định là dòng 1.
- [x] **Tìm cột động (Apps Script):** Tìm kiếm vị trí cột bằng tên (như `"System ID"`, `"id"`, `"Hình_mat_tien"`) để lấy index cột động thay vì hardcode cột 38 hay cột 4.
- [x] **Đổi cột số sang chữ cái động:** Hàm sinh công thức hiển thị hình ảnh `=IMAGE(cột_gốc + dòng)` tự động đổi chỉ số cột động thành chữ cái (ví dụ cột 39 thành `AM`) thay vì hardcode chữ `AM`.
- [x] **Đồng bộ logic Python:** Cập nhật hàm `publish_listing()` trong `pool_lego.py` để quét tìm dòng header và cột ID bên `Source` động tại runtime tương tự.
- [x] **Giữ nguyên định dạng và dữ liệu dòng 1:** Đảm bảo khi lên sóng một căn nhà mới, dữ liệu dòng 1 không bị ghi đè và tin đăng được ghi chính xác vào dòng trống tiếp theo ở cuối bảng.

## Logic hiện tại liên quan
- **DF-001 Luồng Dữ Liệu Biên Tập & Xuất Bản v4**: Khi xuất bản tin (Publish) từ Web UI, hệ thống gọi `publish_listing()` ghi dữ liệu lên sheet Pool, đồng thời đồng bộ Mã Khang Ngô sang cột `id` của sheet Source.
- **DF-002 Luồng Dữ Liệu Đồng Bộ & Khôi Phục v7**: Quy định về dọn dẹp các ký tự bắt đầu công thức Google Sheets (`+`, `-`, `=`) và đồng bộ ảnh.
- Yêu cầu này **XÁC NHẬN VÀ BỔ SUNG** logic trên vì nó cải tiến tính bền vững cho việc đồng bộ bằng cách động hóa hoàn toàn các thao tác tìm hàng/cột trên sheet Source (cả ở Apps Script và Python) để tránh lỗi ghi đè sai dòng.

## Solution

### Configuration
Không thay đổi cấu hình môi trường.

### Input
Không thay đổi schema đầu vào.

### Output / Format
Không thay đổi định dạng đầu ra.

### Key logic
- **Tự động quét tìm dòng Header trên Source (Apps Script & Python):**
  Quét qua 10 hàng đầu tiên của sheet `Source` và kiểm tra sự xuất hiện của từ khóa `"System ID"`, `"id"` hoặc `"Cu_phap"`. Hàng đầu tiên khớp sẽ được coi là hàng header chính thức (`headerRowIdx`).
- **Động hóa tìm cột (Dynamic Column Resolution):**
  Sử dụng `headers.indexOf("Tên Cột")` tại runtime để giải quyết chỉ số cột của các trường cần cập nhật (như `System ID`, `id`, `Hình_mat_tien`, `Đăng BDS`, `Hình Mặt Tiền`).
- **Chuyển đổi số cột sang chữ cái (Apps Script):**
  Xây dựng hàm `getColumnLetter(colNum)` trong Apps Script để tự động chuyển chỉ số cột thành ký tự chữ cái (ví dụ: 39 thành `AM`), phục vụ cho việc ghi công thức hiển thị hình ảnh động `=IMAGE(Letter + row)`.

## 📋 Implementation Plan

### Google Apps Script Layer
#### [MODIFY] [pool_backend_v3.gs](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_backend_v3.gs)
We will modify three synchronization functions to dynamically detect the header row index and column indices on the `Source` sheet.
1. **`onAdminReview(e)`**:
   - Dynamically search for the header row index by scanning the first 10 rows for columns like `"System ID"`, `"id"`, or `"Cu_phap"`.
   - Resolve column indices dynamically for `"System ID"`, `"Hình_mat_tien"`, `"Hình Mặt Tiền"`, and `"Đăng BDS"`.
   - Implement `getColumnLetter(colNum)` to resolve the column letter dynamically for formula assignment.
   - Start the system ID scan from the row immediately following the header row.
2. **`batchSyncTitleToSource()`**:
   - Dynamically locate the header row.
   - Dynamically resolve the column index for `"System ID"` and `"tieu_de"`.
3. **`syncSystemIdToSource()`**:
   - Dynamically locate the header row.
   - Dynamically resolve the column index for `"id"` and `"System ID"`.

### Python Backend Layer
#### [MODIFY] [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py)
We will update the sheet `Source` sync logic inside `publish_listing()` to dynamically resolve row and column indices.
- Dynamically scan `source_values` to locate the header row index containing `"System_ID"`, `"id"`, or `"Cu_phap"`.
- Resolve the column index for `"System_ID"` and `"id"`.
- Scan for the matching `system_id` starting from the first data row (`header_row_idx + 1`).
- Write the new `Ma_Khang_Ngo_ID` to the dynamically resolved row and column.

## 📝 Task Checklist
- [x] **Khảo sát & Thiết kế:** [x] Khảo sát code cũ | [x] Chốt giải pháp dynamic row/column resolution
- [x] **Triển khai Code:** [x] Code logic Apps Script pool_backend_v3.gs | [x] Code logic Python pool_lego.py
- [x] **Kiểm thử & Đóng gói:** [x] Chạy unit tests | [x] Test manual trên sheet Staging | [x] Merge và cập nhật US-151 sang Done

## 🛠️ Update Logic (Drafting while Doing)

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:** 
  - Trong Apps Script, việc lấy index của mảng JS trả về chỉ số bắt đầu từ 0, nhưng Google Sheet API sử dụng index bắt đầu từ 1. Khi setRange hoặc getRange, cần cộng thêm 1 cho đúng chỉ số cột, và cộng startDataRow cho chỉ số dòng.
  - Xây dựng helper `getColumnLetter(columnNumber)` giúp chuyển đổi linh hoạt index cột sang các cột Excel chữ cái (như A, AM, AO) để ghi công thức hình ảnh một cách tự nhiên.
- **Phát kiến ngoài kế hoạch / Điểm tối ưu phát hiện khi code:** 
  - Quét tối đa 10 dòng đầu để tìm header là đủ an toàn, vừa đảm bảo tốc độ tối ưu vừa tránh bỏ sót nếu sheet bị chèn vài dòng rỗng hoặc dòng chú thích nhỏ.

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- **Script kiểm thử thô / nháp đã chạy:** `tests/test_source_sync.py`
- **Output kết quả nháp & Điểm nghẽn đã vượt qua:** 
  ```
  tests\test_source_sync.py ..                                             [100%]
  ============================== 2 passed in 0.27s ==============================
  ```
  Test case kiểm chứng thành công logic cũ bị hụt/lỗi khi cột bị dịch chuyển, trong khi logic mới nhận diện chính xác 100%.

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** Lỗi chèn đè lên dòng 1 của sheet Source do logic cũ tự động mặc định dòng header là dòng 1 và dữ liệu bắt đầu từ dòng 2, đồng thời hardcode cột System ID ở 38. Khi sheet có dòng trống hoặc thay đổi cấu trúc cột, logic này bị phá vỡ hoàn toàn.
- **Nguyên nhân gốc rễ (Root Cause):** Sự thiếu đồng bộ động giữa cấu trúc bảng thực tế trên Google Sheets (do người dùng chỉnh sửa) và logic mã nguồn.
- **Giải pháp phòng ngừa:** Luôn áp dụng Rule 6 của `AGENTS.md` (không hardcode index cột/dòng Google Sheets) và tự động dò tìm header tại runtime.

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm code & Cấu hình:** Viết các helper chuyển đổi số cột sang chữ cái Excel/Sheets giúp tối ưu hóa việc tạo công thức động.

## Verification Plan

### Automated Tests
- Chạy toàn bộ bộ unit test đảm bảo không có regression:
  ```bash
  pytest
  ```
  Kết quả thực tế: 135/135 tests passed.

### Manual Verification
1. Triển khai code thay đổi lên local/staging.
2. Sao chép và cập nhật code Apps Script trên sheet Pool bằng nội dung mới của `pool_backend_v3.gs`.
3. Bấm "Lên sóng" cho một căn nhà mới từ Curator UI hoặc tích chọn "Duyệt Public" trực tiếp từ sheet Pool.
4. Đảm bảo căn nhà được thêm chính xác vào dòng trống tiếp theo (dòng 5) của sheet `Source`, và dòng 1 được bảo vệ nguyên vẹn.

## Files touched
- `pool_backend_v3.gs` — [Apps Script đồng bộ dữ liệu]
- `pool_lego.py` — [Python backend điều phối xuất bản]
- `tests/test_source_sync.py` — [Unit test logic đồng bộ]
- `static/js/lego_core.js` — [JS cốt lõi load dữ liệu và preview]
- `static/js/lego_detail_admin.js` — [JS admin render và preview iframe]

## Truth Cards bị ảnh hưởng
- **DF-001 v5**: Bổ sung cơ chế truyền và đọc token trong iframe Preview Khách hàng để load trực tiếp từ sheet Source qua Secure mode.
- **SF-001 v3**: Bổ sung chi tiết về luồng Preview an toàn qua Google OAuth Token.

