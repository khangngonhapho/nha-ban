---
id: US-094A2
status: accepted
date: 2026-06-15
size: M
---

# US-094A2: Xây dựng Lego Core State Store & Tải dữ liệu

## User story
**As a** Developer  
**I want** tách biệt cơ chế quản lý trạng thái (State Store) và luồng tải dữ liệu (Google Sheets/Auth) ra tệp lego_core.js độc lập  
**So that** loại bỏ hoàn toàn sự phụ thuộc chéo (Circular Dependency) giữa các module Frontend, làm sạch mã nguồn index.html và thiết lập luồng giao tiếp hướng sự kiện (Event-Driven) an toàn.

## Acceptance
- [x] Tạo tệp `static/js/lego_core.js` định nghĩa đối tượng toàn cục `window.LegoState` quản lý trạng thái tập trung (`DATA`, `POOL_ROWS`, `isAdmin`, `isTokenValid`, `gCodeClient`, v.v.).
- [x] Trích xuất toàn bộ luồng tải dữ liệu (`loadData`, `loadPublicDataFallback`) và silent login Google sang `lego_core.js` hoạt động độc lập với DOM/Render.
- [x] Giao tiếp thuần túy qua mô hình Event-Driven: Khi dữ liệu nạp thành công, store phát sự kiện `"rawDataLoaded"`. Tệp `index.html` đăng ký lắng nghe sự kiện này để chạy tiếp hàm dựng giao diện (`finalizeData`) mà không gọi trực tiếp từ store.
- [x] Đảm bảo cơ chế đăng nhập Admin, lưu/refresh token Google OAuth hoạt động ổn định và chính xác trên cả Local và Production sau khi tách.

## Solution

### 1. Thiết kế LegoState Store
Đối tượng `window.LegoState` được định nghĩa trong `static/js/lego_core.js` theo mô hình Event-Driven thuần túy:

```javascript
window.LegoState = {
  // Trạng thái (State)
  DATA: [],
  POOL_ROWS: [],
  isAdmin: false,
  isTokenValid: false,
  gCodeClient: null,
  isSecureLoaded: false,
  isDataLoaded: false,
  secureLoadAttempted: false,
  tokenResolvers: [],

  // Hệ thống Sự kiện (Event System)
  events: {},
  on(event, callback) {
    if (!this.events[event]) this.events[event] = [];
    this.events[event].push(callback);
  },
  emit(event, data) {
    if (this.events[event]) {
      this.events[event].forEach(cb => cb(data));
    }
  },

  // Setters & Actions
  setRawData(data) {
    this.DATA = data;
    this.isDataLoaded = true;
    this.emit('rawDataLoaded', data);
  },
  
  setAdminStatus(isAdmin, isTokenValid) {
    this.isAdmin = isAdmin;
    this.isTokenValid = isTokenValid;
    this.emit('authStatusChanged', { isAdmin, isTokenValid });
  }
};
```

### 2. Tách biệt cơ chế Google Auth & Tải dữ liệu
- Di chuyển `initGoogleAuth`, `handleGoogleLoginClick`, `loadData`, và `loadPublicDataFallback` vào `lego_core.js`.
- Bất kỳ chỗ nào trong logic tải dữ liệu trước đây gọi trực tiếp đến hàm render hoặc cập nhật DOM (ví dụ: `finalizeData(fullList)`, `showError(...)`, `showGoogleLoginButtonState(...)`) sẽ được chuyển đổi sang việc phát sự kiện hoặc gọi thông qua các hàm đăng ký hooks của client (hoặc gọi qua callback đăng ký động).
- Đăng ký lắng nghe sự kiện trong `index.html` để nhận dữ liệu và cập nhật UI tương thích ngược.

---

## 📋 Implementation Plan
- **Cách tiếp cận:** Di cư cơ học logic quản lý dữ liệu và phiên đăng nhập sang một thư viện JavaScript riêng biệt, đăng ký các callback UI thông qua hooks toàn cục của `LegoState` để đảm bảo độ tương thích ngược hoàn hảo trong quá trình refactoring từng bước.
- **Các bước triển khai:**
  1. Tạo tệp `static/js/lego_core.js` và chuyển các biến/hàm core liên quan đến Auth & Data Load sang tệp này.
  2. Cập nhật `index.html` để nạp tệp `static/js/lego_core.js`.
  3. Kết nối các hàm dựng giao diện (`finalizeData`, `showError`, v.v.) trong `index.html` làm các listener lắng nghe sự kiện của `LegoState`.
  4. Chạy bộ E2E Playwright để xác minh giao diện và chức năng đăng nhập hoạt động chuẩn xác.

---

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Phân tích vùng code Auth & Data Load trong `index.html` (dòng 1558-1960 và 4280-4395)
  - [x] Chốt thiết kế API cho `LegoState` Store
- [x] **Triển khai Code:**
  - [x] Tạo tệp `static/js/lego_core.js` và copy logic Auth/Data Load
  - [x] Sửa đổi mã nguồn `index.html` để nạp `lego_core.js` và đăng ký listener sự kiện
  - [x] Xử lý các điểm tương tác DOM/UI từ bên trong logic nạp dữ liệu cũ sang cơ chế callback/event
- [x] **Kiểm thử & Bàn giao:**
  - [x] Chạy bộ kiểm thử E2E Playwright đa thiết bị local đạt 100% PASS
  - [x] Merge code vào `main` và push deploy Live lên Production
  - [x] Báo cáo PO kiểm thử đăng nhập Admin trên môi trường Live

---

## 🛠️ Update Logic (Drafting while Doing)
*(Sẽ cập nhật nhật ký debug và kết quả chạy test nháp trong quá trình làm)*

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:** *[Chưa ghi nhận]*

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- **Script kiểm thử thô / nháp đã chạy:** *[Chưa chạy]*

## 🧠 Retro, Lessons Learned & Good Practices
- **Tương thích ngược qua Getter/Setter**: Sử dụng `Object.defineProperty` để thiết lập getters/setters toàn cục trên `window` ánh xạ sang `LegoState` giúp tách biệt hoàn toàn dữ liệu và logic đăng nhập mà không cần sửa đổi hàng nghìn dòng render/filter UI cũ trong `index.html`. Đây là phương pháp tối ưu cho refactor tiệm tiến.
- **silent login & GSI API Client**: Luồng đăng nhập ngầm và tự động làm mới token cần được xử lý cẩn thận, đảm bảo script GSI (`accounts.google.com/gsi/client`) được tải thành công trước khi khởi tạo client.
- **Event-Driven Architecture**: Mô hình phát sự kiện (Pub/Sub) giúp giảm thiểu hoàn toàn sự phụ thuộc chéo (circular dependency) giữa store dữ liệu và các engine render/bộ lọc giao diện.

---

## Verification Plan

### Automated Tests (BẮT BUỘC - Desktop & Mobile)
- **Script kiểm thử chính:** [test_e2e_curator.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_e2e_curator.py)
- **Lệnh chạy test:** `python scratch/test_e2e_curator.py`
- **Kịch bản test:**
  1. Load trang chủ trên cả 2 viewport Desktop và Mobile để đảm bảo dữ liệu BĐS từ Google Sheets (chế độ Public) vẫn hiển thị và phân trang bình thường.
  2. Xác minh không có lỗi Javascript xuất hiện ở tab Console liên quan đến việc nạp `LegoState`.

### Manual Verification
- Mở Web Admin local và Live, thử click đăng nhập Google Admin, thực hiện silent refresh và xác minh dữ liệu bảo mật Admin được nạp thành công.

---

## Files touched
- `docs/stories/_inbox/US-094A2_lego_frontend_core.md`
- `static/js/lego_core.js`
- `index.html`
- `vercel.json`
