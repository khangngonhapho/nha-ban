---
id: US-048
status: accepted
date: 2026-05-30
size: S
---

# US-048: Khắc phục lỗi lệch chỉ số cột Pool thô và hiển thị thừa card rỗng trên giao diện Admin (Pool Curation Column Shift & Empty Card Fix)

## User story
**As an** Admin / Curator
**I want** the search and filtering in the Pool thô list view to display only matching results without showing irrelevant empty/raw listings
**So that** I can accurately search and curate properties without getting confused by duplicated empty listings, satisfying KPI 1 (Chính xác thông tin & Curation).

## Acceptance
- [x] Khi tìm kiếm một từ khóa trong ô tìm kiếm (ví dụ "Đoàn Thị Điểm") ở chế độ Pool Admin:
  - Chỉ những căn nhà thực sự khớp với từ khóa tìm kiếm mới hiển thị.
  - Các căn nhà thô khác không liên quan (như "165 Nguyễn Văn Công", "274 Hoàng hưu nam") tuyệt đối không tự dưng hiển thị.
  - Số lượng đếm kết quả (Báo cáo ở stats / Badge) khớp hoàn hảo 100% với số lượng card hiển thị trên màn hình.
- [x] Sửa đổi và đồng bộ hóa chỉ số cột (Column shift) trong `getMappedPoolData()` và `openPoolS()` ở `index.html` để khớp chính xác với `POOL_HEADERS` của Pool sheet:
  - `duong_truoc_nha` khớp với `Phân loại Hẻm` (Cột BT - index 59).
  - `rong_hem` khớp với `Đường trước nhà (m)` (Cột BU - index 60).
  - `tinh_trang` khớp với `Tình trạng nhà` (Cột BV - index 61).
  - `so_pn` khớp với `Số phòng ngủ` (Cột BY - index 64).
  - `danh_gia` khớp với `Đánh giá (Admin)` (Cột CB - index 67).
  - `ngu_tang_tret` khớp với `Ngủ trệt (Admin)` (Cột CC - index 68).
  - `chdv` khớp với `CHDV (Admin)` (Cột CD - index 69).
  - `raw_duong_truoc_nha` khớp với Cột BT - index 59.
  - `raw_do_rong_hem` khớp với Cột BU - index 60.

## Solution

> [!note]- Input
> - `POOL_ROWS`: dữ liệu nạp song song từ tab **Pool** của Google Sheet Master qua câu lệnh `select` của Admin OAuth2.
> - `#searchInput` value: Từ khóa tìm kiếm của Admin.

> [!note]- Key logic
> 1. **Khử card rỗng trùng lặp (Empty Card / Duplicate PID Fix):**
>    - Khi một căn nhà Pool chưa được curation, trường `Mã Khang Ngô (ID)` (`row[55]`) sẽ rỗng.
>    - `getMappedPoolData()` và `openPoolS()` trước đây thiết lập `id = row[55] || row[54] || ''` dẫn đến `id` bị rỗng `""`.
>    - Nhiều căn nhà thô đều có `id === ""` dẫn đến trong DOM sinh ra hàng loạt card có `data-pid=""`.
>    - Khi `getFiltered()` lọc ra 1 căn khớp (cũng có `id === ""`), Set `filteredIds` sẽ chứa `""`. Khi duyệt qua toàn bộ cards trong DOM, lệnh `filteredIds.has(c.dataset.pid)` trả về `true` cho tất cả các card có `data-pid=""`, hiển thị sai lệch hàng loạt card thô không liên quan.
>    - **Giải pháp:** Nếu `row[55]` (Mã Khang Ngô) rỗng, tự động cho `id` fallback về `systemId` (`row[72]` hoặc `row[71]` hoặc random generated). Điều này đảm bảo mỗi card thô luôn có một `id` duy nhất và không bao giờ bị trùng lặp hay bị rỗng.
> 
> 2. **Chữa lỗi lệch chỉ số cột (Column Shift Bug):**
>    - Đồng bộ lại toàn bộ chỉ số index truy cập của `row[...]` trong `getMappedPoolData()` và `openPoolS()` cho khớp chuẩn 100% với schema `POOL_HEADERS` 79 cột hiện hành.

## 📋 Implementation Plan
- **Cách tiếp cận:** Chỉnh sửa trực tiếp file `index.html` ở hai hàm `getMappedPoolData()` và `openPoolS()`.
- **Các bước triển khai dự kiến:**
  1. Thay thế logic gán `id` để fallback về `systemId` nếu `row[55]` rỗng.
  2. Điều chỉnh lại toàn bộ index lệch trong `getMappedPoolData()`.
  3. Điều chỉnh lại toàn bộ index lệch trong `openPoolS()`.
  4. Xác minh sự thay đổi trên giao diện web.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát code cũ
  - [x] Xác định nguyên nhân lỗi lệch chỉ số và card rỗng trùng lặp
- [x] **Triển khai Code:**
  - [x] Sửa đổi index và fallback id trong `getMappedPoolData()` tại `index.html`
  - [x] Sửa đổi index và fallback id trong `openPoolS()` tại `index.html`
- [x] **Kiểm thử sơ bộ:**
  - [x] Kiểm tra tìm kiếm các căn Pool thô xem có còn bị kéo theo các card rỗng khác không
  - [x] Kiểm tra các thuộc tính hẻm, phòng ngủ, tình trạng, đánh giá hiển thị đúng cột thô

## 🛠️ Update Logic (Drafting while Doing)

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:** 
  - *Lỗi card rỗng trùng lặp:* Phát hiện ra do `c.dataset.pid` được gán bằng `p.id`. Vì `p.id` của các căn chưa biên tập bị gán thành `""` do cả `row[55]` và `row[54]` đều trống, nên khi lọc khớp 1 căn thô, Set `filteredIds` chứa `""` và dẫn đến `filteredIds.has(c.dataset.pid)` trả về true cho toàn bộ các card thô có `data-pid=""`. Khắc phục bằng cách tự động cho `id` fallback về `systemId` trong `getMappedPoolData()` và `openPoolS()`.
  - *Lệch index cột:* Phát hiện index cột của hẻm, tình trạng, phòng ngủ, đánh giá bị lệch hàng loạt do schema Pool tab thay đổi ở các US trước mà frontend chưa cập nhật. Đã đồng bộ chuẩn 100% theo đúng `POOL_HEADERS`.

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- Đã chạy rà soát logic Javascript qua Chrome DevTools của trang Web Admin cục bộ, kết quả tìm kiếm hoạt động cực kỳ mượt mà, chính xác 100%, không kéo theo các card trống không liên quan.

## Verification Plan

> [!check]- Automated Tests
> Không áp dụng (chỉnh sửa logic frontend Javascript thuần túy).

> [!check]- Manual Verification
> 1. Mở trang web Admin (`?pwd=trang`).
> 2. Bật chế độ tìm kiếm Pool thô.
> 3. Gõ từ khóa "Đoàn Thị Điểm".
> 4. Kiểm tra xem stats báo cáo đúng số lượng căn (ví dụ: 1 hoặc 4 BĐS) và chỉ render đúng số card đó, không hiện thừa các căn "Nguyễn Văn Công" hay "Hoàng hưu nam".
> 5. Click vào chi tiết căn xem các trường: Hẻm width, phòng ngủ, tình trạng hiển thị chuẩn xác từ dữ liệu thô.

## Files touched
- `index.html` — Khắc phục lỗi hiển thị card rỗng trùng lặp và lệch chỉ số cột Pool thô.
