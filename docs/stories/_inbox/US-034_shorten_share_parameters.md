---
id: US-034
status: accepted
date: 2026-05-25
size: S
extends: US-028, US-033
---

# US-034: Tối ưu hóa & Rút ngắn Tham số c khi tạo link gửi khách hàng

## User story
**As an** *Admin / PO*  
**I want** *rút ngắn tối đa giá trị của tham số định danh khách hàng `c` khi chia sẻ liên kết*  
**So that** *đường dẫn chia sẻ (URL) gửi cho khách hàng gọn gàng, tinh tế và chuyên nghiệp hơn, giảm thiểu nguy cơ vượt quá giới hạn ký tự khi chia sẻ trên các nền tảng chat như Zalo, Messenger.*  

## Acceptance
- [ ] **Nén chuỗi thông tin khách hàng phía Client-side:**
  - Thay đổi ký tự phân tách ba thành phần `cName`, `cNote`, `cTitle` từ `" | "` (khoảng trắng - pipe - khoảng trắng) thành `"|"` (chỉ duy nhất ký tự pipe).
  - Loại bỏ hoàn toàn các trường dữ liệu trống ở đuôi (trailing empty fields) trước khi nén Base64:
    - Nếu chỉ có `cName`: chuỗi thô chỉ là `cName` (không có pipe).
    - Nếu có `cName` và `cNote` nhưng không có `cTitle`: chuỗi thô là `cName|cNote` (1 pipe).
    - Nếu có `cName` và `cTitle` nhưng không có `cNote`: chuỗi thô là `cName||cTitle` (2 pipes).
    - Nếu có đầy đủ cả 3: chuỗi thô là `cName|cNote|cTitle` (2 pipes).
- [ ] **Giải mã tương thích ngược 100% (Backward Compatibility):**
  - Cả phía Client-side (`index.html`) và Server-side (`api/index.js`) phải hỗ trợ phân tách bằng ký tự `"|"` và tự động loại bỏ các khoảng trắng thừa ở mỗi phần tử (sử dụng `.trim()`).
  - Đảm bảo toàn bộ các liên kết cũ (đã tạo với định dạng phân tách `" | "`) vẫn giải mã và hoạt động hoàn hảo mà không bị crash hay hiển thị sai lệch thông tin.

## Solution

> [!note]- Input
> - Giá trị nhập từ các ô `#linkCustName`, `#linkCustNote`, và `#linkCustTitle` trong Modal Tạo Link.

> [!note]- Output / Format
> - Tham số `c` trên URL được rút ngắn đáng kể (tiết kiệm từ 8 đến 12 ký tự Base64 trong các trường hợp thông thường).

> [!note]- Key logic
> - **Mã hóa (Client-side):**
>   ```javascript
>   let parts = [cName];
>   if (cTitle) {
>     parts.push(cNote || "");
>     parts.push(cTitle);
>   } else if (cNote) {
>     parts.push(cNote);
>   }
>   const compactCustomerString = parts.join('|');
>   ```
> - **Giải mã (Client & Server):**
>   ```javascript
>   const parts = decoded.split("|").map(p => p.trim());
>   const cName = parts[0];
>   const cNote = parts[1] || "";
>   const cTitle = parts[2] || "";
>   ```

## Verification Plan

> [!check]- Manual Verification
> 1. **Kiểm tra tạo link gọn (Chỉ nhập Tên khách):**
>    * Nhập Tên khách: `"Anh Hùng"`.
>    * **Xác nhận:** Link sinh ra chứa tham số `c` cực kỳ ngắn (`c=QW5oIEjDuW5n` thay vì `c=QW5oIEjDuW5nIHwgIHwg`).
>    * Truy cập link ở chế độ khách: Lời chào và tiêu đề hiển thị chính xác.
> 2. **Kiểm tra tạo link gọn (Nhập Tên + Tiêu đề):**
>    * Nhập Tên: `"Anh Hùng"`, Tiêu đề: `"Biệt thự Q3"`.
>    * **Xác nhận:** Chuỗi thô là `"Anh Hùng||Biệt thự Q3"`, Base64 nén gọn, không chứa khoảng trắng thừa.
>    * Truy cập link ở chế độ khách: Tiêu đề đổi thành `"Biệt thự Q3"`.
> 3. **Kiểm tra tương thích ngược (Backward Compatibility):**
>    * Truy cập một liên kết cũ có `c` mã hóa từ `"Anh Hùng | VIP Q3 | Biệt thự Quận 3"`.
>    * **Xác nhận:** Trang web giải mã bình thường, hiển thị đúng `"Anh Hùng"`, ghi chú `"VIP Q3"` và tiêu đề `"Biệt thự Quận 3"`.

## Files touched
- `index.html` — Cập nhật bộ mã hóa gọn trong `executeGenerateLink()` và bộ giải mã tương thích ngược ở đầu thẻ `<script>`.
- `api/index.js` — Cập nhật bộ giải mã Server-side Vercel tương thích ngược để tiêm dynamic meta tags chính xác.
