---
id: US-002
status: done
date: 2026-05-20
size: S
---

# US-002: Thuật toán Mã Khang Ngô cắt số phụ căn nhà

## User story
**As a** Admin (Quản trị viên)
**I want** thuật toán sinh Mã Khang Ngô tự động cắt bỏ phần số phụ khi căn nhà có 2 số (chứa dấu +)
**So that** mã ID sinh ra được chuẩn hóa, nhất quán và chỉ dựa trên phần số nhà chính (trước dấu cộng).

## Acceptance
- [x] Khi thuật toán `genIdKhangNgo` tiếp nhận số nhà có chứa dấu `+`, hệ thống tự động nhận diện và chỉ cắt lấy chuỗi số phía trước dấu cộng.
- [x] Ví dụ: Số nhà `1168.42+44` được xử lý thành `1168.42`, kết hợp với đường Trường Sa xuất ra đúng mã Khang Ngô là `MWMSTIAHIST`.

## Solution

> [!note]- Input
> - Chuỗi số nhà đầu vào có chứa ký tự `+` (Ví dụ: `"1168.42+44"`).

> [!note]- Output / Format
> - Mã Khang Ngô (ID) 13 ký tự được viết hoa toàn bộ (Ví dụ: `MWMSTIAHIST`).

> [!note]- Key logic
> - Trong Apps Script `pool_backend_v3.gs`, hàm `genIdKhangNgo()` được chèn logic tách chuỗi bằng dấu `+`:
>   ```javascript
>   let soChinh = soNha;
>   if (soNha.includes('+')) {
>     soChinh = soNha.split('+')[0].trim();
>   }
>   ```
> - Quy tắc này đảm bảo hai căn liền kề chung sổ hoặc chung thửa số phụ vẫn được sinh mã nhất quán theo số nhà chính.

## Verification Plan

> [!check]- Manual Verification
> 1. Nhập một căn nhà có số nhà là `1168.42+44` đường Trường Sa $\rightarrow$ Chạy lệnh sinh ID.
> 2. Xác nhận ID được sinh ra là `MWMSTIAHIST` (khớp hoàn toàn với ID sinh ra từ số nhà `1168.42` Trường Sa).

## Files touched
- `pool_backend_v3.gs` — [Apps Script ID Generation Algorithm]
- `BDS-AGENTS.md` — [AI Context & Generation Rules]

## Notes
- Các trường hợp nhà 2 số dùng ký tự khác (như dấu `/` hoặc `-` kéo dài) tạm thời chưa nằm trong phạm vi của US này.
