---
id: US-114
status: accepted
date: 2026-06-29
size: S
---

# US-114: Khắc phục lỗi cú pháp khởi chạy CHAY_APP.bat và lỗi công thức #ERROR trên Google Sheets (Fix Startup Syntax Error & Google Sheets Formula #ERROR)

## User Story
**As an** Admin / Developer
**I want** the local Flask server to start without syntax errors when running `CHAY_APP.bat`
**And** detailed descriptions in the "Pool" sheet starting with `-` or `+` to be saved as plain text instead of invalid formulas
**So that** I can edit listings and view them on Vercel without `#ERROR` messages.

## Acceptance Criteria
- [ ] Chạy `CHAY_APP.bat` khởi động Flask server cục bộ thành công, không gặp lỗi `SyntaxError: unexpected character after line continuation character` ở tệp [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py).
- [ ] Khi đăng tải hoặc cập nhật một căn nhà lên Google Sheets (ở cả chế độ Pool1 và Pool2), các nội dung dạng văn bản (đặc biệt là cột "Mô tả chi tiết") nếu bắt đầu bằng dấu trừ `-` hoặc dấu cộng `+` hoặc dấu bằng `=` (nhưng không phải là công thức hợp lệ) phải được tự động chuyển thành định dạng văn bản thô (text) trên Google Sheets bằng cách thêm ký tự nháy đơn `'` ở đầu giá trị truyền lên API Google Sheets.
- [ ] Google Sheets hiển thị chính xác nội dung bắt đầu bằng `-` hoặc `+` mà không bị báo lỗi `#ERROR!`.
- [ ] Trang chi tiết trên Vercel hiển thị đầy đủ, chính xác nội dung này mà không bị hiển thị chuỗi `#ERROR!`.
- [ ] Các công thức Google Sheets hợp lệ được ghi nhận từ mã nguồn (như `=IMAGE(...)`) vẫn hoạt động bình thường, không bị chèn ký tự nháy đơn.

## Solution

1. **Sửa lỗi cú pháp khởi chạy:**
   - Trong tệp [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py) tại dòng 2109, dấu nháy kép đóng cho chuỗi JSON suffix `"gocNhinDauTu"` chưa được escape, khiến Python đóng chuỗi literal sớm và hiểu nhầm ký tự `,\n` phía sau là lỗi cú pháp. Sửa `" ... điều kiện)",\n"` thành `" ... điều kiện)\",\n"`.

2. **Sửa lỗi công thức #ERROR trên Google Sheets:**
   - Tạo hàm phụ `escape_sheets_value(val)` trong tệp [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py) để kiểm tra các giá trị chuỗi gửi lên Sheets. Nếu chuỗi bắt đầu bằng `-`, `+` hoặc `=` và không phải là công thức được hỗ trợ (ví dụ `=IMAGE(`), tự động chèn dấu nháy đơn `'` phía trước.
   - Gọi hàm này khi xử lý mảng `row_data` trước khi ghi đè hoặc chèn dòng lên Google Sheets trong cả luồng Pool1 (`publish_listing`) và Pool2 (`build_row_data`).

## 📋 Implementation Plan
- **Các bước triển khai:**
  1. Viết tài liệu User Story `US-114` (tệp này).
  2. Cập nhật mục lục [INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md) đăng ký mã `US-114` ở trạng thái `in-progress`.
  3. Sửa dòng 2109 trong [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py).
  4. Bổ sung logic `escape_sheets_value` vào `build_row_data` và `publish_listing` trong [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py).
  5. Chạy thử nghiệm Flask server cục bộ để xác nhận hết lỗi cú pháp.
  6. Kiểm thử tích hợp việc xuất bản căn nhà có chứa nội dung bắt đầu bằng `-` lên Google Sheets để kiểm tra kết quả thực tế.
  7. Chạy bộ kiểm thử E2E tự động để phòng ngừa lỗi hồi quy.

## 📝 Task Checklist (TODO)
- [x] **Khảo sát & Viết tài liệu:** Viết tài liệu User Story `US-114` (Đã hoàn thành tệp này)
- [x] **Đồng bộ Index:** Cập nhật tệp [INDEX.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/INDEX.md)
- [x] **Sửa lỗi khởi chạy:** Sửa lỗi cú pháp dòng 2109 trong [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py)
- [x] **Sửa lỗi Google Sheets:** Thêm hàm `escape_sheets_value` và tích hợp vào `pool_lego.py`
- [x] **Kiểm thử tự động:** Chạy kịch bản test E2E để đảm bảo không lỗi hồi quy
- [x] **Nghiệm thu:** Cập nhật trạng thái story sang `done` hoặc `accepted` trong `INDEX.md`, `NEXT_SESSION.md` và `SOURCE_OF_TRUTH.md`

## Verification Plan

### Automated Tests
- Chạy bộ kịch bản kiểm thử E2E của dự án:
  ```powershell
  python scratch/test_e2e_curation.py
  python scratch/test_e2e_filters.py
  ```

### Manual Verification
1. Chạy file `CHAY_APP.bat` và xác nhận Flask server khởi chạy bình thường, hiển thị `http://localhost:5000`.
2. Vào giao diện biên tập chi tiết một căn nhà, nhập nội dung cột "Mô tả chi tiết" bắt đầu bằng dấu trừ `-` (ví dụ: `- Nhà đẹp 4 tầng hẻm xe hơi`).
3. Bấm xuất bản/lên sóng để hệ thống đồng bộ lên Google Sheets.
4. Truy cập Google Sheets kiểm tra xem ô "Mô tả chi tiết" hiển thị đúng dạng văn bản thô `- Nhà đẹp...` thay vì lỗi `#ERROR!`.
5. Truy cập trang chi tiết trên Vercel/Local để xem nội dung hiển thị bình thường.

## 🧠 Retro, Lessons Learned & Good Practices

### Lessons Learned
1. **Lỗi cú pháp nối chuỗi JSON Suffix**:
   - Khi nối thêm chuỗi JSON suffix để chỉ thị AI, cần chú ý escape tất cả các ký tự nháy kép của các trường JSON (ví dụ `\"gocNhinDauTu\"`). Việc thiếu ký tự escape nháy kép đóng `" ... )"` thay vì `" ... )\""` sẽ kết thúc chuỗi literal của Python sớm và dẫn đến lỗi biên dịch `SyntaxError`.
   - **Bài học:** Cần bổ sung test-run khởi động server Flask cục bộ trong kịch bản CI hoặc git pre-commit hooks để ngăn chặn đẩy code lỗi cú pháp lên nhánh chính.

2. **Lỗi công thức khi ghi Google Sheets với USER_ENTERED**:
   - Google Sheets API khi gọi với `valueInputOption="USER_ENTERED"` sẽ cố gắng biên dịch và parse tất cả các giá trị bắt đầu bằng `-`, `+`, hoặc `=` thành công thức. Các giá trị văn bản thô như mô tả chi tiết bắt đầu bằng các dấu này sẽ gây ra lỗi cú pháp công thức `#ERROR!`.
   - **Bài học:** Các giá trị chuỗi nhập vào tự nhiên có nguy cơ bắt đầu bằng dấu `-` hoặc `+` (danh sách liệt kê) cần phải được làm sạch hoặc tự động thêm dấu nháy đơn `'` ở đầu trước khi ghi lên Google Sheets. Dấu nháy đơn này giúp Google Sheets coi ô đó là văn bản thuần tuý và tự động ẩn nháy đơn đi khi hiển thị hoặc khi lấy dữ liệu ra qua API.

