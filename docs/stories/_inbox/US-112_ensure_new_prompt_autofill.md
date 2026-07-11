---
id: US-112
status: accepted
date: 2026-06-29
size: S
---

# US-112: Đồng bộ siêu cấu trúc Master Prompt mới cho Tự động điền AI trên Vercel và Local

## User Story
**Với vai trò là** Admin (Biên tập viên)
**Tôi muốn** nút "Tự động điền" sử dụng cấu trúc prompt mới từ Google Doc (ID `1-VlvYmwY9_22dULAF4Xtlooa8A8VUfiV3OVU01OaoGE`) và tự động điền Tiêu đề public cũng như Mô tả public chuẩn xác theo các quy tắc mới
**Để đảm bảo** các bài đăng công khai tuân thủ đúng định dạng quảng cáo mới nhất (sử dụng dấu cộng `+` làm đầu dòng, có dòng trống phân cách sau tiêu đề phụ, và ưu tiên đúng các từ khóa CHDV/Mặt tiền ở đầu tiêu đề).

## Tiêu chí Nghiệm thu (Acceptance Criteria)
- [x] Google Doc ID mặc định được cập nhật thành `1-VlvYmwY9_22dULAF4Xtlooa8A8VUfiV3OVU01OaoGE` trong `settings.json`, `api/index.js`, và `manager.py`.
- [x] Chỉ thị định dạng JSON đầu ra (JSON suffix) gửi kèm OpenAI trong cả Node.js (`api/index.js`) và Python (`manager.py`) được đồng bộ theo chuẩn mới:
  - Dấu đầu dòng bắt đầu bằng `+` thay vì `–`.
  - Không có các ký tự in đậm `**` xung quanh nhãn trường (ví dụ: `+ Vị trí:` thay vì `– **Vị trí:**`).
- [x] Logic nối chuỗi mô tả trong `api/index.js` và `manager.py` chèn thêm một dòng trống (`\n\n`) giữa Tiêu đề phụ (🏩 ...) và nội dung mô tả bắt đầu bằng "Mô tả:".
- [x] Chạy "Tự động điền" trên giao diện Admin Vercel điền thành công Tiêu đề và Mô tả đúng định dạng mới.
- [x] Endpoint `/api/ai/generate` và hàm `call_openai_api` của Python chạy local cũng trả về kết quả khớp định dạng.

## Giải pháp (Solution)
1. **Cập nhật ID tài liệu**: Thay thế ID cũ `12LaUJ-34eolQ9ElgQhpe5k9Mh_bn4B7p31DQAZ1Ncto` thành ID mới `1-VlvYmwY9_22dULAF4Xtlooa8A8VUfiV3OVU01OaoGE`.
2. **Cập nhật JSON Suffix**:
   - Ở Node.js (`api/index.js`): Thay đổi mô tả `moTaChiTiet` trong `jsonSuffix` để hướng dẫn AI dùng dấu cộng `+`.
   - Ở Python (`manager.py`): Chuyển đổi `json_suffix` sang cấu trúc 5 trường đầu ra tương đương Node.js và thực hiện ghép chuỗi tại backend Python.
3. **Chèn dòng trống**: Đổi phép cộng chuỗi từ `+ '\n'` thành `+ '\n\n'` giữa tiêu đề phụ và mô tả chi tiết.

## 📋 Kế hoạch Triển khai (Implementation Plan)
1. Cập nhật `settings.json` với Doc ID mới.
2. Cập nhật `api/index.js` (default `docId`, `jsonSuffix`, và logic ghép `moTaRaw`).
3. Cập nhật `manager.py` (cập nhật default `prompt_google_doc_id`, đồng bộ cấu trúc `json_suffix` 5 trường, và cập nhật logic parse/ghép chuỗi ở `call_openai_api` và endpoint `/api/ai/generate`).
4. Đăng ký story mới vào `INDEX.md`.

## 📝 Nhật ký Checklist Nhiệm vụ (TODO)
- [x] **Khảo sát & Viết tài liệu:** Viết tài liệu User Story `US-112`
- [x] **Triển khai Code:** Cập nhật `settings.json`, `api/index.js`, `manager.py`
- [x] **Đồng bộ Index:** Cập nhật `INDEX.md`
- [x] **Kiểm thử & Nghiệm thu:** Chạy bộ test Playwright E2E kiểm chứng | Gọi API test trực tiếp

## Kế hoạch Xác minh

### Kiểm thử Tự động
- Chạy bộ kiểm thử E2E Playwright:
  ```powershell
  python scratch/test_e2e_curation.py
  ```

### Kiểm thử Thủ công
- Gọi API `/api/ai/generate` và kiểm tra chuỗi đầu ra hiển thị đúng dấu cộng và có dòng trống.
