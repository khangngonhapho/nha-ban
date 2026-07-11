---
id: US-098
status: backlog
date: 2026-06-18
size: M
---

# US-098: Kiểm tra Tính Đầy đủ và Khớp Dữ liệu Curation & Crawler (Pool2)

## User story
**As an** Admin Curation (Người biên tập rổ hàng)  
**I want** Thông tin cào thô (đặc biệt là tên Đường, Tiêu đề bài đăng gốc) và các tiêu chí Criteria được hiển thị đầy đủ và trực quan trên giao diện Admin; đồng thời giá Public mặc định bằng giá Chào và phân định rõ 8 ô tiêu chí có thể chỉnh sửa tự do (nằm ở Curation Form bên dưới) và 11 ô tiêu chí hiển thị chỉ đọc (nằm ở khu vực THÔNG TIN THÔ - POOL ở trên cùng UI)  
**So that** Rổ hàng sau khi biên tập đảm bảo tính đầy đủ, chính xác 100% về thông tin vị trí và pháp lý, không bị lọt dữ liệu thô và sẵn sàng xuất bản.

## Acceptance Criteria
- [ ] **1. Lưu trữ Tiêu đề thô (`Title`):** CSDL `listings_v2` và `listings_custom_v2` bổ sung cột `Title` để lưu trữ tiêu đề bài đăng gốc (ví dụ: `"71.5 Cô Giang 53 4 4 14 10.3 tỷ"`).
- [ ] **2. Bảo toàn các trường Public để trống:** Các cột Public gồm `Tieu_de_Public` và `Mo_ta_Public` mặc định hiển thị trống (`''`) trên giao diện Admin và lưu trống trong `listings_custom_v2` cho đến khi admin biên tập (tuyệt đối không tự ý gán đè tiêu đề/mô tả thô sang).
- [ ] **3. Mặc định Giá Public = Giá Chào:** Nếu admin chưa nhập giá public tùy chỉnh (`custom_Gia_Public` trống hoặc None), hệ thống sẽ lấy giá trị của Giá chào thô (`Gia_chao`) làm giá trị mặc định cho ô nhập và hiển thị Public.
- [ ] **4. Tên Đường bắt buộc đầy đủ (Không được để trống):**
  - Mặc định ưu tiên trích xuất tên đường từ Tiêu đề bài đăng (`Title` thô) bằng hàm trích xuất regex thông minh (ví dụ: `'71.5 Cô Giang 53...'` -> `'Cô Giang'`).
  - Dự phòng 1: Nếu tiêu đề lỗi hoặc trống, bóc tách từ địa chỉ đầy đủ `placeName` (ví dụ: `'146/15A Võ Thị Sáu, Xuân Hòa...'` -> `'Võ Thị Sáu'`).
  - Dự phòng 2: Lấy thuộc tính `streetName` hoặc `street.name` từ API gốc.
  - Đảm bảo tên Đường không bao giờ bị để trống trong `listings_v2` và `listings_custom_v2`.
- [ ] **5. Phân vùng 19 tiêu chí Criteria trên giao diện Admin:**
  - **8 Tiêu chí Editable (Curation Form bên dưới):** Gồm 8 tiêu chí có cột trong bảng `listings_custom_v2` (`Criteria_Duong_truoc_nha`, `Criteria_Noi_that`, `Criteria_Thang_may`, `Criteria_Loai_ngo`, `Criteria_Khoang_cach_bai_do_xe`, `Criteria_Kinh_doanh_Dong_tien`, `Criteria_Huong_nha`, `Criteria_Khoang_cach_duong_oto`). Các ô này hiển thị dưới dạng ô nhập văn bản tự do (`<input type="text">`), cho phép admin chỉnh sửa tùy ý.
  - **11 Tiêu chí Read-Only (Khu vực THÔNG TIN THÔ - POOL ở trên cùng UI):** Gồm 11 tiêu chí chỉ có ở bảng thô `listings_v2` (`Criteria_Tiem_nang_Rui_ro`, `Criteria_Loai_BDS`, `Criteria_Giay_to_phap_ly`, `Criteria_Hinh_dang_dat`, `Criteria_Tinh_trang_xay_dung`, `Criteria_Cau_truc_nha`, `Criteria_Vi_tri_tinh_thue`, `Criteria_Mat_thoang`, `Criteria_Tien_ich`, `Criteria_Phong_thuy`, `Criteria_Vi_tri_trong_ngo`). Các ô này được gom nhóm hiển thị dưới dạng lưới thuộc tính chỉ đọc (dotted-grid) mang tên `"Tiêu chí nguồn (Chỉ đọc)"` nằm cạnh các thông tin thô khác của Pool thô. Admin không thể chỉnh sửa hay lưu custom.
- [ ] **6. Không bị đè `Criteria_Duong_truoc_nha`:** Sửa payload gửi lên từ client và API handler để tách biệt `Criteria_Duong_truoc_nha` khỏi Alley Type (Phân loại hẻm), không cho phép ghi đè nhầm lẫn.

## Solution

### 1. Database Schema
Bổ sung các cột mới vào CSDL thông qua cơ chế tự động di cư (migration) khi chạy ứng dụng:
- **Bảng `listings_v2`:** Bổ sung cột `Title TEXT`.
- **Bảng `listings_custom_v2`:** Bổ sung cột `Title TEXT`. (Giữ nguyên cấu trúc 8 cột Criteria của Pool2).

### 2. Logic Bóc tách Tên Đường từ Tiêu đề
Sử dụng hàm regex thông minh trích xuất tên đường nằm giữa số nhà đầu tiên và diện tích (con số đầu tiên sau tên đường):
```python
def parse_street_from_title(title_text):
    if not title_text:
        return ""
    tokens = title_text.strip().split()
    if len(tokens) < 2:
        return ""
        
    area_idx = -1
    for idx, token in enumerate(tokens):
        if idx > 0 and re.match(r"^\d+(\.\d+)?$", token):
            # Nếu số được đi trước bởi chữ "số" hoặc "đường" thì là một phần tên đường (ví dụ: "Đường số 7")
            if tokens[idx-1].lower() in ["số", "đường"]:
                continue
            area_idx = idx
            break
            
    if area_idx != -1:
        first_token = tokens[0]
        has_digit = any(c.isdigit() for c in first_token)
        start_idx = 1 if has_digit else 0
        street = " ".join(tokens[start_idx:area_idx])
        if street:
            return street.strip()
            
    return ""
```

### 3. API Payload & Normalization mapping
- **Input (PUT `/api/listings/<tk_id>`):**
  Chỉ gửi lưu 8 trường custom criteria có trong `listings_custom_v2`.
- **Output (GET `/api/listings/<tk_id>`):**
  Trả về đối tượng listing thô kết hợp với các cột custom.
  - `Tieu_de_Public` = `custom_Tieu_De_Public` hoặc rỗng `''`.
  - `Gia_Public` = `custom_Gia_Public` hoặc nếu trống thì trả về `Gia_chao` thô.
  - Cập nhật ánh xạ đè chỉ áp dụng cho 8 tiêu chí trong bảng custom:
    ```python
    editable_criteria_cols = [
        "Criteria_Duong_truoc_nha", "Criteria_Noi_that", "Criteria_Thang_may", "Criteria_Loai_ngo",
        "Criteria_Khoang_cach_bai_do_xe", "Criteria_Kinh_doanh_Dong_tien", "Criteria_Huong_nha", "Criteria_Khoang_cach_duong_oto"
    ]
    for col in editable_criteria_cols:
        custom_key = f"custom_{col}"
        if d.get(custom_key):
            d[col] = d[custom_key]
    ```

## 📋 Implementation Plan
- **Cách tiếp cận:** Thêm cột `Title` vào SQLite schema. Cập nhật mã nguồn crawler offline/online để lưu trữ `Title` và trích xuất tên đường ưu tiên từ Tiêu đề. Thay đổi 8 dropdown trên UI Curation Form thành ô nhập text editable, và hiển thị 11 dropdown thô còn lại thành lưới dotted-grid chỉ đọc trong nhóm "THÔNG TIN THÔ - POOL".
- **Các bước triển khai dự kiến:**
  1. Thay đổi cấu trúc schema và bổ sung di cư tự động cột `Title` trong [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py).
  2. Bổ sung hàm bóc tách tên đường và cập nhật logic cào offline/online trong [fetcher.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/fetcher.py).
  3. Cập nhật logic trả về thông tin biên tập (`normalize_listing_for_client`) chỉ đè cho 8 criteria editable và mặc định giá public trong [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py).
  4. Sửa đổi giao diện curation Admin [lego_detail_admin_pool2.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_admin_pool2.js): gom 11 tiêu chí thô vào grid chỉ đọc trong khu vực "THÔNG TIN THÔ - POOL" ở trên cùng, và chuyển đổi 8 dropdown criteria bên dưới thành các ô nhập text tự do chỉnh sửa.

## 📝 Task Checklist (TODO)
- [ ] **Thiết kế & Khảo sát:**
  - [x] Khảo sát CSDL cục bộ và file cào thực tế.
  - [x] Chạy thử và chốt thuật toán bóc tách tên đường từ Tiêu đề.
- [ ] **Triển khai Code:**
  - [ ] Cập nhật Schema CSDL & Di cư tự động trong `pool_lego.py`.
  - [ ] Tích hợp bộ bóc tách tên đường & trường `Title` trong `fetcher.py`.
  - [ ] Ánh xạ đè 8 criteria & Mặc định Giá Public = Giá Chào trong `manager.py`.
  - [ ] Chuyển đổi 8 dropdown thành ô nhập text editable, 11 dropdown thành read-only nằm ở khu vực THÔNG TIN THÔ - POOL phía trên cùng UI trong `lego_detail_admin_pool2.js`.
- [ ] **Kiểm thử sơ bộ:**
  - [ ] Chạy kiểm thử schema và di cư.
  - [ ] Xác minh hiển thị trống của `Tieu_de_Public` và giá trị mặc định của `Gia_Public`.
  - [ ] Đảm bảo 8 ô criteria chỉnh sửa được ở form dưới và 11 ô hiển thị chỉ đọc (Read-Only) ở nhóm thô phía trên.

## Verification Plan

### Manual Verification
1. Khởi động ứng dụng biên tập rổ hàng cục bộ.
2. Kiểm tra CSDL bằng script xem bảng `listings_v2` và `listings_custom_v2` đã tự động thêm cột `Title` chưa.
3. Thực hiện cào lại hoặc cào mới file offline `Thien Khoi Group - Chi Tiet New 17-6.html`.
4. Xem chi tiết căn `TKPUH253` trên trang Admin:
   - Ô nhập tiêu đề Public phải trống (`''`).
   - Ô nhập Giá Public hiển thị mặc định bằng Giá chào (`10.3`).
   - Tên đường hiển thị chính xác là `"Cô Giang"` (trích xuất từ tiêu đề).
   - 8 ô tiêu chí editable (như `Criteria_Noi_that`, `Criteria_Duong_truoc_nha`) hiển thị ở Curation Form bên dưới dạng ô nhập văn bản tự do, cho phép sửa lưu thành công.
   - 11 ô tiêu chí còn lại (như `Criteria_Tiem_nang_Rui_ro`, `Criteria_Loai_BDS`) hiển thị ở nhóm "THÔNG TIN THÔ - POOL" phía trên cùng dưới dạng lưới chỉ đọc (Read-Only), không thể chỉnh sửa.

## Files touched
- `pool_lego.py` — Bổ sung cột, tự động di cư, logic đồng bộ và lưu trữ.
- `fetcher.py` — Hàm bóc tách tên đường, cào offline/online bổ sung Title và tên đường.
- `manager.py` — Logic format JSON API, ánh xạ 8 criteria custom, mặc định giá public.
- `static/js/lego_detail_admin_pool2.js` — Nhóm 11 criteria chỉ đọc lên khu vực THÔNG TIN THÔ - POOL, chuyển đổi 8 criteria custom thành text input bên dưới.
