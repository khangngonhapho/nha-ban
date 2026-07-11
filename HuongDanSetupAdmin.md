# Hướng dẫn Setup Web Admin - Khang Ngô Nhà Phố

Tài liệu này lưu trữ các bước cần thiết để thiết lập hệ thống Web Admin quản lý bất động sản (Thêm, Sửa, Xóa) trực tiếp từ Google Sheets thông qua Google OAuth2.

## 🏗️ Kiến trúc & Bảo mật
- **Frontend:** HTML, CSS, Javascript (Không cần Backend server).
- **Database:** Google Sheets.
- **Xác thực (Authentication):** Sử dụng **Google Sign-In (OAuth2)**.
- **Bảo mật:** 
  - Code Frontend có thể để public (GitHub Pages) hoặc private (Vercel/Netlify).
  - Dữ liệu hoàn toàn an toàn vì Google Sheets API chỉ trả về dữ liệu / cho phép ghi khi người dùng đăng nhập bằng đúng tài khoản email đã được cấp quyền (VD: `khangngomr@gmail.com` và `mstrangpmp@gmail.com`). Kẻ lạ dù có mã nguồn cũng không thể truy cập dữ liệu.

---

## 🛠️ PHẦN 1: Cấu hình Google Cloud Console (Bắt buộc)

Thực hiện bởi tài khoản chủ Google Sheet (VD: `khangngomr@gmail.com`).

**Bước 1: Tạo Project**
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/).
2. Đăng nhập bằng tài khoản chủ.
3. Bấm vào Dropdown dự án ở góc trên bên trái -> **New Project**.
4. Nhập Tên dự án (VD: `KhangNgo-Admin`) -> Bấm **Create**.

**Bước 2: Bật Google Sheets API**
1. Menu trái -> **APIs & Services** -> **Library**.
2. Tìm kiếm `Google Sheets API`.
3. Bấm **Enable**.

**Bước 3: Cấu hình OAuth Consent Screen (Màn hình xin quyền)**
1. Menu trái -> **APIs & Services** -> **OAuth consent screen**.
2. Chọn **External** -> Bấm **Create**.
3. Điền thông tin cơ bản:
   - App name: `Khang Ngô Admin`
   - User support email: `khangngomr@gmail.com`
   - Developer contact: `khangngomr@gmail.com`
4. Bấm **Save and Continue** qua các bước Scopes.
5. Tại bước **Test users** -> **Add users**:
   - Thêm các email được phép truy cập (VD: `mstrangpmp@gmail.com`, `khangngomr@gmail.com`).
6. Hoàn tất lưu lại.

**Bước 4: Tạo Credentials (Lấy Client ID)**
1. Menu trái -> **APIs & Services** -> **Credentials**.
2. Bấm **+ Create Credentials** -> Chọn **OAuth client ID**.
3. Application type: Chọn **Web application**.
4. Name: `Admin Web`
5. **Authorized JavaScript origins** (Thêm URL gốc của web):
   - `https://khangngonhapho.vercel.app` (hoặc URL của Vercel nếu dùng Vercel)
6. **Authorized redirect URIs** (Thêm URL chính xác của trang admin):
   - `https://khangngonhapho.vercel.app/admin-nha-ban/`
7. Bấm **Create**.
8. ⚠️ **Copy chuỗi Client ID** (có dạng `xxxxxx.apps.googleusercontent.com`) để dán vào code Frontend.

**Bước 5: Cấp quyền trên Google Sheet**
1. Mở file Google Sheet chứa dữ liệu.
2. Bấm nút **Share** (Chia sẻ).
3. Thêm các email quản trị viên (VD: `mstrangpmp@gmail.com`) với quyền **Editor** (Người chỉnh sửa).

---

## 🌐 PHẦN 2: Host Code Web Admin (Chọn 1 trong 2 cách)

### Cách A: Dùng GitHub Pages (Repo Public)
1. Tạo một repository mới trên GitHub (VD: `admin-nha-ban`).
2. Chế độ: **Public**.
3. Tải code Admin lên repository này.
4. Vào **Settings** -> **Pages** -> Bật deploy từ nhánh `main`.
5. Link truy cập sẽ là: `https://[tên-github].github.io/admin-nha-ban/`.

### Cách B: Dùng Vercel (Repo Private - Bảo mật mã nguồn)
1. Tạo một repository mới trên GitHub (VD: `admin-nha-ban`).
2. Chế độ: **Private**.
3. Tải code Admin lên repository này.
4. Truy cập [Vercel.com](https://vercel.com/) -> Đăng nhập bằng GitHub.
5. Bấm **Add New** -> **Project**.
6. Chọn repository `admin-nha-ban` vừa tạo -> Bấm **Import**.
7. Bấm **Deploy**. Vercel sẽ tự động build và cấp một đường link riêng (VD: `admin-nha-ban.vercel.app`).
   *(Lưu ý: Nếu dùng link Vercel, phải quay lại Google Cloud Console ở Bước 4 để thêm link Vercel vào danh sách `Authorized JavaScript origins` và `Authorized redirect URIs`)*.
