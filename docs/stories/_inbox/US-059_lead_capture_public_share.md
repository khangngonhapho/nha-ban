---
id: US-059
status: accepted
date: 2026-06-02
size: M
---

# US-059: Biểu mẫu Đăng ký Thông tin cho Link Công khai & Phản hồi Khách hàng qua Zalo

## User story
**Với vai trò là** Môi giới / Admin (Anh Khang Ngô)
**Tôi muốn** có thể tạo các liên kết chia sẻ công khai (Public Link) mà không cần nhập trước thông tin khách hàng. Khi khách hàng mở liên kết này, họ bắt buộc phải nhập Tên và Số điện thoại liên hệ để có thể xem thông số chi tiết và hình ảnh của căn nhà.
**Để từ đó** tôi có thể dễ dàng chia sẻ rổ hàng lên các kênh công khai để tìm kiếm khách hàng tiềm năng mới, đồng thời giúp khách hàng dễ dàng đặt lịch hẹn đi xem nhà hoặc gửi yêu cầu tìm nhà khác trực tiếp về Zalo của tôi.

## Acceptance
- [x] Admin có thể tạo link chia sẻ cá nhân hóa trong modal `#linkModal`, hoặc click nút **`⚡ Tạo Link Công Khai Nhanh`** mới để tự động tạo link chia sẻ hàng loạt (bitmask `?b=...` hoặc `?s=...`) không chứa tham số khách hàng `c` và sao chép trực tiếp vào clipboard.
- [x] Kế thừa tính năng **`Copy link nhanh`** của US-049 (tạo link đơn căn dạng `?s=SYS-XXXX`), tự động kích hoạt Lead Capture Form khi khách hàng mở link này.
- [x] Khi khách hàng mở bất kỳ link chia sẻ nào (dạng `shareToken` || `shareBitmask` có giá trị) và không phải Admin, một bảng đăng ký thông tin (Lead Capture Modal) mờ ảo (Glassmorphic) sẽ hiện lên chặn toàn màn hình nếu trình duyệt của họ chưa lưu số điện thoại.
- [x] Nếu link chia sẻ đã có sẵn tên khách hàng từ trước (URL có tham số `c`) nhưng chưa có số điện thoại lưu trong trình duyệt, bảng đăng ký sẽ tự điền sẵn Tên và chỉ yêu cầu khách hàng nhập Số điện thoại.
- [x] Số điện thoại của khách hàng nhập vào sẽ được kiểm tra định dạng hợp lệ (chuẩn số điện thoại di động Việt Nam gồm 10 chữ số).
- [x] Khi khách hàng nhấn gửi thông tin thành công, hệ thống sẽ lưu thông tin khách hàng vào trình duyệt (`localStorage`), ẩn bảng đăng ký, hiển thị banner chào mừng, và tự động gửi tracking hành động (`trackAction`) về Google Sheets.
- [x] Ở giao diện xem chi tiết căn nhà của khách hàng, bổ sung thêm một khung tương tác phản hồi (Feedback Box) nằm ngay dưới phần mô tả căn nhà.
- [x] Khung tương tác có nút "📅 Hẹn đi xem nhà": Khi click sẽ lưu tracking, tự động soạn tin nhắn mẫu Zalo (gồm Tên khách hàng, SĐT, Mã căn và Tiêu đề căn nhà), sao chép vào Clipboard và chuyển tiếp khách hàng sang Zalo chat của Khang Ngô.
- [x] Khung tương tác có nút "✏️ Cần tìm căn khác, gửi lại nhu cầu": Khi click sẽ mở rộng một khung soạn thảo. Khách hàng ghi nhu cầu và bấm gửi sẽ lưu tracking nhu cầu, soạn sẵn tin nhắn Zalo kèm nhu cầu đó, sao chép vào Clipboard và chuyển tiếp sang Zalo chat của Khang Ngô.
- [x] [Cải tiến] Tích hợp nhóm nút hành động nổi Admin ở góc phải màn hình thành một **Speed Dial FAB Menu hình bánh răng `⚙️`** (không text, chỉ icon).
- [x] [Cải tiến] Tự động chuyển đổi các nút bên trong Speed Dial tùy biến theo màn hình: Hiện Chọn tất cả/Lưu/Chia sẻ rổ hàng ở trang danh sách, và tự động chuyển thành Lưu thay đổi `💾`/Gửi Zalo `🔗` ở trang chi tiết căn nhà.
- [x] [Sửa lỗi] Sửa lỗi bỏ chọn tất cả: Khi bấm Bỏ chọn tất cả (`☑`), thực hiện xóa sạch toàn bộ `SELECTED_IDS` toàn cục (kể cả những căn bị ẩn). Tự động đồng bộ icon `☐` / `☑` theo bộ lọc tìm kiếm.
- [x] [Cải tiến] Ẩn hoàn toàn 2 nút cũ "📞 Gọi ngay" và "💬 Tư vấn ngay căn này" ở Client View detail để hướng khách sử dụng khung tương tác mới.

## Solution
- **Phía Admin (Tạo link nhanh):**
  - Trong `#linkModal`, bổ sung thêm nút `⚡ Tạo Link Công Khai Nhanh (Khách tự nhập thông tin)` kích hoạt hàm `executeGenerateQuickLink()`.
  - Hàm `executeGenerateQuickLink()` sẽ bỏ qua kiểm tra `linkCustName` và sinh link không chứa tham số `c`, copy trực tiếp vào clipboard.
- **Phía Khách hàng (Đăng ký thông tin):**
  - Thêm thẻ HTML `#leadCaptureModal` dạng full-screen overlay với thiết kế Glassmorphic mờ ảo cao cấp.
  - Khi load trang khách hàng (`(shareToken || shareBitmask) && !isAdmin`):
    - Đọc `localStorage` tìm `client_name` và `client_phone`.
    - Nếu chưa có `client_phone`, hiện modal `#leadCaptureModal`.
    - Nếu URL có tham số `c`, giải mã điền sẵn (pre-fill) tên khách hàng vào ô Tên.
  - Viết hàm `submitLeadCapture()` validate Tên và SĐT (regex di động Việt Nam `^(0\d{9}|[1-9]\d{8})$`), lưu vào `localStorage`, ẩn modal, cập nhật banner chào mừng và gửi tracking log.
- **Phía Khách hàng (Phản hồi & Đặt lịch):**
  - Bổ sung khối `.client-feedback-box` hiển thị 2 nút lựa chọn dưới mô tả căn nhà ở client view.
  - Viết hàm `scheduleViewing(id, title)` và `submitClientRequirement(id, title)` để soạn tin nhắn mẫu Zalo chuyên nghiệp cá nhân hóa, copy vào Clipboard và chuyển hướng người dùng sang Zalo anh Khang.
  - Ẩn khung `.scta` chứa 2 nút gọi cũ bằng cách chuyển `scta.style.display` thành `'none'` trong client view detail.
- **Cải tiến Speed Dial & Selection Logic:**
  - Thiết kế container `.admin-speed-dial` định vị fixed ở góc phải dưới. Nút chính `.dial-main-btn` (icon bánh răng ⚙️) điều khiển đóng/mở danh sách `.dial-actions`.
  - Viết hàm `renderSpeedDialActions(mode, p)` để vẽ lại danh sách nút con tùy thuộc vào việc người dùng đang đứng ở trang danh sách chính (`mode = 'list'`) hay trang chi tiết (`mode = 'detail'`).
  - Hàm `toggleSelectAll()` được cập nhật: Nếu `allSelected` hoặc visible bằng 0 và có chọn ngầm, gọi `SELECTED_IDS.clear()` và bỏ chọn toàn bộ checkbox.

## 📋 Implementation Plan
- **Bước 1:** Bổ sung giao diện và hàm tạo link công khai nhanh cho Admin trong `#linkModal`.
- **Bước 2:** Xây dựng biểu mẫu Glassmorphic `#leadCaptureModal` thu thập thông tin khách hàng.
- **Bước 3:** Lập trình logic kiểm tra thông tin khách hàng trên LocalStorage khi tải trang và điền sẵn tên nếu có tham số `c`.
- **Bước 4:** Lập trình logic kiểm thử và xử lý khi click gửi thông tin đăng ký.
- **Bước 5:** Bổ sung khung phản hồi tương tác dưới chân chi tiết căn nhà của khách hàng.
- **Bước 6:** Hiện thực hóa các hàm Zalo: `scheduleViewing` và `submitClientRequirement`.
- **Bước 7:** Tích hợp menu Speed Dial ⚙️ cho Admin, gom nhóm nút nổi, ẩn 2 nút gọi cũ cho khách hàng và sửa lỗi logic bỏ chọn.
- **Bước 8:** Kiểm thử các kịch bản và deploy Vercel.

## 📝 Task Checklist (TODO)
- [x] Cập nhật modal chia sẻ `#linkModal` để thêm nút Tạo link công khai nhanh
- [x] Viết hàm `executeGenerateQuickLink` cho Admin
- [x] Thêm mã HTML `#leadCaptureModal` vào giao diện
- [x] Viết CSS cho `#leadCaptureModal` và `.client-feedback-box`
- [x] Lập trình logic kiểm tra thông tin đăng ký của khách hàng khi load trang
- [x] Viết hàm `submitLeadCapture` và validation Số điện thoại
- [x] Tích hợp khung phản hồi tương tác vào client view detail trong `openS`
- [x] Lập trình hàm tương tác đặt lịch xem nhà `scheduleViewing`
- [x] Lập trình hàm gửi yêu cầu tìm nhà khác `submitClientRequirement`
- [x] Thiết kế Speed Dial Menu ⚙️ ẩn text, chỉ chứa icon gom nhóm nút Admin
- [x] Tích hợp các nút hành động của trang chi tiết vào Speed Dial (đổi nút động theo màn hình)
- [x] Sửa lỗi uncheck all để xóa sạch giỏ hàng toàn cục và đồng bộ checkbox theo bộ lọc
- [x] Ẩn 2 nút gọi/tư vấn cũ ở màn hình khách hàng
- [x] Kiểm thử thủ công các trường hợp: Admin tạo link công khai, khách hàng tự nhập thông tin, khách hàng đặt lịch xem, khách hàng gửi nhu cầu khác.

## 🛠️ Update Logic (Drafting while Doing)
- Đưa logic Bỏ chọn toàn bộ vào `SELECTED_IDS.clear()` để tránh tình trạng sót lại các căn bị ẩn do filter tìm kiếm.
- Sử dụng CSS `!important` ghi đè thuộc tính `position: fixed` của các nút nổi cũ khi hiển thị trong container Speed Dial flex.

## Verification Plan
- **Kiểm thử tự động:** Viết test case kiểm tra định dạng Số điện thoại đầu vào.
- **Kiểm thử thủ công:**
  1. Đăng nhập Admin, tạo link công khai nhanh cho 2 căn. Copy URL.
  2. Mở tab ẩn danh, truy cập URL. Đảm bảo modal đăng ký hiện ra, chặn toàn bộ view.
  3. Nhập sai số điện thoại -> Báo lỗi.
  4. Nhập đúng thông tin -> Modal ẩn, danh sách nhà hiển thị, banner chào mừng hiện đúng tên.
  5. Xem chi tiết -> Click đặt lịch -> Kiểm tra clipboard có text mẫu và chuyển hướng Zalo.
  6. Click đổi nhu cầu -> Nhập thông tin nhu cầu -> Click gửi -> Kiểm tra clipboard có text mẫu nhu cầu và chuyển hướng Zalo.
  7. Admin xem danh sách -> Bấm bánh răng ⚙️ -> Kiểm tra bung/thu menu. Chọn uncheck -> Kiểm tra sạch bộ nhớ cache.
  8. Admin xem chi tiết -> Bánh răng ⚙️ chuyển thành nút Lưu và nút Zalo.

## Files touched
- `index.html`

## 🔄 Change Requests (Yêu cầu Thay đổi)
- **CR-01 (02/06/2026):** Gom nhóm nút nổi Admin thành Speed Dial dạng bánh răng ⚙️ chỉ chứa icon.
- **CR-02 (02/06/2026):** Sửa lỗi bỏ chọn tất cả không xóa sạch các căn bị ẩn.
- **CR-03 (02/06/2026):** Đổi nút động bên trong Speed Dial tương thích theo trang chi tiết (Save và Zalo).
- **CR-04 (02/06/2026):** Ẩn 2 nút Gọi ngay và Tư vấn ngay cũ ở màn hình khách hàng.
