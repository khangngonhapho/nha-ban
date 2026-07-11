---
id: US-138
status: done
date: 2026-07-11
size: M
---

# US-138: Trang quản lý liên kết di động links.html (Mobile-First) và Thu hồi trực tuyến

## User story
**As a** Môi giới / Admin (Anh Khang Ngô)
**I want** theo dõi các liên kết chia sẻ công khai đã tạo cho khách hàng nào, ghi nhận lịch sử xem nhà của họ, tự động "khóa" link theo số điện thoại của khách hàng đầu tiên kích hoạt, và có thể thu hồi quyền xem hoặc block số điện thoại khách hàng trực tuyến mọi lúc mọi nơi bằng **Trang quản lý liên kết di động `links.html`** độc lập trên Vercel, mở nhanh bằng nút chìa khóa Speed Dial (**`🔑`**) và tích hợp cảnh báo chuyển tiếp trái phép cùng việc gom tất cả sheet về file Tracking Log.
**So that** bảo mật nguồn hàng và bảo vệ chất xám thông tin rổ hàng không bị lộ hoặc chuyển tiếp bất hợp pháp cho người khác, đồng thời quản lý linh hoạt, tiện lợi trên di động mà không cần mở app Google Sheets hay dùng chung trang curator phức tạp.

## Acceptance
- [x] Thay thế nút Canvas `📊` cũ trên Speed Dial bằng nút Quản lý Link chìa khóa **`🔑`** để mở nhanh trang `/links.html` (tránh trùng với nút tạo link nhanh `🔗`).
- [x] Admin có thể quản lý, thu hồi link chia sẻ và block số điện thoại khách hàng trực tuyến bằng **Trang quản lý liên kết di động `links.html`** (Mobile-First) độc lập trên Vercel. Trang này bắt buộc yêu cầu đăng nhập bằng Google OAuth.
- [x] Tất cả các tab quản lý (`Link_Registry`, `Phone_Blacklist`, `Public_Link_Status`, `Public_Phone_Blacklist`) được tạo thêm trực tiếp trên Spreadsheet **Tracking Log** (`1zCAP0pUSZdVNxbEkVl94y_hJc1ShM4PqtB-fxpm_I5Y`) của anh Khang để quản lý tập trung và gọn gàng.
- [x] Trang `links.html` hỗ trợ thiết kế dọc (Mobile-First) với Bottom Navigation chứa 3 tab:
  1. **Danh sách Link:** Dạng thẻ card lớn, hiển thị tên khách, nút Copy, nút `🔴 Thu hồi` (hoặc `🟢 Kích hoạt lại`).
  2. **Nhật ký:** Dòng sự kiện thời gian thực (Event Stream) hoạt động của khách xem nhà, có nút `🚫 Block SĐT` nhanh bên cạnh.
  3. **Blacklist:** Danh sách số điện thoại đang bị chặn, có nút gỡ nhanh.
- [x] Khách hàng sử dụng link đã bị thu hồi trực tuyến sẽ ngay lập tức bị chặn bằng màn hình Glassmorphic khóa.
- [x] Khách hàng có số điện thoại bị block sẽ không thể truy cập bất kỳ liên kết chia sẻ nào khác (kể cả link mới tạo).
- [x] Tự động "khóa" (bind) link chia sẻ với số điện thoại của người dùng đầu tiên nhập SĐT.
- [x] Nếu người dùng đầu tiên chuyển tiếp link cho người khác, người nhận nhập SĐT của họ hệ thống đối chiếu không khớp sẽ khóa truy cập ngay lập tức.
- [x] **Cảnh báo chuyển tiếp (Leak Alert):** Khi phát hiện người nhận thứ 2 nhập SĐT không khớp với mã băm SĐT đã khóa, hệ thống sẽ tự động gửi log cảnh báo `Link bị chuyển tiếp` kèm SĐT người mở trái phép và SĐT chủ gốc về Sheet log trước khi khóa màn hình.
- [x] Để đảm bảo bảo mật và riêng tư, danh sách số điện thoại bị block và SĐT được khóa trên Google Sheets Public sẽ được băm bằng thuật toán SHA-256 (phát sinh hoàn toàn ở client trình duyệt của khách hàng bằng Web Crypto API và đối chiếu với hash trên Sheets).
- [x] SQLite local đồng bộ dữ liệu ngược từ hai tab mới `Link_Registry` và `Phone_Blacklist` của file Tracking Log về máy tính khi chạy tiến trình `restore_db_from_sheets.py`.

## Solution
- **Phía Admin (links.html & Vercel API):**
  - Tạo trang mới hoàn toàn `links.html` được tối ưu hóa cho di động.
  - Vercel Serverless API (`api/index.js`) sử dụng quyền ghi `auth/spreadsheets` để cập nhật trực tiếp lên Google Sheets tab `Link_Registry` và `Phone_Blacklist` của file Tracking Log (`1zCAP...`).
  - Trên máy tính local, tiến trình sync/restore cập nhật ngược trạng thái thu hồi và block về SQLite local.
- **Phía Khách hàng (Vercel View):**
  - Khi tải trang, nếu URL chứa tham số `lnk`:
    - Truy vấn tab `Public_Link_Status` từ Google Sheets Public của file Tracking Log.
    - Nếu link bị thu hồi/không tồn tại/hết hạn -> Hiện overlay khóa toàn màn hình.
    - So khớp SĐT trong `localStorage` hoặc SĐT nhập từ Lead Capture với trường `Bound_Phone_Hash` của link (nếu đã có).
    - **Trường hợp phát hiện Chuyển tiếp trái phép (SĐT không khớp):**
      - Gọi `window.trackAction("Link bị chuyển tiếp", "SĐT nhận: " + B_Phone + " - SĐT đã khóa: " + A_Name_Phone)`.
      - Chặn hiển thị ngay lập tức và hiện màn hình khóa chặn xem.
    - Nếu link chưa bị khóa, khi khách hàng nhập SĐT lần đầu, gọi API `/api/links/bind` băm SHA-256 SĐT đó và khóa vào link vĩnh viễn trên SQLite & Google Sheets.
  - Khi tải thông tin từ `localStorage` hoặc khi nhập Lead Capture:
    - Băm SHA-256 số điện thoại khách và đối chiếu với danh sách trong tab `Public_Phone_Blacklist` của Google Sheets Public.
    - Nếu trùng khớp -> Hiện overlay khóa toàn màn hình.
  - Truyền `link_id` trong payload `trackAction` gửi về Apps Script Tracking Web App để ghi nhận hoạt động.

## 📋 Implementation Plan

### 📊 Cơ sở dữ liệu (Database Schema)

#### SQLite (`raw_archive.db`) / Google Sheets Tracking Log (`1zCAP0pUSZdVNxbEkVl94y_hJc1ShM4PqtB-fxpm_I5Y`)
Tạo tab mới **`Link_Registry`** trong file Tracking Log để quản lý các link đã tạo:
```sql
CREATE TABLE IF NOT EXISTS shared_links (
    link_id TEXT PRIMARY KEY,          -- Khóa chính: LNK-YYYYMMDD-RandomSuffix
    customer_name TEXT NOT NULL,       -- Tên khách hàng
    customer_note TEXT,                -- Ghi chú nhu cầu khách
    shared_house_ids TEXT NOT NULL,    -- Danh sách System_ID phân tách bởi dấu phẩy
    created_at TEXT NOT NULL,          -- Thời gian tạo
    expires_at TEXT,                   -- Thời gian hết hạn (mặc định 30 ngày)
    bound_phone_hash TEXT,             -- SHA-256 của SĐT khách hàng kích hoạt
    status TEXT NOT NULL DEFAULT 'Active' -- Trạng thái: Active / Revoked
);
```

Tạo tab mới **`Phone_Blacklist`** trong file Tracking Log để chặn khách hàng có vấn đề:
```sql
CREATE TABLE IF NOT EXISTS phone_blacklist (
    raw_phone TEXT,                    -- Số điện thoại thô
    phone_hash TEXT PRIMARY KEY,       -- SHA-256 của SĐT (Vercel tự băm tự động)
    blocked_at TEXT NOT NULL,          -- Thời gian block
    reason TEXT,                       -- Lý do
    status TEXT NOT NULL DEFAULT 'Active' -- Trạng thái: Active / Inactive
);
```

#### Google Sheets Public (Các tab mới bổ sung vào Sheet Public trong file Tracking Log)
- Tab **`Public_Link_Status`**: Chứa 4 cột: `Link_ID`, `Status`, `Expires_At`, `Bound_Phone_Hash` (Công thức `=QUERY(Link_Registry!A:H, "SELECT A, F, G, H")`).
- Tab **`Public_Phone_Blacklist`**: Chỉ chứa cột: `Phone_Hash` (Công thức `=QUERY(Phone_Blacklist!A:E, "SELECT B WHERE E = 'Active'")`).

---

### ☁️ Vercel Serverless Backend (`api/index.js` & `vercel.json`)

#### [MODIFY] `api/index.js`
- Cập nhật OAuth Scope thành: `https://www.googleapis.com/auth/spreadsheets` để cho phép Vercel cập nhật Google Sheets.
- Sử dụng Spreadsheet ID `1zCAP0pUSZdVNxbEkVl94y_hJc1ShM4PqtB-fxpm_I5Y` làm đích ghi nhận cho Link Registry và Blacklist.
- Bổ sung định tuyến phục vụ trang `/links` và `/links.html` (đọc file `links.html`).
- Bổ sung các API Endpoint trực tuyến bảo mật bằng Google OAuth Token (Bearer):
  - `GET /api/links/list`: Đọc danh sách link và blacklist từ Google Sheets Tracking Log.
  - `POST /api/links/revoke`: Cập nhật trạng thái link thành `Revoked` trực tiếp lên Sheet `Link_Registry` của file Tracking Log.
  - `POST /api/links/bind`: Trình duyệt khách hàng gọi API khi kích hoạt link lần đầu -> Lưu mã băm SĐT vào Sheets.
  - `POST /api/blacklist/add`: Nhận SĐT ➔ Tính SHA-256 ➔ Ghi vào Sheet `Phone_Blacklist` của file Tracking Log.
  - `GET /api/links/logs`: Đọc trực tiếp nhật ký từ spreadsheet Tracking Log (`1zCAP0pUSZdVNxbEkVl94y_hJc1ShM4PqtB-fxpm_I5Y`) trả về cho Admin xem trên điện thoại.

#### [MODIFY] `vercel.json`
- Bổ sung `links.html` vào danh sách `includeFiles` trong phần build.

---

### 🎨 Tầng Giao diện Admin Di động (links.html - Trang mới hoàn toàn)

#### [NEW] `links.html`
- Trang độc lập mới với mã nguồn CSS/JS tối ưu **Mobile-First**:
  - Giao diện tối sang trọng (Dark Glassmorphism) kết hợp tông màu Gold của Khang Ngô.
  - Tích hợp đăng nhập Google Login ở màn hình khởi chạy.
  - Bottom Navigation Bar (Thanh điều hướng dưới chân) để chuyển đổi qua lại giữa:
    1. **Danh sách Link (Links)**: Dạng thẻ card, hiện tên khách, nút Copy nhanh, nút `🔴 Thu hồi` (hoặc `🟢 Kích hoạt lại` nếu đã thu hồi).
    2. **Nhật ký (Logs)**: Event stream hiển thị hoạt động của khách (A xem căn X, hẹn xem nhà...), nút `🚫 Block` nhanh SĐT đó ngay bên cạnh.
    3. **Chặn SĐT (Blacklist)**: Quản lý danh sách SĐT bị chặn, có nút gỡ nhanh.

#### [MODIFY] `index.html`
- Thay đổi nút Speed Dial:
  - Cũ: Nút Canvas `📊` trỏ tới `/canvas.html`.
  - Mới: Nút Quản lý Link chìa khóa `🔑` trỏ tới `/links.html`.

---

### 📱 Tầng Client (Vercel Web UI)

#### [MODIFY] `static/js/lego_lead_capture.js`
- Khi load trang, nếu URL có tham số `lnk`:
  - Fetch thông tin trạng thái link từ tab `Public_Link_Status` trên Google Sheets Public của file Tracking Log qua GViz API.
  - Nếu link bị thu hồi (`Status === 'Revoked'`) hoặc hết hạn -> Chặn hiển thị bằng màn hình khóa Glassmorphic.
  - So khớp SĐT trong `localStorage` hoặc SĐT nhập từ Lead Capture với `Bound_Phone_Hash` của link (nếu đã có).
  - **Trường hợp phát hiện Chuyển tiếp trái phép (SĐT không khớp):**
    - Gọi `window.trackAction("Link bị chuyển tiếp", "SĐT nhận: " + B_Phone + " - SĐT đã khóa: " + A_Name_Phone)`.
    - Chặn hiển thị ngay lập tức và hiện màn hình khóa chặn xem.
  - Nếu link chưa bị khóa (`Bound_Phone_Hash` trống), khách nhập SĐT lần đầu sẽ gọi API `/api/links/bind` băm SHA-256 SĐT đó và khóa vĩnh viễn vào link.
- Kiểm tra số điện thoại khách hàng:
  - Tính mã băm SHA-256 SĐT khách, đối chiếu với danh sách trong tab `Public_Phone_Blacklist` của Sheets Public. Nếu trùng khớp -> Chặn hiển thị lập tức.

---

### 📊 Tầng SQLite Local (Đồng bộ ngược)

#### [MODIFY] `restore_db_from_sheets.py`
- Cập nhật tiến trình khôi phục: Đồng bộ ngược dữ liệu từ 2 tab mới `Link_Registry` và `Phone_Blacklist` từ file Tracking Log trên Sheets về SQLite cục bộ trên máy tính khi chạy sync.

---

## 📝 Task Checklist (TODO)
- [ ] **Thiết kế & Khảo sát:**
  - [ ] Khảo sát Google Sheets API của `gspread` trong `pool_lego.py`
  - [ ] Thiết kế giao diện mobile Web Admin cho tệp `links.html` (Bottom Navigation, Cards)
- [ ] **Triển khai Code:**
  - [ ] Cập nhật Vercel serverless `api/index.js` và `vercel.json` để định tuyến và bundle `links.html`
  - [ ] Tạo tệp `links.html` (Mobile-First) hoàn chỉnh tích hợp Google Login & 3 tab quản lý
  - [ ] Tạo bảng SQLite mới (`shared_links`, `phone_blacklist`) trong `manager.py`
  - [ ] Cập nhật `restore_db_from_sheets.py` để đồng bộ ngược trạng thái từ file Tracking Log trên Sheets về SQLite
  - [ ] Thay đổi nút Speed Dial Canvas `📊` thành Quản lý Link `🔑` trong `index.html`
  - [ ] Cập nhật frontend client `static/js/lego_lead_capture.js` để kiểm tra link, đối chiếu SĐT và gửi log cảnh báo chuyển tiếp
  - [ ] Tích hợp gửi kèm `lnk` trong payload `trackAction`
- [ ] **Kiểm thử & Đóng gói:**
  - [ ] Viết test case `tests/test_link_revocation.py` cho backend
  - [ ] Kiểm thử thủ công quy trình tạo link -> xem nhà -> mở links.html trên điện thoại để thu hồi -> kiểm tra chặn xem
  - [ ] Đồng bộ hóa log và cập nhật trạng thái User Story thành done

## Verification Plan

### Automated Tests
- Kiểm tra tính nhất quán băm SHA-256 SĐT giữa backend Node.js (Vercel) và Javascript Client.
- Chạy unit test kiểm tra đồng bộ ngược trạng thái `Revoked` từ Sheets về SQLite.
```bash
python -m pytest tests/test_link_revocation.py
```

### Manual Verification
1. **Admin mở trang quản lý trên điện thoại**: Nhấp vào nút `🔑` trong Speed Dial trên điện thoại ➔ Mở ra `/links.html` ➔ Đăng nhập Google thành công.
2. **Kích hoạt & khóa link**: Khách hàng mở link trên điện thoại, nhập SĐT `0901234567`. Link tự động khóa vào SĐT này.
3. **Chuyển tiếp bị chặn & ghi nhận log cảnh báo**: Khách hàng gửi link cho người khác, người nhận nhập SĐT của họ -> Web chặn xem và đồng thời ghi nhận một dòng log cảnh báo `Link bị chuyển tiếp` trên file Tracking Log.
4. **Admin thu hồi trực tuyến qua điện thoại**: Admin mở `/links.html` trên điện thoại di động ➔ Bấm nút **`🔴 Thu hồi`** cạnh link.
5. **Khách hàng bị chặn ngay**: Khách hàng tải lại trang và lập tức bị chặn bằng màn hình khóa.
6. **Kiểm tra đồng bộ ngược**: Chạy `restore_db_from_sheets.py` trên máy tính local, kiểm tra bảng `shared_links` trong SQLite đã được cập nhật trạng thái `Revoked` tương ứng.

## Files touched
- `manager.py`
- `index.html`
- `static/js/lego_helpers.js`
- `static/js/lego_lead_capture.js`
- `api/routes_links.py` [NEW]
- `tests/test_link_revocation.py` [NEW]
- `docs/stories/_inbox/US-138_link_tracking_and_revocation.md` [NEW]
- `api/index.js`
- `restore_db_from_sheets.py`
- `links.html` [NEW]
- `vercel.json`
