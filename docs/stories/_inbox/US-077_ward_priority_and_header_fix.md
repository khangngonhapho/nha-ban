---
id: US-077
status: accepted
date: 2026-06-08
size: S
---

# US-077: Kiểm tra sự đầy đủ, sắp xếp thứ tự ưu tiên Phường và sửa lỗi hiển thị header Source

## User story
**As an** Admin / Broker Khang Ngô
**I want** bộ lọc Phường (Wards filter) hiển thị đầy đủ danh sách Phường theo đúng thứ tự ưu tiên nghiệp vụ ở cả chế độ hiển thị tất cả (khi không chọn quận) và chế độ chọn quận cụ thể, đồng thời loại bỏ dòng tiêu đề của sheet Source khỏi danh sách hiển thị
**So that** tôi có thể tìm kiếm và xem rổ hàng theo các phân khu trọng điểm được sắp xếp khoa học, đồng thời không thấy các dữ liệu rác mang tên "phuong" và "UAN" trên giao diện.

## Acceptance
- [ ] **Sắp xếp thứ tự ưu tiên Phường chuẩn xác:**
  - Định nghĩa danh sách phường ưu tiên (WARD_PRIORITY) theo đúng thứ tự PO yêu cầu:
    - Xuân Hoà (Xuân Hòa), Bàn Cờ, Nhiêu Lộc
    - Cầu Kiệu, Đức Nhuận, Phú Nhuận
    - Vườn Lài, Hoà Hưng (Hòa Hưng), Diên Hồng
    - Gia Định, Bình Thạnh, Bình Lợi Trung, Thạnh Mỹ Tây, Bình Quới
    - Tân Sơn Hòa, Tân Sơn Nhất, Tân Bình, Bảy Hiền, Tân Hòa
  - Hỗ trợ chuẩn hóa unicode/dấu tiếng Việt khi so sánh (ví dụ: Hòa vs Hoà) để tránh lệch dữ liệu.
- [ ] **Trường hợp 1 (Chế độ hiển thị tất cả - Không chọn quận):**
  - Hiển thị đầy đủ danh sách các phường ưu tiên ở trên lên thanh bộ lọc Phường.
  - Các phường phụ khác (nếu có trong cơ sở dữ liệu) sẽ được tự động xếp ở sau theo thứ tự bảng chữ cái ABC.
- [ ] **Trường hợp 2 (Chọn quận cụ thể - 1 hoặc nhiều quận):**
  - Hiển thị đầy đủ danh sách các phường thuộc các quận được chọn (cả phường tĩnh và động).
  - Sắp xếp các phường này theo đúng thứ tự ưu tiên tương ứng. Các phường không nằm trong danh sách ưu tiên xếp cuối theo thứ tự ABC.
- [ ] **Loại bỏ dòng tiêu đề Source sheet ("phuong" / "UAN"):**
  - Sửa đổi hàm nạp dữ liệu từ Google Sheets Source trong `index.html` để bỏ qua hàng thứ 2 (dòng tiêu đề cột) thay vì map nó thành một listing thông thường.
  - Đảm bảo các chỉ số dòng `targetRowNumber` khi ghi đè hoặc cập nhật vẫn hoàn toàn chính xác.

## Solution

### 1. Khai báo Danh sách Phường ưu tiên và Hàm sắp xếp:
Khai báo mảng `WARD_PRIORITY` toàn cục và hàm chuẩn hóa so sánh chữ tiếng Việt:
```javascript
const WARD_PRIORITY = [
  "Xuân Hoà", "Xuân Hòa",
  "Bàn Cờ",
  "Nhiêu Lộc",
  "Cầu Kiệu",
  "Đức Nhuận",
  "Phú Nhuận",
  "Vườn Lài",
  "Hoà Hưng", "Hòa Hưng",
  "Diên Hồng",
  "Gia Định",
  "Bình Thạnh",
  "Bình Lợi Trung",
  "Thạnh Mỹ Tây",
  "Bình Quới",
  "Tân Sơn Hòa",
  "Tân Sơn Nhất",
  "Tân Bình",
  "Bảy Hiền",
  "Tân Hòa"
];

function normalizeVietnameseTones(str) {
  if (!str) return '';
  return str.normalize('NFC')
    .replace(/o\u0300/g, 'ò').replace(/o\u0301/g, 'ó').replace(/o\u0309/g, 'ỏ').replace(/o\u0303/g, 'õ').replace(/o\u0323/g, 'ọ')
    .replace(/a\u0300/g, 'à').replace(/a\u0301/g, 'á').replace(/a\u0309/g, 'ả').replace(/a\u0303/g, 'ã').replace(/a\u0323/g, 'ạ')
    .replace(/o\u0302\u0300/g, 'ồ').replace(/o\u0302\u0301/g, 'ố').replace(/o\u0302\u0309/g, 'ổ').replace(/o\u0302\u0303/g, 'ỗ').replace(/o\u0302\u0323/g, 'ộ')
    .replace(/a\u0302\u0300/g, 'ầ').replace(/a\u0302\u0301/g, 'ấ').replace(/a\u0302\u0309/g, 'ẩ').replace(/a\u0302\u0303/g, 'ẫ').replace(/a\u0302\u0323/g, 'ậ')
    .replace(/e\u0302\u0300/g, 'ề').replace(/e\u0302\u0301/g, 'ế').replace(/e\u0302\u0309/g, 'ể').replace(/e\u0302\u0303/g, 'ễ').replace(/e\u0302\u0323/g, 'ệ')
    .replace(/oà/g, 'òa').replace(/oá/g, 'óa').replace(/oả/g, 'ỏa').replace(/oã/g, 'õa').replace(/oạ/g, 'ọa')
    .replace(/uý/g, 'úy').replace(/uỳ/g, 'ùy').replace(/uỷ/g, 'ủy').replace(/uỹ/g, 'ũy').replace(/uỵ/g, 'ụy')
    .replace(/oè/g, 'òe').replace(/oé/g, 'óe').replace(/oẻ/g, 'ỏe').replace(/oẽ/g, 'õe').replace(/oẹ/g, 'ọe')
    .replace(/uâ\u0300/g, 'uầ').replace(/uâ\u0301/g, 'uấ').replace(/uâ\u0309/g, 'uẩ').replace(/uâ\u0303/g, 'uẫ').replace(/uâ\u0323/g, 'uậ')
    .trim().toLowerCase();
}

function sortWardsByPriority(wardList) {
  const priorityMap = {};
  WARD_PRIORITY.forEach((w, idx) => {
    priorityMap[normalizeVietnameseTones(w)] = idx;
  });

  return wardList.sort((a, b) => {
    const normA = normalizeVietnameseTones(a);
    const normB = normalizeVietnameseTones(b);
    const idxA = priorityMap[normA] !== undefined ? priorityMap[normA] : 9999;
    const idxB = priorityMap[normB] !== undefined ? priorityMap[normB] : 9999;
    
    if (idxA !== idxB) {
      return idxA - idxB;
    }
    return a.localeCompare(b, 'vi');
  });
}
```

### 2. Cập nhật `STATIC_WARD_MAP` theo đúng thứ tự ưu tiên:
```javascript
const STATIC_WARD_MAP = {
  q3: ["Xuân Hòa", "Bàn Cờ", "Nhiêu Lộc"],
  q10: ["Vườn Lài", "Hòa Hưng", "Diên Hồng"],
  bt: ["Gia Định", "Bình Thạnh", "Bình Lợi Trung", "Thạnh Mỹ Tây", "Bình Quới"],
  tb: ["Tân Sơn Hòa", "Tân Sơn Nhất", "Tân Bình", "Bảy Hiền", "Tân Hòa"],
  pn: ["Cầu Kiệu", "Đức Nhuận", "Phú Nhuận"]
};
```

### 3. Cập nhật `buildWardTabs()` xử lý cả 2 trường hợp:
```javascript
function buildWardTabs() {
  if (!isAdmin) return;
  let wards = [];
  
  if (selDistricts.size === 0) {
    // Trường hợp 1: Hiển thị tất cả
    const staticWards = [];
    ['q3', 'pn', 'q10', 'bt', 'tb'].forEach(d => {
      if (STATIC_WARD_MAP[d]) staticWards.push(...STATIC_WARD_MAP[d]);
    });
    const dataWards = [...new Set(DATA.map(p => p.phuong).filter(w => w && w !== '-' && w !== 'phuong'))];
    const combined = [...new Set([...staticWards, ...dataWards])];
    wards = sortWardsByPriority(combined);
  } else {
    // Trường hợp 2: Chọn 1 hoặc nhiều quận cụ thể
    const staticWards = [];
    for (const d of selDistricts) {
      if (STATIC_WARD_MAP[d]) {
        staticWards.push(...STATIC_WARD_MAP[d]);
      }
    }
    const pool = DATA.filter(p => selDistricts.has(p.q));
    const dataWards = [...new Set(pool.map(p => p.phuong).filter(w => w && w !== '-' && w !== 'phuong'))];
    const combined = [...new Set([...staticWards, ...dataWards])];
    wards = sortWardsByPriority(combined);
  }

  // Render ra UI giữ nguyên logic cũ ...
}
```

### 4. Loại bỏ dòng tiêu đề Source Sheet trong `index.html`:
Chỉnh sửa hàm nạp `sourceRows` để lọc bỏ dòng đầu tiên (chứa tiêu đề cột):
```javascript
          const fullList = sourceRows
            .map((sr, index) => {
              if (index === 0) return null; // Bỏ qua hàng tiêu đề
              if (!sr[3] && !sr[4]) return null;
              // ... giữ nguyên ánh xạ cũ
            })
            .filter(Boolean); // Lọc sạch các phần tử null
```

## 📋 Implementation Plan
- **Cách tiếp cận:**
  - Sửa đổi trực tiếp trong file Vercel frontend `index.html`.
  - Triển khai thuật toán chuẩn hóa dấu tiếng Việt để gộp các dạng gõ khác nhau của cùng một phường (NFC/NFD).
  - Sử dụng hàm sắp xếp có trọng số dựa trên chỉ mục mảng `WARD_PRIORITY`.
  - Bỏ qua index 0 của API Google Sheets Source query kết quả để chặn hàng tiêu đề lọt vào danh sách hiển thị.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:** Khảo sát code lọc phường hiện tại và cấu trúc API nạp Source
- [x] **Triển khai Code:**
  - [x] Khai báo mảng ưu tiên và hàm chuẩn hóa
  - [x] Cập nhật STATIC_WARD_MAP và logic buildWardTabs()
  - [x] Sửa loadData() loại bỏ hàng tiêu đề Source sheet
- [x] **Kiểm thử sơ bộ:** Tự động hóa và kiểm tra chéo cú pháp JavaScript

## 🛠️ Update Logic (Drafting while Doing)
- Đúc kết trong quá trình phát hiện: Tệp `index.html` của client sử dụng `.filter(Boolean)` sẵn ở cuối chuỗi ánh xạ `.map()` trong hàm `loadData()`, nên việc trả về `null` cho `index === 0` để chặn hàng tiêu đề diễn ra cực kỳ mượt mà và không gây lỗi unhandled TypeError.

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** Dữ liệu phường trong database thực tế có sự không đồng nhất về cách đặt dấu tiếng Việt (ví dụ: "Xuân Hoà" vs "Xuân Hòa", "Hoà Hưng" vs "Hòa Hưng").
- **Nguyên nhân gốc rễ (Root Cause):** Người dùng nhập liệu thủ công bằng các bộ gõ tiếng Việt khác nhau (NFC vs NFD, hoặc vị trí đặt dấu thanh khác nhau trên nguyên âm đôi).
- **Giải pháp phòng ngừa:** Viết hàm chuẩn hóa dấu tiếng Việt `normalizeVietnameseTones` để đưa các biến thể dấu về một dạng thống nhất trước khi so khớp hoặc tìm kiếm chỉ mục ưu tiên.

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm code & Cấu hình:** Khi lọc bỏ dữ liệu rác (như hàng tiêu đề cột), việc kết hợp trả về `null` trong `.map()` và lọc sạch bằng `.filter(Boolean)` là giải pháp tối ưu, giúp bảo toàn chỉ số dòng thô (`targetRowNumber = index + 2`) mà không làm lệch ánh xạ.
- **Kinh nghiệm kiểm thử:** Cần thiết kế các trường hợp kiểm thử cho cả 2 trạng thái lọc: trạng thái mặc định (All) và trạng thái lọc theo Quận (Single/Multi) để đảm bảo không bị sót lỗi logic sắp xếp/gộp danh sách phường tĩnh và phường động.

## Verification Plan

### Manual Verification
- **Test Case 1 (Chặn dòng tiêu đề):** Mở web admin ➔ Xác thực không còn bất kỳ dòng dữ liệu lỗi nào chứa Quận "UAN" hay Phường "phuong".
- **Test Case 2 (Ưu tiên Phường hiển thị tất cả):** Ở chế độ mặc định, danh sách phường hiển thị đúng thứ tự 19 phường nghiệp vụ. Các phường phụ khác được xếp phía sau tự động theo thứ tự bảng chữ cái.
- **Test Case 3 (Lọc Quận cụ thể):** Chọn Quận 3 và Phú Nhuận ➔ Bộ lọc Phường hiển thị đúng danh sách Phường chuẩn của cả hai quận và được sắp xếp đúng thứ tự ưu tiên: Xuân Hoà, Bàn Cờ, Nhiêu Lộc, Cầu Kiệu, Đức Nhuận, Phú Nhuận.

## Files touched
- `index.html` — Cập nhật cấu hình phường tĩnh, bổ sung sắp xếp ưu tiên và loại bỏ hàng tiêu đề Source.
