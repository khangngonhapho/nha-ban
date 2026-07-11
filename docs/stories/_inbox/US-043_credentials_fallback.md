---
id: US-043
status: done
date: 2026-05-29
size: S
---

# US-043: credentials.json Location Fallback Resolution for Google Sheet Publishing (Tự động tìm kiếm credentials.json tại nhiều cấp thư mục)

## User story
**As a** Product Owner / Broker Khang Ngô  
**I want** ứng dụng Curator (chạy dưới dạng file thực thi `.exe` độc lập) tự động tìm kiếm tệp xác thực `credentials.json` tại nhiều vị trí thư mục (bao gồm cả thư mục gốc của dự án và các thư mục cha của file chạy) giống như cơ chế đang áp dụng cho `raw_archive.db`  
**So that** việc xuất bản trực tiếp lên Google Sheets Pool luôn hoạt động trơn tru sau khi biên tập tin bài, loại bỏ lỗi báo thiếu `credentials.json` dù tệp tin này đã có sẵn ở thư mục gốc của dự án, đóng góp trực tiếp vào mục tiêu tối ưu hóa tốc độ biên tập của rổ hàng (Value Management Plan KPI 1).

---

## Acceptance
- [x] **Tìm kiếm credentials.json đa cấp (Multi-level Fallback Lookup):**
  - Tích hợp logic tìm kiếm động cho `CREDENTIALS_FILE` trong `curator_server.py`.
  - Nếu ứng dụng chạy dưới dạng đóng gói (`sys.frozen`), kiểm tra file tại:
    1. Thư mục chứa file chạy `.exe` (`exe_dir`).
    2. Thư mục cha của `exe_dir` (1 cấp cha).
    3. Thư mục ông nội của `exe_dir` (2 cấp cha).
    4. Thư mục làm việc hiện tại (`os.getcwd()`).
  - Nếu chạy script Python thông thường, ưu tiên thư mục chứa file `curator_server.py`.
- [x] **Ghi nhật ký (Logging) đường dẫn tường minh:**
  - Nếu tìm thấy file xác thực, in đường dẫn tuyệt đối của tệp xác thực được áp dụng lên nhật ký log: `[🔒 API] Đã tìm thấy tệp xác thực Google Sheets tại: [đường dẫn tuyệt đối]`.
  - Nếu không tìm thấy, log cảnh báo rõ ràng tất cả các đường dẫn hệ thống đã kiểm tra để Broker dễ dàng tự kiểm tra và đặt file đúng chỗ: `[⚠️ CẢNH BÁO] Không tìm thấy credentials.json. Các đường dẫn đã quét qua: [...]`.

---

## Solution
Nâng cấp hàm `get_google_credentials()` trong [curator_server.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator_server.py) để tự động hóa việc rà soát file `credentials.json` thông qua một mảng chứa các đường dẫn tuyệt đối ưu tiên:
1. `CREDENTIALS_FILE` (dựa trên `PROJECT_ROOT` tính toán).
2. Đường dẫn lùi 1 cấp cha từ `PROJECT_ROOT`.
3. Đường dẫn lùi 2 cấp cha từ `PROJECT_ROOT`.
4. Thư mục chạy ứng dụng hiện tại `os.getcwd()`.
5. Đường dẫn lùi 1 cấp từ `os.getcwd()`.
6. (Nếu là EXE frozen) Thư mục chứa file thực thi `.exe` và các cấp cha của nó.

Nếu tìm thấy, hệ thống sử dụng tệp đầu tiên tìm thấy và ghi log xác nhận cụ thể; nếu không, in toàn bộ các đường dẫn đã kiểm tra ra log để hỗ trợ chẩn đoán.

---

## 📋 Implementation Plan
1. **Quét và định vị:** Thiết lập mảng `target_paths` động, bao gồm kiểm tra flag `getattr(sys, 'frozen', False)`.
2. **Kiểm tra sự tồn tại (Scan Loop):** Chạy vòng lặp kiểm tra `os.path.exists` để tìm tệp tin hợp lệ đầu tiên.
3. **Log & Load:** Nếu tìm thấy, thực hiện tải file qua `service_account.Credentials.from_service_account_file` và ghi log an toàn. Nếu không, in toàn bộ các vị trí đã kiểm tra để Broker dễ khắc phục.

---

## 📝 Task Checklist (TODO)
- [x] Thiết lập mảng `target_paths` linh hoạt trong hàm `get_google_credentials()`.
- [x] Thêm kiểm tra flag `sys.frozen` để chèn các thư mục chứa file thực thi `.exe`.
- [x] Viết logic kiểm tra tồn tại và chọn ra file xác thực đầu tiên.
- [x] Tích hợp ghi nhận nhật ký tường minh (đường dẫn tuyệt đối) khi phát hiện hoặc không phát hiện tệp xác thực.
- [x] Chạy thử cục bộ và xác thực tính ổn định.

---

## 🛠️ Update Logic (Drafting while Doing)
* Đã nâng cấp thành công hàm `get_google_credentials()` trong [curator_server.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator_server.py).
* Tiến trình in nhật ký tuyệt đẹp ra terminal và UI log.

---

## Verification Plan
### Kiểm thử thủ công:
1. Chạy `python curator_server.py`.
2. Quan sát log trên terminal: Hệ thống in chính xác đường dẫn tìm thấy `credentials.json` tại `d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\credentials.json` (Green Pass).
3. Bấm thử nút **"XUẤT BẢN LÊN SHEETS"** trên giao diện biên tập viên Curator. Quá trình lưu và đồng bộ thành công 100% không còn báo thiếu file (Green Pass).

---

## Files touched
* [curator_server.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator_server.py)

---

## 🔄 Change Requests (Yêu cầu Thay đổi)
*(Không có)*
