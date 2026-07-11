---
id: US-094B
status: accepted
date: 2026-06-15
size: M
---

# US-094B: Cô lập Module Bộ lọc & Tìm kiếm thông minh

## User story
**As a** Developer  
**I want** cô lập module bộ lọc (quận, phường, đường, hướng, khoảng giá, diện tích, kết cấu...) và tính năng tìm kiếm thông minh từ index.html sang static/js/lego_filters.js  
**So that** làm sạch tệp index.html, mô-đun hóa bộ máy lọc tìm kiếm, nâng cao khả năng mở rộng bộ lọc trong tương lai và duy trì tính tương thích ngược hoàn hảo.

## Acceptance
- [ ] Tạo tệp `static/js/lego_filters.js` để đóng gói toàn bộ logic lọc, tìm kiếm và tạo tab.
- [ ] Di chuyển toàn bộ cấu trúc biến lưu trữ trạng thái bộ lọc (`selDistricts`, `selWards`, `selDuongs`, `selHuong`, `selGia`, `selDanhGia`, `showFavOnly`, `showOnAirOnly`) sang `lego_filters.js`.
- [ ] Di chuyển các hàm dựng giao diện tab/multiselect động (`buildDistrictTabs`, `buildWardTabs`, `buildDuongTabs`, `buildHuongTabs`, `updateMultiselectPlaceholder`, `toggleOption`, `updateSelectionFromCheckboxes`) sang `lego_filters.js`.
- [ ] Di chuyển các hàm xử lý tìm kiếm (`clearSearchInput`, `onSearchInput`, `toggleSearchBar`, `toggleSearchClearBtn`, `searchPoolRows`) sang `lego_filters.js`.
- [ ] Di chuyển các hàm dựng checkbox tiêu chí thô (`renderCriteriaCheckboxes`, `matchCriteriaHelper`) sang `lego_filters.js`.
- [ ] Di chuyển các hàm lõi lọc dữ liệu (`getFiltered`, `applyFilter`, `applyGia`, `resetFilters`, `clearAllFilters`, `toggleFavFilter`, `checkPoolFallbackSearch`) sang `lego_filters.js`.
- [ ] Liên kết và đăng ký toàn cục các biến/hàm trên đối tượng `window` để duy trì tính tương thích ngược hoàn toàn với `index.html` và các module render khác.
- [ ] Đạt tỷ lệ 100% PASS cho bộ kiểm thử E2E Playwright trên cả giao diện Desktop và Mobile.

## Solution

### 1. LegoFilters Module (`lego_filters.js`)
*   Định nghĩa đối tượng toàn cục `window.LegoFilters`.
*   Di chuyển tất cả các Set và biến trạng thái lọc:
    *   `window.selDistricts`, `window.selWards`, `window.selDuongs`, `window.selHuong`, `window.selGia`, `window.selDanhGia` (giữ nguyên cấu trúc Set).
    *   `window.showFavOnly`, `window.showOnAirOnly`.
*   Port các hàm dựng tab động và đăng ký toàn cục:
    *   `buildDistrictTabs`, `buildWardTabs`, `buildDuongTabs`, `buildHuongTabs`.
    *   `updateMultiselectPlaceholder`, `toggleOption`, `updateSelectionFromCheckboxes`.
*   Port các hàm tìm kiếm và đăng ký toàn cục:
    *   `clearSearchInput`, `onSearchInput`, `toggleSearchBar`, `toggleSearchClearBtn`, `searchPoolRows`.
*   Port các hàm lọc dữ liệu và đăng ký toàn cục:
    *   `getFiltered` (gọi đến `getMappedPoolData`, `DATA`, `favs`, v.v.).
    *   `applyFilter` (gọi đến `getFiltered`, `render`, `updateSwitcherCounts`, v.v.).
    *   `applyGia`, `resetFilters`, `clearAllFilters`, `toggleFavFilter`, `checkPoolFallbackSearch`.
*   Port các hàm tiêu chí checklist và đăng ký toàn cục:
    *   `renderCriteriaCheckboxes`, `matchCriteriaHelper`.

### 2. Tái cấu trúc index.html
*   Nạp tệp script `static/js/lego_filters.js` ở thẻ `<head>` của `index.html` ngay sau `lego_render_admin.js` và trước `lego_detail_client.js`.
*   Loại bỏ toàn bộ các khai báo biến trạng thái bộ lọc và các hàm liên quan khỏi phần `<script>` chính của `index.html`.

---

## User Review Required

> [!IMPORTANT]
> **Preserving Global States & DOM Identifiers:**
> - To maintain absolute backward compatibility, all selection Sets (`selDistricts`, `selWards`, `selDuongs`, `selHuong`, `selGia`, `selDanhGia`) and active filter booleans (`showFavOnly`, `showOnAirOnly`) will be preserved as properties of the global `window` object (e.g. `window.selDistricts`).
> - This ensures that other modules (such as rendering engines `LegoRenderClient`/`LegoRenderAdmin` or future modules) can query the active filters without any disruption or breaking API changes.
> - The DOM inputs and checkboxes (like `#filterGiaMin`, `#filterGiaMax`, `.filter-criterion`, etc.) remain in the main HTML, but their change listeners and values will be managed by the new module.

---

## 📋 Implementation Plan

### [Filters Component]

#### [NEW] [lego_filters.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_filters.js)
- Định nghĩa cấu trúc IIFE đóng gói logic.
- Khai báo và gán các Set bộ lọc vào `window`:
  ```javascript
  window.selDistricts = new Set();
  window.selWards = new Set();
  window.selDuongs = new Set();
  window.selHuong = new Set();
  window.selGia = new Set();
  window.selDanhGia = new Set();
  window.showFavOnly = false;
  window.showOnAirOnly = false;
  ```
- Port toàn bộ các hàm lọc, dựng tab, tìm kiếm, checklist tiêu chí từ `index.html` sang.
- Thiết lập các liên kết toàn cục cho tất cả các hàm này để các tệp khác vẫn gọi được bình thường qua `window.functionName`.

#### [MODIFY] [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html)
- Liên kết tệp script mới ở `<head>`:
  ```html
  <script src="static/js/lego_filters.js?v=202606151500"></script>
  ```
- Xóa bỏ khai báo các biến `selDistricts`, `selWards`, `selDuongs`, `selHuong`, `selGia`, `selDanhGia`, `showFavOnly`, `showOnAirOnly`.
- Xóa bỏ định nghĩa các hàm: `syncTabUI`, `toggleMultiselect`, `toggleOption`, `updateSelectionFromCheckboxes`, `updateMultiselectPlaceholder`, `applyGia`, `toggleSearchClearBtn`, `clearSearchInput`, `onSearchInput`, `toggleSearchBar`, `getFiltered`, `matchCriteriaHelper`, `renderCriteriaCheckboxes`, `updateStaticTabsVisibility`, `toggleFilter`, `closeFilter`, `buildDistrictTabs`, `buildWardTabs`, `buildDuongTabs`, `buildHuongTabs`, `updateFilterSummary`, `resetFilters`, `clearAllFilters`, `toggleFavFilter`, `applyFilter`, `checkPoolFallbackSearch`, `searchPoolRows`.

---

## 📝 Task Checklist (TODO)
- [ ] **Thiết kế & Khảo sát:**
  - [ ] Khảo sát toàn bộ danh sách hàm lọc và biến trạng thái trong `index.html`.
  - [ ] Kiểm tra các điểm tương tác giữa bộ lọc với giao diện render và Google Sheets data loading.
- [ ] **Triển khai Code:**
  - [ ] Tạo tệp `static/js/lego_filters.js` và chuyển các biến trạng thái lọc sang.
  - [ ] Di chuyển các hàm dựng tab động và multiselect.
  - [ ] Di chuyển các hàm tìm kiếm thông minh và logic chuẩn hóa tiếng Việt.
  - [ ] Di chuyển các hàm lõi lọc dữ liệu (`getFiltered`, `applyFilter`...).
  - [ ] Tích hợp vào `index.html`, nạp script mới ở head và làm sạch code cũ.
- [ ] **Kiểm thử & Bàn giao:**
  - [ ] Viết script E2E Playwright chuyên biệt `scratch/test_e2e_filters.py` giả lập hành vi lọc.
  - [ ] Chạy bộ kiểm thử E2E tự động đa thiết bị đạt 100% PASS.
  - [ ] Merge code vào `main` và push deploy Live lên Production.
  - [ ] Bàn giao PO nghiệm thu bộ lọc và tìm kiếm trên live.

---

## 🧠 Retro, Lessons Learned & Good Practices
- **Good Practices**:
  - Expose state variables on `window` early to guarantee backward compatibility with inline scripts and other modules.
  - When writing Playwright E2E tests for hidden checkable elements (like custom checkboxes styled with `opacity: 0`), use `.check(force=True)` to avoid element visibility actionability timeouts.
  - Trigger inline events (like `keyup` for search inputs) programmatically with `page.evaluate("onSearchInput()")` to ensure consistent execution across headless testing environments where simple `fill` calls might not fire keyup handlers.
  - Make sure the sheets API mocks match the requested columns and rows exactly, without prepending header rows if the fetching code uses ranges (like `Pool!A2:ZZ`) that don't expect headers.

---

## Verification Plan

### Automated Tests (BẮT BUỘC - Desktop & Mobile)
- **Script kiểm thử chính:** [test_e2e_filters.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_e2e_filters.py) [NEW]
- **Kịch bản test:**
  1. Mở trang chủ ở chế độ khách hàng, kiểm tra thanh tìm kiếm và bộ lọc quận/phường.
  2. Chọn bộ lọc Quận 3 (Q3) và nhập "CMT8" vào ô tìm kiếm, kiểm tra số lượng card BĐS lọc chính xác.
  3. Bấm nút "Xóa bộ lọc", xác nhận toàn bộ bộ lọc và ô tìm kiếm được reset về trạng thái ban đầu, hiển thị đầy đủ danh sách.
  4. Đăng nhập Admin, mở bộ lọc Admin, kiểm tra bộ lọc nâng cao (khoảng giá, diện tích trên sổ, số phòng ngủ), kiểm tra kết quả lọc hiển thị đúng.

### Manual Verification
- Thực hiện chọn nhiều bộ lọc cùng lúc trên giao diện điện thoại (Mobile) và máy tính (Desktop) để xác nhận độ responsive và tốc độ phản hồi.
- Nhập các chuỗi tìm kiếm tiếng Việt có dấu, không dấu, chữ hoa, chữ thường và kiểm tra kết quả.

---

## Files touched
- `docs/stories/_inbox/US-094B_lego_frontend_filters.md`
- `static/js/lego_filters.js`
- `index.html`
