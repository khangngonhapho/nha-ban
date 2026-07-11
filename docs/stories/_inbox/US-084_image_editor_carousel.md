---
id: US-084
status: accepted
date: 2026-06-09
size: M
---

# US-084: Biên tập hình ảnh dạng Carousel và tối ưu hóa nút bấm trên Mobile

## User story
**As an** Admin biên tập rổ hàng bất động sản
**I want** giao diện biên tập hình ảnh dạng Carousel (trượt ảnh ngang) kèm theo bảng điều khiển nút bấm lớn trên Mobile
**So that** tôi có thể dễ dàng xem ảnh lớn, thao tác chọn hình mặt tiền, hình nền, sổ đỏ và bật/tắt hiển thị công khai một cách thuận tiện, chính xác trên các thiết bị di động có độ phân giải cao mà không bị bấm nhầm hay khó nhìn.

## Acceptance
- [ ] **Giao diện Carousel Biên tập:**
  - Thay thế lưới ảnh 3 cột cũ trên mobile bằng một khung nhìn Carousel hiển thị 1 ảnh lớn tại một thời điểm (kích thước lớn, dễ nhìn).
  - Có các nút điều hướng Trái/Phải (`◀` / `▶`) lớn và hỗ trợ thao tác vuốt cảm ứng (Swipe) mượt mà để chuyển ảnh.
  - Có nhãn hiển thị vị trí ảnh hiện tại (Ví dụ: `Ảnh 3 / 15`).
  - Có một dải ảnh thu nhỏ (Thumbnail Strip) nằm ở phía dưới để người dùng có thể trượt và click chọn nhanh ảnh bất kỳ. Thumbnail đang chọn phải có viền nổi bật và tự động cuộn vào giữa vùng nhìn.
- [ ] **Hiển thị Thứ tự Ảnh Công khai (Mới):**
  - Hiển thị chính xác thứ tự xuất hiện của từng ảnh khi public (ví dụ: `#1`, `#2`, `#3`...) dựa trên thuật toán sắp xếp thực tế (Cover luôn là `#1`, tiếp theo là tối đa 2 ảnh Hẻm, và các ảnh Nội Thất public khác).
  - Hiển thị số thứ tự này trực quan trên Slide ảnh lớn hiện tại (ví dụ: `👁️ Công khai #3` thay vì chỉ hiển thị `Hiển Thị`).
  - Hiển thị số thứ tự này trên Badge của các ảnh trong dải Thumbnail (Ví dụ: thay thế dot xanh thông thường bằng một badge tròn xanh lá cây có chứa số thứ tự `#3`).
- [ ] **Tính năng Sắp xếp Thứ tự Ảnh (Mới):**
  - Loại bỏ logic tự động sắp xếp tăng dần theo chỉ số slot khi check hiển thị. Thứ tự hiển thị mặc định sẽ theo thứ tự người dùng bấm chọn (tổng hợp chuỗi index lưu dạng `5,2,3`).
  - Bổ sung 2 nút bấm **Đẩy lên trước ◀** và **Đẩy ra sau ▶** (hoặc nút tráo đổi) bên cạnh nút Hiển thị công khai.
  - Khi click nút sắp xếp, hệ thống tự động tìm kiếm vị trí của ảnh hiện tại trong chuỗi chỉ số tương ứng (`editPublicInteriorIndices` hoặc `editPublicAlleyIndices`), tráo đổi vị trí của nó với ảnh đứng trước hoặc sau, cập nhật lại input ẩn và gọi `window.updateLivePreview()`. Cập nhật lại số thứ tự hiển thị tức thời trên UI.
- [ ] **Quy tắc Lưu Ảnh đặc biệt (Mới - Tương thích Bot đăng tin):**
  - Khi lưu dữ liệu Curation xuống Sheet Source (phục vụ đăng tin bên ngoài):
    - **Ảnh 1** (Cột U trong Source / index 20) bắt buộc phải lưu **Hình Mặt Tiền** (`facadeUrl`).
    - **Ảnh 2** (Cột V trong Source / index 21) bắt buộc lưu **Ảnh Nền** (`coverUrl`).
    - **Ảnh 3 đến 15** lưu các ảnh công khai còn lại theo đúng thứ tự đã chọn.
  - Khi hiển thị trên web client (`khangngonhapho.vercel.app`), trang chi tiết sẽ sử dụng hàm lọc sẵn có để loại bỏ ảnh Mặt tiền (`isFacadeUrl`), giúp **Ảnh Nền** tự động hiển thị ở vị trí số `#1` cho khách hàng xem, bảo mật tuyệt đối ảnh mặt tiền.
- [ ] **Bảng điều khiển Nút bấm lớn (Touch-friendly Controls):**
  - Đặt các nút chức năng ngay dưới ảnh lớn với kích thước tối thiểu 44px (chuẩn Apple/Android cho touch targets).
  - **Nút Mặt Tiền:** Gán/Hủy gán làm ảnh Mặt Tiền. Hiển thị trạng thái khóa màu đỏ (`🔒 Mặt Tiền`) khi active.
  - **Nút Ảnh Nền:** Gán/Hủy gán làm ảnh Nền/Cover. Hiển thị trạng thái ngôi sao màu vàng (`⭐ Ảnh Nền`) khi active.
  - **Dropdown chọn Sổ:** Hỗ trợ menu chọn nhanh để gán làm Sổ 1, Sổ 2, Sổ 3, Sổ 4, Sổ 5 hoặc Không gán (màu tím).
  - **Nút Toggle Hiển thị & Sắp xếp:** Một nút bật/tắt lớn cho việc hiển thị công khai (Public) của ảnh hiện tại. Khi active, hiển thị màu xanh lá (`👁️ Hiển Thị`). Kèm theo 2 nút để thay đổi thứ tự hiển thị: **Đẩy lên trước ◀** và **Đẩy ra sau ▶** (chỉ hiển thị khi ảnh là Public).
  - **Nút Xoay 🔄 & Xem Gốc 🔍:** Các phím bấm kích thước lớn để xoay ảnh (+90°) hoặc mở xem ảnh gốc ở tab mới.
- [ ] **Mini-Badges trên Dải Thumbnail:**
  - Trên mỗi ảnh trong dải thumbnail, hiển thị các ký hiệu nhỏ (Lock 🔒, Star ⭐, Sổ S1-S5, số thứ tự công khai `#X`) để biên tập viên có thể nhìn tổng quan trạng thái của toàn bộ rổ ảnh mà không cần duyệt qua từng slide.
- [ ] **Đồng bộ Dữ liệu thời gian thực:**
  - Mọi thao tác gán Mặt tiền/Nền/Sổ/Hiển thị/Sắp xếp trong bảng điều khiển carousel phải đồng bộ ngay lập tức sang các input ẩn (`editCoverImgUrl`, `editPublicCoverUrl`, `editPublicInteriorIndices`, `editPublicAlleyIndices`, `editSodo1Url` đến `editSodo5Url`) và tự động kích hoạt `window.updateLivePreview()`.

## Solution

> [!note]- Cấu trúc Giao diện Carousel
> ```html
> <!-- Viewport hiển thị ảnh lớn -->
> <div id="imageEditorCarouselViewport" style="position: relative; overflow: hidden; width: 100%; border-radius: 12px; background: #000; aspect-ratio: 4/3; margin-bottom: 8px;">
>   <div id="imageEditorCarouselTrack" style="display: flex; height: 100%; transition: transform 0.3s ease-out; will-change: transform;">
>     <!-- render các slide ảnh lớn -->
>   </div>
>   <button type="button" id="carouselEditPrevBtn" onclick="window.slideImageEditorCarousel(-1)" style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); width: 44px; height: 44px; border-radius: 50%; background: rgba(0,0,0,0.6); border: 1.5px solid rgba(255,255,255,0.25); color: #fff; font-size: 20px; display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 10; font-family: inherit;">◀</button>
>   <button type="button" id="carouselEditNextBtn" onclick="window.slideImageEditorCarousel(1)" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); width: 44px; height: 44px; border-radius: 50%; background: rgba(0,0,0,0.6); border: 1.5px solid rgba(255,255,255,0.25); color: #fff; font-size: 20px; display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 10; font-family: inherit;">▶</button>
>   <div id="carouselEditCounter" style="position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.75); color: #fff; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; z-index: 10;">1 / N</div>
> </div>
> 
> <!-- Dải Thumbnail -->
> <div id="imageEditorThumbStrip" style="display: flex; gap: 8px; overflow-x: auto; padding: 6px 0; margin-bottom: 12px; scroll-behavior: smooth; -webkit-overflow-scrolling: touch; border-bottom: 1px solid rgba(255,255,255,0.08);">
>   <!-- render các thumbnail ảnh nhỏ kèm mini status badges -->
> </div>
> 
> <!-- Bảng điều khiển nút bấm lớn -->
> <div class="carousel-control-panel" style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); padding: 12px; border-radius: 12px; display: flex; flex-direction: column; gap: 10px;">
>   <!-- Hàng 1: Gán vai trò chính -->
>   <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
>     <button type="button" id="panelFacadeBtn" onclick="window.activeImageToggleFacade()" style="height: 44px; border-radius: 8px; font-weight: 700; font-size: 12px; font-family: inherit;">🔒 Mặt Tiền</button>
>     <button type="button" id="panelCoverBtn" onclick="window.activeImageToggleCover()" style="height: 44px; border-radius: 8px; font-weight: 700; font-size: 12px; font-family: inherit;">⭐ Ảnh Nền</button>
>   </div>
>   <!-- Hàng 2: Gán Sổ & Hiển thị -->
>   <div style="display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 8px; align-items: center;">
>     <div style="display: flex; align-items: center; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; height: 44px; padding: 0 10px; box-sizing: border-box;">
>       <label style="font-size: 11px; font-weight: 700; color: #aaa; margin: 0; white-space: nowrap; margin-right: 8px;">📁 Gán Sổ:</label>
>       <select id="activeSodoSelect" onchange="window.activeImageChangeSodo(this.value)" style="flex: 1; background: transparent; color: #fff; border: none; font-size: 12px; font-weight: 700; outline: none; cursor: pointer; font-family: inherit; height: 100%;">
>         <option value="none">Không gán sổ</option>
>         <option value="1">Sổ đỏ 1</option>
>         <option value="2">Sổ đỏ 2</option>
>         <option value="3">Sổ đỏ 3</option>
>         <option value="4">Sổ đỏ 4</option>
>         <option value="5">Sổ đỏ 5</option>
>       </select>
>     </div>
>     <button type="button" id="panelPublicBtn" onclick="window.activeImageTogglePublic()" style="height: 44px; border-radius: 8px; font-weight: 700; font-size: 12px; font-family: inherit; display: flex; align-items: center; justify-content: center; gap: 4px;">👁️ Hiển Thị</button>
>   </div>
>   <!-- Hàng 3: Điều khiển sắp xếp thứ tự hiển thị -->
>   <div id="panelSortControls" style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
>     <button type="button" id="panelSortPrevBtn" onclick="window.activeImageMoveOrder(-1)" style="height: 44px; border-radius: 8px; background: rgba(39, 174, 96, 0.1); border: 1px solid rgba(39, 174, 96, 0.3); color: #2ecc71; font-weight: 700; font-size: 12px; font-family: inherit; display: flex; align-items: center; justify-content: center; gap: 4px;">◀ Đẩy Lên Trước</button>
>     <button type="button" id="panelSortNextBtn" onclick="window.activeImageMoveOrder(1)" style="height: 44px; border-radius: 8px; background: rgba(39, 174, 96, 0.1); border: 1px solid rgba(39, 174, 96, 0.3); color: #2ecc71; font-weight: 700; font-size: 12px; font-family: inherit; display: flex; align-items: center; justify-content: center; gap: 4px;">Đẩy Ra Sau ▶</button>
>   </div>
>   <!-- Hàng 4: Xoay & Zoom -->
>   <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
>     <button type="button" id="panelRotateBtn" onclick="window.activeImageRotate(90)" style="height: 44px; border-radius: 8px; background: rgba(255,191,36,0.12); border: 1px solid rgba(255,191,36,0.3); color: var(--gold); font-weight: 700; font-size: 12px; font-family: inherit; display: flex; align-items: center; justify-content: center; gap: 4px;">🔄 Xoay +90°</button>
>     <button type="button" id="panelZoomBtn" onclick="window.activeImageZoom()" style="height: 44px; border-radius: 8px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); color: #fff; font-weight: 700; font-size: 12px; font-family: inherit; display: flex; align-items: center; justify-content: center; gap: 4px;">🔍 Xem Gốc</button>
>   </div>
> </div>
> ```

## 📋 Implementation Plan
- **Bước 1:** Khởi tạo danh sách ảnh `renderedCards` và theo dõi `window.imageEditorActiveIndex` (mặc định = 0).
- **Bước 2:** Viết lại hàm `renderImageEditorWidget(p)` để render cấu trúc Carousel và dải Thumbnail thay thế cho `#imageEditorGrid` cũ.
- **Bước 3:** Lập trình hàm `window.slideImageEditorCarousel(direction)` và `window.gotoImageEditorSlide(idx)` để điều khiển dịch chuyển thanh trượt Carousel, đồng thời cuộn mượt thumbnail tương ứng vào giữa khung nhìn.
- **Bước 4:** Lập trình các hàm tính toán thứ tự hiển thị:
  - `getImageDisplayOrders(p)`: Dựng bản đồ mapping URL -> số thứ tự hiển thị.
  - `updateImageEditorActiveControls(activeIndex)`: Cập nhật các nút trạng thái Mặt Tiền/Ảnh Nền/Sổ/Hiển Thị/Thứ tự của ảnh đang active.
- **Bước 5:** Triển khai các hàm nghiệp vụ khi bấm nút:
  - `activeImageToggleFacade()`: Gán/Hủy gán mặt tiền, cập nhật input ẩn `#editCoverImgUrl` và các icon badge.
  - `activeImageToggleCover()`: Gán/Hủy gán ảnh nền, cập nhật `#editPublicCoverUrl`, tự động kích hoạt Public.
  - `activeImageChangeSodo(val)`: Gán/Hủy gán sổ đỏ tương ứng `#editSodo1Url` -> `#editSodo5Url`.
  - `activeImageTogglePublic()`: Bật/Tắt check hiển thị, thêm/xóa chỉ số khỏi danh sách và giữ thứ tự thêm.
  - `activeImageMoveOrder(direction)`: Tráo đổi vị trí của chỉ số ảnh đang chọn trong chuỗi `editPublicInteriorIndices` hoặc `editPublicAlleyIndices` để thay đổi thứ tự hiển thị.
  - `activeImageRotate(angle)`: Xoay ảnh thông qua Cloudinary URL transformation.
  - `activeImageZoom()`: Mở URL gốc tab mới.
- **Bước 6 (Mới - Tương thích Bot):** Điều chỉnh hàm `saveSourceChanges` và `saveNewListingFromPool` để tự động ghép **Hình Mặt Tiền** vào cột **Ảnh 1** (index 20) của Source sheet khi xuất bản. Tiếp theo, ghép **Ảnh Nền** vào cột **Ảnh 2** (index 21) và các ảnh công khai còn lại vào cột **Ảnh 3 đến 15**.
- **Bước 7:** Đóng gói CSS Media Queries cho Carousel và Panel điều khiển, tích hợp touch handler vuốt tay (Swipe) trên di động.

## 📝 Task Checklist (TODO)
- [ ] **Thiết kế & Khảo sát:**
  - [ ] Khảo sát lại code quản lý ảnh và các input ẩn trong [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html).
  - [ ] Thống nhất phương án layout Carousel & Controls trên Mobile/Laptop.
- [ ] **Triển khai Code:**
  - [ ] Cấu trúc HTML/CSS mới cho Carousel biên tập & Dải Thumbnail.
  - [ ] Code logic dịch chuyển Carousel, vuốt tay Swipe và auto-scroll thumbnail.
  - [ ] Code logic bảng điều khiển cập nhật các hidden input của form.
  - [ ] Tích hợp cập nhật Mini-Badges trên dải thumbnail theo thời gian thực.
  - [ ] Sửa đổi logic lưu ảnh trong `saveSourceChanges` và `saveNewListingFromPool` để gán Ảnh Mặt Tiền vào Ảnh 1 và Ảnh Nền vào Ảnh 2.
- [ ] **Kiểm thử sơ bộ:**
  - [ ] Test thao tác gán Mặt tiền/Ảnh Nền/Sổ/Hiển Thị trên di động.
  - [ ] Xác nhận lưu Curation và xuất bản thành công không lệch cột.
  - [ ] Dọn dẹp mã nguồn và cập nhật Stories Index.

## Verification Plan

### Automated Tests
- Chạy thử các kịch bản tương tác trên giao diện cục bộ.

### Manual Verification
- **Bước 1:** Mở Web Admin chi tiết một căn nhà (ví dụ căn thô từ Pool).
- **Bước 2:** Kiểm tra Carousel biên tập tải đúng danh sách ảnh, vuốt ngang đổi ảnh mượt mà, số thứ tự chạy chuẩn.
- **Bước 3:** Bấm chọn Mặt Tiền / Ảnh Nền / Sổ 1 / Hiển Thị trên ảnh số 2.
- **Bước 4:** Kiểm tra thumbnail số 2 xuất hiện đủ các badge nhỏ (Lock, Star, Sổ, viền xanh).
- **Bước 5:** Bấm Lưu Curation và kiểm tra dữ liệu đồng bộ chính xác xuống Google Sheets Pool/SQLite.

## Files touched
- `index.html` — Triển khai cấu trúc Carousel biên tập hình ảnh và bảng điều khiển lớn
- `docs/stories/INDEX.md` — Đăng ký story US-084 và cập nhật stats

## 🧠 Retro, Lessons Learned & Good Practices

### 1. Incidents & Root Causes
- **Mobile Transition Glitch (v1.4):**
  - *Sự cố:* Khi sắp xếp lại ảnh hoặc thay đổi trạng thái hình nền/mặt tiền, carousel bị giật lag và tự động chạy slide chạy từ index 0.
  - *Nguyên nhân:* Việc sử dụng `setTimeout` và `offsetHeight` để kích hoạt lại CSS transition sau khi render lại DOM không ổn định trên các luồng vẽ (rendering pipelines) của trình duyệt di động (iOS Safari / Chrome).
  - *Giải pháp:* Chuyển sang sử dụng lớp CSS `.has-transition` động, đặt mặc định `.carousel-slides-track` không có transition, và chỉ thêm lớp `.has-transition` khi người dùng thực hiện vuốt (swipe) hoặc click nút điều hướng.
- **Mobile Layout Stretching & Android Scroll Locking (v1.5 & v1.5.1):**
  - *Sự cố:* Trên mobile, giao diện bị giãn rộng thành desktop mode, hoặc bị khóa cứng không cuộn dọc được trên thiết bị Android.
  - *Nguyên nhân:* 
    1. Bảng bộ lọc ẩn bằng `transform: translateX(100%)` nhưng không có `visibility: hidden`, và thẻ `html`/`body` không khóa `overflow-x: hidden`, khiến trình duyệt di động mở rộng canvas sang `200vw` và tự động zoom nhỏ lại gây kích hoạt Media Query >= 768px (desktop).
    2. Gán `overflow-x: hidden` trên cả `html` và `body` làm Chrome trên Android khóa hoàn toàn chức năng cuộn dọc.
  - *Giải pháp:* Gỡ bỏ thuộc tính `overflow-x: hidden` khỏi thẻ `html` để giải phóng khả năng cuộn của Android, đồng thời thêm `visibility: hidden` cho bảng bộ lọc khi đóng trên điện thoại để triệt tiêu việc tràn viền.

### 2. Good Practices Đúc Kết
- **Quản lý Carousel mượt mà trên di động:** Luôn vô hiệu hóa transition mặc định trên track và điều khiển transition thông qua một class trung gian (như `.has-transition`) được gán động qua JavaScript dựa trên hành động (navigation vs mount/refresh).
- **Tránh dùng `overflow-x: hidden` trên thẻ `html`:** Để ngăn chặn tràn viền ngang trên mobile, chỉ nên đặt `overflow-x: hidden` ở cấp độ `body` (hoặc các wrapper nội dung) kết hợp với thuộc tính `visibility: hidden` cho các panel nằm ngoài màn hình (off-screen drawers).
