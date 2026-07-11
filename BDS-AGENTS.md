# 🤖 Agent Instructions — BDS Khang Ngô

Tài liệu này là con trỏ trung tâm dẫn đến các quy tắc và Gemini Skills chuyên biệt được cấu hình cho dự án.

## 🛑 Rules cốt lõi & Module Map
Toàn bộ quy tắc cốt lõi và bản đồ phân rã module mã nguồn được định nghĩa và tự động tải tại:
- **[Core Rules & Module Map](file:///d:/LHTBrain/.agents/AGENTS.md)**

## 📖 Chi tiết quy tắc nghiệp vụ (Business Rules)
Chi tiết các quy tắc chuẩn hóa tên đường, xử lý số nhà gộp, phân loại hình ảnh và bảo mật dữ liệu PII được phân rã thành các tệp nhỏ tại:
- **[Business Rules Index](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/business_rules/INDEX.md)**

## 🛠️ Danh mục Gemini Skills chuyên biệt
Dự án đã định nghĩa sẵn các Gemini Skills chuyên dùng trong thư mục `.agents/skills/`. Vui lòng đọc tệp `SKILL.md` tương ứng trước khi xử lý:
1. **[fix-bug](file:///d:/LHTBrain/.agents/skills/fix-bug/SKILL.md)**: Dùng khi cần chẩn đoán và sửa lỗi.
2. **[new-feature](file:///d:/LHTBrain/.agents/skills/new-feature/SKILL.md)**: Dùng khi phát triển thêm tính năng mới / User Stories.
3. **[data-sync](file:///d:/LHTBrain/.agents/skills/data-sync/SKILL.md)**: Dùng khi đồng bộ rổ hàng SQLite với Google Sheets.
4. **[refactor-module](file:///d:/LHTBrain/.agents/skills/refactor-module/SKILL.md)**: Dùng khi cần tối ưu hóa và phân rã các script.
5. **[transformation-manager](file:///d:/LHTBrain/.agents/skills/transformation-manager/SKILL.md)**: Dùng để điều phối và theo dõi tiến độ chuyển đổi kiến trúc.