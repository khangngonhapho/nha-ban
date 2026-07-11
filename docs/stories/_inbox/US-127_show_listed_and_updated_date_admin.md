---
id: US-127
status: accepted
date: 2026-07-09
size: S
---

# US-127: Hiển thị Ngày Niêm Yết và Ngày Cập Nhật Trên Card Admin

## User story
**As an** Admin
**I want** to see the listed date ("ngày niêm yết") and updated date ("ngày cập nhật") of a property on its card in the admin list view
**So that** I can track when listings were posted or updated on Thiên Khôi and verify freshness.

## Acceptance
- [x] Add `createdAt`, `updatedAt`, and `listedAt` to `"json_ui_fields"` in `settings.json`.
- [x] Update `static/js/lego_render_admin.js` to extract, format, and render dates on the property cards.
- [x] Format dates into standard Vietnamese format `DD/MM/YYYY`.
- [x] Display "Niêm yết" (using `listedAt` or `createdAt` fallback) and "Cập nhật" (using `updatedAt`) on the admin card view.
- [x] Ensure that sorting by time ("newest") runs correctly and ordering is consistent.

## Solution

> [!note]- Configuration
> Settings in `settings.json` under `json_ui_fields`:
> ```json
> "json_ui_fields": [
>     "Criteria_Duong_truoc_nha",
>     "createdAt",
>     "updatedAt",
>     "listedAt"
> ]
> ```

> [!note]- Input
> Scraped dates in the property data structure:
> - `p.json_ui_parsed.createdAt`: creation timestamp
> - `p.json_ui_parsed.updatedAt`: last update timestamp
> - `p.json_ui_parsed.listedAt`: listing timestamp

> [!note]- Output / Format
> Display on the admin card:
> 📅 Niêm yết: DD/MM/YYYY
> 🔄 Cập nhật: DD/MM/YYYY

## 📋 Implementation Plan
- **Cách tiếp cận:**
  1. Thêm các trường ngày (`createdAt`, `updatedAt`, `listedAt`) vào cấu hình `json_ui_fields` trong `settings.json`. Nhờ cơ chế tự động trích xuất của `extract_json_ui_data`, các trường này sẽ được gom vào cột `JSON_UI` của Google Sheets Pool khi cào/biên tập.
  2. Sửa file `static/js/lego_render_admin.js` để đọc dữ liệu ngày từ `p.json_ui_parsed`. Định dạng ngày sang `DD/MM/YYYY` (hoặc kèm giờ) và hiển thị trực quan dưới dạng hàng văn bản phụ trên Card Admin.
  3. Kiểm tra xem nút sắp xếp thời gian (⏱️) trên Vercel Admin hoạt động đúng (sử dụng thuộc tính `temp_id` hoặc row index đại diện cho thứ tự mới nhất).

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát cấu trúc cơ sở dữ liệu và dữ liệu cào thô Proptech API.
  - [x] Xác định cách thức truyền dữ liệu ngày về Client qua cột `JSON_UI`.
- [x] **Triển khai Code:**
  - [x] Cấu hình `settings.json`: Thêm trường vào `json_ui_fields`.
  - [x] Sửa file `static/js/lego_render_admin.js`: Trích xuất, định dạng ngày tháng và hiển thị trên Card.
- [x] **Kiểm thử sơ bộ:**
  - [x] Khởi chạy local server, thực hiện recrawl thử nghiệm 1 căn để ghi nhận `JSON_UI` mới có chứa ngày.
  - [x] Kiểm tra giao diện Card Admin xem ngày niêm yết & ngày cập nhật có hiển thị chính xác.
  - [x] Kiểm tra tính năng sắp xếp.

## 🛠️ Update Logic (Drafting while Doing)

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- Bổ sung trường `listedAt` trong file `api/routes_crawl.py` và `fetcher.py` để đồng bộ hoàn toàn dữ liệu thô từ Proptech API về SQLite và `JSON_UI` column.
- Nhận thấy cơ chế lưu của `JSON_UI` qua `json_ui_fields` cực kỳ mạnh và linh hoạt, tự động map các thuộc tính mới mà không cần sửa schema SQLite của bảng Pool.

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- Tạo và chạy thành công test script `scratch/test_recrawl_dates.py` kiểm định trích xuất `JSON_UI` với kết quả:
  ```json
  {
      "Criteria_Duong_truoc_nha": "",
      "createdAt": "2026-05-23T04:11:26.939Z",
      "updatedAt": "2026-05-23T05:12:26.939Z",
      "listedAt": "2026-05-23T03:10:26.939Z"
  }
  ```
- Thêm unit test `test_json_ui_fields_contains_dates` vào `tests/test_config.py` và tạo file test mới `tests/test_crawler_dates.py`. Toàn bộ 105 tests đều vượt qua thành công (`passed`).

## 🧠 Retro, Lessons Learned & Good Practices
- Việc tận dụng cột `JSON_UI` giúp giảm thiểu chi phí sửa đổi schema CSDL (SQLite/Google Sheets) và tối ưu hóa lượng dữ liệu tải về client-side.
- Giữ logic sắp xếp thời gian (⏱️) dựa trên `temp_id` (row index tăng dần khi cào mới) giúp đảm bảo tương thích ngược 100% với các căn cũ không có siêu dữ liệu thời gian.

## Verification Plan

> [!check]- Automated Tests
> Không áp dụng test tự động cho UI render, nhưng có thể viết test case kiểm tra cấu hình `json_ui_fields` và trích xuất dữ liệu trong `pool_lego.py`.

> [!check]- Manual Verification
> 1. Chạy local server `python manager.py` và cào/recrawl một căn.
> 2. Đẩy lên Sheets và tải lại trang Web Admin.
> 3. Kiểm tra thông tin card căn nhà đó xem có hiển thị:
>    - Ngày niêm yết (e.g., 23/05/2026)
>    - Ngày cập nhật (e.g., 23/05/2026)
> 4. Nhấp nút Sắp xếp thời gian (⏱️) để kiểm tra thứ tự sắp xếp.

## Files touched
- `settings.json` — Cấu hình json_ui_fields
- `static/js/lego_render_admin.js` — Hiển thị ngày trên Card Admin
- `pool_lego.py` — Ghi đè chọn lọc đồng bộ
- `manager.py` — Trộn ảnh thông minh nâng cao

## Truth Cards bị ảnh hưởng
- **DF-001 v2**: Cập nhật chính sách ghi đè đồng bộ Google Sheets bảo vệ chất xám và trộn ảnh nâng cao.
