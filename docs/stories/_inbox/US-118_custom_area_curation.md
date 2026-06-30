---
id: US-118
status: accepted
date: 2026-07-01
size: S
---

# US-118: Tùy biến Diện tích Sổ & Diện tích Thực tế trên Sheet Source và Vercel Detail

## User Story
**As an** Admin / Product Owner
**I want** the system to support editing and saving custom book area (DT Trên sổ) and actual area (DT Thực tế) on the Source sheet
**And** show both values on the customer detail view on Vercel without the word "Custom"
**And** calculate unit price (đơn giá) as Price divided by DT Trên sổ (instead of DT Thực tế)
**So that** I can curate the area values and display accurate unit prices to my customers.

## Acceptance Criteria
- [x] Sheet Source: Cột F (index 5) tái sử dụng đại diện cho **DT Thực tế** và cột AV (index 47) được thêm mới đại diện cho **DT Trên sổ**.
- [x] Giao diện Biên tập (Vercel) hiển thị 2 ô nhập diện tích: **DT Thực tế** và **DT Trên sổ** (không hiển thị chữ "Custom" trên nhãn).
- [x] Khi lưu biên tập hoặc xuất bản căn mới: **DT Thực tế** lưu vào Cột F và **DT Trên sổ** lưu vào Cột AV trên sheet Source.
- [x] Google Apps Script sync (`pool_backend_v3.gs`) đồng bộ đúng mảng 48 cột, bảo vệ 2 trường diện tích custom này trong mảng `protectedIndices` khỏi bị chép đè.
- [x] SQLite local được thêm cột và cập nhật để đồng bộ với cấu trúc dữ liệu mới.
- [x] Giao diện Khách hàng (Vercel Client View) hiển thị cả 2 dòng **DT Trên sổ** và **DT Thực tế** từ Source, không có chữ "Custom".
- [x] Đơn giá (`giabq`) được tính toán bằng `(Giá bán * 1000) / DT Trên sổ`.

## 📋 Implementation Plan
1. Tạo tệp câu chuyện US-118 (tệp này).
2. Đăng ký US-118 trong [docs/stories/INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md) ở trạng thái `in-progress`.
3. Cập nhật Google Apps Script [pool_backend_v3.gs](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_backend_v3.gs) để đồng bộ diện tích và các cột mở rộng, đồng thời bảo vệ cột F và AV.
4. Cập nhật cơ sở dữ liệu SQLite trong [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py) and [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py) để lưu trữ các cột diện tích mới.
5. Cập nhật Web Admin Curation UI [static/js/lego_detail_admin.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_admin.js) để chỉnh sửa và lưu cả hai trường diện tích.
6. Cập nhật Web Client UI [static/js/lego_detail_client.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_client.js) hiển thị cả hai trường diện tích và tính đơn giá theo DT Trên sổ.
7. Cập nhật calculations và mapping trong [static/js/lego_core.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_core.js) và [static/js/lego_helpers.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_helpers.js).
8. Cập nhật Canvas View [canvas.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/canvas.html).

## 📝 Task Checklist (TODO)
- [x] **Khảo sát & Thiết kế:** Đăng ký và lập kế hoạch US-118
- [x] **Google Sheets & Apps Script:** Đồng bộ và bảo vệ 2 trường diện tích
- [x] **Database & Backend:** Thêm các trường vào SQLite và Python backend
- [x] **Vercel Detail page (Admin/Client):** Cập nhật panel Biên tập và hiển thị thông tin kép cho Khách hàng
- [x] **Canvas:** So sánh Canvas
- [x] **Kiểm thử E2E:** Chạy Playwright E2E và nghiệm thu thực tế
