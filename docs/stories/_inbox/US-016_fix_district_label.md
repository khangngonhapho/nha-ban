---
id: US-016
status: done
date: 2026-05-21
size: S
---

# US-016: Fix hiển thị tên quận TB/PN/BT/GV — card và modal

## User story
**As a** *Khách hàng xem danh sách nhà*
**I want** *thấy tên quận đầy đủ (Tân Bình, Phú Nhuận, Bình Thạnh, Gò Vấp) trên card và trang chi tiết*
**So that** *thông tin hiển thị rõ ràng, không bị viết tắt "TB", "PN"*

## Acceptance
- [x] Card hiển thị "Q.Phú Nhuận" thay vì "Q.PN"
- [x] Card hiển thị "Q.Tân Bình" thay vì "Q.TB"
- [x] Modal chi tiết hiển thị "Phú Nhuận", "Tân Bình" thay vì "PN", "TB"
- [x] Filter theo quận vẫn hoạt động đúng (p.q không đổi)
- [x] Các quận số (Q.3, Q.10) không bị ảnh hưởng

## Root cause
`ql: cleanQ.toUpperCase()` → trả về "PN", "TB" cho quận chữ viết tắt.
Cần map sang tên đầy đủ.

## Solution

```javascript
// Thêm constant trước fullList map:
const QUAN_FULL = { pn: 'Phú Nhuận', tb: 'Tân Bình', bt: 'Bình Thạnh', gv: 'Gò Vấp' };

// Sửa line ql trong data mapping:
ql: QUAN_FULL[cleanQ.toLowerCase()] || cleanQ.toUpperCase(),
```

## Files touched
- `index.html` — thêm `QUAN_FULL` constant, sửa dòng `ql` trong data mapping

---

## Cập nhật sửa lỗi mất tin Phú Nhuận / Tân Bình & Đơn giản hóa hiển thị (2026-05-25)

### 1. Nguyên nhân (Root Cause)
Do người dùng nhập liệu trên Google Sheet để trống hoàn toàn cột **Quận (Cột G / index 6)** đối với các căn Phú Nhuận và Tân Bình, và chỉ điền các tên Phường đặc thù vào **Cột H** (như `"Phú Nhuận"`, `"Cầu Kiệu"`, `"Tân Sơn Nhất"`, `"Tân Hòa"`).
- Cơ chế fallback nhận diện Quận tự động trước đó trong `index.html` chỉ tìm kiếm từ khóa `"phú nhuận"`, `"pn"`, `"tân bình"`, `"tb"` trong cột `Phường` hoặc `Tiêu đề`.
- Vì các tên phường như `"Cầu Kiệu"`, `"Tân Sơn Nhất"`, `"Tân Hòa"` không chứa các từ khóa này, logic fallback không khớp được quận, làm cho trường quận (`q`) bị `undefined`/trống, khiến cho các tin này bị ẩn hoàn toàn khỏi danh sách hoặc các tab lọc Phú Nhuận / Tân Bình.

### 2. Định hướng Kiến trúc Bền vững (Architectural Decision)
**Cảnh báo:** Việc ánh xạ các phường đặc thù để tự động nhận dạng quận trên client-side JS (như hardcode `cầu kiệu` -> `PN`, `tân sơn nhất` -> `TB`) là một giải pháp tình thế, **không bền vững** lâu dài vì số lượng phường rất nhiều, dễ trùng lặp giữa các quận (ví dụ: Phường 1, Phường 2) và yêu cầu cập nhật code liên tục khi có phường mới.
* **Quy chuẩn bền vững:** Cột **Quận (Cột G)** trên Google Sheet luôn cần được điền đầy đủ và chính xác mã quận viết tắt (ví dụ: `PN`, `TB`, `3`, `10`, `BT`, `GV`). Khi đó, client sẽ trực tiếp phân loại theo giá trị trong sheet mà không cần dùng đến logic fallback đoán quận từ phường.

### 3. Giải pháp hiển thị & Tìm kiếm nâng cao (Simplified Display & Enhanced Search)
Theo yêu cầu mới của người dùng, giao diện được đơn giản hóa và tối ưu như sau:
* **Tên hiển thị tinh giản:** Bỏ việc ánh xạ tên đầy đủ bằng `QUAN_FULL` trên card và chi tiết. Thay vào đó, hiển thị ngắn gọn dưới dạng mã viết tắt (ví dụ: `Q.PN`, `Q.TB`, `Q.3`, `Q.10`, `Q.BT`, `Q.GV`) bằng cách gán `ql: cleanQ.toUpperCase()`.
* **Tìm kiếm thông minh (Enhanced Search):** Cập nhật hàm `getFiltered()` trong `index.html` để hỗ trợ tìm kiếm linh hoạt. Khách hàng gõ đầy đủ tên quận có dấu như `"Phú Nhuận"`, `"Tân Bình"`, `"Quận 3"`... hoặc viết tắt `"PN"`, `"TB"`, `"q3"`... thì hệ thống vẫn nhận diện và lọc ra chính xác các căn tương ứng:
```javascript
          const qMatch = p.q.toLowerCase().includes(sv) || 
                         p.ql.toLowerCase().includes(sv) ||
                         (sv === 'phú nhuận' && p.q === 'pn') ||
                         (sv === 'tân bình' && p.q === 'tb') ||
                         (sv === 'bình thạnh' && p.q === 'bt') ||
                         (sv === 'gò vấp' && p.q === 'gv') ||
                         (sv === 'quận 3' && p.q === 'q3') ||
                         (sv === 'quận 10' && p.q === 'q10');
```
