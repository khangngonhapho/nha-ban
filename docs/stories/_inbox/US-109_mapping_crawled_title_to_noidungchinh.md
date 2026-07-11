---
id: US-109
status: accepted
date: 2026-06-27
size: M
---

# US-109: Lấy tiêu đề thô cào về lưu vào cột Nội dung chính trên Pool

## User story
**As a** Admin / Curator
**I want** trường `title` (tiêu đề thô) của căn nhà từ tin cào được lưu trực tiếp vào cột `Nội dung chính` trên Pool
**So that** rổ hàng thô phản ánh đúng tiêu đề gốc của Thiên Khôi, phục vụ Curation AI chính xác và đồng bộ thông tin gốc đầy đủ từ đối tác (KPI 1: Tốc độ biên tập và KPI 2: Chuẩn hóa dữ liệu).

## Acceptance
- [x] Khi cào lẻ 1 căn hoặc cào hàng loạt qua Proptech API, trường `title` (tiêu đề thô hiển thị trên danh sách card của Thiên Khôi) được trích xuất và lưu vào cột `Noi_dung_chinh` (Nội dung chính) trong CSDL SQLite thay vì tự sinh chuỗi ghép nối như hiện tại.
- [x] Khi xuất bản/đồng bộ dữ liệu từ SQLite local hoặc qua Curator Web lên Google Sheets tab `Pool`, giá trị cột `Nội dung chính` (cột J / index 9) phải ghi nhận giá trị tiêu đề thô đã cào này.
- [x] Hỗ trợ fallback: Nếu thông tin thô cào về không có trường `title` (ví dụ cào qua các phương thức cũ hoặc trường trống), tự động ghép nối thông tin địa chỉ + kỹ thuật làm fallback để tránh cột trống.
- [x] Userscript cào tin trên Tampermonkey (`static/js/thienkhoi_list_scraper.user.js`) gửi kèm trường `title` trong payload POST `/api/listings/{tk_id}/recrawl` hoặc `/api/crawl` để backend lưu trữ đồng bộ.
- [x] Chạy bộ E2E Test Suite thành công 100% không lỗi hồi quy.

## Solution

> [!note]- Key logic
> - **Tampermonkey Userscript:** Sửa `static/js/thienkhoi_list_scraper.user.js` để đọc trường `title` của card nguồn hàng và gửi kèm trong JSON body của request POST `/api/listings/{tkId}/recrawl`.
> - **Backend Server (`manager.py`):**
>   - Đọc trường `title` từ request payload gửi lên nếu có, gán cho `noi_dung_chinh`.
>   - Nếu không có `title`, tự động sinh chuỗi fallback bằng cách ghép nối: ngõ số nhà, tên đường, diện tích (nếu diện tích sổ và thực tế khác nhau thì dùng dạng double-area `DT_so/DT_thuc`, ví dụ `46/58`), số tầng, mặt tiền, chiều sâu, giá chào tỷ.
> - **CSDL SQLite & Sheets Sync (`pool_lego.py` & `fetcher.py`):** Đồng bộ hóa logic fallback và lưu trữ tiêu đề thô.
> - **Công cụ migration (`scratch/standardize_existing_noi_dung_chinh.py`):** Quét 96 listings cũ, tính toán và chuẩn hóa lại cột `Noi_dung_chinh` rồi batch update toàn bộ cột J trên Google Sheets Pool `J2:J97`.

## 📋 Implementation Plan
- **Cách tiếp cận:**
  1. Nâng cấp Userscript để trích xuất `title` gốc từ DOM của web Thiên Khôi và đính kèm vào POST payload.
  2. Bổ sung endpoint backend `/api/listings/<tk_id>/recrawl` và pipeline cào hàng loạt để chấp nhận trường `title` này.
  3. Xây dựng logic sinh fallback clean title với định dạng diện tích kép `DT Trên sổ/DT Thực tế` khi hai diện tích lệch nhau (ví dụ: `46/58` thay vì chỉ hiển thị một diện tích).
  4. Chạy migration script để đồng bộ dữ liệu lịch sử trên cả database SQLite cục bộ và Google Sheets Pool.
  5. Đóng gói app EXE mới và chạy kiểm thử tự động.

## 📝 Task Checklist (TODO)
- [x] **Userscript:** Trích xuất title và gửi lên API | Đã test userscript gửi payload
- [x] **Backend API:** Nhận `title` từ request payload | Áp dụng logic fallback & double-area format
- [x] **Migration:** Standardize 96 dòng dữ liệu lịch sử | Batch update Google Sheets Pool cột J
- [x] **Verification:** Viết & chạy kịch bản E2E Test | Đạt 100% PASS
- [x] **Build & Release:** Rebuild KhangNgoCurator.exe | Deploy Live

## 🛠️ Update Logic (Drafting while Doing)

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:**
  - *Sự cố:* Cập nhật Google Sheets row-by-row cho 96 dòng bị chậm và dễ dính lỗi rate limit 429 từ Google Sheets API.
  - *Khắc phục:* Viết script sử dụng cập nhật batch `sheet.update(range_name='J2:J97', values=[...])` chỉ với 1 API call, cực kỳ nhanh chóng và an toàn.
  - *Sự cố:* Quá trình build file EXE bị lỗi khóa file `pyexpat.pyd` do một phiên Curator App cũ vẫn đang chạy ngầm hoặc file lock chưa được release.
  - *Khắc phục:* Dọn dẹp sạch thư mục `dist/KhangNgoCurator/` và kill các tiến trình Python/Curator App chạy ẩn trước khi chạy PyInstaller.

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- **Script kiểm thử thô / nháp đã chạy:** `python scratch/standardize_existing_noi_dung_chinh.py`
- **Output kết quả nháp & Điểm nghẽn đã vượt qua:** Standardized 96 database rows và batch updated Google Sheets J2:J97 thành công.

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** Trước đây khi cào nguồn hàng Thiên Khôi, tiêu đề thô gốc (chứa các thông tin quan trọng do người đăng nhập ghi) bị ghi đè hoàn toàn bởi chuỗi tự sinh ở backend, dẫn đến mất dữ liệu ngữ cảnh thô.
- **Nguyên nhân gốc rễ (Root Cause):** Backend tự động override `Noi_dung_chinh` bằng chuỗi thông số kỹ thuật do ban đầu không nhận được `title` từ userscript ở giao diện danh sách.
- **Giải pháp phòng ngừa:** Đưa trường `title` vào payload gửi từ userscript và lưu trữ trực tiếp. Đồng thời cải thiện hàm fallback ghép nối tiêu đề có hỗ trợ double-area (`{area}/{actualArea}`) để tối đa hóa lượng thông tin lưu giữ.

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm code & Cấu hình:** Khi thực hiện update hàng loạt (migration) trên Google Sheets, luôn gom dữ liệu lại thành danh sách 2 chiều và sử dụng batch update (ví dụ: `update(range_name=..., values=...)`) thay vì lặp qua từng dòng gọi `update_cell` để tránh dính HTTP 429 Rate Limit.
- **Kinh nghiệm kiểm thử:** Tạo môi trường mock hoàn toàn requests của Google Sheets và OAuth để chạy test E2E nhanh và độc lập (không cần mạng thực tế).

## Verification Plan

### Automated Tests
- Chạy test E2E Playwright:
  ```powershell
  python scratch/test_e2e_curation.py
  ```
- Kết quả: **100% PASS**

### Manual Verification
- Kiểm tra tab `Pool` trên Google Sheets, cột J (Nội dung chính) đã được chuyển sang định dạng tiêu đề thô cào về hoặc fallback ghép nối thông số kèm diện tích kép (ví dụ: `46/58`) đối với các căn lệch diện tích.

## Files touched
- `fetcher.py`
- `index.html`
- `manager.py`
- `pool_lego.py`
- `static/js/thienkhoi_list_scraper.user.js`
