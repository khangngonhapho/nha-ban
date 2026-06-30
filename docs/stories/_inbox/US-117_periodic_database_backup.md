---
id: US-117
status: in-progress
date: 2026-06-30
size: S
---

# US-117: Tự động hóa Sao lưu Định kỳ CSDL SQLite cục bộ (Automated Periodic Database Backup)

## User Story
**As an** Admin / Product Owner
**I want** the system to have a standalone background backup script
**And** run it independently of manager.py via Windows Task Scheduler every 15 minutes
**And** keep only the last 5 most recent backup files in a cloud-synchronized folder
**So that** I always have a fresh backup of my crawled data even if manager.py is closed.

## Acceptance Criteria
- [x] Tạo script sao lưu độc lập `scratch/run_backup_only.py` để chạy qua Windows Task Scheduler (quét và sao lưu mỗi 15 phút nếu CSDL có sự thay đổi).
- [x] Giới hạn số lượng tệp sao lưu tối đa là **5 bản gần nhất** trên thư mục đồng bộ Google Drive (`d:/LHTBrain/BDS_Backups`).
- [x] Áp dụng cơ chế thông minh chỉ thực hiện sao lưu khi CSDL thực tế có sửa đổi (mtime mới hơn bản backup gần nhất) để tránh ghi file thừa trùng lặp.
- [x] Chạy nghiệm thu Playwright E2E để đảm bảo toàn hệ thống hoạt động ổn định.

## 📋 Implementation Plan
1. Tạo tệp câu chuyện US-117 (tệp này).
2. Đăng ký US-117 trong [docs/stories/INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md) ở trạng thái `in-progress`.
3. Viết và hoàn thiện script sao lưu độc lập [scratch/run_backup_only.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/run_backup_only.py) với giới hạn xoay vòng **5 bản** và so khớp thời gian thay đổi mtime.
4. Hướng dẫn chi tiết người dùng thiết lập lịch quét 15 phút/lần độc lập thông qua Windows Task Scheduler.
5. Kiểm thử E2E Playwright để xác nhận tính ổn định của hệ thống.

## 📝 Task Checklist (TODO)
- [x] **Khảo sát & Thiết kế:** Tạo file User Story US-117
- [x] **Đăng ký Index:** Đăng ký trạng thái US-117 trong INDEX.md
- [x] **Lập trình Script Độc lập:** Viết xong script `scratch/run_backup_only.py` với cấu hình 5 bản và quét mtime
- [x] **Hướng dẫn Cấu hình:** Bàn giao tài liệu hướng dẫn thiết lập Windows Task Scheduler
- [x] **Kiểm thử E2E:** Chạy Playwright E2E và nghiệm thu thực tế

## Verification Plan
- Chạy `python scratch/run_all_e2e.py` và kiểm tra 100% PASS.
- Chạy thử nghiệm script độc lập `python scratch/run_backup_only.py` và kiểm tra tính hợp lệ của tệp backup được sinh ra tại `d:/LHTBrain/BDS_Backups/`.
