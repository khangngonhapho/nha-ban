# Quy trình Tạo Backlog Mới (New Backlog Workflow)

Tài liệu này định nghĩa quy trình chuẩn chỉnh để AI thực hiện khi nhận được yêu cầu thêm một tính năng, yêu cầu hoặc nhu cầu nghiệp vụ mới vào hàng đợi phát triển (**Backlog**).

**Mục tiêu cốt lõi:** Lưu trữ nhanh chóng ý tưởng và nhu cầu nghiệp vụ dưới dạng một User Story (US) ban đầu. Khi câu chuyện này được chọn để triển khai thực tế, AI hoặc Lập trình viên sẽ mở chính file này ra và bổ sung các thông tin kỹ thuật/kiểm thử còn thiếu vào đúng vị trí.

---

## 🚨 Các bước thực hiện tự động (Automated Steps)

Khi nhận được yêu cầu lưu trữ một nhu cầu mới vào Backlog, AI **bắt buộc phải thực hiện cập nhật toàn bộ các tài liệu liên quan ngay lập tức**:

### 1. Duyệt Stories Index để lấy ID mới (`docs/stories/INDEX.md`)
- Đọc file [INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md) để:
  - Xác định ID lớn nhất hiện tại. ID của backlog mới sẽ là `US-[ID_lớn_nhất + 1]`.

### 2. Khởi tạo file User Story dạng Backlog
- **Kiểm tra tiêu chuẩn DoR (Definition of Ready):** Yêu cầu Backlog bắt buộc phải có **ít nhất 2 tiêu chí Acceptance rõ ràng** (xác định rõ luồng xử lý đầu vào/đầu ra - In/Out, hoặc đặc tả giao diện theo chuẩn). Nếu PO cung cấp chưa đủ 2 tiêu chí, AI phải dựa trên mô tả để chủ động phác thảo đề xuất thêm cho đủ tiêu chuẩn DoR trước khi khởi tạo file.
- **Kiểm tra tính phù hợp nghiệp vụ sơ bộ (Strategic Value Check):** Đối chiếu nhanh xem User Story này đóng góp gì vào Lợi ích mục tiêu được cam kết trong [Value Management Plan](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/business_docs/value_management_plan.md) hoặc [Business Case](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/business_docs/business_case.md) của anh Khang Ngô.
- **Khảo sát kiến trúc sơ bộ:** Đối chiếu tính năng mới với bản đồ kiến trúc hệ thống hiện tại trong [system_architecture_deployment.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/system_architecture_deployment.md) để đánh giá sơ bộ mức độ tác động và tính khả thi trong mô hình Khối Lắp Ráp Lego.
- Tạo file mới tại thư mục `docs/stories/_inbox/` với định dạng tên chuẩn: `US-XXX_slug_viet_tat.md`.
- Sao chép cấu trúc từ template bên dưới.
- **Điền thông tin giai đoạn Backlog (Chỉ điền đến Acceptance):**
  - Thiết lập frontmatter: `id`, trạng thái `status: backlog`, ngày tạo `date`.
  - **Ước lượng kích thước sơ bộ (Preliminary Size Assessment):** Đưa ra đánh giá sơ bộ về quy mô công việc trong trường `size` (`S` / `M` / `L` / `XL`) dựa trên mức độ phức tạp nghiệp vụ hiện tại.
  - Điền phần **User story** (`As a... I want... So that...`) để làm rõ nhu cầu nghiệp vụ và ghi chú ngắn gọn sự đóng góp giá trị (phù hợp với KPIs/lợi ích nào của Value Plan).
  - Điền phần **Acceptance** để mô tả chi tiết các tiêu chí nghiệm thu cần đạt.
  - **⚠️ Cực kỳ quan trọng:** Giữ nguyên các tiêu đề phân mục kỹ thuật ở bên dưới (`Solution`, `Verification Plan`, `Files touched`, v.v.) nhưng để trống hoặc ghi chú là sẽ bổ sung khi thực hiện. Điều này giúp file có sẵn khung cấu trúc chuẩn để điền tiếp sau này.

### 3. Cập nhật ngay lập tức các tài liệu liên quan
AI bắt buộc phải đồng bộ hóa thông tin sang các tài liệu liên quan sau đây:
- **Stories Index (`docs/stories/INDEX.md`):**
  - Tăng tổng số câu chuyện (Total) lên 1.
  - Tăng số lượng status `backlog` lên 1 (nếu có bảng Stats tương ứng).
  - Chèn dòng thông tin của US mới vào đầu bảng **All Stories** (sắp xếp giảm dần theo ID): `| US-XXX | [title] | backlog | [size] | [date] | [files] |`
  - Phân loại US mới vào nhóm từ khóa tương ứng dưới mục **By Keyword** kèm chú thích `(backlog)` (ví dụ: `-[[US-043_tich_hop_thanh_toan|US-043]]: Tích hợp thanh toán trực tuyến (backlog)`).
- **Project Dashboard & Source of Truth (`SOURCE_OF_TRUTH.md`):**
  - Cập nhật mục **Section 9: 🚀 TÍNH NĂNG CẦN THÊM (Backlog)**, thêm entry US mới này vào danh sách để PO dễ dàng theo dõi mức độ ưu tiên tổng thể.

---

## 🔄 Quy trình bổ sung thông tin khi triển khai (When Implementing)

Khi bắt đầu thực hiện User Story đang ở trạng thái `backlog`:
1. Mở file `US-XXX_slug_viet_tat.md` tương ứng đã tạo ở bước trên.
2. Chuyển trạng thái frontmatter từ `status: backlog` sang `status: in-progress` (hoặc `draft`).
3. Thực hiện khảo sát, thiết kế và điền đầy đủ các thông tin kỹ thuật vào các phần còn lại:
   - **Solution:** Điền chi tiết thiết lập cấu hình, định dạng Input/Output, sơ đồ Mermaid và Key logic xử lý (tuân thủ nguyên tắc Modular Lego và quy tắc di động trong [system_architecture_deployment.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/system_architecture_deployment.md)).
   - **Đánh giá lại kích thước (Size Re-assessment):** **⚠️ Bắt buộc** đánh giá lại giá trị trường `size` ở frontmatter và cập nhật lại trong [INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md) sau khi đã có giải pháp kỹ thuật rõ ràng để đảm bảo phản ánh chính xác độ phức tạp thực tế.
   - **Verification Plan:** Lập kế hoạch kiểm thử tự động và thủ công.
   - **Files touched:** Liệt kê các file sẽ bị tác động.
4. Ghi nhận các logic thô vào mục `Update Logic (Drafting while Doing)` trong quá trình code.

---

## 📋 Cấu trúc File Backlog Ban Đầu (Initial Template)

Sao chép toàn bộ cấu trúc dưới đây để khởi tạo file backlog mới:

```markdown
---
id: US-XXX
status: backlog
date: YYYY-MM-DD
size: S # Đánh giá sơ bộ ban đầu (S/M/L/XL), sẽ được đánh giá lại khi triển khai
---

# US-XXX: [Tên ngắn gọn của Backlog 5-10 từ]

## User story
**As a** [Vai trò - ví dụ: Curator / Admin / Khách hàng]
**I want** [Hành động / Tính năng muốn thực hiện]
**So that** [Lợi ích mang lại / Mục tiêu đạt được - Ví dụ đóng góp vào KPI 1 (Tốc độ biên tập) của Value Plan]

## Acceptance
- [ ] [Tiêu chí nghiệm thu 1]
- [ ] [Tiêu chí nghiệm thu 2]

## Solution
*(Sẽ bổ sung chi tiết thiết kế, cấu hình, Input/Output và Key logic khi đưa vào triển khai. Đồng thời thực hiện đánh giá lại size tại đây)*

## 📋 Implementation Plan
*(Sẽ bổ sung chi tiết các bước tiếp cận và phương án triển khai kỹ thuật tại đây khi bắt đầu thiết kế - bắt buộc cho Size M/L/XL)*

## 📝 Task Checklist (TODO)
*(Sẽ thiết lập danh sách việc cần làm cụ thể để theo dõi tiến độ code và test tại đây)*

## 🛠️ Update Logic (Drafting while Doing)
*(Sẽ sử dụng để ghi nhận logic thô trong quá trình triển khai thực tế)*

## Verification Plan
*(Sẽ bổ sung các bước kiểm thử tự động/thủ công khi đưa vào triển khai)*

## Files touched
*(Sẽ bổ sung danh sách file tác động khi đưa vào triển khai)*

## 🔄 Change Requests (Yêu cầu Thay đổi)
*(Sẽ sử dụng để ghi nhận nhật ký thay đổi yêu cầu của PO khi test hoặc triển khai)*
```

---

*Quy trình này được thiết lập và tự động hóa bởi Antigravity AI Assistant. Nâng cấp chuẩn LAAF v1.1 (2026-05-29).*
