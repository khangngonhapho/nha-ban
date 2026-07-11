---
id: US-094A1
status: accepted
date: 2026-06-15
size: S
---

# US-094A1: Tách biệt CSS ngoài ra global.css

## User story
**As a** Developer  
**I want** di chuyển toàn bộ 3,650 dòng CSS trong index.html ra tệp global.css độc lập  
**So that** mã nguồn HTML sạch sẽ, giảm nguy cơ xung đột layout và cho phép CDN cache CSS tĩnh nhằm tăng tốc độ tải trang cho cả Khách hàng và Admin.

## Acceptance
- [x] Tạo tệp `static/css/global.css` chứa toàn bộ nội dung CSS từ thẻ `<style>` của index.html.
- [x] Tệp `index.html` liên kết thành công với `static/css/global.css` qua thẻ `<link>` và xóa bỏ hoàn toàn thẻ `<style>` thô.
- [x] Đảm bảo không xảy ra bất kỳ thay đổi hay lỗi vỡ giao diện (UI/Layout) nào trên cả 2 phiên bản Desktop và Mobile sau khi tách.

## Solution
- **Cách thực hiện:**
  - Tạo thư mục `static/css/` nếu chưa tồn tại.
  - Cắt toàn bộ nội dung CSS từ dòng 21 đến 3670 trong tệp `index.html` và lưu vào `static/css/global.css`.
  - Chèn thẻ `<link rel="stylesheet" href="static/css/global.css">` vào vị trí của block `<style>` cũ trong phần `<head>` của `index.html`.
- **Key logic:**
  - Đảm bảo giữ nguyên thứ tự khai báo CSS để tính năng Cascading và Specifity hoạt động chính xác (đặc biệt là các khối `@media` queries ở cuối file).

## 📋 Implementation Plan
- **Cách tiếp cận:** Tách biệt cơ học tệp stylesheet để làm sạch mã nguồn HTML mà không can thiệp vào bất kỳ logic JavaScript nào.
- **Các bước triển khai:**
  1. Tạo thư mục `static/css` và tệp `global.css`.
  2. Di chuyển nội dung CSS và cập nhật liên kết trong `index.html`.
  3. Xây dựng và chạy bộ kiểm thử E2E Playwright đa thiết bị để xác thực hiển thị.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Định vị vùng thẻ CSS trong `index.html` (dòng 21-3670)
  - [x] Chốt phương án tạo thư mục `/static/css/`
- [x] **Triển khai Code:**
  - [x] Tạo tệp `static/css/global.css` và copy nội dung CSS
  - [x] Cập nhật `index.html` liên kết tới `global.css` và xóa thẻ `<style>`
- [x] **Kiểm thử & Bàn giao:**
  - [x] Tạo tệp test E2E Playwright `scratch/test_e2e_curator.py`
  - [x] Chạy kiểm thử E2E local trên cả Desktop và Mobile viewport đạt 100% PASS
  - [x] Merge code vào `main` và push deploy Live lên Production
  - [x] Báo cáo PO kiểm thử trực tiếp trên Live

## 🛠️ Update Logic (Drafting while Doing)

### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:**
  - **Sự cố:** Khi deploy lên Vercel, giao diện bị vỡ hoàn toàn do Vercel chuyển hướng request tĩnh `/static/css/global.css` vào function `api/index.js` (theo luật wildcard), trả về mã HTML của `index.html` thay vì mã CSS.
  - **Khắc phục:** 
    1. Reset cứng git local về commit trước merge (`2092e45`) và force-push khôi phục ngay trạng thái sản xuất.
    2. Cấu hình `"includeFiles": ["index.html", "static/**"]` trong `vercel.json`.
    3. Thêm middleware phục vụ file tĩnh thủ công có mimes (`text/css`, v.v.) và tiêu đề cache mạnh (`Cache-Control: public, max-age=31536000, immutable`) vào `api/index.js`.
    4. Deploy lại và kiểm thử thành công.

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- **Script kiểm thử:** `python scratch/test_e2e_curator.py` chạy Playwright Desktop/Mobile đạt 100% PASS.

## 🧠 Retro, Lessons Learned & Good Practices
- **Bài học kinh nghiệm:**
  - local test standard `http.server` không thể giả lập chính xác cơ chế định tuyến wildcard của Vercel Serverless. Cần đặc biệt cẩn thận khi chuyển các tài nguyên tĩnh ra file độc lập trên môi trường Serverless.
  - Luôn chuẩn bị sẵn mã commit trước đó để rollback tức thời khi phát sinh sự cố live.
  - Tích hợp `Cache-Control` dài hạn cho tài nguyên tĩnh giúp CDN Vercel cache triệt để, tăng tốc độ tải trang đáng kể đúng theo mục tiêu câu chuyện.

## Verification Plan

### Automated Tests (BẮT BUỘC - Desktop & Mobile)
- **Script kiểm thử chính:** [test_e2e_curator.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_e2e_curator.py)
- **Lệnh chạy test:** `pytest scratch/test_e2e_curator.py` hoặc chạy trực tiếp bằng python.
- **Kịch bản test:**
  1. Load trang chủ `index.html` trên **Desktop (viewport: 1280x800)**: Xác thực HTTP 200, kiểm tra xem logo/badge hiển thị đúng vị trí.
  2. Load trang chủ `index.html` trên **Mobile (viewport di động cảm ứng: 375x812, hasTouch=True)**: Xác thực không bị lỗi vỡ layout hoặc hiển thị sai lệch.

### Manual Verification
- Mở trang chủ local và Live sau khi deploy, kiểm tra responsive bằng chế độ Responsive Design Mode của Chrome.

## Files touched
- `docs/stories/_inbox/US-094A1_lego_frontend_css.md`
- `static/css/global.css`
- `index.html`
- `scratch/test_e2e_curator.py`
