# 🗺️ Bản Đồ Luồng Nghiệp Vụ & Hướng Dẫn Mô Tả Cho AI (AI-Optimized Business Workflows)

Tài liệu này hệ thống hóa 5 luồng nghiệp vụ cốt lõi của dự án BDS Khang Ngô và định nghĩa cấu trúc chuẩn để mô tả nghiệp vụ cho các tác nhân AI đọc hiểu khi thiết kế tính năng mới hoặc sửa lỗi.

---

## 🛑 PHẦN 1: TIÊU CHUẨN MÔ TẢ NGHIỆP VỤ CHO AI (AI Prompting Standard)

Để bất kỳ AI nào (Gemini, Claude, GPT) có thể hiểu và lập trình chính xác mà không làm mất mát dữ liệu hoặc vi phạm nghiệp vụ, mọi yêu cầu thiết kế/sửa lỗi phải được mô tả theo **Cấu trúc 6 thành phần (AI-Ready Spec)** sau:

```markdown
### [Tên Luồng Nghiệp Vụ]

1. **Mục tiêu Nghiệp vụ (Business Goal):** [Mục đích của luồng này giúp ích gì cho ai?]
2. **Tác nhân & Điểm kích hoạt (Actors & Triggers):** [Ai là người chạy? Kích hoạt bằng nút nào, API nào?]
3. **Dữ liệu đầu vào & Định dạng (Inputs & Formats):** [Dữ liệu truyền đi là gì? Kiểu dữ liệu?]
4. **Danh sách các trường Bị Chép Đè vs. Được Bảo Toàn (State Rules):**
   - ⚠️ Bị ghi đè: [Các trường cập nhật mới]
   - 🛡️ Được bảo toàn: [Các trường tuyệt đối giữ nguyên]
5. **Quy trình các bước (Process Steps):** [Từng bước thực hiện kèm mã nguồn tương ứng]
6. **Quy tắc xử lý lỗi & Độ ổn định (Error & Stability Gates):** [Xử lý thế nào khi API lỗi, rớt mạng, mất quyền?]
```

---

## 🗺️ PHẦN 2: BẢN ĐỒ 5 LUỒNG NGHIỆP VỤ CỐT LÕI

---

### Luồng 1: Cào Mới / Nhập Mới Tin Thô (Crawl & Import)

* **Business Goal:** Lấy dữ liệu bất động sản thô từ nguồn Thiên Khôi về CSDL SQLite Pool để bắt đầu phân tích thương mại.
* **Triggers:** Admin bấm nút "Cào tin" từ Tampermonkey Userscript (gọi `POST /api/listings/<tk_id>/recrawl`).
* **Inputs:** `tk_id` (UUID của Thiên Khôi) và `cookie` từ file local `thienkhoi_cookie.txt`.
* **State Rules (SQLite `listings`):**
  * ⚠️ **Bị ghi đè:**
    * *Cột thông tin thô:* `Gia_chao`, `DT_Thuc_te`, `DT_Tren_so`, `So_Tang`, `Mat_Tien`, `Chieu_dai`, `Huong`, `Duong_truoc_nha_m`, `So_phong_ngu`, `So_nha_ve_sinh`, `T_nh`, `Quan`, `Phuong`, `Duong`, `Ngo_So_nha`, `Phan_loai`, `Mo_ta_chi_tiet`, `Ten_Chu_Nha`, `Dien_thoai_1`, `Dien_thoai_Dau_Chu`, `Ten_Dau_Chu_Hop_dong`, `Diem_Facebook`, `Link_Goc`, `Trang_thai` (Trạng thái Thiên Khôi), `Loai_Hop_dong`.
    * *Cột R2/Drive thô:* `raw_images_tk_json` và `raw_sodo_tk_json`.
    * *Cột kỹ thuật:* `raw_json_full` (payload gốc Thiên Khôi), `JSON_UI` (dữ liệu UI thu gọn), `Last_Crawl` (thời điểm cào).
    * *Các cột tiêu chí được parse từ criteria đối tác:* `custom_huong`, `custom_dt_so`, `custom_dt_thuc_te` (nếu có criteria tương ứng trong API), `Phan_loai_Hem` và các cột đặc tính kỹ thuật phụ (`isSigned`, `status_nguon`, `commissionAgent`, `ownerSideUserId`, `certificateSeries`, `latitude`, `longitude`, `placeName`, `streetName`, `balconies`, `sidewalk`, `behindOpenSpace`, `sideOpenSpace`, `createdAt`, `updatedAt`, `commissionType`, `commissionValue`, `isDispute`, `createdAtSigned`, `CCCD_Dau_Chu`, `Kenh_tin_TK`, `The_tags_TK`).
    * *Giá Public (`Gia_Public`):* Tự động đặt lại bằng giá trị `Gia_chao` mới cào được.
    * *Trạng thái xử lý (`status`):* Reset về `'raw_text'` (để kích hoạt luồng di cư ảnh chạy ngầm).
  * 🛡️ **Được bảo toàn:**
    * *Cột chất xám biên tập:* `curated_config_json`, `manual_images_json`, `images_mapping_json`, `images_admin_json`, `images_public_json`.
    * *Thông tin thương mại custom:* `Tieu_de_Public`, `Mo_ta_Public`, `Ma_Khang_Ngo_ID` (nếu đã được điền từ trước thì giữ nguyên, chỉ sinh mới nếu đang trống), `System_ID` (giữ nguyên để đối chiếu).
* **Process Steps:**
  1. API `/api/listings/<tk_id>/recrawl` nhận lệnh ➔ gọi API Thiên Khôi `https://backend.thienkhoi.com/product/v1/property/<tk_id>`.
  2. Bóc tách dữ liệu JSON thô, thu thập toàn bộ danh sách `media` (không phân biệt loại ảnh, chỉ tách sơ đồ ra `sodo_images`, còn lại đưa vào `property_images` để đảm bảo cào hết 100% hình ảnh).
  3. Gọi `pool_lego.save_raw_to_sqlite()` để cập nhật SQLite, đặt `status = 'raw_text'`.
  4. Khởi tạo 2 dòng `crawl` và `self` kề sát nhau cho mã căn này trên tab `Pool_Images` của Google Sheets (nếu chưa có dòng nào).
  5. Gọi di cư ảnh chạy ngầm (`manager.run_image_migration_thread`).

---

### Luồng 2: Di Cư Hình Ảnh & Tối Ưu Hóa R2 (Image Migration)

* **Business Goal:** Tải ảnh từ nguồn đối tác, nén tối ưu và tải lên hạ tầng Cloudflare R2 riêng để tránh phụ thuộc vào link thô dễ chết của đối tác.
* **Triggers:** Trực tiếp sau Luồng 1 hoặc khi Admin kích hoạt di cư hàng loạt (`manager.run_image_migration_thread`).
* **Inputs:** Dòng dữ liệu trong CSDL có trạng thái `status = 'raw_text'`.
* **State Rules (SQLite `listings`):**
  * ⚠️ **Bị ghi đè:** `raw_drive_images_json` (chứa danh sách link R2 mới sau khi tải), `status` chuyển thành `'raw_complete'`.
  * 🛡️ **Được bảo toàn:** Cấu hình sắp xếp ảnh cũ của Admin.
* **Process Steps:**
  1. Đọc danh sách ảnh thô từ `raw_images_tk_json`.
  2. So khớp với `images_mapping_json` cũ để tái sử dụng ảnh R2 đã upload thành công (tránh upload trùng để tiết kiệm băng thông R2).
  3. Đối với ảnh mới: Tải ảnh về ➔ **Nếu không phải ảnh sơ đồ** thì tiến hành nén tối ưu (Canvas/Pillow) ➔ **Nếu là sơ đồ/sổ đỏ** thì bỏ qua nén để bảo toàn độ nét chi tiết phục vụ thu phóng ➔ Tải lên R2 và đặt tên dạng `img_<tk_id>_<index>.jpg`.
  4. Chạy thuật toán **Smart Image Merge**: Giữ nguyên ảnh Admin tự upload (`manual_images`), ghép ảnh thô mới cào vào cuối danh sách, bảo toàn thứ tự sắp xếp và cờ `visible` cũ.
  5. Lưu đè cấu hình mới vào `curated_config_json`.
  6. Ghi danh sách ảnh R2 đã di cư vào dòng **`crawl`** trên sheet `Pool_Images` (chứa toàn bộ ảnh của tin cào).
  7. Gọi `execute_publish_listing(tk_id)` để đẩy dữ liệu lên tab `Pool` của Google Sheets trực tuyến.

---

### Luồng 3: Biên Tập & Lưu Curation (Curation Save)

* **Business Goal:** Admin chỉnh sửa thông tin thương mại, thay đổi thứ tự ảnh, ẩn/hiện hoặc tải thêm ảnh mới từ thiết bị.
* **Triggers:** Admin bấm nút "Lưu" (Save) trên Vercel Admin Curation Dashboard (gọi `PUT /api/listings/<tk_id>`).
* **Inputs:** Payload JSON chứa các thông số đã chỉnh sửa, thứ tự ảnh mới và trạng thái ẩn hiện (`visible`).
* **State Rules (SQLite `listings`):**
  * ⚠️ **Bị ghi đè:**
    * *Dữ liệu JSON ảnh:* `curated_config_json` (cấu hình ẩn hiện/sắp xếp), `images_admin_json` (JSON toàn bộ ảnh đã di cư), `images_public_json` (JSON chứa danh sách các ảnh được phép công khai: `visible = true` và không có role là `facade`, `diagram`, `deleted` hoặc `hidden`), `manual_images_json` (các ảnh tự tải lên).
    * *Các cột thương mại:* `Tieu_de_Public`, `Mo_ta_Public`, `Gia_Public`, `Ma_Khang_Ngo_ID`.
    * *Cột ghi đè địa chỉ:* `Ngo_So_nha`, `Quan`, `Phuong`, `Duong`.
    * *Cột thuộc tính ghi đè:* `Phan_loai_Hem`, `Duong_truoc_nha_m`, `Mat_Tien`, `Chieu_dai`, `Tinh_trang_nha`, `So_phong_ngu`, `So_nha_ve_sinh`, `Danh_gia_Admin`, `Ngu_tret_Admin`, `CHDV_Admin`, `Phuong_cu_AI`, `custom_huong`, `custom_dt_so`, `custom_dt_thuc_te`.
    * *Cột phẳng ảnh liên kết chính:* `Hinh_Nhan_Dien`, `Hinh_Mat_Tien`.
    * *Cột phẳng danh sách ảnh phẳng:* `Hình Hẻm 1` đến `10`, `Ảnh 1` đến `25`, `Sơ đồ thửa đất 1` đến `5`.
  * 🛡️ **Được bảo toàn:** Các thuộc tính thô từ Thiên Khôi (để đối chiếu).
* **Process Steps:**
  1. API nhận JSON payload ➔ Lưu thông số biên tập và danh sách ảnh vào các cột tương ứng trong CSDL SQLite.
  2. Đồng bộ danh sách hình ảnh đã biên tập (chứa link R2 và ảnh tự up) xuống dòng **`self`** của căn nhà trên tab `Pool_Images` Google Sheets (sử dụng Google Sheets API gọi trực tiếp từ client để ghi nhận).
  3. Cập nhật các cột phẳng (`Hình Nhận Diện`, `Hình Mặt Tiền`, `Hình Hẻm 1-10`, `Ảnh 1-25`, `Sơ đồ thửa đất 1-5`) và cột **`Images_Admin_JSON`** trên tab `Pool` Google Sheets.

---

### Luồng 4: Xuất Bản Lên Sóng (Publish / Deployment)

* **Business Goal:** Công khai bất động sản lên Vercel để khách hàng và đầu khách có thể tra cứu nhanh.
* **Triggers:** Admin bấm nút "Lên sóng" (Publish) trên Admin Console (gọi `POST /api/listings/<tk_id>/publish`).
* **Inputs:** Dữ liệu của căn nhà đã qua giai đoạn Curation trong CSDL SQLite.
* **State Rules (SQLite `listings` & Google Sheets):**
  * ⚠️ **Bị ghi đè:**
    * *Trong SQLite:* Cập nhật cột `status = 'published'` và `Last_Sync` = thời gian hiện tại.
    * *Trên Sheet Source:* Ghi đè toàn bộ thông tin căn nhà sang dòng tương ứng trên tab **`Source`** trực tuyến (dùng cột `System ID` để khớp dòng).
    * *Cột Images_Public_JSON trên Source:* Chép danh sách ảnh công khai dạng JSON.
* **Process Steps:**
  1. API kiểm tra và cập nhật `status = 'published'` trong SQLite.
  2. Đồng bộ dòng dữ liệu 79 cột từ `Pool` sang tab `Source` trực tuyến.
  3. Kích hoạt Google Apps Script (`pool_backend_v3.gs` chạy trên phía Google Sheets):
     * GAS tự động đọc giá trị cột `Images_Admin_JSON` của dòng vừa sync.
     * Thực hiện lọc bỏ các ảnh ẩn (`is_hidden = 1`) và các ảnh có vai trò bảo mật (`facade`, `diagram`, `deleted`).
     * Lưu kết quả dạng JSON vào cột **`Images_Public_JSON`** (Cột 49 / Cột AW) trên tab **`Source`**.
  4. Hệ thống Vercel Frontend đọc cột `Images_Public_JSON` này để kết xuất thư viện ảnh cho người dùng xem trên trang chi tiết.

---

### Luồng 5: Khôi Phục Cơ Sở Dữ Liệu Cục Bộ (Database Restore)

* **Business Goal:** Tái thiết lập/Khôi phục toàn bộ CSDL cục bộ SQLite (`raw_archive.db`) từ Google Sheets khi cài máy mới hoặc đồng bộ hóa dữ liệu.
* **Triggers:** Chạy script cứu hộ `python restore_db_from_sheets.py`.
* **Inputs:** Dữ liệu từ 3 tab trực tuyến: `Pool`, `Source`, và `Pool_Images`.
* **State Rules (SQLite `raw_archive.db` / `raw_archive_staging.db`):**
  * ⚠️ **Bảo toàn CSDL Gốc:** Không bao giờ xóa vật lý tệp cơ sở dữ liệu gốc. Chỉ cập nhật hoặc chèn mới dữ liệu. Đối với các căn bị xóa khỏi Google Sheets, cập nhật trạng thái `status = 'sheet_deleted'` thay vì xóa vật lý.
  * ⚙️ **Bảng & Cột bị tác động:**
    1. Bảng **`listings`**: Hợp nhất các trường thông tin phẳng từ CSDL Tạm, bảo toàn 100% các cột lưu trữ ảnh nội bộ và dữ liệu thô cục bộ (`raw_json_full`).
    2. Bảng **`listings_images`**: Cập nhật siêu dữ liệu ảnh đồng bộ từ CSDL Tạm.
* **Process Steps:**
  1. Khởi tạo một tệp cơ sở dữ liệu SQLite tạm thời dạng `.temp` (ví dụ `raw_archive_staging.db.temp`) có cấu trúc schema rỗng.
  2. Kết nối API Google Sheets để tải dữ liệu từ các tab `Pool`, `Source` và nạp vào bảng `listings` của CSDL Tạm.
  3. Tải danh sách hình ảnh lịch sử (gồm dòng `crawl` và `self`) từ tab `Pool_Images` nạp vào bảng `listings_images` của CSDL Tạm.
  4. Thực hiện sao lưu (Backup) CSDL Gốc sang thư mục `BDS_Backups/` trước khi tiến hành cập nhật.
  5. Gọi hàm `merge_temp_to_master(temp_db, master_db)` thực hiện hợp nhất gián tiếp từ CSDL Tạm vào CSDL Gốc.
  6. Xóa bỏ tệp CSDL Tạm `.temp` khỏi thư mục dự án để giải phóng bộ nhớ.
  7. Chạy bộ kiểm thử tự động `pytest tests/test_db.py` để xác nhận tính toàn vẹn của CSDL.
