# Quy trình Lập Kế Hoạch & Triển Khai (Planning & Implementation Workflow)

Tài liệu này định nghĩa quy trình chuẩn chỉnh, chặt chẽ để AI thực hiện lập kế hoạch cùng Product Owner (PO) từ khâu chọn Backlog, thiết kế giải pháp toàn diện, triển khai cho đến nghiệm thu cuối cùng.

**⚠️ NGUYÊN TẮC BẮT BUỘC:** Ở mỗi bước chuyển đổi trạng thái hoặc cập nhật thông tin của công việc, AI **phải lập tức đồng bộ hóa** thông tin sang toàn bộ các tài liệu liên quan (`INDEX.md`, `NEXT_SESSION.md`, `SOURCE_OF_TRUTH.md`). Tuyệt đối không trì hoãn đến cuối phiên.

---

## 🚨 Quy trình Thực hiện Chi tiết (Step-by-Step Flow)

Khi kích hoạt phiên làm việc lập kế hoạch (Planning):

### Bước 1: Liệt kê danh sách các Backlog hiện có
- AI đọc file chỉ mục [INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md).
- Trích xuất toàn bộ các User Story đang ở trạng thái `backlog` (hoặc `draft`).
- Hiển thị danh sách này một cách tường minh cho PO chọn (gồm ID, Title, Size sơ bộ, và tóm tắt User story).

### Bước 2: PO lựa chọn User Story để triển khai
- PO phản hồi chọn 1 US từ danh sách để bắt đầu thiết kế và chuẩn bị phát triển.

### Bước 3: Kích hoạt trạng thái đang thực hiện & Đồng bộ tài liệu (Tự động Tạo Nhánh Git)
- AI mở file của US được chọn tại `docs/stories/_inbox/`.
- Cập nhật trường `status` ở frontmatter thành `in-progress` (hoặc `draft`).
- **🚨 Quản lý & Căn chỉnh Nhánh Git ảo (Tự động):**
  - AI tự động chạy `git branch` kiểm tra xem nhánh `feature/US-[ID]` đã tồn tại chưa.
  - Nếu chưa có, AI đề xuất chạy lệnh tạo nhánh độc lập từ bản chạy ổn định `main`:
    ```powershell
    git checkout -b feature/US-[ID]
    ```
  - Nếu đã có nhánh nhưng máy đang ở nhánh khác: AI tự động chạy lệnh commit draft lưu tiến độ nhánh cũ, rồi checkout sang nhánh đúng `feature/US-[ID]`.
- **Cập nhật tài liệu liên quan ngay lập tức:**
  - **Stories Index (`docs/stories/INDEX.md`):** Tìm dòng US đó trong bảng `All Stories` và đổi cột **Status** sang `in-progress`.
  - **Kế hoạch phiên tiếp theo (`docs/NEXT_SESSION.md`):** Đưa US này vào mục **`## 2. Kế hoạch hành động phiên tiếp theo (Action Plan)`** dưới dạng nhiệm vụ đang triển khai (`in-progress`).

### Bước 4: Thiết kế Giải pháp & Lập Kế hoạch Nghiệm thu (Strategic Value & Solution Design)
- **Kiểm tra chuẩn DoR:** AI đối chiếu US được chọn để đảm bảo đã đạt **Definition of Ready** (có ít nhất 2 tiêu chí Acceptance rõ ràng, xác định rõ luồng In/Out hoặc UI chuẩn). Nếu thiếu, phải báo cáo PO để bổ sung tiêu chí nghiệm thu trước khi thiết kế giải pháp kỹ thuật.
- **Strategic Value & KPI Alignment Check:** AI bắt buộc đối chiếu giải pháp kỹ thuật đề xuất với các KPIs cam kết trong [Value Management Plan](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/business_docs/value_management_plan.md) và mục tiêu chiến lược trong [Business Case](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/business_docs/business_case.md) để đảm bảo prompt/code GenAI được sinh ra phục vụ mục tiêu giá trị (như tốc độ xử lý nhanh, bảo vệ PII, định dạng đường chuẩn).
- AI nghiên cứu sâu mã nguồn và điền đề xuất thiết kế toàn diện trực tiếp vào các mục trong file US hiện tại (**TUYỆT ĐỐI KHÔNG** tạo thêm các file local rời rạc như `current_task.md` hay `task.md` ở ngoài):
  - **Solution:** Chi tiết cấu hình, Input/Output, thuật toán xử lý chính. **⚠️ BẮT BUỘC** đối chiếu thiết kế cấu trúc dữ liệu với [Data Dictionary](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/data_dictionary.md), đối chiếu logic tiền xử lý với [Data Standardization Rules](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/data_standardization_rules.md) (quy tắc chuẩn hóa CMT8->TTMC, 3/2->HTB, loại bỏ số nhà phụ, lọc PII) và tuân thủ các quy tắc di động trong [System Architecture Guide](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/system_architecture_deployment.md).
  - **Implementation Plan:** Chi tiết các bước tiếp cận và phương án triển khai kỹ thuật được điền vào mục `## 📋 Implementation Plan` (bắt buộc đối với các task Size M/L/XL). Ưu tiên sơ đồ hóa Mermaid kèm mô tả.
  - **Task Checklist (TODO):** Thiết lập danh sách đầu việc cần làm với các checkbox `[ ]` và `[x]` vào mục `## 📝 Task Checklist` để PO theo dõi tiến độ tức thời.
  - **Verification Plan:** Các kịch bản và bước kiểm thử chi tiết. Đối với các tính năng GenAI, **bắt buộc** thiết lập các chỉ số định lượng GenAI KPIs và kiểm soát giới hạn lỗi (Limit Controls).
  - **🚨 Quy tắc Đồng bộ Kế hoạch Triển khai (Strict Plan Synchronization - BẮT BUỘC):** Mỗi khi file đề xuất `implementation_plan.md` (artifact) được tạo hoặc cập nhật để PO duyệt, AI bắt buộc phải đồng bộ và cập nhật tương ứng vào file US gốc (`US-XXX.md` nằm trong `docs/stories/_inbox/`). Các mục bắt buộc đồng bộ bao gồm: Chiến lược & Cơ chế (ví dụ: bảo toàn ảnh, đối chiếu thay đổi), Giải pháp kỹ thuật & Quy tắc dữ liệu (Technical Solution), User Review Required (Các điểm cần duyệt), Implementation Plan (Chi tiết component/file sửa đổi), Task Checklist (TODO list), và Verification Plan (Kiểm thử). Sự sai lệch thông tin giữa 2 tài liệu này là không được chấp nhận.
  - **🚨 Thiết kế Unit Test kiểm thử Rule sống còn (BẮT BUỘC):** Nếu logic code mới hoặc chỉnh sửa tác động đến bất kỳ Rule sống còn nào trong `BDS-AGENTS.md` (như chuẩn hóa địa chỉ, xử lý số nhà, bảo mật PII), AI **bắt buộc** phải lập kế hoạch viết hoặc bổ sung các ca kiểm thử tự động (Unit Tests) vào bộ script test (`test_rules.py` hoặc bộ test tương ứng) để kiểm thử tự động.
  - **🚨 Thiết kế E2E Integration Test & Cấu hình Mock Admin (BẮT BUỘC):** Đối với bất kỳ User Story nào có can thiệp, cập nhật hoặc tái cấu trúc mã nguồn giao diện người dùng (UI/Frontend) trong `index.html`, `curator.html` hoặc các module tương ứng, AI **bắt buộc** phải lập kế hoạch và viết kịch bản kiểm thử E2E tự động sử dụng Python (thư viện Playwright hoặc Selenium) để giả lập hành vi người dùng thật trên cả 2 giao diện **Desktop (1280x800)** và **Mobile (375x812, hasTouch=True)**. Kịch bản này phải được định nghĩa rõ ràng trong phần `Verification Plan` trước khi triển khai, với các đặc tả sau:
    - **Cấu hình Mock Admin:** Định nghĩa các bước Playwright để tiêm session admin giả (`localStorage.setItem('isAdminSession', 'true')`) và các interceptors (`page.route`) giả lập dữ liệu Google Sheets để test local/staging.
    - **Vị trí chụp ảnh minh chứng (Evidence Screenshots):** Định rõ các bước kiểm chứng quan trọng (verify) cần chụp màn hình tự động và đường dẫn lưu trữ tệp ảnh (`docs/workflows/assets/[US-ID]_desktop.png` và `docs/workflows/assets/[US-ID]_mobile.png`).
  - **🧠 Tự đánh giá và Thiết kế Tiến hóa Bộ Kiểm Thử (Harness Self-Audit & Evolution - BẮT BUỘC):** AI tự động kiểm toán bộ kiểm thử hiện tại. Tự hỏi: *Độ bao phủ của assertions đã đủ nhạy để phát hiện lỗi trôi lệch (regression/value drift) chưa? Kịch bản biên dữ liệu thô (độ dài, Null, ký tự lạ, lỗi gviz mixed-type) đã có test case phủ chặn chưa?* Nếu phát hiện lỗ hổng kiểm thử, AI phải ghi nhận vào kế hoạch để chủ động viết bổ sung test cases trước hoặc song song với viết code tính năng.
  - **Files touched:** Danh sách toàn bộ các file dự kiến sẽ sửa đổi hoặc tạo mới (điền nháp dự kiến, cập nhật chính xác trong quá trình code).
- **Vòng phản hồi:** AI trình bày toàn bộ kế hoạch trên để PO xem xét. PO có thể đưa ra các điều chỉnh về giải pháp hoặc phạm vi sửa đổi ở bước này cho đến khi thống nhất phương án cuối cùng.

### Bước 5: Chốt phương án & Đánh giá lại kích thước (Size Re-assessment)
- Sau khi toàn bộ thông tin (giải pháp, logic, verification plan, files touched) đã được chốt hoàn toàn:
  1. AI đánh giá lại quy mô công việc thực tế dựa trên thiết kế kỹ thuật chi tiết.
  2. Cập nhật giá trị trường `size` (`S` / `M` / `L` / `XL`) trong frontmatter của file US đó.
  3. **Cập nhật tài liệu liên quan ngay lập tức:**
     - **Stories Index (`docs/stories/INDEX.md`):** Cập nhật lại cột **Size** của US tương ứng trong bảng `All Stories`.
     - **Kế hoạch phiên tiếp theo (`docs/NEXT_SESSION.md`):** Cập nhật lại thông tin kích thước (size) thực tế của US này trong danh sách nhiệm vụ.

### Bước 6: Triển khai phát triển & Báo cáo hoàn thành (`done`)
- AI tiến hành viết mã nguồn theo giải pháp đã chốt.
- Ghi nhận logic thô vào mục `Update Logic (Drafting while Doing)` trong quá trình code nếu chưa pass.
- **Tự kiểm tra và hoàn thành nghiêm ngặt tiêu chuẩn DoD (Definition of Done):**
  1. **Tính nhất quán:** Đảm bảo mã nguồn thực tế khớp 100% với mô tả trong `Solution` và `Implementation Plan` (sửa 1 cái thì cái còn lại phải cập nhật tương ứng).
  2. **Đồng bộ & Giữ lại Update Logic (Quy tắc Không Trùng Lắp - BẮT BUỘC):**
     - Biên tập lại và lưu giữ vĩnh viễn mục `Update Logic` trong US để tích lũy tri thức kỹ thuật thực tế (nhật ký debug, phát kiến ngẫu nhiên, kết quả chạy thử nháp).
     - Rà soát kỹ lưỡng để **TUYỆT ĐỐI KHÔNG** trùng lặp thông tin với phần `Solution` chính thức ở trên (không copy-paste prompt thô, JSON schema đã có ở trên). Xem hướng dẫn chi tiết tại [Update Logic Workflow](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/workflows/Update%20Logic.md).
  3. **Task Checklist:** Hoàn thành 100% các checkbox trong mục `Task Checklist (TODO)`.
  4. **Project Glossary:** Cập nhật các thuật ngữ mới (jargon) nếu phát sinh vào [Project Glossary](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/project_glossary.md).
  5. **Files touched:** Điền chính xác 100% các file thực tế đã chỉnh sửa hoặc tạo mới.
  6. **Clean & Format:** Format code sạch sẽ, xóa bỏ hoàn toàn các file local rời rạc (`current_task.md`, `task.md`...).
  7. **Cập nhật kiến trúc:** Cập nhật lại các file sơ đồ Mermaid, từ điển dữ liệu [Data Dictionary](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/data_dictionary.md) hoặc [Pool Sheet Schema](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/pool_sheet_schema.md) nếu có thay đổi về cấu trúc bảng hoặc luồng dữ liệu.
  8. **Đảm bảo Giá trị:** Bảo đảm giải pháp code và prompt GenAI không đi chệch khỏi các mục tiêu giá trị đã cam kết.
- Sau khi đạt 100% DoD:
  1. Chuyển `status` ở frontmatter của US sang `done`.
  2. **Cập nhật tài liệu liên quan ngay lập tức:**
     - **Stories Index (`docs/stories/INDEX.md`):** Đổi cột **Status** của US tương ứng trong bảng `All Stories` thành `done`. Cập nhật mục Stats (giảm `in-progress` đi 1, tăng `done` lên 1).
     - **Kế hoạch phiên tiếp theo (`docs/NEXT_SESSION.md`):** Cập nhật trạng thái của nhiệm vụ này thành `done` và sẵn sàng để PO kiểm thử.
  3. **Tích hợp & Bàn giao lên Production (BẮT BUỘC - CI/CD Gate):**
     - **Tự động chạy E2E & Tăng phiên bản (Anti-Cache):** Khi chạy `git commit`, hook `pre-commit` sẽ tự động kích hoạt `verify_build.py` chạy tất cả 4 bộ test Playwright E2E. Khi và chỉ khi toàn bộ test pass 100%, hệ thống tự động chạy `python scratch/bump_version.py` để tăng mã số phiên bản `?v=...` trong `index.html` lên thời gian thực tế mới nhất và tự động `git add index.html` vào commit đó.
     - **Gộp code & Push:** AI thực hiện merge nhánh tính năng vào `main` và chạy `git push origin main` để Vercel tự động build/deploy phiên bản mới nhất.
     - **Xác minh trực quan trên Live Vercel:** AI bắt buộc phải kiểm tra trực tiếp phiên bản live (ví dụ: gọi API `/api/config` hoặc check mã version `?v=...` trên trang live) để xác nhận hệ thống đã cập nhật xong trước khi báo cáo kết quả cho PO, tránh tình trạng PO kiểm thử trên bản cũ bị cache.
  4. Báo cáo rõ ràng cho PO link Production, mã version đã deploy và kết quả E2E test để PO kiểm thử trực quan trên môi trường Live.

### Bước 7: PO Kiểm thử & Nghiệm thu (`accepted`)
- PO tiến hành kiểm thử thực tế trên hệ thống.
- **Nếu kết quả đạt yêu cầu ("test pass"):** AI chạy quy trình [Test Pass Workflow](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/workflows/Test%20Pass.md) để đồng bộ hóa trạng thái cuối cùng sang tất cả các tài liệu:
  - Chuyển `status` ở frontmatter của US sang `accepted`.
  - Cập nhật số liệu thống kê và bảng danh sách trong `INDEX.md` thành `accepted`.
  - Cập nhật nhật ký lịch sử thay đổi (Change Log) trong `SOURCE_OF_TRUTH.md`.
  - Dọn dẹp nhiệm vụ khỏi `NEXT_SESSION.md` và đưa vào phần danh sách file bị tác động.
- **Nếu phát sinh lỗi hoặc PO yêu cầu thay đổi/bổ sung:**
  - **Trường hợp thay đổi yêu cầu (Change Request - ví dụ: đổi màu nút xanh thành đỏ):** AI lập tức ghi nhận yêu cầu thay đổi vào mục `## 🔄 Change Requests` ở cuối file US (nêu rõ ngày, yêu cầu cũ, yêu cầu mới, và mức độ tác động). Cập nhật lại Solution, Impl Plan & Tasks cho khớp với yêu cầu mới.
    - **PMP Change Impact Assessment:** Nếu thay đổi lớn tác động phạm vi, chi phí hạ tầng (API GenAI) hoặc kéo dài thời gian, AI bắt buộc phải cảnh báo PM để cập nhật vào bảng **Evolution Log** trong [Business Case](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/business_docs/business_case.md).
  - **Trường hợp thêm chi tiết nhỏ (Sub-versions - ví dụ: thêm nút xóa nhanh, chỉnh text nhỏ):** Ghi nhận phiên bản con dạng `US-XXX.2` (hoặc `.3`, `.4`...) bằng cách chèn trực tiếp các dòng/mục con đánh dấu `US-XXX.2` vào từng phân mục liên quan bị tác động (như User Story, Acceptance, Solution, Impl Plan, Tasks, Verification Plan) để PO có thể dễ dàng thấy rõ các bổ sung chi tiết khi review.
  - AI quay lại Bước 6 để thực hiện chỉnh sửa, cập nhật checklist và bàn giao test lại.

---

*Quy trình này được thiết lập và tự động hóa bởi Antigravity AI Assistant. Nâng cấp chuẩn LAAF v1.1 (2026-05-29).*
