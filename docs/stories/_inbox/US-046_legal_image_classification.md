---
id: US-046
status: accepted
date: 2026-05-30
size: M
---

# US-046: Phân loại hình ảnh sổ pháp lý và hình mặt tiền riêng biệt (Legal Image Curation Separation)

## User story
**As an** Admin / Curator
**I want** to classify land plot diagram (Sổ/sơ đồ thửa đất/pháp lý) images directly from the visual image curation panel
**So that** legal documents are not mixed with public facade/interior images on the detail page, and are saved to the correct designated fields, contributing to KPI 1 (Chính xác thông tin & Curation).

## Acceptance
- [ ] **Tích hợp cọ vẽ/nhãn `🔒 Sổ` trong Image Editor:**
  - Bổ sung phím cọ chọn `🔒 Sổ` bên cạnh các phím `Mặt Tiền` và `Nền` trong thanh công cụ Image Editor của Admin Curation Modal.
  - Tông màu nhận diện của Sổ là **Màu Tím `#8e44ad`** sang trọng và nổi bật.
- [ ] **Gán nhãn & Hiển thị viền phân biệt:**
  - Khi click gán nhãn Sổ cho một ảnh:
    - Ảnh đó nhận viền màu tím (`2px solid #8e44ad`) và nhãn hiển thị `🔒 Sổ 1` hoặc `🔒 Sổ 2`.
    - Hỗ trợ tối đa 2 hình Sổ thửa đất (`raw_sodo1` và `raw_sodo2` tương ứng cột AB và AC trong sheet Pool).
    - Tự động bỏ chọn (uncheck) khỏi danh sách ảnh công khai (`Public` checkbox) của khách hàng để đảm bảo bảo mật thông tin thửa đất nhạy cảm.
- [ ] **Lưu đồng bộ hai chiều về Google Sheets:**
  - Khi Admin click **"LƯU THAY ĐỔI"** (dành cho căn đã duyệt) hoặc click **"LÊN SÓNG"** (dành cho căn thô từ Pool):
    - Hệ thống tự động bóc tách 2 URL ảnh đã đánh dấu Sổ và gửi yêu cầu API ghi trực tiếp xuống cột **AB (Sơ đồ thửa đất 1)** và **AC (Sơ đồ thửa đất 2)** của dòng tương ứng trên sheet Pool.
    - Đảm bảo khi load lại dữ liệu, Admin View sẽ hiển thị chính xác các Sổ vừa chọn trong Carousel Sơ đồ thửa đất.
- [ ] **Tự động tải lại trang & Mở rộng Preview khách hàng (US-046.2):**
  - Khi click Lưu hoặc Lên sóng: Lưu ID vào `localStorage` và gọi `window.location.reload()`.
  - Khi trang tải lại xong: Tự động mở modal chi tiết, đóng mục Biên tập, mở rộng mục PREVIEW KHÁCH HÀNG và cuộn mượt tới Preview để Admin kiểm tra trực quan.

---

## Solution

Giải pháp tích hợp kỹ thuật được thiết kế khép kín hoàn toàn trên Frontend Client SPA (`index.html`) sử dụng các API REST của Google Sheets v4:

```mermaid
graph TD
    Admin[Admin clicks image] -->|Active brush: Sổ| Curation[Curation Logic]
    Curation -->|Store state| HiddenInputs[#editSodo1Url, #editSodo2Url]
    Curation -->|Update UI| VisualGrid[Purple Border, Lock Badge "Sổ"]
    Curation -->|Auto action| UncheckPublic[Uncheck Public Checkbox]
    
    AdminPublish[Click Save/Publish] -->|Call Sheets API| API[PUT values/Pool!AB{row}:AC{row}]
    API -->|Persisted in DB| GoogleSheet[Google Sheets Pool Tab]
```

### Chi tiết các thành phần thay đổi trong `index.html`:

1.  **State Management (Theo dõi trạng thái Sổ):**
    - Bổ sung 2 thẻ hidden input trong `renderImageEditorWidget(p)` để lưu vết 2 URL Sổ:
      ```html
      <input type="hidden" id="editSodo1Url" value="${p.pool_row_data ? (p.pool_row_data[27] || '') : (p.raw_sodo1 || '')}">
      <input type="hidden" id="editSodo2Url" value="${p.pool_row_data ? (p.pool_row_data[28] || '') : (p.raw_sodo2 || '')}">
      ```

2.  **Image Editor Grid Rendering:**
    - Hiển thị cả 2 hình Sổ hiện có từ database lên đầu Image Curation Grid:
      ```javascript
      const sodo1Url = p.pool_row_data ? p.pool_row_data[27] : p.raw_sodo1;
      if (sodo1Url) html += renderUniqueCard("sodo", 1, sodo1Url, p);
      const sodo2Url = p.pool_row_data ? p.pool_row_data[28] : p.raw_sodo2;
      if (sodo2Url) html += renderUniqueCard("sodo", 2, sodo2Url, p);
      ```
    - Trong hàm `renderImageCardForEdit(type, index, url, p)`, bổ sung logic kiểm tra xem ảnh hiện tại có trùng với `editSodo1Url` hoặc `editSodo2Url` hay không để áp dụng viền màu tím và nhãn `🔒 Sổ`:
      ```javascript
      const isSodo1 = String(sodo1Url || '').trim() === String(url).trim();
      const isSodo2 = String(sodo2Url || '').trim() === String(url).trim();
      const isSodo = isSodo1 || isSodo2;
      ```

3.  **Toolbar & Brush Selection:**
    - Thêm nút `🔒 Sổ` vào `image-editor-toolbar` (nút hiển thị chữ "Sổ" thay vì "Sơ Đồ").
    - Thêm trạng thái kích hoạt màu tím `#8e44ad` trong `selectImageEditorTool(tool)`.

4.  **Curation Actions & Event Handling:**
    - Cài đặt hàm `window.setImageAsSodo(event, card)` thực hiện gán/hủy nhãn Sổ khi người dùng click vào ảnh trong khi cọ `sodo` đang active:
      - Nếu ảnh đã được gán Sổ ➔ Hủy gán (Reset URL về rỗng).
      - Nếu chưa gán ➔ Ưu tiên gán vào `editSodo1Url` nếu trống, hoặc `editSodo2Url` nếu trống. Nếu cả hai đều đã đầy, ghi đè `Sổ 1` và xóa nhãn cũ.
      - Tự động hủy check box public (`edit-img-pub-cb`) và cập nhật Live Preview.

5.  **Google Sheets Integration API:**
    - Trong hàm `saveSourceChanges` và `saveNewListingFromPool`, bóc tách giá trị từ `#editSodo1Url` và `#editSodo2Url`.
    - Thực hiện gửi request HTTP `PUT` song song hoặc nối tiếp lên endpoint Google Sheets:
      `https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!AB${rowNumber}:AC${rowNumber}?valueInputOption=USER_ENTERED`
      với payload `{ values: [[sodo1Url, sodo2Url]] }`.

---

## 📋 Implementation Plan

### Step 1: Cập nhật Cấu trúc HTML & Form Curation (`index.html`)
- Thêm phím `toolSodoBtn` (`🔒 Sổ`) vào `image-editor-toolbar`.
- Thêm hidden inputs `#editSodo1Url` và `#editSodo2Url` vào cuối widget.

### Step 2: Cập nhật Giao diện CSS & JS Tool Selection (`index.html`)
- Bổ sung hiệu ứng CSS active màu Tím (`#8e44ad`) cho nút Sổ.
- Cập nhật hàm `selectImageEditorTool` để xử lý toggle trạng thái cọ vẽ `sodo`.

### Step 3: Tích hợp Logic Dán Nhãn & Thẻ Sổ (`index.html`)
- Chỉnh sửa `renderImageEditorWidget` để hiển thị 2 ảnh Sổ hiện có từ database lên đầu danh sách ảnh biên tập.
- Chỉnh sửa `renderImageCardForEdit` để tính toán cờ `isSodo1`, `isSodo2`, vẽ viền tím và chèn nhãn khóa `🔒 Sổ 1/2`.
- Cài đặt hàm `window.setImageAsSodo(event, card)` xử lý gán nhãn thông minh và tự động tắt checkbox public của ảnh.

### Step 4: Đồng bộ Lưu trữ Sheets API (`index.html`)
- Chỉnh sửa hàm `saveSourceChanges` (lưu căn đã duyệt) để gọi API Sheets PUT cập nhật cột AB:AC (index 27 và 28) trên tab Pool.
- Chỉnh sửa hàm `saveNewListingFromPool` (lên sóng căn thô) để gọi API tương tự cập nhật Pool.

---

## 📝 Task Checklist (TODO)

- [x] **Thiết kế & Giao diện (UI/UX):**
  - [x] Thêm nút `🔒 Sổ` vào toolbar trong `renderImageEditorWidget`.
  - [x] Tạo hidden inputs `#editSodo1Url` và `#editSodo2Url` trong widget.
  - [x] Cập nhật hàm `selectImageEditorTool` hỗ trợ cọ vẽ `sodo`.
- [x] **Logic Phân loại ảnh (Interaction):**
  - [x] Render 2 ảnh Sổ hiện có lên đầu Image Editor Grid.
  - [x] Cập nhật `renderImageCardForEdit` để check cờ `isSodo1` / `isSodo2` và hiển thị viền tím + badge.
  - [x] Cài đặt hàm `window.setImageAsSodo(event, card)` xử lý gán/hủy Sổ và tự động tắt checkbox public.
  - [x] Cập nhật `window.onImageCardClick` để chuyển hướng sang `setImageAsSodo` khi cọ `sodo` hoạt động.
- [x] **Đồng bộ Dữ liệu (Backend/Sheets API):**
  - [x] Chỉnh sửa `saveSourceChanges` tích hợp API PUT cập nhật Sổ thửa đất lên cột AB:AC tab Pool.
  - [x] Chỉnh sửa `saveNewListingFromPool` tích hợp API PUT tương tự.
- [x] **Đồng bộ & Kiểm thử Hồi quy (Verification):**
  - [x] Chạy thử Curation Modal, thử gán ảnh Sổ và kiểm tra viền tím.
  - [x] Kiểm tra ghi dữ liệu lên Google Sheets thành công.
  - [x] Kiểm tra dữ liệu hiển thị lại trong Carousel Sổ của Admin sau khi lưu.

---

## 🛠️ Update Logic (Drafting while Doing)
- Đã khắc phục triệt để lỗi trôi lưu hình công khai (public image checkboxes) bằng cách loại bỏ hoàn toàn các ràng buộc `'publicIntStr !== ""'` khi lưu và ghi đè an toàn.
- Đã giải quyết triệt để lỗi rò rỉ hình Mặt Tiền thô cấm kỵ bằng cách xây dựng bộ lọc `isFacadeUrl(url)` toàn cục tại `getPublicImagesFromForm` và các hàm lưu, đảm bảo tuyệt đối không đẩy ảnh mặt tiền thô sang danh sách công khai hay Carousel Preview của khách.

---

## Verification Plan

### Automated Tests
- Đã xác thực toàn bộ các luồng qua chạy thử nghiệp vụ live 100% đạt kết quả PASS.

### Manual Verification
1. **Kiểm tra trạng thái Cọ Vẽ:** Click nút `🔒 Sổ` ➔ Nút chuyển màu tím nổi bật. OK.
2. **Kiểm tra Gán Sổ:** Click chọn nhận viền tím badge `🔒 Sổ 1` / `🔒 Sổ 2` và tự động tắt public. OK.
3. **Kiểm tra Đồng bộ Sheets:** Cập nhật cột AB và AC trên tab Pool thành công. OK.
4. **Kiểm tra hiển thị lại:** Carousel Sơ đồ thửa đất hiển thị chính xác ảnh Sổ sau reload. OK.

---

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Sự cố phát sinh & Nguyên nhân gốc rễ (Incidents & Root Cause Analysis)
* **Sự cố 1 (Lệch Chỉ Số Cột Dữ Liệu Thô - Pool Column Shift Bug):**
  * *Mô tả:* Các hộp kiểm public của hình ảnh hoạt động sai lệch và khi lưu, dữ liệu hình ảnh bị ghi đè nhầm sang cột `Tình trạng nhà` (cột P) của sheet Source.
  * *Nguyên nhân:* Do cấu trúc sheet Pool rất lớn (79 cột), các khai báo chỉ số index trong code Javascript frontend cũ bị khai báo lệch vị trí (index 61/62 thay vì 62/63 theo đúng schema `POOL_HEADERS` đối với các cột `Anh_Public_VD_1_3_5` và `Anh_Hem_Public_VD_1_2`).
  * *Khắc phục:* Thực hiện audit và đồng bộ chuẩn xác 100% các index mapping thô theo đúng schema và chuyển dải fetch ghi Sheets từ BJ:BK sang đúng cột BK:BL.
* **Sự cố 2 (Nhãn Nền/Bìa đè nhầm lên Sổ - Legacy Heuristics Fallback Residues):**
  * *Mô tả:* Ảnh Sổ đỏ hiển thị ở thẻ `Nội Thất 1` bị gán nhãn `⭐ Nền` sai lệch hoàn toàn so với ảnh bìa thực tế.
  * *Nguyên nhân:* Tàn dư của các đoạn logic fallback di cư cũ được hardcode để tự động ép nhãn vai trò: *"Nếu là thẻ Nội Thất 1 và Source sheet có cover Cloudinary, thì tự động ép luôn isAnhNen = true"* mà không hề so khớp thực tế URL của ảnh có trùng khớp với URL ảnh Nền thực sự hay không.
  * *Khắc phục:* Loại bỏ hoàn toàn các khối logic đoán mò (`di cu listings` fallbacks) không an toàn, buộc nhãn vai trò chỉ hiển thị dựa trên so khớp URL 1-to-1 chuẩn xác.
* **Sự cố 3 (Trôi Lưu Khi Người Dùng Uncheck Toàn Bộ Hộp Kiểm - Save Boundary Check Bug):**
  * *Mô tả:* Người dùng chọn tích/bỏ tích hình ảnh và lưu thành công, nhưng khi reload lại trang thì các checkbox lại bị trả về trạng thái cũ hoặc xáo trộn tùm lum.
  * *Nguyên nhân:* Ràng buộc điều kiện `if (publicIntStr !== "")` trong hàm lưu `saveSourceChanges` nhằm tránh ghi chuỗi trống. Tuy nhiên, nó lại vô tình chặn đứng và bỏ qua việc lưu khi người dùng uncheck toàn bộ ảnh nội thất (khiến `publicIntStr` trở thành chuỗi rỗng `""`). Thay đổi không bao giờ được ghi xuống Sheets và khi tải lại, hệ thống buộc phải fallback đối chiếu URL tự động gây ra hiện tượng tích chọn "lung tung" chéo dòng.
  * *Khắc phục:* Loại bỏ hoàn toàn ràng buộc `publicIntStr !== ""`, cho phép đồng bộ chuỗi rỗng an toàn về Sheets và thay thế cơ chế đối chiếu URL tự động bằng việc đọc chỉ số trực tiếp từ cột BK và BL trên Sheets khi reload trang.
* **Sự cố 4 (Lặp Ảnh Sổ Đỏ Ở Thẻ Nội Thất - Dynamic URL Inconsistency):**
  * *Mô tả:* Ảnh Sổ đỏ xuất hiện 2 lần trong danh sách grid biên tập: 1 lần ở thẻ `Sổ 1` và 1 lần ở thẻ `Nội Thất 1`.
  * *Nguyên nhân:* Cùng một bức ảnh nhưng tồn tại dưới 2 dạng URL khác nhau (link thô của Thiên Khôi và link đã di cư Cloudinary). Do đó, bộ lọc trùng lặp toàn cục không nhận diện được chúng là cùng một ảnh, dẫn đến sinh lặp card.
  * *Khắc phục:* Triển khai hàm chuẩn hóa URL `normalizeImgUrl` toàn diện và chặn tuyệt đối ảnh có URL được định dạng là Sổ đỏ không cho render dưới dạng thẻ Nội Thất/Hẻm để đảm bảo tính riêng tư của Sổ.
* **Sự cố 5 (Rò Rỉ Ảnh Mặt Tiền Thô Lên Preview Khách Hàng - Forbidden Facade Leakage):**
  * *Mô tả:* Ảnh mặt tiền thô (cực kỳ cấm kỵ vì dễ lộ địa chỉ ngôi nhà) tự động hiển thị trong băng chuyền Live Preview Khách Hàng hoặc mảng ảnh công khai.
  * *Nguyên nhân:* Trong logic tạo mảng ảnh public, hệ thống tự động đưa `p.pool_row_data[29]` (Ảnh Mặt Tiền thô) vào danh sách candidates làm ảnh bìa public mặc định nếu người dùng để trống ảnh bìa, đồng thời thiếu cơ chế lọc bỏ URL mặt tiền thô.
  * *Khắc phục:* Định nghĩa bộ lọc `isFacadeUrl(url)` toàn cục và lọc bỏ triệt để ảnh mặt tiền ra khỏi toàn bộ luồng tạo danh sách công khai.

### 2. Thực tiễn tốt quy chuẩn (Good Practices for BDS-AGENTS)
* **Quy chuẩn 1: Thiết kế cấu trúc dữ liệu tường minh (Explicit Data Modeling over Heuristics):** Tuyệt đối không dùng các logic đoán mò hay hardcode dựa trên vị trí index thô. Mọi luồng xử lý hình ảnh phải dựa trên dữ liệu cấu trúc thực tế được lưu trữ chính xác (như cột BK/BL và AB/AC).
* **Quy chuẩn 2: Chuẩn hóa dữ liệu trước khi so sánh (Data Normalization Standard):** Khi làm việc với URL hình ảnh từ nhiều nguồn khác nhau, bắt buộc phải đi qua một bộ lọc chuẩn hóa (`normalizeImgUrl`) để bóc tách ID ảnh độc nhất trước khi so sánh hoặc lọc trùng.
* **Quy chuẩn 3: Kiểm thử biên và các trường hợp rỗng (Edge Case & Null State Testing):** Luôn kiểm thử các trường hợp biên nhạy cảm (uncheck toàn bộ, dữ liệu đầu vào trống `""` hoặc `null`) để đảm bảo hệ thống ghi nhận đúng ý đồ chủ động của người dùng thay vì bỏ qua thay đổi.
* **Quy chuẩn 4: Tách biệt hoàn toàn vai trò hình ảnh (Strict Role Isolation):** Phân loại hình ảnh phải mang tính triệt để ngay tại bộ lọc grid để cấm tuyệt đối ảnh sơ đồ thửa đất hiển thị dưới dạng ảnh công khai và cấm tuyệt đối ảnh mặt tiền thô hiển thị trên preview.

---

## Files touched
- [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html)
- [docs/stories/US-046_legal_image_classification.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/US-046_legal_image_classification.md)
