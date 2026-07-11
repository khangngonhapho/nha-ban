---
id: US-102
status: done
date: 2026-06-21
size: S
---

# US-102: Lọc các căn chưa có raw_json_full trên Curator Dashboard

## User story
**As a** Curator / Admin (Người biên tập và quản lý dữ liệu BĐS)
**I want** có một tab "Thiếu JSON" trên Curator Dashboard (bên cạnh tab "Đã xuất bản") để lọc nhanh tất cả các căn nhà trong cơ sở dữ liệu chưa có chi tiết API thô (`raw_json_full` là rỗng hoặc NULL)
**So that** tôi có thể chủ động cào tay lại (recrawl) các căn này nhằm làm đầy dữ liệu chi tiết của chúng.

## Acceptance Criteria
- [ ] Tab **Thiếu JSON** xuất hiện tại sidebar Curator Dashboard, nằm cạnh tab **Đã xuất bản**.
- [ ] Giao diện tab có hiển thị số lượng đếm chính xác: `Thiếu JSON (Số lượng)`.
- [ ] Việc đếm số lượng và hiển thị danh sách phải quét qua toàn bộ cơ sở dữ liệu (tất cả các căn, không phụ thuộc vào trạng thái `published`, `raw_complete`, hay `raw_text` của căn đó), miễn là `raw_json_full` trống.
- [ ] Giao diện vẫn cho phép tìm kiếm và lọc nâng cao (Quận, Đường, Số nhà) bình thường khi đang mở tab **Thiếu JSON**.
- [ ] Thay đổi được đồng bộ hoàn hảo sang file `curator_html_data.py` và biên dịch EXE chạy thành công.

## Solution

> [!note]- Input
> - Lựa chọn tab `missing_raw_json` từ người dùng trên giao diện.
> - Tham số truy vấn `status=missing_raw_json` gửi về API GET `/api/listings`.

> [!note]- Output / Format
> - Danh sách các căn nhà thỏa mãn điều kiện `raw_json_full IS NULL OR raw_json_full = ''`.
> - Trường số lượng `missing_raw_json` trong đối tượng `status_counts` trả về từ API.

> [!note]- Key logic
> - **Backend (`manager.py`)**:
>   - Kiểm tra xem cột `raw_json_full` có tồn tại trong bảng trước khi truy vấn để tránh lỗi schema.
>   - Thêm điều kiện truy vấn `raw_json_full IS NULL OR raw_json_full = ''` when status equals `missing_raw_json`.
>   - Đếm và đưa số lượng vào `status_counts`.
> - **Frontend (`curator.html`)**:
>   - Thêm tab HTML và liên kết sự kiện `onclick="setSidebarStatus('missing_raw_json')"`
>   - Tinh chỉnh CSS `.sidebar-tab` (`font-size: 11px`, `padding: 12px 4px`) để sidebar chứa vừa 5 tab side-by-side.
>   - Cập nhật ánh xạ tab label để render đúng số lượng.

## Verification Plan

> [!check]- Manual Verification
> 1. Truy cập Curator Dashboard, chọn tab **Thiếu JSON**.
> 2. Xác nhận số lượng đếm hiển thị (ví dụ: `Thiếu JSON (12)`).
> 3. Click vào 1 căn bất kỳ trong danh sách, xác nhận giao diện hiển thị được chi tiết thô của nó (hoặc hiển thị trống do chưa cào thô đầy đủ).
> 4. Nhấn nút "Cào lại căn này (Đè dữ liệu)" để hệ thống cào API Thiên Khôi và bổ sung `raw_json_full`.
> 5. Xác nhận căn đó tự động biến mất khỏi tab **Thiếu JSON** (hoặc số lượng đếm giảm đi 1).
> 6. Biên dịch ứng dụng bằng `./build_exe.bat` và kiểm tra file thực thi.

## Files touched
- `manager.py` — [Python Backend]
- `curator.html` — [Frontend HTML/JS]
- `curator_html_data.py` — [Frontend Synced Data Python File]
