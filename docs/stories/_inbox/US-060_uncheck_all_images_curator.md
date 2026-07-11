---
id: US-060
status: accepted
date: 2026-06-02
size: S
---

# US-060: Bỏ chọn tất cả hình ảnh trong biên tập hình Admin cho căn đã lên sóng và mặc định bỏ chọn cho căn chưa lên sóng

## User story
**Với vai trò là** Admin / Người biên tập (Curator)
**Tôi muốn** có một nút bấm nhanh để bỏ chọn toàn bộ hình ảnh (bao gồm hình mặt tiền, hình sổ, hình nền và tất cả hình public) đối với các căn đã lên sóng, và mặc định bỏ chọn toàn bộ hình ảnh đối với các căn chưa lên sóng
**Để** tôi có thể dễ dàng biên tập lại từ đầu mà không cần phải bỏ tích thủ công từng checkbox hay gỡ từng nhãn vai trò hình ảnh, giúp tăng tốc độ làm việc đóng góp vào KPI 1 (Tốc độ biên tập & độ chính xác curation).

## Acceptance
- [ ] **Đối với căn đã lên sóng (curated/published listings):**
  - Xuất hiện một nút `✕ Bỏ All` trong thanh công cụ Image Editor Toolbar của modal Curation.
  - Khi click vào nút này, xuất hiện một hộp thoại thông báo xác nhận: `Bạn có đồng ý xóa hết tất cả các hình đã chọn (bao gồm hình mặt tiền, hình sổ, hình nền và các hình public) để chọn lại từ đầu không?`
  - Nếu Admin nhấn "Đồng ý" (OK):
    - Gỡ bỏ hoàn toàn mọi lớp CSS chỉ định vai trò ảnh: `is-mattien`, `is-anhnen`, `is-sodo`, `is-sodo1`..`is-sodo5`, và `is-public` khỏi tất cả các thẻ hình ảnh trong grid biên tập.
    - Bỏ tích (`checked = false`) tất cả các hộp chọn công khai (`.edit-img-pub-cb`).
    - Làm rỗng toàn bộ giá trị trong các input ẩn: `#editCoverImgUrl`, `#editPublicCoverUrl`, `#editPublicInteriorIndices`, `#editPublicAlleyIndices`, `#editSodo1Url`, `#editSodo2Url`.
    - Gọi hàm `window.updateLivePreview()` để lập tức cập nhật lại diện mạo Preview khách hàng (mô phỏng trắng hình ảnh).
- [ ] **Đối với căn chưa lên sóng (unpublished/pool listings):**
  - Khi mở xem chi tiết một căn chưa lên sóng từ tab Pool, mặc định toàn bộ ảnh trong Grid biên tập phải ở trạng thái bỏ chọn (không có viền đỏ/vàng/tím/xanh lá biểu thị vai trò, không hiển thị các nhãn `🔒 Mặt Tiền`, `⭐ Nền`, `🔒 Sổ`, và các checkbox Hiện đều ở trạng thái unchecked).
  - Khởi tạo giá trị ban đầu của các trường ẩn (`#editCoverImgUrl`, `#editPublicCoverUrl`, `#editPublicInteriorIndices`, `#editPublicAlleyIndices`, `#editSodo1Url`, `#editSodo2Url`) là chuỗi rỗng `""`.
- [ ] **Quy tắc sắp xếp (Sorting Rule) trong Grid biên tập:**
  - Các hình ảnh do người dùng chọn sẽ tự động được đẩy lên trước các hình không chọn. Thứ tự hiển thị cụ thể từ trái qua phải, từ trên xuống dưới là:
    1. Hình Sổ (các ảnh được gán Sổ 1-5).
    2. Hình Mặt tiền (được chọn).
    3. Hình Nền (được chọn).
    4. Các hình chọn công khai còn lại (checked).
    5. Các hình không được chọn (còn lại).
- [ ] **Quy tắc Tích chọn (Image Selection Toggle Rule):**
  - Khi một hình được gán nhãn làm **Sổ** hoặc làm **Mặt tiền**, checkbox công khai (Hiện) tương ứng của hình đó sẽ tự động bị bỏ chọn (`unchecked`).
  - Khi một hình được gán nhãn làm **Nền**, checkbox công khai tương ứng của hình đó sẽ tự động được tích chọn (`checked`).
  - Các hình khác khi click vào checkbox Hiện để chọn công khai sẽ giữ trạng thái `checked`.

## Solution

> [!note]- Input
> ```json
> {
>   "action": "uncheckAllCurationImages",
>   "isFromPoolOnly": "boolean",
>   "imageCardSorting": "Sổ -> Mặt tiền -> Nền -> Public Checked -> Hidden"
> }
> ```

> [!note]- Key logic
> 1. **Khởi tạo Editor Widget (`renderImageEditorWidget`)**:
>    Nếu `p.isFromPoolOnly` là `true` (chưa lên sóng):
>    - Thiết lập các giá trị mặc định cho hidden inputs là rỗng:
>      - `currentCover` = `""`
>      - `currentPublicCover` = `""`
>      - `currentInteriorIndices` = `""`
>      - `currentAlleyIndices` = `""`
>    - Khi gọi `renderImageCardForEdit(type, index, url, p)`, tất cả các cờ kiểm tra vai trò (`isMatTien`, `isAnhNen`, `isSodo`, `isPublic`) sẽ tự động đánh giá thành `false` vì các giá trị mốc so sánh đều rỗng.
>    - Thẻ input `#editSodo1Url` và `#editSodo2Url` cũng được gán giá trị rỗng `""`.
> 2. **Sắp xếp hình ảnh trong Grid biên tập**:
>    - Ngay trước khi render HTML của Grid biên tập hình ảnh, ta tiến hành lọc và sắp xếp lại mảng `cards` (chỉ bao gồm các card có `shouldRender === true`) dựa trên trọng số ưu tiên:
>      - `Trọng số 1` (Sổ): URL trùng khớp sodo1..sodo5.
>      - `Trọng số 2` (Mặt tiền): URL trùng khớp `editCoverImgUrl` (hoặc `img_mat_tien`).
>      - `Trọng số 3` (Nền): URL trùng khớp `editPublicCoverUrl`.
>      - `Trọng số 4` (Các hình chọn Hiện còn lại): Checkbox Hiện được tích (isPublic).
>      - `Trọng số 5` (Hình không chọn): Các hình còn lại.
>    - Mã giả Javascript sắp xếp:
>      ```javascript
>      const renderedCards = cards.filter(c => c.shouldRender);
>      renderedCards.sort((a, b) => getSortWeight(a) - getSortWeight(b));
>      ```
> 3. **Tích chọn / Bỏ chọn tự động**:
>    - Sửa hàm `setImageAsMatTien`: khi click gán Mặt Tiền, tự động tìm checkbox `.edit-img-pub-cb` trên card đó và nếu đang `checked` thì đổi thành `false` và gọi `window.toggleImagePublic(this)`.
>    - Hàm `setImageAsSodo` đã có sẵn logic này (tự động bỏ Hiện khi gán Sổ).
>    - Hàm `setImageAsAnhNen` đã có sẵn logic tự động tích Hiện khi gán Nền.
> 4. **Nút "Bỏ All" cho căn đã lên sóng**:
>    - Trong thanh công cụ `image-editor-toolbar` của `renderImageEditorWidget`:
>      Nếu `!p.isFromPoolOnly` (căn đã lên sóng), hiển thị thêm button:
>      ```html
>      <button type="button" id="toolUncheckAllBtn" onclick="window.uncheckAllCurationImages()" style="background: rgba(192, 57, 43, 0.2); border: 1px solid var(--red); color: var(--red); padding: 5px 12px; border-radius: 6px; font-size: 10.5px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 3px; transition: all 0.2s; font-family: inherit; white-space: nowrap; flex: 1; justify-content: center;">
>        ✕ Bỏ All
>      </button>
>      ```
> 5. **Hàm xử lý bỏ chọn (`window.uncheckAllCurationImages`)**:
>    ```javascript
>    window.uncheckAllCurationImages = function() {
>      const agree = confirm("Bạn có đồng ý xóa hết tất cả các hình đã chọn (bao gồm hình mặt tiền, hình sổ, hình nền và các hình public) để chọn lại từ đầu không?");
>      if (!agree) return;
>      
>      // 1. Reset hidden inputs
>      document.getElementById('editCoverImgUrl').value = '';
>      document.getElementById('editPublicCoverUrl').value = '';
>      document.getElementById('editPublicInteriorIndices').value = '';
>      document.getElementById('editPublicAlleyIndices').value = '';
>      document.getElementById('editSodo1Url').value = '';
>      document.getElementById('editSodo2Url').value = '';
>      
>      // 2. Reset UI card borders & badges
>      document.querySelectorAll('.edit-img-card').forEach(card => {
>        card.classList.remove('is-mattien', 'is-anhnen', 'is-sodo', 'is-sodo1', 'is-sodo2', 'is-sodo3', 'is-sodo4', 'is-sodo5', 'is-public');
>        card.style.borderColor = 'transparent';
>        
>        const badges = card.querySelectorAll('.mattien-lock-badge, .cover-star-badge, .sodo-badge');
>        badges.forEach(b => b.remove());
>        
>        const cb = card.querySelector('.edit-img-pub-cb');
>        if (cb) cb.checked = false;
>      });
>      
>      // 3. Update preview and tool selected (reset tool selection to 'none')
>      if (typeof window.selectImageEditorTool === 'function') {
>        window.selectImageEditorTool('none');
>      }
>      if (typeof window.updateLivePreview === 'function') {
>        window.updateLivePreview();
>      }
>      
>      showToast("Đã bỏ chọn toàn bộ hình ảnh!", "success");
>    };
>    ```
> 
> 6. **Đặc tả ánh xạ dữ liệu khi lưu xuống Google Sheets (Save & Sync Mapping Detail)**:
>    Khi nhấn **Lưu** hoặc **Lên sóng & Lưu**, dữ liệu từ các input ẩn sẽ được bóc tách và ghi đè chuẩn xác xuống Google Sheets theo sơ đồ ánh xạ cột dưới đây để bảo toàn đúng phân loại hình ảnh:
>    *   **Ánh xạ xuống Sheet Source (41 cột):**
>        *   Cột A (`Hinh_mat_tien` - index 0): Ghi công thức tự động hiển thị `=IMAGE(AM{row_index})`.
>        *   Cột AM (`Hình Mặt Tiền` - index 38): Ghi giá trị của ẩn `#editCoverImgUrl` (hình Mặt tiền được chọn). Nếu trống, ghi rỗng `""`.
>        *   Cột U đến AD (`anh_1` đến `anh_10` - index 20 đến 29): Ghi danh sách tối đa 10 hình public sạch theo đúng thứ tự (không bao gồm hình Mặt tiền và hình Sổ). Được dựng từ: Ảnh Nền ở Cột U (`editPublicCoverUrl`), tiếp theo là tối đa 2 ảnh hẻm (được map từ `editPublicAlleyIndices`), tiếp theo là các ảnh nội thất (được map từ `editPublicInteriorIndices`). Các cột thừa được điền rỗng `""`.
>    *   **Ánh xạ xuống Sheet Pool (79 cột) để đồng bộ:**
>        *   Cột AB (`Sơ đồ thửa đất 1` - index 27): Ghi giá trị `#editSodo1Url`.
>        *   Cột AC (`Sơ đồ thửa đất 2` - index 28): Ghi giá trị `#editSodo2Url`.
>        *   Cột AD (`Hình Mặt Tiền` - index 29): Ghi giá trị `#editCoverImgUrl`.
>        *   Cột AO (`Ảnh 1` - index 40): Ghi giá trị `#editPublicCoverUrl`.
>        *   Cột BK (`anhDuocChon` - index 62): Ghi chuỗi chỉ số ảnh nội thất public `#editPublicInteriorIndices` (ví dụ `1,2,5`).
>        *   Cột BL (`anhHemDuocChon` - index 63): Ghi chuỗi chỉ số ảnh hẻm public `#editPublicAlleyIndices` (ví dụ `1`).

## 📋 Implementation Plan
- **Cách tiếp cận:** Tận dụng kiến trúc DOM sẵn có trong modal curation của Admin tại `index.html`. Sửa đổi hàm `renderImageEditorWidget(p)` để tiêm logic mặc định rỗng cho căn chưa lên sóng, sắp xếp lại mảng `cards` trước khi render, sửa đổi `setImageAsMatTien` tự động bỏ check Hiện, và triển khai hàm xử lý `window.uncheckAllCurationImages()`.
- **Các bước triển khai dự kiến:**
  1. Khảo sát cấu trúc hiện có của `renderImageEditorWidget(p)` và cách thức `targetMatTien`, `targetNen`, các biến chỉ số được bóc tách.
  2. Cập nhật hàm `renderImageEditorWidget(p)` để kiểm tra cờ `p.isFromPoolOnly` và gán rỗng các giá trị nếu là căn chưa lên sóng.
  3. Viết hàm/phương thức xác định trọng số và sắp xếp lại mảng `cards` có thuộc tính `shouldRender === true` theo thứ tự: Sổ -> Mặt tiền -> Nền -> Chọn công khai -> Còn lại.
  4. Sửa hàm `setImageAsMatTien` để tự động bỏ check checkbox công khai của card được chọn.
  5. Bổ sung nút bấm `✕ Bỏ chọn tất cả` vào image editor toolbar trong `renderImageEditorWidget(p)` nếu `!p.isFromPoolOnly`.
  6. Định nghĩa hàm `window.uncheckAllCurationImages` xử lý sự kiện click của nút, thực hiện xóa sạch hidden inputs, gỡ bỏ classes, bỏ tích checkboxes, reset công cụ cọ vẽ và gọi live preview.
  7. Đăng ký và kiểm tra các hành vi lưu thay đổi (`saveSourceChanges` và `saveNewListingFromPool`) đảm bảo hoạt động chuẩn khi data rỗng.

## 📝 Task Checklist (TODO)
- [ ] **Thiết kế & Khảo sát:**
  - [ ] Khảo sát code biên tập hình ảnh hiện tại trong `index.html`
  - [ ] Thống nhất thuật toán tính trọng số sắp xếp hình ảnh
- [ ] **Triển khai Code:**
  - [ ] Cập nhật logic render mặc định uncheck cho căn chưa lên sóng trong `renderImageEditorWidget`
  - [ ] Triển khai hàm sắp xếp mảng `cards` theo thứ tự ưu tiên trong `renderImageEditorWidget`
  - [ ] Cập nhật hàm `setImageAsMatTien` tự động uncheck checkbox Hiện
  - [ ] Thêm nút "Bỏ chọn tất cả" và định nghĩa hàm `window.uncheckAllCurationImages`
  - [ ] Đảm bảo đồng bộ và hoạt động tốt với bộ live preview và các nút lưu
- [ ] **Kiểm thử sơ bộ:**
  - [ ] Mở thử một căn đã lên sóng, bấm nút "Bỏ chọn tất cả", xác nhận thông báo, kiểm tra xem UI và Live Preview có bị xóa sạch các ảnh đã chọn không
  - [ ] Mở thử một căn chưa lên sóng (từ tab Pool), kiểm tra xem giao diện có mặc định uncheck toàn bộ ảnh không
  - [ ] Kiểm tra xem ảnh trong Grid có được sắp xếp đúng thứ tự (Sổ -> Mặt tiền -> Nền -> Public Checked -> Còn lại) không
  - [ ] Kiểm tra xem khi gán Mặt tiền hay Sổ thì checkbox Hiện có tự động bỏ tích không
  - [ ] Lưu thay đổi/Lên sóng và kiểm tra đồng bộ chính xác dữ liệu rỗng về Google Sheets

## 🛠️ Update Logic (Drafting while Doing)
*(Sẽ sử dụng để ghi nhận logic thô trong quá trình triển khai thực tế)*

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)
*(Sẽ sử dụng để ghi nhận lại sau khi tính năng được nghiệm thu)*

## Verification Plan

> [!check]- Manual Verification
> 1. Đăng nhập trang Admin bằng mật khẩu hoặc silent login Google thành công.
> 2. **Kiểm thử căn chưa lên sóng:**
>    - Mở một căn thô bất kỳ trong tab Pool (chưa lên sóng).
>    - Kiểm tra xem phần BIÊN TẬP HÌNH ẢNH có mặc định trống hoàn toàn các nhãn Mặt Tiền, Nền, Sổ, và các checkbox Hiện đều ở trạng thái unchecked không.
>    - Thử chọn vài ảnh và bấm "Lưu thay đổi".
> 3. **Kiểm thử căn đã lên sóng:**
>    - Mở một căn bất kỳ đã lên sóng (đang hiển thị ở tab Tất cả).
>    - Bấm nút "✕ Bỏ chọn tất cả" trên toolbar biên tập ảnh.
>    - Xác nhận hộp thoại cảnh báo: nhấn Cancel để xem có giữ nguyên không, nhấn OK để xem tất cả nhãn/viền/checkbox và Live Preview dưới có bị xóa sạch không.
>    - Thử bấm "Lưu" để kiểm tra đồng bộ lên Google Sheets.

## Files touched
- `index.html` — Cập nhật `renderImageEditorWidget` và thêm hàm `uncheckAllCurationImages`

## 🔄 Change Requests (Yêu cầu Thay đổi)
*(Sẽ sử dụng để ghi nhận nhật ký thay đổi yêu cầu của PO nếu có)*
