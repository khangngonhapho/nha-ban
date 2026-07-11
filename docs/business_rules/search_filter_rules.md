# 🔍 Quy Tắc Tìm Kiếm & Bộ Lọc (Search & Filter Rules)

Tài liệu này định nghĩa chi tiết các quy tắc liên quan đến bộ máy tìm kiếm thông minh và logic áp dụng bộ lọc trên giao diện BDS Khang Ngô.

## 1. Bộ Máy Tìm Kiếm Thông Minh (Smart Search Parser)
Thanh tìm kiếm thông minh (`bdsSearchInput`) hỗ trợ người dùng lọc dữ liệu nhanh bằng cách gõ ngôn ngữ tự nhiên:
- **Logic AND phân tách bằng dấu cộng (`+`):** Khi Admin hoặc Khách hàng gõ nhiều từ khóa cách nhau bởi dấu `+` (ví dụ: `q3 + hẻm xe hơi + 10 tỷ`), hệ thống tự động phân tách thành danh sách các điều kiện và áp dụng logic AND (tất cả các điều kiện đều phải khớp).
- **So khớp địa chỉ & Số nhà thông minh:**
  - Nhận diện Số nhà + Tên đường bằng biểu thức chính quy (Regex).
  - So khớp số nhà hỗ trợ:
    - Khớp chính xác (exact match): số nhà trùng khớp hoàn toàn.
    - Khớp phụ (sub-number): nhận diện số nhà dạng xẹt (ví dụ `39/2` khớp khi tìm `39`).
    - Khớp nhiều căn gộp (`+`): gộp tìm kiếm từ số nhà phức hợp (ví dụ: `1168.42+44` khớp khi tìm `1168.42`).

---

## 2. Bản Đồ Phường Tĩnh (STATIC_WARD_MAP)
- Để hiển thị nhanh danh sách tab Phường trên thanh bộ lọc mà không cần chờ tính toán động từ CSDL, hệ thống khai báo bản đồ phường tĩnh `STATIC_WARD_MAP` cho 5 quận trọng điểm:
  - **Quận 3:** `['p1', 'p2', 'p3', 'p4', 'p5', 'p9', 'p10', 'p11', 'p12', 'p13', 'p14', 'võ thị sáu']`
  - **Quận 10:** `['p1', 'p2', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p11', 'p12', 'p13', 'p14', 'p15']`
  - **Tân Bình:** `['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13', 'p14', 'p15']`
  - **Phú Nhuận:** `['p1', 'p2', 'p3', 'p4', 'p5', 'p7', 'p8', 'p9', 'p10', 'p11', 'p13', 'p15', 'p17']`
  - **Bình Thạnh:** `['p1', 'p2', 'p3', 'p5', 'p6', 'p7', 'p11', 'p12', 'p13', 'p14', 'p15', 'p17', 'p19', 'p21', 'p22', 'p24', 'p25', 'p26', 'p27', 'p28']`
- **Cơ chế Tab Phường:** Hàm `buildWardTabs()` hiển thị danh sách các phường chính xác theo đúng thứ tự mảng tĩnh trên mà không áp dụng sắp xếp chữ cái ABC, giúp ưu tiên các phường trọng tâm lên đầu. Nếu chọn quận nằm ngoài danh sách tĩnh, hệ thống sẽ tự động fallback về tính toán động từ CSDL hiện hữu.

---

## 3. Quy Tắc Sắp Xếp Thời Gian Thực (temp_id)
- Để phục vụ tính năng sắp xếp theo cập nhật mới nhất/cũ nhất trong Kho Pool, hệ thống gán thuộc tính `temp_id` cho từng căn:
  - Trong **Kho Pool**, `temp_id` được gán bằng giá trị số nguyên `index + 1` tương ứng với vị trí dòng của căn nhà trong Sheet Pool.
  - Khi click sắp xếp, hệ thống so sánh các `temp_id` này để sắp xếp chính xác dòng mới nhất lên đầu mà không bị đơ/đóng băng trình duyệt (khắc phục lỗi `parseInt` ra `NaN` do dùng string ID cũ).
