---
id: US-117
status: in-progress
date: 2026-06-30
size: S
---

# US-117: Tự động hóa Sao lưu Định kỳ CSDL SQLite cục bộ (Automated Periodic Database Backup)

## User Story
**As an** Admin / Product Owner
**I want** the system to automatically perform periodic backups of the SQLite database in the background
**And** keep only the last 5 most recent backup files
**So that** I always have a fresh backup of my crawled data in a cloud-synchronized folder without any manual work.

## Acceptance Criteria
- [ ] Thiết lập luồng tự động sao lưu định kỳ CSDL `raw_archive.db` cục bộ chạy nền trong `manager.py` (quét và sao lưu mỗi 1 giờ nếu CSDL có sự thay đổi).
- [ ] Giới hạn số lượng tệp sao lưu tối đa là **5 bản gần nhất** trên thư mục đồng bộ Google Drive (`d:/LHTBrain/BDS_Backups`).
- [ ] Giữ nguyên cơ chế thông minh chỉ thực hiện sao lưu khi CSDL thực tế có sửa đổi (mtime mới hơn bản backup gần nhất) để tránh ghi file thừa trùng lặp.
- [ ] Chạy nghiệm thu Playwright E2E để đảm bảo server hoạt động ổn định, không bị nghẽn hay xung đột luồng.

## 📋 Implementation Plan
1. Tạo tệp câu chuyện US-117 (tệp này).
2. Đăng ký US-117 trong [docs/stories/INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md) ở trạng thái `in-progress`.
3. Cập nhật hàm `backup_database()` trong `manager.py` đổi giới hạn lưu trữ từ 15 xuống còn **5 bản**.
4. Viết hàm `start_periodic_backup_scheduler()` trong `manager.py` để chạy vòng lặp ngầm (quét mỗi 1 giờ) và kích hoạt nó khi khởi chạy server.
5. Kiểm thử E2E Playwright để xác nhận tính ổn định của hệ thống.

## 📝 Task Checklist (TODO)
- [x] **Khảo sát & Thiết kế:** Tạo file User Story US-117
- [x] **Đăng ký Index:** Đăng ký trạng thái US-117 trong INDEX.md
- [ ] **Cấu hình giới hạn:** Sửa đổi giới hạn xoay vòng backup thành 5 bản trong `manager.py`
- [ ] **Lập trình Scheduler:** Viết và kích hoạt bộ sao lưu định kỳ chạy ngầm trong `manager.py`
- [ ] **Kiểm thử E2E:** Chạy Playwright E2E và nghiệm thu thực tế

## Verification Plan
- Chạy `python scratch/run_all_e2e.py` và kiểm tra 100% PASS.
- Khởi động server, kiểm tra nhật ký log xem tính năng sao lưu định kỳ có được kích hoạt thành công hay không.
