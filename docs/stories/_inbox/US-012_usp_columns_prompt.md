---
id: US-012
status: done
date: 2026-05-20
size: S
---

# US-012: Đưa thêm cột Phân loại & tối ưu label userPrompt để AI khai thác USP

## User story
**As a** *Admin*
**I want** *userPrompt gửi thêm cột "Phân loại" (Lô góc, Hiếm, Nội thất đẹp...) và đặt lại label rõ ràng hơn cho "Mô tả chi tiết"*
**So that** *AI nhận đủ thông tin USP của từng căn để viết tiêu đề & mô tả khai thác đúng thế mạnh thực tế*

## Acceptance
- [x] Cột `Phân loại` được map vào `cols` và truyền vào `userPrompt`
- [x] Label `userPrompt` cho `moTaGoc` (Mô tả chi tiết) được đổi thành rõ ràng hơn để AI hiểu đây là nguồn USP chính
- [x] `userPrompt` hướng dẫn AI đọc kỹ 2 trường này để extract USP trước khi viết
- [x] Test case: Trần Quang Diệu (Lô góc, Nội thất đẹp) → Tiêu đề & Mô tả phải đề cập lô góc, full nội thất, nhà mới

## Solution

> [!note]- Output / Format
> Ví dụ output kỳ vọng (Lô góc + Nội thất đẹp - giá trị):
> ```
> Tiêu đề: Trần Quang Diệu - Nhiêu Lộc - Q3 - 38m2 - Lô góc 2 mặt thoáng, full nội thất, nhà mới ở ngay - 8.75 tỷ
>
> + Vị trí: Quận 3, Phường Nhiêu Lộc. Hẻm 4m thông, lô góc 2 mặt thoáng, đón ánh sáng tự nhiên hoàn toàn.
> + Kết cấu: Nhà 3 tầng kiên cố, 2 PN lớn, 3 WC. Nội thất cao cấp tặng kèm theo nhà, vào ở ngay không phát sinh chi phí.
> + Kết nối & Tiện ích: ...
> + Pháp lý: Sổ hồng chính chủ, hoàn công đầy đủ, công chứng trong ngày.
> ```

> [!note]- Key logic
> **1. Thêm col mapping:**
> ```javascript
> phanLoai: getIdx("Phân loại")
> ```
> **2. Cập nhật userPrompt — thêm Phân loại + đổi label moTaGoc:**
> ```javascript
> "- Phân loại / Tag USP: " + (rowData[cols.phanLoai] || "") + "\n" +
> "- Điểm nổi bật (từ đầu chủ/môi giới): " + (rowData[cols.moTaGoc] || "") + "\n" +
> ```
> **3. Bổ sung instruction vào systemPrompt:**
> ```
> QUAN TRỌNG: Đọc kỹ 'Phân loại / Tag USP' và 'Điểm nổi bật' — đây là nguồn USP chính.
> Bắt buộc phản ánh các điểm nổi bật này vào Tiêu đề và Mô tả, không bỏ qua.
> ```

## Files touched
- `pool_backend_v3.gs` — cols mapping, `userPrompt` construction, `systemPrompt` instruction

## Notes
- Cột "Phân loại" cần verify tên header chính xác trong Sheet trước khi deploy
- `moTaGoc` đang map đúng cột "Mô tả chi tiết" — chỉ cần đổi label trong userPrompt
