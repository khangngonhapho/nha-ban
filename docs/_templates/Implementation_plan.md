---
us_id: US-XXX
status: in-progress
started: YYYY-MM-DD
---

> [!info]- 📋 Hướng dẫn dùng template này
> **Khi nào dùng**: Size M trở lên, hoặc task có >3 files, hoặc task qua nhiều phiên
> **Khi nào KHÔNG dùng**: Size S, task xong trong 1 phiên <30 phút
> **Lifecycle**: Tạo khi bắt đầu → update liên tục → archive/xoá khi US done
> **Khác US**: File này là "how to build", US là "what to build & why"
> ⚠️ Xoá callout này trong file thật

# Implementation Plan: US-XXX [Tên ngắn]

## Scope
- **US**: [[US-XXX_slug]]
- **Files sẽ tạo/sửa**:
  - `[NEW]` `path/file.ext` — role
  - `[MODIFY]` `path/file.ext` — thay đổi gì

## Checklist

### Phase 1: [Tên phase]
- [ ] [Step cụ thể — đủ chi tiết để resume sau restart]
- [ ] [Step 2]

### Phase 2: [Tên phase]
- [ ] [Step]

### Phase 3: Verification & Deployment (Bắt buộc)
- [ ] Chạy kiểm thử tự động E2E: `python verify_build.py` (hoặc `python scratch/run_all_e2e.py`) để chắc chắn toàn bộ test suite pass 100%.
- [ ] Thực hiện Git Commit (Pre-commit hook sẽ chạy lại E2E & tự động tăng số phiên bản `?v=...` trong `index.html`).
- [ ] Thực hiện Git Push lên nhánh `main` để Vercel tự động build và deploy.
- [ ] Truy cập đường dẫn Live Vercel (sử dụng chế độ ẩn danh hoặc xóa cache) để kiểm tra và xác minh trực quan kết quả cuối cùng.

## Decisions log
- [YYYY-MM-DD]: [Quyết định] — [Lý do ngắn]

## Blockers
- [ ] [Blocker nếu có — xoá section nếu không có]

## Resume checkpoint
> Đang ở: [Phase X / Step Y]
> Files đã touch: [list]
> Cần làm tiếp: [next step]