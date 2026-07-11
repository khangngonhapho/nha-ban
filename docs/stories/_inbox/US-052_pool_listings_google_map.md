---
id: US-052
status: backlog
date: 2026-05-30
size: M
---

# US-052: Bản đồ Tương tác Admin hiển thị các BĐS lân cận trong rổ hàng (Interactive Curation Map with Nearby Pool Listings)

## User story
**As an** Admin / Curator
**I want** to see an interactive map inside the Admin curation modal showing other listings in the Pool that are geographically close to the property currently being viewed
**So that** I can easily check nearby listings, compare pricing, evaluate the local market density, and navigate directly to those properties with one click, supporting KPI 2 (Tốc độ biên tập).

## Acceptance
- [ ] **Bản đồ Tương tác trong Modal (Interactive Modal Map):**
  - Thay thế iframe Google Maps tĩnh hiện tại trong Modal Curation bằng một container bản đồ tương tác (sử dụng Leaflet.js hoặc Google Maps API).
  - Bản đồ hỗ trợ đầy đủ các thao tác zoom, kéo thả, di chuyển mượt mà.
- [ ] **Định vị & Hiển thị các Căn lân cận (Nearby Listings Detection):**
  - Tự động xác định tọa độ của căn nhà đang xem chi tiết làm tâm (Marker chính nổi bật, ví dụ: màu Vàng Gold hoặc có hiệu ứng vòng tròn phát sáng).
  - Quét qua toàn bộ danh sách rổ hàng trong Pool và Source đã tải ở Client, tính toán khoảng cách địa lý (ví dụ trong bán kính 1.5 km hoặc 2.0 km).
  - Đóng các căn nhà lân cận lên bản đồ bằng các ghim màu sắc phân biệt: màu Đỏ cho căn thô trong Pool, màu Xanh lá cho căn đã được duyệt (Source).
- [ ] **Xem nhanh & Điều hướng tức thì (Marker Info Window & Seamless Navigation):**
  - Khi click vào một ghim bất kỳ, hiển thị một hộp thoại thông tin (Popup) trực quan chứa nội dung trích xuất trực tiếp từ phần đầu của Nội dung chính thô kéo dài đến chữ "tỷ" và **bỏ hoàn toàn tất cả các icon** (Ví dụ hiển thị chính xác: `76.77 Phan Tây Hồ 38 5 5.5 7 8.66 tỷ`).
  - Trong hộp thoại thông tin có tích hợp một nút hành động nổi bật: **"⚡ Xem chi tiết"**.
  - Khi click vào nút này, modal hiện tại tự động chuyển đổi tiêu điểm và tải mượt mà dữ liệu curation của căn nhà mới đó ngay lập tức mà không cần đóng mở modal thủ công.
- [ ] **Nút Cào lại nhanh từ Vercel (One-Click Local Recrawl Bridge):**
  - Tích hợp một nút bấm cực kỳ nhỏ gọn chỉ chứa duy nhất icon **`🔄` (không chứa text)** nằm ngay cạnh các nút thao tác chính trong Modal Curation trên Vercel.
  - Khi admin bấm nút `🔄`, trình duyệt thực hiện gửi một cuộc gọi API ngầm xuyên miền (Cross-Origin Fetch) đến Curator Server chạy tại local (`POST http://localhost:5000/api/listings/<tk_id>/recrawl`).
  - Curator Server dưới máy chạy ngầm sử dụng Cookie Thiên Khôi hiện tại để cào mới căn nhà, bóc tách tọa độ thực tế từ HTML và tự động lưu đè SQLite/Sheets.
  - Sau khi server phản hồi thành công, giao diện Web Admin tự động tải lại dữ liệu mới nhất (gồm cả tọa độ) và vẽ ghim chính xác lên bản đồ lân cận mà không làm gián đoạn luồng làm việc của Admin.

---

## Solution (Thiết kế Giải pháp đề xuất)

### 1. Công nghệ Bản đồ: Lựa chọn Leaflet.js + OpenStreetMap (Khuyên dùng)
Để tránh các ràng buộc về chi phí, hạn mức sử dụng và yêu cầu khóa API phức tạp của Google Maps JavaScript API (dễ gặp thông báo lỗi "For development purposes only" nếu không có tài khoản thanh toán hóa đơn hợp lệ), chúng tôi đề xuất sử dụng thư viện mã nguồn mở **Leaflet.js** kết hợp với **OpenStreetMap (OSM)**:
- **Leaflet.js** là thư viện bản đồ cực nhẹ, tối ưu hóa di động rất tốt và hỗ trợ đầy đủ các tính năng Marker, Popup, Event Listener mà anh yêu cầu.
- Nếu anh Khang Ngô muốn sử dụng Google Maps thực sự, chúng ta có thể tích hợp qua **Google Maps JavaScript SDK**, nhưng anh cần cung cấp API Key hợp lệ và cấu hình trong `index.html`.

### 2. Phương án Thu thập Tọa độ (Geocoding & Scraping Strategy)
Để hiển thị các căn nhà trên bản đồ, hệ thống cần biết tọa độ `vĩ độ (latitude)` và `kinh độ (longitude)` của từng căn. 
*   **Xác nhận thực tế từ HTML Thiên Khôi:** Qua kiểm tra thực tế file HTML thô của Thiên Khôi (`Thien Khoi Group - Nguon Hang.html`), dữ liệu tọa độ đã được lưu trữ sẵn trong cấu trúc HTML tại dòng:
    `<div class="flex items-center justify-between"><p class="text-grayscale-500 text-sm">Tọa độ</p><a class="..." href="https://www.google.com/maps/search/?api=1&amp;query=10.7843645848729,106.6732063516974">...`
    Điều này cực kỳ thuận lợi! Chúng ta không cần dùng dịch vụ dịch ngược địa lý (Geocoding API) tốn kém và chậm nữa, mà có thể trích xuất trực tiếp tọa độ thực của đối tác bằng Regex.
*   **Quy tắc phân vùng Dữ liệu (Không chạm vào Source Sheet):**
    - Chúng ta **TUYỆT ĐỐI KHÔNG thêm cột Tọa độ (Vĩ độ / Kinh độ) vào sheet Source** để giữ cho sheet này cực kỳ sạch sẽ, dung lượng gọn nhẹ tối đa.
    - Cột tọa độ chỉ được lưu trữ duy nhất trong SQLite cục bộ và cột cuối của **sheet Pool** (ví dụ cột `CA: lat`, `CB: lng`).
*   **Cơ chế liên kết tọa độ trên Web Vercel (Client-side Joined Lookup):**
    - Khi Admin đăng nhập Vercel Web Admin, hệ thống tự động tải song song rổ hàng từ cả sheet Source và sheet Pool bảo mật.
    - Khi hiển thị một căn đã lên sóng (Source), Client sẽ tìm kiếm ngược dòng thô của nó trong sheet Pool thông qua mã khóa **`System ID`** độc nhất để trích xuất tọa độ `latitude` và `longitude`.
    - Cách tiếp cận này giúp lấy được tọa độ 100% các căn (kể cả căn thô hay căn đã lên sóng) một cách tức thời ngay trên Client mà không cần thay đổi bất kỳ cột nào của cấu trúc Source Sheet!
*   **Giải pháp Thu thập & Cập nhật ngầm:**
    1. **Trích xuất trực tiếp trong `crawl_pipeline.py`:**
       - Nâng cấp hàm phân tích HTML trong `crawl_pipeline.py` để tìm thẻ `<a>` chứa liên kết `google.com/maps/search/?api=1&query=...`.
       - Dùng Regex trích xuất tọa độ thực tế `vĩ độ` và `kinh độ` từ thuộc tính `href` (ví dụ: `10.7843645848729` và `106.6732063516974`).
       - Lưu trực tiếp 2 giá trị này vào 2 cột mới trong SQLite (`latitude` và `longitude`) ngay khi cào dữ liệu thô.
    2. **Đẩy dữ liệu lên Google Sheets Pool:**
       - Bổ sung 2 cột tọa độ tương ứng ở cuối Google Sheets Pool.
       - Khi xuất bản/cập nhật lên Sheets Pool, server tự động đẩy tọa độ đã cào lên.
    3. **Giải pháp Client-side Fallback (Nếu căn cũ chưa có tọa độ):**
       - Ở phía Client (`index.html`), nếu căn nhà chưa có tọa độ trên Sheets, hệ thống tự động gọi API Geocode miễn phí (Nominatim của OSM) để dịch địa chỉ hiện tại thành tọa độ tâm và hiển thị.

### 3. Thuật toán tính khoảng cách lân cận trên Frontend (Haversine Formula)
Frontend sẽ dùng công thức Haversine để lọc các căn nhà nằm trong bán kính cách căn chủ thể $R \le 1.5$ km:
```javascript
function getDistanceKm(lat1, lon1, lat2, lon2) {
  const R = 6371; // Bán kính Trái Đất (km)
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}
```

### 4. Giao diện Marker Popup & Điều hướng Curation
Popup của từng Marker trên bản đồ sẽ hiển thị nội dung HTML động:
```html
<div class="map-popup-card" style="font-family: inherit; font-size:12px; color:#1c1c1e; padding:4px; text-align:left;">
  <div style="font-weight: 800; margin-bottom:8px; line-height:1.4; color:#2c3e50;">
    ${p.short_title_spec}
  </div>
  <button onclick="window.switchCurationFocus('${p.system_id}')" 
    style="background:#f39c12; color:#1c1c1e; border:none; padding:5px 10px; border-radius:6px; font-size:10.5px; font-weight:800; cursor:pointer; width:100%; text-align:center; transition: all 0.2s;">
    ⚡ Xem Chi Tiết
  </button>
</div>
```
Hàm `window.switchCurationFocus(systemId)` toàn cục sẽ:
1. Đóng popup bản đồ.
2. Gọi `openPoolS(systemId)` hoặc `openS(systemId)` tương ứng để mở thẳng thông tin curation của căn mới ngay tại giao diện hiện tại mà không làm tải lại trang.

---

### 5. Cấu hình Cầu nối CORS liên miền (Local CORS Bridge)
Để cho phép trình duyệt của Admin (đang mở trang Web Vercel `https://*.vercel.app`) gửi được request đến cổng local `http://localhost:5000` mà không bị chính sách an toàn của trình duyệt (Same-Origin Policy) chặn lại, chúng tôi bổ sung bộ lọc CORS động dạng trung gian trong `curator_server.py`:
```python
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response
```
Bộ lọc này hoàn toàn sử dụng thư viện Flask mặc định, không cần cài đặt thêm thư viện ngoài, đảm bảo an toàn tuyệt đối và không gây lỗi khi chạy server.

### 6. Trải nghiệm UI/UX Bản đồ tương tác trên Web Vercel (Premium UI/UX Map Design)
*   **Vị trí Bản đồ trên Vercel:** Thay vì hiển thị iframe Google Maps tĩnh như hiện tại, một bản đồ tương tác động **Leaflet** sẽ được nhúng trực tiếp ngay phần "Bản đồ thực địa" trong Modal Curation trên web Vercel.
*   **Giải pháp Tối ưu không gian Bản đồ nhỏ (Map Workspace Expansion):**
    Để khắc phục triệt để vấn đề không gian bản đồ nhỏ hẹp trong modal khi xem chi tiết (đặc biệt là trên di động), chúng tôi thiết kế giải pháp phản hồi thông minh (Responsive Design):
    - **💻 Trên máy tính (Desktop Split-Screen):** Thay vì xếp dọc toàn bộ trường thông tin khiến bản đồ bị đẩy xuống dưới cùng và chật hẹp, Modal Curation của Admin sẽ tự động chia đôi thành **giao diện 2 cột song song (Split Screen)**:
      - *Cột bên Trái (50%):* Hiển thị Carousel ảnh, Form biên tập Curation, Thông tin đầu chủ và nút Lưu.
      - *Cột bên Phải (50%):* Hiển thị một **Bản đồ tương tác cỡ lớn kéo dài toàn bộ chiều cao của Modal**, giúp Admin có một không gian làm việc thực địa cực kỳ bao quát, vừa biên tập text bên trái vừa click xem vị trí và quét căn lân cận bên phải.
    - **📱 Trên điện thoại (Mobile Full-screen Slide-up):** Trên di động, bản đồ mặc định hiển thị gọn gàng ở độ cao 240px. Tuy nhiên, góc trên bên phải của bản đồ tích hợp một nút **`↙️↗️ Phóng to`** (hoặc icon `🗺️`). Khi chạm vào nút này, bản đồ sẽ tự động mở rộng bung tràn toàn màn hình (Full-Screen overlay) với hiệu ứng trượt kính mờ cực kỳ mượt mà. Admin có thể thoải mái zoom, kéo và bấm xem chi tiết các ghim. Bấm nút đóng `✕` để thu nhỏ bản đồ về vị trí cũ trong modal.
*   **Hiển thị Marker Cao cấp (Visual Markers):**
    - **Căn chủ thể đang xem (Tâm bản đồ):** Ghim bằng một biểu tượng **Gold Ring Pulse** cực kỳ premium, có hiệu ứng vòng tròn vàng phát sáng nhấp nháy chuyển động lan tỏa (CSS Animation) để làm nổi bật vị trí trung tâm.
    - **Căn lân cận trong bán kính 1.5km:** Được đánh dấu bằng các ghim màu sắc sắc nét tương phản cao:
      - 🔴 **Ghim Đỏ:** Các căn thô trong Pool (Chưa lên sóng).
      - 🟢 **Ghim Xanh lá:** Các căn đã duyệt trong Source (Đã lên sóng).
*   **Giao diện Popup Tối giản (Minimalist Specs Tooltip):**
    - Khi admin click vào ghim lân cận bất kỳ, popup bản đồ mở ra bằng hiệu ứng trượt mượt mà. 
    - Nội dung là khối kính mờ (glassmorphism) sang trọng hiển thị **thuần chữ specs thô, tuyệt đối không chứa biểu tượng icon** theo đúng quy chuẩn:
      `76.77 Phan Tây Hồ 38 5 5.5 7 8.66 tỷ`
*   **Nút Xem nhanh & Chuyển đổi Curation mượt mà (Seamless Transition):**
    - Phía dưới dòng specs thô là một nút bấm vàng gold nhỏ nhắn: **`⚡ Xem Chi Tiết`** (hoặc biểu tượng mũi tên chuyển tiếp **`➔`**).
    - Khi click vào nút này, bản đồ tự động dịch chuyển mượt mà (Pan/Fly Animation) lấy căn mới làm tâm, đồng thời toàn bộ nội dung ảnh Carousel, thông tin chủ nhà, form biên tập và nút cào lại của modal curation tự động cập nhật mượt mà sang dữ liệu căn mới ngay tại chỗ mà không cần tắt/mở hay tải lại trang Web Vercel!
*   **Hiệu ứng Loading của nút Cào lại nhanh (🔄 Icon-only Recrawl UX):**
    - Nút cào lại được thiết kế cực kỳ tinh gọn, chỉ hiển thị duy nhất biểu tượng **`🔄` (không chứa text)** nằm kín đáo cạnh nút Lưu.
    - Khi bấm `🔄`, biểu tượng sẽ **tự động xoay tròn liên tục** (`fa-spin` CSS) thể hiện trạng thái đang cào dữ liệu ngầm từ local, đồng thời giao diện hiển thị hiệu ứng mờ nhẹ (glassmorphic skeleton). 
    - Khi cào xong, icon dừng xoay, một Toast Success xanh lá hiện lên báo hiệu và ghim bản đồ tự động dịch về tọa độ xịn vừa cập nhật!

---

## 📋 Implementation Plan

### Giai đoạn 1: Chuẩn bị Cơ sở Dữ liệu & APIs & Cầu nối CORS
- Bổ sung 2 cột `latitude` và `longitude` vào cuối Google Sheets Pool và Source.
- Nâng cấp bộ lọc `@app.after_request` hỗ trợ CORS trong `curator_server.py` (sẽ deploy khi anh Khang tạm dừng tiến trình curator).
- Cập nhật logic trích xuất tọa độ thực tế trực tiếp từ thẻ liên kết định vị Google Maps trong HTML chi tiết Thiên Khôi trong `crawl_pipeline.py`.

### Giai đoạn 2: Tích hợp Bản đồ Leaflet & Nút Cào lại 🔄 vào Frontend
- Tiêm thư viện CSS và JS của Leaflet vào `index.html` qua CDN.
- Thay thế `#mapContainer` dạng iframe tĩnh hiện tại bằng một phần tử `div` bản đồ động.
- Phát triển logic khởi tạo bản đồ, vẽ Marker tâm, tính toán khoảng cách Haversine và kết xuất các marker lân cận trong bán kính 1.5 km.
- Tích hợp nút bấm icon **`🔄`** (chỉ hiện icon, không chứa text) vào hàng nút điều hướng trong Modal Curation.
- Viết hàm gọi API local `http://localhost:5000/api/listings/<tk_id>/recrawl` khi bấm `🔄` và tự động cập nhật lại giao diện khi hoàn thành.
- Khai báo hàm `window.switchCurationFocus()` toàn cục để liên kết mượt mà sự kiện click nút xem chi tiết của popup với modal curation.

### Giai đoạn 3: Tối ưu hóa Trải nghiệm người dùng (UX)
- Tùy biến kiểu dáng marker (Icon Vàng Gold cho căn chủ thể, màu Đỏ cho căn Pool thô, màu Xanh cho căn Source).
- Thêm thanh slider phóng to thu nhỏ bán kính lọc (ví dụ: 500m, 1km, 1.5km, 2km) để admin dễ dàng căn chỉnh ranh giới tìm kiếm lân cận.

---

## 📝 Task Checklist (TODO)
- [ ] Bổ sung trường tọa độ `latitude`, `longitude` vào Schema SQLite và Google Sheets.
- [ ] Nâng cấp `@app.after_request` hỗ trợ CORS trong `curator_server.py`.
- [ ] Viết module bóc tách tọa độ từ HTML Thiên Khôi trong `crawl_pipeline.py`.
- [ ] Viết script batch geocode ngầm cho dữ liệu cũ và module geocode tự động khi cào mới ở Backend.
- [ ] Nhúng CDN Leaflet.js vào `index.html`.
- [ ] Viết module khởi tạo bản đồ động thay thế iframe tĩnh hiện tại.
- [ ] Tích hợp nút icon **`🔄`** vào Modal Curation và viết hàm gọi API local.
- [ ] Viết hàm tính Haversine lọc bán kính và đặt marker lân cận.
- [ ] Thiết kế popup marker HTML dạng text specs thô (không icon).
- [ ] Viết hàm điều hướng curation mượt mà `window.switchCurationFocus()`.
- [ ] Kiểm thử luồng hoạt động thực tế trên Admin Curation Panel.

---

## 🛠️ Update Logic (Drafting while Doing)
*(Sẽ sử dụng để ghi nhận logic thô trong quá trình triển khai thực tế)*

## Verification Plan
### Kiểm thử thủ công:
1. **Kiểm tra Bản đồ tương tác:** Mở modal curation của một căn nhà, kiểm tra xem bản đồ động có hiển thị thay thế iframe tĩnh hay không. Bản đồ có hỗ trợ zoom, kéo mượt mà không bị lỗi.
2. **Kiểm tra Marker lân cận:** Bản đồ hiển thị chính xác marker tâm của căn đang xem và các marker lân cận xung quanh trong bán kính 1.5 km (phân biệt rõ màu ghim Đỏ/Xanh).
3. **Kiểm tra Popup & Điều hướng:** Click vào một marker bất kỳ trên bản đồ, popup hiện lên đầy đủ thông tin ngắn và nút xem chi tiết. Bấm nút xem chi tiết và xác nhận giao diện modal curation đổi thông tin sang căn mới ngay tại chỗ.

## Files touched
- `index.html`
- `crawl_pipeline.py`
- `curator_server.py`

## 🔄 Change Requests (Yêu cầu Thay đổi)
*(Sẽ sử dụng để ghi nhận nhật ký thay đổi yêu cầu của PO khi test hoặc triển khai)*
