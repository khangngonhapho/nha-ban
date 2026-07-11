---
id: US-011
status: done
date: 2026-05-20
size: S
replaces: US-009, US-010
---

# US-011: Mô tả tiện ích theo đặc trưng khu vực & kết nối giao thông

## User story
**As a** *Admin*
**I want** *phần "Kết nối & Tiện ích" mô tả đặc trưng con đường/khu vực và kết nối giao thông thực tế thay vì liệt kê tên địa điểm cụ thể*
**So that** *nội dung đúng 100%, có giá trị thực cho khách hàng, không bị hallucinate tên địa điểm sai vị trí*

## Acceptance
- [x] Bỏ instruction yêu cầu AI liệt kê tên cụ thể (chợ, siêu thị, trường, bệnh viện) trong `systemPrompt`
- [x] AI mô tả 3 khía cạnh mà nó biết đúng ở cấp độ khu vực: (1) đặc trưng con đường/khu dân cư, (2) kết nối ra các trục đường lớn lân cận, (3) tính chất sử dụng (yên tĩnh/sầm uất/dân trí...)
- [x] Test case: Trần Quang Diệu Q3 → output phải mô tả đúng đặc trưng tuyến đường (yên tĩnh, cây xanh, dân trí cao, kết nối Đinh Tiên Hoàng/Võ Thị Sáu)
- [x] Không còn xuất hiện tên địa điểm sai quận/khu vực
- [x] **[Refinement]** Phần kết nối giao thông phải nêu **tên đường cụ thể** (Đinh Tiên Hoàng, Võ Thị Sáu...) thay vì dùng cụm chung chung "các trục đường lớn" — AI biết mạng lưới đường phố chính xác nên có thể nêu đúng

## Solution

> [!note]- Output / Format
> Template kỳ vọng:
> ```
> + Kết nối & Tiện ích: [Đặc trưng con đường/khu vực này được biết đến là gì].
> Kết nối thuận tiện ra [các trục đường lớn lân cận] — [thời gian/ưu điểm giao thông].
> ```
> Ví dụ đúng (Trần Quang Diệu Q3):
> ```
> + Kết nối & Tiện ích: Đường Trần Quang Diệu thuộc khu dân cư yên tĩnh, cây xanh,
> an ninh tốt — một trong những tuyến đường được ưa chuộng nhất Q3. Kết nối nhanh
> ra Đinh Tiên Hoàng, Võ Thị Sáu và trung tâm Q1 chỉ 5-7 phút.
> ```
> Ví dụ sai (cũ theo US-009/010):
> ```
> + Kết nối & Tiện ích: Gần chợ Bến Thành (Q1!), Bệnh viện Hòa Hảo (Q10!)...
> ```

> [!note]- Key logic
> Instruction `+ Kết nối & Tiện ích` sau refinement:
> ```
> + Kết nối & Tiện ích: Mô tả đặc trưng con đường và khu vực xung quanh dựa trên
> kiến thức thực tế — con đường này nổi tiếng là gì (yên tĩnh, sầm uất, dân trí
> cao, an ninh tốt...), tính chất khu vực (dân cư/thương mại). Nêu TÊN CỤ THỂ các
> trục đường lớn lân cận mà nhà kết nối được (ví dụ: Đinh Tiên Hoàng, Võ Thị Sáu,
> Nguyễn Đình Chiểu) — KHÔNG dùng chung chung "các trục đường lớn".
> KHÔNG liệt kê tên địa điểm (chợ, siêu thị, bệnh viện, trường học).
> ```

## Files touched
- `pool_backend_v3.gs` — biến `systemPrompt` trong `batchGenerateContentAndWard`

## Notes
- US-009 (liệt kê tên cụ thể) và US-010 (bán kính 1km) đều fail ở production vì LLM không có geospatial knowledge chính xác về tọa độ số nhà
- Hướng B (Google Maps Places API) sẽ được implement riêng trong tương lai khi có resource
