---
id: US-049
status: accepted
date: 2026-05-30
size: M
---

# US-049: Đồng nhất giao diện chi tiết Khách hàng với Admin Preview và bổ sung Sao chép nhanh link gửi khách (Unified Client Detail View & Quick Client Link Copy)

## User story
**As an** Admin / Curator
**I want** the customer's single property detail page to have the exact same interface and layout as the "Customer Preview" section in the Admin panel, and to be able to quickly copy the sharing link of a property without typing customer details
**So that** I can ensure 100% visual and informational consistency before sending listings to clients, and save time by bypassing the customer tracking modal when sending quick links, satisfying KPI 1 (Chính xác thông tin) and KPI 2 (Tốc độ biên tập).

## Acceptance Criteria
- [x] **Đồng nhất giao diện chi tiết Khách hàng (Client Single View):**
  - Giao diện chi tiết của 1 căn nhà khi Khách hàng xem qua link chia sẻ (`?s=SYS-XXXX`) đã khớp hoàn toàn về thiết kế, bố cục, màu sắc, font chữ và các thành phần hiển thị so với phần **"Preview khách hàng"** trong Modal chi tiết của trang Admin.
  - Sử dụng chung cấu trúc grid 8 trường thông tin và hộp mô tả có viền xám, bo góc bo tròn thanh lịch trên nền sáng.
- [x] **Nút Sao chép nhanh link gửi khách (Quick Copy Client Link):**
  - Bổ sung nút **`Copy link nhanh`** vô cùng tinh gọn, không viền bao, không biểu tượng ở góc trên bên phải của modal curation trong trang Admin.
  - Khi click nút này, tự động sinh link dạng `?s=SYS-XXXX` và sao chép trực tiếp vào clipboard, bỏ qua bước nhập thông tin khách hàng (bypassing tracking parameter).
- [x] **Bảo mật và Tự động mở Modal Admin (Secure Auto-Open & Session Persistence):**
  - Khách hàng bình thường mở link `?s=SYS-XXXX` của căn chưa công khai (Pool thô) sẽ bị **chặn an toàn tuyệt đối** và không thấy nút đăng nhập Google.
  - Khi Admin đã từng đăng nhập mở link sạch này, hệ thống nhận diện trình duyệt của Admin thông qua cờ `isAdminSession = 'true'` lưu tại LocalStorage, tự động kích hoạt Silent Refresh làm mới token Google ngầm và tự động mở modal curation (`openPoolS`) của căn đó chỉ trong vòng 1-2 giây.

## Solution

### 1. Đồng nhất layout Khách hàng với Admin Preview
- Chỉnh sửa nhánh `else` (dành cho Public/Customer view) trong hàm `openS()` tại `index.html`.
- Đồng bộ hóa cấu trúc HTML từ bảng 13 trường cũ sang lưới Grid 8 ô phân tách bằng nét đứt tinh tế (`.admin-raw-grid` và `.admin-raw-cell`).
- Định dạng khối mô tả Public với phong cách chuẩn xám bo góc tròn giống hệt giao diện Preview.

### 2. Nút Copy link nhanh tinh gọn (Right-Aligned)
- Thêm container `<div style="margin-bottom: 16px; text-align: right;">` ở đầu phần hiển thị chi tiết của Admin.
- Đặt nút bấm dạng phẳng `Copy link nhanh` bo tròn, không viền, không icon giúp tối ưu hóa không gian hiển thị tối đa.

### 3. Đồng bộ cơ chế Session Admin và Silent Refresh
- Thiết lập cờ `isAdminSession = 'true'` lưu tại `localStorage` ngay khi Admin truy cập qua link mật khẩu `pwd=trang` hoặc đăng nhập thành công.
- Tự động gọi `autoLoginOrSilentRefresh()` bên trong `initGoogleAuth` ngay khi khởi chạy nếu cờ `isAdminSession` là true.
- Trong `finalizeData()`, nếu Admin mở một link sạch `?s=SYS-XXXX` chứa căn thô chưa public, hệ thống tìm trong `POOL_ROWS` và tự động gọi `openPoolS(shareToken)` sau 800ms để bung modal curation.

## 📋 Implementation Plan & Execution
- **Bước 1:** Thay đổi giao diện modal khách hàng để thống nhất 100% với Admin Preview.
- **Bước 2:** Xây dựng nút `Copy link nhanh` căn lề phải gọn gàng, loại bỏ các chi tiết thừa thãi.
- **Bước 3:** Hiện thực hóa logic lưu cờ `isAdminSession` và cơ chế khởi chạy Silent Auto-Login.
- **Bước 4:** Bổ sung hook tự động mở modal `openPoolS` trong `finalizeData`.
- **Bước 5:** Thử nghiệm độc lập và nghiệm thu thực tế.

## Verification Results
- **Safe Block (Incognito):** Đạt. Trình duyệt ẩn danh hoàn toàn bị chặn và hiển thị hộp thoại liên hệ hỗ trợ, không lộ bất kỳ dữ liệu thô nào và không hiển thị nút đăng nhập Google.
- **Admin Session Persistence:** Đạt. Tắt tab, mở lại qua link sạch `?s=SYS-XXXX`, hệ thống tự động nhận diện thiết bị Admin.
- **Silent Token Refresh:** Đạt. Khi giả lập token hết hạn, hệ thống tự động chạy Silent Refresh lấy token Google mới ngầm và bung modal curation thô thành công trong vòng chưa đầy 2 giây.

## Files touched
- [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html)
