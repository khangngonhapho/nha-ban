---
id: US-036
status: done
date: 2026-05-27
size: S
---

# US-036: Hệ thống Cấu hình Tốc độ Cào tin & Speed Presets linh hoạt

## User story
**As an** Admin / Biên tập viên rổ hàng Khang Ngô
**I want** có các tùy chọn tốc độ cào tin khác nhau và cấu hình chi tiết độ trễ ngay trên Curator Dashboard
**So that** tôi có thể rút ngắn thời gian chờ cào tin khi cần thiết mà vẫn đảm bảo an toàn tuyệt đối chống chặn IP/Cookie của Thiên Khôi.

## Acceptance
- [x] Thiết lập 3 preset tốc độ cào tin tối ưu: An toàn (8-15s / 20-40s), Tối ưu (3-6s / 5-10s) và Siêu tốc (1.5-3s / 3-5s).
- [x] Cho phép chọn nhanh preset thông qua ô dropdown trực quan ở Tab 1.
- [x] Thêm 4 ô nhập số chi tiết (delay_house_min/max, delay_page_min/max) ở panel cấu hình bên phải để người dùng tự do tinh chỉnh sâu.
- [x] Tự động chuyển preset về "Tùy chỉnh" khi người dùng tự tay sửa các ô số độ trễ.
- [x] Tự động lưu cấu hình độ trễ mới vào tệp cấu hình cục bộ `curator_config.json`.
- [x] Log terminal cào ngầm tự động nhận dạng và áp dụng chính xác độ trễ cấu hình thời gian thực.
- [x] Sửa đổi lỗi đóng băng log terminal trên curator UI khi lượng log đạt mốc giới hạn 1000 dòng.
- [x] Thiết kế cổng API chuyên dụng `/api/cookie/save` nguyên tử độc lập giải quyết lỗi lưu Cookie thất bại khi luồng ngầm đang chạy bận GIL.
- [x] Vá lỗi Cảnh báo Hết hạn Cookie lặp vô tận (Infinite Alert Loop) khi dán Cookie mới bằng cách tự động dọn dẹp bộ đệm logs cục bộ trên cả máy chủ (server buffer) và trình duyệt ngay khi lưu thành công.

## Solution

> [!note]- Configuration
> ```json
> {
>   "delay_house_min": 3.0,
>   "delay_house_max": 6.0,
>   "delay_page_min": 5.0,
>   "delay_page_max": 10.0
> }
> ```

> [!note]- Input
> Payload lưu cấu hình hệ thống POST `/api/config`:
> ```json
> {
>   "delay_house_min": "number",
>   "delay_house_max": "number",
>   "delay_page_min": "number",
>   "delay_page_max": "number"
> }
> ```

> [note]- Key logic
> 1. **Duy trì Fallback an toàn:** Nếu tệp cấu hình `curator_config.json` trống hoặc lỗi, crawler tự động fallback về khoảng nghỉ tàng hình mặc định cũ (An toàn - 8s đến 15s giữa các căn) để bảo vệ tài khoản.
> 2. **Sleep ngắt quãng chống treo:** Khoảng nghỉ giữa các căn sử dụng hàm `sleep_interruptible(seconds)` bẻ nhỏ thời gian ngủ (bước 100ms) giúp hệ thống phản hồi lệnh ngắt luồng `STOP_REQUESTED` ngay lập tức mà không phải chờ hết cả chuỗi giây nghỉ dài.
> 3. **Giải pháp vá đóng băng log UI:** Thay đổi từ kiểm tra độ dài mảng (`lines.length !== currentLineCount`) sang kiểm tra chữ ký chuỗi joined log (`lines.join('\n') !== lastLogsSignature`) để phát hiện chính xác mọi thay đổi kể cả khi bộ đệm log 1000 dòng trên máy chủ bị dịch chuyển/cắt bớt.
> 4. **Cơ chế Giải quyết Vòng lặp Hết hạn Cookie (Cookie Alert Loop Buster):**
>    * **Nguyên nhân:** Khi Cookie cào bị hết hạn, server ghi dòng log chứa chữ `"hết hạn"` vào bộ đệm `LOGS_BUFFER`. Trên trình duyệt, hàm `fetchLogs()` định kỳ 2 giây đọc bộ đệm này, hễ thấy có chữ `"hết hạn"` là tự động báo động và mở bung modal dán Cookie. Dù người dùng dán Cookie mới thành công và reset cờ cảnh báo, nhưng vì bộ đệm log cũ trên server vẫn còn lưu các dòng log `"hết hạn"` trong quá khứ, cuộc gọi polling 2 giây tiếp theo lại đọc trúng log cũ và tiếp tục kích hoạt báo động sai, khóa chặt người dùng trong modal.
>    * **Giải pháp:**
>      - *Máy chủ (Flask):* Khi lưu Cookie thành công (API `/api/cookie/save` và API `/api/crawl` dạng lưu cookie), máy chủ sẽ lập tức dọn sạch bộ đệm logs hệ thống bằng lệnh `LOGS_BUFFER.clear()`.
>      - *Giao diện (Frontend):* Hàm `saveCookieCache()` sau khi nhận phản hồi lưu thành công sẽ gán `lastLogsSignature = ""` và dọn sạch hiển thị log hiện tại trên DOM để sẵn sàng nhận luồng logs mới từ đầu, triệt tiêu hoàn toàn lỗi lặp cảnh báo.

## Verification Plan

### Manual Verification
1. Mở giao diện Curator, thay đổi dropdown preset sang **Siêu tốc** và kiểm tra 4 ô số bên phải tự nhảy về min/max 1.5s-3s / 3s-5s.
2. Thử sửa ô số nghỉ căn lên 5.5s, dropdown tự động chuyển sang **Tùy chỉnh**.
3. Bấm **Bắt đầu cào tin**, kiểm tra log console trên Web UI cuộn liên tục mượt mà qua các trang và áp dụng chính xác độ trễ mới.
4. Bấm **Lưu Cookie** lúc luồng đang chạy để xác nhận Cookie được cập nhật ngay lập tức xuống tệp tin cục bộ và dừng luồng cũ thành công dưới 10ms.
5. Giả lập cào báo lỗi hết hạn Cookie (xuất hiện modal cập nhật). Tiến hành dán Cookie mới và nhấn Lưu:
   - Xác nhận thông báo lưu thành công và modal đóng lại ngay lập tức.
   - Xác nhận cảnh báo báo động hết hạn **KHÔNG** bị nhảy lại lần thứ 2, luồng cào mới bắt đầu từ trang cấu hình chạy mượt mà không bị ngắt quãng.

## Files touched
- `curator.html` — Tích hợp các trường chọn preset, ô nhập số độ trễ, logic JS đồng bộ và bản vá đóng băng log/lưu cookie, dọn log signature khi dán cookie mới.
- `curator_server.py` — Tích hợp API chuyên trách `/api/cookie/save`, default cấu hình độ trễ tối ưu, bổ sung dọn logs buffer khi ghi cookie mới thành công.
- `crawl_pipeline.py` — Nạp cấu hình độ trễ động từ file json và áp dụng vào chu kỳ cào tin.
- `curator_html_data.py` — Đồng bộ hóa Web UI.
