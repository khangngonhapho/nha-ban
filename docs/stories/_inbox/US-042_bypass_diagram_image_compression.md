---
id: US-042
status: accepted
date: 2026-05-29
size: S
---

# US-042: Bypass Diagram Image Compression in Curator Pipeline (Bỏ qua nén ảnh Sơ đồ thửa đất)

## User Story
**As a** Product Owner / Broker Khang Ngô  
**I want** hệ thống Curator tự động bỏ qua quy trình nén ảnh đối với ảnh Sơ đồ thửa đất (Sơ đồ thửa đất 1 & Sơ đồ thửa đất 2) khi cào và di cư dữ liệu hình ảnh  
**So that** ảnh sơ đồ thửa đất luôn giữ nguyên độ phân giải và chất lượng gốc 100%, đảm bảo các chi tiết nhỏ như chữ số, nét vẽ kết cấu, kích thước không bị mờ nhòe khi người dùng phóng to (zoom) trên mọi thiết bị.

---

## Acceptance Criteria
- [x] **Xác định chính xác ảnh Sơ đồ thửa đất:**
  - Trong luồng xử lý di cư ảnh song song (`process_single_image`), hệ thống lấy động các cột `"Sơ đồ thửa đất 1"` và `"Sơ đồ thửa đất 2"` bằng helper an toàn `get_safe_col_name`.
  - Đối chiếu URL ảnh gốc đang xử lý với URL gốc được lưu trong SQLite của hai cột sơ đồ này.
- [x] **Bỏ qua quy trình nén ảnh:**
  - Nếu ảnh đang xử lý là ảnh Sơ đồ thửa đất, bỏ qua hàm `compress_image` để bảo toàn nguyên vẹn byte ảnh ban đầu và độ phân giải gốc 100%.
  - Nếu ảnh không phải sơ đồ (ảnh nội thất thông thường), tiếp tục chạy qua bộ nén tối ưu hóa dung lượng (`compress_image`) như cũ để tiết kiệm băng thông và dung lượng lưu trữ đám mây.
- [x] **Ghi nhật ký (Logging) tường minh:**
  - Hiển thị log chi tiết trên giao diện thời gian thực của Curator: `[🛡️ Sơ đồ] Ảnh #[idx] của [tk_id] là ảnh Sơ đồ thửa đất. BỎ QUA NÉN để bảo toàn chi tiết.` để broker tiện theo dõi và kiểm soát chất lượng dữ liệu đầu vào.

---

## Technical Implementation Details
* Logic kiểm tra và bỏ qua nén được tích hợp trực tiếp bên trong worker thread `process_single_image` của [curator_server.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator_server.py).
* Hàm tự động dán nhãn và đối chiếu liên kết hoạt động ổn định và chính xác dựa trên dữ liệu cào thô từ Thien Khoi.
* **Công cụ sửa lỗi cho 5,000 căn đã di cư:** 
  - Đã xây dựng kịch bản tiện ích [repair_diagrams.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/repair_diagrams.py) giúp người dùng thực hiện quét toàn bộ SQLite, tự động tải ảnh sơ đồ gốc chưa nén từ Thien Khoi (dữ liệu được bảo toàn nguyên vẹn trong `raw_images_tk_json`), đẩy lên Cloudinary/Drive không nén và tự động cập nhật lại SQLite và danh sách ảnh đã di cư.
  - Công cụ này hỗ trợ throttling an toàn và chế độ giới hạn số lượng (limit) để Broker có thể kiểm thử sửa lỗi thử nghiệm cho 10-20 căn trước khi chạy hàng loạt.
