---
id: US-039
status: accepted
date: 2026-05-28
size: L
---

# US-039: Admin Curation Dashboard trên Web Vercel (View Admin riêng kết nối song song Pool & Source)

## User Story
**As an** Admin / Product Owner Khang Ngô  
**I want** một giao diện quản trị riêng (View Admin) chạy trực tiếp trên website (Vercel) tích hợp song song dữ liệu thô từ Sheet Pool và dữ liệu custom từ Sheet Source  
**So that** tôi có thể xem đầy đủ thông tin crawl tuyệt mật từ nguồn thô (Nội dung chính, SĐT đầu chủ, hình thửa, link FB...) nhằm nắm bắt thông tin, đồng thời chỉnh sửa nhanh các trường dữ liệu bổ trợ (Note, hướng nhà, phòng ngủ, WC...) trực tiếp trên web và lưu thẳng về Sheet Source mà không cần mở file Excel cồng kềnh hay làm lộ thông tin nhạy cảm cho khách hàng.

---

## Acceptance Criteria
- [x] **Bảo mật truy cập (Security Shield):** Chỉ cho phép người dùng đã đăng nhập Google OAuth2 có quyền truy cập cụ thể (Admin) được xem và tương tác với giao diện này.
- [x] **Bộ nạp dữ liệu song song (Dual-Sheet Data Ingestion):**
  - Đọc toàn bộ dữ liệu từ **Sheet Pool** (tab Pool) làm nguồn dữ liệu thô (Chỉ Đọc - Read-Only).
  - Đọc toàn bộ dữ liệu từ **Sheet Source** (tab Source) làm nguồn dữ liệu biên tập (Có Thể Ghi - Writeable).
  - So khớp (matching) tự động dữ liệu giữa hai sheet dựa trên khóa duy nhất là **Mã Hàng** (ví dụ: `TK-534B8B`) hoặc `System ID`.
- [x] **Bố cục giao diện Curation Panel cho Admin:**
  - **Cột Trái (Sidebar):** Danh sách các căn bất động sản đã lên sóng (đọc từ Sheet Source) kèm bộ lọc tìm kiếm nâng cao dành riêng cho Admin.
  - **Cột Phải (Form Chi Tiết):** Form hiển thị thông tin chia làm 2 khu vực trực quan:
    1. **Khu vực Thông tin Thô (Pool - Read-Only):**
       - `Nội dung chính` (văn bản thô crawl).
       - `Mô tả chi tiết` (USP gốc từ Thiên Khôi).
       - `Sơ đồ thửa đất` (Hiển thị tất cả ảnh từ link ảnh cột `Sơ đồ thửa đất 1`, `Sơ đồ thửa đất 2`).
       - `Tên đầu chủ` và `Số điện thoại đầu chủ`.
       - `Điểm Facebook` (hiển thị dạng link bấm mở được).
    2. **Khu vực Chỉnh sửa Custom (Source - Editable & Write-Back):** Các trường này hiển thị dạng ô nhập liệu (input, select, checkbox) cho phép chỉnh sửa:
       - `Note` (Ghi chú riêng của admin).
       - `Hướng` (Đông, Tây, Nam, Bắc...).
       - `Đường trước nhà (m)`.
       - `Đánh giá (Admin)` (Hàng ngon / Hàng thường / Hàng lỗi).
       - `Ngủ trệt (Admin)` (Checkbox).
       - `CHDV (Admin)` (Checkbox).
       - `Số phòng ngủ`.
       - `Số nhà vệ sinh` (WC).
       - `Tiêu đề Public` (Tiêu đề đăng BDS hiển thị công khai).
- [x] **Bộ lọc nâng cao Admin (Advanced Search Filters):**
  - Hỗ trợ ô tìm kiếm văn bản tự do (text search) cho phép quét nhanh qua 3 trường tuyệt mật nằm trong Sheet Pool: `Tên đầu chủ`, `Nội dung chính`, và `Mô tả chi tiết`.
- [x] **Cơ chế ghi ngược dữ liệu (Write-Back to Source):**
  - Khi bấm nút **"LƯU THAY ĐỔI"**:
    - Hệ thống tìm dòng tương ứng trên **Sheet Source** dựa trên cột `Mã Hàng` hoặc `System ID`.
    - Ghi đè các cột custom đã được chỉnh sửa ngược về dòng đó trên Sheet Source qua Google Sheets API Client-side.
    - Hiển thị Toast thông báo thành công xanh lá tươi dạng premium.

---

## Proposed Architecture & Technical Plan

### 1. Phân quyền & Định tuyến (Routing & Auth)
* Giao diện Admin Curation sẽ được tích hợp trong file `index.html` của website (hoặc một trang biệt lập `admin.html` để tách biệt mã nguồn).
* Tận dụng Google OAuth2 Client-side hiện có của anh Khang (đã có scope sheets read/write). Chỉ kích hoạt View Admin sau khi token được xác thực và email khớp với email của Admin (`khangngo...`).

### 2. Luồng dữ liệu & So khớp (Client-side Merging)
```
          [Sheet Pool]                       [Sheet Source]
        (Dữ liệu thô - A:CA)               (Dữ liệu custom - A:AO)
                 │                                  │
                 ▼                                  ▼
           Read via API                       Read via API
                 │                                  │
                 └───────────────┬──────────────────┘
                                 ▼
                         [Client-Side Match]
                      Khóa: Mã Hàng / System ID
                                 │
                                 ▼
                     [Giao diện Admin Curation]
             ┌───────────────────────┬────────────────────────┐
             ▼                       ▼                        ▼
     Pool Info (Read-Only)    Source Custom (Edit)    Advanced Filters
    - SĐT đầu chủ, FB        - Note, hướng, ngủ trệt - Search thô Pool
    - Sơ đồ thửa 1, 2        - Tiêu đề public, WC    - Tên đầu chủ...
                                     │
                                     ▼
                            Click [LƯU THAY ĐỔI]
                                     │
                                     ▼
                            Ghi ngược về Source
                          (Chỉ cột custom edit)
```

### 3. Logic Tìm kiếm & Bộ lọc nâng cao (Advanced Filters)
* Khi Admin nhập từ khóa vào ô tìm kiếm Admin, JavaScript client-side sẽ filter mảng dữ liệu gộp.
* Biểu thức tìm kiếm:
  ```javascript
  const matched = poolRows.filter(row => {
    const tenDauChu = (row.tenDauChu || '').toLowerCase();
    const noiDungChinh = (row.noiDungChinh || '').toLowerCase();
    const moTaChiTiet = (row.moTaChiTiet || '').toLowerCase();
    const q = query.toLowerCase();
    return tenDauChu.includes(q) || noiDungChinh.includes(q) || moTaChiTiet.includes(q);
  });
  ```

---

---

## 📱 UI/UX Mobile-First Design Concept (Giao diện Điện thoại Tối ưu)

Vì 90% thời gian giao dịch BĐS và tra cứu thông tin của anh Khang diễn ra trực tiếp trên điện thoại di động khi đi thực địa, thiết kế UI/UX tuân thủ triệt để nguyên tắc **Mobile-First** và tận dụng tối đa hạ tầng layout hiện có:

### 1. Phân vùng Trực quan (Public vs Private Mode)
* **Navbar / Header (Giữ nguyên Auth Button hiện có):** 
  * Mặc định hiển thị logo và bộ lọc công khai cho khách hàng.
  * Giữ nguyên nút đăng nhập bằng **icon Google Login** hiện tại ở header của website. Khi Admin click đăng nhập thành công bằng tài khoản Google có quyền admin, website tự động chuyển sang chế độ **`body.is-admin` (Admin View)** mà không cần thay đổi hay can thiệp vào cơ chế login ổn định hiện tại.

### 2. Bộ lọc nâng cao của Admin (Hòa hợp, Không xung đột Search hiện tại)
* **Giải pháp chống xung đột layout:** Thay vì tạo Bottom Sheet mới (dễ gây xung đột layout và lỗi CSS với thanh search `#searchBar` và collapsible filter `#filterPanel` hiện tại của website):
  * **Tích hợp trực tiếp vào `#filterPanel`**: Khi ở chế độ `is-admin`, bên trong bộ lọc `#filterPanel` hiện có sẽ xuất hiện thêm một **ô nhập Tìm kiếm nâng cao Admin**.
  * Ô nhập này cho phép Admin quét nhanh qua 3 trường thô tuyệt mật: `Tên đầu chủ`, `Nội dung chính`, và `Mô tả chi tiết`.
  * Bộ lọc này kết nối trực tiếp vào hàm `getFiltered()` và `applyFilter()` hiện có của website, đảm bảo đồng bộ 100% với cơ chế filter, reset lọc, và stats hiện tại.

### 3. Trải nghiệm Chi Tiết Căn Nhà (Property Detail Modal - Toggle Headers UX)
Khi click vào một căn nhà trên danh sách, Modal chi tiết sẽ trượt lên chiếm toàn màn hình điện thoại.

#### 🟢 Chế độ View Khách Hàng (Public View)
* Bố cục **giữ nguyên vẹn 100%** như hiện tại: Slide ảnh public sạch, Tiêu đề BDS AI chuẩn SEO v5, mô tả 4 đoạn không emoji, bản đồ định vị khu vực (không lộ số nhà), nút "Gửi Zalo" nhanh.

#### 🔴 Chế độ View Admin (Private View - Toggle Headers UX)
* Thay vì dùng chia Tab bắt người dùng bấm chọn qua lại, trên điện thoại di động, giải pháp tối ưu nhất là sử dụng **Toggle Headers (Collapse/Expand Accordions)** được cấu hình thứ tự và trạng thái đóng/mở mặc định dựa theo tần suất sử dụng thực tế của môi giới, đồng thời cho phép Admin xem nhanh giao diện hiển thị cho khách hàng (View KH) ngay tại chỗ:
  
  ```
  ┌────────────────────────────────────────────────────────┐
  │ 🔒 CHI TIẾT ADMIN (VIEW NỘI BỘ)                         │
  ├────────────────────────────────────────────────────────┤
  │ [▼] 📢 THÔNG TIN THÔ - POOL (Mở mặc định - Ưu tiên số 1) │
  │   • Tên đầu chủ: Nguyễn Văn Sang                         │
  │   • ĐT Đầu chủ:  [ 📞 0908130555 ] (Chạm để gọi nhanh)  │
  │   • Facebook:    [ 🌐 Mở FB Link ]                       │
  │   • Sơ đồ thửa:  [ 🗺️ Sơ đồ 1 ]  [ 🗺️ Sơ đồ 2 ] (Click Zoom) │
  │   • Nội dung chính (thô):                                │
  │     ┌────────────────────────────────────────────────┐   │
  │     │ 40.78 trần quang diệu 38 3 9 5 8.75 tỷ...      │   │
  │     └────────────────────────────────────────────────┘   │
  ├────────────────────────────────────────────────────────┤
  │ [▶] ✍️ BIÊN TẬP CUSTOM - SOURCE (Đóng mặc định)          │
  │   • Hướng nhà:   [ Đông ]  [ Tây ]  [ Nam ]  [ Bắc ]...  │
  │   • Đánh giá:    [🔥 Ngon]  [ Bình thường ]  [⚠️ Lỗi]    │
  │   • Ngủ trệt:    [  ] Checkbox                           │
  │   • CHDV:        [  ] Checkbox                           │
  │   • Số phòng ngủ: [ - ]  3  [ + ] (Stepper to)           │
  │   • Note Admin:  [ Nhập ghi chú riêng của anh...      ]   │
  ├────────────────────────────────────────────────────────┤
  │ [▶] 📄 PREVIEW KHÁCH HÀNG (Đóng mặc định - View KH)      │
  │   • Tiêu đề Public: Mặt tiền Nguyễn Văn Công - 126m2... │
  │   • Bài đăng Public (Sạch sẽ, 4 đoạn, không emoji):      │
  │     + Vị trí: ...                                      │
  │     + Kết cấu: ...                                     │
  ├────────────────────────────────────────────────────────┤
  │                                                        │
  │            [ 💾 LƯU THAY ĐỔI CỤC BỘ ]                 │
  │   (Sticky Bottom Button - Ghim dưới chân màn hình)     │
  └────────────────────────────────────────────────────────┘
  ```

  * **Chi tiết Touch-Optimized UX:**
    * **Toggle Headers (Accordions) theo thứ tự ưu tiên môi giới:**
      * Nhóm **`📢 THÔNG TIN THÔ - POOL`** (Tần suất sử dụng cao nhất - 90%): Được **đưa lên đầu tiên và Mở mặc định (Expand)** để môi giới lập tức tra cứu SĐT chủ nhà, bấm gọi nhanh, xem hình sổ hồng hoặc đọc nội dung thô khi đi thực địa.
      * Nhóm **`✍️ BIÊN TẬP CUSTOM - SOURCE`** (Chỉ khi cần thiết mới sửa): Đứng thứ hai và **Mặc định Thu gọn (Collapse)**. Khi cần viết Note, đổi hướng hay đánh giá, Admin chạm nhẹ để mở ra chỉnh sửa.
      * Nhóm **`📄 PREVIEW KHÁCH HÀNG`** (Xem trước hiển thị cho khách): Đứng thứ ba và **Mặc định Thu gọn (Collapse)**. Cho phép Admin nhấp mở khi cần kiểm tra nhanh bài viết công khai trước khi lưu.
      * Nhóm **`📄 PREVIEW KHÁCH HÀNG`** (View KH): Mặc định **Thu gọn (Collapse)**. Cho phép Admin nhấp mở để kiểm tra nhanh giao diện và bài viết đã curate sạch sẽ sẽ hiển thị thế nào với khách hàng trước khi quyết định lưu hoặc gửi link.
    * **Click-to-Call:** Số điện thoại đầu chủ được bọc trong thẻ `tel:` to rõ, admin chạm vào là điện thoại tự động gọi điện ngay lập tức mà không cần copy paste.
    * **Facebook Link:** Mở trực tiếp link trong App Facebook của điện thoại.
    * **Image Zoom Overlay:** Ảnh sơ đồ thửa đất hiển thị dạng thumbnail, khi chạm vào sẽ bung ra một Overlay toàn màn hình kèm khả năng Pinch-to-Zoom (dùng 2 ngón tay thu phóng) cực kỳ mượt mà để admin soi rõ nét vẽ trên sổ hồng.
    * **Segmented Radio Control:** Các trường Hướng nhà, Đánh giá được chọn bằng cách tap trực tiếp vào các ô nút (Segmented Controls) thay vì cuộn select box truyền thống của browser.
    * **Sticky Bottom Save Button:** Nút "LƯU THAY ĐỔI" màu xanh lá có chiều cao 48px, chữ in hoa đậm, luôn ghim cố định ở đáy màn hình điện thoại (Sticky footer) để admin bấm lưu tức thì sau khi edit.

---

## Verification Plan

### Automated Tests
* Mock Google Sheets API responses và chạy unit test kiểm tra logic so khớp gộp dữ liệu song song của 2 sheet (Pool & Source) theo `Mã Hàng`.
* Kiểm tra logic update dòng: Gửi yêu cầu cập nhật các trường custom trên mock sheet và xác minh vị trí ghi cột chính xác.

### Manual Verification
1. Đăng nhập Vercel Admin Dashboard bằng tài khoản Google Admin.
2. Xác nhận danh sách các căn nhà hiển thị đầy đủ thông tin.
3. Thử tìm kiếm bằng tên của một đầu chủ (ví dụ: `Nguyễn Văn A`) hoặc nội dung thô (ví dụ: `Nguyễn Văn Sang - Thiên Thạch`) -> Xác nhận bộ lọc hoạt động ngay lập tức và trả về đúng căn tương ứng.
4. Chọn một căn, sửa đổi trường `Note` và `Đánh giá (Admin)` từ `Hàng thường` sang `Hàng ngon`, tích chọn `Ngủ trệt (Admin)` -> Bấm **LƯU THAY ĐỔI**.
5. Mở trực tiếp file Google Sheets tab **Source**, xác nhận dòng tương ứng đã được cập nhật chính xác các giá trị mới trên mây.
6. Mở trình duyệt view khách hàng công khai, xác nhận khách hàng vẫn chỉ thấy thông tin public, không lộ các thông tin thô của Pool (Tên đầu chủ, SĐT đầu chủ, FB, Nội dung chính).
