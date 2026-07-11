---
id: US-009
status: superseded
date: 2026-05-20
size: S
superseded_by: US-011
---

# US-009: Prompt yêu cầu AI liệt kê tiện ích cụ thể

## User story
**As a** *Admin*
**I want** *prompt AI chỉ định rõ phần "Kết nối & Tiện ích" phải liệt kê tên cụ thể (chợ nào, trường nào, bệnh viện nào, siêu thị nào) thay vì câu chung chung*
**So that** *phần mô tả tiện ích đáng tin hơn, có ích hơn cho người đọc và tăng tính thuyết phục của bài đăng*

## Acceptance
- [x] `systemPrompt` hướng dẫn rõ: nếu đề cập tiện ích (chợ, siêu thị, trường học, bệnh viện) thì **bắt buộc ghi tên cụ thể** dựa trên kiến thức địa lý TP.HCM của AI, không viết chung chung
- [x] Trước khi trả về kết quả, AI **bắt buộc tự kiểm tra**: mỗi tên tiện ích đã liệt kê có thực sự tồn tại và nằm gần địa chỉ đó không — nếu không chắc thì **xoá khỏi danh sách**, không giữ lại
- [x] Nếu AI không xác nhận được bất kỳ tên cụ thể nào → viết: "Khu vực có đầy đủ tiện ích sinh hoạt." (không liệt kê)
- [x] Các bài đăng test xuất ra tên thực tế, chính xác (ví dụ: "chợ Tân Định", "Bệnh viện Chợ Rẫy", "THPT Lê Quý Đôn"...)

## Solution

> [!note]- Output / Format
> Ví dụ đoạn Kết nối & Tiện ích **trước** (sai):
> ```
> + Kết nối & Tiện ích: Gần các tiện ích như chợ, siêu thị, trường học, bệnh viện, đáp ứng đầy đủ nhu cầu sinh hoạt hàng ngày.
> ```
> Ví dụ **sau** (đúng):
> ```
> + Kết nối & Tiện ích: Gần chợ Tân Định, siêu thị Co.opmart Lý Thường Kiệt, trường THPT Nguyễn Thị Minh Khai, Bệnh viện Từ Dũ — tiện ích đầy đủ, sinh hoạt cực thuận.
> ```
> Fallback nếu không xác nhận được tên:
> ```
> + Kết nối & Tiện ích: Khu vực có đầy đủ tiện ích sinh hoạt.
> ```

> [!note]- Key logic
> Instruction thêm vào phần rule mô tả trong `systemPrompt`:
> ```
> + Kết nối & Tiện ích: Liệt kê TÊN CỤ THỂ các tiện ích xung quanh (chợ, siêu thị, trường học, bệnh viện) dựa trên kiến thức địa lý thực tế của TP.HCM.
> TRƯỚC KHI ĐƯA VÀO KẾT QUẢ: Tự kiểm tra lại từng tên — tên này có thực sự tồn tại và nằm gần địa chỉ đó không? Nếu không chắc → xoá tên đó khỏi danh sách.
> Nếu không xác nhận được bất kỳ tên cụ thể nào → chỉ viết: "Khu vực có đầy đủ tiện ích sinh hoạt." Tuyệt đối KHÔNG viết chung chung kiểu "gần các tiện ích như...".
> ```

## Files touched
- `pool_backend_v3.gs` — biến `systemPrompt` trong `batchGenerateContentAndWard`

## Notes
- Self-verification là Chain-of-Thought ẩn trong instruction — AI sẽ "suy nghĩ trước khi viết" thay vì hallucinate
- Rủi ro còn lại: AI vẫn có thể tự tin sai với địa chỉ xa trung tâm → PO nên spot-check output lần đầu
