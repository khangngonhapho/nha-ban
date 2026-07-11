# Quy trình Nạp Context Dự Án (Load Context Workflow)

Tài liệu này định nghĩa quy trình chuẩn để AI tự động thực hiện nạp toàn bộ ngữ cảnh (context) kỹ thuật và nghiệp vụ của dự án **BDS Khang Ngô Nhà Phố** khi bắt đầu một phiên làm việc (session) mới. 

Khi người dùng gọi file này (ví dụ qua cú pháp `@Load Context.md`), AI bắt buộc phải đọc các file đích bên dưới để đồng bộ thông tin mà không cần người dùng phải liệt kê thủ công từng file.

---

## 🚨 Giao thức Quản lý & Bảo vệ Nhánh Git (Git Branch Protection Protocol - BẮT BUỘC)

Trước khi thực hiện nạp bất kỳ tài liệu nào bên dưới, AI **bắt buộc** phải thực hiện quy trình kiểm tra và căn chỉnh nhánh Git sau:

1. **Xác định US Mục tiêu:** AI đọc câu lệnh của người dùng để xác định mã US đang cần làm việc (ví dụ: `US-045`). Nếu câu lệnh không ghi rõ mã US, AI bắt buộc mở tệp [NEXT_SESSION.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/NEXT_SESSION.md) để tìm danh sách US đang ở trạng thái `in-progress`. Nếu có nhiều hơn 1 US dở dang, AI **phải dừng lại và hỏi người dùng** xác nhận US mục tiêu trước khi đi tiếp.
2. **Kiểm tra Nhánh Hiện tại:** AI dùng công cụ `run_command` chạy `git branch` để xác định nhánh Git hiện tại dưới máy local.
3. **Thực hiện Căn chỉnh & Gói Code tự động:**
   - **Trường hợp 1 (Nhánh đã khớp):** Nếu nhánh hiện tại đã là `feature/US-[ID]`, AI tiếp tục bước nạp context ở dưới.
   - **Trường hợp 2 (Nhánh khác biệt - Lệch US):** Nếu nhánh hiện tại là `feature/US-[Cũ]` hoặc đang ở `main` nhưng có thay đổi dở dang:
     a. AI tự động chạy lệnh commit nháp để bảo toàn tuyệt đối tiến độ dở của US cũ:
        ```powershell
        git add .
        git commit -m "draft: [US-Cũ] tạm cất tiến độ trước khi chuyển sang US-[Mới]"
        ```
     b. AI tự động chuyển sang nhánh US mới (hoặc tạo mới từ `main` nếu làm lần đầu):
        ```powershell
        git checkout feature/US-[ID_Mới]
        ```
     c. Báo cáo rõ ràng việc đã cất code cũ và kéo code dở mới ra thành công trước khi nạp tài liệu.

---

## 🚨 Chỉ thị Bắt buộc cho AI (Mandatory Instructions for AI)

Khi nhận được yêu cầu đọc hoặc nạp context từ file này, AI **BẮT BUỘC** phải sử dụng công cụ `view_file` để đọc tuần tự toàn bộ các file cốt lõi sau đây trước khi phản hồi người dùng:

1.  **[BDS-AGENTS.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/BDS-AGENTS.md)**
    - *Mục đích:* Nắm rõ các luật sống còn (chuẩn hóa địa chỉ, xử lý số nhà, comment đầu file apps script, cấu hình Git local Vercel, sizing, DoR/DoD, và AI KPIs).

2.  **[docs/NEXT_SESSION.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/NEXT_SESSION.md)**
    - *Mục đích:* Nắm bắt trạng thái dừng của phiên trước, các User Story vừa xong, kế hoạch hành động tiếp theo, và các tệp bị tác động gần nhất.

3.  **[docs/stories/INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md)**
    - *Mục đích:* Xem danh sách User Story, ID lớn nhất hiện tại để tính ID mới (`ID_mới = ID_lớn_nhất + 1`), và phân loại nghiệp vụ theo Keyword.

4.  **[docs/business_docs/business_case.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/business_docs/business_case.md)**
    - *Mục đích:* Nắm vững nhu cầu kinh doanh, phân tích chi phí - lợi ích (CBA) của API, tiêu chí thành công tài chính/phi tài chính và Evolution Log.

5.  **[docs/business_docs/value_management_plan.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/business_docs/value_management_plan.md)**
    - *Mục đích:* Nắm bắt các cam kết lợi ích (tốc độ curation, chuẩn hóa), KPIs đo lường giá trị thực tế cho anh Khang Ngô và Alignment Log.

6.  **[SOURCE_OF_TRUTH.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/SOURCE_OF_TRUTH.md)**
    - *Mục đích:* Bản đồ thông tin dự án, cấu hình kỹ thuật, schema cơ sở dữ liệu, và nhật ký lịch sử thay đổi (Change Log).

7.  **[docs/data_dictionary.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/data_dictionary.md)**
    - *Mục đích:* Đọc từ điển dữ liệu chính thức, hiểu rõ cấu trúc cột của Pool, Source và mối liên hệ đồng bộ dữ liệu.

8.  **[docs/data_standardization_rules.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/data_standardization_rules.md)**
    - *Mục đích:* Nắm vững các nguyên tắc tiền xử lý và chuẩn hóa dữ liệu đầu vào (TTMC, HTB, lọc PII).

9.  **[docs/project_glossary.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/project_glossary.md)**
    - *Mục đích:* Hiểu rõ bảng thuật ngữ chuyên ngành dự án (Jargon Dictionary) để thống nhất ngôn ngữ khi viết logic.

10. **[docs/system_architecture_deployment.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/system_architecture_deployment.md)**
    - *Mục đích:* Nắm bắt bản đồ kiến trúc kỹ thuật hệ thống, hướng dẫn triển khai tính năng di động và quy trình deploy.

11. **[plan_tracking_so_sanh.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/plan_tracking_so_sanh.md)** (Đọc nếu liên quan đến Radar Chart)
    - *Mục đích:* Hiểu lộ trình và đặc tả kỹ thuật của tính năng So sánh Radar Chart & Hệ thống Tracking.

12. **[docs/good_practices.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/good_practices.md)**
    - *Mục đích:* Nắm bắt toàn bộ các bài học xương máu (Lessons Learned) và thực tiễn lập trình tốt (Good Practices) tích lũy qua các User Story để kế thừa tức thì trong session mới.

---

## 🛠️ Hướng dẫn dành cho Người dùng (User Guide)

Để khởi động một phiên làm việc mới nhanh nhất, anh/chị chỉ cần gõ một trong các câu lệnh sau:

*   Cú pháp nhanh:
    > `nạp context @[01_PROJECTS/BDS-KhangNgo/docs/workflows/Load Context.md]`
*   Hoặc câu lệnh tự nhiên:
    > `Đọc file d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\docs\workflows\Load Context.md để bắt đầu phiên mới`

---

*Quy trình này được thiết lập và tự động hóa bởi Antigravity AI Assistant. Nâng cấp chuẩn LAAF v1.1 (2026-05-29).*
