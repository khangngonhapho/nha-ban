# Chính sách Ghi Đè khi Đồng Bộ (Sync Overwrite Policy)

Tài liệu này định nghĩa chi tiết hành vi ghi đè dữ liệu của hệ thống Khang Ngô Nhà Phố khi đồng bộ dữ liệu từ SQLite local lên tab **Pool** của Google Sheets (cả chế độ Pool1 và Pool2) đối với các căn nhà đã tồn tại.

---

## 1. Nguyên Tắc Cốt Lõi

Khi một căn nhà đã tồn tại trên Sheet (được tìm thấy thông qua `Mã Hàng` hoặc `System ID`):
*   Hệ thống **chỉ ghi đè các cột thuộc Nhóm 1** (thông tin thô cào từ Thiên Khôi, Last Crawl, Last Sync, JSON_UI...).
*   Hệ thống **bảo toàn tuyệt đối các cột thuộc Nhóm 2** (chất xám biên tập của PO, ảnh đã lọc, đánh giá nội bộ của Admin, các cột custom tự thêm). Giá trị cũ của các cột này trên Sheet sẽ được đọc ra và ghi lại y nguyên.

---

## 2. Chi Tiết Phân Phối 90 Cột Nghiệp Vụ

### NHÓM 1: CÁC CỘT ĐƯỢC GHI ĐÈ KHI RECRAWL/SYNC (75 Cột)
Các cột này tự động cập nhật dữ liệu mới nhất từ lượt cào hoặc lượt cập nhật hệ thống gần nhất:

1.  `Tỉnh` (Địa giới hành chính thô)
2.  `Quận` (Địa giới hành chính thô)
3.  `Phường` (Địa giới hành chính thô)
4.  `Đường` (Tên đường thô)
5.  `Ngõ/Số nhà` (Số nhà thô)
6.  `Phân loại` (Tag thô từ Thiên Khôi)
7.  `Năm xây dựng` (Thông số thô)
8.  `Nội dung chính` (Thông tin thô)
9.  `Mô tả chi tiết` (Mô tả gốc từ Thiên Khôi)
10. `Giá chào` (Giá thô Thiên Khôi)
11. `Giá chốt` (Giá chốt nội bộ Thiên Khôi)
12. `DT Thực tế` (Diện tích thô)
13. `DT Trên sổ` (Diện tích sổ thô)
14. `Số Tầng` (Thông số thô)
15. `Mat Tien` (Chiều ngang thô)
16. `Hướng` (Thông số thô)
17. `Tên Chủ Nhà` (Liên hệ thô)
18. `Điện thoại 1` (Liên hệ thô)
19. `Điện thoại 2` (Liên hệ thô)
20. `Loại Hợp đồng` (Nghiệp vụ thô)
21. `Số ngày ký` (Nghiệp vụ thô)
22. `Ngày bắt đầu` (Nghiệp vụ thô)
23. `Ngày kết thúc` (Nghiệp vụ thô)
24. `Người ký` (Nghiệp vụ thô)
25. `Trạng thái` (Trạng thái nguồn thô)
26. `Sơ đồ thửa đất 1` (Ảnh sơ đồ thô)
27. `Sơ đồ thửa đất 2` (Ảnh sơ đồ thô)
28. `Sơ đồ thửa đất 3` (Ảnh sơ đồ thô)
29. `Sơ đồ thửa đất 4` (Ảnh sơ đồ thô)
30. `Sơ đồ thửa đất 5` (Ảnh sơ đồ thô)
31. `Hình Hẻm 1` (Ảnh hẻm thô)
32. `Hình Hẻm 2` (Ảnh hẻm thô)
33. `Hình Hẻm 3` (Ảnh hẻm thô)
34. `Hình Hẻm 4` (Ảnh hẻm thô)
35. `Hình Hẻm 5` (Ảnh hẻm thô)
36. `Hình Hẻm 6` (Ảnh hẻm thô)
37. `Hình Hẻm 7` (Ảnh hẻm thô)
38. `Hình Hẻm 8` (Ảnh hẻm thô)
39. `Hình Hẻm 9` (Ảnh hẻm thô)
40. `Hình Hẻm 10` (Ảnh hẻm thô)
41. `Số phòng ngủ` (Thông số thô)
42. `Số nhà vệ sinh` (Thông số thô)
43. `Điện thoại Đầu Chủ` (Liên hệ thô)
44. `Tên Đầu Chủ (Hợp đồng)` (Liên hệ thô)
45. `Điểm Facebook` (Thông số thô)
46. `Mã TK Mới` (Mã thô mới)
47. `Last Crawl` (Thời điểm cào mới nhất)
48. `Last Sync` (Thời điểm đồng bộ mới nhất)
49. `JSON_UI` (Thông tin giao diện phụ, chứa `createdAtSigned` và `updatedAt` của Thiên Khôi)
50. `Images_Admin_JSON` (Trộn thông minh - xem quy tắc tại Mục 3)
51. `Ảnh 1` đến `Ảnh 25` (Danh sách 25 ảnh di cư)

---

### NHÓM 2: CÁC CỘT ĐƯỢC BẢO VỆ TUYỆT ĐỐI (20 Cột)
Các cột này được giữ nguyên giá trị cũ trên Sheet, không bị ghi đè:

1.  `Mã Hàng` (Định danh thô)
2.  `System ID` (Khóa ngoại đồng bộ)
3.  `Mã Khang Ngô (ID)` (ID sinh ra theo thuật toán địa chỉ)
4.  `Hình Nhận Diện` (Ảnh đại diện do PO chọn)
5.  `Hình Mặt Tiền` (Ảnh mặt tiền đã được chọn thủ công)
6.  `Tiêu đề Public` (Chất xám biên tập)
7.  `Mô tả Public` (Chất xám biên tập)
8.  `Giá Public` (Chất xám biên tập)
9.  `Phân loại Hẻm` (Chất xám biên tập)
10. `Đường trước nhà (m)` (Chất xám biên tập)
11. `Tình trạng nhà` (Chất xám biên tập)
12. `Ảnh Public (VD: 1,3,5)` (Chất xám biên tập chọn ảnh)
13. `Ảnh Hẻm Public (VD: 1,2)` (Chất xám biên tập chọn ảnh)
14. `Phường cũ (AI)` (Dữ liệu do AI sinh)
15. `Đánh giá (Admin)` (Đánh giá nội bộ)
16. `Ngủ trệt (Admin)` (Đánh giá nội bộ)
17. `CHDV (Admin)` (Đánh giá nội bộ)
18. `Duyệt Public` (Trạng thái duyệt của PO)
19. `Trạng thái Public` (Trạng thái hiển thị web)
20. **Toàn bộ cột Custom tự thêm:** Bất kỳ cột nào trên Sheet có chứa tiền tố hoặc hậu tố `"custom"` hoặc `"Custom"` trong tiêu đề (ví dụ: `Phường Custom`, `Hướng Custom`).

---

## 3. Quy Tắc Trộn Ảnh Thông Minh (Smart Merge) cho `Images_Admin_JSON`

Khi cập nhật cột `Images_Admin_JSON` trong SQLite và đồng bộ lên Google Sheets, hệ thống tuân thủ nghiêm ngặt 3 bước sau:

1.  **Bảo toàn ảnh thủ công (manual) & Cập nhật ảnh Thiên Khôi hiện tại:**
    *   Tất cả ảnh do người dùng upload thủ công được giữ nguyên vị trí, thứ tự và thuộc tính.
    *   Tất cả ảnh Thiên Khôi cũ vẫn còn tồn tại trong lượt cào mới sẽ được giữ nguyên 100% (không ghi đè URL, role hay trạng thái visible/hidden vì hệ thống/người dùng đã xử lý rồi).
2.  **Xử lý ảnh Thiên Khôi đã bị xóa:**
    *   Nếu một ảnh cũ di cư từ Thiên Khôi không còn xuất hiện trong lượt cào mới (đã bị xóa ở nguồn), hệ thống **VẪN GIỮ LẠI** ảnh đó trong danh sách, đồng thời tự động cập nhật:
        *   `visible = False` (tương đương `is_hidden = 1`)
        *   `role = "deleted"`
3.  **Bổ sung ảnh Thiên Khôi mới cào:**
    *   Tất cả ảnh mới xuất hiện trong lượt cào mới sẽ được tải về, di cư lên Cloud R2/Drive và chèn vào cuối danh sách.
    *   Để tránh tự động hiển thị ra bên ngoài, ảnh mới cào mặc định được đặt **`visible = False` (tương đương `is_hidden = 1`)** — ảnh này chỉ hiển thị trong giao diện Curator của Admin để chờ duyệt, không hiển thị ra khách hàng cuối.
