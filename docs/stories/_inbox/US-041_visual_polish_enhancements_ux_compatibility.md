---
id: US-041
status: accepted
date: 2026-05-29
size: S
---

# US-041: Visual Polish, Device Compatibility, & SPA History State Management (Tinh chỉnh giao diện, Tương thích di động & Điều hướng Back-button)

## User Story
**As a** Product Owner / Broker Khang Ngô  
**I want** giao diện chi tiết, thanh công cụ cọ biên tập, và kích thước chữ của website BDS được tinh chỉnh siêu mượt mà, mỏng nhẹ, tối ưu hóa hiển thị và điều hướng trên cả dòng máy iPhone (Safari) lẫn Android  
**So that** tôi và khách hàng có trải nghiệm duyệt tin đăng, xem ảnh và thao tác quản trị cực kỳ mượt mà, tiện lợi, không bị thoát ứng dụng vô cớ khi bấm nút Back vật lý trên điện thoại, đồng thời đảm bảo nội dung mô tả được tự động làm sạch khỏi các ký tự dấu rác.

---

## Acceptance Criteria
- [x] **Cọ Biên Tập Ảnh & Chống Lỗi Layout Safari (iOS/Android):**
  - Grid ảnh biên tập Admin tự động duy trì 3 cột hoàn chỉnh trên iPhone Safari mà không bị co rút hay thay đổi kích thước.
  - Sử dụng absolute padding-top hack (`padding-top: 75%`, `height: 0`) thay cho `aspect-ratio` flexbox của iOS để chống méo hình.
  - Loại bỏ hoàn toàn thanh công cụ đen cũ ở đáy ảnh, thay bằng thanh công cụ cọ vẽ (`🔒 Mặt Tiền`, `⭐ Nền`, và `✕ Hủy` xuất hiện động) ghim đối xứng phía trên grid ảnh.
  - Checkbox hiển thị "Hiện" được chuyển thành overlay badge màu đen mờ trực tiếp ở góc dưới phải của mỗi hình.
  - Lọc trùng lặp ảnh mặt tiền để mỗi bức ảnh chỉ hiển thị duy nhất một lần.
- [x] **Header Tiêu Đề Căn Sạch Đẹp (Clean Title Header):**
  - Tiêu đề modal chi tiết (`mT`) chỉ giữ lại số nhà/hẻm và tên đường (ví dụ: `165 Nguyễn Văn Công` hoặc `45.2D Nhiêu Tứ`).
  - Cắt bỏ hoàn toàn các thông tin phụ về giá, diện tích, kết cấu và các thông số tracking nội bộ để mang lại cảm giác sạch sẽ, cao cấp và chuyên nghiệp nhất.
- [x] **Thiết Kế Header Đỏ Siêu Mỏng (Ultra-Thin Premium Red Header):**
  - Chuyển đổi toàn bộ viền vàng gradient của các khối accordion và header modal chi tiết thành tông màu Đỏ thương hiệu (`var(--red)`).
  - Thu mỏng chiều cao accordion headers về `padding: 9px 16px !important`.
  - Header modal chi tiết (`.shead`) được thu mỏng tối đa với `padding: 5px 16px` cùng viền đỏ sậm ở đáy (`1.5px solid #b32d2e`).
  - Nút đóng `✕` (`.xbtn`) thu nhỏ xuống `28px` (cỡ chữ `12px`), có màu trắng nổi bật và thiết kế chạm mờ mượt mà (`rgba(255, 255, 255, 0.18)`).
- [x] **Điều Hướng SPA Back-Button (Browser History Integration):**
  - Khi mở modal chi tiết (`openS`), đẩy trạng thái lịch sử ảo (`history.pushState({ detailOpen: true }, "")`).
  - Khi người dùng nhấn nút Back vật lý của điện thoại hoặc vuốt màn hình để Back, sự kiện `popstate` kích hoạt đóng modal chi tiết tại chỗ, đưa người dùng quay lại danh sách BDS hiện tại thay vì thoát trang ra Google.
  - Khi đóng modal thủ công (`closeS`), ứng dụng tự động thực hiện `history.back()` để đồng bộ trạng thái chính xác.
- [x] **Khả Năng Tiếp Cận & Cỡ Chữ Tối Ưu (+1 size):**
  - Tiêu đề địa chỉ của căn nhà (`.stitle`) được tăng lên thành **`18px !important`** nổi bật.
  - Hộp nội dung mô tả chi tiết thô (`.admin-mota-box`) và mô tả công khai khách hàng (`.desc`) được tăng lên thành **`14.5px !important`** với giãn dòng `1.6` cực kỳ thoáng mắt và dễ chịu khi đọc ngoài thực địa.
- [x] **Tự Động Làm Sạch Mô Tả (Description Sanitization):**
  - Lọc sạch tự động tất cả các dòng trống rác hoặc dòng chứa toàn dấu phân cách (`_______`, `---`), dấu chấm hoặc ký tự rác mà không chứa bất kỳ chữ cái hay chữ số nào.
  - Tuyệt đối bảo toàn các dòng chứa số điện thoại liên lạc quan trọng (`☎: 0932624113`).

---

## Technical Implementation Details
* Giao diện HTML/CSS/JS được tinh chỉnh trực tiếp và duy nhất tại [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html).
* Các cập nhật đã được triển khai deploy thành công trực tiếp lên nền tảng đám mây Vercel và được Product Owner kiểm thử nghiệm thu thực tế thành công 100% ("Test Pass").
