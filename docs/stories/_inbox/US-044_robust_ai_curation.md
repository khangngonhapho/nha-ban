---
id: US-044
status: accepted
date: 2026-05-29
size: S
---

# US-044: Robustness Upgrades for AI Curation and Frontend Triggering (Khắc phục triệt để lỗi biên tập AI trống trường và tối ưu luồng gọi)

## User story
**As a** Broker / Curator Khang Ngô  
**I want** tính năng Biên tập AI tự động sửa lỗi điền trống trường và sửa lỗi trùng lặp cuộc gọi, hoạt động trơn tru ngay cả khi cấu hình prompt rỗng hoặc các trường cơ sở dữ liệu có giá trị NULL  
**So that** việc biên tập tự động Tiêu đề, Mô tả và tra Phường cũ luôn hoạt động ổn định và chính xác, tiết kiệm chi phí gọi API OpenAI và tăng trải nghiệm người dùng tối đa (Value Management Plan KPI 1).

---

## Acceptance
- [x] **Fallback cấu hình rỗng (Empty Config Fallback):**
  - Nâng cấp hàm `load_config()` trong `curator_server.py`.
  - Nếu gặp trường chuỗi rỗng trong `curator_config.json` (đặc biệt là `openai_system_prompt`), tự động khôi phục về giá trị mặc định từ `DEFAULT_CONFIG` thay vì đè chuỗi rỗng làm mất system prompt khiến OpenAI sinh sai cấu trúc JSON.
- [x] **Tránh lỗi crash `NoneType` khi xử lý dữ liệu thô (NoneType Error Immunity):**
  - Triển khai hàm trợ giúp `safe_str()` để xử lý các giá trị `None` (NULL) từ SQLite.
  - Áp dụng `safe_str()` cho tất cả các trường dữ liệu thô có khả năng chứa `None` như `Phan_loai_Hem`, `Ngo_So_nha`, `Duong_truoc_nha_m`, `soNha`, `duongTruocNha`, `phanLoaiHem` v.v. trước khi gọi `.strip()` hoặc `.lower()`, đảm bảo luồng xử lý AI không bao giờ bị crash giữa chừng.
- [x] **Loại bỏ trùng lặp cuộc gọi AI (Call Deduplication):**
  - Loại bỏ mã tự động gọi AI bị thừa trong hàm `selectListing()` trên frontend `curator.html`.
  - Giữ lại duy nhất bộ đếm thời gian Debounce an toàn (`window.autoAiTimeoutId`) trong `renderEditor()` để đảm bảo mỗi khi click chọn căn nhà chưa biên tập, hệ thống chỉ kích hoạt đúng 1 cuộc gọi API OpenAI.
- [x] **Tái biên dịch thành công (Executable Rebuild):**
  - Tắt các tiến trình `KhangNgoCuratorApp.exe` cũ đang chạy ngầm để giải phóng khóa tệp tin của Windows.
  - Biên dịch thành công file EXE duy nhất `dist\KhangNgoCuratorApp.exe` chạy trơn tru không lỗi.

---

## Solution
Nâng cấp toàn diện cơ chế xử lý dữ liệu đầu vào và luồng đồng bộ:
1. **Tránh chuỗi rỗng ghi đè:** Cập nhật `load_config()` rà soát thông tin từ file JSON người dùng cấu hình, lọc bỏ các trường rỗng và khôi phục từ mặc định gốc.
2. **Kháng lỗi NoneType:** Tích hợp helper `safe_str(val)` chuyển đổi linh hoạt đối tượng `None` thành chuỗi rỗng `""` trước khi gọi các hàm xử lý chuỗi.
3. **Frontend Debounce độc nhất:** Xóa khối logic gọi AI dư thừa trong `selectListing()`, thống nhất quản lý luồng auto-AI tại hàm `renderEditor()`.

---

## 📋 Implementation Plan
1. **Helper Integration:** Thêm `safe_str(val)` ở phần đầu `curator_server.py`.
2. **Robust Refactoring:** Thay thế các điểm gọi `.strip()` thô thành `safe_str()`.
3. **Frontend Curation Cleanup:** Xóa logic gọi AI dư thừa ở `selectListing` trong `curator.html`.
4. **Recompile:** Thực hiện chạy `taskkill` và `build_exe_single.bat`.

---

## 📝 Task Checklist (TODO)
- [x] Thêm helper `safe_str()` vào đầu `curator_server.py`.
- [x] Cập nhật `load_config()` xử lý fallback thông minh.
- [x] Thay thế các trường dễ dính `None` bằng `safe_str()` trong `generate_fallback_content_python()`, `generate_ai_curation_for_listing_backend()` và endpoint `/api/ai/generate`.
- [x] Gỡ bỏ trigger tự động gọi AI thừa trong `selectListing()` ở `curator.html`.
- [x] Chạy script kiểm thử `scratch/test_ai_curation.py` xác minh kết quả.
- [x] Giải phóng tiến trình và biên dịch thành công file EXE duy nhất.

---

## 🛠️ Update Logic (Drafting while Doing)
- **Tối ưu hóa khả năng chống lỗi NoneType (NoneType Immunity):**
  - Tích hợp hàm trợ giúp `safe_str(val)` trong `curator_server.py` để chuyển đổi an toàn đối tượng `None` thành chuỗi rỗng `""`.
  - Thay thế toàn bộ các điểm gọi `.strip()` và `.lower()` trực tiếp trên dữ liệu thô từ SQLite (như `Phan_loai_Hem`, `Ngo_So_nha`, `soNha`) bằng `safe_str()` để ngăn ngừa lỗi crash server ngắt quãng luồng xử lý AI.
- **Xử lý cơ chế Empty Config Fallback:**
  - Nâng cấp hàm `load_config()` trong `curator_server.py` để phát hiện các giá trị chuỗi rỗng trong tệp cấu hình `curator_config.json`.
  - Khôi phục các trường rỗng về giá trị mặc định trong `DEFAULT_CONFIG` (đặc biệt là `openai_system_prompt`), tránh tình trạng mất prompt hệ thống làm hỏng cấu trúc JSON đầu ra của OpenAI.
- **Loại bỏ trùng lặp cuộc gọi AI ở Frontend:**
  - Gỡ bỏ khối logic kích hoạt gọi AI thừa tại hàm `selectListing()` trong `curator.html`.
  - Giữ lại duy nhất cơ chế Debounce an toàn (`autoAiTimeoutId`) tại `renderEditor()` để đảm bảo mỗi căn nhà chọn biên tập chỉ phát sinh chính xác 1 yêu cầu gọi API OpenAI.
- **Kiểm thử & Đóng gói:**
  - Chạy thử nghiệm thành công tệp kịch bản kiểm thử `scratch/test_ai_curation.py` trên các bản ghi có dữ liệu NULL.
  - Sử dụng lệnh biên dịch đóng gói để tạo thành công tệp thực thi duy nhất `dist\KhangNgoCuratorApp.exe`.


---

## Verification Plan
### Kiểm thử tự động & Thủ công:
1. Chạy `python scratch/test_ai_curation.py` trên bản ghi chứa `Phan_loai_Hem: None` -> Hệ thống chạy trơn tru và trả về kết quả JSON chuẩn xác từ OpenAI (Green Pass).
2. Kiểm tra log gọi AI trên Frontend -> Chỉ ghi nhận đúng 1 cuộc gọi API duy nhất cho mỗi lần tải căn nhà (Green Pass).
3. Đóng gói EXE thành công 100% không dính lỗi Permission (Green Pass).

---

## Files touched
* [curator_server.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator_server.py)
* [curator.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator.html)

---

## 🔄 Change Requests (Yêu cầu Thay đổi)
- **CR-001 (Phát hiện bởi PO Trang & Mr. Khang): Lỗi "Báo AI biên tập thành công nhưng trường bị trống"**
  - **Mô tả:** Người dùng thực hiện biên tập AI, hệ thống báo thành công nhưng kết quả trên giao diện bị trống hoặc rỗng.
  - **Nguyên nhân:**
    1. Cấu hình rỗng `openai_system_prompt` trong `curator_config.json` đè mất system prompt gốc khiến OpenAI sinh sai cấu trúc JSON mong đợi.
    2. Các cuộc gọi AI trùng lặp đồng thời (race condition) từ frontend xóa mờ dữ liệu lẫn nhau.
    3. Trả về rỗng khi gặp giá trị `None` (NULL) trong cơ sở dữ liệu khi nối chuỗi.
  - **Giải pháp khắc phục (Đã hoàn thành):**
    1. Tích hợp Helper `safe_str()` ngăn chặn triệt để lỗi crash `NoneType` khi xử lý chuỗi SQLite.
    2. Tự động phục hồi cấu hình prompt mặc định (`DEFAULT_CONFIG`) nếu cấu hình của người dùng chứa chuỗi rỗng.
    3. Thống nhất cơ chế Debounce độc nhất (`window.autoAiTimeoutId`) tại `renderEditor()`, loại bỏ trigger thừa ở `selectListing()` để loại bỏ trùng lặp cuộc gọi AI.

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)
> [!TIP]
> **Mục đích:** Ghi nhận lại các sự cố thực tế xảy ra khi phát triển để họp rút kinh nghiệm (Retro), đồng thời đúc kết các bài học tốt (Good Practices) nhằm ngăn ngừa tuyệt đối các lỗi tương tự ở các US tiếp theo.

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** Xảy ra lỗi crash server `AttributeError: 'NoneType' object has no attribute 'strip'` khi người dùng biên tập một căn nhà mà các cột phụ trong SQLite trả về giá trị NULL (None).
- **Nguyên nhân gốc rễ (Root Cause):** Do AI hoặc lập trình viên gọi trực tiếp các phương thức xử lý chuỗi (`.strip()`, `.lower()`) trên giá trị thô từ SQLite mà không kiểm tra Null trước.
- **Giải pháp phòng ngừa:** Xây dựng helper `safe_str(val)` để chuyển đổi an toàn đối tượng `None` thành chuỗi rỗng `""` và bắt buộc bọc tất cả các trường SQLite không bắt buộc trước khi xử lý.

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm code & Cấu hình:** 
  1. **Kháng Null:** Coi mọi cột dữ liệu lấy ra từ CSDL đều có nguy cơ chứa Null và bọc an toàn.
  2. **Cấu hình Fallback:** Hàm tải cấu hình JSON phải có cơ chế phục hồi mặc định thông minh nếu người dùng cấu hình giá trị rỗng `""` làm mất system prompt.
- **Kinh nghiệm kiểm thử:** Tạo script kiểm thử độc lập (`test_ai_curation.py`) chạy giả lập trên các bản ghi SQLite chứa giá trị NULL để phát hiện lỗi crash trước khi biên dịch EXE.
