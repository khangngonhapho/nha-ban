---
id: US-025
status: accepted
date: 2026-05-25
size: S
---

# US-025: Cấu trúc Tiêu đề BDS AI mới cho batdongsan.com.vn

## User story
**As an** Admin
**I want** AI viết Tiêu đề BDS theo đúng thứ tự xuất hiện nội dung mới ngay từ gốc (Pool Sheet) kèm theo luật tiền tố và viết hoa/viết tắt chuẩn hóa nghiêm ngặt
**So that** tối ưu hóa thông số kỹ thuật chuẩn SEO và cấu trúc tin đăng đồng đều trên trang batdongsan.com.vn cũng như website.

## Acceptance
- [x] **Tiền tố (Prefix) tùy chọn theo luật**:
    - **"Mặt tiền "** (🚨 Ưu tiên 1): Nếu số nhà (ở địa chỉ hoặc nội dung chính) **không có dấu chấm (`.`)**, đây là nhà Mặt tiền. Thêm `"Mặt tiền "` (có dấu cách) ngay trước tên đường.
    - **"HXH "** (🚨 Ưu tiên 2): Nếu số nhà có dấu chấm (`.`) (nhà trong hẻm) **VÀ** độ rộng đường trước nhà (`Đường trước nhà (m)`) **từ 4m trở lên** (width $\ge 4.0$m), thêm `"HXH "` (có dấu cách) trước tên đường.
    - **Không có Tiền tố**: Nếu số nhà có dấu chấm (`.`) **VÀ** đường trước nhà nhỏ hơn 4m (hoặc không có thông tin rõ ràng $\ge 4$m), **TUYỆT ĐỐI không thêm tiền tố nào** (tiêu đề bắt đầu trực tiếp bằng Tên đường).
- [x] Cấu trúc tiêu đề bắt buộc: `[Prefix nếu có][Tên đường] - [Diện tích]m2 - [Kích thước] - [Số tầng] tầng - [Giá]T | [Ưu điểm nổi bật]`.
- [x] **Quy tắc Viết hoa & Viết tắt trong USP sau " | "** (🚨 CỰC KỲ NGHIÊM NGẶT):
    - Chỉ các từ viết tắt chuyên ngành sau đây được phép viết in hoa toàn bộ: **`HXH`**, **`CHDV`**, **`HĐ`**, **`PN`**, **`CV`**. Các từ khác quy về chữ thường (chỉ viết hoa chữ cái đầu tiên của USP ngay sau dấu `" | "`).
    - Nếu đưa số phòng ngủ vào USP: Bắt buộc viết tắt dạng **`[Số]PN`** (Ví dụ: `3PN`, `4PN`).
    - Nếu đưa công viên vào USP: Bắt buộc viết tắt từ công viên thành **`CV`** (Ví dụ: `CV Lê Văn Tám`, `gần CV`).
- [x] **Danh sách các từ cấm tuyệt đối trong USP**:
    - Không đưa `"hợp đồng điện tử"` / `"HĐĐT"` vào đặc điểm nổi bật. (Nếu có dòng tiền cho thuê thì ghi dạng: `"HĐ thuê cao"` hoặc `"dòng tiền thuê tốt"`).
    - Không đưa `"hẻm nhỏ"` / `"hẻm ba gác"` / `"hẻm"` vào đặc điểm nổi bật.
    - Không đề cập lại từ hẻm/hẻm xe hơi/HXH trong USP nếu ở đầu tiêu đề đã có tiền tố `"HXH "`.
    - Không đưa `"lãi vốn"` hoặc `"chính chủ"` vào USP.
- [x] **Các nội dung được phép đưa vào USP**:
    - Số phòng ngủ (`3PN`), Chợ (ví dụ: `gần chợ Tân Định`), Công viên (`gần CV Lê Văn Tám`), các địa điểm nổi tiếng lân cận đề cập trong mô tả gốc (giữ nguyên case gốc của địa danh).

## Solution

> [!note]- Input
> - Bảng tính dữ liệu Google Sheet chứa cột "Ngõ/Số nhà", "Đường trước nhà (m)", và "Nội dung chính" thô.
> - Lệnh click chạy menu AI Tools trong Apps Script Pool.

> [!note]- Output / Format
> - Tiêu đề BĐS sinh ra theo đúng định dạng Mặt tiền: `Mặt tiền Nguyễn Trọng Tuyển - 80m2 - 4x20 - 5 tầng - 22T | CHDV dòng tiền cao`.
> - Tiêu đề BĐS sinh ra theo đúng định dạng Hẻm xe hơi: `HXH Trần Quang Diệu - 38m2 - 9x5 - 3 tầng - 8.75T | Lô góc 3PN gần CV Lê Văn Tám`.
> - Tiêu đề BĐS sinh ra theo đúng định dạng hẻm nhỏ: `Lê Văn Sỹ - 46m2 - 4.6x10 - 4 tầng - 12.8T | Nhà mới đẹp gần CV Lê Văn Tám`.

> [!note]- Key logic
> - Cập nhật Apps Script `batchGenerateContentAndWard()` tự động tính toán tiền tố (`tienTo`) từ JavaScript (dựa trên sự xuất hiện của dấu chấm trong số nhà và độ rộng đường trước nhà $\ge 4.0$m), truyền thẳng vào `userPrompt` để hướng dẫn AI chính xác tuyệt đối.
> - Cập nhật `systemPrompt` trong `pool_backend_v3.gs` để ép AI tuân thủ cấu trúc chuẩn mới, viết hoa chữ cái đầu sau `" | "`, cho phép viết tắt in hoa các từ `HXH, CHDV, HĐ, PN, CV`, bắt buộc format `[Số]PN` và `CV`, cấm các từ khóa lãi vốn/chính chủ/hợp đồng điện tử/hẻm nhỏ.
> - Đồng bộ hóa Fallback Generator và bộ Auto-Trimmer trong Python `auto_post_server.py` theo đúng luật mới.

## Verification Plan

> [!check]- Manual Verification
> 1. Chọn 1 căn nhà thô $\rightarrow$ Click chạy menu AI Tools sinh Tiêu đề BDS.
> 2. Kiểm tra xem Tiêu đề sinh ra có khớp chính xác cấu trúc và tiền tố theo luật, chữ cái đầu tiên sau `" | "` viết hoa, phòng ngủ và công viên viết tắt chính xác dạng in hoa allowed caps.

## Files touched
- `pool_backend_v3.gs` — [Apps Script AI Prompts & Root Generator]
- `automation/auto_post_server.py` — [Python Bot Auto-Poster Fallback]
