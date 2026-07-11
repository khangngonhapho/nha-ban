---
id: US-062
status: accepted
date: 2026-06-03
size: S
---

# US-062: Sửa lỗi sắp xếp theo cập nhật mới nhất/cũ nhất tùy theo danh sách đang xem

## User story
**As an** Admin
**I want** hệ thống sắp xếp chính xác danh sách Bất Động Sản theo thời gian cập nhật mới nhất/cũ nhất tùy vào chế độ danh sách đang xem (Tất cả Pool thô vs. Chỉ căn lên sóng vs. Danh sách Client)
**So that** có thể theo dõi và quản lý rổ hàng mới/cũ hiệu quả, không bị lỗi đứng im/không tác dụng khi nhấn sắp xếp theo Thời gian trong chế độ "Chỉ căn lên sóng" hoặc "Kho Pool thô".

## Acceptance
- [x] Khi đang ở chế độ xem "Tất cả" trong Kho Pool (`activeMode === 'pool'` và `showOnAirOnly === false`), việc sắp xếp theo Thời gian (`newest`) phải dựa trên thứ tự dòng (chỉ số index) của căn nhà trong Sheet Pool (tức là thứ tự cào về).
- [x] Khi đang ở chế độ xem "Chỉ căn lên sóng" trong Kho Pool (`activeMode === 'pool'` và `showOnAirOnly === true`), việc sắp xếp theo Thời gian (`newest`) phải khớp đúng theo thứ tự dòng (chỉ số index) của căn nhà trong Sheet Source (tức là theo thứ tự lên sóng thực tế).
- [x] Khi ở chế độ Client hoặc xem Source thông thường, việc sắp xếp theo Thời gian vẫn hoạt động bình thường theo thứ tự dòng của Sheet Source.
- [x] Khắc phục triệt để lỗi khi click chọn sắp xếp theo cập nhật mới nhất (`⏱️`) trong Kho Pool không hoạt động (do `temp_id` dạng chuỗi `"pool_SYS-..."` parse ra `NaN`).
- [x] Trạng thái sắp xếp (loại sắp xếp và hướng sắp xếp) hoạt động ổn định và lưu/khôi phục chính xác từ `localStorage`.

## Solution

> [!note]- Key logic
> - **Cải tiến trong `getMappedPoolData()`:**
>   Thay đổi trường `temp_id` của các căn Pool thô từ dạng chuỗi `"pool_" + systemId` thành dạng số `index + 1` đại diện cho thứ tự dòng trong Sheet Pool để có thể so sánh toán học khi sắp xếp:
>   ```javascript
>   MAPPED_POOL_DATA = POOL_ROWS.map((row, index) => {
>     ...
>     const p = {
>       temp_id: index + 1,
>       ...
>   ```
> - **Cải tiến logic sắp xếp trong `render()`:**
>   Tự động phát hiện chế độ danh sách đang xem để áp dụng trọng số thời gian (index) tương ứng:
>   1. Nếu đang xem "Chỉ căn lên sóng" trong Kho Pool (`activeMode === 'pool'` và `showOnAirOnly` là `true`): Dò tìm phần tử tương ứng trong `DATA` (danh sách trên sóng Source) để lấy `temp_id` của nó (index trên Source sheet).
>   2. Các trường hợp còn lại: Sử dụng trực tiếp `temp_id` của phần tử (đã được chuẩn hóa thành dạng số ở bước map dữ liệu).
>   ```javascript
>   const arr = filteredArr.slice().sort((a, b) => {
>     if (currentSortType === 'newest') {
>       let ta, tb;
>       if (isAdmin && activeMode === 'pool' && showOnAirOnly) {
>         const ma = DATA.find(x => 
>           (x.system_id && a.system_id && String(x.system_id).trim() === String(a.system_id).trim()) ||
>           (x.id && a.id && String(x.id).trim() === String(a.id).trim())
>         );
>         const mb = DATA.find(x => 
>           (x.system_id && b.system_id && String(x.system_id).trim() === String(b.system_id).trim()) ||
>           (x.id && b.id && String(x.id).trim() === String(b.id).trim())
>         );
>         ta = ma ? parseInt(ma.temp_id, 10) || 0 : 0;
>         tb = mb ? parseInt(mb.temp_id, 10) || 0 : 0;
>       } else {
>         ta = parseInt(a.temp_id, 10) || 0;
>         tb = parseInt(b.temp_id, 10) || 0;
>       }
>       return currentSortDir === 'asc' ? ta - tb : tb - ta;
>     } else {
>       const ga = parseFloat(a.gia) || 0, gb = parseFloat(b.gia) || 0;
>       return currentSortDir === 'asc' ? ga - gb : gb - ga;
>     }
>   });
>   ```

## 📋 Implementation Plan
- **Cách tiếp cận:** Tận dụng chỉ số index tự nhiên của Google Sheet (đã được tải về client dưới dạng mảng) làm trọng số thời gian cho việc sắp xếp mới nhất/cũ nhất. Chuẩn hóa `temp_id` của Pool data sang dạng số và viết logic điều hướng so sánh động trong hàm `render()`.
- **Các bước triển khai dự kiến:**
  1. Cập nhật `getMappedPoolData()` chuyển đổi `temp_id` từ dạng chuỗi `"pool_SYS-..."` sang dạng số nguyên dựa trên index.
  2. Cập nhật hàm `render()` tinh chỉnh logic sắp xếp theo thời gian (`newest`) có rẽ nhánh động theo chế độ `showOnAirOnly` trong Kho Pool.
  3. Mở trình duyệt chạy thử ở các chế độ xem để kiểm chứng tính đúng đắn của thứ tự sắp xếp.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát code cũ
  - [x] Chốt giải pháp và tạo User Story
- [x] **Triển khai Code:**
  - [x] Chuẩn hóa `temp_id` của Pool sang dạng số nguyên trong `getMappedPoolData()`
  - [x] Cập nhật logic sắp xếp thời gian rẽ nhánh trong hàm `render()`
- [x] **Kiểm thử sơ bộ:**
  - [x] Kiểm tra sắp xếp ở chế độ xem "Tất cả" của Kho Pool
  - [x] Kiểm tra sắp xếp ở chế độ xem "Chỉ căn lên sóng" của Kho Pool
  - [x] Kiểm tra sắp xếp ở chế độ xem Client (Source) thông thường
  - [x] Xác nhận trạng thái lưu/khôi phục từ `localStorage` hoạt động hoàn hảo

## 🛠️ Update Logic (Drafting while Doing)
### 1. Nhật ký Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- **Sự cố kỹ thuật & Cách khắc phục:** Việc convert `temp_id` sang dạng số nguyên hoạt động rất tốt, không gây bất kỳ phản ứng phụ nào vì thuộc tính này chỉ được sử dụng nội bộ để phục vụ tính năng so sánh sắp xếp (không dùng làm ID DOM hay class).
- **Phát kiến ngoài kế hoạch / Điểm tối ưu phát hiện khi code:** Tận dụng dữ liệu Source `DATA` đã được tải sẵn trên Client làm bản đối chiếu ánh xạ (Mapping lookup) để tìm đúng thứ tự lên sóng khi lọc "Chỉ căn lên sóng" trong Kho Pool, giúp tránh được việc phải thực hiện thêm API call hoặc lưu trữ thêm trạng thái phức tạp.

### 2. Nhật ký chạy thử nháp (Draft Test Logs)
- **Script kiểm thử thô / nháp đã chạy:** Đã xác minh hoạt động trực tiếp qua Vercel Live Preview và được Product Owner nghiệm thu đạt 100% yêu cầu.

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)
### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh:** Không có sự cố phát sinh trong quá trình code và triển khai.

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Kinh nghiệm code & Cấu hình:** Sử dụng chỉ số index tự nhiên của mảng làm trọng số thời gian (khi không có timestamp chính xác) là một phương án tối giản, hiệu quả cao và nhẹ nhàng cho client.
- **Kinh nghiệm kiểm thử:** Khi kiểm thử tính năng sắp xếp, luôn kiểm tra sự tương tác giữa bộ lọc (filter) và chức năng sắp xếp để tránh các lỗi logic ẩn.

## Verification Plan

### Manual Verification
1. Đăng nhập Admin vào trang web, chuyển sang chế độ **Kho Pool**.
2. Chọn bộ lọc sắp xếp **Thời gian (⏱️)** $\rightarrow$ Bật tắt để chuyển đổi giữa `⏱️⬇` (Mới nhất) và `⏱️⬆` (Cũ nhất) ở chế độ xem **Tất cả**. Xác nhận danh sách thay đổi thứ tự và các căn ở đáy Google Sheet (cào mới nhất) xuất hiện lên đầu hoặc xuống cuối tương ứng.
3. Bật toggle **Chỉ căn lên sóng (🟢 Đã lên sóng)**. Nhấp thay đổi sắp xếp `⏱️⬇` và `⏱️⬆`. Xác nhận danh sách các căn lên sóng được sắp xếp đúng theo thứ tự thời gian cập nhật trên sóng (dựa theo thứ tự dòng trong Sheet Source).
4. Quay lại màn hình chính của Admin (Source) và Client. Nhấp sắp xếp theo Thời gian và kiểm tra độ chính xác của thứ tự hiển thị.

## Files touched
- `index.html` — [Frontend Sorting UI & Logic]
