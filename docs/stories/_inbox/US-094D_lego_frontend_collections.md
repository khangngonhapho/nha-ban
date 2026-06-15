---
id: US-094D
status: accepted
date: 2026-06-15
size: S
---

# US-094D: Cô lập Module Bộ sưu tập & Lead Capture

## User story
**As a** Developer  
**I want** cô lập module quản lý bộ sưu tập và yêu thích sang `static/js/lego_collections.js`, đồng thời cô lập module thu thập thông tin khách hàng (lead capture modal) và liên hệ khách hàng sang `static/js/lego_lead_capture.js`  
**So that** cấu trúc index.html được tối giản hóa tối đa, phân tách rõ ràng trách nhiệm giữa lưu trữ giỏ hàng (Collections) và tương tác khách hàng (Lead Capture), bảo đảm khả năng mở rộng tốt và tương thích ngược hoàn toàn.

## Acceptance
- [ ] Tạo tệp `static/js/lego_collections.js` để đóng gói toàn bộ logic quản lý bộ sưu tập và yêu thích.
- [ ] Tạo tệp `static/js/lego_lead_capture.js` để đóng gói toàn bộ logic đăng ký khách hàng, chào mừng, và đặt lịch/gửi nhu cầu qua Zalo.
- [ ] Di chuyển các biến trạng thái bộ sưu tập (`collections`, `favs`, `SELECTED_IDS`, `activeCollectionName`) sang `lego_collections.js` và đồng bộ hóa chúng trên `window`.
- [ ] Di chuyển các hàm bộ sưu tập: `updateShareUI()`, `openColViewModal()`, `openColSaveModal()`, `createNewCollection()`, `saveToExistingCollection()`, `viewCollection()`, `exitCollectionView()`, `closeColViewModal()`, `deleteSelectedCollections()`, `deleteCollection()`, `removeFromCol()`, `renderCollectionsManager()`.
- [ ] Di chuyển các hàm lead capture & Zalo: `submitLeadCapture()`, `scheduleViewing()`, `showRequirementForm()`, `submitClientRequirement()`.
- [ ] Trích xuất logic kiểm tra khách hàng tại `finalizeData` sang hàm `checkLeadCapture(isClientView)` đặt trong `lego_lead_capture.js`.
- [ ] Liên kết hai thẻ script mới ở `<head>` của `index.html` và thiết lập các alias tương thích ngược toàn diện.
- [ ] Viết bộ kiểm thử E2E Playwright chuyên biệt `scratch/test_e2e_collections.py` và `scratch/test_e2e_lead_capture.py` (hoặc gộp chung) chạy thành công 100% trên cả Desktop và Mobile.

## Solution

### 1. LegoCollections Module (`lego_collections.js`)
- Đóng gói các biến trạng thái trên `window`: `favs`, `collections`, `activeCollectionName`, `SELECTED_IDS`.
- Định nghĩa các hàm quản lý bộ sưu tập và gán vào `window`:
  - `updateShareUI`, `openColViewModal`, `openColSaveModal`, `createNewCollection`, `saveToExistingCollection`, `viewCollection`, `exitCollectionView`, `closeColViewModal`, `deleteSelectedCollections`, `deleteCollection`, `removeFromCol`, `renderCollectionsManager`.

### 2. LegoLeadCapture Module (`lego_lead_capture.js`)
- Đồng bộ các biến khách hàng trên `window`: `displayCustomerName`, `trackingCustomerName`.
- Định nghĩa các hàm thu thập thông tin và liên hệ:
  - `checkLeadCapture` (trích xuất từ logic `finalizeData`), `submitLeadCapture`, `scheduleViewing`, `showRequirementForm`, `submitClientRequirement`.

### 3. Tái cấu trúc index.html
- Nạp cả hai script `static/js/lego_collections.js` và `static/js/lego_lead_capture.js` ở `<head>`.
- Khai báo các getters/setters toàn cục cho các biến trạng thái để đảm bảo code inline trong `index.html` gọi không bị lỗi.

---

## User Review Required

> [!IMPORTANT]
> **Tách biệt File & Tương thích Ngược:**
> - Toàn bộ dữ liệu của người dùng trong `localStorage` (`favs`, `adminCollections`, `client_name`, `client_phone`) sẽ được giữ nguyên không thay đổi cấu trúc khóa.
> - Các hàm trong `lego_lead_capture.js` sẽ gọi hàm `trackAction()` trong `index.html` để tiếp tục ghi nhận lịch sử hoạt động của khách hàng.

---

## 📋 Implementation Plan

### [Collections & Lead Capture Component]

#### [NEW] [lego_collections.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_collections.js)
- Chi tiết xem tại implementation_plan.md.

#### [NEW] [lego_lead_capture.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_lead_capture.js)
- Chi tiết xem tại implementation_plan.md.

#### [MODIFY] [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html)
- Chi tiết xem tại implementation_plan.md.

---

## 📝 Task Checklist (TODO)
- [ ] **Thiết kế & Khảo sát:**
  - [ ] Khảo sát các điểm liên kết giữa Collections, Lead Capture và các renderer.
- [ ] **Triển khai Code:**
  - [ ] Tạo tệp `static/js/lego_collections.js` và chuyển logic bộ sưu tập sang.
  - [ ] Tạo tệp `static/js/lego_lead_capture.js` và chuyển logic đăng ký/Zalo sang.
  - [ ] Chỉnh sửa `index.html` nạp 2 file script mới, cài đặt alias tương thích ngược, làm sạch code cũ.
- [ ] **Kiểm thử & Bàn giao:**
  - [ ] Viết test E2E Playwright `scratch/test_e2e_collections.py` kiểm thử đầy đủ cả 2 module mới.
  - [ ] Chạy bộ kiểm thử Playwright đạt 100% PASS.
  - [ ] Merge code và deploy lên Production.

---

## Verification Plan

### Automated Tests
- **Script kiểm thử chính:** [test_e2e_collections.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_e2e_collections.py) [NEW]
- **Kịch bản test:**
  1. Kiểm thử Lead Capture: Modal chào mừng hiện khi có token khách hàng chưa đăng ký -> Điền thông tin -> Đóng modal, hiển thị banner chào mừng thành công.
  2. Kiểm thử Favorites: Thêm căn vào Yêu thích -> Kiểm tra badge yêu thích tăng -> Lọc theo yêu thích.
  3. Kiểm thử Collections: Chọn các căn -> Tạo bộ sưu tập -> Xem bộ sưu tập -> Xóa bộ sưu tập.
  4. Kiểm thử Redirection: Trình giả lập click các nút hẹn xem nhà/nhu cầu khác và kiểm tra link chuyển hướng Zalo được tạo chuẩn.

---

## Files touched
- `docs/stories/_inbox/US-094D_lego_frontend_collections.md`
- `static/js/lego_collections.js`
- `static/js/lego_lead_capture.js`
- `index.html`

---

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Sự cố phát sinh & Quá trình khắc phục (Incidents & Troubleshooting)

#### Sự cố 1: Danh sách bộ sưu tập không tự mở/không mặc định hiển thị bộ sưu tập vừa tạo/lưu thành công
*   **Mô tả lỗi:** Sau khi điền tên và lưu hoặc tạo mới bộ sưu tập thành công, hệ thống hiện thông báo nhưng không tự động mở giao diện danh sách của bộ sưu tập vừa tạo (hoặc thông báo là bộ sưu tập đã tồn tại và trả về danh sách trống/mặc định ban đầu).
*   **Lần sửa đổi 1 (Thử nghiệm & Sai lầm):** Nghi ngờ do việc nhấn nút Enter trên bàn phím ảo của thiết bị di động (mobile virtual keyboard) kích hoạt submit form mặc định làm reload trang hoặc reset lại DOM trước khi giao diện kịp cập nhật, chúng tôi đã thêm chặn hành vi mặc định `preventDefault()`, chặn sự kiện phím `onkeydown`, và đặt `setTimeout` trì hoãn 300ms - 500ms khi gọi `viewCollection`. Tuy nhiên cách này hoàn toàn không giải quyết được vấn đề và đã được hoàn tác (rollback).
*   **Nguyên nhân gốc rễ thực sự:** Khi lưu/tải lại danh sách hoặc cập nhật lại giao diện, các biến trạng thái toàn cục bị khởi tạo lại từ đầu, hoặc luồng tải dữ liệu bất đồng bộ đã ghi đè biến `window.activeCollectionName` về `null` trước khi engine render chạy xong, làm mất dấu vết bộ sưu tập đang hoạt động.
*   **Giải pháp đúng đắn:** 
    1. Đồng bộ hóa và duy trì trạng thái của bộ sưu tập đang mở (`activeCollectionName`) vào `localStorage` mỗi khi gọi `viewCollection()`, và xóa giá trị này trong `localStorage` khi thoát (`exitCollectionView`) hoặc xóa bộ sưu tập (`deleteCollection`).
    2. Ở hàm tải dữ liệu/khởi động trang (`restoreState`), đọc giá trị `activeCollectionName` từ `localStorage` và gọi `window.viewCollection(activeCollectionName, false)` để đưa giao diện người dùng về đúng màn hình bộ sưu tập vừa làm việc.
    3. Thêm lệnh đóng Modal lưu/tạo bộ sưu tập một cách trực tiếp bên trong `viewCollection` để đảm bảo phần danh sách hiển thị ngay tức thì mà không bị che khuất.

#### Sự cố 2: Đường dẫn chia sẻ khách hàng (Client view link) bị trắng màn hình (blank page) do lỗi cú pháp tài nguyên
*   **Mô tả lỗi:** Khi khách hàng click vào liên kết chia sẻ (ví dụ: `/1?b=...`), trình duyệt hiển thị một trang trắng tinh. Console báo lỗi cú pháp (Syntax Error) khi nạp các file tĩnh.
*   **Lần sửa đổi 1 (Thử nghiệm & Sai lầm):** Nghi ngờ lỗi phân tách danh sách ID trong base64 regex (`idListRegex`) hoặc thiếu fallback cho ảnh mặt tiền của BĐS. Đã tiến hành chỉnh sửa các hàm này nhưng không khắc phục được.
*   **Nguyên nhân gốc rễ thực sự:** Trong phần `<head>` của `index.html`, các tệp JS/CSS tĩnh được liên kết bằng đường dẫn tương đối (e.g. `static/js/lego_core.js`). Khi truy cập link chia sẻ có cấp đường dẫn sâu hơn (như `/1?b=...`), trình duyệt sẽ cố gắng tìm tài nguyên tương đối từ thư mục con `/1/static/js/lego_core.js`. Do cấu hình routing của Vercel SPA trả về `index.html` cho các subpath không khớp, trình duyệt nhận về mã HTML thay vì code JS/CSS tĩnh, dẫn đến lỗi `Uncaught SyntaxError: Unexpected token '<'` và trang bị sập hoàn toàn.
*   **Giải pháp đúng đắn:** Thay đổi toàn bộ các đường dẫn tài nguyên tĩnh ở `<head>` của `index.html` thành đường dẫn tuyệt đối (bắt đầu bằng `/` như `/static/css/global.css`, `/static/js/lego_core.js`), bảo đảm trình duyệt luôn truy vấn tài nguyên từ thư mục gốc bất kể cấp độ sâu của đường dẫn URL hiện tại.

### 2. Thực tiễn Tốt (Good Practices)
*   **Absolute Resource Paths in SPAs:** Đối với các ứng dụng Single Page Application (SPA) sử dụng client-side routing (như `/1`, `/collection/...`), luôn sử dụng đường dẫn tuyệt đối (bắt đầu bằng `/`) cho tất cả các tài sản tĩnh (JS, CSS, hình ảnh, webmanifest) trong file HTML gốc. Tránh tuyệt đối dùng đường dẫn tương đối để ngăn chặn lỗi nạp HTML thay cho JS/CSS từ serverless router.
*   **LocalStorage for Navigation State Persistence:** Khi một ứng dụng phụ thuộc vào việc render lại động (như khi danh sách cập nhật từ Sheets API), các biến trạng thái điều hướng UI quan trọng (như bộ sưu tập đang mở) nên được lưu trữ bền vững trong `localStorage` thay vì chỉ dùng biến bộ nhớ RAM toàn cục, giúp khôi phục giao diện chính xác sau các chu kỳ tải dữ liệu.
