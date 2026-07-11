1. Đồng ý về cấu trúc folder.
2. Đồng ý về cách lấy link ảnh theo cách B
3. Ẩn thông tin địa chỉ thật, thông tin mô tả thật, tạo mã nhà giả. Dùng mã này làm mã căn trong hệ thống quản lý. Thông tin mô tả giả sẽ được viết lại (thay tên đường thật bằng các con đường chính lớn ở gần).
4. Gợi ý cách nhập liệu, có phân tích đánh đổi chi phí, thời gian, tính bền vững



Có 5 cách nhập liệu khả thi cho workflow của Trang. Tôi phân tích thẳng từng cái rồi recommend cuối bài.

## So sánh tổng hợp

|Cách nhập liệu|Chi phí/tháng|Setup|Time/căn|Bền vững|Bàn giao được?|
|---|---|---|---|---|---|
|**A.** Chat với AI ở Cowork (hiện tại)|$0 (đã có Claude)|1-2 giờ|2-4 phút|Trung bình|Khó|
|**B.** Web App tự build (Apps Script + Claude API)|$5-15|1-2 ngày|1-2 phút|**Cao**|Dễ|
|**C.** Google Form + Apps Script ngầm|$0|4-6 giờ|4-6 phút|Cao|Dễ|
|**D.** No-code (Make/n8n/Zapier)|$9-29|4-8 giờ|1-3 phút|Trung bình|Trung bình|
|**E.** Telegram bot + Claude API|$5-15|2-3 ngày|**30 giây**|Cao|Trung bình|

## Phân tích từng cách

**A. Chat với AI ở Cowork** — đơn giản nhất, dùng ngay được. Trang paste text + drag hình vào chat, tôi gọi MCP Google để ghi Sheet + upload Drive. Đánh đổi: phải mở Cowork, copy-paste mỗi lần, prompt phải nhất quán, khó cho cộng tác viên sau này. Phù hợp cho **giai đoạn 1-2 tháng đầu** để test workflow trước khi đầu tư build.

**B. Web App Apps Script (kết hợp Claude API để extract)** — Trang có 1 web nội bộ (link Google), mở lên thấy form: ô paste text + drag hình + nút "Tạo căn mới". Backend gọi Claude API extract data, tự tạo folder Drive, upload hình, ghi cả Raw lẫn Public. Đánh đổi: tốn 1-2 ngày build, code cần maintain (nhưng Apps Script khá ổn định, ít đổi). **Đáng đầu tư** nếu Trang nghiêm túc làm BĐS lâu dài + có thể mở rộng cho cộng tác viên.

**C. Google Form gốc + Apps Script ngầm** — Trang điền form Google (có sẵn UI, không cần code UI), submit → script tự xử lý. Rẻ, đơn giản, native Google. Đánh đổi: form Google không có AI extract — Trang phải tự gõ từng trường (diện tích, giá, vị trí...) → chậm và dễ sai. Chỉ hợp nếu Trang OK với việc gõ thủ công.

**D. No-code (Make/n8n)** — kéo thả module: text trigger → Claude/OpenAI extract → Google Sheets → Google Drive. Setup nhanh hơn code, có UI visual. Đánh đổi: phí hàng tháng tăng theo số căn. Với 30 căn/tuần (~120/tháng), gói $9 vẫn đủ; nhưng nếu scale lên 200+ thì phải lên gói cao hơn. Cũng phụ thuộc vendor — nếu Make tăng giá hoặc đóng cửa, phải migrate.

**E. Telegram bot** — đỉnh cao về tốc độ. Trang đang đi xem nhà, chụp hình + gõ text "163.24.80 Tô Hiến Thành 50.2 5 4 13 12.9 tỷ" gửi bot, 30 giây sau bot reply "đã thêm căn 163.24.80, xem [link Sheet]". Đánh đổi: build phức tạp hơn (cần host bot 24/7), nhưng có thể dùng Cloudflare Workers free tier. Đặc biệt phù hợp với BĐS vì tính chất "đi field" nhiều.

## Khuyến nghị cụ thể

Tôi đề xuất **lộ trình 2 giai đoạn** thay vì chọn 1 cách duy nhất:

**Giai đoạn 1 (tuần 1-4): Cách A — Chat ở Cowork.** Mục tiêu là _chạy thật_ để phát hiện các edge case (text nguồn có format gì lạ, AI extract sai chỗ nào, quy ước đặt tên hình ra sao). Tôi sẽ chuẩn bị cho Trang 1 prompt template chuẩn để paste cùng data — giúp output nhất quán. Sau ~30-50 căn, Trang sẽ biết rõ workflow nào phù hợp nhất.

**Giai đoạn 2 (tháng 2 trở đi): Cách B — Web App Apps Script + Claude API.** Khi đã rõ workflow, đầu tư 1-2 ngày build web app nội bộ. Đây là điểm "ngọt" giữa chi phí (Apps Script free + Claude API ~$5-15/tháng cho 120 căn), bền vững (code do mình kiểm soát, không lệ thuộc vendor như Make/Zapier), và dễ bàn giao cho cộng tác viên.

**Lý do không recommend Cách E (Telegram) ngay**: dù tốc độ tuyệt vời, Trang nói chỉ mình Trang nhập 10-30 căn/tuần — chưa đủ pain point để justify 2-3 ngày build bot. Có thể cân nhắc khi mở rộng đội hoặc khi Trang nhập tại field nhiều.

**Lý do không recommend Cách C (Form thuần)**: thiếu AI extract → mất hết lợi thế của data input có cả text + hình. Trang sẽ chán sau 1 tuần.

**Lý do không recommend Cách D (No-code)**: với volume hiện tại, no-code không nhanh hơn Apps Script đáng kể, lại phải trả phí hàng tháng + lệ thuộc vendor. Apps Script là native Google → ổn định nhất với hệ Google Sheet/Drive Trang đang dùng.

## Bước tiếp theo

Nếu Trang đồng ý lộ trình 2 giai đoạn, tôi đề xuất ngay bây giờ làm 3 việc cho **Giai đoạn 1**:

1. Tôi viết file `prompt_template.md` (lưu ở `D:\LHTBrain\01_PROJECTS\BDS-KhangNgo\`) — template Trang sẽ dùng mỗi lần paste data mới.
2. Tôi viết file `data_schema.md` — định nghĩa rõ các trường Raw vs Public, kèm rule biến đổi (ẩn địa chỉ, viết lại mô tả, thay tên đường gần).
3. Tôi viết file `drive_naming_rules.md` — quy ước đặt tên file hình (`01_mat-tien.jpg`, `02_phong-khach.jpg`, ...) và rule phân Quận.

Trang OK với 3 file này không? Hay muốn tôi điều chỉnh gì trước khi tôi bắt tay viết?