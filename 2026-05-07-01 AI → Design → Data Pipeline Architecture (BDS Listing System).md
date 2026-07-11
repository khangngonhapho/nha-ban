Mô tả dữ liệu đầu vào:

- dạng text: 163.24.80 Tô Hiến Thành 50.2 5 4 13 12.9 tỷ Hòa Hưng Quận 10
- dạng hình: như đã attach.
- và các hình ảnh nhà ở máy local. Dữ liệu đầu ra đưa vào file google sheet. Có 2 file google sheet: Raw: Có thông tin thật. Public: Thông tin được thay đổi để gửi cho khách hàng. Website đã kết nối với google sheet public rồi. Làm sao để đưa 2 google sheet và nơi sẽ chứa hình sau này của các căn nhà để lấy link đưa vào google sheet

Hiện tại Trang đã có sẵn những gì rồi?Đã có 2 Google Sheet (Raw + Public), Đã có Google Drive folder chứa hình

Hình ảnh nhà thường có bao nhiêu tấm/căn và được tổ chức thế nào?5-15 hình/căn, tên file lộn xộn

Mã căn nhà (ví dụ 163.24.80) sẽ là khóa chính để liên kết Sheet ↔ Drive?Số nhà đã được mã hoá sẽ là khoá chính. Rule để tạo số nhà đã có.

Bao nhiêu căn được nhập mới mỗi tuần và ai nhập?10-30 căn/ tuần, chỉ Trang nhập

2026-05-07-01 AI → Design → Data Pipeline Architecture (BDS Listing System)

Trước khi đề xuất kiến trúc cụ thể, tôi cần hiểu rõ thêm vài điểm để thiết kế đúng nhu cầu của Trang. Để tôi load tool hỏi nhanh.Cảm ơn Trang. Với context hiện tại (2 Sheet đã có, Drive folder đã có, key là mã căn, ~10-30 căn/tuần, hình 5-15 tấm tên lộn xộn), đây là kiến trúc tôi đề xuất.

## 1. Cấu trúc folder Drive đề xuất

Vì sau 1 năm Trang sẽ có ~500-1500 căn, nên không nên để flat. Tôi đề xuất 2 tầng:

```
BDS-KhangNgo/ (folder gốc trên Drive)
├── 01_HINH_NHA/
│   ├── Q10/
│   │   └── 163.24.80/         ← tên folder = mã căn
│   │       ├── 01_mat-tien.jpg
│   │       ├── 02_phong-khach.jpg
│   │       └── ...
│   ├── Q1/
│   ├── Q3/
│   └── ...
├── 02_HINH_PHAP_LY/            ← sổ, HĐ — folder riêng, KHÔNG share public
│   └── 163.24.80/
└── 99_ARCHIVE/                 ← căn đã bán
```

Lý do: folder cấp Quận giúp scan bằng mắt nhanh khi có nhiều căn; tách hình pháp lý ra folder riêng để Trang có thể share công khai folder hình nhà mà không lo lộ sổ/hợp đồng.

## 2. Cách lấy link đưa vào Sheet

Có 2 cách lấy link, chọn theo nhu cầu website:

**Cách A — Link folder (đơn giản, ít cập nhật):** Trong Sheet chỉ cần 1 cột `Link_Hinh` chứa URL folder Drive của căn đó. Khi thêm/xóa hình, không cần đụng vào Sheet. Phù hợp nếu website chỉ cần "xem thêm hình" → mở folder.

**Cách B — Link từng ảnh (linh hoạt cho website):** Sheet có cột `Link_Hinh_1`, `Link_Hinh_2`, ... chứa direct image URL (`https://drive.google.com/uc?id=FILE_ID`). Phù hợp nếu website tự render carousel ảnh. Cần Apps Script tự động list file trong folder và đổ link vào sheet.

Tôi đề xuất **Cách B** vì website BĐS thường cần hiển thị carousel. Tôi sẽ viết Apps Script tự động: khi thêm hình mới vào folder của 1 căn, nó tự cập nhật link vào dòng tương ứng trong Sheet Raw.

## 3. Quan hệ Raw ↔ Public

Hai sheet liên kết qua cột `Mã_căn`. Sheet Public dùng `IMPORTRANGE` + công thức biến đổi để ẩn thông tin nhạy cảm:

|Trường|Raw (thật)|Public (ẩn)|
|---|---|---|
|Số nhà|163/24/80 Tô Hiến Thành|"Hẻm Tô Hiến Thành"|
|Chủ nhà|Nguyễn Hoàng Nam|(bỏ trống)|
|SĐT|0973776929|(bỏ trống)|
|Giá|12.9 tỷ TL|12.9 tỷ|
|Diện tích, kết cấu, mô tả|giữ nguyên|giữ nguyên|
|Link hình nhà|folder Drive|folder Drive (share-link)|
|Link hình pháp lý|có|KHÔNG có|

## 4. Workflow nhập 1 căn (cho Trang)

Khi có 1 căn mới, Trang sẽ làm 4 bước, AI/script lo phần nặng:

1. **Paste text + ảnh listing** vào tool AI → AI extract ra cấu trúc JSON (mã căn, diện tích, giá, kết cấu, vị trí, mô tả...).
2. **AI append 1 dòng vào Raw sheet** với data đã extract + auto-fill cột mã căn theo rule có sẵn.
3. **AI tạo folder Drive** `01_HINH_NHA/Q[X]/[mã căn]/` và upload hình nhà từ local lên đó (đổi tên `01_`, `02_`, ... theo thứ tự).
4. **Apps Script trigger** tự động lấy link folder/từng ảnh → ghi vào cột `Link_Hinh` của dòng vừa thêm.

Sheet Public tự cập nhật qua IMPORTRANGE, website tự load.

## 5. Câu hỏi quyết định trước khi build

Trước khi tôi đi vào setup chi tiết (viết Apps Script, template Sheet, hướng dẫn share quyền Drive), Trang cần chốt 3 điều:

**(a) Website cần link folder hay link từng ảnh?** → quyết định Cách A vs B ở mục 2.

**(b) Rule ẩn thông tin Raw → Public của Trang đã có chưa?** → tôi cần list cụ thể trường nào ẩn, ẩn kiểu nào (xóa, làm mờ, đổi text) để viết công thức/script.

**(c) Trang muốn nhập liệu qua đâu?** → (i) chat trực tiếp với tôi ở Cowork → tôi gọi MCP Google Drive/Sheet, hoặc (ii) một Web App nội bộ (Apps Script) có form paste text + drag hình, hoặc (iii) chỉ Apps Script chạy ngầm + Trang nhập tay vào Sheet.

Trang muốn tôi đi tiếp theo hướng nào? Tôi gợi ý nên answer (a) và (c) trước, còn (b) Trang có thể gửi tôi rule sau.