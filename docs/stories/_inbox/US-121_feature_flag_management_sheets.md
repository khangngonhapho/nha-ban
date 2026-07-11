---
id: US-121
status: done
date: 2026-07-09
size: M
---

# US-121: Quản lý và Đồng bộ Feature Flags trên Google Sheets

## User story
**As a** PO / Admin
**I want** có một cơ chế quản lý Feature Flags tập trung trên Google Sheets Pool và tự động đồng bộ hóa trạng thái cờ từ mã nguồn lên Sheet
**So that** tôi có thể dễ dàng theo dõi các flag hiện có, biết loại flag (Release/Ops), trạng thái dọn dẹp, và thực hiện bật/tắt hoặc dọn dẹp nhanh chóng mà không làm nghẽn tiến độ.

## Acceptance
- [ ] Tạo bảng `Feature_Flags` trên tệp Google Sheets Pool (tự động phân giải theo cấu hình `active_pool_system` của `settings.json`).
- [ ] Bảng gồm các cột: `Tên Flag` | `Loại Flag` | `Giá Trị Hiện Tại` | `Trạng Thái` | `Ngày Release` | `Ngày Cập Nhật` | `Mô tả`.
- [ ] Viết script `scratch/sync_flags.py` để tự động hóa việc đồng bộ danh sách flag từ `settings.json` lên Google Sheets.
- [ ] Khi một flag bị xóa khỏi code (`settings.json`), trạng thái trên Sheet của flag đó chuyển sang `cleaned` chứ không bị xóa dòng hoàn toàn để lưu vết lịch sử.
- [ ] Cập nhật hướng dẫn prompt dọn dẹp flag vào `AGENTS.md`.

## Solution

> [!note]- Configuration
> Biến cấu hình chính nằm trong `settings.json`:
> ```json
> "feature_flags": {
>     "maintenance_mode": false,
>     "enable_new_search_engine": false
> }
> ```

> [!note]- Input
> Đầu vào là đối tượng `"feature_flags"` trong `settings.json`.

> [!note]- Output / Format
> Cấu trúc dòng ghi nhận trên Google Sheets tab `Feature_Flags`:
> - Tên Flag: chuỗi (ví dụ: `enable_new_search_engine`)
> - Loại Flag: `Release Flags` | `Ops Flags` (mặc định `maintenance_mode` là `Ops Flags`, các flag khác là `Release Flags`)
> - Giá Trị Hiện Tại: `TRUE` | `FALSE` (đồng bộ tương ứng giá trị boolean)
> - Trạng Thái: `active` | `cleaned`
> - Ngày Release: Ngày phát hiện flag lần đầu tiên (`YYYY-MM-DD`)
> - Ngày Cập Nhật: Ngày thay đổi giá trị hoặc trạng thái gần nhất
> - Mô tả: mô tả ngắn gọn công năng của flag

## 📋 Implementation Plan
- **Cách tiếp cận:**
  - Định nghĩa cờ tính năng baseline trong `settings.json`.
  - Tạo script Python `scratch/sync_flags.py` sử dụng `gspread` kết nối qua credentials có sẵn từ `manager.get_google_credentials()`.
  - Script sẽ kiểm tra xem tab `Feature_Flags` tồn tại chưa, nếu chưa sẽ tạo mới và set up định dạng header đậm.
  - Quét toàn bộ flag trong `settings.json`. Tải dữ liệu flag hiện tại từ sheet:
    - Nếu flag mới ➔ append dòng mới với trạng thái `active` và Ngày Release là ngày hôm nay.
    - Nếu flag thay đổi giá trị ➔ cập nhật `Giá Trị Hiện Tại` và cập nhật `Ngày Cập Nhật`.
    - Nếu flag trên sheet ở trạng thái `active` nhưng không còn trong `settings.json` ➔ đổi trạng thái thành `cleaned` và cập nhật `Ngày Cập Nhật`.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát code kết nối gspread hiện có
  - [x] Chốt giải pháp cấu hình flag dạng JSON
- [x] **Triển khai Code:**
  - [x] Thêm baseline `"feature_flags"` vào `settings.json`
  - [x] Viết script `scratch/sync_flags.py`
  - [x] Thêm tài liệu hướng dẫn dọn dẹp flag vào `.agents/AGENTS.md`
- [x] **Kiểm thử sơ bộ:**
  - [x] Viết bộ unit test `tests/test_feature_flags.py`
  - [x] Chạy thử nghiệm và xác nhận tab được tạo trên Google Sheets
  - [x] Xác minh trạng thái `cleaned` khi xóa flag trong cấu hình

## 🛠️ Update Logic (Drafting while Doing)
### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:**
  - Đọc `DeprecationWarning` do `worksheet.update` của thư viện gspread phiên bản mới. Đã khắc phục bằng cách chuyển đổi tham số sang dạng named arguments (`update(values=rows_to_write, range_name="A1")`).
  - Lỗi assert mock trong unit test do named arguments làm trống positional args. Đã chuyển đổi lấy giá trị kiểm tra từ `call_args[1].get("values")`.
- **Phát kiến ngoài kế hoạch:** Cơ chế sắp xếp của script tự động dồn các flag `active` lên đầu bảng để tiện quản lý và đẩy các flag cũ `cleaned` xuống cuối bảng.

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- Chạy đồng bộ thực tế trên Google Sheets bằng tài khoản `khangngonhapho`:
  ```
  python scratch/sync_flags.py
  ```
  Kết quả: Tab `Feature_Flags` được tạo tự động, 2 cờ baseline được nạp lên thành công ở trạng thái `active`.

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)
- **Kinh nghiệm code & Cấu hình:** Khi viết code gọi thư viện ngoài (như gspread), nên dùng named arguments để tăng tính tương thích ngược và tránh lỗi Deprecation Warning trên các phiên bản thư viện mới.
- **Kinh nghiệm kiểm thử:** Nên test cả các trường hợp biên như file worksheet bị xóa hoặc get_all_records bị lỗi format rỗng để script không crash.

## Verification Plan

### Automated Tests
- `pytest tests/test_feature_flags.py`

### Manual Verification
- Chạy `python scratch/sync_flags.py` và kiểm tra tab `Feature_Flags` trên trình duyệt Google Sheets.

## Files touched
- `settings.json` — Cấu hình cờ tính năng baseline
- `scratch/sync_flags.py` — Script đồng bộ flag lên Google Sheets
- `.agents/AGENTS.md` — Bổ sung hướng dẫn prompt dọn dẹp flag
- `tests/test_feature_flags.py` — Bộ kiểm thử tự động

