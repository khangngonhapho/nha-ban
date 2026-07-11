---
id: US-006
status: done
date: 2026-05-20
size: S
---

# US-006: Bỏ tiền tố HXH tự động trong tiêu đề

## User story
**As a** *Admin*
**I want** *loại bỏ việc tự động chèn "🚘 HXH - " vào đầu tiêu đề cho nhà hẻm ô tô*
**So that** *tiêu đề không bị gắn nhãn sai lệch — đặc điểm hẻm xe hơi sẽ do AI tự diễn đạt trong phần Ưu điểm nổi bật thay vì bị fix cứng*

## Acceptance
- [x] Code không còn tự động gán `tienTo = "🚘 HXH - "` khi `loaiHem === "hẻm ô tô"`
- [x] Điều kiện gán `tienTo = "Mặt tiền - "` khi `loaiHem.includes("mặt tiền")` vẫn được giữ nguyên
- [x] Hàm `callOpenAI_Tool` (`systemPrompt`) cũng được xoá rule tương tự để 2 path thống nhất

## Solution

> [!note]- Key logic
> Logic `tienTo` sau khi sửa:
> ```js
> var tienTo = "";
> if (loaiHem.includes("mặt tiền")) {
>   tienTo = "Mặt tiền - ";
> }
> // Không còn nhánh "hẻm ô tô" → tienTo giữ rỗng
> ```

## Files touched
- `pool_backend_v3.gs` — biến `tienTo` trong `batchGenerateContentAndWard`, biến `systemPrompt` trong `callOpenAI_Tool`
