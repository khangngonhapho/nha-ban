# 📷 Quy Tắc Phân Loại & Xử Lý Ảnh (Image Classification)

Tài liệu này quy hoạch toàn bộ thiết lập nghiệp vụ và hạ tầng kỹ thuật lưu trữ, xử lý hình ảnh bất động sản của dự án BDS Khang Ngô.

## 1. Phân Loại Hình Ảnh
Mỗi căn nhà có tối đa 25 hình ảnh lưu trữ trong CSDL, được phân loại thành các nhóm vai trò nghiệp vụ khác nhau:

| Loại ảnh | Vai trò nghiệp vụ | Giới hạn số lượng | Cột lưu trữ trên Google Sheet | Quyền riêng tư |
| :--- | :--- | :--- | :--- | :--- |
| **Sơ đồ / Sổ đỏ** | Bản vẽ kỹ thuật, sổ đỏ pháp lý của căn nhà. | Tối đa 5 hình | Cột `AB-AC` (Sổ 1-2) và `CC-CE` (Sổ 3-5) trên tab Pool | **Mật** (Private) - Ẩn hoàn toàn trên Card/Avatar công khai, chỉ hiển thị trong Carousel chi tiết cho khách đã đăng ký. |
| **Mặt tiền** | Ảnh chụp trực diện phía trước nhà. | Tối đa 1 hình | Cột `AJ` (img_mat_tien) ở Source sheet | **Công khai** (Public) - Làm ảnh đại diện chính của Card BĐS. |
| **Hẻm trước nhà** | Ảnh chụp con hẻm, lối đi phía trước nhà. | Nhiều hình | Phân bổ vào các cột ảnh từ Cột 16-25 (`CF-CO`) | **Công khai** (Public) |
| **Nội thất / Chi tiết** | Phòng khách, phòng ngủ, bếp, toilet... | Nhiều hình | Phân bổ vào các cột ảnh từ Cột 16-25 (`CF-CO`) | **Công khai** (Public) |
| **Ảnh Bìa (Cover)** | Ảnh hiển thị đại diện dự phòng | 1 hình | Tự động lấy từ Mặt tiền | **Công khai** (Public) |

---

## 2. Quy Tắc Nén Ảnh & Xoay Đứng Vật Lý
- **Chế độ ảnh thường:** Khi Admin tải ảnh cục bộ lên, hệ thống tự động nén thông qua HTML5 Canvas về độ phân giải tối đa `1600px`, chất lượng `80% JPEG` để tiết kiệm băng thông và tối ưu tốc độ load.
- **Chế độ ảnh sổ đỏ:** **Không nén**, giữ nguyên độ phân giải siêu nét gốc để đảm bảo phóng to đọc được các chữ in nhỏ trên bản vẽ pháp lý.
- **Xoay ảnh đứng vật lý (EXIF Auto-rotation):** Trong quá trình cào dữ liệu từ Thiên Khôi, các hình ảnh bị chụp ngược/nghiêng sẽ được tự động xoay đứng thẳng vật lý bằng thư viện Python Pillow (`ImageOps.exif_transpose`) ở backend trước khi tải lên CDN để đảm bảo tính mỹ thuật 100%.

---

## 3. Hạ Tầng CDN & Quản Lý Bộ Nhớ
- **Dịch vụ lưu trữ chính:** Cloudinary CDN và Cloudflare R2.
- **Quy tắc dọn dẹp ảnh cũ:** Để tránh tràn hạn ngạch lưu trữ Cloudinary, khi Admin xóa hoặc thay thế ảnh cũ trong mục Biên tập ảnh, hệ thống tự động gọi API Signed Destroy (`/image/destroy`) bằng SHA-1 signature để xóa vĩnh viễn tệp ảnh rác cũ trên máy chủ Cloudinary ngay lập tức.
- **Cơ chế sửa ảnh lỗi hàng loạt:** Dự án duy trì công cụ `repair_diagrams.py` quét SQLite và tự động tải các hình ảnh thô Thiên Khôi chưa di cư lên Cloudinary, sau đó đồng bộ ghi đè link CDN trở lại Google Sheets.
