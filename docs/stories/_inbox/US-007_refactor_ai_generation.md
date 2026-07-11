---
id: US-007
status: done
date: 2026-05-20
size: M
---

# US-007: Gộp các hàm AI thành kiến trúc DRY

## User story
**As a** *Admin*
**I want** *gộp toàn bộ logic gọi AI (sinh tiêu đề, mô tả, phường cũ) về một hàm thống nhất, xoá các hàm trùng lặp*
**So that** *prompt AI chỉ cần maintain ở một chỗ — không còn nguy cơ 2 path (batch vs UI button) chạy với prompt khác nhau*

## Acceptance
- [x] Xoá các hàm dư thừa: `batchFindOldWard`, `batchGenerateContent`, `processSelectedCellsTool`, `callAIGenerateContent`, `callAIFindOldWard`, `callOpenAI_Tool`
- [x] Tạo hàm `callOpenAI_Unified(systemPrompt, userPrompt)` dùng chung cho mọi API call, model `gpt-4o-mini`
- [x] Tạo hàm `batchGenerateContentAndWard` — xử lý hàng loạt dòng được bôi đen, gộp 3 tác vụ (Tiêu đề + Mô tả + Phường cũ) vào 1 API call duy nhất
- [x] Hàm mới đọc cột theo tên (`headers.indexOf`), không hardcode số cột
- [x] Menu `onOpen` trỏ về `batchGenerateContentAndWard` thay cho hàm cũ

## Solution

> [!note]- Key logic
> Cấu trúc sau refactor:
> ```
> callOpenAI_Unified(systemPrompt, userPrompt) → JSON object
>   └── batchGenerateContentAndWard()  [menu item]
>         ├── build systemPrompt  (persona + 3 rules)
>         ├── build userPrompt    (data từng dòng)
>         └── ghi tieuDe, moTa, phuongCu nếu ô đang trống
> ```
> - 3 tác vụ trong 1 API call → response JSON: `{ tieuDe, moTa, phuongCu }`
> - Chỉ skip dòng nếu **cả 3 trường** đã có data

> [!note]- Output / Format
> JSON response bắt buộc:
> ```json
> {
>   "tieuDe": "...",
>   "moTa": "...",
>   "phuongCu": "..."
> }
> ```

## Files touched
- `pool_backend_v3.gs` — xoá 6 hàm cũ, thêm `callOpenAI_Unified` + `batchGenerateContentAndWard`, cập nhật `onOpen`
