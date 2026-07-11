---
id: US-061
status: accepted
date: 2026-06-03
size: M
---

# US-061: Khắc phục triệt để lỗi hết hạn phiên đăng nhập Google và tự động làm mới token ngầm (Google OAuth Session Timeout Resolution with Auto Silent Refresh)

## User story
**As an** Admin (Anh Khang Ngô)
**I want** hệ thống tự động kiểm tra và làm mới (refresh) token Google OAuth2 ngầm định kỳ hoặc ngay trước khi thực hiện lưu dữ liệu
**So that** tôi không bị gián đoạn công việc, không bị thông báo hết hạn và tuyệt đối không bao giờ bị mất nội dung tin biên soạn (tiêu đề, mô tả) khi đang thao tác lưu.

## Acceptance
- [x] Xây dựng hàm helper `ensureValidGoogleToken()` kiểm tra thời hạn token. Nếu token hết hạn hoặc còn ít hơn 5 phút (300 giây) hiệu lực, tự động làm mới ngầm (Silent Refresh) bằng Google Identity Services (GSI).
- [x] Đồng bộ hóa hàng đợi yêu cầu token: Khi có nhiều cuộc gọi đồng thời tới `ensureValidGoogleToken()` (ví dụ: vừa lưu Source vừa lưu Pool), chỉ kích hoạt duy nhất một lượt yêu cầu OAuth2 ngầm và phân phối token mới cho tất cả các resolvers trong hàng đợi `window.tokenResolvers`.
- [x] Cơ chế Fallback Đăng nhập Chủ động (Interactive Login Fallback): Nếu cuộc gọi Silent Refresh thất bại (do hết hạn phiên Google hoặc bị chặn cookie bên thứ ba), hiển thị hộp thoại `confirm` hỏi người dùng đăng nhập lại. Khi người dùng đồng ý, kích hoạt popup đăng nhập Google tương tác trực tiếp. Sau khi đăng nhập thành công, tự động tiếp tục (resume) và hoàn tất thao tác lưu ban đầu mà không tải lại trang (no page reload) và không làm mất dữ liệu trên form.
- [x] Thiết lập bộ đếm thời gian chạy ngầm (`setInterval` mỗi 5 phút) tự động kiểm tra và làm mới token ngầm nếu thời gian hiệu lực còn lại dưới 15 phút, duy trì trạng thái đăng nhập liên tục nhiều ngày/tuần khi tab trình duyệt mở.
- [x] Tích hợp `await ensureValidGoogleToken()` vào đầu tất cả các hàm tác động dữ liệu hoặc tải dữ liệu bảo mật (`saveSourceChanges`, `saveNewListingFromPool`, `executePullFromPool`, `fetchFacadeImages`).

## Solution

### 1. Cơ cấu làm mới token ngầm & Đăng nhập chủ động
Sử dụng hàng đợi `window.tokenResolvers` để gom tất cả các yêu cầu token phát sinh trong thời gian làm mới token.

#### Hàm `ensureValidGoogleToken()`
```javascript
window.ensureValidGoogleToken = function() {
  return new Promise((resolve, reject) => {
    const token = localStorage.getItem('g_access_token');
    const expiry = localStorage.getItem('g_token_expiry');
    const now = Date.now();
    
    // Nếu token còn hạn trên 5 phút, trả về ngay lập tức
    if (token && expiry && parseInt(expiry, 10) > now + 300 * 1000) {
      return resolve(token);
    }
    
    // Đưa resolver vào hàng đợi chờ xử lý
    window.tokenResolvers = window.tokenResolvers || [];
    window.tokenResolvers.push({ resolve, reject });
    
    // Nếu đã có một tiến trình refresh đang chạy, chỉ cần đợi
    if (window.tokenResolvers.length > 1) {
      return;
    }
    
    const clientId = localStorage.getItem('gClientId');
    if (!clientId) {
      window.tokenResolvers = [];
      reject(new Error("Chưa cấu hình Google Client ID trong Bộ lọc!"));
      return;
    }
    
    if (!gTokenClient) {
      initGoogleAuth();
    }
    
    if (gTokenClient) {
      console.log("Token đã hết hạn hoặc sắp hết hạn. Đang tự động làm mới ngầm...");
      try {
        gTokenClient.requestAccessToken({ prompt: 'none' }); // Silent refresh
      } catch (e) {
        console.warn("Silent refresh failed synchronously, falling back to interactive login:", e);
        promptInteractiveLogin();
      }
    } else {
      window.tokenResolvers = [];
      reject(new Error("Không thể khởi tạo client xác thực Google!"));
    }
  });
};
```

#### Hàm `promptInteractiveLogin()`
```javascript
function promptInteractiveLogin() {
  if (confirm("Phiên đăng nhập Google đã hết hiệu lực. Nhấp OK để liên kết lại tài khoản Gmail và tự động hoàn thành lưu dữ liệu!")) {
    try {
      gTokenClient.requestAccessToken(); // Interactive login (popup)
    } catch (e) {
      console.error("Interactive login failed:", e);
      const resolvers = window.tokenResolvers || [];
      window.tokenResolvers = [];
      resolvers.forEach(r => r.reject(e));
    }
  } else {
    // Người dùng hủy, từ chối toàn bộ yêu cầu đang chờ
    const resolvers = window.tokenResolvers || [];
    window.tokenResolvers = [];
    resolvers.forEach(r => r.reject(new Error("Người dùng từ chối đăng nhập lại")));
  }
}
```

### 2. Cập nhật Callback trong `initGoogleAuth()`
Sửa đổi hàm callback xử lý token để phân biệt giữa:
- **Silent Refresh background thông thường / Manual Login:** Tự động reload data qua `loadData()`.
- **Refresh khi đang Save / Pull:** Chỉ giải quyết (resolve) hàng đợi token để cho phép luồng save tiếp tục ghi đè Google Sheets mà không reload trang gây mất dữ liệu form thô.

```javascript
        gTokenClient = google.accounts.oauth2.initTokenClient({
          client_id: clientId,
          scope: 'https://www.googleapis.com/auth/spreadsheets',
          callback: (tokenResponse) => {
            if (tokenResponse.error !== undefined) {
              console.error("OAuth2 callback error:", tokenResponse.error);
              showGoogleLoginButtonState(false);
              
              // Nếu đang có thao tác save/pull chờ token, thử đăng nhập popup
              if (window.tokenResolvers && window.tokenResolvers.length > 0) {
                promptInteractiveLogin();
              }
              return;
            }
            
            const token = tokenResponse.access_token;
            const expiry = Date.now() + (tokenResponse.expires_in - 60) * 1000;
            localStorage.setItem('g_access_token', token);
            localStorage.setItem('g_token_expiry', expiry);
            localStorage.setItem('isAdminSession', 'true');
            showGoogleLoginButtonState(true);
            document.body.classList.remove('is-locked');
            secureLoadAttempted = false;
            
            // Xử lý các resolvers đang đợi token
            const resolvers = window.tokenResolvers || [];
            window.tokenResolvers = [];
            
            if (resolvers.length > 0) {
              console.log("Token refreshed successfully for pending operations. Resolving...");
              resolvers.forEach(r => r.resolve(token));
            } else {
              // Chỉ loadData nếu không có tác vụ nào đang đợi token (tránh mất form data thô của admin)
              isSecureLoaded = false;
              isDataLoaded = false;
              loadData();
            }
          }
        });
```

### 3. Bộ làm mới định kỳ chạy ngầm
Thực hiện chạy kiểm tra hiệu lực token mỗi 5 phút. Nếu còn hạn < 15 phút, kích hoạt silent refresh ngầm để duy trì session.
```javascript
    // Bộ kiểm tra và làm mới token ngầm định kỳ (US-061)
    setInterval(() => {
      if (!isAdmin) return;
      const token = localStorage.getItem('g_access_token');
      const expiry = localStorage.getItem('g_token_expiry');
      const now = Date.now();
      
      if (token && expiry) {
        const timeRemaining = parseInt(expiry, 10) - now;
        // Nếu token còn hạn dưới 15 phút, làm mới ngầm ngay lập tức
        if (timeRemaining > 0 && timeRemaining < 15 * 60 * 1000) {
          console.log("Token sắp hết hạn trong", Math.round(timeRemaining / 1000), "giây. Đang làm mới ngầm...");
          if (gTokenClient) {
            try {
              gTokenClient.requestAccessToken({ prompt: 'none' });
            } catch (e) {
              console.warn("Làm mới token định kỳ thất bại:", e);
            }
          }
        }
      }
    }, 5 * 60 * 1000); // 5 phút
```

## 📋 Implementation Plan

### Hướng tiếp cận
Chuyển đổi các hàm gọi Google Sheets API (`saveSourceChanges`, `saveNewListingFromPool`, `executePullFromPool`) sang bất đồng bộ (async/await), tự động gọi và lấy token hợp lệ từ `ensureValidGoogleToken()` trước khi thực thi request.

### Các bước triển khai
1. Định nghĩa hàng đợi `window.tokenResolvers` và helper `ensureValidGoogleToken()`, `promptInteractiveLogin()`.
2. Sửa đổi `initGoogleAuth()` để cập nhật logic callback xử lý resolvers.
3. Thiết lập vòng kiểm tra định kỳ `setInterval` ở cuối khối khởi động.
4. Cập nhật `saveSourceChanges()`, `saveNewListingFromPool()`, `executePullFromPool()`, và `fetchFacadeImages()` sang cấu trúc await token.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát code OAuth hiện tại trong `index.html`
  - [x] Thiết kế giải pháp hàng đợi token ngầm và fallback tương tác
- [x] **Triển khai Code:**
  - [x] Viết hàm `ensureValidGoogleToken` và `promptInteractiveLogin` trong `index.html`
  - [x] Cập nhật callback của `initTokenClient` trong `initGoogleAuth`
  - [x] Tích hợp `ensureValidGoogleToken()` vào các hàm lưu và tải dữ liệu
  - [x] Thêm `setInterval` định kỳ 5 phút tự động làm mới ngầm
- [x] **Kiểm thử & Đóng gói:**
  - [x] Kiểm thử kịch bản token hết hạn khi click Lưu xem có tự động làm mới ngầm thành công không
  - [x] Kiểm thử kịch bản silent refresh lỗi xem popup tương tác có bật lên và tự động lưu tiếp không
  - [x] Rà soát và cập nhật `INDEX.md`, `NEXT_SESSION.md`

## Verification Plan

### Manual Verification
1. **Kiểm thử làm mới ngầm (Silent Refresh):**
   - Chỉnh sửa `localStorage.setItem('g_token_expiry', Date.now() + 60 * 1000)` (sắp hết hạn trong 1 phút).
   - Click "Lưu" hoặc thực hiện Curation thay đổi bất kỳ căn nhà nào.
   - Kiểm tra console log: Hệ thống tự gọi silent refresh, nhận token mới và hoàn tất ghi đè Google Sheets thành công mà không hiển thị thông báo lỗi hay popup.
2. **Kiểm thử Đăng nhập chủ động khi mất phiên (Interactive Fallback):**
   - Chỉnh sửa `localStorage.setItem('g_token_expiry', Date.now() - 1000)` (đã hết hạn) và mở một tài khoản Google khác ở tab ẩn danh hoặc thu hồi quyền truy cập ứng dụng.
   - Soạn tin mô tả chi tiết của căn nhà rồi click "Lưu".
   - Hệ thống hiển thị hộp thoại cảnh báo -> Bấm OK -> Popup đăng nhập của Google hiện lên.
   - Sau khi chọn tài khoản và đăng nhập thành công, kiểm tra: Dữ liệu mô tả vừa soạn vẫn giữ nguyên và tự động hoàn thành lưu lên Google Sheets thành công (Toast xanh lá).
3. **Kiểm thử thời gian thực chạy ngầm (Background Sync):**
   - Mở trang Admin, giữ trang hoạt động. Đè thời gian token còn 10 phút hiệu lực.
   - Đợi 5 phút tiếp theo xem log có tự động in ra "Token sắp hết hạn... Đang làm mới ngầm..." và cập nhật lại thời gian hiệu lực mới hay không.

## Files touched
- `index.html` — Cập nhật logic xác thực, lưu và nạp dữ liệu Admin.
