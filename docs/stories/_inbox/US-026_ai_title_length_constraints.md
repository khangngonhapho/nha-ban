---
id: US-026
status: accepted
date: 2026-05-25
size: S
---

# US-026: Giới hạn độ dài Tiêu đề BDS AI & Auto-Trimmer

## User story
**As an** Admin
**I want** khống chế độ dài của Tiêu đề BDS sinh ra không được vượt quá 99 ký tự tổng cộng và 65 ký tự tính từ đầu đến hết giá trị giá ("T")
**So that** đáp ứng chính xác quy định kiểm duyệt của trang batdongsan.com.vn mà không bị cắt cụt thông tin quan trọng.

## Acceptance
- [x] Tổng số ký tự của Tiêu đề BDS không quá **99 ký tự** (kể cả khoảng trắng).
- [x] Phần nội dung kỹ thuật từ đầu tiêu đề đến hết chữ `"T"` (bao gồm cả chữ `"T"`) không quá **65 ký tự**.
- [x] Tích hợp cơ chế **Auto-Trimmer** thông minh bằng cách tách chuỗi tại dấu phân cách `" | "` để bảo vệ phần kỹ thuật và tự động cắt tỉa phần "Ưu điểm nổi bật" ở đuôi, đồng thời viết hoa chữ cái đầu tiên của USP sau dấu `" | "` (cho phép các viết tắt in hoa allowed caps: `HXH`, `CHDV`, `HĐ`, `PN`, `CV`).

## Solution

> [!note]- Input
> - Tiêu đề BĐS dài do AI sinh ra vượt quá 99 ký tự.

> [!note]- Output / Format
> - Tiêu đề BĐS được cắt tỉa thông minh có độ dài $\le 99$ ký tự và viết hoa chữ cái đầu sau `" | "` (các acronyms viết tắt in hoa chuẩn chuyên ngành).

> [!note]- Key logic
> - **Cơ chế Auto-Trimmer tự động cắt tỉa chuỗi dựa trên phân cách `" | "` (Post-Processor):**
>   ```javascript
>   function trimTieuDeBds(tieuDe) {
>     if (!tieuDe) return "";
>     tieuDe = tieuDe.trim();
>     
>     // 1. Tự động viết hoa chữ cái đầu tiên sau dấu " | "
>     var idxBar = tieuDe.indexOf(" | ");
>     if (idxBar !== -1) {
>       var techPart = tieuDe.substring(0, idxBar);
>       var uspPart = tieuDe.substring(idxBar + 3).trim();
>       if (uspPart.length > 0) {
>         uspPart = uspPart.charAt(0).toUpperCase() + uspPart.slice(1);
>       }
>       tieuDe = techPart + " | " + uspPart;
>     }
> 
>     // 2. Cắt tỉa nếu vượt quá 99 ký tự
>     if (tieuDe.length <= 99) {
>       return tieuDe;
>     }
>     
>     if (idxBar !== -1) {
>       var techPart = tieuDe.substring(0, idxBar);
>       var uspPart = tieuDe.substring(idxBar + 3).trim();
>       if (uspPart.length > 0) {
>         uspPart = uspPart.charAt(0).toUpperCase() + uspPart.slice(1);
>       }
>       
>       if (techPart.length + 3 <= 65) {
>         var allowedUspLen = 99 - (techPart.length + 3);
>         tieuDe = techPart + " | " + uspPart.substring(0, allowedUspLen).trim();
>       } else {
>         tieuDe = tieuDe.substring(0, 99).trim();
>       }
>     } else {
>       tieuDe = tieuDe.substring(0, 99).trim();
>     }
>     return tieuDe;
>   }
>   ```
> - Đồng thời cấu hình siết chặt luật độ dài trong `systemPrompt` của `pool_backend_v3.gs` để AI ưu tiên tự sinh ngắn gọn.
> - Bản Python `auto_post_server.py` được triển khai thuật toán tương đương để đảm bảo tính nhất quán của hệ thống.

## Verification Plan

> [!check]- Manual Verification
> 1. Chạy sinh tiêu đề cho một căn nhà có nhiều mô tả ưu điểm cực dài $\rightarrow$ Xác nhận tiêu đề sinh ra tự động được cắt tỉa gọn đẹp và viết hoa chữ đầu sau `" | "` với tổng ký tự $\le 99$ ký tự.

## Files touched
- `pool_backend_v3.gs` — [Apps Script Code Post-processor]
- `automation/auto_post_server.py` — [Python Bot Auto-Poster Fallback]
