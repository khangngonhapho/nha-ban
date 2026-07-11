---
id: US-113
status: accepted
date: 2026-06-29
size: S
---

# US-113: Sửa lỗi chớp chớp đen màn hình khi phóng to và kéo hình ảnh trên iPhone (iPhone Image Zoom Flickering & Black Screen Fix)

## User Story
**As an** Admin/User (Người dùng di động sử dụng thiết bị iOS)
**I want** to pinch-to-zoom and drag images to focus on different specific details of the property photos (like text on land certificates, building details)
**So that** when I release my fingers, the image stays zoomed in and remains at the panned position (doesn't automatically reset or shrink back to center) so I can inspect details closely.

## Acceptance Criteria
- [ ] Khi mở lightbox phóng to hình ảnh trên iPhone (Safari/Chrome/iOS WebKit), người dùng có thể dùng 2 ngón tay để phóng to (pinch zoom) và kéo (drag) hình ảnh mượt mà.
- [ ] Màn hình không bị chớp nháy màu đen, lúc tắt lúc hiện, hoặc làm mất hoàn toàn hình ảnh khi di chuyển hoặc phóng to hình.
- [ ] **Bảo toàn trạng thái Zoom & Focus khi thả tay:** Khi người dùng kết thúc thao tác zoom/drag (sự kiện `touchend`), nếu tỷ lệ scale lớn hơn 1.05, hình ảnh **phải được giữ nguyên tỷ lệ phóng to (scale) và tọa độ vị trí đã kéo (translate)** để người dùng tập trung xem vùng chi tiết đó, tuyệt đối không tự động co nhỏ về 1x hay nhảy về vị trí căn giữa.
- [ ] Khi tỷ lệ scale nhỏ hơn hoặc bằng 1.05 tại thời điểm thả tay, hình ảnh tự động co nhỏ về tỷ lệ gốc `scale(1)` và căn giữa mượt mà có animation.
- [ ] Trải nghiệm zoom và vuốt chuyển ảnh (swipe to change photo) trên các thiết bị Android và Desktop vẫn hoạt động trơn tru, không bị lỗi hồi quy.

## Solution
1. **Khảo sát nguyên nhân gốc rễ (Root Cause):**
   - CSS transition (`transition: transform 0.15s ease-out`) luôn hoạt động trên phần tử `.lb-img` (được định nghĩa trực tiếp inline trong JavaScript tại tệp [lego_detail_client.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_client.js)).
   - Khi người dùng thực hiện thao tác pinch-to-zoom hoặc kéo hình ảnh, sự kiện `touchmove` liên tục thay đổi thuộc tính `style.transform` (scale và translate). Sự thay đổi dồn dập này xung đột trực tiếp với hiệu ứng transition, bắt trình duyệt phải tính toán và vẽ lại (paint) liên tục các bước chuyển cảnh trung gian (transition frames). Trên công cụ kết xuất WebKit của iOS Safari, điều này gây nghẽn hàng đợi kết xuất GPU và gây ra hiện tượng màn hình chớp chớp đen nhấp nháy hoặc biến mất ảnh.
   - **Hiện tượng chớp đen tại thời điểm thả tay (touchend):** Khi nhấc tay khỏi màn hình, WebKit buộc phải đánh giá lại và tái cấu trúc các lớp kết xuất đồ họa (composite layers) để chuyển từ trạng thái tương tác kéo/zoom động sang tĩnh. Nếu trình dịch và tỷ lệ zoom (`transform`) sử dụng phép biến đổi 2D (`translate`) thay vì 3D (`translate3d`), và thuộc tính `transition` bị khôi phục hoặc thay đổi đột ngột mà không tối ưu hóa tăng tốc phần cứng, trình duyệt sẽ giải phóng layer đồ họa cũ và vẽ layer mới không đồng bộ, tạo ra khoảng trễ hiển thị và gây chớp đen màn hình tại khoảnh khắc nhấc ngón tay.
   - Thêm vào đó, việc sử dụng các hàm biến đổi 2D như `translate(x, y)` không tối ưu hóa phần cứng đồ họa (GPU) tốt như các hàm 3D trên WebKit.

2. **Hướng giải quyết (Fix Actions):**
   - **Tắt transition khi đang thao tác:** Khi người dùng bắt đầu chạm/di chuyển (`touchstart` / `touchmove`), tạm thời gán `img.style.transition = 'none'` để hình ảnh di chuyển tức thì theo tọa độ ngón tay.
   - **Sử dụng Hardware Acceleration (GPU):**
     - Đổi toàn bộ các hàm biến đổi hình ảnh từ `translate(x, y)` sang `translate3d(x, y, 0)` trong [lego_detail_client.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_client.js) để kích hoạt tăng tốc phần cứng.
     - Tương tự, đổi các hàm biến dịch của container slide `#lbTrack` từ `translateX(px)` sang `translate3d(px, 0, 0)`.
   - **Bổ sung thuộc tính tối ưu hóa CSS:** Thêm các thuộc tính phòng ngừa nhấp nháy lớp đồ họa (composite layer flickering) vào CSS của `.lb-img` trong tệp [global.css](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/css/global.css):
     ```css
     -webkit-backface-visibility: hidden;
     backface-visibility: hidden;
     -webkit-perspective: 1000;
     perspective: 1000;
     ```
   - **Phục hồi transition khi reset về 1x:** Chỉ khi kết thúc thao tác (`touchend`) và ảnh cần co nhỏ về vị trí mặc định (`scale <= 1.05`), gán lại `img.style.transition = 'transform 0.15s ease-out'` ngay trước khi thay đổi transform về mặc định để co nhỏ mượt mà. Khi scale lớn (> 1.05), giữ nguyên `img.style.transition = 'none'` để người dùng tiếp tục kéo di chuyển vị trí xem không bị trễ/giật.

## 📋 Implementation Plan
- **Các bước triển khai:**
  1. Cập nhật [lego_detail_client.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_client.js):
     - Gán `img.style.transition = 'none'` khi bắt đầu tương tác trong `touchstart` và `touchmove`.
     - Thay thế `translate(...)` bằng `translate3d(..., 0)` và `translateX(...)` bằng `translate3d(..., 0, 0)`.
     - Khôi phục `img.style.transition = 'transform 0.15s ease-out'` trong `touchend` trước khi đặt lại `transform = 'translate3d(0,0,0) scale(1)'`.
  2. Cập nhật [global.css](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/css/global.css):
     - Thêm các thuộc tính tối ưu hóa GPU (`backface-visibility: hidden`, `perspective`) cho hình ảnh lightbox để chống nhấp nháy trên iOS.
  3. Cập nhật mục lục [INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md) đăng ký mã `US-113` ở trạng thái `backlog`.

## 📝 Task Checklist (TODO)
- [ ] **Khảo sát & Viết tài liệu:** Viết tài liệu User Story `US-113` (Đã hoàn thành tệp này)
- [ ] **Đồng bộ Index:** Cập nhật tệp [INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md)
- [ ] **Triển khai Code:** Sửa mã nguồn trong `static/js/lego_detail_client.js` và `static/css/global.css`
- [ ] **Kiểm thử tự động:** Chạy toàn bộ các test E2E của dự án đảm bảo không có lỗi hồi quy (regression)
- [ ] **Kiểm thử thủ công:** Thực tế pinch-to-zoom trên iPhone để xác nhận lỗi chớp đen đã được khắc phục hoàn toàn

## Verification Plan

### Automated Tests
- Chạy toàn bộ kịch bản kiểm thử E2E hiện có để đảm bảo tính ổn định của hệ thống:
  ```powershell
  python scratch/test_e2e_filters.py
  python scratch/test_e2e_curation.py
  ```

### Manual Verification
1. Dùng thiết bị iPhone (iOS) truy cập vào môi trường thử nghiệm (Local hoặc Vercel Preview).
2. Bấm vào một căn nhà bất kỳ để xem chi tiết Khách hàng, bấm vào Carousel để kích hoạt Lightbox.
3. Sử dụng hai ngón tay để phóng to ảnh tối đa (scale ~2x-3x).
4. Giữ một ngón tay và kéo hình ảnh di chuyển lên, xuống, trái, phải để kiểm tra các góc của ảnh.
5. Đảm bảo toàn bộ quá trình kéo và zoom diễn ra mượt mà, không bị giật khung hình, nhấp nháy đen hay biến mất ảnh.
6. Thả tay ra và kiểm tra xem ảnh có tự động co về 1x mượt mà khi scale nhỏ hay không.
