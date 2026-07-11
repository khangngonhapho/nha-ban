---
id: US-005
status: done
date: 2026-05-20
size: S
replaces: US-004
---

# US-005: Prompt AI đóng vai môi giới, bỏ cấu trúc cứng

## User story
**As a** *Admin*
**I want** *thay prompt AI từ "chuyên gia content BĐS" sang persona môi giới 15 năm kinh nghiệm tại trung tâm TP.HCM, và bỏ cấu trúc tiêu đề cứng nhắc*
**So that** *tiêu đề bài đăng thu hút hơn, tập trung nêu bật USP thay vì liệt kê thông số đơn điệu*

## Acceptance
- [x] Prompt đóng vai "Chuyên gia môi giới nhà phố 15 năm kinh nghiệm tại trung tâm TP.HCM"
- [x] Cấu trúc tiêu đề áp dụng lại: `[Tên đường - Phường - Quận - Diện tích - Ưu điểm nổi bật - Giá]`, không giới hạn ký tự
- [x] Phần "Ưu điểm nổi bật" dùng ngôn từ mạnh, nêu USP thực sự (hẻm ô tô ngủ trong nhà, ngang bề thế...) thay vì hành văn bay bổng
- [x] Tuyệt đối không đưa số nhà thật vào tiêu đề

## Solution

> [!note]- Output / Format
> Cấu trúc tiêu đề:
> ```
> [Tên đường] - [Phường] - [Quận] - [Diện tích]m2 - [USP ngắn gọn, mạnh] - [Giá]
> ```
> Ví dụ: `Lê Văn Sỹ - P.Nhiêu Lộc - Q.3 - 48m2 - Lô góc 2 mặt thoáng, hẻm thông - 6.8 tỷ`

> [!note]- Key logic
> - Tiền tố `Mặt tiền - ` vẫn được gắn cứng nếu `loaiHem.includes("mặt tiền")` → bắt buộc bắt đầu tiêu đề bằng cụm này
> - Prompt được áp dụng cho cả 2 path: batch (hàm `batchGenerateContent`) và UI button (hàm `callOpenAI_Tool`)

## Files touched
- `pool_backend_v3.gs` — biến `prompt` trong `batchGenerateContent`, `systemPrompt` trong `callOpenAI_Tool`
