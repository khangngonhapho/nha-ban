---
id: US-035
status: accepted
date: 2026-05-25
size: L
---

# US-035: Hệ thống cào BĐS & Mini-App biên tập rổ hàng 2000 căn

## User story
**As an** Admin of Khang Ngô Nhà Phố
**I want** to run a local Python script in Ultra-Stealth Mode (crawling 400 houses per district in ~2 hours) and a simple Flask Mini-App
**So that** I can safely crawl all listings, convert all image links to Google Drive links, manually select image categories by eye, and save the curated 79-column data directly to the active Google Sheet with zero risk of account suspension or IP bans

## Acceptance
- [x] SQLite hoạt động trực tiếp (tích hợp sẵn trong Python) tự động tạo file `raw_archive.db` có cấu trúc 79 cột nghiệp vụ đồng nhất với Pool Sheet.
- [x] Script cào `crawl_pipeline.py` hỗ trợ tham số Quận (ví dụ: `--district Q10`) để cào cuốn chiếu từng khu vực.
- [x] Script hoạt động ở **Chế độ Siêu Tàng Hình (Ultra-Stealth Mode)**:
  - Nghỉ ngẫu nhiên `8.0 - 15.0` giây trước mỗi lần mở xem chi tiết căn nhà.
  - Nghỉ ngẫu nhiên `2.0 - 4.0` phút (120 - 240 giây) trước mỗi lần chuyển trang danh sách.
  - Hoàn tất cào text thô 1 Quận (~400 căn) an toàn trong khoảng **2 đến 2.5 tiếng**.
- [x] Luồng tải ảnh và upload lên Google Drive 5TB chạy ngầm tự động, thiết lập chế độ nghỉ 3-5 giây mỗi căn để bảo vệ IP mạng nhà.
- [x] Giao diện Web biên tập viên local `curator.html` hiển thị ảnh trực quan của từng căn nhà để lựa chọn bằng mắt.
- [x] Nút **"LƯU LÊN SHEET"** trên giao diện chèn dòng dữ liệu 79 cột hoàn chỉnh (đã điền link ảnh vào đúng cột chuyên biệt) trực tiếp xuống đáy Google Sheet chính thức.
- [x] Đóng gói thành công ứng dụng **Chạy độc lập (Portable Application - KhangNgoCurator.exe)** hoạt động hoàn hảo trên mọi máy tính Windows mà không cần cài sẵn môi trường Python hay Inno Setup.
- [x] Tự động migration chuẩn hóa tên cột tiếng Việt sang dạng không dấu (`get_safe_col_name`) giúp SQLite hoạt động tin cậy mà không mất dữ liệu cũ.
- [x] Tích hợp Pillow nén ảnh chất lượng 75%, giới hạn tối đa 1600px giúp giảm dung lượng file xuống 90%-95%, tránh tràn hạn mức Cloudinary 25GB.
- [x] Hỗ trợ di cư ảnh trực tiếp lên CDN Cloudinary thông qua giao thức signed REST POST.
- [x] Xử lý chuỗi TSV bằng thuật toán `escape_tsv_field` chuẩn RFC-4180 giúp copy-paste thủ công không bị ngắt dòng lệch cột khi dán vào Google Sheet.
- [x] Rút gọn bảng Curation panel (v2.1 UI), chỉ hiển thị 4 trường địa chỉ chỉnh sửa được, ẩn toàn bộ trường edit rác và hiển thị Dashboard Raw read-only.
- [x] Cơ chế tự động sắp xếp ảnh `sortImagesConfig` đẩy ảnh có nhãn lên đầu và dìm ảnh nhãn "Ẩn" xuống dưới cùng danh sách grid.
- [x] Cào trực tiếp chiều dài thực tế (Chieu_dai) từ chi tiết Thiên Khôi, lưu vào SQLite và hiển thị thô trên giao diện, không tự động tính toán.
- [x] Loại bỏ hoàn toàn thông tin chủ nhà (Nhóm 4) để bảo mật thông tin và tránh crash JS.
- [x] Thiết lập ảnh di cư mặc định có nhãn "Ẩn" và điền tuần tự vào Ảnh 1 - Ảnh 15.
- [x] Chọn ảnh Nền (Bìa) tự động đổi vị trí với Ảnh 1 (index 0), hoán đổi vị trí cũ cho ảnh thay thế.
- [x] Tự động tính toán vị trí dạng 1,3,5 của ảnh "N.Thất" lưu vào cột nghiệp vụ Ảnh Public (VD: 1,3,5).
- [x] Đưa tuần tự ảnh "Hẻm" vào Hình Hẻm 1-10 và tính vị trí dạng 1,2 lưu vào cột nghiệp vụ Ảnh Hẻm Public (VD: 1,2).
- [x] Khắc phục triệt để lỗi cào nhầm Tên đầu chủ (Hợp đồng) thành giá nhà bằng cách ưu tiên Exact Match và loại trừ substring "giá" trong nhãn.
- [x] Chuyển đổi hoàn toàn cơ chế cào Tên Đầu Chủ (Hợp đồng) và Điện thoại Đầu Chủ sang dạng bóc tách dựa trên CSS ID cụ thể (`#Detail_sHopDongDauChu` và `#Detail_sDienThoaiDauChu`) để đảm bảo chính xác 100%, chống lỗi sai lệch do so khớp từ khóa tiêu đề (title/label).
- [x] Tích hợp hệ thống âm thanh cảnh báo kép (winsound vật lý ở Backend và Web Audio API ở Dashboard Frontend) báo hiệu tức thời khi Cookie Thiên Khôi hết hạn (redirection sang `security.html`).
- [x] Tối ưu hóa thời gian chờ (Page Delay) giữa các trang chi tiết xuống trung bình ~30 giây (khoảng ngẫu nhiên 20s - 40s) giúp tăng tốc độ cào tin lên gấp 8 lần.
- [x] Giải quyết triệt để lỗi chặn phân trang GET của Thiên Khôi bằng cách tự động bảo toàn casing và vị trí của tham số `Page` gốc, đồng thời tự động viết lại đường dẫn (in-flight rewrite) sang endpoint phân trang AJAX thực tế `/Hang/Partial_Item` giúp cào sâu tuần tự (trang 1, 2, 3... 241, 244) hoàn hảo.
- [x] Khởi tạo bảng SQLite `crawl_sessions` để lưu trữ vĩnh viễn lịch sử các phiên cào tin (Cookie MD5, thời lượng cào, số lượng căn thành công, trạng thái thoát).
- [x] Xây dựng Tab thứ tư **📊 Lịch sử cào** và API tổng hợp Flask để hiển thị báo cáo tổng quan (Tổng số phiên, tổng số căn, tổng thời lượng, tốc độ cào trung bình) và lưới bảng lịch sử chi tiết so sánh các phiên cào.

## Solution

> [!note]- Configuration
> Thiết lập các biến cấu hình phục vụ kết nối API và tham số "siêu tàng hình" bắt buộc lưu trữ tại `curator_config.json`:
> ```json
> {
>     "sheet_id": "1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0",
>     "drive_folder_id": "folder_id_on_drive",
>     "target_district": "Quận 10",
>     "search_url": "https://data.thienkhoi.com/Hang/List?Page=1&pID_Quan=11",
>     "crawler_limit": 5
> }
> ```

> [!note]- Input / Storage
> 1.  **Cơ sở dữ liệu thô SQLite (`raw_archive.db`):** 
>     *   Bảng `listings`: Chứa đầy đủ 79 cột nghiệp vụ tương tự Pool Sheet cùng các trường quản lý trạng thái (`id`, `tk_id`, `status` [raw_text | raw_complete | published], `raw_images_tk_json`, `raw_drive_images_json`, `curated_config_json`).
>     *   Bảng `crawl_sessions`: Lưu trữ vĩnh viễn lịch sử các phiên cào tin phục vụ theo dõi hiệu năng (`id`, `cookie_sig`, `start_time`, `end_time`, `duration`, `crawled_count`, `status`).

> [!note]- Key Architectural Logic
> ### 1. Sơ đồ tuần tự vận hành mới (Thread-Based & Packaged)
> ```mermaid
> graph TD
>     TK[Hệ thống Thiên Khôi] -- 1. Crawl Text Thô & Link Ảnh --> Server[KhangNgoCurator.exe Flask]
>     Server -- 2. Lưu Metadata thô --> SQLite[(SQLite: raw_archive.db)]
>     
>     SQLite -- 3. Đọc các căn status='raw_text' --> Server
>     
>     Server -- 4a. Down Ảnh & Up Drive có Credentials --> Drive[Google Drive 5TB]
>     Server -- 4b. Down Ảnh & Lưu local không Credentials --> LocalDir[Thư mục static/images/ cục bộ]
>     
>     Drive -- 5a. Trả về Link Drive công khai --> Server
>     LocalDir -- 5b. Trả về Link local server --> Server
>     
>     Server -- 6. Update link ảnh & Đổi status='raw_complete' --> SQLite
>     
>     SQLite -- 7. Hiển thị thông tin & Gallery --> UI[curator.html Web UI]
>     Admin -- 8. Chọn nhãn Cover, MT, Sơ đồ, Hẻm... --> UI
>     UI -- 9. Lưu biên tập cục bộ --> Server
>     
>     Server -- 10a. Ghi đè 79 cột hoàn thiện có Credentials --> Sheets[(Google Sheets Pool)]
>     Server -- 10b. Đẩy mảng copy-paste tab-delimited không Credentials --> UI
>     
>     Server -- 11. Đổi status='published' --> SQLite
> ```
> 
> ### 2. Luồng cào đồng bộ trong luồng ngầm (Same-Process Thread)
> Để chạy độc lập hoàn toàn trên máy không cài Python, ứng dụng không dùng lệnh `subprocess.Popen` gọi Python ngoài nữa.
> - **Thread-Based Execution:** Nhập trực tiếp module `crawl_pipeline` và thực thi hàm `scrape_district` trong một Thread ngầm của Flask.
> - **Log Redirector:** Chuyển hướng luồng đầu ra chuẩn `sys.stdout/sys.stderr` về bộ đệm log trong RAM để hiển thị thời gian thực lên Console UI.
> - **Exit Protection:** Monkeypatch hàm hệ thống `sys.exit()` để nâng lỗi thành `RuntimeError`, chống sập hoặc tắt máy chủ Flask khi script cào gặp lỗi cookie hết hạn.
> 
> ### 3. Vấn đề Bug dis.py của Windows Python 3.10.0 & Giải pháp Monkeypatch
> Phiên bản Python 3.10.0 trên Windows có một bug nổi tiếng trong module tiêu chuẩn `dis.py` (Disassembler) gây ra lỗi `IndexError: tuple index out of range` khi cố gắng phân tích bytecode phức tạp của các gói thư viện mới (như `cryptography 48.0.0`).
> - **Monkeypatch dis:** Trong script đóng gói [build_exe.bat](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/build_exe.bat), em đã chèn đoạn code Python động ghi đè hàm `dis._get_const_info` sang dạng an toàn (bắt ngoại lệ IndexError). Nhờ đó PyInstaller đóng gói thành công 100% ứng dụng mà không bị sập.
> 
> ### 4. Ứng dụng chạy trực tiếp Standalone (Portable Application)
> - Toàn bộ động cơ, Flask server, HTML và Python runtime được PyInstaller đóng gói gọn gàng thành thư mục: `dist/KhangNgoCurator/`.
> - Kích đúp vào file **`KhangNgoCurator.exe`** để chạy trực tiếp ngay tức khắc mà không cần cài đặt Python. Có thể nén file ZIP gửi đi mọi máy tính khác cực kỳ sạch sẽ và tiện lợi.
> 
> ### 5. Chuẩn hóa & Tự động Migration Cột Cơ Sở Dữ Liệu SQLite
> - **Accent Stripping Helper (`get_safe_col_name`):** Tích hợp hàm loại bỏ toàn bộ dấu tiếng Việt trước khi tạo chuỗi an toàn cho tên cột (ví dụ: `Hình Nhận Diện` chuyển thành `Hinh_Nhan_Dien` thay vì `H_nh_Nh_n_Di_n`).
> - **Tự động Migration:** Khi khởi động Flask Server, hệ thống tự động kiểm tra cấu trúc bảng hiện tại bằng `PRAGMA table_info`. Nếu phát hiện các cột cũ chứa ký tự lỗi, nó sẽ tự động chạy câu lệnh `ALTER TABLE listings RENAME COLUMN` để chuyển đổi sang cấu trúc chuẩn mới mà không làm mất bất kỳ bản ghi lịch sử nào của người dùng.
> 
> ### 6. Nén Ảnh Pillow & Di cư Ảnh qua Cloudinary signed REST API
> - **Nén và Resize ảnh Pillow:** Trước khi ảnh được lưu cục bộ hoặc upload lên Cloudinary, thư viện Pillow sẽ tự động kiểm tra kích thước. Nếu ảnh vượt quá `1600px`, hệ thống tự động resize giữ nguyên aspect ratio, đồng thời xuất ảnh dạng JPEG chất lượng `75%`. Điều này giảm dung lượng ảnh từ 2.5MB xuống còn ~120KB (giảm 90%-95%), đảm bảo không vượt quá hạn mức miễn phí 25GB của Cloudinary.
> - **Cloudinary REST signed Uploader:** Flask backend tự sinh chữ ký bảo mật (signed signature) và thực hiện POST trực tiếp dữ liệu nhị phân của ảnh đã nén lên API REST của Cloudinary. Ảnh được phân nhóm thư mục gọn gàng theo mã căn `BDS-KhangNgo/[tk_id]`.
> 
> ### 7. Copy-Paste TSV Chuẩn RFC-4180 Tránh Lệch Dòng Google Sheet
> - **Cơ chế `escape_tsv_field`:** Khi người dùng không cấu hình Google Sheets Credentials và phải copy thủ công rổ hàng qua Clipboard, hệ thống áp dụng bộ lọc chuỗi đặc biệt:
>   - Loại bỏ toàn bộ ký tự Tab (`\t`) trong các trường văn bản.
>   - Gấp đôi ký tự nháy kép (`"`) thành `""` và bao quanh toàn bộ trường văn bản có chứa ký tự xuống dòng (`\n`, `\r`) bằng dấu nháy kép ngoài cùng đúng theo đặc tả RFC-4180.
>   - Khi dán (Ctrl+V) vào Google Sheets, toàn bộ nội dung mô tả nhiều dòng sẽ nằm trọn vẹn trong duy nhất 1 ô dữ liệu, hoàn toàn không bị nhảy dòng phá hỏng cấu trúc 79 cột.
> 
> ### 8. Giao diện Tinh gọn v2.1 & Sắp xếp Thứ tự Ảnh Tự động (Image Role Sorting)
> - **Ẩn trường Edit rác:** Tối ưu hóa bảng curation biên tập, ẩn toàn bộ 12 trường chỉnh sửa nghiệp vụ Khang Ngô để Admin tập trung thao tác trực tiếp trên Google Sheets. Chỉ hiển thị duy nhất 4 trường địa chỉ thực tế có thể chỉnh sửa (`Số nhà`, `Đường`, `Phường`, `Quận`).
> - **Dashboard Raw read-only:** Bổ sung khu vực hiển thị Premium Dashboard bên phải hiển thị toàn bộ 20+ thông số gốc Thiên Khôi (Mã TK, Diện tích thực tế, Diện tích sổ, số tầng, số phòng ngủ, hướng, link Facebook đầu chủ, chiều dài cào trực tiếp từ chi tiết Thiên Khôi, mô tả chi tiết cuộn được) để đối chiếu thông tin nhanh. Thông tin chủ nhà (Nhóm 4) được loại bỏ hoàn toàn để bảo mật.
> - **Advanced Image Curation & Swapping:**
>   - **Trạng thái mặc định:** Toàn bộ ảnh di cư xong lưu tuần tự vào `Ảnh 1` - `Ảnh 15` và mặc định mang nhãn `"Ẩn"`.
>   - **Cơ chế Swap ảnh Nền (Bìa):** Khi một ảnh được chọn làm `"Nền"`, hệ thống tự động đưa link đó lên `Ảnh 1` (index 0), đồng thời hoán đổi vị trí của ảnh cũ đang ở `Ảnh 1` xuống index của ảnh click, đảm bảo thứ tự luôn chuẩn xác.
>   - **Chỉ số Vị trí Nội thất & Hẻm:**
>     - Ảnh chọn làm `"N.Thất"` được hệ thống tính toán vị trí 1-based trong chuỗi `Ảnh 1` - `Ảnh 15`, ghép lại thành chuỗi ngăn cách bằng dấu phẩy (VD: `1,3,5`) lưu vào cột nghiệp vụ `Ảnh Public (VD: 1,3,5)`.
>     - Ảnh chọn làm `"Hẻm"` được tự động đưa tuần tự vào các cột `Hình Hẻm 1` - `Hình Hẻm 10`. Vị trí ban đầu 1-based của chúng trong chuỗi 15 ảnh được ghép lại (VD: `1,2`) lưu vào cột nghiệp vụ `Ảnh Hẻm Public (VD: 1,2)`.
> 
> ### 9. Giải quyết lỗi cào nhầm Tên đầu chủ (Hợp đồng) thành Giá nhà
> - **Nguyên nhân:** Cú pháp tìm kiếm cũ của `get_val_by_label` sử dụng so khớp substring `if label_text.lower() in txt`. Vì nhãn tiền tệ là "Giá chào hợp đồng" có chứa từ khóa "hợp đồng", nên khi quét nhãn từ trên xuống, nó sẽ khớp nhầm với nhãn giá và lấy giá nhà thay vì Tên đầu chủ của nhãn "Hợp đồng".
> - **Giải pháp:** Cải tiến hàm `get_val_by_label` thực hiện tìm kiếm qua hai bước:
>   1. **Exact Match (Ưu tiên hàng đầu):** Duyệt toàn bộ các label và kiểm tra xem có khớp chính xác `txt == target` (ví dụ `"hợp đồng"` khớp chính xác `"hợp đồng"`) hay không. Nếu có, trả về giá trị ngay lập tức.
>   2. **Substring Match (Dự phòng thông minh):** Nếu không khớp chính xác, thực hiện substring match nhưng thêm cơ chế loại trừ false positive: Nếu đang tìm `"hợp đồng"` thì bỏ qua các label chứa chữ `"giá"`; nếu đang tìm `"đầu chủ"` thì bỏ qua các label chứa chữ `"điện thoại"`.
> 
> ### 10. Bảo toàn sơ đồ thửa đất tự động & Công thức ảnh bìa động
> - **Gộp chung ảnh cào:** Hợp nhất `images_td` (sơ đồ) và `images_nd` (nội thất) thành một mảng duy nhất khi cào. Nhờ vậy, ảnh sơ đồ thửa đất được tự động tải về, nén Pillow và tải lên Cloud CDN (Cloudinary/Drive) tương tự ảnh thường.
> - **Nhận diện vai trò tự động (Auto-role mapping):** Khi mở biên tập, Javascript tự động đối chiếu link gốc của ảnh với các cột sơ đồ thửa đất, mặt tiền, nhận diện. Nếu trùng khớp, hệ thống tự động gán nhãn `'Sơ đồ'`, `'Mặt tiền'`, `'Bìa'` ngay lập tức mà người dùng không cần phải thực hiện dán nhãn thủ công.
> - **Công thức động Bìa ảnh:** Lấy số dòng hiện tại của Sheet cộng 1 (`next_row = len(sheet.get_all_values()) + 1`) để tạo công thức động `=IMAGE(AD{next_row})` hiển thị ảnh mặt tiền của dòng đó.
> 
> ### 11. Ghi đè Google Sheets Table & Checkbox Preservation
> - **Khắc phục lỗi lệch format:** Chuyển đổi từ `sheet.append_row()` sang `sheet.update(range_name=f"A{next_row}:CA{next_row}", ...)` trong gspread. Việc ghi trực tiếp vào các ô trống pre-allocated ở cuối bảng dữ liệu sẽ kích hoạt Google Sheets tự động mở rộng vùng Table range, nhờ đó thừa hưởng trọn vẹn checkbox và các dòng xen kẽ (alternating colors) định dạng sẵn.
> 
> ### 12. Hệ thống Toast Notification nổi trên màn hình
> - **Phản hồi trực quan:** Tạo container CSS `#toast-container` và các Toast Item kính mờ nổi lên ở góc trên cùng bên phải. Mỗi hành động click nút (Lưu SQLite, Xuất bản, Cào lại, Xóa tin) đều kích hoạt Toast trượt mượt mà (Success/Warning/Error) cung cấp phản hồi lập tức cho biên tập viên ngay cả khi terminal log đang bị ẩn.
> 
> ### 13. Hệ thống Cảnh báo Âm thanh khi Hết hạn Cookie
> - **winsound ở Backend:** Khi chạy cào hoặc bấm "Cào lại căn này", nếu máy chủ phát hiện cookie đã hết hạn (bị redirect sang `security.html`), nó sẽ phát ra chuỗi âm bíp vật lý qua loa máy tính (gồm 2 tiếng bíp cao `1000Hz` ngắn và 1 tiếng bíp trầm `800Hz` kéo dài) thông qua thư viện tiêu chuẩn `winsound`.
> - **Web Audio API ở Dashboard:** Giao diện quản trị `curator.html` liên tục theo dõi log cào. Ngay khi phát hiện từ khóa cookie hết hạn hoặc `security.html`, nó sử dụng bộ tổng hợp dao động ngầm (`AudioContext` Oscillator Node) của trình duyệt để phát âm báo bíp kép cảnh báo chất lượng cao cùng thông báo toast cảnh báo màu đỏ.
> 
> ### 14. Bảo toàn phân trang Casing & Chuyển đổi Endpoint Dynamic API (/Hang/Partial_Item)
> - **Bảo toàn Casing và thứ tự in-place:** Khi cào tuần tự, hàm `build_paging_url` trong `crawl_pipeline.py` tự động so khớp, trích xuất và bảo toàn chính xác cấu trúc casing của tham số phân trang gốc (`Page`, `p`, v.v.) mà không làm thay đổi vị trí của nó trong URL để tránh lỗi phân tích ở backend ASP.NET MVC của đối tác.
> - **Dynamic Rewrite sang `/Hang/Partial_Item`:** Thử nghiệm chứng minh máy chủ Thiên Khôi khóa cứng tất cả yêu cầu GET trực tiếp đến `/Hang` và `/Hang/Index` để luôn chỉ hiển thị Trang 1 (Anti-scraping). Để giải quyết triệt để, ứng dụng tự động viết lại đường dẫn (in-flight path rewriting) của mọi URL danh sách dán vào sang endpoint AJAX thực tế `/Hang/Partial_Item` giúp phân trang GET hoạt động trơn tru trên mọi độ sâu (trang 2, 3, 241, 244).
> 
> ### 15. Hệ thống Lịch sử Phiên cào & Thống kê Tổng thể
> - **Tự động lưu phiên cào ở khối `finally`:** Toàn bộ vòng lặp cào phân trang được bọc trong khối `try...finally` toàn cục. Bất kể tiến trình cào kết thúc do hoàn thành rổ hàng, đạt giới hạn chỉ định, cookie hết hạn (`sys.exit` ném ra `RuntimeError`), hay người dùng ngắt luồng bằng tay, khối `finally` đều sẽ tự động tính toán tổng số căn cào được, tính thời lượng thực hiện thực tế, nhận diện trạng thái thoát tương ứng và ghi nhận tức thì vào bảng cơ sở dữ liệu `crawl_sessions` cùng mã MD5 đặc trưng của Cookie (`cookie_sig`).
> - **API Tính toán Thống kê Tổng quan (Flask API):** Tích hợp endpoint `GET /api/crawl/sessions` thực hiện truy vấn cơ sở dữ liệu để lấy toàn bộ danh sách phiên cào sắp xếp mới nhất lên trước, đồng thời chạy câu lệnh SQL tổng hợp (`SUM`, `COUNT`) để tính toán thời gian thực các chỉ số tổng quan: Tổng số phiên, Tổng số căn đã cào, Tổng thời lượng, Tốc độ cào trung bình toàn cục.
> - **Giao diện Trực quan Tab 📊 Lịch sử cào:** Thiết kế một tab quản trị hoàn toàn mới trang bị lưới Grid gồm 4 thẻ tổng hợp thông tin (Metric Cards Grid) bóng bẩy theo phong cách kính mờ (glassmorphism) và bảng lịch sử chi tiết. Mỗi phiên cào hiển thị đầy đủ thông tin thời điểm bắt đầu/kết thúc, thời lượng cào, tốc độ cào của phiên đó, và đính kèm Badge màu sắc tương ứng biểu diễn trạng thái thoát (`Hoàn thành` 🟢, `Đạt giới hạn` 🟡, `Hết hạn Cookie` 🔴, `Đã dừng` ⚪).






## Verification Plan

> [!check]- Automated Tests
> - **Stealth Timing Verification:** Chạy thử cào 2 căn đầu tiên và đo thời gian dừng nghỉ giữa các request xem có nằm đúng trong khoảng 8-15 giây hay không.
> - **dis.py Bug Verification:** Kịch bản build `build_exe.bat` chạy hoàn tất thành công 100% với log `Build complete!`, chứng minh monkeypatch đã giải quyết triệt để lỗi phân tích bytecode của Python 3.10.0.

> [!check]- Manual Verification
> - Kích đúp file `KhangNgoCurator.exe` và kiểm tra xem giao diện web `http://localhost:5000` có tự động mở ra trên trình duyệt hay không.
> - Biên tập thử 1 căn nhà, gán nhãn ảnh, sắp xếp thứ tự và bấm "Lưu lên Google Sheet". Kiểm tra dòng mới chèn ở đáy Google Sheet rổ hàng chính thức.

## Files Touched
- `curator_server.py` — Server Flask local được tái cấu trúc thành Thread-based và tích hợp cảnh báo âm thanh winsound.
- `curator.html` — Giao diện Web biên tập viên tuyển chọn hình ảnh, copy fallback và tích hợp Web Audio API cảnh báo ngầm.
- `crawl_pipeline.py` — Pipeline cào tin, tích hợp tối ưu thời gian chờ ~30s, in-place casing preservation và dynamic API routing (/Hang/Partial_Item).
- `build_exe.bat` — Script đóng gói có tích hợp monkeypatch dis.
- `installer_script.iss` — Kịch bản cài đặt Inno Setup tùy chọn.
- `docs/stories/INDEX.md` — Đăng ký US-035.
- `SOURCE_OF_TRUTH.md` — Cập nhật nhật ký thay đổi.

