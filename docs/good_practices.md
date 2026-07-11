# 🧠 Sổ Tay Thực Tiễn Tốt & Bài Học Kinh Nghiệm (Good Practices & Lessons Learned)

Tài liệu này là Kho tri thức tập trung (Centralized Knowledge Base) của dự án. Tất cả các bài học xương máu (Lessons Learned) và thực tiễn tốt (Good Practices) đúc kết từ quá trình nghiệm thu các User Story sẽ được tự động tổng hợp về đây.

> [!IMPORTANT]
> **Lưu ý sống còn:** Đây là các **Good Practices** (Thực tiễn tốt trong bối cảnh cụ thể) chứ chưa phải là *Best Practices* (Quy chuẩn tối cao luôn đúng trong mọi trường hợp). Do đó, khi kế thừa, lập trình viên và AI bắt buộc phải đối chiếu bối cảnh gốc của US liên quan để áp dụng cho phù hợp.

---

## 🛠️ 1. Lập trình & Kiến trúc Hệ thống (Development & Architecture)

### GP-001 (SQLite NoneType Immunity - Kháng Lỗi Null)
- **Tham chiếu US gốc:** [US-044_robust_ai_curation.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-044_robust_ai_curation.md)
- **Tóm tắt Bối cảnh (Context):** Trong bối cảnh server Python (`curator_server.py`) truy vấn trực tiếp từ cơ sở dữ liệu SQLite địa phương. Các trường thông tin không bắt buộc (ví dụ: `Phan_loai_Hem`, `Ngo_So_nha`) rất dễ chứa giá trị `None` (NULL) trong cơ sở dữ liệu. 
- **Giải pháp & Thực tiễn Tốt:** Tuyệt đối không gọi trực tiếp các phương thức chuỗi (`.strip()`, `.lower()`) trên dữ liệu thô. Phải xây dựng và bọc an toàn qua một hàm helper chuyển đổi đối tượng `None` thành chuỗi rỗng `""`.
- **Ví dụ minh họa:**
  ```python
  def safe_str(val):
      return "" if val is None else str(val)

  # Cách dùng an toàn chống crash server:
  phan_loai_hem = safe_str(row['Phan_loai_Hem']).strip().lower()
  ```

### GP-002 (Cấu hình Fallback mặc định an toàn)
- **Tham chiếu US gốc:** [US-044_robust_ai_curation.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-044_robust_ai_curation.md)
- **Tóm tắt Bối cảnh (Context):** Ứng dụng client-server đóng gói cho phép người dùng tự điều chỉnh tệp cấu hình JSON cục bộ (`settings.json`). Người dùng có thể lỡ tay bỏ trống các trường quan trọng (đặc biệt là Prompt hệ thống của OpenAI), gây sập API hoặc làm trôi lệch kết quả JSON đầu ra.
- **Giải pháp & Thực tiễn Tốt:** Hàm tải cấu hình `load_config()` phải kiểm tra từng trường chuỗi rỗng và tự động khôi phục (fallback) về giá trị mặc định của hệ thống (`DEFAULT_CONFIG`) thay vì ghi đè chuỗi rỗng làm hỏng prompt gốc.
- **Ví dụ minh họa:**
  ```python
  def load_config():
      config = read_json("settings.json")
      # Tránh đè chuỗi rỗng lên prompt hệ thống:
      if not config.get("openai_system_prompt", "").strip():
          config["openai_system_prompt"] = DEFAULT_CONFIG["openai_system_prompt"]
      return config
  ```

### GP-006 (Tránh Sử Dụng Logic Đoán Mò - Explicit Data Modeling)
- **Tham chiếu US gốc:** [US-046_legal_image_classification.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/US-046_legal_image_classification.md)
- **Tóm tắt Bối cảnh (Context):** Trong bối cảnh frontend Client SPA (`index.html`) quản lý hiển thị lưới ảnh biên tập hình ảnh (Image Editor Grid). Có các khối logic fallback di cư cũ tự động ép gán vai trò: *"Nếu là thẻ Nội Thất 1 thì tự động coi là ảnh bìa"* mà không so khớp thực tế URL của ảnh có trùng khớp hay không.
- **Giải pháp & Thực tiễn Tốt:** Loại bỏ hoàn toàn các logic đoán mò không an toàn. Mọi logic gán nhãn vai trò, phân loại hình ảnh phải dựa trên so khớp 1-to-1 chính xác (như so sánh URL trực tiếp hoặc đọc chỉ số cột lưu trữ thực tế từ database).
- **Ví dụ minh họa:**
  ```javascript
  // LẤY RA VÀ SO KHỚP CHÍNH XÁC:
  const isAnhNen = String(nềnImgUrl || '').trim() === String(currentImgUrl).trim();
  if (isAnhNen) {
      renderBadge("⭐ Nền");
  }
  ```

### GP-008 (Tối ưu hóa ghi Google Sheets - Batch Updates)
- **Tham chiếu US gốc:** [US-089B_pool2_cloud_publishing.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-089B_pool2_cloud_publishing.md)
- **Tóm tắt Bối cảnh (Context):** Trong bối cảnh đồng bộ dữ liệu lên Google Sheets thực tế của Khách hàng, khi các tệp Sheets bị lệch hoặc thiếu nhiều cột so với schema mới, logic cũ thực hiện thêm cột và ghi đè ô tiêu đề hàng tuần tự từng cột một trong vòng lặp. Việc này sinh ra hàng chục cuộc gọi API ghi liên tục dẫn đến lỗi sập do hạn mức Google API: `429 Quota Exceeded`.
- **Giải pháp & Thực tiễn Tốt:** Tuyệt đối không gọi thêm cột và cập nhật ô đơn lẻ trong vòng lặp. Phải gộp toàn bộ cột thiếu để thêm một lần duy nhất (`add_cols(len(missing))` hoặc `insert_cols`) và thực hiện ghi đè cả hàng tiêu đề bằng một cuộc gọi duy nhất (`update(range_name='A1:col1', values=[headers])`).
- **Ví dụ minh họa:**
  ```python
  # Gộp thêm cột và ghi hàng tiêu đề bằng 2 calls thay vì hàng chục calls:
  raw_sheet.add_cols(len(missing))
  for col in missing:
      raw_headers.append(col)
  col_letter = get_col_letter(len(raw_headers))
  raw_sheet.update(range_name=f"A1:{col_letter}1", values=[raw_headers], value_input_option='USER_ENTERED')
  ```

### GP-009 (Thiết kế Lưu trữ Hình ảnh Lớp Kép - Hybrid Image Storage)
- **Tham chiếu US gốc:** [US-096_connect_vercel_web_to_pool2.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-096_connect_vercel_web_to_pool2.md)
- **Tóm tắt Bối cảnh (Context):** Trong bối cảnh hệ thống Pool2 sử dụng CSDL quan hệ local (`listings_images`) nhưng cần đồng bộ lên 3 file Google Sheets độc lập. Việc lưu trữ ảnh dạng dòng riêng lẻ trên Google Sheets sẽ làm tăng đột biến số lượng dòng trên Sheets (gấp 30 lần) gây sập quota và làm giảm tốc độ load của Web Client. Tuy nhiên, nếu chỉ lưu trữ ảnh dạng chuỗi JSON thô trong database cục bộ sẽ làm giảm nghiêm trọng hiệu năng truy vấn của các công cụ Python offline khi xử lý ảnh hàng loạt (như xoay ảnh, kiểm toán, nén ảnh).
- **Giải pháp & Thực tiễn Tốt:** Áp dụng mô hình Hybrid. Sử dụng chuỗi JSON (`curated_config_json` / `images_metadata_json`) làm trường vận chuyển phẳng (Transport Field) tối ưu cho Google Sheets và Web Client; đồng thời duy trì bảng quan hệ SQLite `listings_images` làm nguồn dữ liệu quan hệ cho các công cụ Python offline. Khi Admin lưu curation từ Web, backend phải đồng thời cập nhật cả hai cấu trúc (nén JSON và chạy truy vấn UPDATE vai trò/thứ tự ảnh trong SQLite). Sử dụng cơ chế Xóa logic (`role='deleted'` hoặc `'hidden'`) để tránh việc Recrawler tự động kéo lại ảnh thô cũ từ API đối tác.
- **Ví dụ minh họa:**
  ```python
  # Cập nhật chọn lọc vai trò và thứ tự ảnh từ dữ liệu curation gửi lên
  for idx, img in enumerate(new_images):
      url = img.get("url")
      role = img.get("role", "interior") # có thể là 'deleted', 'hidden', 'cover'...
      existing = cursor.execute(
          "SELECT id FROM listings_images WHERE tk_id = ? AND (image_url = ? OR r2_url = ?)",
          (tk_id, url, url)
      ).fetchone()
      if existing:
          cursor.execute(
              "UPDATE listings_images SET role = ?, sequence_index = ? WHERE id = ?",
              (role, idx, existing["id"])
          )
  ```

---

## 🤖 2. Kỹ nghệ Prompt & Xử lý GenAI (Prompt Engineering & GenAI)

### GP-003 (Bảo vệ PII và Lọc dữ liệu nhạy cảm)
- **Tham chiếu US gốc:** [US-014_pool_sheet_schema.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-014_pool_sheet_schema.md)
- **Tóm tắt Bối cảnh (Context):** Hệ thống AI Curation gửi thông tin thô của căn nhà sang API OpenAI/Gemini để biên tập tiêu đề/mô tả tự động. Các thông tin nhạy cảm định danh (PII) như số điện thoại, tên riêng của khách hàng/chủ nhà có nguy cơ bị rò rỉ sang bên thứ ba.
- **Giải pháp & Thực tiễn Tốt:** Thiết lập bộ lọc Regex cục bộ trên máy để thay thế/loại bỏ số điện thoại và tên riêng trước khi đóng gói payload gửi đi.
- **Ví dụ minh họa:**
  ```python
  def clean_pii_data(text):
      # Regex xóa số điện thoại:
      return re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REMOVED]', text)
  ```

---

## 🔀 3. Git & Quản lý Nhánh ảo (Git & Branching Automation)

### GP-004 (Luật phòng vệ Switch-Tab chéo nhánh)
- **Tham chiếu US gốc:** [BDS-AGENTS.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/BDS-AGENTS.md)
- **Tóm tắt Bối cảnh (Context):** Môi trường phát triển cục bộ song song nhiều User Story. Lập trình viên/AI mở nhiều tab trò chuyện cùng lúc trên giao diện chat. Khi họ gõ lệnh ở Conversation cũ, AI có thể vô tình ghi đè code trực tiếp lên nhánh Git của Conversation mới đang active dưới máy.
- **Giải pháp & Thực tiễn Tốt:** AI bắt buộc phải chạy lệnh `git branch` đối chiếu trước mọi thao tác ghi file. Nếu phát hiện lệch nhánh, AI tự động chạy commit nháp để cất code dở và checkout sang nhánh đúng.
- **Ví dụ minh họa:**
  ```mermaid
  graph TD
      AI[AI gets File Edit request] --> CheckBranch[Run git branch]
      CheckBranch -->|Branch matches target US| Edit[Edit file safely]
      CheckBranch -->|Branch mismatch| DraftCommit[Commit draft on old branch]
      DraftCommit --> Checkout[Checkout target US branch]
      Checkout --> Edit
  ```

---

## 🧪 4. Kiểm thử & Đảm bảo Chất lượng (Testing & QA)

### GP-005 (Chốt chặn CI kiểm thử Rules sống còn)
- **Tham chiếu US gốc:** [Test Pass.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/workflows/Test%20Pass.md)
- **Tóm tắt Bối cảnh (Context):** Quy trình nghiệm thu tính năng trước khi đưa lên nhánh chính `main` ổn định. AI khi sửa đổi mã nguồn có thể vô ý làm hỏng các quy tắc nghiệp vụ sống còn (chuẩn tên đường, số nhà...).
- **Giải pháp & Thực tiễn Tốt:** Bắt buộc cài đặt Unit Test cho các quy tắc nhạy cảm (`test_rules.py`) và thiết lập chốt chặn cứng ở đầu quy trình nghiệm thu: chỉ cho phép merge về nhánh chính khi 100% các ca test PASS.
- **Ví dụ minh họa:**
  ```powershell
  # Chạy test trước khi merge:
  python test_rules.py
  # Nếu fail -> dừng merge ngay lập tức!
  ```

### GP-007 (Chuẩn Hóa URL Trước Khi So Sánh)
- **Tham chiếu US gốc:** [US-046_legal_image_classification.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/US-046_legal_image_classification.md)
- **Tóm tắt Bối cảnh (Context):** Trong bối cảnh hệ thống quản lý ảnh Carousel và lưới ảnh biên tập. Cùng một bức ảnh có thể tồn tại dưới nhiều dạng URL khác nhau (link thô từ Thiên Khôi, link đã di cư Cloudinary, link có ký tự trống đầu/cuối), dẫn đến việc bộ lọc trùng lặp bỏ sót và render lặp ảnh.
- **Giải pháp & Thực tiễn Tốt:** Viết và áp dụng hàm `normalizeImgUrl()` bóc tách ID ảnh độc nhất trước khi đưa vào bộ so khớp hoặc lọc trùng.
- **Ví dụ minh họa:**
  ```javascript
  function normalizeImgUrl(url) {
      if (!url) return "";
      // Bóc tách phần ID duy nhất sau dấu gạch chéo cuối cùng:
      const parts = url.split('/');
      return parts[parts.length - 1].split('?')[0].trim();
  }
  ```

### GP-014 (Xử Lý Trạng Thái Rỗng/Uncheck Biên)
- **Tham chiếu US gốc:** [US-046_legal_image_classification.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/US-046_legal_image_classification.md)
- **Tóm tắt Bối cảnh (Context):** Trong bối cảnh gọi API Google Sheets để cập nhật thay đổi khi người dùng tích/bỏ tích ảnh công khai. Việc thiết lập điều kiện `if (publicIntStr !== "")` nhằm tránh ghi đè chuỗi rỗng vô tình chặn đứng hành động khi người dùng chủ động uncheck toàn bộ ô chọn (khiến `publicIntStr` trở thành chuỗi rỗng `""`). Kết quả là thay đổi không được ghi xuống và bị khôi phục lại khi reload trang.
- **Giải pháp & Thực tiễn Tốt:** Luôn thiết lập kiểm thử cho các trường hợp biên rỗng, đảm bảo database ghi nhận chính xác ý đồ xóa sạch dữ liệu của người dùng.
- **Ví dụ minh họa:**
  ```javascript
  // Cho phép đồng bộ chuỗi trống để xóa sạch các checkbox trên Sheet:
  const payload = {
      values: [[publicIntStr || ""]]
  };
  ```

### GP-009 (Tách Biệt Vai Trò Hình Ảnh Nhạy Cảm - Role Isolation)
- **Tham chiếu US gốc:** [US-046_legal_image_classification.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/US-046_legal_image_classification.md)
- **Tóm tắt Bối cảnh (Context):** Trong bối cảnh hệ thống phân phối ảnh ra Preview khách hàng hoặc Carousel công khai. Ảnh Sổ đỏ thửa đất hoặc ảnh Mặt Tiền thô chứa thông tin nhạy cảm của ngôi nhà có nguy cơ bị rò rỉ lên công khai nếu người dùng quên bỏ chọn hoặc hệ thống fallback tự động.
- **Giải pháp & Thực tiễn Tốt:** Thiết lập bộ lọc Regex `isFacadeUrl()` hoặc lọc thẻ Sổ đỏ tại grid biên tập và API public để loại bỏ triệt để trước khi render.
- **Ví dụ minh họa:**
  ```javascript
  function isFacadeUrl(url) {
      return url.includes("/raw_facade/") || url.includes("_raw_front_");
  }
  // Loại bỏ triệt để ảnh mặt tiền khỏi mảng ảnh public:
  const publicCandidates = allImages.filter(url => !isFacadeUrl(url));
  ```

### GP-010 (Concurrent Token Refresh Queue - Tránh Race Condition Token)
- **Tham chiếu US gốc:** [US-061_google_auth_timeout_resolution.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-061_google_auth_timeout_resolution.md)
- **Tóm tắt Bối cảnh (Context):** Khi trang web client-side gửi nhiều yêu cầu ghi dữ liệu (hoặc API bảo mật) đồng thời lên Google Sheets, nếu token hết hạn, mỗi luồng gọi sẽ tự động kích hoạt một yêu cầu refresh độc lập. Điều này gây ra lỗi tranh chấp token (race condition), đăng nhập lặp và crash ứng dụng.
- **Giải pháp & Thực tiễn Tốt:** Xây dựng một hàng đợi các Promise resolvers toàn cục `window.tokenResolvers`. Khi một yêu cầu token phát sinh khi tiến trình refresh đang chạy, hãy gom nó vào hàng đợi. Khi nhận được token mới, giải quyết toàn bộ các resolvers trong hàng đợi một lượt để các thao tác được tiếp tục trơn tru.
- **Ví dụ minh họa:**
  ```javascript
  window.ensureValidGoogleToken = function() {
    return new Promise((resolve, reject) => {
      // Nếu token hợp lệ -> trả về luôn
      if (isValid(token)) {
        return resolve(token);
      }
      
      // Đăng ký resolver vào hàng đợi
      window.tokenResolvers.push({ resolve, reject });
      
      // Nếu là yêu cầu đầu tiên kích hoạt refresh, gọi requestAccessToken
      if (window.tokenResolvers.length === 1) {
        gTokenClient.requestAccessToken({ prompt: 'none' });
      }
    });
  }
  ```

### GP-011 (Unique Key Base64 Sharing instead of Array Index Bitmasking)
- **Tham chiếu US gốc:** [US-070_fix_duplicates_and_restore_sqlite.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-070_fix_duplicates_and_restore_sqlite.md)
- **Tóm tắt Bối cảnh (Context):** Trong bối cảnh chia sẻ danh sách nhiều căn BĐS cho khách hàng (multi-share links). Ban đầu hệ thống sử dụng cơ chế nén chỉ mục mảng (bitmask index) của danh sách lọc. Khi dữ liệu database thay đổi (thêm, sửa, xóa, hoặc cào mới chèn dòng), vị trí chỉ mục mảng của các căn bị dịch chuyển, dẫn đến việc giải mã hiển thị sai lệch hoàn toàn danh sách các căn mà admin đã tick chọn gửi cho khách.
- **Giải pháp & Thực tiễn Tốt:** Tuyệt đối không dùng chỉ mục mảng tạm thời hoặc vị trí dòng để mã hóa liên kết chia sẻ. Hãy sử dụng trực tiếp các khóa định danh duy nhất bất biến của thực thể (ở đây là `System ID`). Để tối ưu độ dài URL và tránh bị các app chat cắt cụt link, hãy mã hóa danh sách ID này dưới dạng Base64URL-safe phân tách bằng dấu phẩy.
- **Ví dụ minh họa:**
  ```javascript
  // Mã hóa danh sách System IDs gửi đi:
  function encodeShareIds(systemIds) {
      const idsStr = systemIds.join(',');
      return btoa(idsStr).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  // Giải mã phía Client:
  function decodeShareIds(base64Str) {
      if (!base64Str) return [];
      let normalBase64 = base64Str.replace(/-/g, '+').replace(/_/g, '/');
      while (normalBase64.length % 4) normalBase64 += '=';
      const decodedStr = atob(normalBase64);
      return decodedStr.split(',');
  }
  ```

### GP-012 (Modular Lego Architecture - Kiến trúc Lắp ráp Lego)
- **Tham chiếu US gốc:** [US-088_pool1_lego_migration.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-088_pool1_lego_migration.md)
- **Tóm tắt Bối cảnh (Context):** Trong bối cảnh hệ thống crawler và Flask server cũ được viết dưới dạng Monolithic. Logic phân tích cú pháp, lưu trữ SQLite và đồng bộ Google Sheets bị phân tán chồng chéo, khiến việc phát triển và thử nghiệm các tính năng mới cho rổ hàng Pool2 dễ gây ra lỗi hồi quy (regression) cho rổ hàng Pool1 cũ.
- **Giải pháp & Thực tiễn Tốt:** Tách biệt triệt để mã nguồn hoạt động chính (`fetcher.py`, `manager.py`) khỏi các logic đặc thù của rổ hàng. Xây dựng khối Lego trung tâm `pool_lego.py` để đóng gói toàn bộ logic nghiệp vụ (schema database, SQLite parse & write, Google Sheets sync). Tất cả code phải được viết dưới dạng hàm độc lập, thực hiện một nhiệm vụ duy nhất (Single Responsibility). Các module ngoài tương tác thông qua khớp nối hàm chuẩn và hàm callback để tránh import vòng (Circular Import).
- **Ví dụ minh họa:**
  ```python
  # Trong pool_lego.py:
  def save_raw_to_sqlite(tk_id, metadata, images_tk_list, db_file=None):
      # Chỉ thực thi logic phân tích cú pháp và ghi SQLite
      ...

  # Trong fetcher.py (Module ngoài):
  from pool_lego import save_raw_to_sqlite, get_db_file
  db_file = get_db_file()
  save_raw_to_sqlite(tk_id, crawled_metadata, images_list, db_file)
  ```

### GP-013 (Vercel Serverless Static File Bundling - Đóng gói File tĩnh cho Serverless)
- **Tham chiếu US gốc:** [US-092_fix_homepage_missing_index_error.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-092_fix_homepage_missing_index_error.md)
- **Tóm tắt Bối cảnh (Context):** Trong bối cảnh chạy các serverless functions của Node.js trên Vercel (ví dụ: `api/index.js`). Việc sử dụng các đường dẫn động như `process.cwd()` để đọc tệp tĩnh (như `index.html`) sẽ khiến Vercel NFT (Node File Trace) không thể nhận diện tệp tĩnh này là một dependency, dẫn đến việc tệp không được đóng gói vào lambda zip và gây lỗi `Internal Server Error: Missing index.html` khi chạy thực tế.
- **Giải pháp & Thực tiễn Tốt:** Bắt buộc áp dụng mảng đường dẫn fallback chứa cả đường dẫn tĩnh tương đối sử dụng `__dirname` để Vercel NFT bắt được sự phụ thuộc. Đồng thời cấu hình tường minh thuộc tính `config.includeFiles` trong `vercel.json` để ép trình đóng gói luôn đính kèm các tệp tĩnh cần thiết.
- **Ví dụ minh họa:**
  ```javascript
  // Trong api/index.js:
  const htmlPaths = [
    path.join(__dirname, '..', 'index.html'),
    path.join(process.cwd(), 'index.html')
  ];
  ```
  ```json
  // Trong vercel.json:
  "config": {
    "includeFiles": ["index.html"]
  }
  ```

### GP-015 (SQLite Connection Locking on Windows - Tránh Khóa File Kết Nối SQLite)
- **Tham chiếu US gốc:** [US-089C_pool2_cross_pool_sync.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-089C_pool2_cross_pool_sync.md)
- **Tóm tắt Bối cảnh (Context):** Trên hệ điều hành Windows, các thao tác tệp tin như ghi đè hoặc xóa tệp cơ sở dữ liệu SQLite bị hệ thống kiểm soát rất nghiêm ngặt. Khi một tiến trình hoặc một kịch bản kiểm thử (Unit Test) mở một kết nối SQLite đọc dữ liệu, mọi nỗ lực ghi song song hoặc dọn dẹp file từ tiến trình khác/luồng khác sẽ bị chặn và quăng lỗi `PermissionError: [WinError 32]` hoặc `sqlite3.OperationalError: database is locked`.
- **Giải pháp & Thực tiễn Tốt:** Luôn đóng kết nối SQLite ngay lập tức sau khi lấy xong dữ liệu (`conn.close()`), đặc biệt là trước khi gọi bất kỳ hàm xử lý nào khác có khả năng kết nối lại database đó hoặc thực hiện xóa tệp. Sử dụng khối `try...finally` hoặc context manager (`with sqlite3.connect(...)`) để đảm bảo kết nối luôn được giải phóng an toàn kể cả khi chương trình bị lỗi hoặc thất bại assert ở giữa tiến trình.
- **Ví dụ minh họa:**
  ```python
  def read_helper(db_file):
      conn = sqlite3.connect(db_file)
      try:
          cursor = conn.cursor()
          cursor.execute("SELECT * FROM listings")
          return cursor.fetchall()
      finally:
          conn.close() # Giải phóng khóa file lập tức trên Windows
  ```

### GP-016 (Circular Imports Prevention via Local Imports - Tránh Import Vòng Cục Bộ)
- **Tham chiếu US gốc:** [US-089C_pool2_cross_pool_sync.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-089C_pool2_cross_pool_sync.md)
- **Tóm tắt Bối cảnh (Context):** Khi cấu trúc hệ thống phình to, việc module A (`pool_lego.py`) cần import hàm tiện ích từ module B (`fetcher.py`) và ngược lại module B cũng cần sử dụng các logic lõi của module A để kiểm tra schema hoặc di trú dữ liệu. Việc thực hiện import toàn cục ở đầu tệp tin (global import) sẽ dẫn đến lỗi crash tuần hoàn (Circular Import) ngay khi ứng dụng Flask hoặc kịch bản Unit Test khởi chạy.
- **Giải pháp & Thực tiễn Tốt:** Chuyển các lệnh import của các module phụ thuộc chéo vào bên trong thân hàm cụ thể nơi chúng được gọi (local import). Việc này trì hoãn quá trình giải quyết dependency cho đến khi hàm thực sự được chạy, tránh việc import vòng tại thời điểm load module.
- **Ví dụ minh họa:**
  ```python
  # Trong pool_lego.py:
  def recrawl_all_listings(db_file=None):
      # Tránh circular import bằng cách import cục bộ
      from fetcher import parse_criteria_groups, scrape_district_proptech
      # Tiến hành xử lý nghiệp vụ...
  ```

### GP-017 (Empty Dynamic SQL Syntax Prevention - Phòng ngừa Lỗi SQL Cú Pháp Rỗng)
- **Tham chiếu US gốc:** [US-089C_pool2_cross_pool_sync.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-089C_pool2_cross_pool_sync.md)
- **Tóm tắt Bối cảnh (Context):** Trong các hệ thống lai (Pool1/Pool2), schema của các bảng CSDL có thể khác nhau (ví dụ bảng `listings_v2` loại bỏ hoàn toàn các cột ảnh phẳng). Việc build câu lệnh SQL cập nhật động bằng cách so khớp với danh sách cột thực tế của bảng mục tiêu qua `PRAGMA table_info` đôi khi dẫn đến danh sách trường cần cập nhật bị rỗng (empty), tạo ra các câu lệnh SQL lỗi cú pháp SQLite nghiêm trọng như `UPDATE table SET , status = 'raw_complete'` (thừa dấu phẩy trước cột đầu tiên).
- **Giải pháp & Thực tiễn Tốt:** Trước khi build và thực thi các câu lệnh UPDATE/INSERT động, bắt buộc phải có chốt chặn kiểm tra tính hợp lệ và độ dài của mảng trường động cần cập nhật (`if update_fields:`). Nếu mảng rỗng, thực thi một câu lệnh SQL tĩnh đơn giản tối giản chỉ để cập nhật trạng thái/log thay vì build động lỗi cú pháp.
- **Ví dụ minh họa:**
  ```python
  # Kiểm tra an toàn trước khi ghép chuỗi SQL cập nhật động
  if update_fields:
      cols_sql = ", ".join([f"{col} = ?" for col in update_fields])
      query = f"UPDATE listings_v2 SET {cols_sql} WHERE tk_id = ?"
      cursor.execute(query, values)
  else:
      # Chốt chặn tối giản khi danh sách cột update rỗng
      query = "UPDATE listings_v2 SET status = 'raw_complete' WHERE tk_id = ?"
      cursor.execute(query, (tk_id,))
  ```

### GP-018 (Vietnamese Raw Payload to SQLite Column Mapping - Phân Giải Ánh Xạ Cột Đa Dạng)
- **Tham chiếu US gốc:** [US-089C_pool2_cross_pool_sync.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-089C_pool2_cross_pool_sync.md)
- **Tóm tắt Bối cảnh (Context):** Trong tiến trình cào lại và đối chiếu thay đổi (Crawl Diff Tracking), payload dữ liệu thô nhận về từ đối tác thường lưu dưới dạng các key Tiếng Việt có dấu (ví dụ `"Giá chào"`, `"Số phòng ngủ"`), trong khi cấu trúc cột trong CSDL SQLite được chuẩn hóa thành dạng snake_case không dấu (`"Gia_chao"`, `"bedrooms"`). Việc so khớp trực tiếp giữa key thô tiếng Việt và tên cột SQLite sẽ dẫn đến lệch key, bỏ sót thông tin khác biệt hoặc tạo ra các so khớp sai lệch.
- **Giải pháp & Thực tiễn Tốt:** Xây dựng một bộ phân giải hoặc từ điển ánh xạ động (Dynamic Key Mapping Resolver) để đối chiếu dữ liệu. Khi cần tìm giá trị của một cột trong SQLite từ payload thô, chương trình sẽ tìm kiếm theo cả tên cột SQLite chuẩn hóa lẫn key gốc tiếng Việt có dấu.
- **Ví dụ minh họa:**
  ```python
  # Bộ phân giải tìm kiếm giá trị theo mapping từ điển linh hoạt
  KEY_MAPPING = {
      "Gia_chao": ["Gia_chao", "Giá chào", "Giá"],
      "bedrooms": ["bedrooms", "Số phòng ngủ", "Phòng ngủ"]
  }
  
  def get_payload_val(payload, col_name):
      # Tìm theo key mapping quy ước trước
      for key in KEY_MAPPING.get(col_name, [col_name]):
          if key in payload:
              return payload[key]
      # Fallback tìm trực tiếp
      return payload.get(col_name)
  ```
### GP-019 (Automated E2E Test Suite Run, Evidence Capture & Test Creation)
- **Tham chiếu US gốc:** [US-096_connect_vercel_web_to_pool2.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-096_connect_vercel_web_to_pool2.md)
- **Tóm tắt Bối cảnh (Context):** Để phòng ngừa triệt để các lỗi hồi quy (regression) và đảm bảo tính liên tục của hệ thống, mỗi khi thực hiện một User Story mới hoặc tái cấu trúc mã nguồn, nhà phát triển (hoặc AI agent) bắt buộc phải đảm bảo chạy lại toàn bộ test suite hiện có, bổ sung test case mới cho các tính năng mới và thu thập bằng chứng kiểm định (test evidence).
- **Giải pháp & Thực tiễn Tốt:**
  1. **Chạy toàn bộ test suite tự động:** Trước khi đánh dấu bất kỳ User Story nào hoàn thành (`done`/`accepted`), bắt buộc phải chạy lệnh `python scratch/run_all_e2e.py`. Script này sẽ tự động phát hiện mọi tệp `test_e2e_*.py` trong thư mục `scratch/` và thực thi chúng, đảm bảo đạt tỷ lệ 100% PASS để tránh lỗi hồi quy.
  2. **Viết mới test E2E:** Nếu User Story can thiệp/bổ sung UI hoặc API mới, bắt buộc phải tạo mới tệp kịch bản kiểm thử E2E tương ứng đặt trong thư mục `scratch/` (dạng `test_e2e_[feature].py`) để runner tự động nhận diện và chạy.
  3. **Chụp ảnh bằng chứng (Evidence Screenshots):** Các tệp E2E test cho luồng UI phải cấu hình tự động chụp màn hình và lưu vào thư mục `docs/workflows/assets/` với định dạng tên `[US-ID]_desktop.png` và `[US-ID]_mobile.png`.
- **Ví dụ minh họa:**
  ```python
  # Trong tệp test E2E Playwright, tự động chụp ảnh màn hình làm bằng chứng kiểm thử
  page.screenshot(path="docs/workflows/assets/US-096_desktop.png", full_page=True)
  print("[E2E] Saved desktop screenshot evidence for US-096")
  ```

### GP-020 (Handling E2E Local Port & Network Flakiness on Windows)
- **Tham chiếu US gốc:** [US-096B_pool2_vercel_frontend_load.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-096B_pool2_vercel_frontend_load.md)
- **Tóm tắt Bối cảnh (Context):** Khi chạy toàn bộ bộ kịch bản kiểm thử E2E Playwright hàng loạt qua script runner (`scratch/run_all_e2e.py`) trên môi trường Windows cục bộ, các tệp test khởi chạy máy chủ web cục bộ động và mở trình duyệt Chromium nhanh chóng có thể dẫn đến xung đột cổng (port conflicts) hoặc trôi lệch cấu hình mạng ảo. Điều này gây lỗi ngắt kết nối trình duyệt như `Page.goto: net::ERR_NETWORK_CHANGED` hoặc `ERR_ABORTED`.
- **Giải pháp & Thực tiễn Tốt:** 
  1. Sử dụng hàm cấp phát cổng ngẫu nhiên thông minh (`get_free_port()`) bằng cách ràng buộc socket vào cổng `0` rồi đóng lại trước khi khởi chạy HTTP server.
  2. Nếu phát hiện một kịch bản test đơn lẻ bị sập do lỗi mạng (`ERR_NETWORK_CHANGED`), hãy thực thi cô lập tệp kiểm thử đó riêng biệt (`python scratch/[test_name].py`). Nếu chạy đơn lẻ vượt qua thành công, đó là lỗi do flakiness cục bộ, không phải do lỗi hồi quy (regression) của mã nguồn.
- **Ví dụ minh họa:**
  ```python
  # Hàm cấp phát cổng ngẫu nhiên và giải phóng lập tức:
  def get_free_port():
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.bind(('', 0))
      port = s.getsockname()[1]
      s.close()
      return port
  ```

### GP-021 (Avoiding Scope Shadowing in Lego Modules - Tránh Shadowing Hàm Toàn Cục)
- **Tham chiếu US gốc:** [US-108_fix_curation_shadowing_render.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/stories/_inbox/US-108_fix_curation_shadowing_render.md)
- **Tóm tắt Bối cảnh (Context):** Khi chia nhỏ mã nguồn Frontend thành kiến trúc Lego (`lego_*.js` nạp qua thẻ script ở `<head>`), các module cục bộ định nghĩa các hàm có tên trùng khớp với các hàm callback toàn cục (như `render()`). Khi gọi trực tiếp tên hàm thô, quy tắc scope chain của Javascript sẽ ưu tiên gọi hàm module cục bộ thay vì hàm toàn cục trên đối tượng `window`, gây lỗi crash/undefined reference khi thiếu tham số truyền vào.
- **Giải pháp & Thực tiễn Tốt:** Khi gọi các hàm callback toàn cục (ví dụ hàm vẽ lại danh sách card, hàm hiển thị toast, hàm reload) từ bên trong Lego modules, luôn chỉ định namespace tường minh `window.render()` hoặc `window.showToast()`. Tránh gọi hàm không có namespace nếu trong module cục bộ có hàm private trùng tên.
- **Ví dụ minh họa:**
  ```javascript
  // Lời gọi lỗi (bị che khuất bởi render(p, sbody) cục bộ của module):
  // render(); // Lỗi: p is undefined

  // Lời gọi đúng:
  window.render(); // Gọi đúng callback render danh sách của index.html
  ```


