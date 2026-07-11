---
id: US-004
status: superseded
date: 2026-05-20
size: unknown
superseded_by: US-005
backfilled: true
---

# US-004: [Legacy] Prompt cũ sinh Tiêu đề & Mô tả AI

## Previous behavior
Hệ thống gọi OpenAI API qua 2 hàm riêng biệt (`batchGenerateContent` dùng `gpt-3.5-turbo`, `processSelectedCellsTool` dùng `gpt-4o-mini`). Cả hai hàm chứa prompt riêng không đồng bộ nhau. Prompt quy định tiêu đề dưới 88 ký tự, cấu trúc cứng `[Tên đường - Quận - Diện tích - Ưu điểm nổi bật - Giá]`, tự động gắn tiền tố `🚘 HXH - ` nếu hẻm ô tô hoặc `Mặt tiền - ` nếu mặt tiền. Mô tả 4 đoạn không có quy định ký tự đầu dòng nên AI tự ý dùng emoji (📍, ✨, 🏗️...) hoặc bullet point tuỳ thích.

## Files (trước khi thay)
- `pool_backend_v3.gs` — hàm `batchGenerateContent`, `processSelectedCellsTool`, `callAIGenerateContent`, `callOpenAI_Tool`

## Note
Stub tạo khi US-005 replace behavior prompt. Acceptance gốc không có.
