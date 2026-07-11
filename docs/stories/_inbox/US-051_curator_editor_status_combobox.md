---
id: US-051
status: accepted
date: 2026-05-30
size: S
---

# US-051: Tích hợp Combobox Tình trạng và Loại bỏ trường Rộng hẻm thừa tại giao diện Biên tập Admin (Curator Editor Status Combobox & Alley Width Cleanup)

## User story
**As an** Admin / Curator
**I want** to remove the redundant "Rộng hẻm" input field from the curation editor interface, auto-populate its database value from the crawled "Đường trước nhà" field upon saving, and replace its UI position with a "Tình trạng" combobox containing: Bình thường, Mới, Nát, Đã bán, Ẩn
**So that** I can clean up redundant fields, easily change the property status directly from the curation panel, and ensure seamless mapping to the `tinh_trang` column in the Source sheet, supporting KPI 2 (Tốc độ biên tập).

## Acceptance
- [x] **Loại bỏ trường Rộng hẻm khỏi giao diện Biên tập (Alley Width UI Removal):**
  - Xóa bỏ ô nhập liệu "Rộng hẻm" khỏi form biên tập trong Modal Curation của Admin để giao diện thông thoáng hơn.
  - Khi lưu dữ liệu lên Google Sheets, hệ thống tự động gán giá trị của trường "Đường trước nhà" (cào được) vào cột "Rộng hẻm" để đảm bảo tính toàn vẹn của dữ liệu ở database.
- [x] **Tích hợp Combobox Tình trạng (Property Status Combobox):**
  - Tại vị trí trống của trường "Rộng hẻm" vừa xóa, hiển thị một hộp chọn (Combobox/Select) có nhãn **Tình trạng**.
  - Các tùy chọn có sẵn bao gồm: **Bình thường**, **Mới**, **Nát**, **Đã bán**, **Ẩn**.
  - Giá trị chọn của combobox này phải được đồng bộ chính xác và lưu trực tiếp xuống cột **Tình trạng** (`tinh_trang`) tương ứng trong sheet Source của Google Sheets.
- [x] **Khởi tạo dữ liệu mặc định (Default Value Initialization):**
  - Khi mở Modal Curation của bất kỳ căn nhà nào, combobox **Tình trạng** phải hiển thị chính xác trạng thái hiện tại của căn nhà đó lấy từ database. Nếu trống, mặc định hiển thị là "Bình thường".

## Solution

### 1. Cập nhật giao diện biên tập Admin (`index.html`)
- Thay thế đoạn mã HTML trường nhập "Rộng hẻm" (`#editRongHem`):
  ```html
  <div class="admin-edit-group">
    <label for="editRongHem">Rộng hẻm (m):</label>
    <input type="number" id="editRongHem" step="0.1" value="...">
  </div>
  ```
  Bằng combobox "Tình trạng" (`#editTinhTrang`):
  ```html
  <div class="admin-edit-group">
    <label for="editTinhTrang">Tình trạng:</label>
    <select id="editTinhTrang">
      <option value="Bình thường">Bình thường</option>
      <option value="Mới">Mới</option>
      <option value="Nát">Nát</option>
      <option value="Đã bán">Đã bán</option>
      <option value="Ẩn">Ẩn</option>
    </select>
  </div>
  ```

### 2. Thiết lập giá trị mặc định khi mở Modal Curation
- Trong hàm `openS()` (phần Admin), gán giá trị mặc định cho trường Tình trạng từ đối tượng `p`:
  ```javascript
  const editTinhTrang = document.getElementById('editTinhTrang');
  if (editTinhTrang) {
    editTinhTrang.value = p.tinh_trang || 'Bình thường';
  }
  ```

### 3. Cập nhật giá trị khi lưu dữ liệu
- **Trường hợp Lưu thay đổi căn nhà cũ (`saveCurationChanges`):**
  - Đọc giá trị chọn:
    ```javascript
    const tinhTrang = document.getElementById('editTinhTrang').value;
    ```
  - Thay vì đọc trường rộng hẻm cũ từ DOM, tự động lấy giá trị từ trường cào "Đường trước nhà":
    ```javascript
    const rongHem = p.raw_duong_truoc_nha || p.duong_truoc_nha || '';
    ```
  - Lưu vào đối tượng `original_row_data` và cập nhật client-side:
    ```javascript
    p.original_row_data[14] = rongHem || '-'; // O: do_rong_hem
    p.original_row_data[15] = tinhTrang;      // P: tinh_trang_nha
    p.tinh_trang = tinhTrang;
    ```
- **Trường hợp Đăng căn mới từ Pool (`saveNewListingFromPool`):**
  - Đọc giá trị chọn:
    ```javascript
    const tinhTrang = document.getElementById('editTinhTrang').value;
    ```
  - Tự động lấy giá trị từ trường cào của dòng gốc trong Pool (`matchedRow[59]`):
    ```javascript
    const rongHem = matchedRow[59] || '';
    ```
  - Truyền giá trị `tinhTrang` vào mảng hàng đẩy lên cột P (`tinh_trang_nha`):
    ```javascript
    tinhTrang, // 15: tinh_trang_nha (Cột P)
    ```

## 📋 Implementation Plan
- **Bước 1:** Thay thế ô nhập "Rộng hẻm" bằng hộp chọn Tình trạng trong tệp [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html).
- **Bước 2:** Bổ sung gán giá trị mặc định của Tình trạng khi mở modal.
- **Bước 3:** Sửa đổi logic lưu dữ liệu của cả 2 hàm `saveCurationChanges` và `saveNewListingFromPool` để đọc giá trị combobox, và tự động lấy giá trị cào đường trước nhà gán cho rộng hẻm.
- **Bước 4:** Thực hiện kiểm thử trên môi trường nội bộ để đảm bảo lưu dữ liệu lên Google Sheets hoạt động trơn tru.

## 📝 Task Checklist (TODO)
- [ ] Thay thế UI rộng hẻm thành combobox tình trạng.
- [ ] Gán dữ liệu ban đầu khi mở modal.
- [ ] Cập nhật logic trích xuất và gán dữ liệu rộng hẻm tự động khi lưu căn đã duyệt.
- [ ] Cập nhật logic gán dữ liệu rộng hẻm tự động và tình trạng khi lên sóng căn mới.
- [ ] Chạy thử nghiệm và kiểm tra dữ liệu đẩy lên Google Sheets chính xác.

## 🛠️ Update Logic (Drafting while Doing)
*(Sẽ sử dụng để ghi nhận logic thô trong quá trình triển khai thực tế)*

## Verification Plan
### Kiểm thử thủ công:
1. **Kiểm tra giao diện:** Mở modal curation của một căn nhà, kiểm tra xem trường "Rộng hẻm" đã biến mất và thay thế bằng hộp chọn "Tình trạng" với 5 giá trị hay chưa.
2. **Kiểm tra lưu dữ liệu căn cũ:** Đổi tình trạng sang "Mới" và lưu. Xác minh trên Google Sheet cột P (`tinh_trang_nha`) được cập nhật sang "Mới", và cột O (`do_rong_hem`) được điền đúng giá trị của "Đường trước nhà" (cào được).
3. **Kiểm tra lên sóng căn mới:** Lên sóng một căn thô từ Pool, đổi tình trạng sang "Đã bán". Xác minh trên Google Sheet cột P của dòng mới được điền "Đã bán", và cột O tự động thừa hưởng dữ liệu "Đường trước nhà" gốc từ Pool.

## Files touched
- [index.html](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html)

## 🔄 Change Requests (Yêu cầu Thay đổi)
*(Sẽ sử dụng để ghi nhận nhật ký thay đổi yêu cầu của PO khi test hoặc triển khai)*
