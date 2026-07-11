# Kế hoạch Triển khai: Bảng So Sánh Bất Động Sản & Hệ Thống Tracking Hành Vi Khách Hàng

Bản kế hoạch này mô tả kiến trúc, luồng xử lý và các bước kỹ thuật để hiện thực hóa tính năng "So sánh Radar Chart" và "Theo dõi hành vi (Tracking)" trên nền tảng Web Dành Cho Khách Hàng của Khang Ngô Nhà Phố.

---

## PHẦN 1: TÍNH NĂNG TẠO LINK CÁ NHÂN HOÁ (Trên Web Client - Chế độ Admin)
**Mục tiêu:** Tạo ra một đường link duy nhất, chứa thông tin mã hoá của khách hàng và danh sách các căn nhà được chọn. Tính năng này được thực hiện trực tiếp trên trang Web dành cho Khách hàng nhưng yêu cầu truy cập bằng link Admin (`?pwd=trang`).

1. **Giao diện Admin (Web Client):**
   - Kế thừa tính năng check-box chọn nhà hiện có trên Web Client (chế độ Admin).
   - Bổ sung nút **"🔗 Tạo Link Gửi Khách"**.
2. **Popup Nhập Thông Tin Khách:**
   - Khi bấm tạo link, hiện Popup yêu cầu nhập: `Tên khách hàng`, `Số điện thoại` (tuỳ chọn), `Ghi chú định danh`.
3. **Mã hoá URL (Tương thích với logic cũ):**
   - Hiện tại trang Client (`BDS-KhangNgo`) đã có tính năng chia sẻ danh sách qua `?s=` (mã hoá Base64 mảng ID) hoặc `?b=`.
   - Ta sẽ nối thêm tham số:
     👉 `https://[domain-client]/?s=[Base64_Của_Mảng_ID]&c=[Base64_Của_Tên_Khách_Hàng]`
     (Ví dụ: `?s=WzEwMDEsMTAyMl0=&c=QW5oIEjDuW5n`)

---

## PHẦN 2: HỆ THỐNG TRACKING (Theo Dõi Hành Vi Khách Hàng)
**Vấn đề bảo mật:** Web dành cho khách hàng mang tính Public, KHÔNG ĐƯỢC chứa Token Google Sheets API (nếu không hacker sẽ xoá mất data).
**Giải pháp kiến trúc:** Sử dụng **Google Apps Script (GAS) Web App** làm cổng API trung gian để ghi Log an toàn.

1. **Tạo Sheet `TrackingLog` (Bắt buộc dùng File Độc Lập Mới):** 
   - Vì file dữ liệu nhà đang để chế độ "Share Anyone", nếu đặt Tracking chung file sẽ rất dễ bị lộ thông tin khách hàng nếu ai đó biết được Sheet ID.
   - **Giải pháp:** Tạo hẳn một File Google Sheet *riêng biệt và hoàn toàn Private* (Chỉ tài khoản Khang Ngô được xem).
   - Thiết lập các cột: `Thời gian`, `Tên Khách`, `SĐT`, `Hành động`, `Chi tiết (Các căn đang xem/loại bỏ)`, `Tiêu chí quan tâm`.
2. **Viết Google Apps Script (Backend an toàn):**
   - Script này được nhúng vào file Tracking Private, chạy dưới quyền của Chủ sở hữu (Khang Ngô). Do đó Web Client dù public vẫn có thể gửi data về an toàn tuyệt đối qua đường Web App URL.
   - Publish script này dưới dạng Web App (Anyone can access).
3. **Các Điểm Bắt Sự Kiện (Touchpoints) cần Tracking:**
   - Khi khách **Mở link lần đầu**: Log `[Anh Hùng] bắt đầu xem danh sách`.
   - Khi khách **Bấm vào 1 căn**: Log `[Anh Hùng] đang xem chi tiết nhà #1001`.
   - Khi khách **Bỏ chọn / Nhấn ❌ loại 1 căn**: Log `[Anh Hùng] đã GẠT BỎ nhà #1050 khỏi danh sách`.
   - Khi khách **Chọn tiêu chí Radar Chart**: Log `[Anh Hùng] chọn ưu tiên so sánh: [Diện tích, Hẻm xe hơi, Mặt tiền]`.
   - Khi khách **Bấm nút Zalo CTA**: Log `💥 [Anh Hùng] ĐÃ CHỐT yêu cầu đi xem nhà #1001 và #1022`.

---

## PHẦN 3: TÍNH NĂNG SO SÁNH & RADAR CHART (Trên Web Client)

### 3.1. Trạng thái Danh sách (State Management & Local Storage)
- Hệ thống sẽ quản lý 3 mảng trạng thái:
  - `activeList`: Các căn nhà khách đang xem xét (Tối đa hiển thị theo link).
  - `compareList`: Các căn khách chọn vào rổ so sánh (Tối đa 4 căn).
  - `discardedList`: Các căn khách bấm ❌ loại bỏ.
- **Bảo toàn dữ liệu (Persistence):** Toàn bộ trạng thái này sẽ được lưu liên tục vào `localStorage` của trình duyệt theo từng ID Khách Hàng. Nếu khách lỡ tay ấn F5, tắt trình duyệt, hoặc mở lại link cũ vào ngày hôm sau, hệ thống sẽ tự động lấy dữ liệu từ máy lên và **khôi phục y nguyên trạng thái cuối cùng** (căn nào đã loại vẫn nằm ở đáy, rổ so sánh vẫn giữ nguyên).
- **Trải nghiệm UI:** Bất kỳ căn nào rơi vào `discardedList` sẽ lập tức bị làm mờ (Grayscale / Opacity 40%), mất tag trạng thái và tự động trôi tuột xuống đáy danh sách. 
- **Khôi phục trạng thái:** Khách vẫn có thể bấm vào các căn "Đã loại" này để thêm lại vào biểu đồ. Khi đó, căn nhà sẽ được xoá hiệu ứng làm mờ, lấy lại màu sắc và các tag, trở về trạng thái "đang cân nhắc" (khôi phục hoàn toàn).

### 3.2. Màn Hình Cấu Hình So Sánh (Pre-Chart Selection)
- Khi khách chọn 2-4 căn và bấm nút **"So Sánh Đỉnh Cao"**:
- **Màn hình 1:** Khách được yêu cầu chọn TỐI ĐA 4 - 5 tiêu chí quan trọng nhất với họ. 
  - [ ] Giá rẻ nhất
  - [ ] Diện tích to nhất
  - [ ] Đơn giá/m² tốt nhất
  - [ ] Đường/Hẻm rộng nhất
  - [ ] Bề ngang mặt tiền to nhất
  - **[+] Khác (Tự nhập):** Cho phép khách tự gõ tiêu chí (VD: Gần siêu thị, Khu dân trí cao). Hệ thống sẽ hiện thông báo nhỏ: *"Tiêu chí [XYZ] tạm thời chưa tự động vẽ trên biểu đồ. Khang Ngô đã ghi nhận và sẽ tư vấn riêng cho anh/chị về điểm này nhé!"*. Yêu cầu này lập tức được bắn về file Tracking.
- *Bẫy Tracking:* Ngay khi khách bấm "Xác nhận tiêu chí", ta đã biết được "Khẩu vị" thật sự của khách là gì để tư vấn chốt sale sau này (Ví dụ: Biết khách ưu tiên Mặt tiền hơn Diện tích).

### 3.3. Màn Hình Radar Chart & Bảng Xếp Hạng
- **Biểu đồ Radar (Dùng thư viện Chart.js):** 
  - Vẽ đa giác với các trục là tiêu chí khách vừa chọn. Mỗi trục sẽ tự động chuẩn hoá (Normalize) tỷ lệ điểm từ 1-10 để biểu diễn đẹp nhất.
  - 4 căn nhà sẽ là 4 lớp màu trong suốt đè lên nhau (Xanh dương, Đỏ, Vàng, Tím). Khách nhìn vào sẽ thấy ngay đa giác màu nào "phình ra" nhiều nhất -> Căn đó có thông số áp đảo nhất.
- **Tính năng Loại trực tiếp trên Chart:**
  - Dưới biểu đồ có list các căn đang xem. Khách thấy căn Đỏ cùi quá, bấm ❌ loại ngay trong màn hình này. Biểu đồ mượt mà tự vẽ lại với 3 căn còn lại.
  - Có nút `+ Thêm căn khác` để cuộn xuống danh sách bên dưới lôi thêm vào biểu đồ.
- **Nút Chốt Sale Thần Thánh (CTA):**
  - Text linh động: `🚀 Đặt lịch đi xem ngay [X] căn này cùng Khang Ngô!`
  - Nút bấm sẽ tạo link Deep-link dẫn thẳng vào app Zalo, kèm sẵn text: *"Chào Khang, anh [Anh Hùng] muốn đi xem ngay Căn #1001 và Căn #1022 mà anh vừa lọc ra nè em."*

---

## LỘ TRÌNH THỰC HIỆN (INCREMENTAL DELIVERY)
Thay vì làm xong toàn bộ mới ra mắt, dự án sẽ đi theo hướng Incremental (Cuốn chiếu): Mỗi giai đoạn hoàn thành là một tính năng **có thể dùng ngay, và tracking được ngay**.

**Khởi động: Setup Hạ tầng Tracking (Nền tảng)**
- Tạo File Google Sheet `TrackingLog` (Private) và viết Google Apps Script Web App để sẵn sàng hứng Data.

**Giai đoạn 1: Link Cá Nhân & Tracking Lượt Xem**
- *Tính năng:* Thêm Form tạo Link chứa tên khách (`&c=Base64`) ngay trên Web Client (chế độ Admin `?pwd=trang`). Trên màn hình Khách, giải mã tên khách để cá nhân hoá.
- *Tracking đạt được:* Biết ngay khách có mở Link không, và đặc biệt là **khách click mở xem chi tiết căn nào** (Log: `[Anh Hùng] mở chi tiết nhà #1001`).
- 👉 *Hoàn thành GĐ 1: Anh Khang có thể gửi link xịn và đo lường được ngay "độ ấm" của khách thông qua số lần họ bấm xem chi tiết từng căn.*

**Giai đoạn 2: Bảng So Sánh Đỉnh Cao (Radar Chart)**
- *Tính năng:* Khách tick chọn tối đa 4 căn, chọn Tiêu chí (có ô tự nhập), và xem Biểu đồ Radar mạng nhện. Hệ thống tự động phân tích và highlight các thông số tốt nhất.
- *Tracking đạt được:* Biết được "Khẩu vị" mua nhà của khách (Log: `[Anh Hùng] ưu tiên so sánh: [Diện tích, Tự nhập: Sân đỗ ô tô]`).
- 👉 *Hoàn thành GĐ 2: Ra mắt Tính năng WOW, kích thích khách hàng tự tương tác và cân nhắc.*

**Giai đoạn 3: Chốt Sale (Zalo CTA)**
- *Tính năng:* Dưới Bảng so sánh (hoặc chi tiết), gắn nút mở thẳng app Zalo với tin nhắn soạn sẵn (`Khang ơi, anh Hùng muốn xem căn #1001 và #1022`).
- *Tracking đạt được:* Log lại chính xác khoảnh khắc khách quyết định xuống tiền đi xem nhà trước khi mở app Zalo.
- 👉 *Hoàn thành GĐ 3: Đóng phễu chốt Sale siêu mượt.*

**Giai đoạn 4: Tính năng "Loại Trừ" & Lưu Trạng Thái (LocalStorage)**
- *Tính năng:* Cung cấp công cụ cho phép khách bấm ❌ gạt bỏ các căn không ưng ý (làm mờ, đẩy xuống đáy) hoặc phục hồi lại. Mọi thao tác này và danh sách so sánh tự động lưu vào `localStorage` (F5 không mất).
- *Tracking đạt được:* Ghi nhận được sự chán ghét/yêu thích rõ ràng của khách đối với từng căn (Log: `[Anh Hùng] đã GẠT BỎ nhà #1050`).
- 👉 *Hoàn thành GĐ 4: Nâng cấp trải nghiệm thanh lọc hoàn hảo.*
