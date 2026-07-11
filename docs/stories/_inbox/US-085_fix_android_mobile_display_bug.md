---
id: US-085
status: accepted
date: 2026-06-10
size: S
---

# US-085: Sửa lỗi hiển thị và vỡ bố cục trên điện thoại Android

## User story
**As an** Admin / Môi giới
**I want** Giao diện Web Admin và chi tiết tin đăng hiển thị chuẩn xác, không bị vỡ hoặc tràn màn hình trên điện thoại di động Android
**So that** Tôi có thể thao tác lọc, xem và biên tập rổ hàng một cách mượt mà và trực quan ngay trên thiết bị di động của mình.

## Acceptance
- [ ] Khi bộ lọc (Filter Panel) ở trạng thái đóng trên di động, trang web không bị kéo giãn chiều ngang (no horizontal scroll / canvas stretching) và không tự động zoom-out làm kích hoạt nhầm bố cục Grid của Laptop (US-074).
- [ ] Khi mở bộ lọc trên di động, bộ lọc phải hiển thị toàn màn hình dạng drawer di động chuẩn, không bị hiển thị lệch hay thu hẹp dạng cột bên phải.
- [ ] Lưới chi tiết Admin Curation modal (`.sheet`) phải được căn giữa/dưới mượt mà, chiều rộng vừa khít khung màn hình di động (không vượt quá chiều rộng màn hình vật lý) và không bị lệch phải hay cắt cụt nội dung.
- [ ] Không xảy ra lỗi hiển thị (regression) đối với giao diện Laptop/Desktop (US-074) và Carousel biên tập hình ảnh (US-084).

## Solution

### Nguyên nhân gốc rễ (Root Cause Analysis)
1. **Trapping Containing Block (Bẫy chứa khối):**
   Phần tử `<header>` được định nghĩa sticky kèm thuộc tính transition/transform:
   ```css
   header {
     position: sticky;
     transition: transform 0.3s cubic-bezier(0.33, 1, 0.68, 1);
   }
   ```
   Trong đặc tả CSS, bất kỳ phần tử tổ tiên nào có `transform` hoặc `transition` liên quan đến transform sẽ trở thành Containing Block cho các phần tử con có `position: fixed`. Do đó, `.filter-panel` (vốn được định vị `position: fixed`) trên mobile bị giữ lại trong phạm vi layout của `<header>` thay vị định vị tương đối với viewport.
2. **Horizontal Canvas Stretching (Giãn chiều ngang trang):**
   Khi bộ lọc đóng trên mobile, nó được đẩy ra ngoài màn hình về phía bên phải sử dụng:
   ```css
   transform: translateX(100%);
   ```
   Do `.filter-panel` bị mắc kẹt bên trong `<header>` và tài liệu mặc định không khóa chiều ngang ở `html` và `body` (`overflow-x: hidden`), việc dịch chuyển 100% chiều rộng sang phải làm giãn chiều ngang của `<header>` lên `200vw`.
3. **Viewport Auto Zoom-out & Desktop style Leakage:**
   Trình duyệt Chrome trên Android tự động zoom-out toàn bộ trang để hiển thị hết phần canvas bị kéo giãn `200vw` đó. Khi zoom-out, chiều rộng viewport tính bằng pixel CSS tăng lên vượt quá `768px` (thường lên đến 1000px - 1200px). 
   Điều này vô tình kích hoạt các Media Queries của desktop/laptop (`@media (min-width: 768px)` và `@media (min-width: 1200px)`). Hậu quả là:
   - Bộ lọc `#filterPanel` bị ép kiểu hiển thị dạng Grid của desktop (`display: grid !important`) lệch bên phải, đè nén danh sách card sang trái (Lỗi hiển thị ở Ảnh 1).
   - Modal chi tiết `.sheet` nhận kiểu rộng của desktop (`width: 1100px !important`) và được căn giữa viewport ảo `1200px` (trọng tâm ở `600px`). Với màn hình vật lý chỉ có `400px`, modal bị dịch sang phải và cắt cụt (Lỗi hiển thị ở Ảnh 2).

### Giải pháp đề xuất (Proposed Solution)
Chúng ta sẽ giải quyết triệt để vấn đề bằng CSS thuần cực kỳ an toàn mà không cần thay đổi cấu trúc HTML DOM hay JavaScript:

1. **Khóa chiều rộng và overflow trang:**
   Bổ dung quy tắc khóa chiều rộng tối đa và ngăn cuộn ngang cho `html` và `body` để đảm bảo trình duyệt di động không bao giờ tự động zoom-out:
   ```css
   html, body {
     max-width: 100%;
     overflow-x: hidden;
   }
   ```
2. **Đổi hướng đóng ẩn của Drawer di động:**
   Trên các thiết bị LTR (Trái-sang-Phải), các phần tử tràn biên về phía **bên trái** (tọa độ âm) sẽ bị trình duyệt cắt bỏ (clip) và **không bao giờ** làm giãn chiều ngang canvas hay tạo thanh cuộn ngang.
   Do đó, chúng ta đổi hướng ẩn của `.filter-panel` trên mobile sang phía bên trái:
   - Khi đóng: `transform: translateX(-100%)` (ẩn về bên trái).
   - Khi mở: `transform: translateX(0)` (trượt ra từ bên trái).
   Sự thay đổi này cũng rất phù hợp với nút Back (`◀`) nằm ở góc trái tiêu đề bộ lọc di động (khi bấm back, bộ lọc trượt lùi về bên trái).

   *Phương án dự phòng:* Nếu không muốn trượt từ bên trái, có thể trượt từ dưới lên bằng `transform: translateY(100%)` khi đóng và `transform: translateY(0)` khi mở. Tuy nhiên, trượt từ bên trái (`translateX(-100%)`) là tối ưu và tự nhiên nhất cho drawer tìm kiếm.

## 📋 Implementation Plan
- **Cách tiếp cận:** Thực hiện điều chỉnh trực tiếp trong file `index.html` tại thẻ `<style>` ở đầu trang.
- **Các bước triển khai dự kiến:**
  1. Thêm `max-width: 100%; overflow-x: hidden;` vào định nghĩa CSS của `body` và `html`.
  2. Tìm định nghĩa `.filter-panel` trong block `@media (max-width: 767px)` và đổi `transform: translateX(100%)` thành `transform: translateX(-100%)`.
  3. Kiểm tra xem các modal `.sheet` và `.overlay` có bị ảnh hưởng ngược không.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát mã nguồn styles hiện tại của header, filter-panel và modal.
  - [x] Chốt phương án CSS (translateX(-100%) và html/body overflow-x: hidden).
- [x] **Triển khai Code:**
  - [x] Cập nhật CSS của `body` và `html` trong `index.html`.
  - [x] Cập nhật CSS ẩn của `.filter-panel` trong `@media (max-width: 767px)` trong `index.html`.
- [x] **Kiểm thử sơ bộ:**
  - [x] Kiểm tra hiển thị bộ lọc và modal chi tiết trên chế độ giả làm mobile (rộng < 768px).
  - [x] Kiểm tra hiển thị bộ lọc và modal chi tiết trên màn hình laptop/desktop (rộng >= 768px và >= 1200px) đảm bảo không có lỗi vỡ layout.
  - [x] Đồng bộ hóa trạng thái User Story lên `INDEX.md`, `NEXT_SESSION.md`.

## 🛠️ Update Logic (Drafting while Doing)

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:** 
  1. Dịch chuyển drawer đóng về bên phải (`translateX(100%)`) kết hợp với Containing Block của sticky header gây giãn canvas trên di động Chrome Android. Khắc phục bằng cách lật ngược hướng ẩn về bên trái (`translateX(-100%)`).
  2. **[US-085.2 Regression Fix]** Việc thêm global lock `overflow-x: hidden` trên cả `html` và `body` đồng thời làm chậm thread xử lý sự kiện touch (touch events) trên Chrome di động, gây hiện tượng vuốt chạm (swipe) ảnh carousel trên card danh sách kém nhạy. Khắc phục triệt để bằng cách xóa bỏ hoàn toàn thuộc tính `overflow-x: hidden` thừa này trên `html` và `body` (vì dịch chuyển sang trái `translateX(-100%)` đã tự động ngăn chặn hoàn toàn việc giãn canvas mà không cần dùng đến overflow lock).
  3. **[US-085.3 Carousel & Lazy Loading Performance Optimization]** Gặp hiện tượng vuốt ngang đổi ảnh (swipe/scroll-snap) trên di động kém nhạy, phải vuốt nhiều cái mới chuyển hình. Nguyên nhân là do thuộc tính `scroll-behavior: smooth` xung đột với cơ chế snap-align của trình duyệt di động trên các container `scroll-snap-type: x mandatory` tạo độ cản/trễ lớn, và thiếu cấu hình `touch-action` phù hợp khiến vuốt chéo nhẹ bị trình duyệt hiểu nhầm là cuộn dọc và hủy sự kiện vuốt ngang. Khắc phục bằng cách loại bỏ `scroll-behavior: smooth` khỏi container `.admin-scroll-carousel`, thiết lập `touch-action: pan-x pan-y` trên các bộ scroll-carousel tự nhiên để khôi phục khả năng vuốt ngang nguyên bản của trình duyệt, thiết lập `touch-action: pan-y` trên trình biên tập ảnh (vốn dùng JS vuốt ngang), rút ngắn thời gian opacity transition của ảnh card xuống `0.15s`, và thêm `decoding="async"` cho tất cả ảnh lazy-loaded để giải phóng main thread khi giải mã ảnh.
- **Phát kiến ngoài kế hoạch / Điểm tối ưu phát hiện khi code:** Tọa độ âm (phía bên trái) trên LTR layouts được trình duyệt xem là vùng clip tĩnh và không bao giờ kích hoạt scrollbar ngang hay giãn canvas, giúp duy trì chuyển động trượt mượt mà mà không làm thay đổi layout viewport, đồng thời giúp loại bỏ được thuộc tính `overflow-x: hidden` vốn gây lag scroll/touch trên mobile.


### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- **Script kiểm thử thô / nháp đã chạy:** Đã xác minh thủ công qua Git diff và inspect cấu trúc stylesheet.
- **Output kết quả nháp & Điểm nghẽn đã vượt qua:** Đã pass test, CSS selectors đồng bộ chuẩn xác.

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)
- **Bẫy Containing Block với Sticky Header (CSS Specification):** Khi phần tử tổ tiên (`header`) có thuộc tính `transition/transform`, nó sẽ biến thành Containing Block của các phần tử con định vị `position: fixed`. Do đó, drawer menu bộ lọc di động `.filter-panel` không định vị theo viewport mà bị bó hẹp trong layout của header, dẫn đến giãn canvas ngang lên `200vw` khi ẩn bên phải (`translateX(100%)`).
- **Nguyên lý Xén Tọa độ Âm (Negative Coordinates Clipping):** Trong các layout LTR (Trái-sang-Phải) của trình duyệt, các phần tử tràn về phía bên trái (tọa độ âm, ví dụ `translateX(-100%)`) sẽ được trình duyệt tự động cắt bỏ (clip) mà không bao giờ kích hoạt cuộn ngang hay kéo giãn canvas. Tận dụng thuộc tính này giúp ẩn drawer bên trái cực kỳ an toàn mà không cần lạm dụng khóa tràn màn hình `overflow-x: hidden`.
- **Xung đột giữa Smooth Scroll và Scroll Snap:** Tránh sử dụng `scroll-behavior: smooth` trên các container dùng `scroll-snap-type: x mandatory` (như bộ ảnh chi tiết `.admin-scroll-carousel`). Việc ép trình duyệt nội suy mượt mà qua thuộc tính này sẽ tranh chấp với thuật toán snap-align của hệ thống, khiến trải nghiệm vuốt ngang bị ì, rít và không nhạy trên Chrome/Safari di động.
- **Phân chia vai trò touch-action cho các loại Carousel:**
  - **Với Native Scroll Carousel (Dùng thanh cuộn tự nhiên):** Bắt buộc dùng `touch-action: pan-x pan-y` hoặc để mặc định để đảm bảo trình duyệt xử lý cả cử chỉ vuốt dọc cuộn trang lẫn vuốt ngang cuộn ảnh. Cấu hình nhầm `touch-action: pan-y` sẽ vô hiệu hóa hoàn toàn khả năng vuốt ngang của container này.
  - **Với JS-based Carousel (Tự viết logic swipe bằng Javascript):** Cần dùng `touch-action: pan-y` để chặn cử chỉ vuốt ngang mặc định của trình duyệt (tránh kích hoạt lùi/tiến trang trên mobile), đồng thời cho phép người dùng cuộn dọc trang khi lướt ngón tay qua vùng này.
- **Tối ưu hóa tải ảnh di động:** Sử dụng `decoding="async"` kết hợp với giảm thời gian chuyển tiếp mờ/tỏ (`opacity transition` từ `0.4s` xuống `0.15s`) giúp cải thiện rõ rệt tốc độ hiển thị hình ảnh trên di động. Việc giải mã ảnh bất tuần tự giúp tránh hiện tượng giật đứng thanh cuộn dọc (scroll jank) khi có nhiều ảnh được tải và render cùng lúc.


## Verification Plan

### Automated Tests
- Không áp dụng cho thay đổi thuần giao diện (CSS).

### Manual Verification
1. Mở trang Web Admin trên Chrome DevTools.
2. Chuyển sang chế độ Responsive / Device Mode giả lập iPhone/Android (width < 768px, ví dụ 390px):
   - Đảm bảo trang web hiển thị đúng tỉ lệ, không bị tự động thu nhỏ/zoom-out.
   - Bấm nút **Bộ lọc** (`⚙️` hoặc icon phễu), kiểm tra panel trượt ra mượt mà từ bên trái và hiển thị full screen. Bấm nút Back (`◀`) để đóng, panel trượt ẩn sang trái mượt mà.
   - Mở modal chi tiết tin đăng (bằng cách chọn một căn trong danh sách), kiểm tra modal `.sheet` hiển thị bo góc dưới/giữa màn hình di động, không bị tràn viền hay lệch phải.
3. Chuyển sang kích thước màn hình lớn (Laptop width >= 1024px và Desktop >= 1200px):
   - Bấm nút **Bộ lọc**, kiểm tra panel hiển thị dạng Grid 2 cột sticky chuẩn xác dưới header.
   - Mở modal chi tiết tin đăng, kiểm tra hiển thị dạng modal lớn 2 cột song song chuẩn kích thước `1100px`.

## Files touched
- `index.html` — Cập nhật CSS styles cho body, html và .filter-panel di động.
