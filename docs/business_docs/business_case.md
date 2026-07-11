# Business Case (Bản Thuyết Minh Kinh Doanh Dự Án BDS Khang Ngô)

Tài liệu này định nghĩa lý do thương mại, tính khả thi và phân tích chi phí - lợi ích (Cost-Benefit Analysis) để quyết định đầu tư và vận hành hệ thống **BDS Khang Ngô Nhà Phố** do **Trang (PO / System Designer)** quản lý và anh **Khang Ngô (End-User)** đầu tư và sử dụng.

---

## 🎯 1. Nhu Cầu Kinh Doanh & Mục Tiêu Chiến Lược (Business Need & Strategic Alignment)
*   **Vấn đề / Cơ hội:**
    *   Hàng ngày, lượng thông tin nguồn bất động sản (từ Thiên Khôi và các đối tác) đổ về rất lớn dưới dạng tin nhắn thô, HTML phức tạp, chứa nhiều rác thông tin và thiếu cấu trúc.
    *   Việc lọc, phân tích và biên tập thủ công một căn nhà phố mất trung bình từ 5 đến 10 phút, gây nghẽn rổ hàng và giảm tốc độ chốt sale.
    *   Dữ liệu chưa được chuẩn hóa tên đường (ví dụ: CMT8, 3/2 viết lộn xộn) khiến việc so sánh và định giá gặp khó khăn.
*   **Mục tiêu dự án:**
    *   Tự động hóa hoàn toàn quy trình cào, trích xuất và lọc sạch thông tin bằng AI GenAI (Curator System).
    *   Rút ngắn thời gian biên tập rổ hàng từ 5 phút xuống dưới 30 giây cho mỗi căn.
    *   Tạo hệ thống đồng bộ dữ liệu real-time giữa SQLite local và Google Sheets để phục vụ phân tích Radar Chart so sánh giá.
*   **Sự phù hợp chiến lược:** Nâng cao năng lực cạnh tranh cốt lõi của Khang Ngô Nhà Phố thông qua việc sở hữu rổ hàng sạch nhất, tốc độ cập nhật nhanh nhất thị trường.

---

## 📈 2. Phân Tích Chi Phí - Lợi Ích (Cost-Benefit Analysis - CBA)
*   **Chi phí dự kiến (Costs):**
    *   *Chi phí hạ tầng:* Phí sử dụng API Key GenAI (Gemini 1.5 Pro / Flash) ước tính khoảng $10 - $20/tháng. Phí hosting Vercel & Firebase nằm trong gói Free/Hobby.
    *   *Chi phí phát triển:* Phí quản lý PM (Trang) và lập trình AI (nội bộ).
*   **Lợi ích hữu hình & Vô hình (Benefits):**
    *   *Lợi ích hữu hình:* 
      - Tiết kiệm 80% thời gian curation hàng ngày của anh Khang Ngô (tương đương tiết kiệm ~1.5 giờ làm việc/ngày, trị giá ~5 triệu VNĐ/tháng quy đổi).
      - Tiết kiệm hoàn toàn chi phí thuê cộng tác viên nhập liệu thủ công (~6 triệu VNĐ/tháng).
      - Rút ngắn thời gian đưa tin bài lên live, tăng tỷ lệ tiếp cận khách hàng nhanh gấp 10 lần.
    *   *Lợi ích vô hình:*
      - Tránh rò rỉ dữ liệu nhạy cảm của khách hàng và chủ nhà nhờ bộ lọc PII tự động trước khi gửi qua API bên thứ ba.
      - Chuẩn hóa 100% dữ liệu tên đường về mã định danh chuẩn (TTMC, HTB) giúp vẽ biểu đồ radar chart so sánh chính xác và chuyên nghiệp.

---

## 📊 3. Tiêu Chí Thành Công & KPIs (Success Criteria)
*   **Tiêu chí thành công tài chính:** Thời gian thu hồi vốn API đầu tư trong vòng 1 tháng đầu tiên vận hành thực tế. ROI đạt > 200% sau 3 tháng.
*   **Tiêu chí thành công phi tài chính:**
    *   Tốc độ phản hồi của Curator App đạt dưới 2 giây.
    *   Tỷ lệ trích xuất AI đúng định dạng địa chỉ, không bị ảo tưởng (Hallucination) đạt 100%.
    *   Bảo vệ PII đạt tuyệt đối 100% (không lọt số điện thoại chủ nhà ra API ngoài).

---

## 🔄 4. Nhật Ký Tiến Hóa Của Business Case (Evolution Log)

| Phiên bản | Ngày cập nhật | Người điều chỉnh | Nội dung thay đổi / Điều chỉnh mục tiêu | Lý do điều chỉnh & Tác động |
|---|---|---|---|---|
| **v1.0** | 2026-05-29 | PM/Trang | Khởi tạo Business Case ban đầu. | Thiết lập mục tiêu cơ sở (Baseline) phục vụ hệ thống Curation và so sánh giá. |

---

*Tài liệu này được bảo trì bởi PM/Trang và là chốt chặn cao nhất để đảm bảo dự án luôn đem lại giá trị thực tế cho anh Khang Ngô.*
