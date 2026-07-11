---
id: US-015
status: superseded
date: 2026-05-21
size: S
note: Root cause sai. TK CDN block mobile access at server level. Reverted.
---

# US-015: Fix ảnh đen trong modal chi tiết trên mobile

## User story
**As a** *Khách hàng xem nhà trên điện thoại*
**I want** *tất cả ảnh trong trang chi tiết hiển thị đúng, không bị đen*
**So that** *trải nghiệm xem ảnh nhà mượt mà trên mọi thiết bị*

## Acceptance
- [x] Ảnh trong modal chi tiết không còn bị đen trên mobile
- [x] Ảnh vẫn đủ sắc nét trên cả mobile và desktop
- [x] Không có hiện tượng flash/giật khi load ảnh

## Root cause
Drive thumbnail `w1200` fail trên một số thiết bị mobile (CDN throttle / băng thông) → ảnh không load được → hiển thị đen trên nền lightbox. Desktop không bị vì tốc độ cao hơn.

## Solution

> [!note]- Key logic
> Đổi size thumbnail từ `w1200` → `w800` trong hàm `fixImgUrl` khi gọi cho modal/lightbox.
> `w800` đủ sắc nét cho mọi màn hình (kể cả Retina 2x: 390px × 2 = 780px).

## Rollback
```powershell
git revert HEAD
git push
```

## Files touched
- `index.html` — hàm `fixImgUrl` hoặc nơi gọi với tham số `w1200`
