# 🏛️ Đánh Giá Kiến Trúc US-125 (Transformation Manager Review)

Tài liệu này đánh giá giải pháp kỹ thuật của **US-125** (Tự động đăng nhập và tự động cuộn trang Thiên Khôi) để đảm bảo tính nhất quán với cấu trúc modular và các nguyên tắc bền vững mới thiết lập của dự án **BDS-KhangNgo**.

---

## 🔍 Đánh Giá Điểm Nghẽn & Giải Pháp Kỹ Thuật

### 1. Vấn Đề Cookie HttpOnly & Quyền Hạn
* **Rủi ro**: `TKG_accessToken` và `TKG_refreshToken` có khả năng được cấu hình là `HttpOnly` từ phía server Thiên Khôi. Nếu là `HttpOnly`, mã JavaScript chạy tại Content Script (`content.js`) sẽ **không thể** đọc hoặc ghi các cookie này qua `document.cookie`.
* **Giải pháp kiến trúc**:
  * **Không** đọc/ghi cookie trực tiếp ở Content Script.
  * Mọi hoạt động truy xuất hoặc ghi đè token phải được chuyển giao hoàn toàn cho Service Worker (`background.js`) thông qua API chuyên dụng của Chrome: `chrome.cookies.get` và `chrome.cookies.set`.
  * **Yêu cầu bổ sung**: Manifest bắt buộc phải khai báo quyền `"cookies"` và host permission cho cả domain API `"https://backend.thienkhoi.com/*"`.

### 2. Khai Báo Host Permissions & CORS trong Manifest
* **Rủi ro**: Việc gọi API làm mới token từ phía Client có thể bị chặn bởi cơ chế CORS nếu không khai báo đúng.
* **Giải pháp**: Cấu hình `manifest.json` bắt buộc phải bao quát 3 tên miền sau:
  ```json
  "host_permissions": [
    "https://data.thienkhoi.com/*",
    "https://proptech.thienkhoi.com/*",
    "https://backend.thienkhoi.com/*"
  ]
  ```
  *(Thiếu `backend.thienkhoi.com` sẽ khiến lệnh gọi API làm mới token bị trình duyệt chặn đứng)*

### 3. Tương Thích Với React State ở Trang Đăng Nhập
* **Rủi ro**: Trang đăng nhập của Thiên Khôi được xây dựng bằng Next.js/React. Nếu tiện ích mở rộng chỉ gán giá trị thô dạng `input.value = "..."`, React sẽ không cập nhật State bên trong (Virtual DOM), dẫn đến lỗi biểu mẫu rỗng khi bấm Đăng nhập.
* **Giải pháp**: Sử dụng cơ chế gán giá trị đặc biệt để kích hoạt hàm setter gốc của trình duyệt và gửi sự kiện sủi bọt (bubbling event) cho React:
  ```javascript
  function setReactInputValue(inputEl, value) {
      const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
      nativeSetter.call(inputEl, value);
      const event = new Event('input', { bubbles: true });
      inputEl.dispatchEvent(event);
  }
  ```

### 4. Cuộn Trang Thông Minh & Tự Ngắt
* **Rủi ro**: Trang danh sách của Thiên Khôi có chứa nhiều khung cuộn phụ (ví dụ: Sidebar danh mục). Nếu dùng `window.scrollTo` thô có thể không kích hoạt được bộ cuộn của khung chứa danh sách thực tế.
* **Giải pháp**:
  * Thực hiện cuộn song song cả cửa sổ chính (`window`) và toàn bộ các phần tử khớp lớp `.overflow-auto`, `.overflow-y-auto` hoặc `.custom-scrollbar`.
  * Đếm tổng số thẻ hàng (`tr[id^="tr_"]` hoặc thẻ card đại diện) trước và sau khi cuộn.
  * Dùng cơ chế đếm số lần thử cuộn tối đa (tối đa 3 lần) nếu không phát hiện số lượng nhà tăng thêm để tự động ngắt interval, bảo vệ tài nguyên trình duyệt.

---

## 🏁 Kết Luận & Khuyến Nghị Từ Transformation Manager

> [!IMPORTANT]
> **Khuyến Nghị**: Giải pháp kỹ thuật hoàn toàn khả thi và không xung đột với bất kỳ module backend Python nào vừa tái cấu trúc. Tiện ích mở rộng hoạt động hoàn toàn ở tầng Client-side độc lập.

**Kế hoạch được phê duyệt để triển khai tiếp bước code (EXTRACT/WIRE) sau khi PO đồng ý.**
