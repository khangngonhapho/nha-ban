---
id: US-092
status: accepted
date: 2026-06-13
size: S
replaces: none
---

# US-092: Sửa lỗi Internal Server Error: Missing index.html khi truy cập trang chủ trên Vercel

## User story
**As an** Admin / Người dùng  
**I want** khắc phục triệt để lỗi `Internal Server Error: Missing index.html` khi truy cập trang chủ của Vercel App hoặc các link chia sẻ  
**So that** khách hàng và admin luôn mở được trang web bình thường và không gặp màn hình lỗi trắng hoặc báo lỗi máy chủ từ Vercel.

## Acceptance Criteria
- [x] **Sửa lỗi tìm tệp index.html**:
  - Khi deploy lên Vercel, hàm serverless `/api/index.js` phải đọc thành công nội dung tệp `index.html`.
  - Hỗ trợ đa lớp fallback đường dẫn (đường dẫn tương đối so với file api sử dụng `__dirname` và `process.cwd()`).
- [x] **Bảo đảm đóng gói đầy đủ (Static Bundling)**:
  - Cấu hình `vercel.json` để builder của Vercel chủ động gom tệp `index.html` vào gói phân phối của hàm serverless `/api/index.js`.
- [x] **Kiểm tra hoạt động thực tế**:
  - Truy cập trang chủ `/` trả về mã trạng thái `200` cùng mã HTML hoàn chỉnh.
  - Các đường link chia sẻ có query `s` hoặc `c` vẫn hoạt động tốt, inject meta tags động bình thường.

## Solution

### 1. Nguyên nhân gốc rễ (Root Cause)
*   **Vercel Serverless Isolation:** Trên Vercel, các tệp script trong thư mục `api/` được biên dịch độc lập thành các AWS Lambda function (hoặc môi trường tương đương). 
*   **Thiếu tệp tĩnh ở Runtime:** Khi `/api/index.js` chạy, lệnh `process.cwd()` trả về thư mục gốc của lambda execution, nhưng các tệp tĩnh như `index.html` không tự động được sao chép vào thư mục này nếu Vercel NFT (Node File Trace) không phân tích được sự phụ thuộc.
*   **Không dùng __dirname:** NFT chỉ phân tích được các liên kết dạng tĩnh sử dụng `__dirname` như `path.join(__dirname, '../index.html')`. Code cũ chỉ dùng `path.join(process.cwd(), 'index.html')`, khiến Vercel bỏ qua `index.html` khi bundle function.

### 2. Thiết kế giải pháp kỹ thuật
*   **Multi-path Fallback:** Trong `api/index.js`, thực hiện đọc thử tệp ở 3 vị trí:
    1. `path.join(__dirname, '..', 'index.html')` (Để Vercel NFT bắt được sự phụ thuộc).
    2. `path.join(process.cwd(), 'index.html')` (Duy trì tính tương thích chạy local).
    3. `path.join(__dirname, 'index.html')` (Tránh lỗi nếu cấu trúc build thay đổi).
*   **Explicit inclusion in vercel.json:** Bổ sung cấu hình `config.includeFiles` để chỉ thị Vercel copy chính xác tệp `index.html` vào bundle.

---

## 📋 Proposed Changes

### 1. Cấu hình Deploy (`vercel.json`)
#### [MODIFY] [vercel.json](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/vercel.json)
* Cấu hình builder `@vercel/node` include file `index.html`.

### 2. File Routing Serverless (`api/index.js`)
#### [MODIFY] [api/index.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/api/index.js)
* Cải tiến đoạn đọc file `index.html` sử dụng mảng đường dẫn fallback và `fs.existsSync`.

---

## 🔍 Verification Plan

### Manual Verification
* Deploy nháp hoặc chạy thử local:
  - Mở trang chủ.
  - Mở trang chia sẻ (ví dụ `/?s=SYS-1`).
  - Đảm bảo HTML load thành công không có lỗi `Internal Server Error: Missing index.html`.

---

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Sự cố xảy ra (Incidents) & Nguyên nhân gốc rễ (Root Cause)
- **Sự cố:** Xảy ra lỗi `Internal Server Error: Missing index.html` khi truy cập trang chủ ngay sau khi hoàn thành deploy US-090.
- **Nguyên nhân gốc rễ:** Việc phình to dung lượng thư mục dự án do các file SQLite sao lưu (`raw_archive.db` ~ 40MB) khiến trình đóng gói của Vercel tối ưu hóa nghiêm ngặt dung lượng serverless zip. Các tệp tĩnh được đọc bằng lệnh động `process.cwd()` (như `index.html`) bị Vercel NFT loại bỏ hoàn toàn, gây thiếu tệp ở runtime.

### 2. Thực tiễn tốt rút ra (Good Practices)
- Khởi tạo thực tiễn tốt **GP-013**: Đối với tệp tĩnh cần thiết trong môi trường serverless Node.js, bắt buộc sử dụng mảng đường dẫn fallback chứa `__dirname` tương đối tĩnh và cấu hình tường minh `includeFiles` trong `vercel.json`.

