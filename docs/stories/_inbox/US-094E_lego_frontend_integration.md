---
id: US-094E
status: accepted
date: 2026-06-16
size: M
---

# US-094E: Tích hợp toàn diện, tối ưu hiệu năng và dọn dẹp index.html

## User story
**As an** Admin / Developer  
**I want** di chuyển toàn bộ logic mock API sheets và các hàm utility/helper còn lại trong `index.html` sang các tệp module tĩnh `static/js/lego_mock.js` và `static/js/lego_helpers.js`, tối ưu hóa caching CDN qua Cache-Control headers, đồng thời thu gọn tệp index.html xuống dưới 100 dòng script  
**So that** toàn bộ kiến trúc frontend đạt chuẩn Lego Frontend 100%, trang tải cực nhanh qua CDN, tránh rủi ro hồi quy và dễ dàng bảo trì trong tương lai.

## Acceptance
- [x] Tạo mới tệp `static/js/lego_mock.js` và di chuyển logic Mock Fetch Interceptor (dùng cho offline testing & Playwright).
- [x] Tạo mới tệp `static/js/lego_helpers.js` và di chuyển toàn bộ các hàm utility/helper:
  - Nhóm định dạng/cleaner: `formatPhone`, `stripVietnameseAccents`, `abbreviateAndReverseRoad`, `mapSoNha`, `generateMaKhangNgo`, `generateAutoTitle`, `generateAutoDescription`, `normalizeImgUrl`, `cleanRawNoiDungChinh`, `extractSource`, `cutTitleToDistrict`, `formatRawDescription`, `extractCommission`, `getDaiNha`, `decodeBitmask`, `isFacadeUrl`.
  - Nhóm tải ảnh: `downloadSingleImage`, `fetchAllBlobs`, `shareAllImagesToGallery`, `downloadSequential`, `renderDownloadProgress`, `clearDownloadProgress`, `downloadAllListingImages`.
  - Nhóm hệ thống/UI chung: `showToast`, `trackAction`, `showError`, `saveState`, `restoreState`, `updateStats`, `updateSortButtonsUI`, `toggleSortNew`, `toggleSortPrice`.
  - Nhóm ánh xạ dữ liệu: `getMappedPoolData`, `finalizeData`.
- [x] Tái cấu trúc `index.html` làm sạch block script inline khổng lồ (lines 476–2607), đưa về dưới 100 dòng script khởi chạy lõi (setup events, loadData).
- [x] Nạp các script tĩnh mới trong `<head>` của `index.html` sử dụng query parameter cache-busting `?v=...` khớp với version hiện hành.
- [x] Đăng ký các alias tương thích ngược toàn cục trên đối tượng `window` trong `lego_mock.js` và `lego_helpers.js` để tránh lỗi tham chiếu từ các template HTML.
- [x] Xác nhận Cache-Control headers được trả về đúng từ Vercel/Node Serverless cho các file JS tĩnh này (`public, max-age=31536000, immutable`).
- [x] Bộ kiểm thử E2E Playwright (`scratch/test_e2e_curation.py`, v.v.) phải chạy thành công 100% trên môi trường giả lập (mock).

---

## Solution

### 1. Đóng gói Module Mock API (`lego_mock.js`)
- Di chuyển đoạn IIFE tự chạy chặn `window.fetch` và giả lập các phản hồi của Google Sheets API, Google OAuth Token khi tham số `mock=true` hoặc `localStorage.getItem('isMockMode') === 'true'`.
- Đảm bảo mock API được khởi tạo cực sớm trước bất kỳ lệnh gọi fetch nào khác.

### 2. Đóng gói Module Helpers (`lego_helpers.js`)
- Chứa toàn bộ các hàm hỗ trợ độc lập.
- Đăng ký chúng trên đối tượng `window` để giữ khả năng tương thích ngược tuyệt đối.

### 3. Tối giản `index.html` & Khớp nối
- Loại bỏ toàn bộ các hàm helper, chỉ giữ lại script khởi tạo lõi của trang:
  - Xử lý trạng thái URL parameters (`preview=true`, `pwd=...`, giải mã `c` cho tên khách hàng).
  - Lắng nghe sự kiện của `LegoState` (`authStatusChanged`, `authRequired`, `rawDataLoaded`, v.v.) để điều phối UI tổng thể và gọi `render` hoặc `finalizeData`.
  - Hàm `openS` điều khiển mở detail sheet (gọi render chi tiết Khách hàng / Admin tương ứng).
  - Gọi khởi động `LegoState.loadData()`.
- Tổng số dòng JS inline trong `index.html` sẽ giảm xuống dưới 100 dòng.

---

## 📋 Implementation Plan
Xem chi tiết tại [implementation_plan.md](file:///C:/Users/Khang%20Ngo/.gemini/antigravity/brain/595fc691-aac4-4d6b-9257-a1e94612755c/implementation_plan.md).

---

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát sự phụ thuộc giữa các hàm utility trong inline script và các module Lego khác.
- [x] **Triển khai Code:**
  - [x] Tạo tệp `static/js/lego_mock.js` và di chuyển logic Mock Fetch Interceptor sang.
  - [x] Tạo tệp `static/js/lego_helpers.js` và di chuyển toàn bộ các hàm utility/helper sang.
  - [x] Làm sạch `index.html`, loại bỏ hơn 2000 dòng code script inline và liên kết các file JS tĩnh mới.
  - [x] Đăng ký đầy đủ alias toàn cục trên `window` cho các hàm đã di cư.
- [x] **Kiểm thử & Bàn giao:**
  - [x] Chạy bộ kiểm thử E2E Playwright (`test_e2e_curation.py` và các bộ test khác) đảm bảo 100% PASS.
  - [x] Đồng bộ hóa các tài liệu (`INDEX.md`, `NEXT_SESSION.md`, `SOURCE_OF_TRUTH.md`).
  - [x] Merge code ảo về nhánh `main` và push deploy lên Production.

---

## Verification Plan

### Automated Tests
- **Bộ test E2E Playwright:**
  - `python scratch/test_e2e_curation.py`
  - Các Playwright tests khác nếu có.
- **Mục tiêu:** 100% PASS ở cả Desktop và Mobile.

### Manual Verification
- Tải trang trên trình duyệt thực với `?mock=true` để kiểm tra Mock Mode hoạt động trơn tru.
- Kiểm tra cache-control header của `/static/js/lego_mock.js` và `/static/js/lego_helpers.js` qua F12 Network tab.

---

## Files touched
- `docs/stories/_inbox/US-094E_lego_frontend_integration.md`
- `static/js/lego_mock.js`
- `static/js/lego_helpers.js`
- `index.html`
- `docs/stories/INDEX.md`
- `docs/NEXT_SESSION.md`
- `SOURCE_OF_TRUTH.md`

---

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Incidents & Root Cause Analysis
- **Sự cố 1: Lỗi Speed Dial Actions trôi nổi tự do trên Mobile**:
  - *Nguyên nhân*: Thuộc tính layout của CSS `.dial-actions` trước đây được định vị tương đối, dẫn đến việc trên viewport dọc hẹp của Mobile, menu bị đẩy nhảy lung tung ra giữa màn hình.
  - *Giải pháp*: Căn chỉnh `.dial-actions` thành `position: absolute` neo ngay phía trên của nút Speed Dial FAB chính (`bottom: 60px; right: 0;`).
- **Sự cố 2: Lỗi caching trình duyệt trên Live khi deploy**:
  - *Nguyên nhân*: CDN và trình duyệt người dùng lưu cache phiên bản `index.html` hoặc `global.css` cũ, khiến các thay đổi CSS/JS không hiển thị hoặc bị crash do mismatch hàm.
  - *Giải pháp*: Bổ sung version query parameter `?v=202606161110` vào thẻ `<link>` và `<script>` trong `<head>` của `index.html`.

### 2. Good Practices (Thực tiễn tốt)
- **GP-013: Versioning Cache-Busting cho Tài nguyên Tĩnh**: Luôn đính kèm tham số phiên bản dạng `?v=YYYYMMDDHHMM` vào tất cả các liên kết CSS, JS tĩnh tại `<head>` trang chủ để đảm bảo tính đồng bộ tức thì khi deploy Production.
- **GP-014: Tuyệt đối neo tuyệt đối/cố định cho floating controls di động**: Các thành phần trôi nổi điều hướng (Speed Dial, floating actions) bắt buộc phải sử dụng `position: fixed` hoặc `position: absolute` neo vào viewport thay vì layout trôi tự do để đảm bảo responsive trên mọi tỷ lệ khung hình.

### 3. Harness Evolution (Tiến hóa bộ test E2E)
- Cập nhật test suite E2E `test_e2e_curator.py` để chụp ảnh màn hình nghiệm thu tự động (Desktop & Mobile screenshots) giúp phát hiện nhanh các lỗi vỡ layout hoặc trôi nút bấm mà không cần thao tác thủ công.
