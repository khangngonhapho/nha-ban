---
id: US-116
status: accepted
date: 2026-06-30
size: M
---

# US-116: Reset CSDL và Tái sử dụng Hình ảnh R2 cũ (Clean Database Reset & R2 Image Reuse)

## User Story
**As an** Admin / Product Owner
**I want** to perform a clean database reset on Google Sheets (Pool & Source) and SQLite to fix row mismatch issues
**And** automatically extract true image mappings directly from the filenames of R2 URLs on Google Sheets to avoid downloading and re-uploading existing images
**And** regenerate all `System_ID`, `Ma_Khang_Ngo_ID`, public titles, and public descriptions completely fresh
**So that** I have a 100% consistent database while preserving all my custom/R2 photos on Cloudflare.

## Acceptance Criteria
- [ ] Xóa sạch nội dung dòng trên tab `Pool` của sheet Pool bắt đầu từ **dòng 2** (giữ nguyên tiêu đề dòng 1).
- [ ] Xóa sạch nội dung dòng trên tab `Source` của sheet Source bắt đầu từ **dòng 3** (giữ nguyên tiêu đề và ghi chú dòng 1-2).
- [ ] Xóa file CSDL `raw_archive.db` cục bộ để chuẩn bị cào mới từ đầu.
- [ ] Quét trực tiếp tab `Pool` trên Google Sheets để trích xuất bản đồ ảnh R2 `{tk_id: {stt: R2_URL}}` dựa trên tên file trong URL R2, bỏ qua cột `tk_id` hay thông tin cùng dòng bị lệch.
- [ ] **KHÔNG** khôi phục hay sử dụng lại các mã `System_ID`, `Ma_Khang_Ngo_ID` cũ cũng như các mô tả/tiêu đề tự viết cũ.
- [ ] Khi lưu dữ liệu mới cào, nếu `tk_id` khớp với bản đồ ảnh R2, tự động gán lại các R2 URL tương ứng theo thứ tự mà không cần upload lại.

## 📋 Implementation Plan
- **Các bước triển khai:**
  1. Tạo file câu chuyện US-116 (tệp này).
  2. Viết script `backup_and_map_curation.py` để quét Sheets tab `Pool`, bóc tách ảnh R2 theo tên file và xuất ra `scratch/r2_images_by_tk_id.json`.
  3. Viết script `wipe_local_and_sheets.py` để clear sạch dữ liệu dòng trên 2 sheets (Pool: dòng 2+, Source: dòng 3+) và CSDL local.
  4. Người dùng tiến hành chạy cào lại toàn bộ tin sạch từ đầu.
  5. Cập nhật `pool_lego.py` để tự động tra cứu `scratch/r2_images_by_tk_id.json` khi lưu tin mới cào, gán lại link R2 cũ trực tiếp.
  6. Chạy Playwright E2E để nghiệm thu toàn hệ thống.

## 📝 Task Checklist (TODO)
- [x] **Khảo sát & Viết tài liệu:** Tạo file câu chuyện US-116 (Đã xong)
- [ ] **Sao lưu hình ảnh:** Tạo bản đồ ảnh R2 từ URL Sheets trong `scratch/r2_images_by_tk_id.json`
- [ ] **Dọn dẹp hệ thống:** Clear dòng trên Google Sheets (Pool: dòng 2+, Source: dòng 3+) và SQLite
- [ ] **Cập nhật Cập nhật Lưu trữ:** Cấu hình `pool_lego.py` để tự động gán lại ảnh R2 cũ theo `tk_id`
- [ ] **Cào mới & Đồng bộ:** Chờ người dùng cào mới dữ liệu và tự động sinh mới ID cũng như gán lại link R2 cũ không cần upload lại
- [ ] **Kiểm thử & Nghiệm thu:** Chạy Playwright E2E test và nghiệm thu thực tế

## Verification Plan

### Automated Tests
- Chạy toàn bộ bộ test suite Playwright E2E:
  ```powershell
  python scratch/run_all_e2e.py
  ```

### Manual Verification
1. Kiểm tra file `scratch/r2_images_by_tk_id.json` đảm bảo bản đồ ảnh R2 chứa đúng cấu trúc `tk_id` bóc tách từ URL và thứ tự ảnh.
2. Xác minh Google Sheets đã trống dữ liệu sau khi wipe nhưng vẫn giữ nguyên header (dòng 1 trên Pool, dòng 1-2 trên Source).
3. Xác minh các căn cào mới có `System_ID` và `Ma_Khang_Ngo_ID` được sinh mới hoàn toàn sạch sẽ.
4. Xác minh ảnh R2 cũ được gán tự động vào đúng căn nhà theo đúng thứ tự ảnh.
