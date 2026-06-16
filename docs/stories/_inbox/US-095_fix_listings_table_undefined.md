---
id: US-095
status: accepted
date: 2026-06-16
size: S
replaces: none
---

# US-095: Khắc phục lỗi name 'listings_table' is not defined khi tự động hóa Curation & Xuất bản ở chế độ Pool1

## User story
**As an** Admin  
**I want** biến `listings_table` được định nghĩa chính xác trong hàm `publish_listing` của `pool_lego.py` cho cả hai phân hệ Pool1 và Pool2  
**So that** quy trình tự động hóa Curation và đẩy dữ liệu lên Google Sheets ở chế độ Pool1 hoạt động trơn tru, không gặp lỗi `NameError`.

## Acceptance Criteria
- [x] Khắc phục lỗi NameError: `name 'listings_table' is not defined` khi thực hiện `publish_listing()` trong chế độ Pool1.
- [x] Khai báo biến `listings_table` tương thích động dựa trên phân hệ pool đang hoạt động:
  - `listings_v2` nếu `is_pool2` là `True`.
  - `listings` nếu `is_pool2` là `False` (chế độ Pool1).
- [x] Bảo đảm toàn bộ các thao tác SQLite liên quan đến bảng listings trong `publish_listing()` (truy vấn thông tin căn, đếm trùng Mã Hàng, cập nhật Mã Khang Ngô, cập nhật System ID, cập nhật trạng thái `published` và mốc `Last_Sync`) ở chế độ Pool1 chạy bình thường trên bảng `listings`.

## Solution

### 1. Phân tích nguyên nhân
Trong hàm `publish_listing()` của `pool_lego.py`, khi hệ thống hoạt động ở chế độ Pool1 (`is_pool2` là `False`), khối xử lý SQLite local (từ dòng 1204 trở đi) thực hiện các câu lệnh SQL sử dụng chuỗi định dạng (f-string) có chứa biến `{listings_table}`, ví dụ:
- `row = cursor.execute(f"SELECT * FROM {listings_table} WHERE tk_id = ?", (tk_id,)).fetchone()` (Dòng 1249)
- `f"SELECT COUNT(DISTINCT tk_id) FROM {listings_table} WHERE Ma_Hang = ?"` (Dòng 1325)
- `cursor_db.execute(f"UPDATE {listings_table} SET ...")` (Dòng 1452 & 1468)
- `f"UPDATE {listings_table} SET status = 'published' ..."` (Dòng 1512)

Tuy nhiên, biến `listings_table` chưa từng được định nghĩa hay gán giá trị ở bất cứ đâu trong phạm vi hàm `publish_listing()`, dẫn tới lỗi thông báo: `name 'listings_table' is not defined`.

### 2. Thiết kế giải pháp
Thêm dòng khai báo biến `listings_table` tại đầu hàm `publish_listing()` ngay sau khi thiết lập kết nối SQLite local:
```python
    listings_table = "listings_v2" if is_pool2 else "listings"
```

---

## 📋 Proposed Changes

### 1. Cập nhật mã nguồn `pool_lego.py`
#### [MODIFY] [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py)
* Định nghĩa biến `listings_table` ngay sau khi mở kết nối sqlite3 trong hàm `publish_listing()`.

---

## 🔍 Verification Plan

### Automated Tests
* Thực hiện biên dịch thử tệp nguồn:
  ```powershell
  python -m py_compile pool_lego.py
  ```

### Manual Verification
* Thực hiện chạy thử logic xuất bản bằng script kiểm thử cục bộ hoặc chạy thử tự động hóa cào/biên tập 1 căn ở chế độ Pool1 và kiểm tra nhật ký log xem có còn lỗi `listings_table` không.

---

## 🧠 Retro, Lessons Learned & Good Practices

### 🚨 Sự cố phát sinh (Incidents) & Nguyên nhân gốc rễ
1. **Sự cố:** Lỗi `NameError: name 'listings_table' is not defined` sập luồng tự động hóa Curation & Xuất bản cho căn lẻ khi chạy ở chế độ Pool1.
2. **Nguyên nhân gốc rễ:** Khi tách biệt logic cũ sang khối Lego `pool_lego.py` (US-088), hàm `publish_listing` sử dụng biến `listings_table` trong các câu lệnh SQLite f-string nhưng không hề khai báo hay gán giá trị cho biến này ở bất cứ đâu trong hàm. Phía Pool2 không bị ảnh hưởng vì có lệnh `return publish_listing_pool2` ngắt luồng ở trên.

### 💡 Bài học kinh nghiệm & Thực tiễn Tốt (Lessons Learned & Good Practices)
1. **Kiểm tra phủ cả hai phân hệ khi cấu hình động:** 
   - Khi viết mã nguồn điều phối động qua config (như `settings.json` chọn active_pool_system), luôn cần chạy thử nghiệm quy trình E2E/Unit test cho **cả hai nhánh logic** (Pool1 và Pool2) để đảm bảo không bị sót lỗi biến thiếu định nghĩa ở nhánh không hoạt động mặc định.
2. **Kế thừa các hàm xác định tên bảng:**
   - Để đồng bộ hóa và giảm thiểu khai báo cứng, nên tái sử dụng các hàm xác định bảng như `get_listings_table_name()` để tránh khai báo cục bộ lặp lại ở nhiều file.

