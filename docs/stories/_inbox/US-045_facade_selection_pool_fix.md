---
id: US-045
status: done
date: 2026-05-29
size: S
---

# US-045: Chọn hình mặt tiền trong web admin cho căn chưa lên sóng (Pool Curation Facade Fix)

## User story
**As an** Admin / Curator
**I want** to select and lock the Facade Image (Hình Mặt Tiền) when editing properties from the Pool tab ("chưa lên sóng")
**So that** the selected facade image displays with the "🔒 Mặt Tiền" badge and red border, and is saved correctly to the Source Google Sheet upon publishing (⚡ Lên sóng), contributing to KPI 1 (Tốc độ biên tập & độ chính xác curation).

## Acceptance
- [x] Khi click chọn xem chi tiết một căn chưa lên sóng (từ tab Pool) trong Web Admin:
  - Trạng thái ảnh mặt tiền hiện tại (lấy từ cột 29 của dòng Pool - `p.pool_row_data[29]`) được nhận diện chính xác.
  - Nếu đã có ảnh mặt tiền sẵn, ảnh này phải hiển thị viền đỏ và nhãn `🔒 Mặt Tiền` tương tự như các căn đã lên sóng.
  - Nếu chưa có ảnh mặt tiền sẵn (cột 29 trống), không có ảnh nào bị dán nhãn `🔒 Mặt Tiền` mặc định, và giá trị `#editCoverImgUrl` được khởi tạo là rỗng (`""`).
- [x] Khi sử dụng công cụ "🔒 Mặt Tiền" để chọn mới hoặc thay đổi hình mặt tiền đã có:
  - Ảnh click chọn mới lập tức nhận viền đỏ và nhãn `🔒 Mặt Tiền`, đồng thời gỡ bỏ viền đỏ & nhãn khỏi ảnh mặt tiền cũ (nếu có).
  - Giá trị input ẩn `#editCoverImgUrl` được cập nhật chính xác bằng URL của ảnh được chọn mới này.
- [x] Khi bấm "⚡ Lên sóng & Lưu" (`saveNewListingFromPool`), giá trị ảnh mặt tiền mới chọn/cập nhật này được đẩy đồng bộ chính xác sang cột AM (`Hình Mặt Tiền`) của Google Sheets Source.

## Solution
*(Sẽ bổ sung chi tiết thiết kế, cấu hình, Input/Output và Key logic khi đưa vào triển khai. Đồng thời thực hiện đánh giá lại size tại đây)*

## 📋 Implementation Plan
*(Sẽ bổ sung chi tiết các bước tiếp cận và phương án triển khai kỹ thuật tại đây khi bắt đầu thiết kế - bắt buộc cho Size M/L/XL)*

## 📝 Task Checklist (TODO)
*(Sẽ thiết lập danh sách việc cần làm cụ thể để theo dõi tiến độ code và test tại đây)*

## 🛠️ Update Logic (Drafting while Doing)
*(Sẽ sử dụng để ghi nhận logic thô trong quá trình triển khai thực tế)*

## Verification Plan
*(Sẽ bổ sung các bước kiểm thử tự động/thủ công khi đưa vào triển khai)*

## Files touched
*(Sẽ bổ sung danh sách file tác động khi đưa vào triển khai)*

## 🔄 Change Requests (Yêu cầu Thay đổi)
*(Sẽ sử dụng để ghi nhận nhật ký thay đổi yêu cầu của PO khi test hoặc triển khai)*
