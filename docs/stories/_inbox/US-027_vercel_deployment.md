---
id: US-027
status: accepted
date: 2026-05-24
size: S
---

# US-027: Di chuyển Hosting sang Vercel & Dynamic Meta Tags khi share 1 căn

## User story
**As a** Sale / PO (anh Khang)
**I want** di chuyển toàn bộ Client Web từ GitHub Pages sang hosting trên Vercel và triển khai Serverless Function để thay đổi động các thẻ meta OG
**So that** khi gửi link chia sẻ chỉ chứa duy nhất 1 căn nhà qua Zalo, khách hàng thấy ngay hình đại diện của chính ngôi nhà đó và tiêu đề cá nhân hóa trên khung Zalo Preview (miễn phí và giữ nguyên cơ chế phân biệt chế độ Admin / Khách).

## Acceptance
- [x] Di chuyển hosting Client Web sang Vercel, giữ nguyên cách phân biệt Admin / Khách bằng URL param `?pwd=trang`.
- [x] Khi share link chứa duy nhất 1 căn nhà (`?s=SYS-XXXX`), Vercel Serverless Function tự động intercept yêu cầu, cào dữ liệu từ Google Sheets, tiêm (inject) động các thẻ `<meta property="og:image">` (lấy ảnh của chính căn đó), `<meta property="og:title">` (lấy tiêu đề căn đó), và trả về mã HTML hoàn thiện cho Zalo Crawler.
- [x] Zalo Preview hiển thị chính xác ảnh và tiêu đề của căn nhà khi chia sẻ.
- [x] Dòng mô tả (description) trong Zalo Preview hiển thị Mã Khang Ngô định dạng ẩn tinh tế (Ví dụ: `#q3-10 · `) lên đầu trước các thông số kỹ thuật.

## Solution

> [!note]- Configuration
> - Cấu hình định tuyến **Vercel Routing** (`vercel.json`):
>   ```json
>   {
>     "version": 2,
>     "builds": [
>       { "src": "api/index.js", "use": "@vercel/node" }
>     ],
>     "routes": [
>       { "src": "/avatarKhangNgo.jpg", "dest": "/avatarKhangNgo.jpg" },
>       { "src": "/(.*)", "dest": "api/index.js" }
>     ]
>   }
>   ```
> - File Public Google Sheets nạp dữ liệu:
>   ID: `1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0`

> [!note]- Input
> - Lọc request chứa query parameter: `?s=SYS-XXXX` (hoặc index tạm, ID cũ).

> [!note]- Output / Format
> - HTML trả về chứa các thẻ meta được thay thế động:
>   ```html
>   <title>[Tiêu đề căn nhà thật]</title>
>   <meta property="og:title" content="[Tiêu đề căn nhà thật]" />
>   <meta property="og:description" content="#q3-10 · Diện tích: 50m², 3 tầng..." />
>   <meta property="og:image" content="https://drive.google.com/thumbnail?id=[id_anh]&sz=w800" />
>   ```

> [!note]- Key logic
> - **Cơ chế Serverless Interceptor:** 
>   Hàm `api/index.js` chặn bắt toàn bộ request. Nếu không có query `?s=...` hoặc có `?pwd=trang`, nó chỉ đọc và trả về file tĩnh `index.html` gốc ngay lập tức để giữ nguyên logic Admin/Khách ở Client.
> - **Dynamic Meta Injection:** 
>   Nếu có `?s=...`, nó fetch dữ liệu JSON từ Google Sheets API bằng Node.js, tìm dòng nhà tương ứng, dùng Regex thay thế toàn bộ tiêu đề và meta OG trong chuỗi HTML gốc của `index.html`, sau đó trả về HTML hoàn chỉnh cho Zalo/Facebook Crawler.
> - **Định dạng ẩn mã nhà:** Tự động prepend cụm `#MÃ_NHÀ · ` (Ví dụ: `#q3-10 · `) vào đầu dòng meta mô tả tinh tế để Admin lướt chat nhận diện ngay lập tức mà không gây tò mò cho khách hàng.

## Verification Plan

> [!check]- Manual Verification
> 1. Mở trang web ở chế độ Admin (`?pwd=trang`) $\rightarrow$ Xác nhận website hoạt động bình thường, đăng nhập Admin mượt mà.
> 2. Copy link chia sẻ 1 căn duy nhất (Ví dụ: `https://khangngonhapho.vercel.app/?s=SYS-001`) và dán vào cửa sổ chat Zalo $\rightarrow$ Xác nhận Zalo Preview hiển thị bong bóng chat gồm ảnh đại diện thực tế của căn nhà, tiêu đề căn nhà và mô tả bắt đầu bằng mã ẩn `#q3-01 · `.

## Files touched
- `index.html` — [Frontend HTML Template]
- `vercel.json` — [Vercel Routing Configuration]
- `package.json` — [Vercel Node.js Dependencies]
- `api/index.js` — [Vercel Serverless Function logic]
