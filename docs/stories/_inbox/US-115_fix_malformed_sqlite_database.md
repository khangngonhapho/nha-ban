---
id: US-115
status: in-progress
date: 2026-06-29
size: S
---

# US-115: Khắc phục lỗi cơ sở dữ liệu SQLite bị hỏng (malformed) khi khởi chạy ứng dụng

## User story
**As an** Admin
**I want** to enable SQLite WAL mode and add a token abort safeguard in the userscript
**So that** database files are protected against corruption when closed abruptly, and the crawler stops immediately on token expiration without infinite loops.

## Acceptance
- [ ] Tích hợp thành công `PRAGMA journal_mode=WAL;` vào hàm khởi tạo cơ sở dữ liệu `init_db()`.
- [ ] Userscript `thienkhoi_list_scraper.user.js` lập tức ngừng cào hàng loạt và hiển thị cảnh báo đỏ khi gặp lỗi xác thực 401/403.
- [ ] Kiểm thử tự động E2E Playwright chạy đạt 100% PASS.

## Solution

> [!note]- Configuration
> Biến cấu hình hoạt động:
> ```
> active_pool_system=Pool1
> ```

> [!note]- Key logic
> - Kích hoạt SQLite WAL mode trong `pool_lego.py` qua `PRAGMA journal_mode=WAL;`.
> - Thêm cờ `isAuthError` trong Userscript `crawlBulk()` để dừng vòng lặp ngay khi gặp phản hồi 401/403.

## Proposed Changes

### 1. Database Curation & Optimization

#### [MODIFY] [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py)
Kích hoạt chế độ WAL trong hàm `init_db()` để bảo vệ tệp tin CSDL khỏi hư hỏng khi tắt ứng dụng đột ngột.

### 2. Browser Crawler Script (Userscript)

#### [MODIFY] [thienkhoi_list_scraper.user.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/thienkhoi_list_scraper.user.js)
Thêm cờ hiệu và kiểm tra lỗi xác thực để dừng ngay lập tức tiến trình cào hàng loạt.

## 📋 Implementation Plan
> [!plan]- Kế hoạch Triển khai (Bắt buộc cho Size M/L/XL)
> - **Cách tiếp cận:** Tích hợp WAL Mode vào SQLite và cấu hình Userscript dừng cào khi hết token.
> - **Các bước triển khai dự kiến:**
>   1. Tích hợp WAL mode vào `init_db()` trong `pool_lego.py`.
>   2. Vá Userscript `thienkhoi_list_scraper.user.js`.
>   3. Chạy local server và kiểm tra sự tồn tại của file `.db-wal`.
>   4. Chạy `python scratch/run_all_e2e.py` để chạy bộ test Playwright.

## 📝 Task Checklist (TODO)
> [!todo]- Danh sách việc cần làm để theo dõi tiến độ
> - [/] **Thiết kế & Khảo sát:** [x] Khảo sát CSDL hỏng | [x] Thiết lập giải pháp WAL & Userscript Abort
> - [/] **Triển khai Code:** [x] Tích hợp SQLite WAL mode | [x] Vá lỗi Userscript tự ngắt cào
> - [ ] **Kiểm thử sơ bộ:** [ ] Kiểm tra hoạt động WAL mode | [ ] Giả lập lỗi token | [ ] Chạy test E2E

## 🛠️ Update Logic (Drafting while Doing)

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:** *[Ghi nhận lỗi cụ thể và giải pháp điều chỉnh code]*
- **Phát kiến ngoài kế hoạch / Điểm tối ưu phát hiện khi code:** *[Ghi nhận nếu có]*

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- **Script kiểm thử thô / nháp đã chạy:** *[Ví dụ: python test_xxx.py]*
- **Output kết quả nháp & Điểm nghẽn đã vượt qua:** *[Dán log lỗi và phân tích nếu có]*

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)

### 1. Nhật ký Sự cố & Tiền trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** *[Mô tả lỗi hoặc blocker]*
- **Nguyên nhân gốc rễ (Root Cause):** *[Phân tích lý do]*
- **Giải pháp phòng ngừa:** *[Cách xử lý để không lặp lại]*

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm code & Cấu hình:** *[Mẹo viết code hoặc setup tối ưu]*
- **Kinh nghiệm kiểm thử:** *[Mẹo test nhanh hoặc phát hiện lỗi sớm]*

## Verification Plan

> [!check]- Automated Tests
> Chạy toàn bộ bộ test suite Playwright E2E để kiểm tra lỗi hồi quy:
> ```powershell
> python scratch/run_all_e2e.py
> ```

> [!check]- Manual Verification
> 1. Chạy ứng dụng để kích hoạt hàm `init_db()`.
> 2. Kiểm tra xem tệp tin `raw_archive.db` có file phụ `.db-wal` sinh ra bên cạnh để xác nhận WAL mode hoạt động.
> 3. Kiểm tra tính năng ngắt cào của Userscript bằng cách giả lập cookie sai.

## Files touched
- `docs/stories/_inbox/US-115_fix_malformed_sqlite_database.md` — Tài liệu User Story mới
- `docs/stories/INDEX.md` — Đăng ký US mới
- `docs/NEXT_SESSION.md` — Cập nhật kế hoạch phiên tiếp theo
- `SOURCE_OF_TRUTH.md` — Ghi nhận Change Log
- `pool_lego.py` — Kích hoạt WAL mode
- `static/js/thienkhoi_list_scraper.user.js` — Vá lỗi ngắt cào hàng loạt
