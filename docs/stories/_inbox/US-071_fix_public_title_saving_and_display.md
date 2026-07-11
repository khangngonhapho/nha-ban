---
id: US-071
status: accepted
date: 2026-06-04
size: S
---

# US-071: Khắc phục lỗi lệch cột lưu tiêu đề public và hiển thị trùng lặp giá tiền ở panel preview

## User story
**As an** Admin
**I want** trường nhập liệu tiêu đề public trong Admin Editor lưu chính xác vào cột tieu_de của sheet Source, đồng thời Live Preview không tự động chèn thêm giá tiền vào sau tiêu đề.
**So that** tiêu đề public hiển thị khớp nhau 100% giữa các View và không bị lỗi lặp giá.

## Acceptance
- Trong Admin Editor, tiêu đề public được đọc lên từ cột E (`tieu_de`, index 4) và có fallback về cột AN (`Tiêu đề BDS`, index 39).
- Khi bấm "Lưu thay đổi", tiêu đề public được ghi lại chính xác vào cột E (`tieu_de`) và dọn sạch cột AN (`Tiêu đề BDS`).
- Khi "Lên sóng" một căn mới từ Pool:
  - Sửa toàn bộ lỗi lệch chỉ số cột Pool (từ index 54 dịch lên 1 đơn vị) để ghi đúng ID, tiêu đề, mô tả, số phòng ngủ/vệ sinh, phường cũ, phân loại hẻm và độ rộng hẻm sang Source.
  - Reset cột AN (`Tiêu đề BDS`) về rỗng mặc định.
- Live Preview và danh sách card khách hàng chỉ hiển thị chính xác tiêu đề public lấy từ cột `tieu_de`, không tự động chèn thêm giá tiền vào sau.

## Solution
- Sửa đổi các hàm `saveSourceChanges`, `saveNewListingFromPool` và `executePullFromPool` trong tệp `index.html`.
- Loại bỏ logic kiểm tra `.includes(p.gia + ' tỷ')` và nối thêm giá tiền ở Live Preview và Danh sách Card khách hàng trong `index.html`.

## Files touched
- `index.html`

## 🧠 Retro, Lessons Learned & Good Practices
- **Importing Cell in gspread v6+**: Khi viết các script Python tương tác với Google Sheets qua thư viện `gspread` mới, lớp `Cell` cần được import trực tiếp từ `gspread` thay vì `gspread.models` (gây lỗi `ModuleNotFoundError` ở gspread v6+).
- **Tránh tự động chèn giá trị (programmatic mutation)**: Hạn chế tự động chèn thêm đơn vị/giá tiền vào tiêu đề người dùng đã biên tập (nhất là kiểm tra nhạy cảm chữ hoa/thường như `Tỷ` và `tỷ`), dễ dẫn đến lặp thông tin rác. Hãy tôn trọng và hiển thị chính xác chuỗi tiêu đề người dùng đã nhập.
- **Quy trình deploy Vercel**: Vercel Serverless Function đọc file `index.html` tại runtime. Mọi chỉnh sửa ở local cần được chạy `git push` lên GitHub để Vercel tự động deploy bản mới nhất thì code mới có hiệu lực trên môi trường live.
