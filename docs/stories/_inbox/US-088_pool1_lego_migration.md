---
id: US-088
status: accepted
date: 2026-06-11
size: L
---

# US-088: Đổi tên file và di cư tính năng cũ (Pool1) sang Lego

## User story
**As an** Admin  
**I want** phân rã và tách biệt toàn bộ mã nguồn xử lý thô và đồng bộ Google Sheets của hệ thống cũ (Pool1) ra thành một khối Lego riêng biệt tên là `pool_lego.py` và đổi tên các file cốt lõi sang tiếng Anh thân thiện dễ hiểu  
**So that** hệ thống hoạt động ổn định, không bị lỗi hồi quy (regression) và sẵn sàng tích hợp các khối Lego Pool tiếp theo trong tương lai một cách an toàn.

## Acceptance Criteria
- [x] Thực hiện đổi tên các file cốt lõi sang tiếng Anh đơn giản (non-tech friendly) và cập nhật toàn bộ các tham chiếu liên quan trong mã nguồn, batch files, spec builders và scripts:
  - `curator_config.json` $\rightarrow$ `settings.json` (Tệp thiết lập)
  - `crawl_pipeline.py` $\rightarrow$ `fetcher.py` (Tệp lấy tin)
  - `curator_server.py` $\rightarrow$ `manager.py` (Tệp điều hành biên tập & đồng bộ)
- [x] Tạo tệp Lego điều phối trung tâm mới: `pool_lego.py`.
- [x] Phân rã và di chuyển toàn bộ logic nghiệp vụ của hệ thống cũ (`Pool1`) sang `pool_lego.py`:
  - Di chuyển danh sách `POOL_HEADERS` và logic tạo bảng `listings` thô của Pool1.
  - Di chuyển bộ phân tích, ánh xạ và lưu SQLite dữ liệu thô cũ từ `fetcher.py` sang hàm `pool_lego.save_raw_to_sqlite()`.
  - Di chuyển logic đồng bộ dữ liệu và lưu ảnh dạng cột thô sang Google Sheets từ `manager.py` sang hàm `pool_lego.publish_listing()`.
- [x] Tích hợp cấu hình `"active_pool_system"` trong `settings.json` (mặc định là `"Pool1"` ở giai đoạn này) và kết nối nó vào khớp nối điều phối của `pool_lego.py`.
- [x] Chạy thử cào dữ liệu và xuất bản (Publish) trong chế độ Pool1:
  - Xác nhận dữ liệu vẫn ghi chính xác vào file SQLite thô cũ `raw_archive.db`.
  - Xác nhận dữ liệu và hình ảnh xuất bản thành công sang tab `Pool` cũ của Google Sheets đúng cột chỉ mục mà không gặp bất kỳ lỗi nào.

## Solution
Xem chi tiết sơ đồ kiến trúc Lego mới tại [docs/system_architecture_deployment.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/system_architecture_deployment.md).

### Files to Modify
- `curator_config.json` $\rightarrow$ Đổi tên thành `settings.json`
- `crawl_pipeline.py` $\rightarrow$ Đổi tên và làm sạch thành `fetcher.py`
- `curator_server.py` $\rightarrow$ Đổi tên và làm sạch thành `manager.py`
- `CHAY_APP.bat` $\rightarrow$ Cập nhật tham chiếu
- `build_exe.bat` $\rightarrow$ Cập nhật tham chiếu
- PyInstaller spec files (`KhangNgoCurator.spec`, `KhangNgoCuratorApp.spec`, `KhangNgoCurator_v2.spec`, `KhangNgoCurator_v3.spec`) $\rightarrow$ Cập nhật tham chiếu
- Scripts (`upload_curator_zip.py`, `fix_tilted_images.py`, `restore_db_from_sheets.py`) $\rightarrow$ Cập nhật tham chiếu

## Verification Plan

### Automated Tests
- Chạy kiểm tra cú pháp của toàn bộ file python mới: `python -m py_compile fetcher.py manager.py pool_lego.py` để đảm bảo không có lỗi cú pháp.

### Manual Verification
1. Chạy `CHAY_APP.bat` và xác nhận Flask server khởi động bình thường trên tệp `manager.py` mới.
2. Thực hiện cào thử một vài căn bằng lệnh cào trên web hoặc trực tiếp bằng `fetcher.py`. Xác nhận dữ liệu thô được ghi đúng vào database `raw_archive.db` cũ qua khớp nối `pool_lego.py`.
3. Biên tập curation và bấm **Xuất bản (Publish)**. Xác nhận dữ liệu và 25 ảnh nội thất, 10 ảnh hẻm được đẩy lên tab `"Pool"` cũ trên Google Sheet đúng cột, không bị lệch chỉ số.
