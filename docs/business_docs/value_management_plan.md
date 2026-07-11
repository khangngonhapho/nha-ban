# Value Management Plan (Kế Hoạch Quản Lý Giá Trị Dự Án BDS Khang Ngô)

Tài liệu này quy định cách thức đo lường, giám sát và tối ưu hóa các giá trị/lợi ích thực tế (value/benefits) mà dự án **BDS Khang Ngô Nhà Phố** mang lại cho khách hàng và người sử dụng cuối (End-User - Anh Khang Ngô).

---

## 💎 1. Khung Định Nghĩa Giá Trị (Value Realization Framework)

| Lợi ích mục tiêu | Chỉ số đo lường (KPI) | Thời điểm đo lường | Người chịu trách nhiệm |
|---|---|---|---|
| **1. Tốc độ biên tập tin bài** | Giảm thời gian xử lý 1 căn nhà từ 5-10 phút xuống dưới 30 giây. | Hàng tuần sau khi deploy | PM / Trang |
| **2. Độ chính xác chuẩn hóa địa chỉ** | Tỷ lệ tự động chuyển đổi tên đường CMT8 ➔ TTMC, 3/2 ➔ HTB đạt 100%. Lọc bỏ số nhà phụ sau dấu "+" đạt 100%. | Hàng tuần | AI Agent |
| **3. Bảo mật PII & Tin bài sạch** | Tỷ lệ lọc sạch SĐT, thông tin liên hệ nhạy cảm trước khi gửi API LLM đạt 100%. Tin bài sinh ra không lỗi chính tả đạt > 98%. | Hàng tháng | PM / Trang & Anh Khang Ngô |
| **4. Hiệu quả định giá so sánh** | Biểu đồ Radar Chart hiển thị chính xác dữ liệu định giá so sánh rổ hàng để hỗ trợ chốt sale nhanh. | Định kỳ hàng tháng | End-User / Anh Khang Ngô |

---

## 📈 2. Quy Trình Giám Sát & Tối Ưu Hóa Giá Trị (Value Monitoring & Drift Management)

Để đảm bảo giá trị dự án thực sự đạt được và tránh hiện tượng trôi lệch giá trị (KPI drift), PM và AI thực hiện quy trình giám sát sau:
1.  **Thu thập dữ liệu thực tế:** Sau mỗi đợt bàn giao tính năng (Test Pass), PM Trang tiến hành thu thập dữ liệu đo lường thực tế từ anh Khang Ngô (ví dụ: tốc độ biên tập thực tế, độ hài lòng đối với tin public).
2.  **Đánh giá độ lệch (Variance Analysis):** So sánh giá trị đạt được thực tế với baseline trong mục 1.
3.  **Điều chỉnh Kế hoạch & Giải pháp (Value Realignment):** Nếu giá trị đạt được thấp hơn kỳ vọng (ví dụ: AI nhận diện sai tên đường CMT8 hoặc bỏ sót PII):
    *   AI chủ động phân tích nguyên nhân và đề xuất điều chỉnh lại giải pháp kỹ thuật, tinh chỉnh prompt GenAI hoặc cập nhật lại bộ Regex lọc thông tin.
    *   Cập nhật thay đổi này trực tiếp vào file User Story liên quan và lưu vết tiến hóa của Plan tại mục 3 dưới đây.

---

## 🔄 3. Nhật Ký Điều Chỉnh Kế Hoạch Giá Trị (Alignment & Evolution Log)

| Phiên bản | Ngày cập nhật | Người điều chỉnh | Lợi ích/KPI điều chỉnh | Giải pháp điều chỉnh để đạt giá trị thực tế |
|---|---|---|---|---|
| **v1.0** | 2026-05-29 | PM/Trang | Khởi tạo Value Management Plan ban đầu. | Thiết lập khung đo lường lợi ích cơ sở (Baseline). |
| **v1.1** | 2026-05-31 | AI Agent & PM | KPI 3 (Bảo mật PII & Tin bài sạch) & KPI 1 (Tốc độ biên tập) | Nghiệm thu US-054 & US-055: Di cư 4.872 ảnh Sổ siêu nét không nén lên Cloudinary; bảo mật tuyệt đối PII bằng cách loại bỏ triệt để ảnh Sổ khỏi avatar/cover danh sách Card Admin & preview công khai khách hàng. |
| **v1.2** | 2026-06-03 | AI Agent & PM | Duy trì phiên đăng nhập & Tránh mất mát dữ liệu nhập (UX Session Continuity) | Nghiệm thu US-061: Loại bỏ 100% tình trạng mất dữ liệu nhập trên form biên tập do session timeout 1 giờ bằng cách triển khai hàng đợi token và silent refresh ngầm GSI, kèm popup interactive login fallback không tải lại trang. |
| **v1.3** | 2026-06-04 | AI Agent & PM | Độ chính xác chia sẻ & Đồng bộ dữ liệu (Share Integrity & Data Sync Accuracy) | Nghiệm thu US-070: Sửa sạch 170 dòng trùng System ID, đồng bộ Mã Khang Ngô giữa Pool và Source. Chuyển đổi mã hóa link gửi khách sang Base64URL của danh sách System ID, đảm bảo khách hàng xem đúng 100% danh sách căn được chọn. |
| **v1.4** | 2026-06-07 | AI Agent & PM | Tối ưu diện tích hiển thị & Hiệu suất biên tập (Laptop View Space & Curation Efficiency) | Nghiệm thu US-074: Mở rộng modal lên 1100px và hiển thị grid 2 cột song song (thông tin thô và Curation Admin) trên laptop/desktop. Giải quyết 100% visual bugs xẹp ảnh đại diện, rò rỉ grid panel khi đóng và cuộn lồng nhau (nested scrollbar). |
| **v1.5** | 2026-06-08 | AI Agent & PM | KPI 2 (Độ chính xác bộ lọc & độ sạch bộ lọc Phường) | Nghiệm thu US-077: Loại bỏ hoàn toàn dòng header "phuong"/"UAN" khỏi bộ lọc và listings. Chuẩn hóa dấu tiếng Việt (NFC/NFD) và sắp xếp hiển thị 19 phường nghiệp vụ ưu tiên hàng đầu ở cả hai chế độ. |
| **v1.6** | 2026-06-08 | AI Agent & PM | KPI 1 (Tốc độ biên tập) & KPI 3 (Bảo mật PII & Tin bài sạch) | Nghiệm thu US-078: Tích hợp nút Tự động điền AI trong Pool sử dụng Master Prompt Trà Mi; chia nhỏ JSON schema để sinh đầy đủ Tiêu đề phụ 🏩; tự động loại bỏ markdown **; và chặn lộ số nhà thô (bảo mật địa chỉ) bằng cảnh báo bảo mật số nhà động. |
| **v1.7** | 2026-06-08 | PM/Trang | Hiệu suất Curation & Bảo mật (Curation Celerity & Media Security) | Nghiệm thu US-079: Tích hợp nút Tải toàn bộ hình ảnh căn nhà dạng các file ảnh riêng lẻ (không nén ZIP, đặt tên [SystemID]-[STT]), loại bỏ hoàn toàn các ảnh sơ đồ thửa đất / sổ đỏ nhạy cảm để bảo vệ quyền riêng tư và thông tin nội bộ của chủ nhà. |
| **v1.8** | 2026-06-15 | AI Agent & PM | KPI 2 (Độ chính xác bộ lọc nâng cao & tốc độ tìm kiếm) | Nghiệm thu US-094B: Cô lập module bộ lọc & tìm kiếm thông minh tiếng Việt AND ('+') sang lego_filters.js, giúp giảm thiểu đáng kể mã lệnh trong index.html và tối ưu hóa tốc độ tải trang, đảm bảo 100% các bộ lọc quận, phường, đường nâng cao hoạt động chuẩn xác và mượt mà. |
| **v1.9** | 2026-06-16 | AI Agent & PM | KPI 1 (Tốc độ tải trang) & Trải nghiệm giao diện đa thiết bị (Page Load & Multi-device UI Performance) | Nghiệm thu US-094E: Hoàn tất dọn dẹp index.html (giảm xuống dưới 170 dòng script), nạp toàn bộ các module helper & mock qua CDN cache-busting (?v=...), và sửa hoàn chỉnh bố cục định vị Speed Dial Actions cố định trên Mobile, tối ưu hóa tốc độ tải trang chủ và mang lại trải nghiệm điều hướng mượt mà, đồng nhất 100% E2E Playwright. |
| **v1.10** | 2026-06-17 | AI Agent & PM | KPI 1 (Tốc độ biên tập) & KPI 2 (Hiển thị dữ liệu & Curation động) | Nghiệm thu US-096B: Triển khai cơ chế bóc tách cột Google Sheet động, nhận diện Spreadsheet cấu hình active pool từ backend (`/api/config`), hiển thị ô nhập hẻm mới `Custom_Rong_Hem` trên Form Admin với fallback tự động về hẻm thô và sửa hiển thị Carousel sơ đồ thửa đất/mặt tiền, giúp Admin tải và quản lý thông số hẻm tùy biến an toàn. |

---

*Kế hoạch này được cập nhật liên tục để đảm bảo dự án không chỉ hoàn thành đúng hạn, đúng code mà phải thực sự đem lại giá trị và hiệu quả kinh doanh cao nhất cho anh Khang Ngô.*
