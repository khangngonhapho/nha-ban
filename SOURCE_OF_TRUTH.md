---
title: BDS-KhangNgo - Source of Truth
type: source-of-truth
project: BDS-KhangNgo
last-meaningful-update: 2026-06-11
note: File pre-existing trước khi adopt Protocol V1.1. Giữ tên `SOURCE_OF_TRUTH.md` (uppercase) thay vì rename `00 Source of Truth.md` để không break Antigravity workflow đang reference path này.
tags:
  - source-of-truth
  - bds-khangngo
  - real-estate
---

# 🏠 SOURCE OF TRUTH — Dự Án BDS Khang Ngô Nhà Phố

> **Mục đích:** File này là nguồn thông tin duy nhất (single source of truth) cho toàn bộ dự án website bất động sản của Khang Ngô Nhà Phố. Mọi thay đổi cần được ghi chép lại ở đây.

> **Cập nhật lần cuối:** 2026-06-11

---

## 0. 🔄 WORKFLOW — Cách Làm Việc Với AI

### Mỗi khi bắt đầu session mới, nói với AI:

> *"Đọc SOURCE_OF_TRUTH tại `d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\SOURCE_OF_TRUTH.md` trước khi làm."*

Hoặc ngắn gọn hơn:

> *"Web khangngonhapho, đọc SOT trước"*

---

### Luồng xử lý yêu cầu:

```
Bạn đặt yêu cầu
       ↓
AI đọc SOURCE_OF_TRUTH.md  ← lấy đủ context (repo, file path, schema...)
       ↓
AI implement thay đổi trong nha_ban_sheets.html
       ↓
AI copy → index.html → git commit → git push origin main
       ↓
AI cập nhật Change Log + Backlog trong file này
```

---

### Cách đặt yêu cầu theo từng loại:

| Loại yêu cầu            | Cách nói                               | AI sẽ làm                         |
| -------------------------- | ---------------------------------------- | ----------------------------------- |
| **Làm ngay**        | *"Thêm filter khoảng giá vào web"* | Implement + TỰ ĐỘNG `git push` ngay lập tức + cập nhật SOT   |
| **Ghi vào backlog** | *"Ghi vào backlog: [mô tả]"*        | Chỉ cập nhật Backlog, chưa code |
| **Xem trạng thái** | *"Backlog còn gì chưa làm?"*       | Đọc SOT và báo cáo             |
| **Fix bug**          | *"Web bị lỗi [mô tả]"*             | Debug + fix + TỰ ĐỘNG `git push` ngay lập tức + ghi log        |
| **Hỏi thông tin**  | *"Sheet ID là gì?"*                  | Đọc SOT và trả lời ngay        |

> ⚠️ **LUẬT THÉP:** Khách hàng (Khang Ngô) **không bao giờ test Local**. Do đó, mỗi khi có yêu cầu thêm tính năng hoặc sửa lỗi, AI bắt buộc phải **Tự động chạy `git commit` và `git push`** lên nhánh main ngay lập tức sau khi sửa code xong để khách test thẳng trên môi trường Live (GitHub Pages). Không được hỏi lại "Tôi có nên push không?". Mọi lỗi sẽ được fix bằng các commit cuốn chiếu.

---

### ⚠️ Lý do cần đọc SOT trước:

- AI **không nhớ** context giữa các session
- Chat history cũ **không được load tự động**
- File này chứa đủ: repo URL, file path, schema, password, lịch sử — đọc 1 file là đủ

---

## 1. 👥 STAKEHOLDERS (Các bên liên quan)

| Vai trò | Người phụ trách | Quyền hạn |
| :--- | :--- | :--- |
| **Product Owner** | Khang Ngô | Chủ sở hữu dự án, cung cấp data nhà bán gốc, ra quyết định Business, sở hữu GitHub Repo `khangngonhapho`. |
| **Lead Dev / PM** | LHT (mstrangpmp) | Collaborator Git, kiến trúc sư trưởng, quy hoạch PKM, quản lý server/domain và API ngầm. |

---

## 2. 🔗 THÔNG TIN KẾT NỐI CỐT LÕI

| Mục                                 | Giá trị                                                             |
| ------------------------------------ | --------------------------------------------------------------------- |
| **GitHub Repo**                | `https://github.com/khangngonhapho/nha-ban`                         |
| **GitHub Pages URL**           | `https://khangngonhapho.vercel.app/`                         |
| **Owner GitHub**               | `khangngonhapho`                                                    |
| **Collaborator GitHub**        | `mstrangpmp` (vẫn có quyền push)                                 |
| **Branch deploy**              | `main`                                                              |
| **File nguồn (edit)**         | `d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\index.html`                |
| **File deploy (GitHub Pages)** | `index.html` (cùng file, không cần copy)                          |
| **File Source of Truth**       | Nằm trong `.gitignore` — 🛑 BẢO MẬT LOCAL, TUYỆT ĐỐI KHÔNG PUSH GIT |
| **⚠️ QUY TẮC:**             | Chỉ edit trực tiếp `index.html`, TỰ ĐỘNG commit và push từ thư mục dự án |

### Tài nguyên liên kết (Artifact Links):

* **Google Sheet rổ hàng tổng (Data gốc):** [Mở Sheet](https://docs.google.com/spreadsheets/d/1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0/edit?gid=0#gid=0)
* **Google Form đăng ký tìm nhà (Cho khách):** [Mở Form](https://docs.google.com/forms/d/1JbCyE6peGBcsH8EUhlqdwPwDH9k3wwR6Sog9-pBflc4/edit)
* **Google Sheet đăng ký tìm nhà (Log Form):** [Mở Sheet Log](https://docs.google.com/spreadsheets/d/14qsVxa4l3m_J4DiJg4V0ZRGxjiHtNNAhD9sauhRguiU/edit?resourcekey=&gid=2114620836#gid=2114620836)
* **Web Client Role Admin (Tạo link share):** [Mở Web Admin](https://khangngonhapho.vercel.app/?pwd=trang)
* **iCloud Note (Thông tin nhà Raw / Gốc):** [Mở Note](https://www.icloud.com/notes/0a965wA8UmhsMU3c2oqX5jdpw)
* **Schema Sheet Source (Bản nháp Admin):** [Schema Sheet Source.md](./Schema%20Sheet%20Source.md)
* **Schema Sheet Public (Bản website hiển thị):** [Schema Sheet Public.md](./Schema%20Sheet%20Public.md)
* **Schema Sheet Raw (Dữ liệu cào thô):** [Schema Sheet Raw.md](./Schema%20Sheet%20Raw.md)
* **Kế hoạch phiên làm việc tiếp theo:** [NEXT_SESSION.md](./docs/NEXT_SESSION.md)
* **Đặc tả bộ cào dữ liệu Proptech mới:** [proptech_crawler_specification.md](./docs/features/proptech_crawler_specification.md)
* **🧰 Kho Tech Stack (Giải pháp kỹ thuật tái sử dụng):** [00_TECH_STACK/README.md](file:///d:/LHTBrain/00_TECH_STACK/README.md)


### Quy trình deploy chuẩn (Tự động hoá 100%):

```powershell
# Bắt buộc tự chạy sau mỗi task code (không cần hỏi ý kiến user):
git add index.html
git commit -m "feat/fix/chore: mô tả thay đổi"
git push origin main
```

---

## 2. 📊 GOOGLE SHEETS

| Mục                          | Giá trị                                                                                               |
| ----------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Sheet ID**            | `1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0`                                                        |
| **Truy cập dữ liệu** | JSONP endpoint (tránh CORS khi mở local)                                                              |
| **Endpoint**            | `https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json;responseHandler:__gsCallback` |

### Schema cột Google Sheet Public (43 cột thực tế):

> ⚠️ **Quy tắc lệch chỉ số cột (Column Shift Bug):** 
> Dữ liệu được đồng bộ từ sheet **Source** (46 cột) sang sheet **Public** (43 cột) thông qua công thức `=IMPORTRANGE("Source!D3:AT1000")` đặt ở cell A3 để giấu đi 3 cột nhạy cảm đầu tiên của Source (Cột A: `Hinh_mat_tien`, Cột B: `Cu_phap`, Cột C: `Note`).
> Do đó, toàn bộ chỉ số cột trong javascript (`r.c[index]`) trên trang web client sẽ bị **dịch sang trái đúng 3 cột** so với cấu trúc cột trên sheet Source gốc:
> `Chỉ số Public = Chỉ số Source - 3`
> Ví dụ:
> *   `id` ở Source là Cột D (chỉ số 3) -> sang Public là Cột A (chỉ số 0).
> *   `System ID` ở Source là Cột AL (chỉ số 37) -> sang Public là Cột AI (chỉ số 34).
> *   `Hình Mặt Tiền` ở Source là Cột AM (chỉ số 38) -> sang Public là Cột AJ (chỉ số 35).

| Cột | Index JS | Tên field JS | Tên cột Schema | Chỉ số ở Source | Mô tả |
|---|---|---|---|---|---|
| A | `r.c[0]` | `id` | `id` | D (index 3) | Mã căn (13 ký tự, khóa chính) |
| B | `r.c[1]` | `t` | `tieu_de` | E (index 4) | Tiêu đề hiển thị |
| C | `r.c[2]` | `dt` | `dien_tich` | F (index 5) | Diện tích (m²) |
| D | `r.c[3]` | `tang` | `so_tang` | G (index 6) | Số tầng |
| E | `r.c[4]` | `mat` | `mat_tien` | H (index 7) | Bề ngang mặt tiền (m) |
| F | `r.c[5]` | `gia` | `gia` | I (index 8) | Giá bán (tỷ) |
| G | `r.c[6]` | `q`, `ql` | `quan` | J (index 9) | Tên quận |
| H | `r.c[7]` | `phuong` | `phuong` | K (index 10) | Phường |
| I | `r.c[8]` | `loai_hinh` | `loai_hinh` | L (index 11) | `Mặt tiền` hoặc `Hẻm` |
| J | `r.c[9]` | `huong` | `huong_nha` | M (index 12) | Hướng nhà |
| K | `r.c[10]` | `duong_truoc_nha` | `duong_truoc_nha` | N (index 13) | Phân loại đường/hẻm |
| L | `r.c[11]` | `rong_hem` | `do_rong_hem` | O (index 14) | Độ rộng hẻm (m) |
| M | `r.c[12]` | `tinh_trang` | `tinh_trang_nha` | P (index 15) | Tình trạng nhà |
| N | `r.c[13]` | `danh_gia` | `danh_gia` | Q (index 16) | Đánh giá (`Hàng Ngon` / `Hàng Lỗi`) |
| O | `r.c[14]` | `ngu_tang_tret` | `ngu_tang_tret` | R (index 17) | Ngủ tầng trệt |
| P | `r.c[15]` | `chdv` | `chdv` | S (index 18) | CHDV (căn hộ dịch vụ) |
| Q | `r.c[16]` | `m` | `mo_ta` | T (index 19) | Mô tả đã viết lại |
| R–AA | `r.c[17..26]` | `imgs[]` | `anh_1`..`anh_10` | U–AD (index 20–29) | URLs ảnh (tối đa 10) |
| AB | `r.c[27]` | `last_updated` | `Last updated` | AE (index 30) | Thời gian cập nhật cuối cùng |
| AC | `r.c[28]` | `phuong_cu` | `phuong_cu` | AF (index 31) | Phường cũ trước sáp nhập |
| AD | `r.c[29]` | `so_pn` | `so_pn` | AG (index 32) | Số phòng ngủ |
| AE | `r.c[30]` | `so_wc` | `so_wc` | AH (index 33) | Số nhà vệ sinh |
| AF | `r.c[31]` | `ten_duong` | `ten_duong` | AI (index 34) | Tên đường thật |
| AG | `r.c[32]` | `gio_dang` | `gio_dang` | AJ (index 35) | Giờ đăng |
| AH | `r.c[33]` | `trang_thai` | `trang_thai` | AK (index 36) | Trạng thái |
| AI | `r.c[34]` | `system_id` | `System ID` | AL (index 37) | System ID |
| AJ | `r.c[35]` | `img_mat_tien` | `Hình Mặt Tiền` | AM (index 38) | Link ảnh mặt tiền gốc (giấu) |
| AK | `r.c[36]` | `tieu_de_bds` | `Tiêu đề BDS` | AN (index 39) | Tiêu đề BDS AI |
| AL | `r.c[37]` | `dang_bds` | `Đăng BDS` | AO (index 40) | Checkbox kích hoạt Bot |
| AM | `r.c[38]` | `anh_11` | `anh_11` | AP (index 41) | Ảnh bổ sung thứ 11 |
| AN | `r.c[39]` | `anh_12` | `anh_12` | AQ (index 42) | Ảnh bổ sung thứ 12 |
| AO | `r.c[40]` | `anh_13` | `anh_13` | AR (index 43) | Ảnh bổ sung thứ 13 |
| AP | `r.c[41]` | `anh_14` | `anh_14` | AS (index 44) | Ảnh bổ sung thứ 14 |
| AQ | `r.c[42]` | `anh_15` | `anh_15` | AT (index 45) | Ảnh bổ sung thứ 15 |

> ⚠️ **Nguồn thực tế:** Schema này được xác nhận từ header thực tế của Google Sheet ngày 2026-05-24. Cột AJ (index 35) chính là `img_mat_tien` dùng riêng cho Admin.

### Mã quận (nhập vào cột G):

| Quận        | Mã nhập |
| ------------ | --------- |
| Quận 3      | `q3`    |
| Phú Nhuận  | `pn`    |
| Tân Bình   | `tb`    |
| Bình Thạnh | `bt`    |
| Gò Vấp     | `gv`    |
| Quận 10     | `q10`   |

> ⚠️ Nhập **lowercase, không dấu** đúng như bảng trên. Nếu muốn thêm quận mới, cần thêm cả nút filter vào HTML.

### Mã đánh giá (nhập vào cột O):

| Đánh giá    | Giá trị nhập | Màu hiển thị  |
| -------------- | --------------- | ---------------- |
| Hàng tốt     | `Hàng Ngon`  | Xanh lá         |
| Hàng xấu     | `Hàng Lỗi`  | Xám             |
| Bình thường | (để trống)   | Không hiện tag |

---

## 3. 🔐 PHÂN QUYỀN TRUY CẬP

| Role                               | Cách truy cập                      | Tính năng                                                                  |
| ---------------------------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| **Admin (Trang)**            | Thêm `?pwd=trang` vào URL        | Xem tất cả căn, filter theo quận, chọn & tạo share link, xem tab/stats |
| **Khách (có link share)**  | Nhận link dạng `?s=BASE64_TOKEN` | Chỉ xem đúng các căn được chọn                                      |
| **Khách (không có link)** | URL gốc                             | Chỉ thấy thông báo liên hệ                                             |

### Logic share link (Bitmask — cập nhật 2026-05-10):

- **Format mới `?b=<bitmask>`**: Mỗi căn = 1 bit (chọn=1, bỏ=0). Nén bằng bảng ký tự URL-safe (64 ký tự). 64 căn → chỉ ~11 ký tự URL.
- **Lý do đổi**: Mã căn chứa Unicode → `btoa()` crash. Liệt kê 64+ ID → URL >2000 ký tự → bị Zalo/Messenger cắt. Link rút gọn → khách sợ virus.
- **Encode**: `DATA.map(id → SELECTED_IDS.has(id) ? '1' : '0')` → nhóm 6 bit → ký tự B64
- **Decode**: Trong `loadData()` callback, giải mã bitmask → map bit thứ N → ID thứ N trong `fullList`
- **Backward-compatible**: Vẫn hỗ trợ `?s=<IDs>` (comma-separated hoặc base64 JSON cũ)
- **⚠️ Lưu ý**: Bitmask phụ thuộc thứ tự dữ liệu trong Sheet. Nếu thêm/xoá hàng giữa lúc link đang active, vị trí bit sẽ lệch.

---

## 4. 🧠 KEY DECISIONS LOG (Các quyết định kiến trúc)

| Ngày | Vấn đề | Quyết định | Lý do (Context) |
| :--- | :--- | :--- | :--- |
| 2026-05-27 | Kiến trúc Đồng bộ theo nhu cầu (US-037) | Áp dụng On-Demand Pull Ingestion: EXE cục bộ cào -> đẩy lên Pool. Trên Vercel Admin, anh Khang gõ Số nhà + Đường để query trên Pool và tự động copy & sync sang Source (có chứa thông tin custom) để lên sóng công khai. | Giữ Source cực kỳ nhẹ (~50-200 căn), web tải siêu tốc (<0.2s), bảo mật tuyệt đối 5000 căn thô ở Pool, loại bỏ chi phí VPS/Serverless DB, tận dụng Google OAuth2 của Admin. |
| 2026-05-12 | Share link rò rỉ Info Khách | Mã hoá gộp `&c=Tên|Ghi chú` bằng btoa() | Đảm bảo Khách chỉ thấy Tên mình trên UI, còn Ghi chú nội bộ thì giấu đi nhưng vẫn đủ data bắn về Tracking Log. |
| 2026-05-10 | Crash khi encode share link | Chuyển từ base64 sang **Bitmask** (`&b=1011...`) | Mã nhà chứa Unicode làm `btoa()` bị crash. Thay vì encode cả mảng, dùng mảng nhị phân (chọn=1, bỏ=0) rồi nén lại thành chuỗi URL-safe ~11 ký tự để Zalo/Messenger không bị cắt link. |
| 2026-05-10 | Rác cấu trúc PKM | Di dời từ `00_INBOX` sang `01_PROJECTS` | Dự án đã chín muồi thành 1 hệ sinh thái (Client + Admin), không còn là dự án thử nghiệm nằm trong Inbox nữa. |

## 5. 🧩 KIẾN TRÚC LEGO VÀ CHI TIẾT MODULE (pool_lego.py)

Module `pool_lego.py` đóng vai trò là khối Lego điều phối dữ liệu trung tâm, đóng gói toàn bộ logic nghiệp vụ (schema, parser, lưu SQLite, đồng bộ Google Sheets) của các phân hệ Pool. Điều này giúp cô lập logic xử lý dữ liệu và đảm bảo tính tương thích ngược khi nâng cấp hệ thống.

### Nguyên tắc thiết kế (Design Guidelines)
*   **Thiết kế Hướng hàm (Functional Design):** Mã nguồn được triển khai 100% dưới dạng các hàm độc lập, tinh gọn, thực hiện một nhiệm vụ duy nhất (Single Responsibility).
*   **Tránh import vòng (Circular Import Avoidance):** Không import trực tiếp `manager.py` hay `fetcher.py`. Các logic kết nối OAuth2 hoặc Logger được nhận qua tham số dưới dạng hàm callback.
*   **Khớp nối phẳng:** Sử dụng schema 100 cột phẳng đồng nhất `POOL_HEADERS` đại diện cho rổ hàng Pool.

---

### Danh sách Hàm Nghiệp vụ (API Reference)

#### 1. `remove_accents(input_str)`
*   **Vai trò:** Khử toàn bộ dấu tiếng Việt từ chuỗi đầu vào.
*   **Tham số:**
    *   `input_str` (str/None): Chuỗi tiếng Việt cần loại bỏ dấu.
*   **Kết quả trả về:** Chuỗi không dấu tương ứng. Trả về chuỗi rỗng `""` nếu đầu vào là `None` hoặc rỗng.
*   **Lưu trữ:** Chỉ xử lý trên RAM, không lưu xuống đĩa.

#### 2. `get_safe_col_name(header)`
*   **Vai trò:** Chuẩn hóa tiêu đề cột tiếng Việt thành tên cột an toàn dùng cho SQLite (khử dấu, đổi khoảng trắng/ký tự đặc biệt thành dấu gạch dưới `_`).
*   **Tham số:**
    *   `header` (str): Nhãn tiêu đề cột tiếng Việt (ví dụ: `"Sơ đồ thửa đất 1"`).
*   **Kết quả trả về:** Tên cột SQLite an toàn (ví dụ: `"So_do_thua_dat_1"`).
*   **Lưu trữ:** Chỉ xử lý trên RAM.

#### 3. `gen_id_khang_ngo_python(so_nha, duong, quan)`
*   **Vai trò:** Thuật toán mã hóa tự động sinh ra mã ID Khang Ngô độc nhất dựa trên địa chỉ (số nhà, đường, quận) phục vụ so khớp và đăng tin.
*   **Tham số:**
    *   `so_nha` (str/None): Số nhà thô.
    *   `duong` (str/None): Tên đường thô.
    *   `quan` (str/None): Tên quận thô.
*   **Kết quả trả về:** Chuỗi mã ID Khang Ngô tự sinh (ví dụ: `MWTSIH...`).
*   **Lưu trữ:** Chỉ xử lý trên RAM.

#### 4. `get_db_file()`
*   **Vai trò:** Xác định và trả về đường dẫn tệp tin SQLite đang được hệ thống kích hoạt.
*   **Tham số:** Không có.
*   **Kết quả trả về:** Chuỗi tên file database SQLite (`"raw_archive.db"` cho Pool1).
*   **Lưu trữ:** Chỉ xử lý trên RAM.

#### 5. `init_db(db_file=None)`
*   **Vai trò:** Khởi tạo cấu trúc cơ sở dữ liệu SQLite cục bộ bao gồm bảng lưu trữ rổ hàng `listings` (schema 100 cột dựa trên `POOL_HEADERS`) và bảng lịch sử phiên cào `crawl_sessions`. Đồng thời tự động quét và nâng cấp (Migration) cấu trúc bảng nếu có thêm cột mới trong danh sách `POOL_HEADERS`.
*   **Tham số:**
    *   `db_file` (str/None): Tên file SQLite cần khởi tạo. Nếu `None`, tự động lấy qua `get_db_file()`.
*   **Kết quả trả về:** Không có (`None`).
*   **Lưu trữ:** Tạo/Cập nhật cấu trúc tệp tin `.db` SQLite trên đĩa cứng local.

#### 6. `save_raw_to_sqlite(tk_id, metadata, images_tk_list, db_file=None)`
*   **Vai trò:** Ghi nhận hoặc cập nhật dữ liệu thô bóc tách được từ crawler vào cơ sở dữ liệu SQLite. Đặt trạng thái mặc định của căn nhà là `'raw_text'` để chờ xử lý hình ảnh ở bước tiếp theo.
*   **Tham số:**
    *   `tk_id` (str): Mã căn thô đối tác.
    *   `metadata` (dict): Cặp Key-Value chứa dữ liệu thô bóc tách từ DOM.
    *   `images_tk_list` (list): Danh sách URLs hình ảnh thô Thiên Khôi.
    *   `db_file` (str/None): Tên file SQLite để ghi.
*   **Kết quả trả về:** Không có (`None`).
*   **Lưu trữ:** Ghi đè hoặc chèn mới 1 dòng dữ liệu trong bảng `listings` của tệp tin SQLite.

#### 7. `get_table_end_row_index(sheet_id, creds, add_log_message)`
*   **Vai trò:** Sử dụng Google Sheets API truy vấn lấy dòng chỉ số kết thúc thực tế (`endRowIndex`) của Table chính thức trên tab "Pool".
*   **Tham số:**
    *   `sheet_id` (str): Spreadsheet ID.
    *   `creds` (Google OAuth credentials): Đối tượng xác thực Google Cloud.
    *   `add_log_message` (func): Hàm ghi log callback.
*   **Kết quả trả về:** Số dòng kết thúc (int) hoặc `None` nếu xảy ra lỗi.
*   **Lưu trữ:** Không có.

#### 8. `escape_tsv_field(val)`
*   **Vai trò:** Chuẩn hóa dữ liệu văn bản trước khi đưa vào hàng xuất TSV (chuyển tab thành khoảng trắng, bọc dấu nháy kép nếu có ký tự xuống dòng hoặc nháy kép) phục vụ cơ chế copy tay của Admin.
*   **Tham số:**
    *   `val` (any): Giá trị của trường dữ liệu.
*   **Kết quả trả về:** Chuỗi văn bản an toàn (str).
*   **Lưu trữ:** Chỉ xử lý trên RAM.

#### 9. `publish_listing(tk_id, get_google_credentials, load_config, add_log_message, db_file=None)`
*   **Vai trò:** Thực hiện đồng bộ xuất bản dữ liệu của một căn nhà từ SQLite local lên Google Sheets trực tuyến. 
    *   Nếu mã hàng đã tồn tại trên cột A của Sheets, thực hiện chép đè có chọn lọc (chỉ cập nhật hình ảnh và cột Last Crawl, bảo lưu các cột văn bản khác).
    *   Nếu chưa tồn tại, thực hiện chèn dòng mới ở cuối bảng Table chính thức để thừa hưởng format.
    *   Tự động đồng bộ mã ID Khang Ngô mới tạo sang cột `id` của tab `Source` tương ứng.
    *   Cập nhật trạng thái trong SQLite sang `'published'` sau khi đồng bộ thành công.
*   **Tham số:**
    *   `tk_id` (str): Mã căn cần xuất bản.
    *   `get_google_credentials` (func): Hàm callback lấy credentials xác thực Google Cloud.
    *   `load_config` (func): Hàm callback nạp cấu hình hệ thống settings.
    *   `add_log_message` (func): Hàm callback ghi log.
    *   `db_file` (str/None): Tên file SQLite.
*   **Kết quả trả về:** `dict` chứa:
    *   `status` (str): Trạng thái (`'success'` hoặc `'warning'`).
    *   `published_to_cloud` (bool): `True` nếu cập nhật Sheets trực tuyến thành công.
    *   `message` (str): Mô tả chi tiết kết quả.
    *   `row_data` (list): Mảng 100 cột dữ liệu đã được escape phục vụ copy tay dự phòng.
*   **Lưu trữ:** Ghi dữ liệu trực tuyến vào Google Sheets và cập nhật trường `status`, `Last_Sync` trong SQLite.

## 7. 📝 LỊCH SỬ THAY ĐỔI (Change Log)


### 2026-06-16 (Nghiệm thu US-095 - Khắc phục lỗi name 'listings_table' is not defined khi tự động hóa Curation & Xuất bản ở chế độ Pool1 - TEST PASS)
*   **Mã User Story:** `US-095`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
     - **Khai báo listings_table**: Khai báo và gán giá trị tương thích động cho biến `listings_table` dựa trên phân hệ Pool hoạt động (`listings_v2` cho Pool2, `listings` cho Pool1) ở đầu hàm `publish_listing()` trong `pool_lego.py`.
     - **Sửa lỗi NameError**: Khắc phục triệt để lỗi sập luồng tự động hóa curation do NameError 'listings_table' is not defined khi chạy ở chế độ Pool1.
     - **Kiểm thử E2E Playwright**: Đạt tỷ lệ **100% PASS** cho toàn bộ 4 kịch bản kiểm thử E2E Playwright (`test_e2e_curation.py`, `test_e2e_collections.py`, `test_e2e_filters.py`, `test_e2e_modal.py`) trên cả hai viewports Desktop & Mobile.

### 2026-06-16 (Nghiệm thu US-094E - Tích hợp toàn diện, tối ưu hiệu năng và dọn dẹp index.html - TEST PASS)
*   **Mã User Story:** `US-094E`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
     - **Tách tệp Static Helpers & Mock**: Di chuyển logic mock fetch interceptor và các hàm helper tiện ích từ `index.html` sang `static/js/lego_mock.js` và `static/js/lego_helpers.js`.
     - **Làm sạch index.html**: Rút gọn tối đa block inline script trong `index.html` xuống dưới 170 dòng sạch sẽ. Thiết lập query parameter cache-busting `?v=202606161110` cho toàn bộ tài nguyên static trong head (kèm theo link css để tránh cache trình duyệt).
     - **Sửa lỗi Nghiệp vụ & Khởi tạo**: Khắc phục lỗi reset default activeMode của Admin thành `'pool'`, chèn tự động `#adminSpeedDial` và cơ chế click-outside.
     - **Sửa lỗi UI Bộ sưu tập & Speed Dial**: Khôi phục nút lưu bộ sưu tập `#colFloatBtn` và nút xóa bộ sưu tập `.delete-col-btn-float` trong Speed Dial actions, sửa lỗi các hàm toggle không gọi cập nhật UI.
     - **Sửa lỗi bố cục Speed Dial**: Cấu trúc lại CSS định vị `.dial-actions` thành `position: absolute` neo trên nút chính `⚡` cố định góc dưới bên phải viewport (tránh lỗi nút bấm bị đẩy lên giữa màn hình).
     - **Kiểm thử E2E Playwright**: Đạt tỷ lệ **100% PASS** cho toàn bộ 5 kịch bản kiểm thử E2E (`test_e2e_curation.py`, `test_e2e_filters.py`, `test_e2e_collections.py`, `test_e2e_modal.py`, `test_e2e_curator.py`) trên cả Desktop & Mobile.

### 2026-06-15 (Nghiệm thu US-094F - Cô lập Module Chi tiết, Preview & Curation dành riêng cho Admin - TEST PASS)
*   **Mã User Story:** `US-094F`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Cô lập Module Chi tiết, Preview & Curation cho Admin**: Tạo tệp `static/js/lego_detail_admin.js` chứa toàn bộ logic xem chi tiết của Admin, form curation và các tabs quản lý của Admin.
    - **Cơ chế Preview Khách Hàng WebView Iframe**: Triển khai `<iframe>` tải thực tế giao diện khách hàng với tham số `?s=${p.system_id}&preview=true`. Nếu chưa xuất bản tin, hiển thị cảnh báo màu đỏ tương ứng.
    - **Đấu nối Google Sheets API**: Di chuyển logic đồng bộ Google Sheets API `saveSourceChanges` và `saveNewListingFromPool` vào module và xuất ra `window` đảm bảo tương thích ngược 100% cho inline templates.
    - **Chỉnh sửa lego_core.js**: Cập nhật logic `LegoState` để bỏ qua trạng thái Admin trong local storage nếu phát hiện URL chứa tham số `preview=true`, ngăn chặn rò rỉ session Admin vào iframe khách hàng.
    - **Kiểm thử Playwright E2E**: Chạy kiểm thử tự động `scratch/test_e2e_curation.py` giả lập đầy luồng chỉnh sửa, auto-fill AI, chọn ảnh public/sổ đỏ và lưu sheets trên cả Desktop & Mobile đạt 100% SUCCESS.

### 2026-06-15 (Nghiệm thu US-094D - Cô lập Module Bộ sưu tập & Lead Capture - TEST PASS)
*   **Mã User Story:** `US-094D`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Cô lập Module Bộ sưu tập & Lead Capture**: Tạo tệp `static/js/lego_collections.js` chứa toàn bộ logic bộ sưu tập, yêu thích và chia sẻ; tạo tệp `static/js/lego_lead_capture.js` chứa toàn bộ logic chào mừng khách hàng, đăng ký thông tin liên hệ và tích hợp Zalo.
    - **Làm sạch index.html**: Rút gọn hơn 400 dòng lệnh cũ, nạp hai thẻ script mới ở `<head>` và khai báo các alias toàn cục trên `window` để duy trì tương thích ngược 100% cho toàn bộ các module khác.
    - **Giải quyết Sự cố Lớn (Retro)**: Khắc phục lỗi reset mất trạng thái danh sách bộ sưu tập sau khi tải lại bằng cách bền vững hóa `activeCollectionName` trong `localStorage`. Khắc phục lỗi trắng trang (blank page) trên các đường dẫn chia sẻ khách hàng (ví dụ: `/1?b=...`) bằng việc chuyển đổi các đường dẫn tài nguyên tĩnh ở `<head>` từ đường dẫn tương đối sang tuyệt đối.
    - **Kiểm thử Playwright E2E**: Chạy kiểm thử tự động `scratch/test_e2e_collections.py` mô phỏng hành vi Client/Admin và đa thiết bị đạt 100% PASS.

### 2026-06-15 (Nghiệm thu US-094B - Cô lập Module Bộ lọc & Tìm kiếm thông minh - TEST PASS)
*   **Mã User Story:** `US-094B`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Cô lập Module Bộ lọc & Tìm kiếm**: Tạo tệp `static/js/lego_filters.js` và di chuyển toàn bộ logic bộ lọc (quận, phường, đường, hướng, khoảng giá, kết cấu, đánh giá, checkbox tiêu chí) và tìm kiếm thông minh tiếng Việt AND (`+`), khớp số nhà, từ `index.html` sang.
    - **Di chuyển các hàm xử lý phụ trợ**: Di chuyển các hàm tab động, toggle dropdown, checklist tiêu chí động, tìm kiếm, clear lọc nâng cao, và Smart Pool Fallback sang `lego_filters.js`.
    - **Duy trì tương thích ngược**: Nhúng script vào thẻ `<head>` của `index.html`, loại bỏ hơn 800 dòng lệnh cũ, và đăng ký các biến/hàm toàn cục qua `window`.

### 2026-06-15 (Nghiệm thu US-094C - Cô lập Module Chi tiết & Carousel thực tế của Khách hàng - TEST PASS)
*   **Mã User Story:** `US-094C`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Cô lập Module Chi tiết & Carousel của Khách hàng**: Triển khai `static/js/lego_detail_client.js` chứa phương thức `LegoDetailClient.render(p, sbody)` dựng giao diện chi tiết công khai cho khách hàng.
    - **Di chuyển Carousel & Lightbox**: Tách biệt hàm `setupScrollCarousel`, `openLightboxForCarousel`, và toàn bộ hệ thống biến/trình lắng nghe sự kiện của Lightbox (zoom, swipe, keydown, thumbnails, drag) sang `lego_detail_client.js`.
    - **Di chuyển các hàm phụ trợ**: Di chuyển các hàm gallery phụ trợ (`buildG`, `gm`, `ua`) sang `lego_detail_client.js` và export toàn cục qua `window` đảm bảo 100% tương thích ngược cho giao diện Admin.
    - **Tái cấu trúc index.html**: Rút gọn hàm `openS` bằng cách ủy nhiệm render Client detail cho `LegoDetailClient.render`, nạp script mới ở `<head>` và thêm tham số cache-busting `?v=202606151500`.
    - **Kiểm thử Playwright E2E**: Chạy kiểm thử tự động E2E đa viewport (Desktop/Mobile) và đa phân quyền (Client/Admin) thông qua mock JSONP và Sheets API v4 đạt 100% SUCCESS.

### 2026-06-15 (Nghiệm thu US-094A3 - Phân tách Engine Render danh sách Card BĐS - TEST PASS)
*   **Mã User Story:** `US-094A3`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Phân tách Engine Render danh sách Card BĐS**: Triển khai `static/js/lego_render_client.js` và `static/js/lego_render_admin.js` tách biệt hoàn toàn phần render dữ liệu Card (`DocumentFragment`) ra khỏi `index.html` cho cả giao diện Khách hàng và Admin, đảm bảo tương thích ngược 100% và không làm gãy các tính năng tương tác.
    - **Tái cấu trúc index.html**: Liên kết 2 tệp script mới trong `<head>` của `index.html` và rút gọn hàm `render()` gốc qua Event-Delegated rendering, loại bỏ hơn 200 dòng inlined HTML render card cũ dư thừa.
    - **Tách helper function**: Di chuyển hàm `formatPhone` sang `static/js/lego_core.js` làm hàm tiện ích dùng chung và export toàn cục qua `window.formatPhone`.
    - **Triển khai fallback phòng thủ & Cache-busting**: Tích hợp tham số cache-busting `?v=202606151500` cho tất cả script static trong head của `index.html`, đồng thời định nghĩa hàm `formatPhone` dự phòng trực tiếp tại head của `index.html` nhằm ngăn chặn tuyệt đối lỗi sập trang do trình duyệt người dùng lưu cache tệp core cũ.
    - **Kiểm thử Playwright E2E**: Chạy bộ test Playwright E2E đa viewport (Desktop/Mobile) đạt 100% PASS và chụp ảnh minh chứng.

### 2026-06-15 (Nghiệm thu US-094A2 - Xây dựng Lego Core State Store & Tải dữ liệu - TEST PASS)
*   **Mã User Story:** `US-094A2`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Tạo mới Lego Core State Store**: Triển khai `static/js/lego_core.js` định nghĩa `window.LegoState` Pub/Sub event engine làm kho lưu trữ và giao tiếp trạng thái tập trung.
    - **Tách logic Google Auth & Sheet Data Loading**: Di chuyển toàn bộ Google Identity Services (GSI Auth client, login, silent refresh, token validation) và Google Sheets loading actions (`loadData`, `loadPublicDataFallback`) sang `lego_core.js`.
    - **Tách helper functions**: Di chuyển `cv`, `fixImgUrl`, `getDaiNha`, `cleanConsecutiveNewlines`, `parseGia`, `sha256` sang core và export toàn cục (`window.*`) đảm bảo tương thích ngược 100%.
    - **Đấu nối Event-Driven**: Tái cấu trúc `index.html` đăng ký lắng nghe sự kiện (`rawDataLoaded`, `authStatusChanged`, `authRequired`, `authSuccess`, `authError`, `dataLoading`) để cập nhật giao diện mà không gọi trực tiếp từ store.
    - **Kiểm thử Playwright E2E**: Chạy bộ test Playwright E2E đa viewport (Desktop/Mobile) đạt 100% PASS và chụp ảnh minh chứng.

### 2026-06-15 (Nghiệm thu US-094A1 - Tách biệt CSS ngoài ra global.css - TEST PASS)
*   **Mã User Story:** `US-094A1`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Tách tệp CSS tĩnh**: Di chuyển toàn bộ ~3,650 dòng CSS trong `index.html` sang `static/css/global.css`.
    - **Liên kết CSS tĩnh**: Thay thế khối `<style>` thô bằng thẻ `<link rel="stylesheet" href="static/css/global.css">`.
    - **Cấu hình đóng gói & Serving**: Cập nhật `vercel.json` đóng gói thư mục `static/**` và bổ sung middleware trong `api/index.js` phục vụ file tĩnh kèm tiêu đề `Cache-Control` (Edge Caching 1 năm).
    - **Kiểm thử Playwright E2E**: Tích hợp `scratch/test_e2e_curator.py` chạy tự động xác thực hiển thị đa viewport (Desktop/Mobile) đạt 100% PASS.

### 2026-06-14 (Nghiệm thu US-089B - Tích hợp Google Sheets Đa Quyền Hạn & Luồng Xuất bản Public Whitelist - TEST PASS)
*   **Mã User Story:** `US-089B`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Phân tách 3 Google Sheets độc lập**: Tích hợp 3 Spreadsheet ID (`pool2_raw_sheet_id`, `pool2_custom_sheet_id`, `pool2_public_sheet_id`) vào cấu hình hệ thống Pool2 để ngăn ngừa lộ PII.
    - **Đồng bộ đa quyền hạn**: 
      - Đẩy dữ liệu thô và mảng ảnh JSON vào File 1 Raw.
      - Đẩy dữ liệu nghiệp vụ Custom và metadata ảnh an toàn (loại bỏ facade & diagram) vào File 2 Custom.
      - Đẩy whitelist cột sạch và rã mảng ảnh an toàn thành các cột `Ảnh 1` đến `Ảnh N` vào File 3 Public, giữ cột `Last updated` trước các cột ảnh.
      - Hỗ trợ tự động khởi tạo dòng Custom mặc định nếu chưa có.
    - **Tối ưu hóa tránh lỗi API Quota (429)**: Gộp các lệnh thêm cột qua `add_cols(len(missing))` / `insert_cols` và cập nhật dòng tiêu đề 1 bằng một cuộc gọi duy nhất `update()`.
    - **Đồng bộ hóa link R2 tự động**: Cập nhật đồng bộ các link R2 mới vào trường `images_metadata_json` của bảng `listings_custom_v2` trong tiến trình di cư ảnh.
*   **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-14 (Nghiệm thu US-093 - Kiểm tra tính khả dụng và lập báo cáo hình ảnh tự tải lên - TEST PASS)
*   **Mã User Story:** `US-093`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Thiết kế công cụ kiểm toán (`scratch/audit_manual_images.py`):** Xây dựng script Python để quét toàn bộ CSDL Pool1 (`raw_archive.db` bảng `listings`), lọc ra các hình ảnh tự tải lên dựa theo các mẫu đặc tả (Local paths, Drive link, custom R2/Cloudinary chứa pattern `_interior_` / `_sodo` hoặc prefix `SYS-`).
    - **Kiểm thử HTTP đa luồng (User-Agent fix):** Thực hiện kiểm tra tính khả dụng của ảnh từ xa sử dụng `ThreadPoolExecutor` đa luồng, tích hợp User-Agent giả lập trình duyệt Chrome để vượt qua cơ chế chống bot/rate-limit của Cloudflare R2, tránh tình trạng lỗi giả HTTP 503.
    - **Cấu trúc lại báo cáo hợp nhất (`broken_listings_report.md`):** Tái cấu trúc báo cáo thành 3 danh sách riêng biệt dưới các tiêu đề `##` để dễ đóng/mở (collapse). Bổ sung Danh sách 3 báo cáo tình trạng toàn bộ 23 căn chứa ảnh tự tải lên (23 căn hoạt động tốt, 0 căn bị lỗi).
*   **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-13 (Nghiệm thu US-092 - Sửa lỗi Internal Server Error: Missing index.html khi truy cập trang chủ - TEST PASS)
*   **Mã User Story:** `US-092`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Sửa mã nguồn (`api/index.js`):** Thay thế cơ chế đọc tệp tĩnh qua `process.cwd()` bằng mảng đường dẫn đọc tệp dự phòng (multi-fallback), ưu tiên sử dụng `__dirname` (`path.join(__dirname, '..', 'index.html')`) để kích hoạt Vercel NFT (Node File Trace) đóng gói tệp tĩnh vào bundle serverless function.
    - **Cấu hình deployment (`vercel.json`):** Bổ sung thuộc tính `config.includeFiles` để ép Vercel builder đóng gói tệp `index.html` vào function zip.
    - **Đồng bộ hóa tài liệu:** Tạo mới User Story đặc tả lỗi [US-092_fix_homepage_missing_index_error.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-092_fix_homepage_missing_index_error.md) và đồng bộ hóa INDEX.md, NEXT_SESSION.md.
*   **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-13 (Nghiệm thu US-090 - Di cư toàn bộ kho hình ảnh sang Cloudflare R2 & Khắc phục giới hạn Cloudinary - TEST PASS)
*   **Mã User Story:** `US-090`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Di cư SQLite (`migrate_to_r2.py`):** Viết script di cư hình ảnh đa luồng (`ThreadPoolExecutor`) tải ảnh từ Cloudinary cũ và đẩy trực tiếp lên Cloudflare R2 công khai. Cập nhật thành công 5.180 link ảnh mới vào CSDL `raw_archive.db`.
    - **Đồng bộ Google Sheets (`sync_pool_v1_sheet.py`):** Tích hợp thuật toán so khớp chéo tên file (Cross-column Matching) giảm từ 17.200 API calls xuống còn 191 calls (tiết kiệm 99%). Làm sạch và bóc tách các chuỗi mảng JSON dán nhầm trên Sheets về URL đơn sạch sẽ.
    - **Báo cáo lỗi ảnh (`list_broken_listings.py` & `check_db_cloudinary.py`):** Lập báo cáo danh sách 581 căn bị lỗi ảnh (Cloudinary 404 chết không thể di cư) trên cả Google Sheets và SQLite database. Báo cáo tự động trích xuất đầy đủ thông tin địa chỉ (`Ngõ/Số nhà`, `Đường`, `Phường`, `Quận`) và `Nội dung chính` để thuận tiện xử lý thủ công.
*   **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-12 (Nghiệm thu US-089A - Thiết lập CSDL Quan hệ Pool2 & Tích hợp Luồng Cào thô cục bộ - TEST PASS)
*   **Mã User Story:** `US-089A`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Cấu hình & Database Core (`pool_lego.py`):** Thiết lập tệp SQLite `"raw_archive_v2.db"` cho chế độ `"Pool2"`. Khởi tạo bảng `listings_v2` (metadata thô và 19 cột tiêu chí `Criteria_...`), `listings_images` (dòng ảnh độc lập liên kết qua khóa ngoại), và `listings_custom_v2` (thông tin Admin chỉnh sửa đè). Hỗ trợ cơ chế tự động di cư cấu hình cột.
    - **Luồng Cào (`fetcher.py`):** Tích hợp hàm bóc tách tiêu chí `parse_criteria_groups()` và ghi nhận dữ liệu văn bản vào `listings_v2`. Hỗ trợ bóc tách động các badges tiêu chí qua DOM Fallback.
    - **Hình Ảnh & Phân Nhóm (`pool_lego.py`):** Thiết lập cơ chế **phân nhóm lưu trữ hình ảnh (Nội thất trước, Sơ đồ sau)**. Gán chỉ số `sequence_index` tuần tự đúng theo nhóm này vào `listings_images` và cập nhật mảng JSON `raw_images_tk_json`.
    - **Web Admin & API (`manager.py`, `curator.html`):** Tích hợp trường Mặt tiền và Chiều dài trong cả hai bảng SQLite. Đồng bộ dữ liệu join giữa bảng thô và bảng custom cho Admin.
    - **Công cụ Tra cứu (`query_helper.py` & `TRUY_VAN_CSDL.bat`):** Xây dựng menu dòng lệnh tra cứu nhanh CSDL thô cục bộ và tự động mở chi tiết căn nhà dưới dạng trang HTML Premium Dark Mode.
*   **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-11 (Nghiệm thu US-088 - Đổi tên file và di cư tính năng cũ (Pool1) sang Lego - TEST PASS)
*   **Mã User Story:** `US-088`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Kiến trúc Lego (pool_lego.py):** Tạo mới tệp module trung tâm `pool_lego.py` để đóng gói toàn bộ logic nghiệp vụ (SQLite Schema, save raw sqlite, publish Google Sheets) của rổ hàng Pool1 cũ thành các hàm Lego độc lập, ngăn ngừa circular imports qua callback injection.
    - **settings.json:** Đổi tên `curator_config.json` thành `settings.json` (tên thân thiện hơn cho non-tech) và bổ sung thuộc tính `"active_pool_system": "Pool1"`.
    - **fetcher.py:** Đổi tên `crawl_pipeline.py` thành `fetcher.py` (tệp lấy tin) và tích hợp các khớp nối với `pool_lego.py`.
    - **manager.py:** Đổi tên `curator_server.py` thành `manager.py` (tệp điều hành) và điều chỉnh các API endpoint gọi qua `pool_lego.py`.
    - **Đóng gói di động & Script:** Cập nhật file `.spec`, `CHAY_APP.bat`, `build_exe.bat`, `upload_curator_zip.py`, `fix_tilted_images.py`, `restore_db_from_sheets.py` để trỏ đúng sang các tên file mới và build bản chạy exe thành công.
    - **Good Practices:** Định nghĩa thực tiễn tốt `GP-012` về Kiến trúc Lắp ráp Lego và tài liệu hóa chi tiết Section 5 trong `SOURCE_OF_TRUTH.md`.
*   **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-11 (Nghiệm thu US-087 - Fix lỗi không xóa được bộ sưu tập đã tồn tại - TEST PASS)
*   **Mã User Story:** `US-087`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **index.html (Web Admin):**
        - Sửa lỗi không xóa được bộ sưu tập trên Chrome di động do hiện tượng cuộn vi mô (micro-scroll) làm triệt tiêu sự kiện click trong vùng cuộn `overflow-y: auto`.
        - Thiết lập cơ chế tích chọn checkbox 24px kế bên danh sách bộ sưu tập trong modal, cho phép chạm vùng trống của dòng để toggle chọn nhanh.
        - Tích hợp nút Xóa đỏ `🗑️` (chỉ icon không chữ) nổi trên Speed Dial (`#adminSpeedDial` nằm ở vị trí `fixed` ngoài vùng cuộn) khi modal mở rộng.
        - Khắc phục lỗi Speed Dial tự động thu gọn khi click ngoài bằng cách bỏ qua sự kiện đóng khi modal xem BST đang hiển thị.
        - Cập nhật hàm `deleteSelectedCollections()` sử dụng hộp thoại `confirm()` gốc để xác nhận xóa hàng loạt và tự động khôi phục Speed Dial về trạng thái `'list'` sau khi thực hiện xong.
    - **Commit:** `86364a4`
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-11 (Nghiệm thu US-086 - Fix lỗi tạo bộ sưu tập - TEST PASS)
*   **Mã User Story:** `US-086`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **index.html (Web Admin):**
        - Sửa lỗi hiển thị màu chữ trắng trên nền trắng (white-on-white) của các nút bấm trong Modal lưu/xem bộ sưu tập.
        - Bổ sung logic tự động bỏ chọn (uncheck) toàn bộ các checkbox chọn căn trên giao diện ngay khi lưu bộ sưu tập thành công.
        - Điều chỉnh logic so khớp ID của bộ lọc danh sách và bộ sưu tập: chỉ sử dụng duy nhất mã `system_id` để so khớp (không sử dụng Mã Khang Ngô) để tránh lệch dữ liệu.
    - **Commit:** `36401c2` (phiên bản rollback ổn định, giữ các phần fix trên).
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-10 (Nghiệm thu US-085 - Sửa lỗi hiển thị và vỡ bố cục trên điện thoại Android - TEST PASS)
*   **Mã User Story:** `US-085`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **index.html (Web Admin & Client Viewport):**
        - Dịch chuyển drawer đóng của `.filter-panel` trên mobile sang trái (`translateX(-100%)`) thay vì bên phải để trình duyệt di động tự động cắt bỏ phần tử tràn ngoài vùng hiển thị, giải quyết triệt để lỗi kéo giãn canvas ngang lên `200vw` và ngăn trình duyệt tự động zoom-out làm rò rỉ layout desktop lên mobile.
        - Khôi phục tính năng vuốt chạm bằng cách loại bỏ thuộc tính `overflow-x: hidden` trên `html, body` vốn làm Chrome di động chặn/trễ các touch events.
        - Sửa lỗi vỡ bố cục modal chi tiết `.sheet` bằng cách giữ nó vừa vặn trong phạm vi 100% viewport rộng trên di động (max `540px`).
        - Khắc phục xung đột vuốt ngang bằng cách loại bỏ `scroll-behavior: smooth` khỏi `.admin-scroll-carousel` (tránh xung đột với thuật toán `scroll-snap-type: x mandatory` của trình duyệt di động làm dính ảnh).
        - Thiết lập `touch-action: pan-x pan-y` trên các bộ scroll-carousel chi tiết để cho phép cuộn ngang/dọc tự nhiên, đồng thời thiết lập `touch-action: pan-y` trên trình biên tập ảnh JS để bảo lưu cử chỉ vuốt ngang nhạy bén.
        - Tăng tốc độ phản hồi bằng cách giảm thời gian transition opacity của ảnh thẻ từ `0.4s` xuống `0.15s` và bổ sung `decoding="async"` cho các ảnh lazy-loaded để giải phóng main thread khi giải mã ảnh.
    - **Commit:** `397f587`, `ee96520`, `92ec1ed`, `a8896a8`
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô) trên môi trường live Vercel.

### 2026-06-09 (Nghiệm thu US-084 - Biên tập hình ảnh dạng Carousel và tối ưu hóa nút bấm trên Mobile - TEST PASS)
*   **Mã User Story:** `US-084`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **index.html (Web Admin):**
        - Thay thế lưới ảnh 3 cột cũ bằng một khung nhìn Carousel hiển thị 1 ảnh lớn tại một thời điểm (kích thước lớn, dễ nhìn).
        - Thiết kế thanh trượt ngang ảnh nhỏ (Thumbnail Strip) hiển thị bên dưới, tự động cuộn ảnh đang hoạt động vào giữa màn hình và hiển thị viền nổi bật.
        - Tích hợp điều hướng Carousel bằng hai nút Trái/Phải (`◀` / `▶`) lớn và hỗ trợ thao tác vuốt cảm ứng (Swipe) mượt mà.
        - Thiết kế bảng điều khiển các nút chức năng kích thước lớn (chiều cao >= 44px) hỗ trợ thao tác chạm chính xác: Mặt Tiền (🔒), Ảnh Nền (⭐), Dropdown chọn Sổ (S1-S5), Toggle Hiển thị công khai (👁️).
        - Thiết kế hệ thống nhãn nhỏ (Mini-Badges) trên dải thumbnail để quan sát trực quan vai trò và thứ tự công khai.
        - Bổ sung nút **Đẩy Lên Trước ◀** và **Đẩy Ra Sau ▶** để sắp xếp linh hoạt thứ tự công khai của ảnh.
        - Tự động hóa quy tắc lưu ảnh đặc biệt: lưu ảnh Mặt Tiền vào Ảnh 1, ảnh Nền/Cover vào Ảnh 2 và các ảnh công khai còn lại vào Ảnh 3 đến 15 của Source sheet để tương thích với bot đăng tin bên ngoài.
        - Giải quyết triệt để lỗi giật nhảy ảnh về index 0 khi re-render carousel bằng cách sử dụng class `.has-transition` động và vô hiệu hóa transition mặc định trên track.
    - **Commit:** `4ae8c9d` — `fix(carousel): refactor transitions to fix mobile transition bug`
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô) trên môi trường live Vercel.

### 2026-06-09 (Nghiệm thu US-083 - Bổ sung tính năng xoay ảnh bằng chuyển đổi URL Cloudinary trực tiếp trên Web Admin - TEST PASS)
*   **Mã User Story:** `US-083`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **index.html (Web Admin):**
        - Rút gọn thanh công cụ biên tập hình ảnh thành một nút duy nhất: **"🔄 Xoay tất cả +90°"** (loại bỏ nút `-90°` dư thừa).
        - Thêm nút xoay đơn lẻ dưới dạng icon **"🔄"** (không kèm chữ `+90°` để tiết kiệm không gian) ở góc dưới bên trái của mỗi thẻ ảnh Cloudinary.
        - Thêm nút kính lúp **"🔍"** ở chính giữa thẻ ảnh khi hover. Click vào nút này sẽ mở ảnh gốc full-size ở tab mới (`event.stopPropagation()` tránh kích hoạt chọn ảnh của thẻ).
        - Khi xoay ảnh (cả đơn lẻ hoặc hàng loạt), liên kết của nút kính lúp tự động cập nhật sang URL mới đã xoay để hiển thị đúng.
    - **curator.html (Curator App):**
        - Thêm các nút xoay ảnh đơn lẻ (+90° và -90°) bên dưới các hình ảnh trong tab "Biên tập & Xuất bản" của Curator App.
    - **Commit:** `6a35384` & `9c2d5e3`
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô) trên môi trường live Vercel.

### 2026-06-09 (Nghiệm thu US-082 - Sửa lỗi xuống dòng Nội dung chính trong trang chi tiết Pool - TEST PASS)
*   **Mã User Story:** `US-082`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Root cause thật:** Extension Chrome crawl HTML `#Detail_sNoiDung` từ TK (người nhập xuống dòng trong textarea trên web TK) → POST thẳng `noiDungChinh` có `\n` vào GAS `doPost` → Google Sheets cell lưu `\n` vật lý → JS đọc về string có `\n` → browser render xuống dòng thật trong Pool.
    - **pool_backend_v3.gs (line 107):** Strip `\r\n|\r|\n` trong `noiDungChinh` ngay tại GAS `doPost` trước khi ghi vào Pool Sheet — data mới từ Extension sẽ sạch hoàn toàn.
    - **crawl_pipeline.py (line 625):** Strip `\n` trong `Noi_dung_chinh` khi crawl bulk HTML TK.
    - **curator_server.py (line 2386):** Strip `\n` trong `Noi_dung_chinh` khi recrawl lẻ HTML TK.
    - **index.html (4 điểm assign):** Strip `\n` tại tất cả điểm đọc `raw_noi_dung_chinh` từ Pool Sheets rows — data cũ đã tồn tại trong Sheets với `\n` sẽ hiển thị đúng ngay mà không cần re-crawl hay sửa Sheets thủ công.
    - **Commit:** `07434bd` — `fix(US-082): strip \n khoi Noi dung chinh tu Pool Sheets`
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô) trên môi trường live Vercel.

### 2026-06-09 (Nghiệm thu US-081 - Sửa lỗi Carousel Mobile — Zoom tự nhảy ảnh & Chuyển ảnh thiếu animation - TEST PASS)
*   **Mã User Story:** `US-081`
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **touch-action: none trên gallery & lightbox:** Thay `pan-y` bằng `none` để JS kiểm soát 100% gesture — ngăn browser zoom cả trang khi pinch trên carousel.
    - **maxTouches pattern (thay isPinching):** Dùng biến `gwMaxTouches` ghi nhận số ngón tối đa suốt cả gesture, chỉ reset khi tất cả ngón nhấc lên (`e.touches.length === 0`) — giải quyết race condition khi ngón 1 nhấc trước ngón 2.
    - **Cache gwCw + transition một lần:** Cache `gw.offsetWidth` vào biến `gwCw` tại `touchstart` (không đọc layout 60fps), set `transition: none` một lần duy nhất tại `touchstart` thay vì mỗi `touchmove` — loại bỏ forced layout thrashing.
    - **Double-rAF cho snap animation:** `touchend` gọi `rAF(() => { transition=''; rAF(() => snapTo()) })` — frame 1 browser vẽ drag position, frame 2 bật CSS transition + set transform mới → animation bắt đầu đúng cách.
    - **All-px transforms:** Thay `translateX(calc(-N% - Xpx))` bằng `translateX(${-gI*cw - dx}px)` — cùng đơn vị, browser interpolate mượt mà.
    - **will-change: transform trên .gtrack:** GPU composite layer trước, zero-jank animation.
    - **Lightbox carousel track (v6):** Thay cơ chế replace innerHTML + fade bằng flex track chứa toàn bộ hình. Slide navigation dùng translateX track (same pattern as gallery). Swipe thấy cả 2 hình cùng lúc (current trượt ra, next trượt vào).
    - **Pinch-to-zoom trong lightbox:** Implement pinch-to-zoom (scale 1-4x) trên ảnh hiện tại trong lightbox track. Khi scale > 1, swipe = pan ảnh thay vì chuyển hình.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô) trên môi trường live Vercel.


### 2026-06-08 (Nghiệm thu US-080 - Nâng cấp UX Mobile — Tải gộp 1 lần & Lưu ảnh vào Gallery điện thoại - TEST PASS)
*   **Mã User Story:** `US-080` (Nâng cấp UX Mobile — Tải toàn bộ ảnh riêng lẻ & Lưu vào Gallery điện thoại)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Web Share API (Mobile-first):** Refactor `downloadAllListingImages` để sau khi fetch xong Blob[], hệ thống gọi `navigator.share({ files: File[] })` — gửi toàn bộ file ảnh riêng lẻ cùng 1 lần. iOS Safari tự hiện sheet "Lưu N ảnh vào Ảnh?" (tap 1 lần → vào Camera Roll); Chrome Android tự hiện Share Sheet → chọn "Lưu ảnh" → vào Gallery. Không còn popup lặp lại 15 lần.
    - **Sequential Fallback (Desktop/Firefox):** Giữ nguyên cơ chế tải từng file ảnh riêng lẻ (delay 250ms) cho Desktop và các trình duyệt không hỗ trợ Web Share API. **Tuyệt đối không dùng ZIP** — nhất quán 100%: mọi thiết bị đều nhận file ảnh riêng lẻ.
    - **Progress Bar Inline:** Thay thế trạng thái nút đơn giản bằng thanh tiến trình (`dl-progress-wrap`) hiển thị ngay dưới nút bấm, cập nhật thời gian thực theo từng ảnh fetch xong. Không có popup, không modal ngoài.
    - **`fetchAllBlobs`:** Tách riêng hàm fetch tất cả Blob song song (có error-handling từng ảnh), một ảnh lỗi không hủy toàn bộ batch. Ghi log warning và bỏ qua ảnh lỗi tiếp tục xử lý.
    - **Toast thành công:** Sau khi hoàn thành, `showToast("✅ Đã lưu N ảnh vào Gallery!")` hiện lên — không còn `alert()` gây chặn UI.
    - **Bảo toàn từ US-079:** Giữ nguyên logic loại trừ ảnh sổ đỏ/sơ đồ pháp lý (`window.isListingSodoUrl`), đặt tên file `[SystemID]-[Index].[ext]`, tracking action.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô) trên môi trường live Vercel.

### 2026-06-08 (Nghiệm thu US-079 - Tải toàn bộ hình ảnh căn nhà dạng các file ảnh riêng lẻ cho Admin - TEST PASS)
*   **Mã User Story:** `US-079` (Tải toàn bộ hình ảnh căn nhà dạng các file ảnh riêng lẻ cho Admin)
*   **Các thay đổi thực tế đã deploy & nghiệm thu (Retro & Adjustments):**
    - **Tải ảnh riêng lẻ tuần tự**: Thay đổi hoàn toàn cơ chế nén ZIP (do khó giải nén trên điện thoại di động) thành cơ chế tải tuần tự từng ảnh riêng lẻ trực tiếp về máy.
    - **Chống chặn tải hàng loạt**: Triển khai delay `250ms` giữa các lượt tải để tránh cơ chế chặn tải hàng loạt của trình duyệt trên cả máy tính và điện thoại.
    - **Thu thập & Loại trừ ảnh nhạy cảm**: Hàm `downloadAllListingImages()` tự động gom ảnh mặt tiền (`p.img_mat_tien`) và các ảnh trong `p.imgs`, đồng thời lọc sạch các ảnh sơ đồ/sổ đỏ qua hàm kiểm tra `window.isListingSodoUrl` để bảo mật thông tin pháp lý.
    - **Quy tắc đặt tên file khoa học**: Đặt tên ảnh tự động dưới dạng `[SystemID]-[Index].[ext]` (ví dụ: `SYS-20260608-001-1.jpg`), giúp gom nhóm hình theo căn cực kỳ dễ dàng.
    - **Giao diện & Trạng thái tải**: Bổ sung nút bấm xanh lá "📥 Tải toàn bộ ảnh" bên cạnh nút "Copy link nhanh" ở detailed view, và thêm icon `📥` vào Speed Dial FAB chi tiết. Hiển thị nhãn chờ `⏳ Đang tải [STT]/[Tổng]...` trực quan trên nút.
    - **CORS Fallback**: Tích hợp cơ chế tự động mở ảnh trong tab mới nếu trình duyệt gặp lỗi chặn CORS khi fetch ảnh.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-08 (Nghiệm thu US-078 - Tích hợp nút Tự động điền AI trong Pool và bảo mật số nhà trên Vercel Admin - TEST PASS)
*   **Mã User Story:** `US-078` (Tích hợp nút Tự động điền AI trong Pool và bảo mật số nhà trên Vercel Admin)
*   **Các thay đổi thực tế đã deploy & nghiệm thu (Retro & Adjustments):**
    - **Tách cấu trúc JSON Output của AI**: Chia nhỏ schema JSON output từ AI thành các trường riêng biệt (`tieuDeChinh`, `tieuDePhu`, `moTaChiTiet`, `gocNhinDauTu`, `phuongCu`) giúp AI tập trung viết đúng yêu cầu của từng phần trong Master Prompt Trà Mi, khắc phục triệt để lỗi AI bỏ sót mục 2 (Tiêu đề phụ 🏩).
    - **Ghép mô tả public và loại bỏ markdown**: Backend thực hiện ghép nối các trường này một cách chuẩn xác: đặt `tieuDePhu` lên đầu, tiếp đến là `moTaChiTiet`, và chèn dòng kẻ `---` ngăn cách với `gocNhinDauTu`. Đồng thời tự động loại bỏ các dấu in đậm markdown `**` trên toàn bộ văn bản trước khi trả về.
    - **Quy tắc bảo mật số nhà động**: Backend tự động trích xuất số nhà thô (`body.soNha`, ví dụ `"63"`) và chèn một cảnh báo bảo mật nghiêm ngặt (`🚨 QUY TẮC BẢO MẬT ĐỊA CHỈ`) vào User Prompt, bắt buộc AI so khớp và loại bỏ số nhà cụ thể khỏi Tiêu đề chính, Tiêu đề phụ, và Mô tả.
    - **Tích hợp nút Tự động điền trên giao diện Admin**: Triển khai hàm `autoFillCurationDetails` phía client-side (`index.html`) để gọi API `/api/ai/generate`, xử lý trạng thái loading và tự động điền form, cùng cơ chế fallback pre-fill template cũ nếu xảy ra lỗi.
    - **Đồng bộ phường cũ**: Ghi nhận và chuyển thông tin phường cũ (`phuong_cu`) sang cột AF của Source sheet khi lên sóng thành công.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô) trên môi trường live.

### 2026-06-08 (Nghiệm thu US-077 - Sắp xếp thứ tự ưu tiên Phường và sửa lỗi hiển thị header Source - TEST PASS)
*   **Mã User Story:** `US-077` (Kiểm tra sự đầy đủ, sắp xếp thứ tự ưu tiên Phường và sửa lỗi hiển thị header Source)
*   **Các thay đổi thực tế đã deploy & nghiệm thu (Retro & Adjustments):**
    - **Sắp xếp thứ tự ưu tiên Phường chuẩn xác**: Định nghĩa danh sách phường ưu tiên (`WARD_PRIORITY`) gồm 19 phường nghiệp vụ theo đúng thứ tự PO yêu cầu. Triển khai hàm chuẩn hóa dấu tiếng Việt (`normalizeVietnameseTones`) để so khớp chính xác giữa các kiểu gõ NFC/NFD và hàm `sortWardsByPriority(wardList)` sắp xếp có trọng số.
    - **Cập nhật STATIC_WARD_MAP**: Cấu hình các phường tĩnh của 5 quận trọng điểm (Quận 3, Quận 10, Bình Thạnh, Tân Bình, Phú Nhuận) theo đúng thứ tự ưu tiên.
    - **Hỗ trợ 2 chế độ hiển thị**:
        - Chế độ hiển thị tất cả (không chọn quận): Gộp các phường tĩnh và các phường động từ dữ liệu thực tế, lọc trùng lặp và sắp xếp theo ưu tiên (các phường ngoài danh sách xếp sau theo bảng chữ cái).
        - Chế độ chọn quận cụ thể: Chỉ hiển thị các phường thuộc các quận được chọn và sắp xếp theo thứ tự ưu tiên tương ứng.
    - **Loại bỏ hàng tiêu đề của Source sheet**: Cập nhật hàm `loadData()` để bỏ qua hàng thứ 2 của dữ liệu nhận được từ Google Sheets (có chỉ số `index === 0` trong `sourceRows`) và lọc bỏ bằng `.filter(Boolean)`. Loại bỏ hoàn toàn lỗi hiển thị dữ liệu rác "phuong" và "UAN" trên UI.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô) trên môi trường live.

### 2026-06-08 (Sửa lỗi nghiệm thu & Điều chỉnh giao diện bộ lọc US-076 - TEST PASS)
*   **Mã User Story:** `US-076` (Nâng cấp bộ lọc thông số chi tiết nâng cao)
*   **Các sửa đổi thực tế đã deploy & nghiệm thu (Retro & Adjustments):**
    - **Khóa vị trí chân trang bộ lọc trên Mobile**: Tái cấu trúc `#filterPanel` trên mobile sang Flexbox dọc (`display: flex; flex-direction: column; overflow: hidden;`) và bao bọc toàn bộ nội dung cuộn vào thẻ `.filter-scroll-content` (`flex: 1; overflow-y: auto;`). Nút hành động chân trang `.filter-footer-actions` được đặt tương đối (`position: relative; flex-shrink: 0;`), loại bỏ triệt để lỗi trôi nổi lơ lửng ở giữa màn hình khi cuộn do CSS Transform Containing Block.
    - **Tráo đổi vị trí 2 nút hành động**: Đưa nút "Tìm kiếm" sang góc phải và nút "Xóa điều kiện" sang góc trái ở chân trang để phù hợp với trải nghiệm người dùng.
    - **Giải quyết lỗi đè nút Settings**: Tự động tăng khoảng cách bánh răng `.admin-speed-dial` lên `bottom: 120px !important` khi bộ lọc mở trên mobile, tránh chồng lấp phím bấm.
    - **Chặn tự động đóng bộ lọc**: Vô hiệu hóa tính năng click ra ngoài để đóng bộ lọc khi thao tác trên thiết bị di động (< 768px).
    - **Khắc phục lỗi iOS Safari Auto-zoom**: Ép kiểu `font-size: 16px !important` cho tất cả các thẻ input, select, và textarea trên mobile, giải quyết triệt để lỗi tự động zoom giao diện làm lệch màn hình của iOS.
    - **Xử lý số thập phân có dấu phẩy (Comma decimal range parsing)**: Thêm hàm `parseFloatHelper` chuẩn hóa dấu phẩy thành dấu chấm. Cập nhật logic `getFiltered()` để ưu tiên trường giá đã phân tích sạch (`p.gia`) và chuyển đổi so khớp số học qua hàm helper này, loại bỏ lỗi hiển thị căn `8,5 tỷ` khi đặt giới hạn tối đa là `8`.
    - **Được kiểm thử đạt và nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô) trên môi trường live.

### 2026-06-07 (Nghiệm thu US-076 - Nâng cấp bộ lọc thông số chi tiết nâng cao - TEST PASS)
*   **Mã User Story:** `US-076` (Nâng cấp bộ lọc thông số chi tiết nâng cao)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Nâng cấp bộ lọc 6 thông số khoảng**: Hỗ trợ đầy đủ Khoảng giá (tỷ), Diện tích sổ (m²), Diện tích thực tế (m²), Ngang (mặt tiền) (m), Rộng hẻm (m), và Số phòng ngủ (phòng) sử dụng cấu trúc Từ/Đến.
    - **Bố cục giao diện CSS responsive**: Thiết kế dạng Grid 2 cột tự co giãn trên laptop/desktop và dọc linh hoạt trên di động. Các ô nhập tròn viền xám kem, nhãn phụ "Từ"/"Đến" ở phía trên, đơn vị ("tỷ", "m²", "m", "phòng") hiển thị ở phía góc phải bên trong ô nhập.
    - **Logic ưu tiên dữ liệu thô (Pool-first)**: Logic lọc `getFiltered()` ưu tiên so khớp dữ liệu gốc từ Pool (`raw_gia_chao`, `raw_dt_tren_so`, `raw_dt_thuc_te`, `raw_mat_tien`, `raw_duong_truoc_nha`, `raw_so_pn`). Nếu dữ liệu trống hoặc không có liên kết dòng Pool, hệ thống tự động fallback sang dữ liệu đã biên tập trong Source (`gia`, `dt`, `mat`, `rong_hem`, `so_pn`).
    - **Lưu trữ & Khôi phục trạng thái (State Persistence)**: Tự động lưu 12 ô nhập lọc nâng cao vào `localStorage` (`adminState.adv`) và tự khôi phục khi tải lại trang qua `saveState()` và `restoreState()`.
    - **Xóa bộ lọc (Reset)**: Nút "Xóa điều kiện" / "↺ Xóa lọc" được cập nhật để xóa sạch toàn bộ 12 trường lọc nâng cao này.
    - **[US-076.2] So khớp số nhà theo tiếp đầu ngữ (Prefix matching)**: Đơn giản hóa helper `matchHouseNumber()` sử dụng `.startsWith()`, cho phép tìm kiếm chính xác số nhà phức tạp (ví dụ gõ "100.8" vẫn ra "100.85b").
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô) trên môi trường live.

### 2026-06-07 (Nghiệm thu US-074 - Tối ưu hóa bố cục giao diện hiển thị trên thiết bị Laptop và màn hình lớn - TEST PASS)
*   **Mã User Story:** `US-074` (Tối ưu hóa bố cục giao diện hiển thị trên thiết bị Laptop và màn hình lớn)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Tối ưu Grid hệ thống Filter Panel trên Laptop**: Trên màn hình rộng (width >= 768px), bảng bộ lọc chuyển đổi sang dạng Grid 2 cột tự động co giãn. Cột trái cố định nhãn rộng `160px`, cột phải chứa các bong bóng/tabs bộ lọc. Hỗ trợ hiển thị Phường/Đường/Hướng tự co dãn chiều cao bằng max-height và transition khi lọc theo Quận.
    - **Mở rộng Modal Curation/Admin chi tiết**: Tăng kích thước modal `.sheet` lên `1100px` trên màn hình desktop/laptop lớn (width >= 1200px) để hiển thị song song 2 cột rộng rãi.
    - **Sắp xếp song song Curation Admin**: Cho phép cột thông tin thô (`#accPool`) và cột biên tập/curator (`.admin-accordion`) hiển thị song song cạnh nhau, thanh copy nhanh (`.admin-quick-link-bar`) được trải rộng toàn màn hình.
    - **Bảo toàn giao diện Mobile First**: Mọi thay đổi grid/flexbox đều được đóng gói trong media queries, đảm bảo trên thiết bị di động (< 768px) giữ nguyên bố cục 1 cột cuộn dọc và Bottom Sheet mượt mà.
    - **Khắc phục lỗi hiển thị Laptop**:
      - Sửa lỗi hình đại diện bị thu nhỏ (xẹp ảnh) do co flexbox bằng cách di chuyển media query xuống cuối file CSS và gán `!important` cho layout card của `.crow` và `.ibox`.
      - Sửa lỗi rò rỉ grid panel khi ẩn bằng cách ràng buộc bộ lọc CSS grid chỉ khi có lớp `.open` (`#filterPanel.open`).
      - Sửa lỗi cuộn lồng nhau (nested scrollbar) cắt mất accordion header `📄 PREVIEW KHÁCH HÀNG` bằng cách loại trừ `.admin-accordion` khỏi CSS `overflow-y` của thẻ con `.sbody`.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô) trên môi trường live.

### 2026-06-06 (Nghiệm thu US-073 - Khắc phục lỗi lệch chỉ số cột ảnh nội thất 16-25 khi lưu Curation - TEST PASS)
*   **Mã User Story:** `US-073` (Khắc phục lỗi lệch chỉ số cột ảnh nội thất 16-25 khi lưu Curation)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Phân giải chỉ số cột tập trung (DRY Helpers)**: Triển khai 3 helper phân giải chỉ số cột ảnh nội thất 1-25 (`getPoolInteriorColIdx`), ảnh sổ 1-5 (`getPoolSodoColIdx`), ảnh hẻm 1-10 (`getPoolAlleyColIdx`) loại bỏ hoàn toàn việc tính chỉ số tĩnh gây lệch cột.
    - **Hợp nhất Logic Trích xuất Ảnh**: Tái cấu trúc hàm `getPublicImagesFromForm` thành Single Source of Truth cho việc trích xuất ảnh, loại bỏ hoàn toàn các logic tính toán rời rạc trùng lặp ở `saveSourceChanges` và `saveNewListingFromPool`.
    - **Đồng bộ RAM khi Đăng căn**: Sửa lỗi ghi đè dữ liệu rỗng lên Google Sheets khi lên sóng bằng cách sao chép các ảnh mới tải lên từ bộ nhớ RAM `pool_row_data` vào dòng dữ liệu thô `matchedRow` của Sheets trước khi xuất bản.
    - **Nâng cấp dải ảnh Backend**: Điều chỉnh luồng quét di cư ảnh `run_image_migration_thread` trong `curator_server.py` để ghi nhận và lưu trữ trọn vẹn dải 25 ảnh thô thay vì giới hạn 15 ảnh như trước.
    - **Cơ chế Tự phục hồi Credentials & Throttling**: Tự động đồng bộ và sao lưu tệp xác thực Google Cloud vào Home Directory cục bộ (`~/.bds_khangngo/credentials.json`) để tránh bị xóa khi dọn dẹp Git. Hỗ trợ quét tự động, xác minh chữ ký các tệp khóa `khangngo-admin-*.json` hợp lệ trực tuyến và tự sửa đè lên `credentials.json` lỗi. Giới hạn tần suất log cảnh báo Sheets lỗi trên UI tối đa 1 lần mỗi 10 phút.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-05 (Nghiệm thu US-053 - Admin tự upload hình ảnh local cho căn nhà và quản lý tags, public - TEST PASS)
*   **Mã User Story:** `US-053` (Admin tự upload hình ảnh local cho căn nhà, tùy chọn nén & phân loại ảnh sổ/ảnh thường, tagging lại và nâng cấp schema hình ảnh)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Local Image Uploader UI**: Tích hợp giao diện Glassmorphism sang trọng cho phép tải ảnh trực tiếp từ máy cục bộ lên Cloudinary CDN sử dụng Signed REST API và SHA-1 signature tính toán client-side.
    - **Nén & Phân loại linh hoạt**: Hỗ trợ 2 chế độ: *Ảnh thường* (tự động nén Canvas max 1600px, 80% JPEG, tự động điền slot trống, mặc định Public) và *Ảnh sổ* (không nén, điền slot Sổ 1-5, mặc định Private).
    - **Mở rộng Schema an toàn chống Column-Shift**: Nâng cấp schema Sheet Source lên 46 cột (thêm Ảnh 11-15 ở cột AP-AT) và Sheet Pool lên 93 cột (thêm Ảnh 16-25 ở cột CF-CO), căn chỉnh và bảo toàn vị trí lưu trữ Sổ 3-5 ở dải cột CC-CE.
    - **Hotfix & Ổn định Production**: Khắc phục lỗi Syntax Error `\n\n` gây treo Vercel load, lỗi redraw DOM do Selector bắt sai textbox Ghi chú, và lỗi Google Sheets API 400 do lệch range lưu trữ.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-04 (Nghiệm thu US-068 - Tự động sinh ID cho luồng cào từng căn lẻ - TEST PASS)
*   **Mã User Story:** `US-068` (Tự động sinh ID cho luồng cào từng căn lẻ)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Endpoint `/api/listings/<tk_id>/recrawl`**: Hỗ trợ tự động cào mới các căn chưa tồn tại trong SQLite database.
    - **Sinh Mã ID tự động**: Tự động sinh Mã Khang Ngô bằng hàm `gen_id_khang_ngo_python()` và System ID dạng `SYS-YYYYMMDD-XXX` khi cào lẻ, đồng thời bảo toàn mã ID cũ nếu đã tồn tại.
    - **SQLite và Pool Sheet Integration**: Đảm bảo các ID tự sinh được lưu trữ nhất quán vào SQLite database (`raw_archive.db`) thông qua `save_raw_to_sqlite` và đồng bộ đầy đủ lên Pool sheet.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-03 (Nghiệm thu US-061 - Khắc phục triệt để lỗi hết hạn phiên đăng nhập Google và tự động làm mới token ngầm - TEST PASS)
*   **Mã User Story:** `US-061` (Khắc phục triệt để lỗi hết hạn phiên đăng nhập Google và tự động làm mới token ngầm (Google OAuth Session Timeout Resolution with Auto Silent Refresh))
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Hàm `ensureValidGoogleToken()` và Hàng đợi Token**: Xây dựng hàng đợi `window.tokenResolvers` để gom tất cả các yêu cầu token phát sinh trong thời gian làm mới. Khi có nhiều yêu cầu token đồng thời, chỉ kích hoạt một luồng silent refresh duy nhất.
    - **Làm mới token ngầm (Silent Refresh)**: Tích hợp GSI `requestAccessToken({ prompt: 'none' })` để lấy/làm mới token OAuth2 ngầm định kỳ bằng session cookie của Google. Thiết lập khoảng thời gian chạy ngầm `setInterval` mỗi 5 phút để kiểm tra và tự động gia hạn token trước khi hết hạn 15 phút.
    - **Cơ chế Fallback Đăng nhập Chủ động (Interactive Login Fallback)**: Nếu silent refresh thất bại (do cookie bị chặn hoặc phiên Google hết hạn), hiển thị thông báo tương tác yêu cầu đăng nhập lại mà không làm mất thông tin biên tập trên form hoặc tải lại trang.
    - **Tích hợp Gọi API bảo mật**: Chèn cuộc gọi `await ensureValidGoogleToken()` vào trước tất cả các API thao tác ghi dữ liệu hoặc tải hình ảnh bảo mật.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-03 (Nghiệm thu US-062 - Sửa lỗi sắp xếp theo cập nhật mới nhất/cũ nhất tùy theo danh sách đang xem - TEST PASS)
*   **Mã User Story:** `US-062` (Sửa lỗi sắp xếp theo cập nhật mới nhất/cũ nhất tùy theo danh sách đang xem)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Chuẩn hóa temp_id của Pool**: Thay đổi `temp_id` của các căn Pool thô từ chuỗi `"pool_SYS-..."` sang số nguyên `index + 1` đại diện cho thứ tự dòng trong mảng `POOL_ROWS` (Sheet Pool). Điều này khắc phục triệt để lỗi khi click chọn sắp xếp theo cập nhật mới nhất (`⏱️`) trong Kho Pool bị đơ/đóng băng do `parseInt` ra `NaN`.
    - **Định tuyến sắp xếp động theo chế độ xem (Smart Sorting Routing)**: Sửa logic trong hàm `render()` để rẽ nhánh so sánh động. Khi ở chế độ xem **Kho Pool** và chọn lọc **Chỉ căn lên sóng** (`showOnAirOnly === true`), hệ thống tự động ánh xạ phần tử tương ứng trong `DATA` để lấy `temp_id` đại diện cho thứ tự dòng trong mảng `DATA` (Sheet Source), giúp hiển thị đúng thứ tự lên sóng thực tế. Ngược lại, nếu ở chế độ xem Tất cả Pool hoặc Client/Source thông thường, hệ thống sẽ sử dụng trực tiếp chỉ số dòng tương đối của chính mảng đó.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-02 (Nghiệm thu US-060 - Bỏ chọn tất cả hình ảnh trong biên tập hình Admin cho căn đã lên sóng và mặc định bỏ chọn cho căn chưa lên sóng - TEST PASS)
*   **Mã User Story:** `US-060` (Bỏ chọn tất cả hình ảnh trong biên tập hình Admin cho căn đã lên sóng và mặc định bỏ chọn cho căn chưa lên sóng)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Mặc định bỏ chọn cho căn chưa lên sóng (Pool):** Toàn bộ hình ảnh trong lưới biên tập của căn Pool chưa lên sóng đều mặc định unchecked và không có nhãn vai trò, hidden inputs bắt đầu bằng chuỗi rỗng `""`.
    - **Nút "✕ Bỏ All" cho căn đã lên sóng:** Tích hợp nút reset toàn bộ ảnh và vai trò trên thanh công cụ biên tập kèm hộp thoại xác nhận.
    - **Thuật toán sắp xếp rổ ảnh:** Sắp xếp lưới hiển thị ảnh ưu tiên theo thứ tự: Sổ -> Mặt tiền -> Nền -> Công khai -> Còn lại.
    - **Sắp xếp động thời gian thực (Real-time Sorting):** Tự động nhảy ảnh về đúng vị trí phân loại ngay khi thay đổi vai trò hoặc check/uncheck mà không gây giật cuộn màn hình (Scroll-preservation).
    - **Quy tắc tích chọn vai trò:** Tự động bỏ check "Hiện" khi gán Mặt Tiền/Sổ, tự động tích check "Hiện" khi gán Nền.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-02 (Nghiệm thu US-059 - Biểu mẫu Đăng ký Thông tin cho Link Công khai & Phản hồi Khách hàng qua Zalo - TEST PASS)
*   **Mã User Story:** `US-059` (Biểu mẫu Đăng ký Thông tin cho Link Công khai & Phản hồi Khách hàng qua Zalo)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Tạo Link Công Khai Nhanh:** Bổ sung nút "⚡ Tạo Link Công Khai Nhanh" trong `#linkModal` cho phép Admin tạo và sao chép trực tiếp link chia sẻ rổ hàng hoặc đơn căn không chứa thông số khách hàng `c` về clipboard.
    - **Lead Capture Form (Thu thập thông tin khách):** Thiết kế overlay `#leadCaptureModal` dạng Glassmorphic mờ ảo cao cấp chặn toàn màn hình của khách hàng truy cập từ link công khai. Validate định dạng Số điện thoại Việt Nam hợp lệ (10 chữ số). Lưu thông tin khách hàng vào `localStorage` và tự động pre-fill nếu URL chứa tham số `c`.
    - **Khung tương tác phản hồi qua Zalo:** Bổ sung `.client-feedback-box` hiển thị 2 nút lựa chọn dưới phần mô tả căn nhà: "📅 Hẹn đi xem nhà" và "✏️ Cần tìm căn khác, gửi lại nhu cầu" cho khách hàng. Hệ thống tự động tạo tin nhắn Zalo mẫu chuyên nghiệp được cá nhân hóa, copy vào Clipboard và chuyển tiếp khách hàng sang Zalo chat của Admin. Ẩn hoàn toàn 2 nút cũ "📞 Gọi ngay" và "💬 Tư vấn ngay căn này" ở Client View.
    - **Gom nhóm Admin Speed Dial FAB:** Thiết kế lại nhóm nút nổi góc phải dưới màn hình thành Speed Dial FAB hình bánh răng `⚙️` (không text, chỉ icon). Nút tự động chuyển đổi các nút con tương thích theo màn hình (Chọn tất cả/Lưu/Chia sẻ rổ hàng ở danh sách, Lưu thay đổi 💾/Gửi Zalo 🔗 ở chi tiết).
    - **Sửa lỗi Bỏ chọn tất cả:** Khắc phục lỗi bỏ chọn tất cả không xóa sạch giỏ hàng toàn cục (`SELECTED_IDS.clear()`) đối với các căn bị ẩn do filter tìm kiếm.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-01 (Nghiệm thu US-057 - Thanh tìm kiếm thông minh kết hợp nhiều điều kiện và phân tích địa chỉ - TEST PASS)
*   **Mã User Story:** `US-057` (Thanh tìm kiếm thông minh kết hợp nhiều điều kiện và phân tích địa chỉ (Multi-Condition Smart Search Engine with Address & Price Parser))
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Hệ thống hóa Parser thông minh:** Phân tách chuỗi truy vấn bằng dấu `+` để áp dụng logic AND, nhận diện khoảng giá `<số> tỷ` (prefix match) và `<số>.<số> tỷ` (exact match), bóc tách Số nhà + Tên đường bằng Regex và so khớp số nhà thông minh (hỗ trợ split `+` phức hợp, exact, sub-number, letter suffix).
    - **Chuẩn hóa tên đường đặc biệt:** Tích hợp bộ chuyển đổi tự động các biến thể đường phổ biến sang mã cơ sở dữ liệu đã chuẩn hóa (ví dụ: `cmt8`/`cách mạng tháng tám` -> `ttmc`, `3/2`/`ba tháng hai` -> `htb`, `đường số 7` -> `7sd`).
    - **Bypass Browser Autofill Prompt:** Giải quyết hoàn toàn lỗi Chrome/Edge liên tục gợi ý lưu mật khẩu/tài khoản thanh toán bằng cách đổi tên ID ô tìm kiếm thành `bdsSearchInput` và thay thế ô chứa Google Client ID nhạy cảm sang input văn bản thông thường kết hợp thuộc tính ẩn ký tự (`disc masking`).
    - **Tối ưu hóa hiệu năng (Debounce):** Thêm debounce 300ms giảm tần suất vẽ lại DOM liên tục trên mỗi keystroke, giải quyết triệt để tình trạng gõ chữ bị lag giật bất thường.
    - **Khắc phục Crash & Cải tiến độ chính xác:** Ép kiểu chuỗi `String()` chặt chẽ và wrap các DOM thống kê (chỉ có ở Admin) trong check an toàn để tránh unhandled TypeError gây đơ/đóng băng tìm kiếm phía Client. Loại bỏ việc fallback tìm kiếm trong bài mô tả dài tự do để tăng độ chính xác 100%, tránh kết quả rác.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-31 (Nghiệm thu US-056 - Cập nhật danh sách Phường chuẩn từ SQL vào bộ lọc tìm kiếm trên giao diện Web Vercel Admin cho các Quận trọng điểm - TEST PASS)
*   **Mã User Story:** `US-056` (Cập nhật danh sách Phường chuẩn từ SQL vào bộ lọc tìm kiếm trên giao diện Web Vercel Admin cho các Quận trọng điểm)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Tích hợp bản đồ Phường tĩnh STATIC_WARD_MAP:** Khai báo danh sách các phường thực tế từ SQL cho 5 quận trọng điểm (Quận 3, Quận 10, Tân Bình, Phú Nhuận, Bình Thạnh) trong giao diện web.
    - **Cập nhật buildWardTabs() bỏ sắp xếp tự động:** Hiển thị danh sách các phường chính xác theo đúng thứ tự thủ công được khai báo trong cấu hình thay vì sắp xếp bảng chữ cái ABC, giúp ưu tiên hiển thị phân khu trọng điểm lên đầu bộ lọc.
    - **Cơ chế Fallback thông minh:** Tự động fallback về bộ lọc động từ dữ liệu hiện hữu nếu người dùng chọn nhiều quận cùng lúc hoặc chọn quận ngoài danh sách map tĩnh.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-31 (Nghiệm thu US-055 - Khắc phục triệt để lỗi ảnh Sổ đỏ hiện làm ảnh đại diện trên danh sách Admin - TEST PASS)
*   **Mã User Story:** `US-055` (Khắc phục triệt để lỗi ảnh Sổ đỏ hiện làm ảnh đại diện trên danh sách Admin)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Khử triệt để hình Sổ đỏ khỏi Avatar/Cover danh sách Card:** Sửa lỗi trong hàm `isListingSodoUrl` và các bộ lọc cover của `index.html` để lọc bỏ tất cả hình ảnh sơ đồ thửa đất ra khỏi danh sách ảnh public hoặc ảnh bìa mặc định.
    - **Mở rộng hỗ trợ toàn diện cả 5 Sơ đồ thửa đất:** Hỗ trợ đầy đủ `Sơ đồ thửa đất 3`, `Sơ đồ thửa đất 4`, `Sơ đồ thửa đất 5` (các cột index 77, 78, 79 trên sheet Pool) trong mọi luồng check Sổ và hiển thị đầy đủ cả 5 ảnh Sổ này trong Carousel Sơ đồ thửa đất ở chi tiết Admin và các nhãn tím `🔒 Sổ 1` đến `🔒 Sổ 5` trong Image Curation Editor.
    - **Giải quyết mismatch giữa link thô Thiên Khôi và link di cư Cloudinary:** Cải tiến hàm `isListingSodoUrl` trên client để tự động chuẩn hóa URL, so sánh normalized của link thô Thiên Khôi và Cloudinary, đồng thời nhận diện mẫu URL Cloudinary chứa `/sodo1_` đến `/sodo5_` để gán nhãn sodo tự động.
    - **Chạy công cụ sửa lỗi data hàng loạt cho dữ liệu cũ:** Khởi chạy thành công `repair_diagrams.py --publish` rà soát toàn bộ SQLite, di cư tất cả sơ đồ thô cũ lên Cloudinary không nén và lưu đè link Cloudinary về các cột tương ứng trên Google Sheets Pool.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-31 (Nghiệm thu US-054 - Di cư ảnh Sổ không nén lên Cloudinary và lưu link về Pool sheet - TEST PASS)
*   **Mã User Story:** `US-054` (Di cư ảnh Sổ không nén lên Cloudinary và lưu link về Pool sheet)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Vá lỗi SQLite khóa tranh chấp:** Cập nhật tham số `timeout=30.0` vào toàn bộ các câu lệnh kết nối SQLite `sqlite3.connect(DB_FILE, timeout=30.0)` trong `repair_diagrams.py`, `curator_server.py`, và `crawl_pipeline.py`.
    - **Nâng cấp di cư sơ đồ siêu tốc song song:** Xây dựng script `repair_diagrams_fast.py` sử dụng `ThreadPoolExecutor` với 5 luồng song song xử lý di cư sơ đồ sang Cloudinary không nén trực tiếp vào SQLite local, tăng tốc độ xử lý lên **36 lần** (3.997 căn xử lý hoàn tất chỉ trong 77.2 phút!).
    - **Đồng bộ Sheets tối ưu hàng loạt (Bulk Sync):** Phát triển script `sync_to_sheets.py` tải toàn bộ Sheet về RAM và ghi đè hàng loạt qua tính năng `batch_update` cực kỳ hiệu quả, đồng bộ thành công **4.872 căn** lên Google Sheets chỉ mất đúng **23.57 giây** trong 1-2 API calls duy nhất mà không lo lỗi quota.
    - **Tích hợp 3 cột sơ đồ mới an toàn:** Bổ sung `Sơ đồ thửa đất 3, 4, 5` vào cuối danh sách cột Pool Sheet an toàn chống lệch chỉ số cột trên giao diện Web Admin.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-30 (Khắc phục lỗi tìm kiếm số nhà thô vượt giới hạn 200 căn Kho Pool - DONE)
*   **Mã Sự cố:** `BUGFIX-002` (Sửa lỗi tìm kiếm số nhà trong Kho Pool)
*   **Các thay đổi thực tế đã deploy:**
    - **Sửa logic nguồn render:** Thay thế việc sử dụng `sourceArr` (danh sách thô chưa lọc) thành `getFiltered()` (danh sách đã qua bộ lọc tìm kiếm) làm dữ liệu nguồn đầu vào cho hàm `render()`. Nhờ đó, tất cả các căn nhà khớp tìm kiếm (ví dụ `210.18`) đều được vẽ đầy đủ thẻ DOM, giải quyết triệt để việc mất thẻ khi nằm ngoài 200 căn đầu tiên.
    - **Tích hợp Recursion Guard cho `applyFilter()`:** Bổ sung cờ bảo vệ đệ quy `inApplyFilter` trong hàm `applyFilter()` để khi người dùng gõ tìm kiếm, trình duyệt tự động vẽ lại DOM theo danh sách khớp một cách mượt mà và an toàn.

### 2026-05-30 (Nghiệm thu US-046 - Phân loại hình ảnh sổ pháp lý và hình mặt tiền riêng biệt - TEST PASS)
*   **Mã User Story:** `US-046` (Phân loại hình ảnh sổ pháp lý và hình mặt tiền riêng biệt)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Tích hợp cọ vẽ/nhãn `🔒 Sổ`:** Thêm nút cọ vẽ `🔒 Sổ` (ID: `toolSodoBtn`) màu Tím `#8e44ad` trong thanh công cụ Image Editor của modal curation (Khắc phục triệt để lỗi trùng lặp hình ảnh Google Drive khác định dạng URL bằng cơ chế so khớp ID chuẩn hóa).
    - **Hiển thị nhãn Sổ & Tự động tắt công khai:** Click gán Sổ ➔ Nhận viền tím, badge `🔒 Sổ 1` / `🔒 Sổ 2` (tối đa 2 hình, tự động xoay tua) và tự động tắt checkbox công khai (public) để bảo mật thông tin nhạy cảm của thửa đất.
    - **Chặn gán nhãn Mặt Tiền/Nền cho Sổ:** Sửa triệt để lỗi khi URL của ảnh Sổ trùng với ảnh bìa/mặt tiền gốc (Ví dụ: căn 175.51 Nguyễn Thiện Thuật). Chặn tuyệt đối việc gán nhãn Mặt Tiền (`isMatTien`) và Nền (`isAnhNen`) cho thẻ Sổ (`type === 'sodo'`) để đảm bảo ảnh Sổ luôn hiển thị độc lập, riêng tư, và không bao giờ bị highlight nhầm làm ảnh công khai đại diện.
    - **Đồng bộ cơ sở dữ liệu & Google Sheets API:** Khi click Lưu hoặc Lên sóng ➔ Đồng bộ ghi đè 2 URL ảnh Sổ vào cột **AB (Sơ đồ thửa đất 1)** và **AC (Sơ đồ thửa đất 2)** trên tab Pool của Google Sheets qua request PUT lên `Pool!AB{row}:AC{row}`.
    - **Tự động tải lại trang & Mở rộng Preview:** Bổ sung cơ chế `localStorage` khi click Lưu hoặc Lên sóng ➔ Tự động gọi `window.location.reload()` để nạp lại dữ liệu Google Sheets mới nhất sạch sẽ, sau đó tự động mở modal `openS`, tự động collapse mục Biên tập và tự động expand mục **PREVIEW KHÁCH HÀNG**, đồng thời smooth-scroll thẳng đến vị trí preview để Admin dễ dàng kiểm tra diện mạo cuối cùng của khách hàng! Bảo toàn 100% hộp thoại gợi ý Zalo thông minh sau reload.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-30 (Nghiệm thu US-051 - Tích hợp Combobox Tình trạng và Loại bỏ trường Rộng hẻm thừa tại giao diện Biên tập Admin - TEST PASS)
*   **Mã User Story:** `US-051` (Tích hợp Combobox Tình trạng và Loại bỏ trường Rộng hẻm thừa tại giao diện Biên tập Admin)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Loại bỏ UI trường nhập Rộng hẻm:** Xóa bỏ hoàn toàn trường nhập độ rộng hẻm `#editRongHem` khỏi giao diện biên tập Admin/Curation Modal.
    - **Tích hợp combobox Tình trạng:** Thay thế vị trí trống bằng hộp chọn `#editTinhTrang` gồm 5 tùy chọn: `Bình thường`, `Mới`, `Nát`, `Đã bán`, `Ẩn`.
    - **Khởi tạo dữ liệu mặc định:** Khi mở modal, dropdown tự động load tình trạng hiện tại từ `p.tinh_trang` hoặc mặc định là `Bình thường`.
    - **Tự động hóa giá trị Rộng hẻm và Tình trạng:**
        - Khi lưu thay đổi của căn đã duyệt (`saveSourceChanges`): Trường `rong_hem` tự động lấy từ giá trị cào `raw_duong_truoc_nha` hoặc `duong_truoc_nha` và lưu xuống cột O (index 14). Trạng thái chọn từ combobox được lưu xuống cột P (index 15) và đồng bộ Client-side.
        - Khi đăng căn thô mới từ Pool (`saveNewListingFromPool`): Trường `rong_hem` thừa hưởng từ cột `matchedRow[59]` và trạng thái được ghi chính xác xuống cột P (`tinh_trang_nha`) của Source Sheet.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-30 (Nghiệm thu US-050 - Hỗ trợ lướt xem ảnh tiếp theo và thanh xem trước ảnh nhỏ khi phóng to hình - TEST PASS)
*   **Mã User Story:** `US-050` (Hỗ trợ lướt xem ảnh tiếp theo và thanh xem trước ảnh nhỏ khi phóng to hình)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Đồng bộ hóa Lightbox cao cấp (`lbOverlay`):** Loại bỏ hoàn toàn cơ chế đơn lẻ `openZoomOverlay` của `setupScrollCarousel` (dùng ở cả Curation Modal của Admin và Client Detail View của khách). Thay thế bằng hàm tích hợp `window.openLightboxForCarousel(imageUrls, index)` để mở bộ Lightbox cao cấp.
    - **Điều hướng hình ảnh & Thao tác ngầm:** 
        - Hỗ trợ đầy đủ phím mũi tên Trái/Phải để chuyển ảnh kế tiếp, và phím `Escape` để đóng nhanh lightbox trên máy tính qua bộ lắng nghe `keydown` toàn cục.
        - Giữ vững thao tác vuốt (swipe) tự nhiên trên các thiết bị di động.
    - **Thanh hình ảnh thu nhỏ nằm ngang (Horizontal Thumbnails Strip):** Tải mượt danh sách ảnh nhỏ ở chân lightbox, tự động highlight viền vàng gold cho ảnh đang mở và cuộn mượt ảnh nhỏ đó vào giữa tầm nhìn.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-30 (Nghiệm thu US-049 - Đồng nhất giao diện chi tiết Khách hàng với Admin Preview và bổ sung Sao chép nhanh link gửi khách - TEST PASS)
*   **Mã User Story:** `US-049` (Đồng nhất giao diện chi tiết Khách hàng với Admin Preview và bổ sung Sao chép nhanh link gửi khách)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Đồng nhất giao diện Khách hàng với Admin Preview:** Đồng bộ hóa 100% bố cục chi tiết của khách hàng khi mở liên kết sạch `?s=SYS-XXXX` giống hệt giao diện Preview của Admin (sử dụng lưới Grid 8 trường SPEC thô và khung mô tả xám bo góc chuẩn).
    - **Nút Copy link nhanh tinh gọn (Căn phải):** Bổ sung nút bấm `Copy link nhanh` phẳng, không viền, không icon và căn lề phải cực kỳ gọn gàng nằm ngay đầu modal curation trên Admin panel, tối ưu hóa không gian làm việc tối đa.
    - **Session Admin persistent & Silent Auto-Login ngầm:**
        - Tích hợp cờ `isAdminSession = 'true'` vào `localStorage` thiết bị khi đăng nhập bằng mật khẩu hoặc Google thành công.
        - Tự động gọi Silent Login khi khởi động nếu phát hiện thiết bị Admin nhưng token hết hạn, giúp tải mượt dữ liệu bảo mật và tự động bung modal curation thô (`openPoolS`) của căn nhà tương ứng trong chưa đầy 2 giây mà không cần tương tác thủ công.
        - Khách hàng thường mở link căn thô hoàn toàn bị chặn an toàn và không thấy nút Google Login.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-01 (Nghiệm thu US-058 - Quét, xoay ảnh thẳng đứng vật lý và tự động dọn dẹp bộ nhớ ảnh lỗi cũ trên Cloudinary cho rổ hàng đã di cư - TEST PASS)
*   **Mã User Story:** `US-058` (Quét, xoay ảnh thẳng đứng vật lý và tự động dọn dẹp bộ nhớ ảnh lỗi cũ trên Cloudinary cho rổ hàng đã di cư)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Signed Destroy API Integration**: Tích hợp gọi API Signed Destroy của Cloudinary (`/image/destroy`) sử dụng chữ ký bảo mật SHA-1. Tự động trích xuất `public_id` và xóa sạch ảnh rác cũ trước khi tải ảnh mới lên để tránh tràn bộ nhớ.
    - **Two-Phase Sweep Architecture**: Thiết kế quy trình 2 pha: Pha 1 quét đa luồng EXIF song song 15 luồng, tự động cào lại Thiên Khôi bằng cookie mới nếu thiếu ảnh gốc. Pha 2 download ảnh từ CDN công khai `tk-assets.spms2.com`, xoay đứng vật lý (`ImageOps.exif_transpose`), nén tối ưu 40-80%, và đẩy lên Cloudinary + đồng bộ Sheets Pool.
    - **Retroactive Clean-up Script**: Viết và chạy thành công script [cleanup_previous_listings.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/cleanup_previous_listings.py) dọn sạch 31 ảnh rác của 5 căn test cũ.
    - **Production Execution**: Hoàn thành quét và sửa lỗi xoay ảnh thành công cho **893 / 893 căn** bị ảnh hưởng trong tổng số 5.714 căn published, đồng bộ chép đè chuẩn xác lên Sheets Pool (dòng 10 đến 5.719).
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-01 (Nghiệm thu US-057 - Thanh tìm kiếm thông minh kết hợp nhiều điều kiện và phân tích địa chỉ - TEST PASS)
*   **Mã User Story:** `US-057` (Thanh tìm kiếm thông minh kết hợp nhiều điều kiện và phân tích địa chỉ)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Smart Search Input & Debounce**: Tích hợp debounce 300ms giảm tải real-time, đổi tên ID sang `bdsSearchInput` kết hợp Disc Masking trên Google Client ID để bypass trình duyệt lưu mật khẩu.
    - **Address & Price Parser**: Hỗ trợ tìm kiếm thông minh, nhận diện số nhà có dấu chấm `.` (ví dụ `95.`), giới hạn fallback text không quét mô tả tự do rộng để đạt độ chính xác 100%.
    - **DOM Crash Fixes**: Wrap các thống kê DOM trong check an toàn để chặn hoàn toàn crash client-side khi kết quả lọc rỗng.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-30 (Hoàn thành US-048 - Khắc phục lỗi lệch chỉ số cột Pool thô và trùng lặp card rỗng trên giao diện Admin - DONE)
*   **Mã User Story:** `US-048` (Khắc phục lỗi lệch chỉ số cột Pool thô và trùng lặp card rỗng trên giao diện Admin)
*   **Các thay đổi thực tế đã deploy:**
    - **Khắc phục lỗi hiển thị card rỗng trùng lặp (Empty Card Duplicate Fix):** Thay thế cơ chế gán `id = row[55] || row[54] || ''` thành `id: row[55] || row[54] || systemId || ''` in `getMappedPoolData()` và `openPoolS()` để tự động fallback về `systemId` độc nhất nếu Mã Khang Ngô trống. Điều này chặn đứng hoàn toàn việc sinh hàng loạt card thô có `data-pid=""` trong DOM, ngăn chặn việc hiển thị sai lệch các card không liên quan khi lọc.
    - **Sửa chữa triệt để lệch chỉ số cột (Column Shift Bug):** Khắc phục lỗi lệch cột bằng cách đồng bộ chuẩn xác 100% các index mapping của `row[...]` theo đúng schema `POOL_HEADERS` 79 cột đối với các trường: `duong_truoc_nha` (index 59), `rong_hem` (index 60), `tinh_trang` (index 61), `so_pn` (index 64), `danh_gia` (index 67), `ngu_tang_tret` (index 68), `chdv` (index 69), `raw_duong_truoc_nha` (index 59), `raw_do_rong_hem` (index 60).

### 2026-05-30 (Nghiệm thu US-047 - Nâng cấp độ tin cậy và cào chuẩn xác mô tả chi tiết của API Cào lại căn nhà - TEST PASS)
*   **Mã User Story:** `US-047` (Nâng cấp độ tin cậy và chống lỗi gọi API Cào lại căn nhà)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Khắc phục lỗi KeyError & Bọc an toàn server**:
        - Sửa KeyError trên khóa có dấu `Link_Gốc` thành lookup dictionary an toàn `d_row.get("Link_Goc") or d_row.get("Link_Gốc")` để khớp với cột không dấu thực tế trong SQLite.
        - Bọc toàn bộ khối logic cào lại của route Flask trong `try...except` để đảm bảo luôn phản hồi JSON khi xảy ra lỗi.
    - **Lá chắn Đăng nhập & Chuyển hướng bảo mật**: Tự động phát hiện khi yêu cầu cào lại bị Thiên Khôi chuyển hướng sang trang đăng nhập (`Account/Login`) hoặc bị chặn (`security.html`), lập tức chặn ghi đè SQLite trống và trả về mã lỗi HTTP `401 Unauthorized` kèm chỉ dẫn bằng tiếng Việt.
    - **Lá chắn Bảo vệ Dữ liệu rỗng**: Nếu thông tin bóc tách chi tiết trả về trống rỗng (không tìm thấy `#Detail_sNoiDung` và `#Detail_sDiaChi`), hủy ghi đè database SQLite.
    - **Khắc phục lỗi trích xuất sai liên kết mô tả dài**: Sửa hàm `get_val_by_label()` trong `crawl_pipeline.py` để loại trừ các trường văn bản mô tả/nội dung dài khỏi cơ chế trích xuất thẻ liên kết nhanh `find('a')`. Điều này bảo toàn 100% nội dung chữ dài kèm liên kết Zalo/Facebook được chèn ở cuối (ví dụ như căn Phan Tây Hồ 8.66 tỷ).
    - **Cải tiến bắt lỗi thông minh Frontend**: Cập nhật hàm `recrawlActiveListing()` trong `curator.html` kiểm tra `res.ok` trước khi gọi `res.json()`, loại bỏ hoàn toàn lỗi crash cú pháp `Unexpected token '<'`.
    - **Biên dịch File chạy độc nhất**: Safely force-killed các tiến trình ngầm cũ bị khóa và đóng gói lại thành công file chạy độc nhất `dist\KhangNgoCuratorApp.exe`.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-30 (Nghiệm thu US-044 - Nâng cấp tính năng tự động biên tập AI và Tích hợp Đẩy hàng loạt chọn lọc nâng cao - TEST PASS)
*   **Mã User Story:** `US-044` (Nâng cấp tính năng tự động biên tập AI và Tích hợp Đẩy hàng loạt chọn lọc nâng cao)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Khắc phục lỗi trống trường AI Curation (CR-001)**: 
        - Tránh chuỗi rỗng đè mất System Prompt khi người dùng cấu hình trống trong `curator_config.json` bằng cách tự động phục hồi về prompt gốc từ `DEFAULT_CONFIG`.
        - Kháng lỗi `NoneType` hoàn toàn bằng cách áp dụng helper `safe_str()` cho tất cả các giá trị NULL lấy từ SQLite.
        - Khử hoàn toàn cuộc gọi API OpenAI bị trùng lặp đồng thời (race condition) trên frontend bằng cơ chế Debounce độc nhất (`window.autoAiTimeoutId`) tại `renderEditor()`.
    - **Nâng cấp Luật Prompt AI (Bản cập nhật của Mr. Khang)**: Tích hợp luật "🚨 BẮT BUỘC KHÔNG BỊA ĐẶT THÔNG SỐ VẬT LÝ" (độ rộng hẻm, nội thất, dòng tiền, nở hậu, pháp lý) và đặc tả cấu trúc mô tả Public có Banner Catchy IN HOA TOÀN BỘ giật tít chuyên nghiệp, dịch miền Nam "Trệt, lầu đúc kiên cố".
    - **Tích hợp Đẩy hàng loạt có chọn lọc nâng cao**:
        - Giao diện Sidebar hỗ trợ bộ 3 ô nhập lọc inline cực kỳ tinh tế cho **Quận, Đường, Số nhà** (lọc tức thời `oninput="fetchListings()"`).
        - Giao diện checkbox an toàn ở card tin và thanh thao tác nhanh sidebar với nút **⚡ ĐẨY POOL (N)** bulk publishing.
        - API `/api/listings/bulk-publish` đẩy tuần tự hàng loạt các căn đã chọn lên Google Sheets Pool với throttling `0.5s` bảo vệ quota của Google Sheet.
        - Hiệu ứng loading chờ tải (**Premium Glassmorphic Search Loader**) hình vòng xoay vàng gold tuyệt đẹp trong ô tìm kiếm.
     - Được nghiệm thu trực tiếp ("test pass") bởi Product Owner (Khang Ngô).

### 2026-06-04 (Nghiệm thu US-071 - Khắc phục lỗi lệch cột lưu tiêu đề public và hiển thị trùng lặp giá tiền ở panel preview - TEST PASS)
*   **Mã User Story:** `US-071` (Khắc phục lỗi lệch cột lưu tiêu đề public và hiển thị trùng lặp giá tiền ở panel preview)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Sửa lỗi hiển thị & lưu Tiêu đề public trong Admin Editor**: Load tiêu đề trong Editor từ cột E (`tieu_de` - index 4) và fallback về cột AN (`Tiêu đề BDS` - index 39). Khi bấm "Lưu thay đổi", tiêu đề chỉnh sửa được lưu chính xác vào cột E (`tieu_de`), cập nhật `p.t` ở client-side, và dọn trống cột AN.
    - **Sửa lệch cột khi đồng bộ từ Pool**: Căn chỉnh toàn bộ lệch chỉ số cột Pool từ index 54 trở đi (tăng lên 1 đơn vị) trong `executePullFromPool` và `saveNewListingFromPool` để ghi đúng ID, tiêu đề, mô tả, số phòng ngủ/vệ sinh, phường cũ, phân loại hẻm và độ rộng hẻm sang Source. Reset cột AN (`Tiêu đề BDS`) về rỗng mặc định.
    - **Loại bỏ lặp giá tiền**: Loại bỏ hoàn toàn logic tự động chèn thêm giá tiền (`p.gia + ' tỷ'`) trong hiển thị Card khách hàng và Live Preview. Tiêu đề hiển thị chuẩn xác lấy thuần túy từ cột E.
    - **Kịch bản di trú dữ liệu**: Tạo và chạy thành công kịch bản di trú một lần `scratch/migrate_tieu_de.py --write` sửa thành công 29 căn bị lưu lệch cột tiêu đề public cũ sang đúng cột E (`tieu_de`) và làm trống cột AN (`Tiêu đề BDS`) trên Google Sheet Source.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-06-04 (Sửa trùng lặp System ID, gộp dòng, đồng bộ Mã Khang Ngô bằng System ID & Nghiệm thu US-070 - TEST PASS)
*   **Mã User Story:** `US-070` (Sửa trùng lặp System ID trên Sheets và khôi phục SQLite hợp nhất từ hai sheet)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Duplicate System ID Repair**: Phát hiện và sửa lỗi 170 dòng trùng lặp `System ID` trên sheet Pool.
    - **Dual-Sheet SQLite Restore**: Nâng cấp script `restore_db_from_sheets.py` để kết hợp an toàn dữ liệu thô từ Pool và dữ liệu curated từ Source theo `System ID`, khôi phục 5727 dòng dữ liệu vào SQLite.
    - **Address-Based ID Sync & Deduplication**: Đồng bộ chép đè Mã Khang Ngô và gộp các dòng thủ công thừa trên sheet Pool bằng thuật toán so khớp địa chỉ chuẩn hóa (dọn sạch dòng trùng lặp của Cô Bắc, Trần Huy Liệu, Vạn Kiếp).
    - **System ID URL Encoding**: Thay đổi cơ chế tạo link gửi khách từ Bitmask index không ổn định sang mã hóa trực tiếp danh sách `System ID` dạng Base64URL safe (cập nhật `index.html`), giải quyết triệt để lỗi lệch căn hiển thị cho khách.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-29 (Hoàn thành luồng thô cào di cư và đẩy Pool không qua AI & Nghiệm thu US-040 - TEST PASS)
*   **Mã User Story:** `US-040` (Tự động hóa Luồng Curation đẩy Pool)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Tối giản hóa luồng ngầm (Pure Raw Data Pipeline)**: Loại bỏ hoàn toàn cuộc gọi OpenAI API đắt đỏ và chậm chạp ở backend khi cào và di cư hình ảnh chạy ngầm. Không tự động sinh tiêu đề, mô tả public và mã Khang Ngô tại server backend (thiết lập trống hoàn toàn `""`).
    - **Tự động di cư và phân loại ảnh theo cấu trúc (Diagram-Aware Routing)**: 
        - Ảnh sơ đồ thửa đất gốc (bóc tách chính xác từ `#lightgalleryTD li`) sau khi di cư được map trực tiếp vào cột `Sơ đồ thửa đất 1` và `Sơ đồ thửa đất 2` của SQLite và Sheets Pool. Bỏ qua nén chất lượng để giữ nguyên chi tiết.
        - Ảnh sản phẩm/nội thất (bóc tách từ `#lightgalleryND li`) sau khi di cư được lưu tuần tự vào cột `Ảnh 1` đến `Ảnh 15`.
        - Không gán bừa bãi ảnh nhà vào cột sơ đồ thửa đất, không tự biên tập/curate hình ảnh ở backend.
    - **Đẩy thẳng Google Sheets Pool**: Luồng ngầm tự động đẩy dòng dữ liệu 79 cột phẳng hoàn toàn thô lên tab **Pool** của Google Sheets thừa hưởng định dạng Table ngay khi quá trình di cư ảnh hoàn tất (SQLite status chuyển thành `published`).
    - **Được nghiệm thu trực tiếp ("test pass")** bởi PO Trang (System Designer).

### 2026-05-28 (Nghiệm thu toàn diện US-039 - Admin Curation Dashboard song song Pool & Source - TEST PASS)
*   **Mã User Story:** `US-039` (Admin Curation Dashboard trên Web Vercel)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **Dual-Sheet Integration (Gộp song song)**: Đọc song song tab Pool (Read-Only) và Source (Writeable) rồi ghép nối theo `System ID` / `id`.
    - **Advanced Curation Stack (Nút stack chi tiết thô phẳng hóa)**: Loại bỏ Accordion 1, phẳng hóa toàn bộ specs, carousels, maps. Sắp xếp các phím tròn (Lưu, Zalo) di động nổi ở góc phải modal thay vì Header.
    - **Tìm kiếm thô nâng cao**: Đồng bộ ô `#searchInput` bên ngoài quét qua Tên đầu chủ, SĐT đầu chủ, tin thô của Pool.
    - **Image Curation Grid (Biên tập ảnh trực quan)**: Grid 15 ảnh thô mở rộng lên `460px` (đạt 6 ảnh cùng lúc) kèm nút sao `Nền` (Cover) và checkbox `Hiện` (Public) ghi ngược an toàn về sheet.
    - **Đồng bộ màu sắc & SVG Premium**: Đồng nhất màu nền tất cả phím tròn (Chọn tất cả, Bộ sưu tập, Chia sẻ ở trang danh sách; Lưu thô, Lưu curated, Zalo ở chi tiết) thành màu **Vàng Gold `#f39c12`**, phối với **icon SVG đen tuyền `#1c1c1e`** độ tương phản cao sắc nét 100% trên mọi nền di động.
    - **Auto-Fill & Live Preview**: Nút bấm tự điền tiêu đề/mô tả tự động và cập nhật Live Preview trực quan theo thời gian thực trước khi lưu.
    - **Đăng nhập & Khôi phục Admin Mode**: Tích hợp cổng đăng nhập bảo mật `🔒 Đăng nhập Admin` ở chân trang lỗi khách và hỗ trợ dynamic session reload.
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-28 (Giải quyết lỗi chèn dòng Table Google Sheets không thừa hưởng định dạng & Nghiệm thu US-037, US-038 - TEST PASS)
*   **Mã User Story:** `US-037` (Tích hợp AI Tools, Cấu hình System Prompt) và `US-038` (Đồng bộ đa thiết bị qua Cloud Junction)
*   **Các thay đổi thực tế đã deploy & nghiệm thu:**
    - **US-037 (Sửa lỗi chèn dòng Table)**: Tích hợp helper `get_table_end_row_index` truy vấn API Google Sheets tìm `endRowIndex` của Table chính thức trên tab **Pool**. Chèn dòng mới trực tiếp tại đúng vị trí dòng cuối cùng của Table để kích hoạt cơ chế tự động co giãn của Google Sheets. Nhờ đó, dòng mới chèn thuộc về Table và thừa hưởng 100% định dạng, màu xen kẽ zebra, viền bảng, checkbox và công thức ảnh bìa `=IMAGE()`.
    - **US-038 (Đồng bộ đa thiết bị qua Cloud Junction)**: Thiết lập thành công mô hình ảo hóa NTFS Junction Link liên kết thư mục code `D:\LHTBrain` cục bộ và bộ não AI `antigravity-ide` thông qua Google Drive Desktop. Lịch sử chat được hợp nhất và đồng bộ tự động 2 chiều thời gian thực giữa 2 máy.
    - **Dọn dẹp Sheet**: Dọn dẹp sạch sẽ các dòng dữ liệu test giả lập trên Sheet Pool.
    - **Biên dịch & Đóng gói**: Đóng gói lại tệp tin chạy đơn độc lập `KhangNgoCuratorApp.exe` chạy trơn tru trên môi trường Python 3.14.5 của anh Khang (monkeypatch PyInstaller thành công).
    - **Được nghiệm thu trực tiếp ("test pass")** bởi Product Owner (Khang Ngô).

### 2026-05-27 (Giải quyết lỗi chặn phân trang, Cảnh báo Cookie kép & Nghiệm thu US-035 - TEST PASS)
*   **Giải quyết triệt để lỗi chặn phân trang Deep-Paging:** Vượt qua rào cản Thiên Khôi khóa cứng GET request sâu (Redirect về Page 1) bằng cách dynamic rewrite in-flight sang AJAX endpoint `/Hang/Partial_Item?...&Page=[index]`. Đảm bảo cào sâu tuần tự (trang 1, 2, 3... 241, 244) hoàn hảo.
*   **Hệ thống cảnh báo kép hết hạn Cookie:** Tích hợp winsound phát âm báo bíp vật lý ở Backend và Web Audio API (Oscillator Node) phát âm bíp kép kèm toast đỏ nổi ở Dashboard Frontend khi phát hiện Cookie Thiên Khôi hết hạn.
*   **Tối ưu tốc độ cào:** Rút ngắn Page Delay ngẫu nhiên xuống ~30 giây giúp tăng tốc cào tin lên gấp 8 lần nhưng vẫn siêu tàng hình (Ultra-Stealth).
*   **Nghiệm thu toàn diện (TEST PASS):** Chạy thử cào sâu thực tế, đồng bộ rổ hàng SQLite cục bộ, chuẩn hóa 79 cột nghiệp vụ và xuất bản trực tiếp lên Google Sheets Pool chính thức hoàn tất.
*   **Sửa lỗi luồng cào ngầm chạy vô hạn khi hết hạn Cookie:** Khắc phục lỗi tiến trình cào không dừng sau khi cookie hết hạn (bắt nhầm `RuntimeError` do `sys.exit` ném ra trong khối `except Exception` của trang). Thiết lập bộ lọc ngoại lệ `except RuntimeError as re_err: raise re_err` giúp ngắt luồng cào ngầm ngay lập tức, giải phóng bộ nhớ RAM và ngăn chặn việc tiếp tục gửi request lỗi.
*   **Tự động mở Modal Cập nhật Cookie thông minh:** Bổ sung tính năng tự động bung cửa sổ Modal dán Cookie mới và tự động focus con trỏ vào ô Textarea khi luồng cào phát hiện hết hạn Cookie. Giúp người dùng thực hiện 1-click dán mới siêu tốc mà không cần thao tác click mở thủ công.
*   **Hỗ trợ Cào không giới hạn (Unlimited Crawl Mode):** Nâng cấp ô nhập "GIỚI HẠN CĂN" trong giao diện Curation Panel cho phép để trống hoặc điền 0 để cào không giới hạn. Tự động mở rộng dải phân trang tối đa lên **1000 trang** (thay vì 20 trang giới hạn cứng như trước), cào tiến tới liên tục cho đến khi rổ hàng đối tác kết thúc hoặc Cookie hết hạn.
*   **Tự động Kiểm tra & Chép đè Ảnh thông minh khi xuất bản Google Sheets (Duplicate Check & Overwrite Mode):** Khi bấm **"LƯU LÊN SHEET"**, hệ thống sẽ tự động quét cột A (`Mã Hàng`) trên Google Sheets xem mã `TK-[tk_id]` đã tồn tại chưa. Nếu có, hệ thống sẽ xác định chính xác dòng cũ (`row_index`), đọc dòng đó về và chỉ chép đè duy nhất các cột liên quan đến hình ảnh và cột `Last Crawl` thời gian cào mới nhất, giữ nguyên vẹn 100% tất cả các cột text nghiệp vụ khác anh đã sửa đổi trực tiếp trên Sheet.
*   **Đồng bộ Thời Gian Thực "Trang Bắt Đầu" trên Web UI (Real-time UI Start Page Sync):** Sửa lỗi đường dẫn ghi start page trong `crawl_pipeline.py` từ tệp nhầm `config.json` về tệp chuẩn `curator_config.json`. Giờ đây, mỗi khi cào xong 1 trang danh sách, hệ thống tự động ghi nhận trang tiếp theo và giao diện Web UI Curator của anh sẽ **tự động cập nhật tăng chỉ số "Trang Bắt Đầu" theo thời gian thực**.

### 2026-05-26 (Hệ thống cào BĐS & Mini-App biên tập rổ hàng 2000 căn độc lập - US-035)
*   **Cào trực tiếp chiều dài thực tế (Chieu_dai):** Thực hiện cào trực tiếp chiều dài từ input `#Detail_iDai_show` / `#Detail_iDai` trên Thiên Khôi và lưu vào cột SQLite `Chieu_dai`. Bỏ hoàn toàn cơ chế tính toán chiều dài tự động nếu cào về rỗng để giữ dữ liệu nguyên bản sạch nhất.
*   **Xóa vĩnh viễn thông tin chủ nhà (Nhóm 4):** PURGE triệt để Nhóm thông tin chủ nhà ra khỏi giao diện Biên tập và dọn dẹp các innerText handlers trong Javascript để bảo mật thông tin và tránh crash JS.
*   **Luồng xử lý ảnh nghiệp vụ nâng cao (Nền Swap, Nội thất, Hẻm sequence):**
    - Mặc định ảnh di cư được set nhãn `"Ẩn"` và điền tuần tự vào `Ảnh 1` - `Ảnh 15` của SQLite.
    - Đổi tên nhãn "Bìa" thành **Nền**. Khi click chọn **Nền**, ảnh được tự động swap vị trí lên `Ảnh 1` (index 0), ảnh cũ ở `Ảnh 1` tự hoán đổi về vị trí click ban đầu.
    - Ảnh chọn làm `"N.Thất"` được tự động tính index 1-based dạng `1,3,5` trong chuỗi 15 ảnh và lưu vào cột nghiệp vụ `Ảnh Public (VD: 1,3,5)`.
    - Ảnh chọn làm `"Hẻm"` được tự động điền tuần tự vào `Hình Hẻm 1` - `Hình Hẻm 10` và tính index 1-based dạng `1,2` lưu vào cột nghiệp vụ `Ảnh Hẻm Public (VD: 1,2)`.
*   **Cập nhật SQLite PUT API:** Tích hợp đồng bộ hai cột chỉ số ảnh public (`Anh_Public_VD_1_3_5` và `Anh_Hem_Public_VD_1_2`) vào API Flask `/api/listings/<tk_id>` method `PUT` để lưu vĩnh viễn và xuất bản đồng bộ lên Google Sheets.
*   **Tái cấu trúc cào dạng Thread-based:** Chuyển đổi cơ chế gọi cào tin từ Subprocess thành chạy trực tiếp trong luồng ngầm (Thread) cùng tiến trình Flask. Chuyển hướng log `sys.stdout` động và ghi đè bảo vệ sập app `sys.exit()`. Giúp phần mềm chạy độc lập hoàn toàn trên máy tính không cài sẵn môi trường Python.
*   **Monkeypatch giải quyết Bug dis.py của Windows Python 3.10.0:** Thiết lập đoạn code Python ghi đè hàm `dis._get_const_info` trong RAM để xử lý ngoại lệ IndexError. Bứt phá rào cản lỗi disassembler nổi tiếng của Python 3.10.0 khi phân tích bytecode của các gói mới như `cryptography`, giúp PyInstaller biên dịch thành công 100%.
*   **Đóng gói Ứng dụng chạy trực tiếp Standalone (Portable App):** Đóng gói toàn bộ code, Flask, giao diện `curator.html`, `thienkhoi_cookie.txt` thành thư mục độc lập chạy ngay tại `dist/KhangNgoCurator/` với file thực thi chính **`KhangNgoCurator.exe`**. Có thể nén ZIP gửi đi mọi máy tính khác để chạy trực tiếp không cần cài đặt.
*   **Tạo kịch bản bộ cài đặt Inno Setup:** Cung cấp sẵn file kịch bản [installer_script.iss](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/installer_script.iss) giúp tạo Setup Wizard chuyên nghiệp với 1 click.
*   **V5 Scrubber & Copy Fallback UI:** Tích hợp bộ dọn dẹp chống trùng lặp hẻm/xe hơi trên tiêu đề public và giao diện copy mảng 79 cột tab-separated nếu chưa cấu hình `credentials.json`.

### 2026-05-24 (Tối ưu hóa tìm kiếm, Sắp xếp mặc định, Triển khai Vercel & Ảnh đại diện Admin US-023, US-024, US-026, US-027)
*   **Xóa bộ lọc & Ô tìm kiếm (US-023):** Tự động xóa sạch ký tự ở ô tìm kiếm khi click nút "↺ Xóa lọc". Đồng thời tích hợp nút xóa nhanh `✕` ngay trong ô tìm kiếm.
*   **Ảnh đại diện Admin mặt tiền (US-024) [SỬA LỖI HIỂN THỊ]:** Revert phương pháp truy vấn trực tiếp file private Master (do bị trình duyệt chặn Cookie bên thứ ba khi gửi cross-origin). Thay vào đó, truy vấn tab `"Source"` của file Public (`1klR5...`) chỉ lấy duy nhất 2 cột: Cột A (`id`) và Cột B (`Hình Mặt Tiền`) thông qua câu truy vấn SQL `select A, B`. Yêu cầu admin tạo tab tên `"Source"` trên spreadsheet Public và dùng `IMPORTRANGE` kéo duy nhất 2 cột ID (Source!D:D) và Hình Mặt Tiền (Source!AM:AM) từ file private Master. Việc này vừa bảo mật tuyệt đối thông tin nhạy cảm của rổ hàng, vừa bypass hoàn toàn cơ chế chặn cookie của trình duyệt.
*   **Triển khai Vercel Serverless (US-027):** Cấu hình `vercel.json`, `package.json`, và xây dựng Node.js Serverless Function tại `api/index.js` cào dữ liệu Google Sheet và tiêm động thẻ `<meta og:image>` / `<meta og:title>` cho link chia sẻ 1 căn (`?s=SYS-XXXX`), giải quyết triệt để lỗi Zalo Preview hiển thị ảnh cũ/logo.
*   **Sắp xếp mặc định "Mới nhất lên trước" (US-028):** Thay đổi logic sắp xếp mặc định của cả trang Admin và trang Khách: các sản phẩm mới thêm (dòng dưới cùng trong Sheet, ID lớn nhất) sẽ được đẩy lên trên cùng của danh sách.
*   **Dual Sorting UI (US-028):** Tách biệt nút Sắp xếp cũ thành 2 nút Sắp xếp theo Thời gian (`⏱️`) và Sắp xếp theo Giá (`💰`) đặt cạnh nhau. Trực quan hóa trạng thái active (nền trắng chữ đỏ) và hướng sắp xếp (`⬇`/`⬆`) cực kỳ premium. Đồng bộ trạng thái vào `localStorage` của Admin.

### 2026-05-18 (Data Ingestion Pipeline Elastic Architecture & Extension V18.2)
*   **Selective Update (Cập nhật có chọn lọc):** Thêm tính năng "CẬP NHẬT LẠI (ĐÃ CÓ)" trên Extension. Cho phép cào lại dữ liệu mới nhất (Giá, Sơ đồ...) nhưng bảo tồn các dữ liệu viết tay của Admin (Tiêu đề, Mô tả, Đánh giá, Lựa chọn ảnh).
*   **Bypass Google Sheets Quirk (Fallback Siêu hạng):** Khắc phục triệt để lỗi `Service error: Spreadsheets` khi hàm `setValues` chạm mặt công thức `=IMAGE` hoặc các ký tự đặc biệt (`=, +, -`). Sử dụng kiến trúc "Cell-by-cell Fallback" kết hợp `setFormula` tách rời để đảm bảo update 100% thành công.
*   **Tự động mở rộng Google Sheets (Elastic Columns):** Script tự động đếm chiều dài `rowData` mới nhất và bơm thêm cột vào cuối sheet (hàm `insertColumnsAfter`) nếu schema mở rộng, chống crash khi array vượt quá physical columns.
*   **Cập nhật Schema V18:** Bổ sung bóc tách 3 trường nhạy cảm mới từ web: `Điện thoại Đầu Chủ`, `Tên Đầu Chủ (Hợp đồng)`, `Điểm Facebook`.
*   **Luồng dữ liệu Admin Review:** Chuyển hướng duyệt bài từ Sheet `Public` cũ sang Sheet `BDS_KhangNgo_Source` (38 cột).
*   **UI Trạm Phân Loại Ảnh (V13/V14):** Gom 3 nút dán nhãn (`[MT]`, `[HẺM]`, `[NỀN]`) trực tiếp vào mỗi tấm ảnh ở Thư viện Nội dung. Tự động tính toán thứ tự chuẩn xác. Trả Thư viện Thửa đất về nguyên trạng mặc định lưu vào `Sơ đồ 1, 2`.

### 2026-05-16 (Dual-ID System & Extension V10)
*   **Dual-ID System:** Xây dựng cơ chế Hệ thống ID Kép. Thêm `System ID` (Cột BU Pool, AI Public) sinh ngẫu nhiên 1 lần bằng thời gian base36 (Vd: `SYS-LW842XYZ-QW`) để làm mỏ neo không đổi.
*   **Share Link Robustness:** Web Client `BDS-KhangNgo` sử dụng `System ID` để gen link share thay cho `temp_id` hoặc Mã Khang Ngô. Điều này đảm bảo Link Khách không gãy dù Khang đổi thuật toán Mã Khang Ngô.
*   **Cập nhật Cipher Khang Ngô:** Đổi hàm tạo Mã Khang Ngô tự động. Số nhà ➡️ chuyển thành Chữ in hoa (1:M, 2:H, 3:B, 4:A, 5:N, 6:S, 7:Z, 8:T, 9:C, 0:O, .:I). Chữ cái ➡️ in thường. Tên đường ➡️ Viết tắt đảo ngược có Regex Normalization cho các họ đường phức tạp (CMT8, 3/2, Đường số X). Cài chữ W vào vị trí số 2.
*   **Cập nhật Chrome Ext V10:** Gói thêm `sourceUrl` vào dữ liệu cào. Chuẩn hoá quy tắc lưu trữ ZIP Extension (bắt buộc dùng `v` in thường và bọc root folder).

### 2026-05-13 (Nâng cấp Share Link & Tính năng Tàng hình)
*   **Share Link Robustness:** Thay thế cơ chế mã hoá `bitmask` bằng `temp_id` (Auto Row Index). Giải quyết triệt để lỗi khách hàng không mở được link khi Khang thay đổi chuỗi ID (Mã căn). Cấu trúc URL mới: `?s=1,4,15`. Vẫn giữ tính tương thích ngược với các link chia sẻ cũ.
*   **Tính năng Mark Invisible:** Cho phép Khang đánh dấu ẩn 1 căn nhà (không hiện trên Web và trong link Khách) bằng cách gõ `Đã bán`, `Ẩn`, hoặc `Invisible` vào cột N (**Tình trạng nhà**). Khắc phục vấn đề sai lệch index khi xoá dòng.

### 2026-05-12 (Giai đoạn 1 Hệ Thống Tracking & Link Cá Nhân Hoá)

- **feat(tracking): Google Apps Script API Setup** — Cấu hình API qua `setup_tracking.gs` để ngầm lưu Tracking Log (với tuỳ chọn mode: `no-cors` ẩn danh) về Private Sheet của Admin. Bắt hai sự kiện cốt lõi: `Mở danh sách nhà` và `Xem chi tiết nhà #ID`.
- **feat(ui): Custom Modal Tạo Link Gửi Khách** — Thay thế `prompt()` thô sơ của trình duyệt bằng một HTML Overlay Modal chuyên nghiệp, cho phép nhập cùng lúc **Tên Khách Hàng** (hiển thị web) và **Ghi Chú Nội Bộ** (ẩn hiển thị, chỉ ném vào Tracking).
- **feat(encode): Multi-variable URL Params** — Đóng gói Tên + Ghi chú (phân tách bằng `|`) để encode base64 vào param `&c=`. Logic decode tách phần tên đẩy ra giao diện, phần ghép đẩy về tracking log.
- **feat(seo): Open Graph Thumbnail (Zalo/FB preview)** — Tích hợp Meta tags (og:title, og:description, og:image) để hiển thị Thumbnail chuyên nghiệp (ảnh `avatarKhangNgo.jpg`) khi Share qua Zalo hoặc Facebook.
- **fix(share): Khôi phục Web Share API** — Đảm bảo trải nghiệm trên Mobile thiết bị thật: Gỡ bỏ việc Share Box chiếm chỗ và gọi thẳng `navigator.share()` thay vì chỉ copy text tĩnh trên mobile.
- **sync(pkm): Cập nhật Dashboard Protocol V1** — Cấu trúc lại toàn bộ hệ sinh thái Admin & Client web trong `00 Projects Dashboard.md` theo nguyên tắc MoC.

### 2026-05-10 (buổi tối)

- **feat: Lightbox toàn màn hình** — Click ảnh/video trong chi tiết → mở full-screen viewer với nền đen, dải thumbnail cuộn ngang, vuốt trái/phải chuyển ảnh. Không mở link ảnh gốc nữa.
- **fix: Video iframe bị cắt chiều cao** — Sửa CSS `aspect-ratio: 9/16; width: auto; height: 100%` để fit theo chiều cao, hai bên letterbox.
- **perf: Tối ưu hiệu năng iOS filter** — Refactor: `render()` chỉ chạy 1 lần khi load. Tách `applyFilter()` chỉ toggle CSS `display:none` → phản hồi <50ms, hết đơ iPhone.
- **fix: Share link Unicode crash** — Bỏ `btoa/atob` (crash ký tự Việt). Dùng ID trực tiếp.
- **feat: Bitmask share link** — Nén 64+ căn thành ~11 ký tự URL-safe, giữ domain GitHub tin cậy.
- **feat: Admin Chọn tất cả / Bỏ chọn tất cả** — Nút floating ☐/☑, hoạt động theo danh sách đang hiển thị sau filter.
- **ux: Auto-close bộ lọc** — Đóng khi bấm ra ngoài header hoặc cuộn xuống, giải phóng màn hình.
- **feat: Icon đánh giá trên card** — ▶ xanh (Hàng Ngon) / ⏸ đỏ (Hàng Lỗi), kế chip "tầng".
- **chore: Di dời repo** — Chuyển từ `00_INBOX` sang `01_PROJECTS/BDS-KhangNgo`, xoá file cá nhân khỏi GitHub.

### 2026-05-25 (Nghiệm thu US-034 - Tối ưu hóa & Rút ngắn Tham số c)

- **feat: Tối ưu hóa & Rút ngắn Tham số c khi chia sẻ link gửi khách (US-034)**
  - Tối ưu hóa bộ mã hóa Client-side (`index.html`) bằng cách thay đổi ký tự phân tách thông tin khách hàng từ `" | "` sang `"|"`.
  - Thiết kế cơ chế nén chủ động "cắt đuôi" (cắt bỏ phần trường trống phía sau nếu không nhập Ghi chú hay Tiêu đề trang).
  - Tích hợp chuẩn mã hóa **Base64URL** (triệt tiêu hoàn toàn dấu đệm padding `=` dư thừa cuối chuỗi), giúp độ dài biến `c` tiết kiệm từ **6 đến 8 ký tự** trên URL thực tế.
  - Tương thích ngược hoàn hảo 100% bằng cách nâng cấp bộ giải mã ở cả Client-side (`index.html`) và Server-side (`api/index.js`) sử dụng `.split("|").map(p => p.trim())` kết hợp khôi phục padding `=` tự động dựa trên bội số của 4. Đảm bảo toàn bộ các link cũ đã gửi khách hàng vẫn xem mượt mà, không gặp lỗi.
  - Chạy test suite mô phỏng 4 kịch bản đạt 100% Green Pass, đẩy trực tiếp lên GitHub production.

### 2026-05-25 (Nghiệm thu US-033 - Tùy chỉnh Tiêu đề trang khi chia sẻ)

- **feat: Tùy chỉnh Tiêu đề trang khi tạo link chia sẻ gửi khách hàng (US-033)**
  - Tích hợp ô nhập liệu **Tiêu đề trang (hiển thị trên tab trình duyệt của khách)** vào `#linkModal` trong `index.html`.
  - Nâng cấp cơ chế mã hóa thông tin chia sẻ phía Client: ghép thêm `cTitle` vào chuỗi token khách hàng `fullCustomerString = `${cName} | ${cNote} | ${cTitle}`` và nén Base64.
  - Xử lý giải mã động `parts[2]` ở phía Client để tự động thay đổi `document.title` tương ứng. Đảm bảo tính tương thích ngược hoàn hảo với toàn bộ link cũ.
  - Khắc phục lỗi trên Vercel Serverless Function ([api/index.js](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/api/index.js)): Thay thế điều kiện chặn sớm `if (!s)` thành khối điều kiện `if (s) { ... }`, giúp hàm serverless luôn đi tiếp đến bộ giải mã `c` để cập nhật tiêu đề `<title>` và `<meta og:title>` tĩnh phía server khi chia sẻ nhiều căn bằng link bitmask (`?b=...`).
  - Đã được kiểm thử mô phỏng đạt kết quả tuyệt đối (100% Green Pass) và đẩy thành công lên GitHub production.

### 2026-05-25 (Sửa đổi v5, US-028 & US-029)

- **feat: Nén link gửi khách bằng Bitmask siêu ngắn (Compressed Bitmask Links - US-028)**
  - Đồng bộ hóa thuật toán mã hóa Bitmask B64 cho luồng tạo link khách hàng cá nhân hóa (Flow B). Khi chọn nhiều căn, đường dẫn sẽ được nén cực ngắn thành dạng `?b=encoded_bitmask&c=encoded_name` thay vì chuỗi dài `?s=SYS-XXXX,SYS-YYYY...` dễ bị Zalo/Messenger cắt vụn.
  - Bảo toàn tính tương thích ngược và tính năng Zalo Preview thông minh (US-027) cho trường hợp chỉ chọn đúng 1 căn nhà: luồng vẫn tự động sinh `?s=SYS-XXXX&c=encoded_name` để Vercel Serverless Function tiêm dynamic meta tags (tiêu đề, mô tả và hình ảnh chính xác của căn nhà).
  - Tối ưu hóa bộ giải mã `decodeBitmask` ở phía Client, tự động loại bỏ các sản phẩm ẩn (`is_invisible`) trước khi lập bản đồ nhị phân, loại bỏ hoàn toàn rủi ro lệch vị trí bit (bit shifting) gây hiển thị sai lệch khi rổ hàng thay đổi.
- **feat: Bộ lọc lập trình (Scrubber) chống trùng lặp Hẻm / Xe hơi trong USP (Sửa đổi v5 - US-025)**
  - Tích hợp bộ dọn dẹp hậu xử lý (post-processing scrubber) trong cả JavaScript (`trimTieuDeBds`) và Python (`trim_tieu_de_bds`).
  - Tự động phát hiện tiêu đề bắt đầu bằng tiền tố `"HXH "` và lọc bỏ triệt để các từ khóa trùng lặp liên quan đến hẻm/xe hơi (như `hẻm`, `xe hơi`, `ô tô`, `đỗ cửa`, `đậu`...) ra khỏi phần USP sau dấu `" | "`.
  - Tự động định dạng viết hoa chữ cái đầu tiên và chuyển `"sát "` thành `"Sát "` ở đầu phần USP còn lại.
  - Sửa lỗi thực tế: `"HXH Điện Biên Phủ - ... | Hẻm ô tô đỗ cửa sát mặt tiền"` thành `"HXH Điện Biên Phủ - ... | Sát mặt tiền"`.
- **feat: Tối ưu hóa Trải nghiệm cuộn trang dứt khoát (Premium Scroll UX)**
  - Tích hợp bộ đo vận tốc cuộn trang (`velocity`) và khoảng cách vuốt (`deltaY`) thời gian thực trong `index.html`.
  - Thiết lập vùng an toàn đầu trang (`scrollY < 120`px) luôn hiển thị Header để điều hướng dễ dàng.
  - Khử nhiễu rung tay (micro-jitter) bằng cách yêu cầu `deltaY > 10`px mới xét cử chỉ.
  - Tách biệt hoàn toàn hành vi cuộn đọc (lướt lên chậm để xem tin cũ - menu giữ ẩn) khỏi hành vi chủ động gọi menu (vuốt lên nhanh dứt khoát với `velocity > 1.6` px/ms hoặc kéo lên cực đại `deltaY > 150`px - menu xuất hiện ngay lập tức).
- **feat: Sắp xếp thời gian & giá (Universal Sort - US-029)**
  - Sắp xếp mặc định sản phẩm mới nhất lên hàng đầu cho tất cả mọi người (khi load dữ liệu thật).
  - Bổ sung nút xếp thời gian `⏱️` kế bên nút xếp giá `💰` trong `.filter-bar` của riêng giao diện Admin.
  - Giữ giao diện Khách hàng hoàn toàn thoáng sạch, đơn giản và tối giản tuyệt đối (ẩn hoàn toàn các nút xếp/lọc cho khách).
- **docs: Cập nhật tài liệu & Test suite**
  - Cập nhật và chạy thành công test suite [test_fallback_title.py](file:///C:/Users/Admin/.gemini/antigravity-ide/brain/e5f1e850-c44e-43e2-9292-9301c94f41bf/scratch/test_fallback_title.py) đạt 100% Green Pass.
  - Deploy và push thành công toàn bộ mã nguồn lên hai repository GitHub (`admin-nha-ban` và `nha-ban`).

### 2026-05-26 (Curator System v2.1 - Tối Giản & Sạch SQLite)

- **feat: Tinh giản giao diện tối đa (Curator Panel v2.1)** — Ẩn hoàn toàn các trường Khang Ngô bổ sung (Mã Khang Ngô, Giá Public, Phân loại Hẻm, Tình trạng nhà, Đánh giá, Ngủ trệt, CHDV, Số PN, Số WC, Đường trước nhà). Trên mục biên tập chỉ hiển thị duy nhất 4 trường địa chỉ thực tế có thể sửa thủ công: **Số nhà (edit-ngo-so-nha)**, **Đường**, **Phường**, **Quận**.
- **feat: Bảng thông tin gốc cào được (Thiên Khôi - Chỉ đọc)** — Thêm khung thông tin chỉ đọc ở góc phải hiển thị đầy đủ 20+ trường cào thô (Mã hàng, Giá chào gốc, Diện tích thực tế/trên sổ, Mặt tiền/Số tầng, Hướng, ĐT/Tên Đầu chủ, ĐT/Tên Chủ nhà, link Facebook của đầu chủ clickable, Nội dung chính & Mô tả chi tiết dạng khung scroll box riêng để copy).
- **feat: Sắp xếp hình ảnh thông minh** — Mặc định khi tin mới tải về toàn bộ ảnh có vai trò là **Ẩn** (nhãn màu xám). Bất kỳ ảnh nào được dán nhãn vai trò khác Ẩn (Bìa, Mặt tiền, Sơ đồ, Hẻm, Nội thất) sẽ **tự động bay lên trên đầu danh sách**, các ảnh Ẩn tự động dồn xuống dưới đáy, giúp tối ưu UX duyệt ảnh.
- **feat: Tự động di cư (Auto-Migration) SQLite Column sạch sẽ** — Thay thế thuật toán regex cũ bằng helper `get_safe_col_name()` thông minh: **Loại bỏ dấu tiếng Việt chuẩn xác trước**, sau đó mới thay khoảng trắng/ký tự đặc biệt bằng một dấu gạch dưới duy nhất. Tên cột trong SQLite hiển thị tiếng Việt không dấu siêu đẹp (`Ma_Hang`, `Hinh_Nhan_Dien`, `Gia_chao`...). Tích hợp cơ chế tự động migration ở Flask startup sử dụng `PRAGMA table_info` và `ALTER TABLE listings RENAME COLUMN` giúp đổi toàn bộ cột database cũ sang cột mới sạch sẽ mà không làm mất 1 dòng dữ liệu.
- **feat: Cloudinary signed upload với Pillow compression 90-95%** — Chuyển đổi image migration từ Drive sang Cloudinary CDN siêu tốc. Tích hợp Pillow-based pre-processing pipeline nén ảnh JPEG quality=75, resize max boundary 1600px giúp giảm dung lượng trung bình từ 2.5MB xuống ~120KB tránh tràn hạn mức miễn phí 25GB.
- **feat: RFC-4180 Escaping TSV Clipboard Copy-Paste** — Khử tab (`\t`) và bọc text có newlines (`\n`, `\r`) hoặc dấu nháy kép (`"`) trong Excel-compatible double-quotes chuẩn RFC-4180, đảm bảo copy-paste dòng 79 cột vào Google Sheets không bao giờ bị lệch dòng hay lệch cột.

### 2026-05-10 (buổi chiều)

- **fix: Mô tả xuống dòng** — Thêm `white-space: pre-wrap` để hiển thị đúng ký tự xuống dòng từ Google Sheet.
- **feat: Facebook Reel** — Tự động nhúng iframe cho link FB (`facebook.com`, `fb.watch`, `fb.gg`). Video ưu tiên vị trí #1 trong gallery chi tiết, ảnh đại diện trang chủ chỉ dùng ảnh tĩnh.
- **feat: Tìm kiếm Real-time** — Thanh search lọc đồng thời Mã căn, Tiêu đề, Tên đường, Phường.
- **feat: Smart Scroll Header** — Header trượt ẩn khi cuộn xuống, hiện khi cuộn lên.
- **feat: Avatar + rebrand header** — Thay icon nhà bằng avatar Khang Ngô, chữ xuống hàng.

### 2026-05-09

- **feat: add reset filter button** (`b0df8c2`)

  - Nút "↺ Xóa lọc" xuất hiện bên phải summary bar — **chỉ hiện khi đang có filter active**
  - Tap → clear tất cả filter, reset toàn bộ tabs về "Tất cả", render lại danh sách
- **feat: multi-select filters + reorder districts + separate Đánh giá row** (`f7ed663`)

  - **Multi-select:** tất cả filter đều toggle (chọn nhiều cùng lúc). Cùng loại = OR, khác loại = AND
  - **Thứ tự quận:** Q3 → Q10 → Phú Nhuận → Tân Bình → Bình Thạnh → Gò Vấp
  - **Tách Đánh giá:** 💎 Ngon / ⚠️ Lỗi thành dòng riêng bên dưới Khoảng giá
  - Refactor toàn bộ JS: thay `cur*` string → `sel*` Set; thêm `getFiltered()`, `tSel()`, `syncTabUI()`
  - `updateStats()` và `render()` dùng chung `getFiltered()` — đảm bảo nhất quán
- **feat: add price range filter** (`da754c2`)

  - 5 khoảng: Dưới 7 tỷ / 7–10 / 10–15 / 15–20 / Trên 20 tỷ
  - Filter giá **độc lập** với quận/phường/đường (không reset khi đổi các filter khác)
  - Summary hiện đầy đủ: *"Quận 3 · P.10 · Hẻm ô tô · 10–15 tỷ"*
- **fix: rename `p_ngu_tret` → `ngu_tang_tret`** (`8a1d16b`)

  - Header thực tế trong sheet là `ngu_tang_tret` (không phải `p_ngu_tret`)
  - Sửa trong mapping JS và hiển thị modal
  - **Lưu ý về quy trình:** AI không tự truy cập Google Sheet. Nếu thêm/xóa cột, paste header thực tế vào chat để AI sửa đúng.
- **feat: add `duong_truoc_nha` filter + fix field name** (`e6fa89a`)

  - Sửa lỗi tên biến: `duong` → `duong_truoc_nha` cho khớp Schema Public thực tế (cột L = loại đường trước nhà)
  - Thêm filter “Đường trước nhà” vào panel: generate động từ data
  - Filter có cấp bậc: Quận → Phường → Đường trước nhà
  - Chọn quận mới → reset phường + đường; chọn phường mới → reset đường
  - Summary hiện đủ: *“Quận 3 · P.10 · Hẹm ô tô”*
  - Sửa SOT: cập nhật Schema đúng với thực tế (24 cột, tên đúng)
- **feat: add compact collapsible filter with ward (phuong) support** (`8ed558f`)

  - Header gọn mặc định: chỉ hiện nút "🎚 Bộ lọc" + tóm tắt filter đang active
  - Tap nút → mở panel trượt xuống với 2 tầng: Quận/TP + Phường
  - Phường được generate động từ DATA, tự thay đổi khi chọn quận khác
  - Đổi quận → tự reset phường về "Tất cả"
  - Summary bar hiện filter đang chọn (ví dụ: "Quận 3 · P.10")
  - Áp dụng cho Admin only (public không thấy)
- **feat: sort listing by price high to low** (`b3c72ac`)

  - Thêm `DATA.sort()` theo giá giảm dần ngay sau khi load data xong
  - Áp dụng cho cả Admin và khách có share link

### 2026-05-07 (buổi chiều)

- **Fix data override bug: use fullList** (`d726153`)
  - Bug: Biến `list` chưa được định nghĩa trong scope → DATA bị ghi đè thành `undefined`
  - Fix: Đổi tên mảng map thành `fullList`, gán đúng vào `DATA`
- **Fix undefined fields** (`5c8d3b6`)
  - Khôi phục mapping `rong_hem` (col M) và `tinh_trang` (col N)
  - Các trường này bị mất sau lần refactor trước

### 2026-05-07 (buổi sáng)

- **Fix share logic and sync** (`2fc3a1e`)
  - Sửa logic share link persistent: lưu danh sách ID thay vì encode cả data
  - Sử dụng `mstrangpmp` làm collaborator để push code
  - Transfer ownership repo sang `khangngonhapho`
- **Simplify address format** (`5912f69`)
  - Đổi format địa chỉ thành `P.{phường}, Q.{quận}` thay vì tên đầy đủ
- **Fix image box stretching** (`6529751`)
  - Thêm `height: 125px` cố định cho `.ibox` → ảnh đứng không kéo giãn card
- **Add District 10 filter** (`82d56e6`)
  - Thêm nút filter Quận 10, mã `q10`

### 2026-05-05 ~ 2026-05-06

- **Hide assessment from public** (`df1a1f9`)
  - Tab filter "Ngon/Lỗi" chỉ hiện cho Admin (`body.is-admin`)
  - Stats bar cũng ẩn với public
- **Add CHDV field** (`de741c2`)
  - Thêm trường "Căn hộ dịch vụ" (col Q)
- **Add Assessment tags** (`531d432`)
  - Tag màu xanh "Hàng Ngon", màu xám "Hàng Lỗi" hiện trên card
  - Thêm trường "Phòng ngủ trệt" (col P)
- **Replace Frontage with Street** (`aa4f0d6`)
  - Card ngoài hiện tên đường thay vì mặt tiền
- **Rebrand to Khang Ngô Nhà Phố** (`65f563d`)
  - Đổi từ "Nhà Bán HXH" sang "Khang Ngô Nhà Phố"
  - Đổi badge "căn HXH" → "BĐS"
- **Add Ward (Phường)** (`89472b6`)
  - Thêm cột Phường (col I), hiển thị trên card và modal chi tiết
- **Support 10 images** (`8e9b17c`)
  - Mở rộng từ 5 → 10 ảnh mỗi căn (col S đến AB)

### 2026-05-04 (khởi tạo)

- **first commit: nha ban HXH website** (`673ed04`)
  - Khởi tạo website với Google Sheets JSONP integration
  - Filter theo quận (q3, pn, tb, bt, gv)
  - Card list view với ảnh, giá, thông tin cơ bản
  - Bottom sheet modal xem chi tiết
  - Tính năng yêu thích (♡)

---

## 8. ⚠️ LƯU Ý KỸ THUẬT QUAN TRỌNG

### 7.1 Workflow đã đơn giản hoá (từ 10/05/2026)

- Chỉ còn 1 file duy nhất: `index.html` (không cần `nha_ban_sheets.html` nữa)
- Edit trực tiếp `index.html`, commit và push
- Thư mục dự án: `d:\LHTBrain\01_PROJECTS\BDS-KhangNgo`

### 7.2 JSONP thay vì fetch

- Website dùng JSONP callback (`__gsCallback`) thay vì `fetch()` vì:
  - Tránh lỗi CORS khi test local bằng `file://`
  - Hoạt động ngay cả không có server

### 7.3 Google Drive image URL

- Ảnh Google Drive cần convert sang thumbnail URL:
  - Input: `https://drive.google.com/file/d/{ID}/...`
  - Output: `https://drive.google.com/thumbnail?id={ID}&sz=w800`
- Hàm `fixImgUrl(url, sz)` xử lý tự động
- List view dùng `w400`, modal chi tiết dùng `w1200`

### 7.4 Admin password

- Password hiện tại: `trang`
- Kiểm tra qua URL param: `?pwd=trang`
- Để đổi: sửa biến `const ADMIN_PASSWORD = 'trang';`

### 7.5 Sort order

- Danh sách luôn được sort theo **giá từ cao → thấp** sau khi load
- Sort áp dụng trước khi render, sau khi lọc Admin/Share/Public

---

## 9. 🚀 TÍNH NĂNG CẦN THÊM (Backlog)

> Cập nhật khi có thêm yêu cầu mới

- [x] **US-095:** Khắc phục lỗi name 'listings_table' is not defined khi tự động hóa Curation & Xuất bản ở chế độ Pool1 ✅ Done 2026-06-16
- [x] **US-094:** Tái cấu trúc trang chủ index.html theo Kiến trúc Lego Frontend (Master Epic) ✅ Done 2026-06-16
- [x] **US-094A1:** Tách biệt CSS ngoài ra global.css ✅ Done 2026-06-15
- [x] **US-094A2:** Xây dựng Lego Core State Store & Tải dữ liệu ✅ Done 2026-06-15
- [x] **US-094A3:** Phân tách Engine Render danh sách Card BĐS ✅ Done 2026-06-15
- [x] **US-094C:** Cô lập Module Chi tiết & Carousel thực tế của Khách hàng ✅ Done 2026-06-15
- [x] **US-094B:** Cô lập Module Bộ lọc & Tìm kiếm thông minh ✅ Done 2026-06-15
- [x] **US-094D:** Cô lập Module Bộ sưu tập & Lead Capture ✅ Done 2026-06-15
- [x] **US-094F:** Cô lập Module Chi tiết, Preview & Curation dành riêng cho Admin ✅ Done 2026-06-16
- [x] **US-094E:** Tích hợp toàn diện, tối ưu hiệu năng và dọn dẹp index.html ✅ Done 2026-06-16
- [x] **US-093:** Kiểm tra tính khả dụng và lập báo cáo hình ảnh tự tải lên (Không phải hình từ TK) ✅ Done 2026-06-14
- [x] **US-092:** Sửa lỗi Internal Server Error: Missing index.html khi truy cập trang chủ ✅ Done 2026-06-13
- [x] **US-090:** Di cư toàn bộ kho hình ảnh sang Cloudflare R2 & Khắc phục giới hạn hạn mức Cloudinary ✅ Done 2026-06-13
- [ ] **US-089:** Thiết kế hệ thống Pool2 - Phân hệ dữ liệu mới cho SQLite và Google Sheets v2 theo kiến trúc Lego
- [x] **US-089A:** Thiết lập CSDL Quan hệ Pool2 & Tích hợp Luồng Cào thô cục bộ ✅ Done 2026-06-12
- [x] **US-089B:** Tích hợp Google Sheets Đa Quyền Hạn & Luồng Xuất bản Public Whitelist ✅ Done 2026-06-14
- [x] **US-088:** Đổi tên file và di cư tính năng cũ (Pool1) sang Lego ✅ Done 2026-06-11
- [x] **US-085:** Sửa lỗi hiển thị và tối ưu hóa lướt vuốt trên điện thoại Android ✅ Done 2026-06-10

- [x] **US-083:** Bổ sung tính năng xoay ảnh bằng chuyển đổi URL Cloudinary trực tiếp trên Web Admin ✅ Done 2026-06-09
- [x] **US-079:** Tải toàn bộ hình ảnh căn nhà dạng các file ảnh riêng lẻ cho Admin ✅ Done 2026-06-08
- [x] **US-078:** Tích hợp nút Tự động điền AI trong Pool và bảo mật số nhà trên Vercel Admin ✅ Done 2026-06-08
- [x] **US-077:** Kiểm tra sự đầy đủ, sắp xếp thứ tự ưu tiên Phường và sửa lỗi hiển thị header Source ✅ Done 2026-06-08
- [x] **US-076:** Nâng cấp bộ lọc thông số chi tiết nâng cao (Khoảng giá, diện tích sổ, diện tích thực tế, ngang, rộng hẻm, số phòng ngủ) ✅ Done 2026-06-07
- [x] **US-075:** Giải pháp duy trì phiên đăng nhập Google tối thiểu 1 ngày (dùng Apps Script Web App hoặc OAuth Refresh Token) ✅ Done 2026-06-07
- [x] **US-058:** Quét, xoay ảnh thẳng đứng vật lý và tự động dọn dẹp bộ nhớ ảnh lỗi cũ trên Cloudinary cho rổ hàng đã di cư ✅ Done 2026-06-01
- [x] **US-059:** Biểu mẫu Đăng ký Thông tin cho Link Công khai & Phản hồi Khách hàng qua Zalo (Public Share & Lead Capture) ✅ Done 2026-06-02
- [x] **US-060:** Bỏ chọn tất cả hình ảnh trong biên tập hình Admin cho căn đã lên sóng và mặc định bỏ chọn cho căn chưa lên sóng ✅ Done 2026-06-02
- [x] **US-057:** Thanh tìm kiếm thông minh kết hợp nhiều điều kiện và phân tích địa chỉ (Multi-Condition Smart Search Engine with Address & Price Parser) ✅ Done 2026-06-01
- [x] **US-056:** Cập nhật danh sách Phường chuẩn từ SQL vào bộ lọc tìm kiếm trên giao diện Web Vercel Admin cho các Quận trọng điểm ✅ Done 2026-05-31
- [x] **US-055:** Khắc phục triệt để lỗi ảnh Sổ đỏ hiện làm ảnh đại diện trên danh sách Admin ✅ Done 2026-05-31
- [x] **US-054:** Di cư ảnh Sổ không nén lên Cloudinary và lưu link về Pool sheet (backlog) ✅ Done 2026-05-30
- [x] **US-062:** Sửa lỗi sắp xếp theo cập nhật mới nhất/cũ nhất tùy theo danh sách đang xem (Fix Sorting by Last Update depending on Active View) ✅ Done 2026-06-03
- [x] **US-061:** Khắc phục triệt để lỗi hết hạn phiên đăng nhập Google và tự động làm mới token ngầm (Google OAuth Session Timeout Resolution with Auto Silent Refresh) ✅ Done 2026-06-03
- [x] **US-063:** Cào danh sách nguồn hàng từ trang Web Proptech mới ✅ Done 2026-06-03
- [x] **US-064:** Cào Thông tin chung & Giải mã ảnh Swiper trang Chi tiết ✅ Done 2026-06-03
- [x] **US-065:** Nghiên cứu API & Cào tab Thông tin chi tiết (Chủ nhà) + Hồ sơ pháp lý (Sổ đỏ) ✅ Done 2026-06-03
- [x] **US-066:** Đồng bộ Google Sheets Pool & Tương thích Curator UI ✅ Done 2026-06-03
- [x] **US-067:** Sinh ID tự động khi cào hàng loạt và luồng đẩy tin không trùng lặp dữ liệu ✅ Done 2026-06-03
- [x] **US-068:** Tự động sinh ID cho luồng cào từng căn lẻ ✅ Done 2026-06-04
- [x] **US-069:** Menu sinh Mã Khang Ngô và System ID cho các căn gõ tay trên Google Sheets ✅ Done 2026-06-03
- [x] **US-070:** Sửa trùng lặp System ID trên Sheets và khôi phục SQLite hợp nhất từ hai sheet ✅ Done 2026-06-04
- [x] **US-071:** Khắc phục lỗi lệch cột lưu tiêu đề public và hiển thị trùng lặp giá tiền ở panel preview ✅ Done 2026-06-04
- [x] **US-053:** Admin tự upload hình ảnh local cho căn nhà và quản lý tags, public (Local Image Upload & Tagging) ✅ Done 2026-06-05
- [x] **US-072:** Khắc phục lỗi xuất bản Curation ghi đè thiếu trường & lệch cột Google Sheets ✅ Done 2026-06-03
- [x] **US-074:** Tối ưu hóa bố cục giao diện hiển thị trên thiết bị Laptop và màn hình lớn ✅ Done 2026-06-07
- [x] **US-073:** Khắc phục lỗi lệch chỉ số cột ảnh nội thất 16-25 khi lưu Curation ✅ Done 2026-06-06
- [x] **US-086:** Fix lỗi tạo bộ sưu tập (lỗi hiển thị màu chữ, bỏ toàn bộ checkbox sau khi lưu thành công, so khớp chỉ dùng mã system_id duy nhất) ✅ Done 2026-06-11
- [x] **US-087:** Fix lỗi không xóa được bộ sưu tập đã tồn tại (lỗi vỡ chuỗi HTML, click lan truyền sự kiện và tự bật modal xem) ✅ Done 2026-06-11
- [ ] **US-052:** Bản đồ Tương tác Admin hiển thị các BĐS lân cận trong rổ hàng (Interactive Curation Map with Nearby Pool Listings)
- [x] **US-051:** Tích hợp Combobox Tình trạng và Loại bỏ trường Rộng hẻm thừa tại giao diện Biên tập Admin (Curator Editor Status Combobox & Alley Width Cleanup) ✅ Done 2026-05-30
- [x] **US-050:** Hỗ trợ lướt xem ảnh tiếp theo và thanh xem trước ảnh nhỏ khi phóng to hình (Lightbox Photo Swipe & Thumbnails Strip) ✅ Done 2026-05-30
- [x] **US-049:** Đồng nhất giao diện chi tiết Khách hàng với Admin Preview và bổ sung Sao chép nhanh link gửi khách (Unified Client Detail View & Quick Client Link Copy) ✅ Done 2026-05-30
- [x] **US-048:** Khắc phục lỗi lệch chỉ số cột Pool thô và trùng lặp card rỗng trên giao diện Admin (Pool Curation Column Shift & Empty Card Fix) ✅ Done 2026-05-30
- [x] **US-047:** Nâng cấp độ tin cậy và chống lỗi gọi API Cào lại căn nhà (Curator Recrawl API Safety & Robustness) ✅ Done 2026-05-30
- [x] **US-045:** Chọn hình mặt tiền trong web admin cho căn chưa lên sóng (Pool Curation Facade Fix) ✅ Done 2026-05-29
- [x] **US-046:** Phân loại hình ảnh sổ pháp lý và hình mặt tiền riêng biệt (Legal Image Curation Separation) ✅ Done 2026-05-30
- [x] **US-044:** Robustness Upgrades for AI Curation and Frontend Triggering (Khắc phục triệt để lỗi biên tập AI trống trường và tối ưu luồng gọi) ✅ Done 2026-05-29
- [x] **US-043:** credentials.json Location Fallback Resolution for Google Sheet Publishing (Tự động tìm kiếm credentials.json tại nhiều cấp thư mục) ✅ Done 2026-05-29
- [ ] Thêm filter theo loại hình (Mặt tiền / Hẻm)
- [ ] Thêm quận mới khi có nhu cầu
- [x] **US-023:** Tự động xóa ô tìm kiếm và tích hợp nút xóa nhanh ✕
- [x] **US-024:** Bảo mật hình ảnh mặt tiền Admin bằng Google OAuth2 & Silent Auto-Login
- [x] **US-025:** Cấu trúc Tiêu đề BDS AI mới cho batdongsan.com.vn (Bao gồm bộ dọn dẹp Scrubber chống trùng lặp)
- [x] **US-026:** Giới hạn độ dài Tiêu đề BDS AI & Auto-Trimmer
- [x] **US-027:** Di chuyển Hosting sang Vercel & Dynamic Meta Tags khi share 1 căn (Zalo dynamic og:image)
- [x] **US-028:** Đồng bộ cơ chế nén Bitmask gửi khách nhiều căn (?b=...) siêu ngắn để Zalo không bị cắt link
- [x] **US-029:** Sắp xếp theo Sản phẩm mới thêm mặc định trên danh sách, thêm nút xếp thời gian ⏱️ kế bên xếp giá 💰
- [x] **UX Polish:** Tối ưu hóa Trải nghiệm cuộn trang dứt khoát (Premium Scroll UX): Chỉ hiển thị header khi vuốt lên nhanh/mạnh
- [x] **US-033:** Tùy chỉnh Tiêu đề trang khi tạo link chia sẻ gửi khách hàng
- [x] **US-034:** Tối ưu hóa & Rút ngắn Tham số c khi tạo link gửi khách hàng
- [x] **US-035:** Hệ thống cào BĐS & Mini-App biên tập rổ hàng 2000 căn
- [x] **US-036:** Hệ thống Cấu hình Tốc độ Cào tin & Speed Presets linh hoạt
- [x] **US-037:** Tích hợp AI Tools, Cấu hình System Prompt & Tự động tạo Mã Khang Ngô (Fix lỗi trống thông tin, Tự động lưu và chèn Table kế thừa format)
- [x] **US-038:** Đồng bộ Cơ sở Dữ liệu Dự án & Bộ não AI (Memory) đa thiết bị
- [x] **US-039:** Admin Curation Dashboard trên Web Vercel (View Admin riêng kết nối song song Pool & Source và lọc tìm kiếm thô nâng cao) ✅ Done 2026-05-28
- [x] **US-040:** Tự động hóa Luồng Curation & Dán nhãn Sơ đồ khi Cào tin đẩy thẳng về Pool (Tự động di cư đẩy Pool không qua AI Curation & Hỗ trợ đẩy hàng loạt chọn lọc theo bộ lọc Quận, Đường, Số nhà) ✅ Done 2026-05-29

---

---

### 📌 Quy tắc cập nhật file này:

1. **Sau mỗi lần deploy** → thêm entry vào Change Log (section 7)
2. **Sau mỗi yêu cầu backlog** → thêm vào Backlog (section 9), xóa khi done
3. **Nếu thay đổi schema Sheet** → cập nhật bảng section 3
4. **Nếu đổi password/SĐT** → cập nhật section 4 và 5

*File này được tạo và duy trì bởi Antigravity AI Assistant. Cập nhật lần cuối: 2026-06-11.*


## QUY TẮC ĐẶT TÊN (NAMING CONVENTIONS)
- **Phiên bản Chrome Extension**: Đặt chữ v in thường kèm số phiên bản (Ví dụ: 10). TUYỆT ĐỐI KHÔNG dùng V in hoa (V10).
- **Tên file ZIP Chrome Extension**: Phải giữ nguyên cấu trúc tên thư mục gốc làm tiền tố, hậu tố là version (Ví dụ: Chrome_Ext_Crawl_TK_v10.zip). File ZIP này khi bung ra phải trực tiếp trả về một thư mục mang đúng tên Chrome_Ext_Crawl_TK để Chrome hiểu đây là bản cập nhật, không phải Extension mới.
