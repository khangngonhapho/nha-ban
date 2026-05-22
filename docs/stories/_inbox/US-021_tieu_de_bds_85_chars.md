---
id: US-021
status: ready
date: 2026-05-22
size: M
---

# US-021: Tích hợp Tiêu đề BDS ngắn gọn dưới 85 ký tự và tối ưu AI (Cập nhật: Admin tự thêm cột thủ công, Bot sinh fallback thông minh)

## User story
**As an** *Admin / PO*  
**I want** *cột `Tiêu đề BDS` trên sheet Source được để trống khi đồng bộ mới để tôi tự tay biên soạn tối ưu SEO trực tiếp, đồng thời bot tự động sinh tiêu đề fallback dưới 85 ký tự (có HXH nếu thỏa điều kiện) nếu tôi để trống*  
**So that** *tôi có thể linh hoạt tối ưu hóa tiêu đề tin đăng trực tiếp trên sheet Source mà không làm ảnh hưởng tới sheet Pool, và bot đăng tin hoạt động ổn định*  

## Acceptance
- [ ] Sheet `Pool` giữ nguyên vẹn 100%, **KHÔNG** chèn thêm bất kỳ cột mới nào.
- [ ] Cột **`Tiêu đề BDS`** (Header: `Tiêu đề BDS`, alias `tieu_de_bds`) được Admin chèn **thủ công (bằng tay)** tại **Cột AN (Cột thứ 40, index 39)** trên sheet `Source`.
- [ ] Cột **`Đăng BDS`** trên sheet `Source` được Admin dời sang **Cột AO (Cột thứ 41, index 40)**.
- [ ] Khi Admin nhấn nút **`Duyệt Public`** để chạy hàm `onAdminReview` đồng bộ dữ liệu:
  - Hệ thống **không tự động sinh tiêu đề từ Pool** mà để trống (`""`) tại index 39 trên sheet `Source` để Admin tự điền thủ công tùy chỉnh.
  - Cột `Tiêu đề BDS` được cấu hình là cột riêng biệt thuộc nhóm `protectedIndices` (index 39) trong cơ chế Smart Merge, đảm bảo không bao giờ bị ghi đè dữ liệu cũ khi đồng bộ các lần sau.
  - Checkbox mặc định `false` được ghi vào cột `Đăng BDS` (index 40, Cột AO).
  - Hàm vẽ checkbox cập nhật vẽ chính xác tại cột 41 (AO).
- [ ] Bot Local Playwright (`auto_post_server.py`) trích xuất tiêu đề đăng tin từ cột mới `Tiêu đề BDS` (Cột AN, index 39):
  - Nếu cột này **có dữ liệu**: Bot lấy chính xác tiêu đề đó để đăng lên batdongsan.com.vn.
  - Nếu cột này **bị trống**: Bot tự động ghép tiêu đề fallback dưới 85 ký tự theo công thức: `[Tên đường] - [Diện tích]m2 - [Giá chào] tỷ`.
  - **Quy tắc HXH có điều kiện của Bot khi làm Fallback:** Chỉ bắt buộc thêm chữ `HXH ` đứng trước tên đường (Ví dụ: `HXH Đường CMT8`) nếu hẻm có độ rộng từ 4m trở lên HOẶC phân loại hẻm (`Phân loại Hẻm`, cột N) chứa chữ "xe hơi", "ô tô", "oto". Ngược lại chỉ để tên đường thông thường (Ví dụ: `Đường CMT8`).
- [ ] Toàn bộ các chỉ số index cột hiện hữu khác trong sheet `Source` và `Pool` được giữ nguyên vẹn 100%, bảo đảm tính ổn định tuyệt đối cho các tính năng khác của dự án.

## Solution

> [!note]- Configuration
> ```
> Cột mới: Tiêu đề BDS (Admin chèn thủ công)
> Vị trí Pool: KHÔNG CHÈN (giữ nguyên)
> Vị trí Source: Cột thứ 40 (Cột AN, index 39)
> Cột Đăng BDS dời sang: Cột thứ 41 (Cột AO, index 40)
> ```

## Verification Plan

> [!check]- Automated Tests
> - Chạy bot local `auto_post_server.py` quét Google Sheet xem có phát hiện đúng checkbox trigger ở cột AO (index 40) và đọc đúng cột AN (index 39) làm tiêu đề không.

> [!check]- Manual Verification
> 1. Admin chèn thủ công cột `Tiêu đề BDS` vào cột AN, dời checkbox sang cột AO trên sheet Source.
> 2. Nhập thủ công một tiêu đề tùy ý dưới 85 ký tự vào ô `Tiêu đề BDS` của một dòng bất kỳ trên Source, sau đó bấm tick ở cột AO. Quan sát Bot Playwright lấy chính xác tiêu đề này để điền vào form batdongsan.com.vn.
> 3. Để trống ô `Tiêu đề BDS` (cột AN) của một dòng:
>    - Nếu dòng đó có hẻm 5m (hoặc phân loại hẻm xe hơi): Xác nhận Bot tự động sinh tiêu đề đăng tin có chữ `HXH ` ở đầu.
>    - Nếu dòng đó có hẻm 2m (không phải hẻm xe hơi): Xác nhận Bot sinh tiêu đề đăng tin không có chữ `HXH ` ở đầu.
> 4. Đồng bộ một căn từ Pool sang Source, xác nhận cột `Tiêu đề BDS` trên Source được bảo vệ nguyên vẹn dữ liệu cũ, không bị ghi đè.

## Files touched
- `pool_backend_v3.gs` — Apps Script xử lý AI và đồng bộ
- `docs/pool_sheet_schema.md` — Cập nhật tài liệu schema
- `automation/auto_post_server.py` — Python bot local đăng tin (nằm trong thư mục `admin-nha-ban/automation/`)

## Notes
Giải pháp này giúp Admin hoàn toàn tự do tùy chỉnh SEO trực tiếp trên sheet Source, đồng thời bảo vệ hệ thống đồng bộ ổn định và hỗ trợ Bot tự sinh fallback thông minh có điều kiện nếu Admin quên không nhập tiêu đề.
// Hết tài liệu US-021
