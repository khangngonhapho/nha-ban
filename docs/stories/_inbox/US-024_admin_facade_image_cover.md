---
id: US-024
status: accepted
date: 2026-05-24
size: XL
---

# US-024: Bảo mật hình ảnh mặt tiền Admin bằng Google OAuth2 & Silent Auto-Login

## User story
**As an** Admin (anh Khang)
**I want** lấy ảnh mặt tiền làm hình đại diện hiển thị trên card danh sách khi tôi đăng nhập Admin
**So that** dễ dàng nhận diện và thẩm định BĐS trực quan, nhưng khách xem hoặc share link vẫn không thấy được ảnh mặt tiền để bảo mật tuyệt đối nguồn hàng (số nhà).

## Acceptance
- [x] Khi đăng nhập chế độ Admin (`isAdmin === true`), card danh sách hiển thị ảnh đại diện lấy từ cột `Hình Mặt Tiền` (cột AM).
- [x] Khi Khách xem (link share hoặc chế độ public), card danh sách hiển thị ảnh đại diện thông thường (`anh_1`), tuyệt đối không thể xem được ảnh mặt tiền.
- [x] Triệt tiêu vĩnh viễn lỗ hổng rò rỉ số nhà qua file Public công khai.
- [x] Hỗ trợ duy trì phiên đăng nhập Admin tự động lên đến nhiều tuần/tháng để tối ưu hóa trải nghiệm sử dụng.

## Solution

> [!note]- Configuration
> - **Google OAuth Client ID** mặc định:
>   `1088195961071-25r6rpvsfmoudqokb75u0m2ugu8na0v0.apps.googleusercontent.com`
> - Biến lưu trữ `localStorage`:
>   `gClientId` (lưu Client ID), `g_access_token` (Access token tạm), `g_token_expiry` (Thời gian hết hạn).
> - File Private gốc:
>   ID: `1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE`
>   Sheet: `Source` (Range: `D2:AM`)
> - OAuth Scope yêu cầu:
>   `https://www.googleapis.com/auth/spreadsheets.readonly`

> [!note]- Input
> - Lệnh gọi endpoint API trung gian:
>   `fetch('/api/get-facade-images')`
> - Header bắt buộc:
>   `Authorization: Bearer <access_token>`

> [!note]- Output / Format
> - Response từ Google Sheets REST API dạng JSON chứa các giá trị dải ô `D2:AM`:
>   ```json
>   {
>     "values": [
>       ["SYSID-001", "...", "...", "https://drive.google.com/file/d/img1_url"],
>       ["SYSID-002", "...", "...", "https://drive.google.com/file/d/img2_url"]
>     ]
>   }
>   ```

> [!note]- Key logic
> - **Thiết kế tuần tự bảo mật đa lớp qua Server-side Middleware:**
>   ```mermaid
>   sequenceDiagram
>       autonumber
>       actor Admin as Admin (Trình duyệt)
>       participant Vercel as Server Vercel (/api/get-facade-images)
>       participant Google as Google Sheets REST API (File Private)
> 
>       Admin->>Admin: Tải trang & Khởi chạy Silent Auto-Login
>       alt Token hợp lệ trong LocalStorage
>           Note over Admin: Tái sử dụng Token lập tức
>       else Token hết hạn hoặc chưa có
>           Admin->>Admin: Âm thầm gửi Silent Request (prompt: 'none')
>           Admin-->>Admin: Nhận Access Token mới tự động
>       end
>       
>       Admin->>Vercel: Gửi request fetch ảnh mặt tiền (Kèm Token)
>       Note over Vercel: Dùng ID Private giấu kín trên Server để query
>       Vercel->>Google: Fetch dải ô Source!D2:AM (Kèm Bearer Token)
>       
>       alt Gmail được cấp quyền truy cập
>           Google-->>Vercel: Trả về mảng dữ liệu ảnh mặt tiền & ID nhà
>           Vercel-->>Admin: Trả về JSON sạch liên kết ảnh mặt tiền
>           Admin->>Admin: Merge khớp ID và render card ảnh mặt tiền thực tế
>       else Tài khoản lạ / Không có quyền
>           Google-->>Vercel: Trả lỗi 403 Forbidden
>           Vercel-->>Admin: Chặn truy cập an toàn
>       end
>   ```
> - **Serverless Function xử lý ở máy chủ Vercel (`api/index.js`):**
>   Chặn bắt request, lấy token từ Header, gọi trực tiếp lên Google Sheets API của file Private bằng ID giấu kín để bảo mật 100% trước người dùng F12 ở client.
> - **Cơ chế Silent Auto-Login (`prompt: 'none'`):**
>   Nếu token hết hạn, hệ thống chạy ngầm Silent Request để lấy Access Token mới mà không hiển thị popup và không cần Admin phải click chuột.

## Verification Plan

> [!check]- Manual Verification
> 1. **Kiểm thử đăng nhập Admin:** Truy cập bằng `?pwd=trang` $\rightarrow$ Thấy nút Google Login nền trắng. Click đăng nhập và chọn Gmail được phân quyền $\rightarrow$ Nút chuyển sang xanh lá báo "Đã liên kết Gmail", toàn bộ ảnh đại diện trên card đổi sang ảnh mặt tiền thật có số nhà.
> 2. **Kiểm thử duy trì phiên:** Tải lại trang (F5) $\rightarrow$ Xác nhận ảnh mặt tiền hiển thị ngay lập tức không cần đăng nhập lại.
> 3. **Kiểm thử Silent Auto-Login:** Xóa token trong `localStorage` và F5 $\rightarrow$ Hệ thống tự động gửi Silent Request dưới background để lấy token mới và hiển thị ảnh mặt tiền mượt mà không có bất kỳ popup nào.
> 4. **Kiểm thử Khách hàng:** Truy cập bằng link khách hoặc link chia sẻ $\rightarrow$ Xác nhận ảnh mặt tiền bị ẩn hoàn toàn, card fallback về ảnh public (`anh_1`), F12 Inspect hoàn toàn không có bất kỳ ID file Private hay URL ảnh nhạy cảm nào.

## Files touched
- `index.html` — [Frontend UI Card & Client OAuth logic]
- `api/index.js` — [Serverless secure middleware proxy]
