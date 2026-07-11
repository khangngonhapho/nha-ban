---
id: US-101
status: backlog
date: 2026-06-21
size: M
---

# US-101: Tối ưu hóa di cư ảnh khi cào lại, bảo toàn hình ảnh tự tải lên và sắp xếp thứ tự hợp nhất (Pool1)

## User story
**As an** Admin / Curator
**I want** hệ thống di cư ảnh tự động nhận diện, tái sử dụng các ảnh đã di cư thành công, và tách biệt lưu trữ các ảnh tự tải lên để bảo vệ tuyệt đối không bị đè mất khi cào lại (recrawl)
**So that** tối ưu tốc độ cào lại, tiết kiệm băng thông R2, đồng thời cho phép sắp xếp thứ tự kết hợp tự do (cả ảnh di cư và ảnh tự tải lên), quản lý hình ảnh sổ đỏ độc lập và bật/tắt ẩn hiện từng ảnh (mặc định ẩn sơ đồ & mặt tiền đối với khách hàng) trong giao diện biên tập theo đúng nhu cầu hiển thị.

## Acceptance Criteria
- [ ] **Bản đồ đối chiếu hình ảnh JSON (Images Mapping JSON):** Thêm trường `images_mapping_json` (TEXT) vào bảng `listings` (hệ thống Pool1) lưu trữ dạng JSON map: `{"link_thô_TK": "link_R2"}` (chứa cả ảnh thường và sổ đỏ).
- [ ] **Tách biệt lưu trữ ảnh tự tải lên:** Thêm cột `manual_images_json` (TEXT) vào bảng `listings` để lưu trữ danh sách các ảnh được tải lên thủ công dạng `["R2_url_1", "R2_url_2"]` (bao gồm cả ảnh sơ đồ tự tải).
- [ ] **Quản lý Hình Sổ đỏ thô JSON (Raw Diagrams JSON):**
  - Thêm cột `raw_sodo_tk_json` (TEXT) vào bảng `listings` để lưu trữ danh sách các link sơ đồ thô cào về từ Thiên Khôi (bóc tách từ `#lightgalleryTD li`).
  - Cột này được dùng để giúp tiến trình di cư ảnh nhận diện chính xác các ảnh là sổ đỏ (sơ đồ) để **bỏ qua nén** nhằm bảo toàn chi tiết thu phóng khi cào lại, mà không cần dựa vào các cột phẳng `So_do_thua_dat_X` trong SQLite database.
- [ ] **Cơ chế Đối chiếu Hình ảnh phân tách (Separated Image Comparison Mechanism):**
  - Khi cào lại tin, phân loại các link ảnh thô mới cào thành 2 mảng: Ảnh thường thô (`new_raw_interiors`) và Ảnh sơ đồ thô (`new_raw_diagrams`).
  - Đối với ảnh thường thô: So khớp link thô mới với `raw_images_tk_json` cũ và `images_mapping_json` cũ. Nếu trùng, tái sử dụng link R2 đã có. Nếu không trùng, tiến hành tải, **nén Canvas tối ưu**, upload R2 và ghi nhận mapping mới.
  - Đối với ảnh sơ đồ thô: So khớp link thô mới với `raw_sodo_tk_json` cũ và `images_mapping_json` cũ. Nếu trùng, tái sử dụng link R2 đã có. Nếu không trùng, tiến hành tải, **bỏ qua nén**, upload R2 và ghi nhận mapping mới.
  - Dọn dẹp: Xóa các mapping lỗi thời không còn tồn tại ở cả 2 mảng thô mới.
- [ ] **Thuộc tính Ẩn/Hiện riêng biệt (Hide/Show Visibility Flag):**
  - Mỗi ảnh trong `curated_config_json` có thêm trường boolean `visible` (mặc định là `true`).
  - **Mặc định Ẩn Sổ đỏ và Mặt tiền đối với Customer:** 
    - Khi khởi tạo ảnh thô hoặc Admin gán nhãn vai trò **Sơ đồ** hoặc **Mặt tiền**, hệ thống tự động gán mặc định cờ ẩn là `visible = false` (chống lộ địa chỉ và thông tin nhạy cảm của chủ nhà).
    - Khi Admin gán vai trò **Bìa**, **Hẻm**, hoặc **Nội thất**, hệ thống tự động gán mặc định là `visible = true`.
    - Admin vẫn có thể click chọn bật/tắt thủ công cờ **Hiện** này cho từng ảnh để ghi đè mặc định.
  - Các hình ảnh bị tắt **Hiện** (`visible: false`) vẫn xuất hiện trong giao diện biên tập của Admin (với độ mờ giảm đi để phân biệt) để có thể phục hồi bật lại sau này, nhưng **tuyệt đối không** được đưa lên Google Sheets và website công khai của khách hàng.
- [ ] **Sắp xếp thứ tự hợp nhất (Unified Custom Ordering):**
  - Sử dụng `curated_config_json` làm nguồn dữ liệu duy nhất quy định thứ tự hiển thị của tất cả các ảnh (ảnh thường và sổ đỏ). Mảng `images` trong JSON tự chứa thứ tự hiển thị thông qua chỉ số (index) của phần tử. Các ảnh sơ đồ có thể sắp xếp đan xen hoặc gom nhóm tùy ý Admin.
  - Loại bỏ hoàn toàn việc cập nhật/đồng bộ vào dải cột phẳng `Anh_1` - `Anh_25` và `So_do_thua_dat_1` - `5` trên SQLite database khi lưu trữ/chỉnh sửa trong Admin.
- [ ] **Luật Hợp nhất Hình ảnh thông minh (Smart Image Merge):** Khi cào lại (recrawl) và chạy di cư ảnh:
  - Đọc `manual_images_json` và `curated_config_json` cũ để **giữ nguyên vẹn các ảnh tự tải lên** (ảnh thường & sổ đỏ) và trạng thái ẩn/hiện (`visible`) của chúng tại đúng vị trí thứ tự tương đối trong danh sách.
  - Cập nhật các ảnh di cư với link R2 mới đã đối chiếu và bảo toàn cờ `visible` cũ của chúng.
  - Append các ảnh thô mới cào thêm vào cuối danh sách.
  - Ghi đè cấu hình mới vào `curated_config_json`.
- [ ] **Dàn phẳng động có lọc ẩn/hiện khi xuất bản Google Sheets (On-the-fly Sheet Flattening with Visibility Filter):**
  - Khi đồng bộ xuất bản lên Sheet Pool (hoặc Source/Public), hệ thống sẽ đọc `curated_config_json` từ SQLite, **loại bỏ các hình ảnh có `visible: false`**, sau đó phân loại các ảnh còn lại:
    - Ảnh có `role === "Sơ đồ"` được điền tuần tự vào các cột `Sơ đồ thửa đất 1` đến `5`.
    - Ảnh có `role === "Bìa"` được điền vào `Hình Nhận Diện`.
    - Ảnh có `role === "Mặt tiền"` được điền vào `Hình Mặt Tiền`.
    - Ảnh có `role === "Hẻm"` được điền vào `Hình Hẻm 1` đến `10`.
    - Ảnh có `role === "Nội thất"` (hoặc các ảnh còn lại) được điền vào `Ảnh 1` đến `25`.
  - Tự động dàn phẳng (flatten) thành các cột tương ứng trên Google Sheets trực tuyến.

## Solution

### SQLite Schema Changes
```sql
ALTER TABLE listings ADD COLUMN images_mapping_json TEXT;
ALTER TABLE listings ADD COLUMN manual_images_json TEXT;
ALTER TABLE listings ADD COLUMN raw_sodo_tk_json TEXT;
```

### Smart Image Merge Algorithm (Python logic)
```python
def smart_image_merge(old_curated, manual_images, new_migrated_map):
    # 1. Khởi tạo danh sách ảnh mới
    merged_images = []
    
    # 2. Xây dựng tập hợp các ảnh di cư mới từ new_migrated_map
    new_migrated_urls = set(new_migrated_map.values())
    
    # 3. Duyệt qua danh sách đã sắp xếp cũ để giữ vị trí và trạng thái
    if old_curated and "images" in old_curated:
        for img in old_curated["images"]:
            url = img.get("url")
            role = img.get("role", "interior")
            visible = img.get("visible", True)
            
            # Nếu là ảnh tự up -> Giữ lại nguyên vẹn vị trí, vai trò, ẩn/hiện
            if url in manual_images or "SYS-" in url or "/static/images/" in url:
                merged_images.append({"url": url, "role": role, "visible": visible})
            # Nếu là ảnh di cư và vẫn tồn tại ở nguồn mới -> Giữ lại và cập nhật link mới nếu đổi
            else:
                orig_tk = None
                for tk, r2 in old_images_mapping.items():
                    if r2 == url:
                        orig_tk = tk
                        break
                
                if orig_tk in new_migrated_map:
                    new_r2 = new_migrated_map[orig_tk]
                    merged_images.append({"url": new_r2, "role": role, "visible": visible})
                    new_migrated_urls.discard(new_r2)
                    
    # 4. Thêm các ảnh di cư mới xuất hiện vào cuối
    for new_r2 in new_migrated_urls:
        # Nếu link R2 này thuộc danh sách sơ đồ thô mới, mặc định gán vai trò Sơ đồ, và set visible = False
        is_sodo = is_new_sodo(new_r2)
        role = "Sơ đồ" if is_sodo else "Ẩn"
        visible = False if is_sodo else True
        merged_images.append({"url": new_r2, "role": role, "visible": visible})
        
    return merged_images
```

## 📋 Implementation Plan
1. **Schema Check**: Viết logic tự động kiểm tra và thêm cột `images_mapping_json`, `manual_images_json` và `raw_sodo_tk_json` vào bảng `listings` trong `pool_lego.py`.
2. **Cập nhật Upload API**: Sửa hàm `upload_manual_image` trong `manager.py` cho Pool1 để ghi url ảnh mới tải lên vào `manual_images_json` và `curated_config_json` (nếu là ảnh sổ đỏ, gán `role: "Sơ đồ"` và `visible: false`; nếu là ảnh mặt tiền, gán `role: "Mặt tiền"` và `visible: false`).
3. **Cập nhật Cập nhật API (PUT)**: Lưu `curated_config_json` có chứa cờ `visible` và vai trò của từng ảnh.
4. **Cải tiến Tiến trình Di cư**: Sửa `run_image_migration_thread` để tích hợp `images_mapping_json` và `raw_sodo_tk_json` và chạy thuật toán Smart Merge.
5. **Dàn phẳng động có lọc Ẩn/Hiện và Sơ đồ**: Cập nhật hàm `publish_listing` trong `pool_lego.py` để loại bỏ ảnh ẩn (`visible: false`), lọc ảnh theo vai trò (sơ đồ, mặt tiền, nội thất...) và dàn phẳng dữ liệu ảnh lên Google Sheets.
6. **Cập nhật UI Biên tập**: Nâng cấp `renderImageGrid` trong `curator.html` hiển thị ảnh sổ đỏ chung trong grid kèm nhãn badge "Sơ đồ" và hỗ trợ di chuyển/ẩn hiện giống ảnh thường. Thêm checkbox **Hiện** (Show/Hide) kiểm soát trạng thái `visible`.
7. **Luật Đổi Nhãn UI**: Khi đổi vai trò ảnh sang "Sơ đồ" hoặc "Mặt tiền" ở client, tự động bỏ chọn checkbox "Hiện" (visible = false). Khi chuyển sang "Bìa", "Hẻm", hoặc "Nội thất", tự động tích chọn checkbox "Hiện" (visible = true).
8. **Viết Test Case**: Tạo file kiểm thử tự động `scratch/test_us101_image_merge.py`.

## Task Checklist (TODO)
- [ ] Thiết lập schema CSDL SQLite tự động thêm 3 cột mới.
- [ ] Tích hợp logic bootstrapping bản đồ đối chiếu hình ảnh.
- [ ] Viết hàm `smart_image_merge` ở Python backend.
- [ ] Cập nhật endpoint `/api/listings/<tk_id>/upload-image` cho Pool1.
- [ ] Nâng cấp luồng di cư ảnh song song trong `run_image_migration_thread` để bỏ qua nén sổ đỏ qua `raw_sodo_tk_json`.
- [ ] Cập nhật hàm `publish_listing` để lọc ảnh ẩn (`visible: false`) và dàn phẳng động (tách sổ đỏ ra cột Sơ đồ thửa đất) khi lên Sheets.
- [ ] Cập nhật giao diện biên tập `curator.html` để quản lý sổ đỏ hợp nhất trong grid và điều phối checkbox Ẩn/Hiện ảnh theo vai trò.
- [ ] Tạo file kiểm thử tự động `scratch/test_us101_image_merge.py`.
- [ ] Kiểm thử và nghiệm thu.
