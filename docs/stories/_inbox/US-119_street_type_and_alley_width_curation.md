---
id: US-119
status: accepted
date: 2026-07-01
size: S
---

# US-119: Quản lý và Biên tập Đường trước nhà & Độ rộng hẻm trên Vercel Detail & local Python Backend

## User Story
**As an** Admin / Product Owner
**I want** to edit the custom street type (dropdown) and custom alley width (text input) independently on Vercel's curation editor
**And** display the original road type (`Criteria_Duong_truoc_nha`) and raw road width (`Đường trước nhà (m)`) in the read-only Specs ("Thông tin") section of the Vercel detail page
**And** ensure that custom alley width (do_rong_hem, Column O) is protected from being overwritten by sync triggers in Apps Script
**And** align local SQLite and AI payload mappings
**So that** I can accurately curate road specs without any data leakage or incorrect overlaps on the frontend.

## Acceptance Criteria
- [x] Giao diện read-only Specs ("Thông tin") trên Vercel:
  - `"Đường trước nhà:"` hiển thị `Criteria_Duong_truoc_nha` (từ JSON_UI của Pool).
  - `"Đường vào nhỏ nhất:"` hiển thị `raw_duong_truoc_nha` kèm đơn vị `m` (không bị fallback nhầm sang custom street type text).
- [x] Giao diện Curation Editor (BIÊN TẬP panel) trên Vercel:
  - Hiển thị dropdown `"Đường trước nhà custom:"` (lưu vào Column N `duong_truoc_nha` của Source).
  - Thêm ô nhập văn bản `"Độ rộng hẻm custom (m):"` (lưu vào Column O `do_rong_hem` của Source, mặc định trống nếu giá trị là `-`).
- [x] Apps Script `pool_backend_v3.gs`:
  - Thêm index `14` (Column O, `do_rong_hem`) vào danh sách `protectedIndices` để bảo vệ độ rộng hẻm đã biên tập.
  - Cập nhật header file ghi nhận US-119.
- [x] Python local server `manager.py`:
  - Lưu `phan_loai_hem` (từ UI) vào cột `Criteria_Duong_truoc_nha` của bảng `listings_custom_v2` khi lưu curation.
- [x] Scripts và helpers:
  - `static/js/lego_helpers.js`: Gửi đúng `duongTruocNha` (độ rộng) và `phanLoaiHem` (loại đường) cho API AI.
  - `static/js/lego_core.js`: Sửa default unmatched Pool listings (rong_hem mặc định lấy từ raw width poolRow[60]). Ngắt các cơ chế fallback của trường raw sang custom khi poolRow là null.

## 📋 Implementation Plan
1. Tạo tệp câu chuyện US-119 (tệp này).
2. Đăng ký US-119 trong [docs/stories/INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md) ở trạng thái `in-progress`.
3. Cập nhật Apps Script [pool_backend_v3.gs](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_backend_v3.gs) bảo vệ index 14.
4. Cập nhật Python backend [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py) lưu `Criteria_Duong_truoc_nha`.
5. Cập nhật frontend state store [static/js/lego_core.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_core.js) (sửa mapping và fallback).
6. Cập nhật frontend helpers [static/js/lego_helpers.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_helpers.js) (sửa payload AI).
7. Cập nhật Web Admin Curation UI [static/js/lego_detail_admin.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_admin.js) thêm trường input, sửa render và luồng save.

## 📝 Task Checklist (TODO)
- [x] **Khảo sát & Thiết kế:** Đăng ký và lập kế hoạch US-119
- [x] **Google Sheets & Apps Script:** Bảo vệ trường do_rong_hem trên Source
- [x] **Database & Backend:** Cập nhật API save của SQLite local
- [x] **Vercel Detail page (Admin Curation):** Tách biệt hiển thị read-only, thêm trường Độ rộng hẻm custom và sửa luồng lưu
- [x] **AI Payload & Core:** Sửa payload AI và logic fallback
- [x] **Kiểm thử & Nghiệm thu:** Kiểm tra luồng lưu và hiển thị trên local

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Sự cố & Nguyên nhân (Incidents & Root Causes)
*   **Lệch chỉ mục dữ liệu thô:** Lỗi hiển thị trống `"Đường vào nhỏ nhất"` trên giao diện chi tiết căn Pool thô phát sinh do ánh xạ lệch chỉ số cột (chỉ số 59 thay vì 60).
*   **Thiếu phân tích JSON_UI:** Giao diện xem trước căn thô không parse trường dữ liệu động `JSON_UI` ở phía frontend làm nhầm lẫn dữ liệu thô cào về.
*   **Nhầm lẫn giá trị custom và raw:** Thiết lập mặc định `rong_hem` lấy trực tiếp từ `row[60]` thô đã điền sẵn giá trị custom không mong muốn thay vì để trống mặc định.

### 2. Bài học kinh nghiệm (Good Practices)
*   **Đồng bộ hóa cấu trúc parse JSON:** Luôn đảm bảo parse đầy đủ cấu trúc `JSON_UI` cho mọi trường hợp đối tượng (cả căn đã lên sóng và căn thô từ Pool).
*   **Tách biệt tuyệt đối biến custom:** Các trường custom chỉnh sửa bởi admin (như custom area, custom alley width) không được tự ý fallback sang trường thô để tránh làm nhiễm bẩn dữ liệu khi lưu trữ.
*   **Thống nhất chỉ mục cột:** Thiết lập một sơ đồ ánh xạ chỉ mục cột tập trung hoặc kiểm tra thực tế bằng các script bổ trợ (`inspect_sheets.py`) trước khi thay đổi code.
