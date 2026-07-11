---
id: US-075
status: accepted
date: 2026-06-07
size: M
---

# US-075: Giải pháp duy trì phiên đăng nhập Google tối thiểu 1 ngày và Bảo mật mật khẩu Admin

## User story
**As an** Admin (Anh Khang Ngô)
**I want** hệ thống tự động duy trì trạng thái đăng nhập hoặc quyền truy cập Google Sheets/Drive tối thiểu 1 ngày (hoặc vĩnh viễn), đồng thời mật khẩu Admin `trang` phải được bảo mật tuyệt đối không lưu lộ thiên trên URL hay mã nguồn công khai.
**So that** công việc biên tập và đồng bộ bất động sản lên Google Sheets đ�- [x] **Bảo mật mật khẩu Admin (Lớp 1):**
  - [x] Hỗ trợ băm mật khẩu bằng thuật toán SHA-256 một chiều. Không lưu trữ mật khẩu dưới dạng văn bản thường trong file nguồn.
  - [x] Cơ chế kích hoạt ẩn: Nhấp click đủ **5 lần** vào biểu tượng lock hoặc văn bản "🔒 Hệ thống quản trị viên" thì mới kích hoạt hộp thoại nhắc nhập mật khẩu.
  - [x] Cơ chế dọn dẹp URL tức thì (Instant URL Clean-up): Nếu người dùng gõ trực tiếp `?pwd=trang` trên thanh địa chỉ, trang web sẽ xác thực ngầm, lưu phiên Admin và lập tức xóa sạch tham số mật khẩu khỏi URL bar để tránh lưu trong lịch sử trình duyệt hay lộ khi chia sẻ màn hình.
- [ ] **Duy trì phiên Google tối thiểu 1 ngày (Lớp 2):**
  - [ ] Admin có thể lưu thay đổi hoặc xuất bản tin lên Google Sheets bình thường sau hơn 24 giờ kể từ phiên đăng nhập trước đó mà không gặp thông báo "hết hạn phiên" hoặc popup Google Login.
  - [ ] Chuyển đổi Google OAuth2 trên Frontend từ Implicit Flow sang Authorization Code Flow (với `access_type: 'offline'`), thu hồi `refresh_token` từ Google OAuth API, lưu trữ an toàn refresh token ở client dưới dạng HttpOnly cookie (hoặc localStorage) và tự động làm mới access token thông qua Vercel serverless function trung gian `/api/auth/refresh`.
  - [ ] Không gây ảnh hưởng đến dữ liệu cũ, tương thích hoàn toàn trên các trình duyệt Desktop, Mobile (Safari/Chrome iOS & Android) và môi trường Tab ẩn danh (Incognito).

## Solution

### 1. Bảo mật mật khẩu Admin & Kích hoạt ẩn
*   **SHA-256 Hash:** Mã băm của mật khẩu Admin `"trang"` được lưu trữ dưới dạng hằng số tĩnh: `ADMIN_PASSWORD_HASH = 'd555c82a203f56860361a12e52e46b9a8cf6fb0010996f8c2e1751d3b0e12776'`.
*   **Trình xử lý click 5 lần:** Biến đếm `loginClickCount` sẽ tích lũy số lần bấm. Khi đạt giá trị 5, hệ thống mới bật hộp thoại `prompt`.
*   **Dọn URL bằng replaceState / replace:** Lệnh `window.location.replace(newUrl)` được thực thi ngay khi tải trang để chuyển hướng sạch sẽ khỏi các tham số `pwd` và `pw`.

```javascript
// Trích đoạn logic băm và so khớp
async function sha256(message) {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}
```

### 2. Google OAuth2 Refresh Token (Phiên 1 Ngày+)
*   Frontend sử dụng Google Identity Services Code Client (`google.accounts.oauth2.initCodeClient`) để xin mã Code ủy quyền.
*   API backend trên Vercel `/api/auth/token` sẽ dùng Code này và `client_secret` (lưu trong Vercel variables) để đổi lấy `refresh_token` từ Google.
*   Client lưu trữ `refresh_token` trong Cookie/Local. Khi token hết hạn, client gọi ngầm `/api/auth/refresh` để nhận `access_token` mới và ghi đè Google Sheets.

---

## 📋 Implementation Plan

- **Các bước đã triển khai:**
  1. Thay đổi logic kiểm tra mật khẩu Admin sang so khớp chuỗi băm SHA-256 trong [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html).
  2. Thêm trình đếm click 5 lần cho nút Đăng nhập Admin.
  3. Cấu hình tự động lưu phiên Admin vào `localStorage` và xóa tham số mật khẩu khỏi URL Address Bar bằng `window.location.replace` để tránh lặp tải trang.
- **Các bước tiếp theo (OAuth2 Refresh Token):**
  1. Tạo API Endpoint `/api/auth/token` và `/api/auth/refresh` trong thư mục [api/](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/api/).
  2. Cập nhật giao diện Google Sign-in trên client để chuyển sang Authorization Code Flow.
  3. Tích hợp tự động làm mới access token định kỳ bằng refresh token qua Vercel API.

---

## 📝 Task Checklist (TODO)

- [x] **Lớp 1: Bảo mật Mật khẩu Admin & 5-click**
  - [x] Triển khai hàm băm mật khẩu SHA-256 bất đồng bộ trong [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html).
  - [x] Tích hợp bộ đếm click 5 lần vào hàm `triggerAdminAuthPrompt()`.
  - [x] Viết logic instant URL clean-up tự động dọn sạch thanh địa chỉ và lưu session.
- [ ] **Lớp 2: Google OAuth2 Refresh Token (Phiên 1 Ngày+)**
  - [ ] Cấu hình Client-side để gọi Authorization Code Flow và nhận mã Auth Code.
  - [ ] Viết Serverless API `/api/auth/token` và `/api/auth/refresh` trên Vercel.
  - [ ] Tích hợp làm mới access token tự động ngầm khi lưu thay đổi Google Sheets.

## 🛠️ Update Logic (Drafting while Doing)

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
*   **Phát kiến về Web Crypto API:** Vì Web Crypto API hoạt động bất đồng bộ (`async/await`), chúng ta không thể gọi đồng bộ kiểm tra password trên page load. Để giải quyết, ta cho kiểm tra đồng bộ cờ `isAdminSession` trong `localStorage` trước, còn việc kiểm tra tham số `?pwd=` trên URL được đưa vào một Promise chạy bất đồng bộ ngay sau đó để reload trang sạch sẽ.
*   **Sự cố kỹ thuật: Vòng lặp tải trang vô hạn (Infinite Reload Loop):**
    *   *Lỗi:* Khi click hoặc gõ URL chứa `?pwd=trang`, ban đầu sử dụng `window.history.replaceState` để đổi URL hiển thị rồi gọi `window.location.reload()`. Tuy nhiên, trong một số trình duyệt, `reload()` cố tình lấy lại URL nguyên bản gốc của phiên duyệt web trước đó (vẫn có tham số `pwd=trang`), tạo ra vòng lặp vô hạn gây nhấp nháy/reload liên tục.
    *   *Cách khắc phục:* Thay đổi cơ chế từ `replaceState` + `reload()` sang sử dụng trực tiếp **`window.location.replace(newUrl)`**. Lệnh `replace` điều hướng sạch sang URL mới và thay thế trực tiếp vị trí trong lịch sử tab, ngăn hoàn toàn lỗi quay lại URL có mật khẩu và chặn đứt vòng lặp.

---

## Verification Plan

### Manual Verification
1. **Kiểm thử click 5 lần:**
   - Mở web ở chế độ khách: `https://khangngonhapho.github.io/nha-ban/` (màn hình hiển thị thông báo yêu cầu liên hệ).
   - Click thử 1-4 lần vào dòng chữ "🔒 Hệ thống quản trị viên" ở dưới -> Đảm bảo **không** hiển thị prompt.
   - Click lần thứ 5 -> Màn hình prompt yêu cầu nhập mật khẩu xuất hiện.
2. **Kiểm thử SHA-256 & Mật khẩu Admin:**
   - Nhập sai mật khẩu -> Báo lỗi "Sai mật khẩu Admin!" và không kích hoạt Admin.
   - Nhập mật khẩu đúng: `trang` -> Báo "Đăng nhập Admin thành công!", sau đó trang tự reload và hiển thị đầy đủ giao diện Admin (Tab Pool, bộ lọc...).
3. **Kiểm thử Instant URL Clean-up:**
   - Gõ trực tiếp link: `https://khangngonhapho.github.io/nha-ban/?pwd=trang`
   - Kiểm tra: Thanh địa chỉ URL bar ngay lập tức chuyển hướng sạch sẽ về `https://khangngonhapho.github.io/nha-ban/` và chế độ Admin được mở khóa thành công, hoàn toàn **không bị vòng lặp tải trang**.

---

## Files touched
- `index.html` — Triển khai băm mật khẩu, click 5 lần và URL cleanup.
- `docs/stories/_inbox/US-075_duy_tri_session_google.md` — Cập nhật tài liệu User Story.ck thử 1-4 lần vào dòng chữ "🔒 Đăng nhập Admin" ở dưới -> Đảm bảo **không** hiển thị prompt.
   - Click lần thứ 5 -> Màn hình prompt yêu cầu nhập mật khẩu xuất hiện.
2. **Kiểm thử SHA-256 & Mật khẩu Admin:**
   - Nhập sai mật khẩu -> Báo lỗi "Sai mật khẩu Admin!" và không kích hoạt Admin.
   - Nhập mật khẩu đúng: `trang` -> Báo "Đăng nhập Admin thành công!", sau đó trang tự reload và hiển thị đầy đủ giao diện Admin (Tab Pool, bộ lọc...).
3. **Kiểm thử Instant URL Clean-up:**
   - Gõ trực tiếp link: `https://khangngonhapho.github.io/nha-ban/?pwd=trang`
   - Kiểm tra: Thanh địa chỉ URL bar ngay lập tức chuyển thành `https://khangngonhapho.github.io/nha-ban/` và chế độ Admin được mở khóa thành công. Mật khẩu không bị lưu lại trên URL.

---

## Files touched
- `index.html` — Triển khai băm mật khẩu, click 5 lần và URL cleanup.
- `docs/stories/_inbox/US-075_duy_tri_session_google.md` — Cập nhật tài liệu User Story.
