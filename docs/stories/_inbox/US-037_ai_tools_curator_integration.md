---
id: US-037
status: accepted
date: 2026-05-27
size: M
---

# US-037: Tích hợp AI Tools, Cấu hình System Prompt & Tự động tạo Mã Khang Ngô

## User story
**As an** Admin / Biên tập viên Khang Ngô
**I want** tự động hóa việc tạo Mã Khang Ngô, chạy AI viết bài đăng Public, tra Phường cũ và đồng bộ trực tiếp 1 căn sang sheet Source public ngay trên Curator Dashboard
**So that** tôi có thể tối giản hóa 95% thao tác biên tập thủ công, đồng thời tùy ý điều chỉnh luật viết bài của AI hay đồng bộ nhanh rổ hàng công khai trực tiếp mà không cần cấu hình lại code gốc hay biên dịch lại tệp EXE.

## Acceptance
- [x] Tự động tính toán và hiển thị **Mã Khang Ngô (ID)** trên giao diện Curation Panel theo thời gian thực (Real-time) mỗi khi địa chỉ (`Số nhà`, `Đường`, `Quận`) thay đổi.
- [x] Thuật toán sinh Mã Khang Ngô bằng JavaScript trên trình duyệt phải trùng khớp tuyệt đối 100% kết quả mã hóa so với Google Sheets Apps Script.
- [x] Bổ sung ô nhập lớn cấu hình **System Prompt AI** và **OpenAI API Key** bảo mật ở bảng cấu hình bên phải, lưu trữ trực tiếp vào tệp `curator_config.json`.
- [x] Nạp sẵn System Prompt mặc định chuẩn mực được port nguyên bản từ Apps Script `pool_backend_v3.gs` (Luật sáp nhập phường cũ và Luật cấu trúc USP batdongsan.com.vn).
- [x] Thiết kế nút bấm **🤖 CHẠY BIÊN TẬP AI** trực quan trong Curation Panel đi kèm hiệu ứng xoay tải (Loading Spinner) khi đang gọi API ngầm.
- [x] Flask API ngầm `/api/ai/generate` (POST) gọi OpenAI GPT-4o-mini với prompt động do người dùng tự sửa đổi ở settings, phân tích căn nhà để tự động trả về định dạng cấu trúc JSON chuẩn (`phuong_cu`, `tieu_de_public`, `mo_ta_public`).
- [x] Tự động điền (Auto-populate) các kết quả AI sinh ra vào form nhập liệu sau khi chạy thành công để Admin duyệt và chỉnh sửa nhanh.
- [x] **Bổ sung tính năng Đồng bộ sang Source (Publish to Public Web):**
  - [x] Thiết kế form nhập địa chỉ (Số nhà, Tên đường) và nút "🌐 LÊN SÓNG" trong Admin Panel của `index.html`.
  - [x] Nâng cấp scope Google OAuth2 trong `index.html` lên full read-write (`https://www.googleapis.com/auth/spreadsheets`).
  - [x] Tích hợp logic Sheets API client-side gọi `gapi.client.sheets` tìm kiếm căn nhà trên **Sheet Pool** từ trình duyệt của anh Khang, mapping dữ liệu 78 cột từ Pool sang cấu trúc 41 cột của Source.
  - [x] Tự động nạp công thức ảnh `=IMAGE(AM{row})` và chép đè/append sang Sheet Source, tự động nạp Last Sync ngược lại cột BZ bên Sheet Pool.

## Solution

> [note]- Configuration
> Các khóa cấu hình lưu tại `curator_config.json`:
> ```json
> {
>   "openai_api_key": "sk-proj-...",
>   "openai_system_prompt": "Bạn đóng vai một Chuyên gia môi giới nhà phố 15 năm kinh nghiệm tại trung tâm TP.HCM...",
>   "public_sheet_id": "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
> }
> ```

> [note]- Input
> Payload gửi tới API ngầm `/api/ai/generate` (POST):
> ```json
> {
>   "so_nha": "string",
>   "duong": "string",
>   "phuong": "string",
>   "quan": "string",
>   "gia": "string",
>   "dien_tich_thuc_te": "string",
>   "dien_tich_tren_so": "string",
>   "mat_tien": "string",
>   "chieu_dai": "string",
>   "so_tang": "string",
>   "so_phong_ngu": "string",
>   "so_nhave_sinh": "string",
>   "huong": "string",
>   "mo_ta_chi_tiet": "string",
>   "noi_dung_chinh": "string"
> }
> ```

> [note]- Output / Format
> Phản hồi JSON trả về từ `/api/ai/generate`:
> ```json
> {
>   "status": "success",
>   "phuong_cu": "Phường 6 cũ",
>   "tieu_de_public": "Cách Mạng Tháng 8 - 45m2 - 4x11 - 3 tầng - 6.9T | Hẻm xe hơi đỗ cửa",
>   "mo_ta_public": "Chính chủ gửi bán gấp nhà phố trung tâm Quận 3..."
> }
> ```

> [note]- Key logic
> 1. **Thuật toán sinh mã Khang Ngô:**
>    * Phần Số nhà: Lọc số nhà trước dấu `+`, chuyển đổi số thành chữ in hoa (`1`->`M`, `2`->`H`...) theo bảng mật mã học, giữ chữ thường.
>    * Phần Đường: Normalization các tên đường đặc biệt (`cmt8`->`CMTT`, `3/2`->`BTH`), viết tắt chữ cái đầu tiên và Đảo ngược chuỗi acronyms.
>    * Kết nối chuỗi: `[Mã Số Nhà] + 'I' + [Tên Đường Đảo Ngược]`.
>    * Ciphering: Chèn chữ cái `W` vào vị trí index số 2 (1-based) của chuỗi kết quả.
> 2. **Bắt buộc định dạng JSON từ OpenAI:**
>    * System prompt cấu hình động bắt buộc phải chứa chỉ dẫn `"response_format": { "type": "json_object" }` và mô tả chi tiết schema JSON đầu ra để GPT trả về JSON thuần khiết, giúp parser frontend hoạt động không lỗi.
> 3. **Cơ chế Đồng bộ sang Source (Python gspread):**
>    * Map chính xác 41 cột nghiệp vụ của Source. Lấy hình nền công khai làm ảnh thứ nhất, 2 ảnh hẻm (chọn lọc hoặc random) làm ảnh tiếp theo, sau đó là các ảnh nội thất còn lại.
>    * So khớp bằng cột `System ID` ở cột AL (cột 38). Nếu tìm thấy dòng cũ, chép đè dòng đó (Smart Merge/Force Overwrite tương đương). Nếu chưa có, append dòng mới vào tab `Source`.
>    * Đặt công thức hiển thị hình ảnh `=IMAGE(AM{row})` tại cột A (cột 1) và insert checkbox đăng tin tại cột AO.
>    * Lưu kết quả thành công và thời gian đồng bộ vào cột `source_sync_status = 'synced'` và `source_sync_time` trong SQLite.
> 4. **Trực quan hóa trạng thái trên Sidebar:**
>    * Payload trả về `/api/listings` chứa đầy đủ `source_sync_status` và `source_sync_time`. Trên Sidebar, nếu `source_sync_status === 'synced'`, vẽ thêm icon quả địa cầu nhỏ hoặc tag badge màu xanh lá tươi `🌐 Public` để biên tập viên nắm bắt căn nào đã hiển thị lên web public theo thời gian thực.
> 5. **Bổ sung cột SQLite:**
>    * Hàm `init_db()` trong `crawl_pipeline.py` tự động phát hiện và thêm 2 cột `source_sync_status TEXT DEFAULT 'not_synced'` và `source_sync_time TEXT` vào SQLite nếu chưa tồn tại.

---

### 6. Kiến Trúc Đồng Bộ & Cập Nhật Rổ Hàng (On-Demand Pull Ingestion)

#### 🚨 Bài toán Hiệu năng & Bảo mật (The Challenge)
Khi quy mô rổ hàng cào từ Thiên Khôi đạt đến **~5000 căn**:
1. **Giảm trải nghiệm người dùng (Chậm):** Nếu đồng bộ toàn bộ 5000 căn sang Sheet Source công khai, Google Sheets API sẽ phản hồi cực kỳ chậm, khiến Web Vercel tải chậm (>3-5 giây) và làm trình duyệt khách hàng bị giật lag.
2. **Lộ thông tin bảo mật:** Kho thô chứa đầy đủ địa chỉ thực tế, số điện thoại chủ nhà và các ảnh pháp lý chưa qua kiểm duyệt.
3. **Quá tải tài nguyên:** 95% trong số 5000 căn thô là rác hoặc chưa có nhu cầu chào bán thực tế.

#### 💡 Giải pháp: Đồng Bộ Theo Nhu Cầu (On-Demand Pull Ingestion)
Hệ thống triển khai mô hình **"Đồng bộ kéo theo yêu cầu" (On-Demand Pull Ingestion)** trực tiếp từ Admin Panel của Web Vercel, giải quyết triệt để vấn đề hiệu năng và bảo mật.

> [!IMPORTANT]
> - **Sheet Pool (Cloud Raw - ~5000 căn):** Kho dữ liệu thô tuyệt mật, chỉ lưu trữ nội bộ.
> - **Sheet Source (Cloud Curated - ~50-200 căn):** Chỉ chứa các căn chất lượng cao thực sự đang chào bán.
> - **On-Demand Sync (Client-side Google OAuth2):** Dữ liệu được kéo từ Pool sang Source chỉ khi anh Khang yêu cầu bằng cách nhập Số nhà + Tên đường trên Web Admin.

#### 🔄 Sơ đồ Luồng Dữ Liệu (Data Flow Architecture)

```mermaid
graph TD
    %% Nodes
    TK[Thiên Khôi Group] -->|Crawler Pipeline| SQLite[(SQLite Cục bộ)]
    
    subgraph Curator App (Local EXE - Máy của Trang)
        SQLite -->|Hiển thị danh sách| VisualUI[Giao diện Biên tập]
        VisualUI -->|1. Chọn & Lọc ảnh| FilterImg[Dán nhãn Ảnh Public]
        VisualUI -->|2. Nhập Địa chỉ| LiveID[Mã Khang Ngô Real-time]
        VisualUI -->|3. Click AI| AICuration[gpt-4o-mini Curation]
        
        FilterImg --> SaveLocal[Lưu SQLite & Xuất bản]
        LiveID --> SaveLocal
        AICuration --> SaveLocal
    end

    SaveLocal -->|Đồng bộ tự động| SheetPool[Google Sheet POOL<br>~5000 căn thô tuyệt mật]

    subgraph Web Vercel Admin (Máy của anh Khang)
        InputUI[Form Yêu cầu Lên sóng<br>Nhập: Số nhà + Đường] -->|Bấm LÊN SÓNG| GoogleAPI[Google Sheets API Client]
        GoogleAPI -->|1. Tìm kiếm thông minh & So khớp| SheetPool
        GoogleAPI -->|2. Tự động Mapping 41 cột| SheetSource[Google Sheet SOURCE<br>~50-200 căn tinh tuyển]
        GoogleAPI -->|3. Ghi nhận Last Sync| SheetPool
    end

    subgraph Web Vercel Public (Khách hàng)
        SheetSource -->|Auto Mirror| SheetPublic[Google Sheet PUBLIC<br>Đã ẩn số nhà & SĐT]
        SheetPublic -->|Tải cực nhanh <0.2s| WebPublic[Website Khách hàng]
    end

    %% Styles
    style SheetPool fill:#f9f,stroke:#333,stroke-width:2px
    style SheetSource fill:#bbf,stroke:#333,stroke-width:2px
    style SheetPublic fill:#bfb,stroke:#333,stroke-width:2px
```

#### 🛠️ Chi Tiết Các Thành Phần & Logic Nghiệp Vụ
1. **Phân tách Rổ hàng (Sheet Pool vs Sheet Source):**
   - **Sheet Pool (Cloud Raw):** Nhận đồng bộ trực tiếp từ máy của Trang. Đây là nơi chứa toàn bộ 5000 căn thô với đầy đủ thông tin nội bộ.
   - **Sheet Source (Curated Catalog):** Chỉ chứa những căn chất lượng cao đã được anh Khang duyệt "lên sóng". 
     * **Dung lượng siêu nhẹ:** Giữ ở mức ~50 - 200 căn giúp tăng tốc độ phản hồi API tối đa, thời gian tải web công khai đạt mức xuất sắc (<0.2 giây).
     * **Custom Fields:** Hỗ trợ các trường thông tin đặc thù bổ sung thủ công trên Sheets hoặc Web Admin (ví dụ: ghi chú riêng, giá ưu đãi, tag thị trường) mà kho thô Pool không quản lý.
2. **Logic So khớp Thông minh & Mapping Cột (On-Demand Sync):**
   Khi anh Khang gõ Số nhà + Đường và bấm **🌐 LÊN SÓNG**:
   - **Chuẩn hóa Địa chỉ (Normalization):** Trình duyệt chuẩn hóa chuỗi địa chỉ nhập vào (loại bỏ khoảng trắng, dấu tiếng Việt, xử lý CMT8 -> CMTT, 3/2 -> BTH, Đường số X -> DSX) để tìm kiếm chính xác trên Sheet Pool.
   - **Mapping 78 cột sang 41 cột:**
     * **Mã Khang Ngô:** Sinh tức thời tại client và ghi vào cột D.
     * **Công thức ảnh đại diện:** Tự động điền `=IMAGE(AM{row})` tại cột A để hiển thị ảnh bìa ngay trên Sheets.
     * **Gộp và lọc hình ảnh Public:** Trích xuất tối đa 10 ảnh public sạch (ảnh bìa mặt tiền, 2 ảnh hẻm ngẫu nhiên hoặc được dán nhãn, và các ảnh nội thất).
     * **Định dạng nghiệp vụ:** Định dạng giá tỷ chuẩn, chuyển đổi ký hiệu Quận (Quận 10 -> 10, Phú Nhuận -> PN), trích xuất cú pháp từ nội dung thô.
   - **Ghi đè thông minh (Smart Merge):** Đối chiếu theo `System ID`. Nếu căn nhà đã tồn tại trên Source, thực hiện cập nhật ghi đè dòng cũ; nếu chưa, tiến hành append dòng mới.
   - **Đồng bộ trạng thái ngược (Last Sync):** Ghi nhận mốc thời gian đồng bộ thành công vào cột `Last Sync` (cột BZ) bên Sheet Pool để kiểm soát trạng thái.

#### 🎯 Lợi ích Đột phá của Kiến trúc
1. **Hiệu năng Vượt trội (Superb Performance):** Website khách hàng không bao giờ bị quá tải vì chỉ phải truy xuất kho Source cực kỳ tinh gọn.
2. **Bảo mật Tuyệt đối (Absolute Security):** Dữ liệu 5000 căn thô và thông tin nhạy cảm của chủ nhà được cô lập hoàn toàn tại Sheet Pool, không bao giờ bị phơi bày ra môi trường public hay Web client của khách hàng.
3. **Quản lý Tập trung (Centralized Control):** Cho phép anh Khang làm chủ hoàn toàn rổ hàng công khai, tự do tùy biến thông tin bài đăng trực tiếp mà không ảnh hưởng tới dữ liệu gốc được Trang lưu trữ cục bộ.

---

## Verification Plan

### Manual Verification
1. Chọn một căn nhà bất kỳ trong danh sách, thay đổi trường Số nhà và Đường, xác nhận ô Mã Khang Ngô tự động cập nhật khớp chính xác 100% với mã Apps Script.
2. Thử sửa đổi System Prompt AI trong bảng cấu hình (ví dụ: yêu cầu thêm hashtag ở cuối bài viết), nhấn nút **🤖 CHẠY BIÊN TẬP AI**, kiểm tra bài viết sinh ra có phản hồi lập tức theo luật mới hay không.
3. Không điền OpenAI API Key, nhấn chạy AI, giao diện hiện thông báo cảnh báo yêu cầu cập nhật API Key thân thiện.
4. Bấm **"🌐 ĐỒNG BỘ SOURCE"** cho một căn bất kỳ:
   - Xác nhận căn nhà được ghi thành công sang file Google Sheets Source (tab Source).
   - Xác nhận trạng thái trên Curator UI cập nhật tức thì thành `Đã đồng bộ` kèm mốc thời gian thực tế.
   - Xác nhận sidebar hiển thị badge quả địa cầu `🌐` lung linh bên cạnh tên/mã căn đó.

## Files touched
- `curator.html` — Thiết kế các ô settings mới, hiển thị Mã Khang Ngô, nút chạy AI, nút đồng bộ Source, các badge hiển thị trạng thái cào & đồng bộ, hàm mã hóa JS và logic xử lý API `/api/ai/generate`, `/api/sync_to_source/<tk_id>`.
- `curator_server.py` — Tích hợp API endpoint `/api/ai/generate`, `/api/sync_to_source/<tk_id>`, nâng cấp API listings để cung cấp trường trạng thái, lưu cấu hình prompt và api key mới.
- `crawl_pipeline.py` — Bổ sung cột SQLite tự động cho database và di cư dữ liệu.
- `curator_html_data.py` — Đồng bộ hóa Web UI.
