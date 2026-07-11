---
id: US-131
status: accepted
date: 2026-07-10
size: M
---

# US-131: Khắc phục lệch ảnh khi cào lại và phân giải Images_Admin_JSON trên Web Vercel Admin

## User story
**As an** Admin
**I want** hiển thị toàn bộ ảnh phân giải từ Images_Admin_JSON không giới hạn số lượng và đồng bộ tương ứng sang Ảnh 1-25 khi cào lại
**So that** giao diện biên tập Admin trên Web Vercel hiển thị đầy đủ tất cả hình ảnh để dễ dàng quản lý nhãn và trạng thái ẩn hiện.

## Logic hiện tại liên quan
- **[DF-003] Luồng Dữ Liệu Cào & Nhập Kho Tin Thô v1**: Nhận dữ liệu cào và lưu SQLite, bảo vệ cột chất xám.
- **[DF-004] Luồng Dữ Liệu Di Cư Ảnh & Tối Ưu Hóa R2 v2**: Trộn ảnh thông minh (Smart Merge) và cập nhật cột `Images_Admin_JSON`.
- **[DF-001] Luồng Dữ Liệu Biên Tập & Xuất Bản v2**: Đồng bộ dữ liệu lên tab Pool Google Sheets.
- Yêu cầu này **BỔ SUNG** và **XÁC NHẬN** logic hiện tại: Cập nhật song song cả `Images_Admin_JSON` và `Ảnh 1-25` ở backend, phân giải động và hiển thị không giới hạn danh sách ảnh từ `Images_Admin_JSON` ở client.

## Acceptance
- [x] Khi cào lại hoặc di cư ảnh, các cột phẳng `Ảnh 1` đến `Ảnh 25` của SQLite/Google Sheets được điền đầy đủ URL tương ứng từ danh sách ảnh mới nhất.
- [x] Giao diện Web Vercel Admin (vai trò Admin) phân giải thành công dữ liệu từ `Images_Admin_JSON` thành `curated_config` và hiển thị toàn bộ hình ảnh không giới hạn số lượng (hiển thị đầy đủ tất cả các hình có trong `Images_Admin_JSON` của căn `ZWBINHIBVH` trong curation panel cho cả tin đã duyệt và tin thô trong Pool).

## Solution

### Configuration
*Không sử dụng các cấu hình biến môi trường mới.*

### Key logic
1. Trong `manager.py`, khi kết thúc di cư ảnh cho bảng `listings`, hệ thống không còn skip việc cập nhật các cột phẳng `Ảnh 1-25` vào SQLite.
2. Trong `lego_core.js`, bổ sung parsing cột `Images_Admin_JSON` (đầu vào là chỉ số cột động `window.getPoolColumnIndex("Images_Admin_JSON", 94)`) thành `tempCuratedConfig` và gán vào `p.curated_config` ở cả matched loop và unmatched loop.
3. Trong `lego_detail_admin.js`, hàm `window.openPoolS` dùng để mở tin thô chưa duyệt (Pool row) cần bổ sung phân giải `Images_Admin_JSON` sang `curated_config` và `p.imgs` sử dụng các chỉ số cột động (`window.getPoolColumnIndex`) thay vì hardcode đọc từ cột phẳng `Ảnh 1-25`.

## 📋 Implementation Plan
- **Cách tiếp cận:**
  1. Loại bỏ bộ lọc `image_fields_to_skip` trong hàm `run_image_migration_thread` ở `manager.py` cho bảng `listings` để ghi nhận các cột ảnh phẳng vào SQLite.
  2. Cập nhật chỉ số fallback và thêm đoạn logic parsing `Images_Admin_JSON` trong `lego_core.js`.
  3. Bổ sung logic phân giải `Images_Admin_JSON` và chuyển đổi cột index động trong `openPoolS()` của `static/js/lego_detail_admin.js`.
  4. Cập nhật cache-buster.
- **Các bước triển khai dự kiến:**
  1. Thay đổi logic ghi database trong `manager.py`. (Đã xong)
  2. Thay đổi logic parsing trong `static/js/lego_core.js`. (Đã xong)
  3. Thay đổi logic trong `static/js/lego_detail_admin.js` và `static/js/lego_helpers.js`. (Đã xong)
  4. Cập nhật cache-buster. (Đã xong)

## Truth Cards bị ảnh hưởng
- **DF-004 v2**: Cập nhật logic di cư ảnh, Smart Merge, khôi phục ảnh cũ, và phân giải hiển thị ở cả backend & frontend.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:** [x] Khảo sát code cũ | [x] Chốt giải pháp
- [x] **Triển khai Code:** [x] Code logic ghi ảnh phẳng (`manager.py`) | [x] Code logic parsing client (`lego_core.js`, `lego_helpers.js`) | [x] Code logic parsing trong openPoolS (`lego_detail_admin.js`) | [x] Cập nhật cache-buster
- [x] **Kiểm thử sơ bộ:** [x] Chạy các ca test E2E/EVAL | [x] Nghiệm thu cùng PO

## 🛠️ Update Logic (Drafting while Doing)
1. **Sửa đổi manager.py**:
   - Trực tiếp chuyển các ảnh không phải sơ đồ/hẻm vào `flat_anh` (tương ứng `Ảnh 1-25`), kể cả các ảnh có vai trò `deleted` hay `hidden` để đồng bộ 100% thứ tự với `Images_Admin_JSON`.
   - Ghi nhận `clean_sodo1-5` từ `flat_sodo`.
   - Ghi nhận `flat_hem` từ `Images_Admin_JSON`.
2. **Sửa đổi lego_core.js**:
   - Parse `Images_Admin_JSON` ở matched/unmatched loop, và gán vào `p.curated_config`.
   - Đối với admin (`window.isAdmin === true`), cho phép `poolImgs` giữ toàn bộ ảnh (kể cả deleted/hidden) để render ra curation thumbnail strip.
3. **Sửa đổi lego_detail_admin.js**:
   - Cập nhật hàm `openPoolS()` để tìm và parse cột `Images_Admin_JSON` sang `curated_config` của listing thô, gộp các ảnh vào `p.imgs` để hiển thị đầy đủ hình ảnh.

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)

### 1. Nhật ký Sự cố & Tiến trình Retro (Incident & Retro Log)
- **Sự cố phát sinh**: Khi cào lại, các cột ảnh phẳng `Ảnh 1-25` trống rỗng mặc dù `Images_Admin_JSON` chứa đầy đủ 16 ảnh, đồng thời giao diện Admin hiển thị thiếu ảnh.
- **Nguyên nhân gốc rễ (Root Cause)**: 
  - Backend bỏ qua (skip) việc cập nhật các cột ảnh phẳng để tối ưu, trong khi Frontend không hề có logic phân giải `Images_Admin_JSON` sang `curated_config` khi tải dữ liệu từ Google Sheets.
  - Sau khi sửa ở `lego_core.js`, Admin vẫn thấy thiếu ảnh khi chọn biên tập tin thô chưa duyệt (Pool) vì hàm `openPoolS()` trong `lego_detail_admin.js` khi khởi tạo dữ liệu tạm từ Pool chỉ đọc các cột ảnh phẳng cũ mà không đọc cột `Images_Admin_JSON`.
- **Giải pháp phòng ngừa**: Duy trì cập nhật song song cả cột phẳng và cột JSON, và đảm bảo mọi dữ liệu dạng JSON lưu trên Google Sheets được phân giải đúng chỉ số cột động phía client cho cả tin đã duyệt và tin chưa duyệt.

### 2. Thực tiễn tốt đúc kết (Good Practices)
- **Đồng bộ cột phẳng và cột JSON**: Khi chuyển đổi kiến trúc từ phẳng sang JSON, luôn giữ tính tương thích ngược bằng cách đồng bộ song song ở backend cho đến khi hoàn thành chuyển đổi hoàn toàn.

## Verification Plan

### Automated Tests
- Chạy toàn bộ suite test:
  ```bash
  python -m pytest tests/
  ```

### Manual Verification
- Đã chạy thử nghiệm di cư ảnh cục bộ trên căn `427f3f55-85a4-4806-b539-d00368c7b17d` (Mã hàng `TK84K4WO`), kết quả các cột phẳng `Anh_1` đến `Anh_16` được điền đầy đủ và đẩy lên Google Sheets chính xác.
- Đã kiểm tra logic parse `Images_Admin_JSON` chạy đúng định dạng trên node.js.

## Files touched
- `manager.py` — Triển khai ghi đè các cột ảnh phẳng vào SQLite.
- `static/js/lego_core.js` — Triển khai parsing `Images_Admin_JSON` sang `curated_config`.
- `static/js/lego_detail_admin.js` — Bổ sung phân giải `Images_Admin_JSON` trong `openPoolS()`.
- `index.html` — Cập nhật cache-buster.
- `sw.js` — Cập nhật phiên bản cache PWA.
