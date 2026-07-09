# Tài liệu Đặc tả Kỹ thuật - Bộ cào dữ liệu Next.js Proptech Thiên Khôi

Tài liệu này ghi lại toàn bộ kiến thức kỹ thuật, cấu trúc API, và sơ đồ ánh xạ dữ liệu thu thập được trong quá trình nghiên cứu và di chuyển bộ cào dữ liệu từ nền tảng ASP.NET MVC cũ sang nền tảng Next.js Proptech mới (`proptech.thienkhoi.com`).

---

## 🌐 1. Hệ thống Endpoint API ngầm (REST API)

Thay vì bóc tách cấu trúc DOM HTML phức tạp và chạy trình duyệt giả lập, bộ cào mới giao tiếp trực tiếp với hệ thống API backend của Thiên Khôi tại tên miền `backend.thienkhoi.com`.

### 1.1. Xác thực thông tin tài khoản (Auth Check)
- **Endpoint**: `GET https://backend.thienkhoi.com/auth/v1/users/me`
- **Headers**: 
  - `Authorization: Bearer <TKG_accessToken>`
- **Mục đích**: Kiểm tra xem access token hiện tại còn hoạt động hay không. Nếu phản hồi có mã HTTP 200, phiên đăng nhập hợp lệ.

### 1.2. Gia hạn Token tự động (Silent Refresh Token)
- **Endpoint**: `POST https://backend.thienkhoi.com/auth/v1/auth/refresh-token`
- **Headers**:
  - `Content-Type: application/json`
  - `Origin: https://proptech.thienkhoi.com`
  - `Referer: https://proptech.thienkhoi.com/`
- **Payload**:
  ```json
  {
    "refresh_token": "<TKG_refreshToken>",
    "appLogin": "nguonhang",
    "platform": "web"
  }
  ```
- **Mục đích**: Nhận cặp Access Token và Refresh Token mới khi Access Token cũ hết hạn (thời hạn mặc định của access token là 10 phút).
- **Cơ chế lưu trữ**: Bộ cào tự động cập nhật lại tệp `thienkhoi_cookie.txt` để sử dụng cho các lần sau.

### 1.3. Lấy danh sách nguồn hàng (List Properties)
- **Endpoint**: `GET https://backend.thienkhoi.com/product/v1/property`
- **Params**:
  - `page`: Số trang (bắt đầu từ 1)
  - `limit`: Số lượng căn mỗi trang (mặc định: 20)
  - `searchBy`: Tiêu chí tìm kiếm (mặc định: `address`)
  - *Các filter khác như `districtId`, `wardId` có thể truyền vào tương tự như trên URL của trình duyệt.*
- **Mục đích**: Lấy danh sách các căn để trích xuất UUID của các căn mới chưa có trong cơ sở dữ liệu.

### 1.4. Lấy chi tiết nguồn hàng (Property Detail)
- **Endpoint**: `GET https://backend.thienkhoi.com/product/v1/property/<UUID>`
- **Mục đích**: Lấy toàn bộ thông tin chi tiết của một căn nhà (bao gồm thông tin chủ nhà, đầu chủ, sổ đỏ, mô tả chi tiết, hình ảnh nội thất) dưới dạng JSON sạch chỉ trong một request duy nhất.

---

## 🗃️ 2. Sơ đồ ánh xạ Dữ liệu JSON (Schema Mapping)

Dữ liệu JSON trả về từ API chi tiết được phân tích và ánh xạ trực tiếp vào SQLite / Google Sheets Pool theo bảng quy chuẩn dưới đây:

| Tên trường (Google Sheets Pool) | Cột SQLite (Listing) | Đường dẫn khóa trong JSON API Chi tiết (`data.`) | Ghi chú / Cách xử lý |
| :--- | :--- | :--- | :--- |
| **Mã Hàng** | `Ma_Hang` | `code` | Mã tin Thiên Khôi (Ví dụ: `TKQLMB8Q`) |
| **Tỉnh** | `T_nh` | `district.provinceName` | Mặc định là `TP Hồ Chí Minh` nếu null |
| **Quận** | `Quan` | `district.name` | Tên quận hiển thị |
| **Phường** | `Phuong` | `ward.name` | Tên phường hiển thị |
| **Đường** | `Duong` | `street.name` hoặc `streetName` | Sử dụng tên đường từ `street` hoặc fallback `streetName` |
| **Ngõ/Số nhà** | `Ngo_So_nha` | `address` | Số nhà / Tên hẻm |
| **Phân loại** | `Phan_loai` | `criteria` | Danh sách các tiêu chí (join cách nhau bởi dấu phẩy) |
| **Nội dung chính** | `Noi_dung_chinh` | *(Tự tổng hợp)* | Định dạng: `{address} {street}, {area}m2, {floors} tầng, mt {wide}m, sâu {depth}m, giá {price} tỷ, Phường {ward} {district}` |
| **Mô tả chi tiết** | `Mo_ta_chi_tiet` | `description` | Toàn bộ bài viết mô tả của Đầu chủ |
| **Giá chào** | `Gia_chao` | `offeringPrice` | Giá chào (đơn vị: Tỷ) |
| **DT Thực tế** | `DT_Thuc_te` | `actualArea` | Diện tích thực tế |
| **DT Trên sổ** | `DT_Tren_so` | `area` | Diện tích trên sổ đỏ |
| **Số Tầng** | `So_Tang` | `floors` | Số tầng của căn nhà |
| **Mặt Tiền** | `Mat_Tien` | `wide` | Độ rộng mặt tiền |
| **Chieu_dai** | `Chieu_dai` | `depth` | Chiều sâu của đất |
| **Số phòng ngủ** | `So_phong_ngu` | `bedrooms` | Số phòng ngủ |
| **Số nhà vệ sinh** | `So_nha_ve_sinh` | `restrooms` | Số phòng vệ sinh / WC |
| **Hướng** | `Huong` | `direction` | Hướng nhà (nếu có) |
| **Đường trước nhà (m)** | `Duong_truoc_nha_m` | `minimumRoadWidth` | Độ rộng ngõ/đường trước nhà |
| **Trạng thái** | `Trang_thai` | `status` | Trạng thái nguồn hàng (Ví dụ: `qualified`) |
| **Tên Chủ Nhà** | `Ten_Chu_Nha` | `homeOwner` | Danh sách tên chủ nhà (join cách nhau bởi dấu phẩy) |
| **Điện thoại 1** | `Dien_thoai_1` | `contactPhoneNumber` | SĐT chủ nhà (nếu được cấp quyền xem công khai) |
| **Điện thoại Đầu Chủ** | `Dien_thoai_Dau_Chu` | `ownerSideUser.phone` | SĐT của Đầu chủ quản lý |
| **Tên Đầu Chủ (Hợp đồng)** | `Ten_Dau_Chu_Hop_dong` | `ownerSideUser.name` | Tên của Đầu chủ quản lý |
| **Điểm Facebook** | `Diem_Facebook` | `ownerSideUser.fbLink` | Đường dẫn trang cá nhân Facebook đầu chủ |
| **Link Gốc** | `Link_Goc` | *(Tự dựng)* | Đường dẫn: `https://proptech.thienkhoi.com/warehouse/sources/{UUID}` |

### 2.1. Phân loại và Phân phối Hình ảnh (Media Handling)
Mảng `media` chứa tất cả hình ảnh liên quan đến căn nhà. Chúng ta lọc và tách chúng theo thuộc tính `type`:
- **Ảnh sổ đỏ/Sơ đồ**: Các ảnh có `type` là `parcel_map` hoặc `certificate_image` được phân phối tuần tự vào các cột `Sơ đồ thửa đất 1` đến `Sơ đồ thửa đất 5`.
- **Ảnh nhà/nội thất**: Các ảnh có `type` là `property_image` hoặc `checkin_image` (ảnh khảo sát) đều được gộp lại lưu vào `raw_images_tk_json` để chuẩn bị cho luồng đẩy lên Cloudflare R2 / Drive.


---

## 🛡️ 3. Quy tắc Đảm bảo An toàn & Ổn định (None-Safety)

Backend API của đối tác trả về giá trị `null` đối với bất kỳ trường thông tin nào bị thiếu hoặc chưa cập nhật. Để tránh lỗi tắt luồng đột ngột (`AttributeError: 'NoneType' object has no attribute 'get'`), tất cả các truy vấn lồng trong python phải áp dụng cú pháp:
```python
district_obj = detail_data.get("district") or {}
quan_name = district_obj.get("name", "")
```
Không được sử dụng `.get("district", {}).get("name")` vì nếu key `district` tồn tại với giá trị `None`, phương thức sẽ trả về `None` thay vì `{}` và gây lỗi khi gọi `.get()` tiếp theo.
