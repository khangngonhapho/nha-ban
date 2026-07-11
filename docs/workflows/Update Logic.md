# Quy trình Update Logic Chưa Pass (Unpassed Logic Preservation Workflow)

Tài liệu này định nghĩa quy trình chuẩn chỉnh để AI lập tức ghi nhận, cập nhật tài liệu và sao lưu mã nguồn khi có sự thay đổi về mặt logic, kiến trúc hoặc tính năng mới **ngay cả khi chưa chạy thử thành công hoặc chưa nghiệm thu (unpassed)**. Quy trình này giúp bảo toàn 100% tri thức thiết kế, tránh mất mát dữ liệu và mất context do lịch sử trò chuyện (chat history) bị nén hoặc quá dài.

---

## 🚨 Lý do cốt lõi (Core Purpose)
- AI không giữ được bộ nhớ dài hạn giữa các session và lịch sử chat dài sẽ bị cắt cụt (truncation).
- Nếu phát triển một logic phức tạp (SQLite migrations, crawler updates, image upload logic) mà dừng session giữa chừng khi chưa "pass", toàn bộ chi tiết thiết kế ngầm sẽ bị biến mất ở phiên sau nếu không được ghi lại ngay lập tức vào file vật lý.
- Quy trình này hoạt động như một điểm khôi phục hệ thống (System Restore Point) bằng cách tích hợp trực tiếp một phần **Update Logic Template** ngay trong cấu trúc câu chuyện (User Story - US) khi đang thực hiện (`doing`).
- **Đảm bảo nhất quán kiến trúc:** Mọi cập nhật logic hay cấu trúc dữ liệu phải đảm bảo tuân thủ thiết kế Khối Lắp Ráp Lego quy định trong [system_architecture_deployment.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/system_architecture_deployment.md).

---

## 🔄 Các bước thực hiện tự động (Automated Steps)

### GIAI ĐOẠN 1: KHI ĐANG TRIỂN KHAI (DOING - CHƯA TEST PASS)

Khi vừa hoàn thành viết hoặc chỉnh sửa một phần logic quan trọng nhưng **chưa chạy thử, chưa pass, hoặc chưa được PO nghiệm thu**:

#### 1. Ghi nhận trực tiếp vào mục `## 🛠️ Update Logic` của file US hiện tại
- AI tìm file `.md` của User Story đang triển khai tại `docs/stories/_inbox/`.
- Di chuyển xuống phần **`## 🛠️ Update Logic (Drafting while Doing)`** (được cung cấp sẵn trong template).
- Ghi nhận chi tiết:
  - **Logic & Thuật toán đã viết:** Hàm nào, file nào, hoạt động thế nào.
  - **Cấu trúc dữ liệu thay đổi:** Payload JSON, thay đổi cột SQLite, tham số API.
  - **Điểm nghẽn:** Lý do chưa test pass, hoặc các ca kiểm thử cần thực hiện tiếp theo.

#### 2. Cập nhật Kế hoạch bàn giao (`docs/NEXT_SESSION.md`)
- Mở file [NEXT_SESSION.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/NEXT_SESSION.md).
- Thêm một mục riêng biệt có tiêu đề: **`## 🛠️ Logic Đang Phát Triển (Chưa Nghiệm Thu / Draft Logic)`**.
- Liệt kê mã US và trỏ link markdown trực tiếp đến phần `## 🛠️ Update Logic` của file US đó để session tiếp theo AI có thể truy cập tức thì.

#### 3. Thực hiện Commit và Push mã nguồn "Draft" lên Git
AI bắt buộc phải thực hiện commit và push lên nhánh `main` để sao lưu tri thức:
```powershell
git add .
git commit -m "draft: [US-XXX] sao lưu logic chưa pass vào template US để ghi nhận"
git push origin main
```

---

### GIAI ĐOẠN 2: KHI TEST PASS / NGHIỆM THU THÀNH CÔNG

Khi nhận được xác nhận nghiệm thu hoặc kiểm thử đạt (ví dụ: "test pass" cho một User Story cụ thể):

#### 1. Đồng bộ, tinh chỉnh và giữ lại mục Update Logic chuẩn PMP
- Mở file `.md` của User Story đó.
- **Quy tắc Không Trùng Lắp (Non-Duplication Rule - BẮT BUỘC):**
  - **Các mục chính thức (`Solution` / `Verification Plan`):** Tập trung mô tả **Cái gì (WHAT)** - đặc tả cuối cùng của cấu trúc CSDL, schema API JSON chính thức, và kịch bản test sạch.
  - **Mục `🛠️ Update Logic` (BẮT BUỘC GIỮ LẠI):** Tập trung mô tả **Như thế nào và Tại sao (HOW & WHY)** - nhật ký hành trình kỹ thuật thực tế.
  - AI rà soát để **TUYỆT ĐỐI KHÔNG** để trùng lặp thông tin giữa `Update Logic` và `Solution` (không copy-paste cấu hình JSON hoặc prompt thô đã có ở trên). Thay vào đó, biên tập mục `Update Logic` để lưu trữ vĩnh viễn:
    1.  *Nhật ký Debug & Sự cố giải quyết (Issue Resolution Log):* Các lỗi cụ thể phát sinh trong quá trình code (ví dụ: `NoneType error`, `permission block`) và các helper/line-of-code cụ thể được viết để xử lý.
    2.  *Những phát kiến ngoài kế hoạch (Unexpected Discoveries):* Các điểm tối ưu phát hiện ngẫu nhiên trong lúc viết code (ví dụ: phát hiện frontend gọi API 2 lần nên gỡ trigger).
    3.  *Lịch sử chạy thử nghiệm nháp (Draft Test Logs):* Kết quả chạy các script nháp (`test_ai_curation.py`) kèm phân tích lỗi đã vượt qua.
- **Đúc kết Bài học & Thực tiễn Tốt (Retro & Lessons Learned - BẮT BUỘC):**
  - AI cùng PM rà soát lại toàn bộ các sự cố nghiêm trọng phát sinh trong quá trình code và test để ghi nhận cụ thể vào mục **`## 🧠 Retro, Lessons Learned & Good Practices`** (nêu rõ sự cố, nguyên nhân gốc rễ và giải pháp phòng ngừa).
  - Đồng thời ghi nhận các bài học tốt (Good Practices) đúc kết được để làm cẩm nang hướng dẫn phòng tránh lỗi tương tự cho các US sau.
- Chuyển `status` ở frontmatter của US sang `accepted` (hoặc `done`).
- **Bảo trì Kiến trúc & Deployment:** Nếu các thay đổi logic này tác động tới kiến trúc hoặc sơ đồ hệ thống, cần cập nhật tương ứng vào bản đồ kiến trúc trong [system_architecture_deployment.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/system_architecture_deployment.md).

#### 2. Dọn dẹp kế hoạch phiên tiếp theo
- Xóa bỏ mục logic nháp của US vừa xong khỏi [NEXT_SESSION.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/NEXT_SESSION.md).

---

*Quy trình này được thiết lập và tự động hóa bởi Antigravity AI Assistant để đảm bảo an toàn tri thức tối đa cho dự án. Nâng cấp chuẩn LAAF v1.1 - Quy tắc Không Trùng Lắp (2026-05-29).*
