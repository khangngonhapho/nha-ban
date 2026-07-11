---
id: US-076
status: accepted
date: 2026-06-07
size: M
---

# US-076: Nâng cấp bộ lọc thông số chi tiết nâng cao

## User story
**As an** Admin (Anh Khang Ngô)
**I want** bộ lọc chi tiết hiển thị đầy đủ 6 thông số: Khoảng giá, Diện tích sổ, Diện tích thực tế, Ngang (mặt tiền), Rộng hẻm, Số phòng ngủ với layout ô nhập "Từ/Đến" có nhãn và đơn vị rõ ràng.
**So that** dễ dàng lọc nhanh các căn nhà phù hợp với yêu cầu cụ thể của từng khách hàng từ kho rổ hàng.

## Acceptance
- [x] Hiển thị đầy đủ 6 nhóm lọc khoảng:
  - Khoảng giá (tỷ)
  - Diện tích sổ (m²)
  - Diện tích thực tế (m²)
  - Ngang (mặt tiền) (m)
  - Rộng hẻm (m)
  - Số phòng ngủ (phòng)
- [x] Bố trí layout 2 cột song song cho "Từ" và "Đến" với nhãn phụ "Từ" và "Đến" ở phía trên mỗi ô nhập. (Được thay thế bởi phong cách gọn hơn ở US-076.3)
- [x] Hiển thị đơn vị tương ứng bên phải bên trong ô nhập: "tỷ" cho khoảng giá, "m²" cho diện tích, "m" cho ngang/hẻm. (Được thay thế bởi phong cách gọn hơn ở US-076.3)
- [x] Lọc chính xác theo các khoảng giá trị nhập vào trên cả Client và Admin View (Kho Pool).
- [x] Nút "Xóa điều kiện" / "↺ Xóa lọc" sẽ xóa sạch các giá trị trong các ô nhập này.
- [x] Đồng bộ lưu trữ và phục hồi bộ lọc nâng cao từ `localStorage` qua `saveState` và `restoreState`.
- [x] **[US-076.2]** Hỗ trợ tìm kiếm số nhà bằng tiếp đầu ngữ (prefix matching): Ví dụ gõ "100.8" sẽ tìm ra nhà số "100.85b".
- [x] **[US-076.3]** Thiết kế bộ lọc nâng cao dạng thẻ card bo viền tròn, chứa lưới grid 2 cột cân xứng. Mỗi bộ lọc hiển thị gọn gàng trên 1 dòng bao gồm nhãn kèm emoji, ô nhập Từ/Đến có gạch dưới dashed mờ và đơn vị đo màu đỏ đất trầm ấm bên phải.

## Solution

### 1. Cấu trúc HTML Bộ Lọc Nâng Cao Mới
*   Các trường lọc được nhóm lại trong các thẻ `.detailed-spec-group` để CSS Grid trên desktop hoạt động ổn định.
*   Bố trí mỗi trường bao gồm nhãn chính, nhãn phụ "Từ"/"Đến" và ô nhập tương ứng có gắn nhãn đơn vị `.unit`.

```html
<div class="detailed-specs-card">
  <div class="detailed-specs-grid">
    <div class="spec-item">
      <span class="spec-label">🏠 Thực tế:</span>
      <div class="spec-value-group">
        <input type="number" id="filterDtThucTeMin" placeholder="..." class="inline-input" oninput="onSearchInput()">
        <span class="spec-sep">–</span>
        <input type="number" id="filterDtThucTeMax" placeholder="..." class="inline-input" oninput="onSearchInput()">
        <span class="spec-unit">m²</span>
      </div>
    </div>
  </div>
</div>
```

*   Định dạng inline card và dashed inputs:
```css
    .detailed-specs-card {
      background: #ffffff;
      border: 1.5px solid #e2ded6;
      border-radius: 16px;
      padding: 12px 14px;
      margin: 5px 0 10px;
    }
    .detailed-specs-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }
    @media (min-width: 576px) {
      .detailed-specs-grid {
        grid-template-columns: 1fr 1fr;
        column-gap: 24px;
        row-gap: 14px;
      }
    }
    .spec-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .inline-input {
      border: none;
      border-bottom: 1.5px dashed #a1a1a6;
      text-align: center;
      width: 42px;
    }
    .spec-unit {
      font-size: 12px;
      color: #c0392b;
      font-weight: 700;
    }
```

### 3. Logic Lọc Dữ Liệu (`getFiltered`) và Ưu tiên Dữ liệu Pool
*   **Quy tắc ưu tiên dữ liệu:** Khi thực hiện lọc khoảng, hệ thống sẽ ưu tiên so khớp với dữ liệu gốc cào thô từ **Pool** (nếu có). Chỉ khi dữ liệu trong Pool bị trống hoặc listing không khớp dòng Pool thì mới lấy dữ liệu curated trong **Source** làm fallback.
*   **Bổ sung mapping ở `loadData()`:** Bổ sung trường `p.raw_dt_thuc_te = poolRow[13] || '';` khi map dữ liệu từ Source khớp Pool để đảm bảo có diện tích thực tế thô.
*   Cách lấy giá trị so sánh trong bộ lọc:
    - **Giá:** Ưu tiên `p.raw_gia_chao`, fallback `p.gia`.
    - **Diện tích sổ:** Ưu tiên `p.raw_dt_tren_so`, fallback `p.dt`.
    - **Diện tích thực tế:** Ưu tiên `p.raw_dt_thuc_te`, fallback `p.dt`.
    - **Ngang (mặt tiền):** Ưu tiên `p.raw_mat_tien`, fallback `p.mat`.
    - **Rộng hẻm:** Ưu tiên `p.raw_duong_truoc_nha`, fallback `p.rong_hem`.
    - **Phòng ngủ:** Ưu tiên `p.raw_so_pn`, fallback `p.so_pn`.

```javascript
// Trích đoạn logic lọc ưu tiên
let val = parseFloat(p.raw_dt_thuc_te);
if (isNaN(val) || val === 0) {
  val = parseFloat(p.dt) || 0;
}
```

### 4. Đồng bộ & Reset Trạng Thái
*   `resetFilters()`: Xóa sạch 12 input IDs mới.
*   `saveState()` & `restoreState()`: Lưu trữ thêm đối tượng `adv` chứa 12 giá trị min/max này vào `localStorage` của Admin.

### 5. [US-076.2] Tìm kiếm số nhà bằng tiếp đầu ngữ (Prefix Matching)
* Thay thế logic phức tạp cũ của hàm `matchHouseNumber` bằng lệnh so sánh `.startsWith()` để hỗ trợ gõ prefix ra đầy đủ số nhà phức tạp:
```javascript
if (normalizedRaw.startsWith(cleanQuery)) return true;
```

## 📋 Implementation Plan

- **Các bước triển khai:**
  1. Thay thế cấu trúc cũ trong `.detailed-specs-container` ở [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html) bằng 6 trường mới dạng cấu trúc cột và nhãn đơn vị.
  2. Bổ sung các class CSS `.range-label`, `.range-col` và cập nhật `.range-box .unit` trong `<style>` ở [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html).
  3. Bổ sung ánh xạ `p.raw_dt_thuc_te` khi tải dữ liệu trong hàm `loadData()`.
  4. Cập nhật hàm `getFiltered()` để thực hiện so sánh 6 trường tương ứng, áp dụng logic ưu tiên dữ liệu từ Pool trước Source sau.
  5. Cập nhật danh sách xóa lọc `advInputs` trong hàm `resetFilters()`.
  6. Nâng cấp `saveState()` và `restoreState()` để bảo toàn cấu hình lọc chi tiết nâng cao khi tải lại trang.

## 📝 Task Checklist (TODO)

- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát lại giao diện và CSS của bộ lọc chi tiết cũ.
  - [x] Thống nhất danh sách 12 id input và ánh xạ thuộc tính trong Object dữ liệu.
- [x] **Triển khai Code:**
  - [x] Cập nhật HTML cấu trúc bộ lọc chi tiết mới trong [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html).
  - [x] Cập nhật CSS định dạng nhãn và đơn vị trong [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html).
  - [x] Cập nhật logic Javascript lọc trong `getFiltered()`.
  - [x] Cập nhật logic reset, saveState & restoreState.
- [x] **Kiểm thử & Nghiệm thu:**
  - [x] Kiểm tra hiển thị giao diện trên Mobile và Laptop (Grid 2 cột).
  - [x] Kiểm tra lọc chính xác từng trường hợp min/max độc lập và kết hợp.
  - [x] Kiểm tra tính năng Reset và phục hồi State sau khi tải lại trang.
- [x] **[US-076.2] Tìm kiếm số nhà tiếp đầu ngữ:**
  - [x] Đơn giản hóa logic `matchHouseNumber` trong `index.html` sử dụng `.startsWith()`.
  - [x] Kiểm thử tìm kiếm số nhà "100.8" khớp "100.85b".
- [x] **[US-076.3] Giao diện bộ lọc inline dashed và card:**
  - [x] Thay thế cấu trúc cũ bằng thẻ `.detailed-specs-card` và lưới `.detailed-specs-grid` 2 cột.
  - [x] CSS định vị nhãn, đơn vị đo màu đỏ đất trầm ấm và gạch dưới dashed cho ô nhập số.
  - [x] Tối ưu hóa độ rộng và căn chỉnh khoảng trống trên thiết bị Mobile/Laptop.

## 🛠️ Update Logic (Drafting while Doing)
- Đã cập nhật 6 bộ lọc Từ/Đến (12 inputs) trong `index.html`.
- Định vị đơn vị `.unit` bên phải, nhãn `.range-label` bên trên.
- Sử dụng grid layout linh hoạt trên desktop và cột co giãn trên mobile.
- Đã cấu hình logic ưu tiên Pool so với Source cho cả 6 bộ lọc khoảng.
- Xác nhận lưu trạng thái và phục hồi từ `localStorage` thông qua `adminState.adv`.
- Nút reset `resetFilters()` đã xóa sạch 12 inputs của bộ lọc chi tiết.

## Verification Plan

### Manual Verification
1. **Kiểm thử hiển thị giao diện:**
   - Mở bộ lọc, kiểm tra xem có đủ 6 trường: Khoảng giá, Diện tích sổ, Diện tích thực tế, Ngang (mặt tiền), Rộng hẻm, Số phòng ngủ.
   - Kiểm tra xem chữ "Từ", "Đến" có căn lề đúng phía trên từng ô nhập tương ứng không.
   - Kiểm tra các đơn vị "tỷ", "m²", "m" có nằm ở góc phải của ô nhập không.
2. **Kiểm thử tính năng lọc:**
   - Nhập "Khoảng giá" Từ 10 Đến 15 -> Kiểm tra xem danh sách có chỉ hiển thị căn có giá từ 10 đến 15 tỷ không.
   - Nhập "Diện tích sổ" Từ 50 -> Kiểm tra xem chỉ có các căn có DT trên sổ >= 50m² hiển thị.
   - Nhập "Ngang (mặt tiền)" Từ 4 -> Kiểm tra xem chiều ngang >= 4m.
   - Nhập "Rộng hẻm" Từ 4 -> Chỉ hiển thị hẻm rộng >= 4m.
3. **Kiểm thử Reset & Auto-save State:**
   - Nhập một số thông số lọc nâng cao -> F5 tải lại trang -> Kiểm tra xem các thông số có tự phục hồi vào ô nhập không.
   - Bấm nút "Xóa điều kiện" -> Kiểm tra xem tất cả các ô nhập nâng cao có được xóa trống và rổ hàng reset về mặc định không.

## Files touched
- `index.html` — Cập nhật cấu trúc HTML, CSS, và logic lọc Javascript.
- `docs/stories/_inbox/US-076_nang_cap_bo_loc_chi_tiet.md` — Cập nhật tài liệu User Story.

## 🔄 Change Requests (Yêu cầu Thay đổi)
*   **Ngày:** 2026-06-08
*   **Yêu cầu cũ:** Logic so khớp số nhà chỉ hỗ trợ so sánh bằng, so sánh bắt đầu bằng suffix single letter (`100` khớp `100a`), hoặc prefix nếu query kết thúc bằng dấu `.`.
*   **Yêu cầu mới [US-076.2]:** Hỗ trợ so khớp số nhà theo tiếp đầu ngữ tổng quát (prefix matching). Ví dụ, gõ "100.8" vẫn khớp và tìm ra "100.85b".
*   **Mức độ tác động:** Rất thấp, chỉ thay đổi helper JavaScript `matchHouseNumber` trong `index.html`.

---

*   **Ngày:** 2026-06-08
*   **Yêu cầu cũ [US-076.3]:** Các bộ lọc chi tiết hiển thị dưới dạng khối hộp đầy đủ có nhãn và ô nhập riêng biệt chiếm nhiều diện tích dọc.
*   **Yêu cầu mới [US-076.3]:** Chuyển sang phong cách gọn gàng, tinh tế: bọc trong thẻ card bo tròn, bố trí grid 2 cột cân xứng. Nhãn kèm emoji nằm bên trái, ô nhập Từ/Đến inline có gạch dưới nét đứt dashed mảnh và đơn vị đo màu đỏ đất trầm ấm bên phải.
*   **Mức độ tác động:** Trung bình, cập nhật HTML cấu trúc bộ lọc và bổ sung CSS classes tương ứng trong `index.html`.

## 🧠 Retro, Lessons Learned & Good Practices (Bugs & Adjustments - 2026-06-08)

Trong quá trình nghiệm thu thực tế trên môi trường Live di động, hệ thống đã ghi nhận các sự cố/lỗi hiển thị và được điều chỉnh như sau:

### 1. Sự cố Đè Nút Cài đặt (Settings dial overlap)
- **Lỗi**: Nút bánh răng cài đặt trôi nổi `.admin-speed-dial` đè lên hai nút hành động của bộ lọc.
- **Giải pháp**: Thêm CSS dịch chuyển `.admin-speed-dial` lên `bottom: 120px !important` khi bộ lọc hoạt động (`body.filter-active`).

### 2. Sự cố Tự đóng Bộ lọc (Mobile auto-close)
- **Lỗi**: Khi nhấp vào các ô nhập số chi tiết, bộ lọc tự đóng do hiểu nhầm là click ra ngoài tiêu đề.
- **Giải pháp**: Tắt cơ chế "nhấp ngoài đóng bộ lọc" trên thiết bị màn hình nhỏ (< 768px).

### 3. Sự cố Phóng to Safari (iOS Auto-zoom)
- **Lỗi**: iOS Safari tự động zoom giao diện khi nhấp vào ô nhập có cỡ chữ < 16px, làm vỡ khung hiển thị.
- **Giải pháp**: Đặt cứng `font-size: 16px !important` cho toàn bộ các ô nhập, select, textarea trên mobile.

### 4. Đổi vị trí Nút Hành động (Action buttons swap)
- **Lỗi**: Khách hàng muốn nút "Tìm kiếm" nằm bên phải góc màn hình và "Xóa điều kiện" ở bên trái.
- **Giải pháp**: Tráo đổi thứ tự HTML của 2 nút trong thẻ `.filter-footer-actions`.

### 5. Khóa chân trang bộ lọc trên điện thoại (Mobile footer anchoring)
- **Lỗi**: Việc sử dụng `position: fixed` khiến hai nút hành động bị trôi nổi lơ lửng ở giữa danh sách bộ lọc khi cuộn, do thuộc tính `transform` của container tạo một Containing Block mới.
- **Giải pháp**:
  - Đóng gói toàn bộ các phần tử cuộn trong thẻ `.filter-scroll-content`.
  - Thiết lập `.filter-scroll-content` là `display: contents` trên máy tính để giữ nguyên bố cục lưới Grid.
  - Trên mobile, thiết lập `#filterPanel` thành Flexbox đứng (`display: flex; flex-direction: column; overflow: hidden;`), đẩy `.filter-scroll-content` chiếm hết phần trống (`flex: 1; overflow-y: auto;`) và giữ nút chân trang `.filter-footer-actions` cố định tự nhiên ở đáy dưới dạng `position: relative; flex-shrink: 0;`.

### 6. Sự cố Lọc Số thập phân Dấu phẩy (Comma decimal range parsing)
- **Lỗi**: Cào dữ liệu từ Pool có giá dạng `"8,5 tỷ"`. Lọc `7` đến `8` tỷ vẫn cho ra căn `8,5 tỷ` do `parseFloat("8,5 tỷ")` trả về số `8` thay vì `8.5`.
- **Giải pháp**: 
  - Tạo hàm [parseFloatHelper](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html#L4023) chuẩn hóa dấu phẩy thành dấu chấm.
  - Cập nhật logic `getFiltered()` để ưu tiên thuộc tính giá đã parse sạch (`p.gia`), fallback dùng `parseFloatHelper(p.raw_gia_chao)` và chuyển đổi tất cả so sánh khoảng số học qua hàm helper này.

---

*   **Ngày:** 2026-06-08
*   **Yêu cầu cũ [US-076.3]:** Các bộ lọc chi tiết hiển thị dưới dạng khối hộp đầy đủ có nhãn và ô nhập riêng biệt chiếm nhiều diện tích dọc.
*   **Yêu cầu mới [US-076.3]:** Chuyển sang phong cách gọn gàng, tinh tế: bọc trong thẻ card bo tròn, bố trí grid 2 cột cân xứng. Nhãn kèm emoji nằm bên trái, ô nhập Từ/Đến inline có gạch dưới nét đứt dashed mảnh và đơn vị đo màu đỏ đất trầm ấm bên phải.
*   **Mức độ tác động:** Trung bình, cập nhật HTML cấu trúc bộ lọc và bổ sung CSS classes tương ứng trong `index.html`.
