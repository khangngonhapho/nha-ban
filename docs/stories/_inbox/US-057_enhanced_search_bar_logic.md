---
id: US-057
status: accepted
date: 2026-05-31
size: M
---

# US-057: Thanh tìm kiếm thông minh kết hợp nhiều điều kiện và phân tích địa chỉ (Multi-Condition Smart Search Engine with Address & Price Parser)

## User story
**As a** Client / Admin
**I want** to search for properties using an enhanced search bar that supports combined multi-condition query parsing separated by `+`, parses standalone numbers as house numbers followed by street names, and parses price numbers with "tỷ" next to them as price range matches
**So that** I can naturally and extremely quickly search for properties using structured query combos (e.g. `17 ngô thời nhiệm + 25 tỷ + trà mi`), significantly supporting KPI 1 (Tốc độ biên tập) and KPI 4 (Hiệu quả định giá so sánh) of the Value Plan.

## Acceptance
- [ ] **Admin-Only Feature (Dành riêng cho Admin):**
  - The new multi-condition smart query parsing logic is strictly active only when `isAdmin === true`.
  - If `isAdmin === false` (regular client view), the search bar continues to use the existing simple string matching algorithm.
- [ ] **Combined Multi-Condition Query Parsing (AND Search via `+`):**
  - Split the search input by `+` character into multiple sub-queries.
  - All parsed sub-queries must match (AND logic) for a property to be displayed.
  - Filter out and ignore empty sub-queries (e.g. `17 ngô thời nhiệm + + 25 tỷ` is treated as just two queries).
- [ ] **Price Range Query Matching (Price + `tỷ`):**
  - Recognize a sub-query matching `<number> tỷ` (e.g. `25 tỷ`, `25.5 tỷ`) as a price search.
  - Standalone numbers without the word "tỷ" MUST NOT be parsed as price queries.
  - **Nếu nhập số nguyên (Ví dụ `25 tỷ`):** Tìm tiếp đầu ngữ (prefix match), tức là các căn có giá từ 25.0 tỷ đến dưới 26.0 tỷ ($25 \le P < 26$).
  - **Nếu nhập số lẻ (Ví dụ `25.5 tỷ`):** Tìm chính xác giá (exact match), tức là giá bán của căn nhà bằng đúng $25.5$ tỷ.
- [ ] **House Number and Street Name Extraction:**
  - If a sub-query starts with a number (e.g., `17 ngô thời nhiệm`, `1168.42 trường sa`, `17/3 cmt8`), extract the leading number as the **house number** (số nhà) and any following text as the **street name** (tên đường).
  - If a sub-query consists ONLY of a number (e.g., `17`), it is parsed as a standalone house number query.
  - **House Number Matching Rules:**
    - Support exact match (e.g., query `17` matches property `17`).
    - Support complex house number split rule: split raw house numbers by `+` and check the first part (e.g., `1168.42+44` -> `1168.42`).
    - Support sub-number match (e.g., query `17` matches property `17/3` or `17/3A`).
    - Support letter suffix match (e.g., query `17` matches property `17A`).
- [ ] **Normalized Street Name Query Matching:**
  - Automatically normalize street names typed in the search bar to match the system's normalized database codes (Rule 1 of `BDS-AGENTS.md`):
    - `Cách Mạng Tháng 8` (and its variants like `CMT8`, `Cách Mạng Tháng Tám`) -> `ttmc`
    - `Ba Tháng Hai` (and its variants like `3/2`, `3-2`, `3 tháng 2`) -> `htb`
    - `Đường số 7` -> `7sd`
  - Match the normalized query against the property's normalized street fields (`p.raw_ten_duong`, `p.duong_truoc_nha`).
- [ ] **Accent-Free Search Support (Tìm kiếm không dấu):**
  - Support matching search strings without accents (accents/diacritics removed) across all fields (street name, title, landlord name, notes, description).
  - Typing `phan dinh phung` matches `Phan Đình Phùng`, and `tra mi` matches `Trà Mi`.
- [ ] **General Text Query (Fallback Matching):**
  - If a sub-query is neither a price query nor starts with a number (e.g. `trà mi`, `ngô thời nhiệm`), match it against:
    - Property street name fields (`p.raw_ten_duong`, `p.duong_truoc_nha`).
    - Property title (`p.t`).
    - Landlord name (`p.raw_ten_dau_chu` - Admin mode only).
    - District/Ward/ID (as a fallback).

---

## Solution

### 1. Architectural Design & Query Parser
The search query parser is implemented directly inside `getFiltered()` in `index.html`. It works by parsing the raw search input string into a list of parsed query objects and executing AND-logic matches across properties.

### 2. High-Performance JS Implementation (Proposed `getFiltered` logic)
```javascript
    function getFiltered() {
      let a = (isAdmin && activeMode === 'pool') ? getMappedPoolData() : DATA;
      
      // Lọc động: Chỉ hiện căn Public (US-039.7)
      if (isAdmin && activeMode === 'pool' && showOnAirOnly) {
        a = a.filter(p => DATA.some(x => 
          (x.system_id && p.system_id && String(x.system_id).trim() === String(p.system_id).trim()) ||
          (x.id && p.id && String(x.id).trim() === String(p.id).trim())
        ));
      }
      
      const sv = (document.getElementById('searchInput')?.value || '').trim();
      if (sv) {
        if (isAdmin) {
          // Combined Multi-condition AND Search for Admin
          const subQueries = sv.split('+').map(s => s.trim()).filter(Boolean);
          
          // Helper to normalize street queries (Rule 1 of BDS-AGENTS.md)
          function normalizeStreetQuery(street) {
            let s = String(street || '').trim().toLowerCase();
            if (!s) return '';
            s = s.replace(/cách\s+mạng\s+tháng\s+8|cách\s+mạng\s+tháng\s+tám|cmt8/g, 'ttmc');
            s = s.replace(/ba\s+tháng\s+hai|3\/2|3-2|3\s+tháng\s+2/g, 'htb');
            s = s.replace(/đường\s+số\s+7/g, '7sd');
            return s;
          }

          // Helper to match Vietnamese complex house numbers
          function matchHouseNumber(rawSoNha, querySoNha) {
            const cleanRaw = String(rawSoNha || '').trim().toLowerCase();
            const cleanQuery = String(querySoNha || '').trim().toLowerCase();
            if (!cleanQuery) return true;
            if (!cleanRaw) return false;
            
            // Rule 2: compound numbers "1168.42+44" -> "1168.42"
            const normalizedRaw = cleanRaw.split('+')[0].trim();
            
            if (normalizedRaw === cleanQuery) return true;
            if (normalizedRaw.startsWith(cleanQuery + '/')) return true;
            
            const suffixRegex = new RegExp('^' + cleanQuery + '[a-z]$');
            if (suffixRegex.test(normalizedRaw)) return true;
            
            return false;
          }
          
          a = a.filter(p => {
            return subQueries.every(sub => {
              const subLower = sub.toLowerCase();
              
              // 1. Match Price query: e.g. "25 tỷ", "25.5 tỷ"
              const priceMatch = sub.match(/^([\d,.]+)\s*tỷ$/i) || sub.match(/([\d,.]+)\s*tỷ/i);
              if (priceMatch) {
                const numStr = priceMatch[1].replace(',', '.');
                const num = parseFloat(numStr);
                const pGia = parseFloat(p.gia) || 0;
                if (numStr.includes('.')) {
                  // Decimal price: exact match
                  return Math.abs(pGia - num) < 0.001;
                } else {
                  // Integer price: prefix match range [num, num+1)
                  return pGia >= num && pGia < num + 1;
                }
              }
              
              // 2. Match House Number + Street: starts with a digit
              const houseStreetMatch = sub.match(/^(\d+[\d/a-zA-Z.]*)\s*(.*)$/);
              if (houseStreetMatch) {
                const houseNumQuery = houseStreetMatch[1];
                const streetQuery = houseStreetMatch[2].trim();
                
                const hnMatch = matchHouseNumber(p.raw_so_nha, houseNumQuery);
                if (!hnMatch) return false;
                
                if (streetQuery) {
                  const normStreetQ = normalizeStreetQuery(streetQuery);
                  const normRawDuong = normalizeStreetQuery(p.raw_ten_duong);
                  const normDuongTruoc = normalizeStreetQuery(p.duong_truoc_nha);
                  const titleMatch = p.t.toLowerCase().includes(streetQuery.toLowerCase());
                  return normRawDuong.includes(normStreetQ) || normDuongTruoc.includes(normStreetQ) || titleMatch;
                }
                return true;
              }
              
              // 3. Fallback: General text match
              const normSub = normalizeStreetQuery(sub);
              const streetMatch = normalizeStreetQuery(p.raw_ten_duong).includes(normSub) || 
                                  normalizeStreetQuery(p.duong_truoc_nha).includes(normSub);
              const titleMatch = p.t.toLowerCase().includes(subLower);
              const pMatch = p.phuong.toLowerCase().includes(subLower);
              const idMatch = String(p.id).toLowerCase().includes(subLower);
              const qMatch = p.q.toLowerCase().includes(subLower) ||
                             p.ql.toLowerCase().includes(subLower) ||
                             (subLower === 'phú nhuận' && p.q === 'pn') ||
                             (subLower === 'tân bình' && p.q === 'tb') ||
                             (subLower === 'bình thạnh' && p.q === 'bt') ||
                             (subLower === 'gò vấp' && p.q === 'gv') ||
                             (subLower === 'quận 3' && p.q === 'q3') ||
                             (subLower === 'quận 10' && p.q === 'q10');
                             
              const dauChuMatch = (p.raw_ten_dau_chu || '').toLowerCase().includes(subLower);
              const dtMatch = (p.raw_dt_dau_chu || '').toLowerCase().includes(subLower);
              const ndMatch = (p.raw_noi_dung_chinh || '').toLowerCase().includes(subLower);
              const mtMatch = (p.raw_mo_ta_chi_tiet || '').toLowerCase().includes(subLower);
              const noteMatch = (p.note || '').toLowerCase().includes(subLower);
              const cpMatch = (p.cu_phap || '').toLowerCase().includes(subLower);
              const soNhaMatch = (p.raw_so_nha || '').toLowerCase().includes(subLower);
              const duongMatch = (p.raw_ten_duong || '').toLowerCase().includes(subLower);
              
              return idMatch || titleMatch || streetMatch || pMatch || qMatch ||
                     dauChuMatch || dtMatch || ndMatch || mtMatch || noteMatch || cpMatch || soNhaMatch || duongMatch;
            });
          });
        } else {
          // Regular client search logic (remains unchanged)
          const svLower = sv.toLowerCase();
          a = a.filter(p => {
            const idMatch = String(p.id).toLowerCase().includes(svLower);
            const tMatch = p.t.toLowerCase().includes(svLower);
            const dMatch = p.duong_truoc_nha.toLowerCase().includes(svLower);
            const pMatch = p.phuong.toLowerCase().includes(svLower);
            const qMatch = p.q.toLowerCase().includes(svLower) ||
              p.ql.toLowerCase().includes(svLower) ||
              (svLower === 'phú nhuận' && p.q === 'pn') ||
              (svLower === 'tân bình' && p.q === 'tb') ||
              (svLower === 'bình thạnh' && p.q === 'bt') ||
              (svLower === 'gò vấp' && p.q === 'gv') ||
              (svLower === 'quận 3' && p.q === 'q3') ||
              (svLower === 'quận 10' && p.q === 'q10');
            return idMatch || tMatch || dMatch || pMatch || qMatch;
          });
        }
      }
      
      // ... rest of filtering logic ...
```

---

## 📋 Implementation Plan

### Giai đoạn 1: Khảo sát & Thiết kế Parser
- Rà soát hàm `getFiltered()` trong `index.html`.
- Thiết kế và kiểm toán bộ regex tách số nhà + đường phố, số tiền + tỷ.
- Đối chiếu với các quy tắc sống còn trong `BDS-AGENTS.md`.

### Giai đoạn 2: Cài đặt logic tìm kiếm mới vào `index.html`
- Thay đổi logic lọc trong hàm `getFiltered()` theo mã đề xuất ở trên.
- Đảm bảo giữ nguyên các bộ lọc thông số chi tiết (Diện tích, Chiều ngang, Hướng, v.v.) và bộ sưu tập ở phía dưới hàm.
- Tinh chỉnh cơ chế debounce hoặc tự động xóa kết quả khi người dùng nhập liệu để trải nghiệm tìm kiếm cực kỳ nhạy và mượt mà.

### Giai đoạn 3: Kiểm thử & Nghiệm thu
- Thực hiện chạy thử nghiệm tìm kiếm với các từ khóa đơn lẻ và kết hợp nhiều điều kiện (AND) có dấu `+`.
- Xác nhận các ca kiểm thử hoạt động chính xác theo tiêu chí Acceptance.

---

## 📝 Task Checklist (TODO)
- [ ] **Thiết kế & Khảo sát:**
  - [ ] Khảo sát code cũ của hàm `getFiltered()` trong `index.html`
  - [ ] Chốt bộ Regex parsing cho Giá ("tỷ"), Số nhà + Tên đường
- [ ] **Triển khai Code:**
  - [ ] Code logic parser trong `getFiltered()`
  - [ ] Tích hợp bộ chuẩn hóa tên đường đặc biệt (Rule 1: CMT8 -> ttmc, 3/2 -> htb, Đường số 7 -> 7sd)
  - [ ] Tích hợp bộ so khớp số nhà thông minh (Rule 2: split `+` phức hợp, exact, sub-number, letter suffix)
  - [ ] Đảm bảo fallback an toàn cho tìm kiếm Admin (landlord, note, cu phap, dt)
- [ ] **Kiểm thử sơ bộ:**
  - [ ] Chạy các ca test thủ công (17 ngô thời nhiệm + 25 tỷ + trà mi, v.v.)
  - [ ] Kiểm tra tính tương thích trên thiết bị di động
  - [ ] Đóng gói & Clean tài liệu

---

## 🛠️ Update Logic (Drafting while Doing)
- **Hệ thống hóa Parser thông minh:** 
  - Phân tách chuỗi truy vấn bằng dấu `+`.
  - Hỗ trợ phân tích cú pháp giá trị dạng `<số> tỷ` hoặc `<số>.<số> tỷ` để thực hiện tìm kiếm khoảng (prefix match) hoặc tìm kiếm chính xác (exact match) tương ứng.
  - Phân tích cú pháp Số nhà + Tên đường bằng Regex nâng cao: Tách phần số nhà đứng đầu và phần tên đường đứng sau.
  - Hỗ trợ chuẩn hóa tên đường đặc biệt (ví dụ: `cmt8` -> `ttmc`, `3/2` -> `htb`, `đường số 7` -> `7sd`) khớp với cơ sở dữ liệu đã chuẩn hóa của dự án.
  - Hỗ trợ khớp số nhà phức tạp (ví dụ: tách dấu `+` trong số nhà thực tế như `1168.42+44` -> `1168.42`).
- **Bypass Browser Autofill Prompt:** Thay đổi trường Google Client ID từ loại `password` hoặc các trường có kiểu bảo mật nhạy cảm sang thẻ văn bản thông thường kết hợp thuộc tính che phủ kí tự (disc masking) và đổi tên ID ô tìm kiếm từ `searchInput` thành `bdsSearchInput` để trình duyệt (Chrome, Edge) không nhận nhầm là form lưu mật khẩu/tài khoản thanh toán.
- **Tối ưu hóa hiệu năng & Chống lag (Debounce):** Tích hợp cơ chế Debounce 300ms khi gõ bàn phím trước khi kích hoạt hàm lọc và render lại DOM giúp giảm lag đáng kể khi gõ.
- **Phòng chống Crash (Safety Checks & Casts):** 
  - Ép kiểu chuỗi `String()` chặt chẽ khi gọi hàm `generateAdminTitleFromNộiDungChinh` để tránh lỗi kiểu dữ liệu (TypeError).
  - Thêm kiểm tra an toàn `window.isListingSodoUrl` trong hàm `render()`.
  - Khắc phục lỗi crash trên giao diện Client: Bao bọc các phần cập nhật DOM thống kê (chỉ có ở giao diện Admin như `sTong`, `sTang`, v.v.) bằng các khối điều kiện kiểm tra tồn tại phần tử để tránh unhandled TypeError làm đóng băng tìm kiếm của Client.
- **Tối ưu độ chính xác tìm kiếm (Structured Fallback):** Loại bỏ việc tìm kiếm trong các trường mô tả chi tiết tự do quá rộng (`p.raw_mo_ta_chi_tiet`, `p.raw_noi_dung_chinh`, `p.note`) nhằm tránh các kết quả khớp giả (false-positive) do các từ khóa ngẫu nhiên trong bài viết, tập trung khớp chuẩn vào địa chỉ cấu trúc, tên đường chuẩn hóa, khoảng giá và tên đầu chủ.

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)
1. **Lessons Learned (Bài học kinh nghiệm):**
   - **Autofill Triggers:** Trình duyệt hiện đại cực kỳ nhạy cảm với các input có liên quan đến bảo mật hoặc có thuộc tính che ẩn ký tự. Việc sử dụng thuộc tính dạng mật khẩu hoặc đặt tên input quá phổ quát có thể kích hoạt cơ chế Autofill của trình duyệt. Đặt tên riêng biệt như `bdsSearchInput` và tách rời style che ẩn là giải pháp lâu dài cực kì sạch sẽ.
   - **Client/Admin DOM Isolation:** Khi chạy ứng dụng dạng Single Page App hoặc chung một file giao diện cho cả Admin và Client, phải tuyệt đối cẩn thận khi cập nhật DOM. Mọi thao tác ghi/đọc thuộc tính của DOM node đều phải được wrap trong điều kiện kiểm tra phần tử tồn tại (`if (element) ...`) để tránh việc crash JS làm ngưng toàn bộ logic động phía sau.
   - **Performance vs Reactivity:** Lọc real-time cực kỳ tiện lợi nhưng với rổ hàng lớn (hàng nghìn căn), việc kích hoạt render DOM liên tục trên mỗi tổ hợp phím (keystroke) là nguyên nhân gây lag. Một khoảng thời gian debounce ngắn (300ms) là vừa đủ để mang lại cảm giác mượt mà tức thì cho người dùng.
2. **Good Practices (Thực tiễn tốt):**
   - Luôn sử dụng bộ lọc tìm kiếm có cấu trúc (Structured Location & Price metadata) làm ưu tiên hàng đầu thay vì fallback tìm kiếm văn bản tự do tràn lan trong bài mô tả dài để tránh kết quả rác.
   - Luôn ép kiểu `String()` an toàn cho các trường dữ liệu lấy từ sheet trước khi thực hiện thao tác so khớp chuỗi như `.toLowerCase()` hoặc `.includes()`.

## Verification Plan

### Automated Tests
- *(Không áp dụng kiểm thử tự động cho Client JS, sử dụng bộ kiểm thử thủ công trực quan)*

### Manual Verification
- **Test Case 1 (Lọc Giá):** Nhập `25 tỷ` vào search bar. Xác nhận kết quả hiển thị tất cả các căn có giá từ 25.0 tỷ đến 25.99 tỷ (ví dụ 25 tỷ, 25.1 tỷ, 25.9 tỷ). Căn có giá `2.5 tỷ` hoặc `250 tỷ` tuyệt đối không được xuất hiện.
- **Test Case 2 (Lọc Số nhà):** Nhập `17` vào search bar. Xác nhận hiển thị các căn số nhà `17`, `17/3`, `17A`.
- **Test Case 3 (Số nhà + Tên đường):** Nhập `17 ngô thời nhiệm`. Xác nhận tìm chính xác căn số `17` ở đường `Ngô Thời Nhiệm`.
- **Test Case 4 (Kết hợp nhiều điều kiện với dấu +):** Nhập `17 ngô thời nhiệm + 25 tỷ + trà mi`. Xác nhận tìm đúng căn số 17 ngô thời nhiệm, giá trong khoảng 25.x tỷ, đầu chủ có tên trà mi (trong Admin mode).
- **Test Case 5 (Chuẩn hóa tên đường đặc biệt):** Nhập `cmt8` hoặc `3/2` vào ô tìm kiếm. Xác nhận hệ thống tìm khớp chính xác với các đường được lưu mã hóa `TTMC` và `HTB` tương ứng.

## Files touched
- `index.html` — Nâng cấp hàm `getFiltered()` nâng cao bộ lọc tìm kiếm thông minh.

## 🔄 Change Requests (Yêu cầu Thay đổi)
*(Sẽ ghi nhận nếu PO có thay đổi yêu cầu)*
