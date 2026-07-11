---
id: US-078
status: accepted
date: 2026-06-08
size: M
---

# US-078: Tích hợp nút Tự động điền AI trong Pool và bảo mật số nhà trên Vercel Admin

## User story
**As an** Admin / Broker Khang Ngô
**I want** nút "⚡ Tự động điền" (Curation Auto-fill) ở giao diện Admin hoạt động mượt mà, sử dụng AI (GPT-4o-mini) để tự động sinh Tiêu đề chính, Tiêu đề phụ, Mô tả chi tiết và Phường cũ dựa trên dữ liệu thô của Pool listings kết hợp với Master Prompt Trà Mi tải động từ Google Doc, đồng thời tự động loại bỏ số nhà cụ thể và ký tự markdown khỏi kết quả.
**So that** tôi có thể biên tập và lên sóng giỏ hàng nhanh chóng, đúng văn phong Trà Mi chuyên nghiệp mà không lo bị lộ địa chỉ số nhà ra bên ngoài.

## Acceptance
- [x] **Tự động điền AI hoạt động ổn định:** Nút "⚡ Tự động điền" gửi request lên backend Vercel `/api/ai/generate` thành công mà không gặp lỗi API Key hay phân quyền.
- [x] **Tải Prompt động từ Google Doc:** Backend lấy prompt động từ Google Doc ID (`1-VlvYmwY9_22dULAF4Xtlooa8A8VUfiV3OVU01OaoGE`) thông qua Service Account credentials để có đầy đủ quyền đọc Drive.
- [x] **Cấu trúc Mô tả đầy đủ Tiêu đề phụ 🏩:** Phần mô tả public sinh ra phải bắt đầu bằng Tiêu đề phụ (Mục 2) viết hoa toàn bộ và có biểu tượng 🏩, tiếp nối ngay bên dưới là Mô tả chi tiết (Mục 3) và Góc nhìn đầu tư (Mục 4) nếu thỏa mãn điều kiện.
- [x] **Bảo mật địa chỉ số nhà tuyệt đối:** Không lọt số nhà cụ thể (ví dụ: "63") hoặc số hẻm cụ thể vào Tiêu đề chính, Tiêu đề phụ hay Mô tả.
- [x] **Loại bỏ ký tự markdown:** Không chứa các dấu in đậm markdown `**` trong kết quả cuối cùng điền vào form.
- [x] **Xử lý lỗi (Fallback) mượt mà:** Nếu API gặp sự cố, hiện thông báo Toast màu vàng và điền template tĩnh cũ để tránh đơ giao diện.
- [x] **Đồng bộ phường cũ:** Ghi nhận và chuyển thông tin phường cũ (`phuong_cu`) sang cột AF của Source sheet khi lên sóng hoặc lưu hàng.

## Solution

### 1. Phân tách Cấu trúc JSON Output của AI (api/index.js)
Để tránh OpenAI (gpt-4o-mini) gộp chung và bỏ quên mục 2 (Tiêu đề phụ 🏩), chúng ta chia nhỏ schema JSON định dạng đầu ra của AI:
```json
{
  "tieuDeChinh": "Tiêu đề public chính (viết theo hướng dẫn của Mục 1 thuộc Bước 3)",
  "tieuDePhu": "Tiêu đề phụ public (bắt buộc viết hoa toàn bộ, bắt đầu bằng biểu tượng 🏩, viết theo hướng dẫn của Mục 2 thuộc Bước 3)",
  "moTaChiTiet": "Mô tả chi tiết (bắt đầu bằng chữ 'Mô tả:', tiếp nối ngay bên dưới là các dòng con bắt đầu bằng dấu gạch bạt dài '–' theo hướng dẫn của Mục 3 thuộc Bước 3)",
  "gocNhinDauTu": "Góc nhìn đầu tư (bắt đầu bằng dòng tiêu đề viết hoa toàn bộ 'GÓC NHÌN ĐẦU TƯ...' sau đó là các dòng con bắt đầu bằng dấu chấm tròn nhỏ '•' theo hướng dẫn của Mục 4 thuộc Bước 3. Để trống nếu không thỏa mãn bộ lọc điều kiện)",
  "phuongCu": "Tên phường cũ (nếu có sáp nhập phường, hoặc để trống)"
}
```

### 2. Ghép chuỗi và Làm sạch Markdown ở Backend (api/index.js)
Sau khi parse JSON kết quả từ AI, backend sẽ làm sạch các ký tự markdown `**` và thực hiện ghép nối các trường thành mô tả public hoàn chỉnh:
```javascript
let moTaRaw = '';
if (tieuDePhuClean) {
  moTaRaw += tieuDePhuClean.trim() + '\n';
}
if (moTaChiTietClean) {
  moTaRaw += moTaChiTietClean.trim();
}
if (gocNhinDauTuClean && gocNhinDauTuClean.trim()) {
  let gnd = gocNhinDauTuClean.trim();
  if (!gnd.startsWith('---')) {
    moTaRaw += '\n---\n';
  } else {
    moTaRaw += '\n';
  }
  moTaRaw += gnd;
}
const moTaClean = moTaRaw ? String(moTaRaw).replace(/\*\*/g, '') : '';
```

### 3. Quy tắc Bảo mật Số nhà trong User Prompt
Tự động lấy số nhà động (`body.soNha`, ví dụ `"63"`) gửi kèm theo chỉ dẫn cảnh báo bảo mật nghiêm ngặt (`🚨 QUY TẮC BẢO MẬT ĐỊA CHỈ`) vào cuối User Prompt, bắt buộc AI so khớp và loại bỏ số nhà cụ thể này khỏi Tiêu đề chính, Tiêu đề phụ, và Mô tả.

### 4. Tích hợp Phía Client (index.html)
Triển khai hàm `window.autoFillCurationDetails` để thu thập dữ liệu thô của căn nhà từ Pool, gọi API `/api/ai/generate` và tự động cập nhật các thẻ `textarea` trong form Curation. Đồng thời cập nhật các hàm `executePublishListing` và `executePullFromPool` để lấy phường cũ điền vào sheet.

## 📋 Implementation Plan
- **Backend API**: Xây dựng endpoint `/api/ai/generate` trong file `api/index.js`, tích hợp gọi OpenAI GPT-4o-mini và lấy credentials của Google Service Account để tải prompt động.
- **AI Prompt Tuning**: Thiết lập cấu trúc JSON đầu ra chi tiết và cơ chế cảnh báo bảo mật số nhà động.
- **Client Integration**: Tích hợp nút bấm, xử lý giao diện chờ, gán dữ liệu và xử lý lỗi fallback trên file `index.html`.
- **Git Deployment**: Push toàn bộ lên GitHub nhánh `main` để Vercel tự động build & deploy.

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh 1 (Mất Tiêu đề phụ):** Khi yêu cầu AI trả về một trường `moTa` chứa cả Tiêu đề phụ, Mô tả chi tiết và Góc nhìn đầu tư, AI thường bỏ qua Tiêu đề phụ (Mục 2) và viết thẳng vào phần Mô tả chi tiết.
  - *Giải pháp:* Thiết lập schema JSON phân tách rõ ràng các trường và thực hiện ghép nối chuỗi một cách tường minh tại backend.
- **Sự cố phát sinh 2 (Lộ số nhà trong Tiêu đề):** AI lầm tưởng số nhà trong input địa chỉ là một phần của tên đường (Ví dụ: "63 đường 6D" thay vì "đường 6D"), dẫn đến lộ số nhà.
  - *Giải pháp:* Lấy số nhà động và chèn chỉ dẫn bảo mật `🚨 QUY TẮC BẢO MẬT ĐỊA CHỈ` trực tiếp trong User Prompt để cảnh báo và hướng dẫn AI cách loại bỏ số nhà cụ thể trước khi viết bài.

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Thiết kế Prompt**: Khi muốn AI trả về cấu trúc gồm nhiều phần phức tạp, việc chia nhỏ chúng thành các key JSON riêng biệt là lựa chọn thông minh và có độ tin cậy cao hơn hẳn việc chỉ dẫn AI tự gộp vào một trường văn bản lớn.
- **Bảo mật PII / Thông tin nhạy cảm**: Cung cấp ví dụ cụ thể về số nhà cần loại bỏ trong User Prompt giúp mô hình LLM hiểu sâu sắc và thực thi quy tắc lọc địa chỉ chính xác hơn nhiều so với việc chỉ ghi quy tắc chung trong System Prompt.

## Verification Plan

### Manual Verification
- **Kiểm tra UI**: Tải trang Admin, bấm nút "⚡ Tự động điền" trên căn nhà thuộc Pool.
- **Xác nhận cấu trúc**:
  - Tiêu đề public chính xác, không chứa số nhà.
  - Mô tả bắt đầu bằng Tiêu đề phụ viết hoa toàn bộ và có biểu tượng `🏩` ở đầu.
  - Tiếp nối ngay dưới là chữ `Mô tả:` và các dòng thông số phân tách bằng dấu gạch bạt `–`.
  - Không có ký tự in đậm markdown `**`.
- **Xác nhận lưu phường cũ**: Kiểm tra Source sheet cột AF có chứa phường cũ sau khi lên sóng thành công.

## Files touched
- [api/index.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/api/index.js) — Thêm endpoint AI, tinh chỉnh JSON output, ghép nối mô tả và chặn lộ số nhà.
- [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html) — Thêm nút tự động điền, tích hợp client-side API call và lưu phường cũ.
