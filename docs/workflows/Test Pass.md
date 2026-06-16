# Quy trình xử lý "Test Pass" (Test Pass Workflow)

Tài liệu này định nghĩa quy trình chuẩn để AI thực hiện khi nhận được thông báo **"test pass"** từ Product Owner hoặc khi một tính năng đã được kiểm thử thành công và nghiệm thu thực tế trên môi trường Live.

> ⚠️ **QUY TẮC CỐT LÕI (MANDATORY RULE):** AI tuyệt đối **KHÔNG ĐƯỢC TỰ Ý** chạy quy trình "Test Pass" này ngay sau khi vừa code xong. Quy trình này **chỉ được phép thực hiện** sau khi tính năng đã được deploy thành công lên live (tuân thủ quy trình deploy tại [system_architecture_deployment.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/system_architecture_deployment.md)), báo cáo ở trạng thái `done` (hoặc gửi bản nháp chờ duyệt), và nhận được **sự xác nhận nghiệm thu trực tiếp ("test pass" / duyệt)** từ phía Product Owner (Khang Ngô).
>
> **⚠️ NGUYÊN TẮC ĐỒNG BỘ LIÊN TỤC:** AI bắt buộc phải thực hiện cập nhật và đồng bộ hóa thông tin sang tất cả các tài liệu liên quan bên dưới **ngay lập tức** khi nhận được xác nhận nghiệm thu.


---

## 🔍 Quy chuẩn Thiết kế & Bằng chứng Kiểm thử E2E Admin (Admin E2E Verification & Evidence Rules)

Đối với các User Stories liên quan đến giao diện Admin (như Curation, Image Editor, Pool Cào, Lưu Sheets...), AI bắt buộc phải tuân thủ quy chuẩn thiết kế E2E và ghi nhận bằng chứng nghiệm thu (Test Evidence) như sau:

### 1. Cách thiết kế E2E ở View Admin (`scratch/test_e2e_curation.py`)
Hệ thống kiểm thử E2E của Admin được thiết kế giả lập hoàn chỉnh quy trình quản lý của Admin bằng Playwright (Python) theo kiến trúc cô lập:
- **Giả lập môi trường (Sandboxed Environments):** Khởi chạy một Server HTTP cục bộ động trên cổng ngẫu nhiên để phục vụ các file tĩnh trong thư mục dự án mà không ảnh hưởng đến Production.
- **Mock Google Identity Services & Sheets API:** Sử dụng Playwright Route Interception (`page.route`) để đánh chặn toàn bộ các yêu cầu OAuth đăng nhập Google và Sheets API. Hệ thống sẽ tự động trả về dữ liệu giả lập (Mocked Rows) và bắt gói tin ghi đè (HTTP PUT Payload) để xác minh tính chính xác của dữ liệu Curation gửi đi.
- **Kiểm thử Responsive đa thiết bị:**
  - **Desktop View (1280x800):** Giả lập luồng mở rộng Accordion chỉnh sửa, nhấp nút **Tự động điền AI** (`btnAutoFillCuration`), xác minh logic bật/tắt hiển thị của nút **Lên sóng** ⚡, thực hiện hoán đổi/bật tắt tag (Public/Sổ đỏ) trong Carousel Image Editor, nhấp Lên sóng và xác nhận Payload lưu trữ Sheets hợp lệ.
  - **Mobile View (375x812, hasTouch=True):** Kiểm tra tính tương thích và khả năng đóng mở Drawer, nhấp các tiêu đề Accordion để kiểm tra hiển thị Drawer trên màn hình dọc nhỏ của điện thoại di động.

### 2. Quy tắc lưu bằng chứng nghiệm thu (Verification Evidence)
- Mọi phiên kiểm thử E2E Admin phải được chụp lại màn hình ở cả hai view Desktop và Mobile làm bằng chứng nghiệm thu thực tế.
- Các ảnh chụp bằng chứng nghiệm thu phải được tự động lưu vào thư mục `docs/workflows/assets/`.
- Dưới đây là bằng chứng nghiệm thu thực tế khi chạy thành công bộ test **`scratch/test_e2e_curation.py`**:

#### 💻 Giao diện Admin Curation trên Desktop (E2E Pass):
![Admin Curation Desktop](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/workflows/assets/admin_curation_desktop.png)

#### 📱 Giao diện Admin Curation trên Mobile (E2E Pass):
![Admin Curation Mobile](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/workflows/assets/admin_curation_mobile.png)

---

## Các bước thực hiện tự động (Automated Steps)

Khi có thông báo nghiệm thu thành công hoặc kiểm thử đạt (ví dụ: "test pass" cho một User Story cụ thể):

### 0. Chạy Unit Test & E2E Integration Test (BẮT BUỘC - MANDATORY GATE)
Trước khi thực hiện gộp bất kỳ đoạn code nào về nhánh chính `main` ổn định, AI **bắt buộc** phải chạy bộ công cụ kiểm thử tự động (Unit Tests & E2E Tests) để xác minh các Rule sống còn và tính toàn vẹn giao diện:
- Chạy bộ script test rules (ví dụ: `python test_rules.py` hoặc bộ test tương ứng).
- Chạy bộ script kiểm thử tích hợp E2E giả lập hành vi người dùng bằng Python trên trình duyệt không đầu (ví dụ: `python scratch/test_e2e_[US-ID].py` hoặc bộ test E2E tương ứng của US) chạy song song trên **cả 2 giao diện Desktop và Mobile** để kiểm thử độ tương thích responsive trên môi trường staging/local test. Các script này bắt buộc phải cài đặt cấu hình mock Admin session và mock API Google Sheets để đảm bảo chạy độc lập.
- **Lưu bằng chứng kiểm thử (E2E Test Evidence):** Bộ kiểm thử E2E tự động chụp màn hình tại các bước cần verify (ví dụ: khi modal mở rộng hoặc khi lưu thành công), và tự động lưu tệp hình ảnh vào thư mục `docs/workflows/assets/` với định dạng tên `[US-ID]_desktop.png` và `[US-ID]_mobile.png` để làm chứng cứ nghiệm thu.
- **Ranh giới an toàn (Hard CI Gate):**
  - **100% các ca test (cả Unit Test và E2E Test) PASS:** AI mới được phép chuyển sang Bước 1 (Gộp nhánh Git).
  - **Bất kỳ ca test nào FAIL** (ví dụ: lỗi chuẩn hóa địa chỉ, lỗi giao diện vỡ, lỗi bộ lọc sập, lộ PII, thiếu comment đầu file Apps Script...): AI **tuyệt đối KHÔNG được gộp code**, lập tức tạm dừng và báo cáo chi tiết log lỗi kiểm thử cho người dùng để sửa đổi.

### 1. Dọn dẹp Nhánh Git ảo (Git Cleanup - Tự động)
Vì code của US đã được tự động merge và deploy trực tiếp lên nhánh `main` (Production) ở cuối pha Triển khai/Planning để phục vụ việc PO kiểm thử trực tiếp trên Live, ở bước này AI chỉ thực hiện dọn dẹp nhánh ảo local:
- Xóa nhánh ảo local để làm sạch máy:
  ```powershell
  git branch -d feature/US-[ID]
  ```
- *Lưu ý về Rollback:* Nếu trong quá trình PO kiểm thử trên Live phát hiện lỗi lớn và hệ thống buộc phải rollback về commit cũ, AI bắt buộc phải checkout lại nhánh ảo từ commit rollback để sửa đổi, hoàn thiện và deploy lại trước khi chạy lại quy trình nghiệm thu này.

  > [!NOTE]
  > Việc đóng gói và deploy tính năng lên live cần tuân thủ hướng dẫn và quy chuẩn bảo mật trong [system_architecture_deployment.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/system_architecture_deployment.md).

### 2. Cập nhật tài liệu User Story tương ứng
- Tìm file `.md` của User Story tương ứng trong thư mục `docs/stories/_inbox/`.
- Thay đổi thuộc tính `status` ở phần frontmatter từ `done` hoặc `draft` sang `accepted`.
  ```yaml
  status: accepted
  ```

### 2. Cập nhật Stories Index (`docs/stories/INDEX.md`)
- Cập nhật số liệu thống kê (Stats):
  - Giảm số lượng `done` (hoặc `in-progress` / `draft`) đi 1.
  - Tăng số lượng `accepted` lên 1.
- Trong bảng **All Stories**, tìm dòng của User Story tương ứng và đổi cột **Status** từ `done` sang `accepted`.
- Trong phần **By Keyword** ở dưới, cập nhật trạng thái bên cạnh mã US từ `(done)` hoặc `(backlog)` thành `(accepted)`.

### 3. Cập nhật Bảng điều khiển dự án (Project Dashboard — `SOURCE_OF_TRUTH.md`)
- Tìm mục **Section 9: 🚀 TÍNH NĂNG CẦN THÊM (Backlog)**.
- Thêm hoặc đánh dấu tick hoàn thành `[x]` bên cạnh User Story tương ứng.
- Cập nhật **Section 7: 🔄 LỊCH SỬ THAY ĐỔI (Change Log)** bằng cách bổ sung nhật ký cập nhật cho phiên làm việc hiện tại, ghi nhận rõ mã US, các thay đổi thực tế đã deploy và tình trạng nghiệm thu.

### 4. Dọn dẹp kế hoạch phiên tiếp theo (`docs/NEXT_SESSION.md`)
- Xóa bỏ hoặc chuyển trạng thái các đầu việc vừa hoàn thành khỏi file `NEXT_SESSION.md` để đảm bảo file này luôn phản ánh chính xác các công việc tồn đọng thực sự cho phiên làm việc tiếp theo.
- Cập nhật mục **`## 3. Các file bị tác động trong phiên vừa qua`** để ghi nhận lại các file đã sửa đổi phục vụ cho tính năng này.
- Cập nhật mô tả nhiệm vụ cho phiên tiếp theo dựa trên backlog thực tế.

### 5. Đo lường Lợi ích & Ghi nhận trôi lệch giá trị (Benefit Realization Check)
- **Hành động bắt buộc:** AI nhắc nhở PM tiến hành đo lường chỉ số thực tế (ví dụ: tốc độ xử lý Curator App, độ chính xác chuẩn hóa địa chỉ) dựa trên các KPIs đã thiết lập trong [Value Management Plan](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/business_docs/value_management_plan.md).
- So sánh hiệu năng thực tế với baseline.
- **Nếu có trôi lệch giá trị (KPI drift):** Phối hợp cùng PM Trang thảo luận giải pháp kỹ thuật hiệu chỉnh và ghi nhận một dòng log giải pháp khắc phục vào **Alignment & Evolution Log (Mục 3)** của Value Management Plan để làm cơ sở tối ưu hóa ở session tiếp theo.

### 6. Đúc kết Bài học Kinh nghiệm, Thực tiễn Tốt & Tiến hóa Bộ Kiểm Thử (Retro, Good Practices & Harness Evolution)
- **Hành động bắt buộc:** AI hỗ trợ PM mở và rà soát mục **`## 🧠 Retro, Lessons Learned & Good Practices`** của User Story vừa hoàn thành để:
  1. Thống kê nhanh các sự cố phát sinh thực tế (Incidents) và nguyên nhân gốc rễ để chuẩn bị cho buổi họp rút kinh nghiệm (Retro) định kỳ của dự án.
  2. Tổng hợp các bài học tốt (Good Practices) đúc kết được trong quá trình phát triển nhằm phòng tránh lỗi tương tự cho các US sau.
  3. Tự động cập nhật bộ kiểm thử tự động (Unit Tests) để phủ các trường hợp biên, lỗi phát sinh ghi nhận trong Retro nhằm đảm bảo tính năng không bao giờ bị hỏng lại (regression immunity).
  4. Đề xuất cập nhật các Good Practices mang tính quy chuẩn sống còn vào [BDS-AGENTS.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/BDS-AGENTS.md) nếu có để không ngừng cải tiến năng lực của AI Agent.

---

*Quy trình này được thiết lập và tự động hóa bởi Antigravity AI Assistant. Nâng cấp chuẩn LAAF v1.1 (2026-05-29).*
