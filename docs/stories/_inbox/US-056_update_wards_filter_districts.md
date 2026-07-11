---
id: US-056
status: accepted
date: 2026-05-31
size: S
---

# US-056: Cập nhật danh sách Phường chuẩn từ SQL vào bộ lọc tìm kiếm trên giao diện Web Vercel Admin cho các Quận trọng điểm

## User story
**As an** Admin / Broker Khang Ngô
**I want** bộ lọc Phường (Wards filter) trên giao diện Web Vercel Admin hiển thị đầy đủ và chính xác danh sách các Phường thực tế lấy từ cột `Phường` (cột gốc, không phải Phường cũ) của cơ sở dữ liệu SQL cho 5 quận trọng điểm: Quận 3, Quận 10, Bình Thạnh, Tân Bình, Phú Nhuận
**So that** tôi có thể lọc tìm nhà theo đúng phân khu/phường thực tế của Thien Khoi một cách ổn định, đồng bộ và đầy đủ, ngay cả khi danh sách BĐS hiện tại đang hiển thị trên giao diện chưa bao phủ hết các phường này.

---

## Acceptance
- [x] **Trích xuất danh sách Phường chuẩn từ SQLite:**
  - Xác định danh sách phường duy nhất từ cột `Phuong` (không phải `Phuong_cu_AI`) trong bảng `listings` của SQLite `raw_archive.db` tương ứng với 5 quận trọng điểm.
  - Các phường cụ thể cần được cấu hình tĩnh hoặc động bao gồm:
    - **Quận 3:** Xuân Hòa, Bàn Cờ, Nhiêu Lộc
    - **Quận 10:** Vườn Lài, Hòa Hưng, Diên Hồng
    - **Bình Thạnh:** Gia Định, Bình Thạnh, Thạnh Mỹ Tây, Bình Quới, Bình Lợi Trung
    - **Tân Bình:** Tân Sơn Hòa, Tân Sơn Nhất, Tân Hòa, Bảy Hiền, Tân Bình, Tân Sơn
    - **Phú Nhuận:** Phú Nhuận, Cầu Kiệu, Đức Nhuận
- [x] **Bổ sung bộ lọc cố định/tĩnh trên Web Vercel Admin:**
  - Cập nhật hàm `buildWardTabs()` trong `index.html` để khi người dùng chọn một trong 5 quận trên, thay vì tạo danh sách phường động từ `DATA` hiện tại (vốn có thể bị thiếu nếu dữ liệu tải về chưa đủ), hệ thống sẽ hiển thị đầy đủ danh sách các phường chuẩn đã được cấu hình ở trên.
  - Đảm bảo khi bấm chọn phường, logic lọc `applyFilter()` hoạt động chính xác dựa trên trường `p.phuong`.
- [x] **Hỗ trợ đa chọn và xóa bộ lọc mượt mà:**
  - Người dùng có thể chọn một hoặc nhiều phường cùng lúc (cơ chế multi-select sẵn có).
  - Bộ lọc hoạt động nhanh, cập nhật thống kê BĐS ngay lập tức trên giao diện.

---

## Solution (Proposed)

### 1. Khai báo Ward Map tĩnh trong `index.html`:
Bổ sung một hằng số map tĩnh chứa danh sách các phường chuẩn theo mã quận:
```javascript
const STATIC_WARD_MAP = {
  q3: ["Xuân Hòa", "Bàn Cờ", "Nhiêu Lộc"],
  q10: ["Vườn Lài", "Hòa Hưng", "Diên Hồng"],
  bt: ["Gia Định", "Bình Thạnh", "Thạnh Mỹ Tây", "Bình Quới", "Bình Lợi Trung"],
  tb: ["Tân Sơn Hòa", "Tân Sơn Nhất", "Tân Hòa", "Bảy Hiền", "Tân Bình", "Tân Sơn"],
  pn: ["Phú Nhuận", "Cầu Kiệu", "Đức Nhuận"]
};
```

### 2. Cập nhật `buildWardTabs()` sử dụng STATIC_WARD_MAP:
```javascript
function buildWardTabs() {
  let wards = [];
  
  // Nếu chỉ chọn 1 quận và quận đó nằm trong bản đồ phường tĩnh
  if (selDistricts.size === 1) {
    const selectedDistrict = [...selDistricts][0];
    if (STATIC_WARD_MAP[selectedDistrict]) {
      wards = [...STATIC_WARD_MAP[selectedDistrict]];
    }
  }
  
  // Fallback về tạo động nếu chọn nhiều quận hoặc quận không có map tĩnh
  if (wards.length === 0) {
    const pool = selDistricts.size ? DATA.filter(p => selDistricts.has(p.q)) : DATA;
    wards = [...new Set(pool.map(p => p.phuong).filter(w => w && w !== '-'))].sort();
  }
  
  const wt = document.getElementById('wardTabs');
  const wl = document.getElementById('wardLbl');
  if (!wards.length) { wt.classList.remove('has-wards'); wl.style.display = 'none'; return; }
  wl.style.display = 'block';
  wt.innerHTML = `<button class="tab ${selWards.size === 0 ? 'on' : ''}" data-val="all" onclick="tWard('all')">Tất cả</button>`
    + wards.map(w => `<button class="tab ${selWards.has(w) ? 'on' : ''}" data-val="${w}" onclick="tWard('${w}')">${w}</button>`).join('');
  wt.classList.add('has-wards');
}
```

---

## 📋 Implementation Plan
- **Bước 1**: Khai báo cấu trúc dữ liệu `STATIC_WARD_MAP` trong phần cấu hình của `index.html`.
- **Bước 2**: Sửa đổi hàm `buildWardTabs()` để ưu tiên lấy từ `STATIC_WARD_MAP` khi chọn đơn quận, giúp bộ lọc hiển thị đầy đủ phường mà không bị phụ thuộc vào dữ liệu hiển thị hiện tại.
- **Bước 3**: Kiểm tra lại hàm `applyFilter()` để đảm bảo so khớp chính xác giá trị `p.phuong` của BĐS với các tab phường được chọn.

---

## Files touched
- `index.html` — Cập nhật cấu hình phường tĩnh và logic hiển thị tab phường
- `docs/stories/US-056_update_wards_filter_districts.md` — [NEW] Tài liệu hóa câu chuyện người dùng

---

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** Cột dữ liệu `Phuong` (Phường) cào về từ hệ thống gốc của Thiên Khôi chứa các phân khu nội bộ riêng biệt (Ví dụ: `Bàn Cờ`, `Nhiêu Lộc` cho Q.3) thay vì tên phường hành chính số chính thức của nhà nước, gây nhầm lẫn khi thiết lập bộ lọc tĩnh nếu không đối chiếu kỹ.
- **Nguyên nhân gốc rễ (Root Cause):** Hệ thống Thiên Khôi phân chia khu vực quản lý và lưu trữ dữ liệu theo các vùng môi giới thực tế (phân khu cổ/truyền thống) trong cột Phường gốc của họ, yêu cầu so khớp chính xác từng ký tự chữ hoa chữ thường.
- **Giải pháp phòng ngừa:** Trích xuất trực tiếp danh sách phường từ SQLite thực tế để đảm bảo các giá trị tĩnh khai báo trong `STATIC_WARD_MAP` khớp hoàn hảo 100% với chuỗi ký tự trong cơ sở dữ liệu, tránh hiện tượng bộ lọc hiển thị nhưng không tìm thấy BĐS nào do lệch chữ hoa chữ thường (Ví dụ: `Gia Định` vs `Gia định`).

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm lập trình:** Khi người dùng cung cấp danh sách phân khu ưu tiên hiển thị, hãy tôn trọng và giữ nguyên thứ tự sắp xếp tĩnh do họ định nghĩa (loại bỏ cơ chế `.sort()` tự động). Điều này giúp người dùng dễ dàng đưa các phân khu trọng điểm có lượng giao dịch lớn lên đầu hàng bộ lọc thay vì bắt buộc phải sắp xếp theo thứ tự chữ cái ABC.
- **Kinh nghiệm kiểm thử:** Luôn kiểm tra chéo độ khớp của các chuỗi ký tự trong cột `Phường` với dữ liệu thực tế bằng các đoạn script Python kiểm thử nhanh trước khi đóng băng cấu hình.
