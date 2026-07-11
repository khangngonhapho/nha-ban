---
id: US-XXX
status: done
date: YYYY-MM-DD
size: S
---

> [!info]- 📋 Hướng dẫn điền template
> **id**: Lấy từ INDEX.md, +1 so với US lớn nhất
> **status**: `draft` | `backlog` | `in-progress` | `done` | `superseded`
> **size**:
>   `S` — 1-2 files, logic có sẵn, break isolated
>   `M` — 2-5 files, feature mới, pattern có sẵn, break 1 flow  
>   `L` — nhiều component tương tác, break cross-feature
>   `XL` — thay đổi kiến trúc / auth / security / data layer, break toàn hệ thống
> **DoR (Definition of Ready):** Backlog phải có **ít nhất 2 tiêu chí Acceptance rõ ràng** (xác định rõ luồng xử lý đầu vào/đầu ra - In/Out, hoặc đặc tả giao diện theo chuẩn) trước khi đưa vào Planning.
> **DoD (Definition of Done):** Code thực tế phải nhất quán với Solution/Impl Plan; hoàn thành 100% Task Checklist; sơ đồ hóa Mermaid; cập nhật Project Glossary nếu có thuật ngữ mới; điền Files touched; dọn dẹp sạch file local và cập nhật sơ đồ kiến trúc dữ liệu trước khi chuyển sang Done.
> **Quy tắc Đồng bộ Kế hoạch Triển khai (Strict Plan Synchronization - BẮT BUỘC):** Mỗi khi file đề xuất `implementation_plan.md` (artifact của Gemini) được tạo hoặc cập nhật để PO duyệt, AI **bắt buộc** phải đồng bộ và cập nhật tương ứng vào file US gốc (`US-XXX.md`). Các mục bắt buộc đồng bộ bao gồm:
>   - **Chiến lược & Cơ chế** (Strategy & Mechanisms - ví dụ: bảo toàn ảnh, đối chiếu thay đổi)
>   - **Giải pháp kỹ thuật & Rã/Gom dữ liệu** (Technical Solution & Schema rules)
>   - **User Review Required** (Các điểm PO cần duyệt)
>   - **Implementation Plan** (Chi tiết các file/component sửa đổi)
>   - **Task Checklist** (TODO checklist)
>   - **Verification Plan** (Kịch bản kiểm thử)
>   Hai tài liệu này phải luôn nhất quán và khớp thông tin 100% trước khi triển khai và kiểm thử.
> **Change Requests (Thay đổi yêu cầu):** Khi PO đổi yêu cầu nghiệp vụ giữa chừng (ví dụ: đổi xanh thành đỏ), ghi nhận tại mục `## 🔄 Change Requests`, đồng thời cập nhật Solution, Impl Plan & Tasks.
> **Sub-versions (Chi tiết bổ sung - ví dụ: US-XXX.2):** Khi test phát sinh thêm chi tiết bổ sung nhỏ (ví dụ: thêm nút, chỉnh label nhỏ), ghi nhận phiên bản con dạng `US-XXX.2` (hoặc `.3`, `.4`...) bằng cách tạo thêm mục con/dòng phụ đánh dấu `US-XXX.2` trong từng phân mục liên quan (User story, Acceptance, Solution, Impl Plan, Tasks, Verification Plan) để hiển thị trực quan các bổ sung khi review.
> ⚠️ Xoá callout này trong file US thật


# US-XXX: [Tên ngắn 5-10 từ]

## User story
**As a** [Sale / Admin]
**I want** [hành động]
**So that** [lợi ích]

## Acceptance
- [ ] [Criteria 1]
- [ ] [Criteria 2]

## Solution

> [!note]- Configuration
> [Biến môi trường, settings, toggle, API key dùng — những thứ không thấy trong code logic]
> ```
> VARIABLE_NAME=value
> ```

> [!note]- Input
> [Schema đầu vào — param, payload, form field, trigger]
> ```json
> {
>   "field": "type — mô tả"
> }
> ```

> [!note]- Output / Format
> [Định dạng đầu ra — response, UI render, file, prompt text]
> ```
> [paste prompt, JSON schema, hoặc mô tả format]
> ```

> [!note]- Key logic
> [Đoạn logic quan trọng, rule xử lý, edge case — những thứ không đọc code không biết]

[Diagram nếu có nhiều component — dùng Mermaid]
```mermaid
graph TD
    A --> B
```

## 📋 Implementation Plan
> [!plan]- Kế hoạch Triển khai (Bắt buộc cho Size M/L/XL)
> - **Cách tiếp cận:** [Mô tả hướng giải quyết kiến trúc hoặc phương pháp thực hiện]
> - **Các bước triển khai dự kiến:**
>   1. [Bước 1]
>   2. [Bước 2]

## 📝 Task Checklist (TODO)
> [!todo]- Danh sách việc cần làm để theo dõi tiến độ
> - [ ] **Thiết kế & Khảo sát:** [ ] Khảo sát code cũ | [ ] Chốt giải pháp
> - [ ] **Triển khai Code:** [ ] Code logic chính | [ ] Xử lý edge cases | [ ] Cấu hình / Settings
> - [ ] **Kiểm thử sơ bộ:** [ ] Chạy các ca test thủ công | [ ] Đóng gói / Clean tài liệu

## 🛠️ Update Logic (Drafting while Doing)
> [!IMPORTANT]
> **Quy tắc Không Trùng Lắp (Non-Duplication Rule - BẮT BUỘC GIỮ LẠI VĨNH VIỄN):**
> - **Mục đích:** Lưu trữ lịch sử hành trình kỹ thuật thực tế (**HOW & WHY**). Tuyệt đối **KHÔNG** xóa bỏ mục này sau khi test pass.
> - **Nguyên tắc không trùng lắp:** Tuyệt đối không copy-paste các cấu trúc thô, JSON schema, prompt hoặc mã nguồn hoàn chỉnh đã có trong phần `Solution` hoặc `Verification Plan` chính thức ở trên.
> - **Nội dung cần tập trung ghi nhận:**
>   1.  *Nhật ký Debug & Sự cố giải quyết (Issue Resolution Log):* Liệt kê các lỗi kỹ thuật phát sinh thực tế (ví dụ: lỗi phân quyền, lỗi ép kiểu, lỗi kết nối) và cách xử lý cụ thể bằng dòng code/helper.
>   2.  *Những phát kiến ngoài kế hoạch (Unexpected Discoveries):* Điểm tối ưu, giải pháp thông minh phát hiện ngẫu nhiên khi viết code (ví dụ: debounce tối ưu lượt gọi API, cải tiến cơ chế caching).
>   3.  *Lịch sử chạy thử nghiệm nháp (Draft Test Logs):* Nhật ký và output chạy thử nháp của các script test độc lập trước khi có kiểm thử chính thức.

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:** *[Ghi nhận lỗi cụ thể và giải pháp điều chỉnh code]*
- **Phát kiến ngoài kế hoạch / Điểm tối ưu phát hiện khi code:** *[Ghi nhận nếu có]*

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- **Script kiểm thử thô / nháp đã chạy:** *[Ví dụ: python test_xxx.py]*
- **Output kết quả nháp & Điểm nghẽn đã vượt qua:** *[Dán log lỗi và phân tích nếu có]*

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)
> [!TIP]
> **Mục đích:** Ghi nhận lại các sự cố thực tế xảy ra khi phát triển để họp rút kinh nghiệm (Retro), đồng thời đúc kết các bài học tốt (Good Practices) nhằm ngăn ngừa tuyệt đối các lỗi tương tự ở các US tiếp theo.
> - **Nhật ký Sự cố & Retro (Incident & Retro Log):** *[Ghi nhận lỗi nghiêm trọng xảy ra, nguyên nhân gốc rễ và giải pháp khắc phục thực tế]*
> - **Thực tiễn tốt đúc kết (Good Practices):** *[Ghi nhận các mẹo code, cấu hình an toàn, hoặc kinh nghiệm test đúc kết được giúp tăng hiệu suất / tránh lỗi]*

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** *[Mô tả lỗi hoặc blocker]*
- **Nguyên nhân gốc rễ (Root Cause):** *[Phân tích lý do]*
- **Giải pháp phòng ngừa:** *[Cách xử lý để không lặp lại]*

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm code & Cấu hình:** *[Mẹo viết code hoặc setup tối ưu]*
- **Kinh nghiệm kiểm thử:** *[Mẹo test nhanh hoặc phát hiện lỗi sớm]*

## Verification Plan

> [!check]- Automated Tests
> [Lệnh test hoặc kiểm thử tự động nếu áp dụng]

> [!check]- Manual Verification
> [Các bước test thủ công cụ thể từng bước]

## Files touched
- `path/file.ext` — [role ngắn]

## 🔄 Change Requests (Yêu cầu Thay đổi)
> [!quote]- Nhật ký các yêu cầu thay đổi nghiệp vụ của PO trong quá trình thực hiện
> *(Ghi nhận khi PO thay đổi yêu cầu cũ sang yêu cầu mới - ví dụ: đổi màu từ xanh sang đỏ)*
> - **CR-01 (YYYY-MM-DD):**
>   - **Yêu cầu cũ:** [Mô tả yêu cầu gốc]
>   - **Yêu cầu mới:** [Mô tả yêu cầu thay đổi mới]
>   - **Tác động:** [Cập nhật Solution, Implementation Plan, v.v.]

## Notes
[Quirk, blocker, TODO — xoá section này nếu không có]