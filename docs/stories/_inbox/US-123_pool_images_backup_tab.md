---
id: US-123
status: draft
date: 2026-07-09
size: M
---

# US-123: Thêm Sheet "Pool_Images" chuyên lưu hình ảnh (Hình thô & Hình tự thêm) làm Backup

## User story
**As an** Admin (Người dùng quản lý)
**I want** có một tab riêng tên là "Pool_Images" trên Google Sheets chuyên lưu trữ danh sách hình ảnh của mỗi căn nhà dưới dạng 2 dòng kề nhau (crawl/self)
**So that** tôi có một nguồn dữ liệu dự phòng (backup) độc lập, đầy đủ, không bị giới hạn số lượng ảnh và không làm ảnh hưởng đến luồng hoạt động thương mại hiện tại của trang web Vercel công khai.

## Acceptance
- [ ] **Khởi tạo Sheet:** Tab `Pool_Images` tự động được tạo trên Google Sheets (của tài khoản Admin) nếu chưa tồn tại, với cấu trúc cột: `["Mã", "Địa chỉ", "Loại", "Số lượng", "Ảnh 1", "Ảnh 2", ...]`.
- [ ] **Khởi tạo 2 dòng Kề nhau khi Cào mới:** Khi cào hoặc nhập mới một căn nhà, hệ thống tự động chèn đồng thời 1 cặp gồm dòng `"crawl"` (chứa ảnh thô cào về) và dòng `"self"` (được để trống hoàn toàn, `Số lượng = 0`) nằm kề sát nhau ở cuối sheet.
- [ ] **Cập nhật dòng self khi Biên tập:** Khi Admin biên tập ảnh (ẩn/hiện, thay đổi thứ tự, tải thêm ảnh mới) và lưu lại trên Admin Console, hệ thống cập nhật danh sách ảnh đã sửa trực tiếp vào dòng `"self"` tương ứng, tự động chèn thêm cột tiêu đề mới (`Ảnh 51`, `Ảnh 52`...) nếu số lượng ảnh vượt quá số cột hiện tại trên Sheet.
- [ ] **Cập nhật dòng crawl khi Cào lại:** Khi cào lại tin (Recrawl), hệ thống xóa sạch toàn bộ các cột ảnh cũ của dòng `"crawl"` tương ứng trên sheet `Pool_Images` và ghi lại loạt ảnh thô mới cào về. Dòng `"self"` được giữ nguyên 100% để bảo toàn dữ liệu chỉnh sửa của admin.
- [ ] **Khôi phục Database cục bộ:** Tiến trình khôi phục database cục bộ (`restore_db_from_sheets.py`) sẽ đọc trực tiếp dữ liệu ảnh thô và ảnh biên tập từ sheet backup `Pool_Images` để khôi phục chính xác bảng `listings_images` và các trường ảnh trong SQLite local (`raw_archive.db`).
- [ ] **Tính độc lập với Vercel:** Mọi hoạt động xem nhà và hiển thị hình ảnh công khai của khách hàng trên trang web Vercel công khai vẫn diễn ra bình thường, không bị thay đổi logic hay bị ảnh hưởng hiệu năng.

## Solution

> [!note]- Configuration
> Tab mới `Pool_Images` nằm trên cùng file Google Spreadsheet của Pool.
> ID Spreadsheet được cấu hình trong settings.json: `sheet_id` (production) hoặc `staging_pool_sheet_id` (staging).

> [!note]- Input
> Payload lưu hình ảnh từ Client gửi đi: danh sách URL ảnh đã sắp xếp và cập nhật trạng thái.

> [!note]- Output / Format
> Dòng trên tab `Pool_Images` có định dạng:
> - Cột A: Mã căn nhà (`TK-xxxx` hoặc `SYS-xxxx`).
> - Cột B: Địa chỉ (`Số nhà + Tên đường`).
> - Cột C: Loại (`crawl` hoặc `self`).
> - Cột D: Số lượng (Số nguyên).
> - Cột E trở đi: Các cột ảnh (`Ảnh 1`, `Ảnh 2`, ...).

```mermaid
sequenceDiagram
    actor Admin as Admin (Người dùng)
    participant AdminUI as Admin Console (Browser JS)
    participant Backend as Python Backend (Flask)
    database SQLite as CSDL Local (SQLite: raw_archive.db)
    participant SheetsPool as Google Sheets (Tab Pool & Source)
    participant SheetsImages as Google Sheets (Tab Pool_Images)

    %% Luồng Cào / Nhập mới
    Note over Backend, SheetsImages: Luồng 1: Cào / Nhập căn nhà mới
    Backend->>Backend: Cào tin / Quét Drive ra ảnh thô
    Backend->>SQLite: Lưu raw_images_tk_json & raw_drive_images_json
    Backend->>SheetsPool: Ghi đè dòng thông tin mới lên tab 'Pool'
    Backend->>SheetsImages: Ghi 2 dòng KỀ NHAU lên tab 'Pool_Images'<br/>(Dòng 1: crawl chứa ảnh cào, Dòng 2: self để TRỐNG)

    %% Luồng Biên tập & Lưu thay đổi
    Note over Admin, SheetsImages: Luồng 2: Admin biên tập & Lưu thay đổi / Lên sóng
    Admin->>AdminUI: Kéo thả, chỉnh sửa vai trò ảnh, ẩn/hiện, thêm ảnh mới
    AdminUI->>SheetsPool: 1. Ghi đè thông số lên tab 'Source' & 'Pool' (luồng cũ không đổi)
    AdminUI->>SheetsImages: 2. [BACKUP] Tìm dòng 'self' của Mã Hàng trên tab 'Pool_Images'<br/>và ghi đè danh sách ảnh đã sửa (tự động mở rộng cột tiêu đề nếu cần)

    %% Luồng Cào Lại (Recrawl)
    Note over Admin, SheetsImages: Luồng 3: Cào lại tin (Recrawl)
    Admin->>AdminUI: Bấm nút "Cào lại" (Recrawl)
    AdminUI->>Backend: Gọi API cào lại (POST /api/listings/<tk_id>/recrawl)
    Backend->>Backend: Quét lại tin nguồn, tải mảng hình ảnh thô mới nhất
    Backend->>SQLite: Cập nhật raw_images_tk_json & raw_drive_images_json mới
    Backend->>SheetsImages: Xóa sạch ảnh cũ trên dòng 'crawl' của căn nhà đó trên tab 'Pool_Images'<br/>và ghi đè loạt ảnh thô mới cào về. Dòng 'self' GIỮ NGUYÊN.

    %% Luồng Khôi phục Database
    Note over Backend, SheetsImages: Luồng 4: Khôi phục SQLite từ Sheets (Restore DB)
    Admin->>Backend: Kích hoạt khôi phục (Chạy script restore_db_from_sheets.py)
    Backend->>SheetsPool: 1a. Tải dữ liệu thuộc tính từ tab 'Pool' và 'Source'
    Backend->>SheetsImages: 1b. Tải dữ liệu hình ảnh từ tab 'Pool_Images'
    Backend->>Backend: 2. Hợp nhất thông tin thuộc tính & hình ảnh (crawl & self)
    Backend->>SQLite: 3. Tái tạo file raw_archive.db sạch sẽ để desktop app đọc nhanh
```

## 3. Cơ Chế Định Vị Dòng Động (Dynamic Row Lookup)

Để triệt tiêu hoàn toàn rủi ro lệch dòng khi người dùng chèn dòng, xóa dòng hoặc sắp xếp (sorting) trên Google Sheets, hệ thống sẽ sử dụng cơ chế **Tra cứu dòng động** thay vì dùng công thức cố định:

1. **Khi Client JS cần ghi đè dòng `self`:**
   - Client JS gửi một truy vấn đọc dải ô `Pool_Images!A:C` (chứa cột Mã và Loại).
   - Lặp qua mảng trả về để tìm dòng thứ $R$ thỏa mãn đồng thời: `A[R] == Mã căn` và `C[R] == "self"`.
   - Tiến hành ghi đè dữ liệu ảnh vào dải ô `Pool_Images!D{R}:N{R}` (với N tương ứng số lượng ảnh mới).

2. **Khi Backend cần ghi đè dòng `crawl` khi cào lại:**
   - Backend sử dụng gspread đọc các giá trị cột `Mã` và `Loại`.
   - Xác định dòng chính xác thỏa mãn `Mã == tk_id` (hoặc Mã Hàng) và `Loại == "crawl"`.
   - Thực hiện xóa sạch hình cũ và ghi đè hình mới lên dòng đó.

## 📋 Implementation Plan

- **Cách tiếp cận:**
  1. Thêm các hàm phụ trợ kiểm tra, khởi tạo và tự động mở rộng cột cho tab `Pool_Images` trên gspread (`pool_lego.py`).
  2. Bổ sung ghi đè ảnh crawl và khởi tạo dòng self trống tại luồng ghi/cập nhật căn nhà mới.
  3. Cập nhật mã nguồn JS client-side để tự động tìm dòng `self` của Mã căn trên tab `Pool_Images` và lưu đè mảng ảnh mới khi nhấn Save/Publish.
  4. Sửa lại tiến trình khôi phục SQLite để đọc ảnh từ tab `Pool_Images`.
  5. Viết kịch bản kiểm thử E2E Playwright để tự động hóa kiểm tra tính chính xác của 2 dòng và việc lưu trữ trên sheets.

## 📝 Task Checklist (TODO)

- [ ] **Thiết kế & Khảo sát:**
  - [ ] Khảo sát cấu trúc gspread và cấu trúc lưu ảnh thô hiện tại
  - [ ] Thống nhất tên sheet và các quy tắc chèn cột động
- [ ] **Triển khai Code:**
  - [ ] Hàm tạo tab `Pool_Images` và kiểm tra header động trong `pool_lego.py`
  - [ ] Tích hợp ghi 2 dòng crawl/self kề nhau trong `pool_lego.py`
  - [ ] Client JS tìm và cập nhật dòng `self` trên tab `Pool_Images` trong `lego_detail_admin.js`
  - [ ] Bổ sung cơ chế cập nhật dòng `crawl` khi cào lại trong `pool_lego.py`/`manager.py`
  - [ ] Sửa lại restore script `restore_db_from_sheets.py` để sử dụng dữ liệu từ `Pool_Images`
- [ ] **Kiểm thử & Đóng gói:**
  - [ ] Chạy kiểm thử tự động E2E Playwright kiểm tra đồng bộ hình ảnh
  - [ ] Build lại executable `KhangNgoCurator.exe`
  - [ ] Hoàn thành tài liệu stories và cập nhật Project Glossary

## 🛠️ Update Logic (Drafting while Doing)

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- *Sẽ cập nhật trong quá trình code*

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- *Sẽ cập nhật trong quá trình code*

## 🧠 Retro, Lessons Learned & Good Practices

- *Sẽ cập nhật sau khi hoàn thành tính năng*

## Verification Plan

### Automated Tests
- Chạy bộ kiểm thử E2E:
  ```bash
  .\RUN_TEST_E2E_HEADED.bat
  ```

### Manual Verification
1. Mở Admin Console, cào hoặc nhập thử 1 căn nhà mới. Kiểm tra Google Sheets tab `Pool_Images` xem có tự động tạo ra 2 dòng kề nhau (`crawl` chứa các ảnh thô, `self` để trống hoàn toàn).
2. Vào giao diện biên tập căn đó, thực hiện sửa thứ tự ảnh, ẩn ảnh hoặc up thêm ảnh mới, bấm lưu. Xác nhận dòng `self` trên `Pool_Images` được cập nhật chính xác danh sách ảnh mới.
3. Bấm nút "Cào lại" căn nhà đó. Xác nhận dòng `crawl` trên `Pool_Images` được xóa sạch các ảnh cũ và cập nhật lại ảnh thô mới cào về. Kiểm tra dòng `self` vẫn được giữ nguyên vẹn.
4. Chạy script khôi phục database cục bộ `restore_db_from_sheets.py`. Kiểm tra file `raw_archive.db` cục bộ xem bảng `listings_images` và các trường ảnh trong bảng `listings` được khôi phục chính xác danh sách ảnh tương ứng.
5. Mở web công khai của khách hàng trên Vercel, kiểm tra hiển thị bình thường.

## Files touched
- `pool_lego.py` — Khởi tạo sheet, chèn dòng kề nhau, cập nhật khi cào lại.
- `static/js/lego_detail_admin.js` — Client JS lưu đè danh sách hình ảnh đã sửa lên dòng `self`.
- `restore_db_from_sheets.py` — Khôi phục SQLite cục bộ từ tab `Pool_Images`.
- `manager.py` — Tích hợp luồng cào lại và gọi backend tương ứng.
- `fetcher.py` — Tải ảnh và khởi tạo dòng khi cào mới.
