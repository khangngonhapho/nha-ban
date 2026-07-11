---
id: US-130
status: accepted
date: 2026-07-10
size: M
---

# US-130: Thiết lập Hệ thống Truth Cards — Bộ nhớ dài hạn chống quên logic cho AI Agent

## User story
**As a** Chủ sở hữu dự án (PO)
**I want** hệ thống Truth Cards cô đọng ghi nhận logic đúng hiện tại (luồng hệ thống + luồng dữ liệu), được AI Agent bắt buộc đọc trước khi phân tích/đề xuất, và được cập nhật sau mỗi US nghiệm thu
**So that** AI Agent không bao giờ quên hoặc nhầm lẫn logic nghiệp vụ, không đưa đề xuất dựa trên logic cũ đã bị thay thế, và các tài liệu luôn nhất quán với code thực tế

## Acceptance
- [ ] **Tạo thư mục `.agents/truth_cards/`** chứa ít nhất 6 truth cards ban đầu (SF-001, DF-001 → DF-005).
- [ ] **Mỗi truth card < 50 dòng**, gồm: logic đúng, anti-patterns, code anchors, và `source_docs` trỏ về tài liệu gốc chi tiết.
- [ ] **Phase kiểm toán hoàn tất**: Duyệt 12 tài liệu hiện có, phát hiện và sửa mâu thuẫn (ví dụ: `workflows_map.md` Luồng 5 ghi sai logic cũ).
- [ ] **3 skills được cập nhật**: `new-feature`, `fix-bug` thêm Bước 0 đọc cards; `test-pass` thêm Gate cập nhật cards.
- [ ] **Cơ chế Kiểm toán khi phát hiện Xung đột (Conflict-Triggered Audit)**: Khi user bắt lỗi AI nói sai logic → DỪNG → kiểm toán truth cards + docs + code → tìm gốc rễ xung đột → sửa từ gốc → cập nhật truth card NGAY (không cần chờ test-pass).
- [ ] **Rule 8 được thêm vào `AGENTS.md`**: Bắt buộc xác minh logic từ truth cards trước khi khẳng định.
- [ ] **Script `verify_truth_cards.py`** chạy phát hiện cards lỗi thời = 0 cảnh báo.

## Solution

### Truth Cards KHÔNG thay thế tài liệu hiện có

Truth Cards là **tầng Index cô đọng** — không phải bản sao. Chúng ghi nhận logic đúng hiện tại ở dạng ngắn nhất và **trỏ ngược** về tài liệu gốc chi tiết.

#### Phân cấp tài liệu

| Tầng | Tài liệu | Vai trò | Khi nào đọc |
|---|---|---|---|
| **T1 — Luật** | `AGENTS.md` | Rules sống còn, Module Map, IDs Map | Luôn load tự động vào system prompt |
| **T2 — Truth Cards** | `.agents/truth_cards/*.md` | Logic ĐÚNG hiện tại (cô đọng <50 dòng/card) + trỏ về tài liệu gốc | **Bắt buộc** đọc ở Bước 0 mỗi US/bug |
| **T3 — Tài liệu gốc** | `docs/business_rules/`, `docs/architecture/`, `docs/stories/` | Chi tiết đầy đủ, State Rules, Process Steps | Chỉ đọc khi truth card trỏ đến & cần chi tiết sâu |

#### Quy tắc đồng bộ
- Khi US thay đổi logic → cập nhật truth card **VÀ** tài liệu gốc tương ứng
- Nếu truth card nói khác tài liệu gốc → **truth card thắng** (vì card luôn được verify gần nhất)

### Cơ chế Kiểm toán khi phát hiện Xung đột (Conflict-Triggered Audit)

Khi user **bắt lỗi AI nói sai logic** trong bất kỳ thời điểm nào (trao đổi, phân tích, test...), đây là tín hiệu nghiêm trọng rằng có xung đột ẩn trong hệ thống. Quy trình xử lý:

```
User bắt lỗi AI nói sai logic
    ▼
DỪNG NGAY mọi công việc đang làm
    ▼
KIỂM TOÁN 3 TẦNG (tìm gốc rễ xung đột):
  1. Truth card nói gì? → Đọc lại card liên quan
  2. Code thực tế làm gì? → grep/view_file xác minh
  3. Tài liệu gốc nói gì? → Đọc source_docs
    ▼
XÁC ĐỊNH GỐC RỄ:
  ├─ Card sai (chưa cập nhật) → Sửa card NGAY
  ├─ Tài liệu gốc sai (lỗi thời) → Sửa tài liệu gốc NGAY
  ├─ Code sai (bug) → Tạo bug fix
  └─ Card chưa tồn tại → Tạo card mới NGAY
    ▼
BÁO CÁO cho user:
  "Đã tìm ra gốc rễ: [X] sai vì [lý do]. Đã sửa [Y]."
    ▼
Tiếp tục công việc đang làm
```

> **Quan trọng**: Trường hợp này truth card được cập nhật NGAY LẬP TỨC, không cần chờ test-pass. Vì xung đột logic nếu không sửa ngay sẽ gây sai lệch dây chuyền cho mọi đề xuất tiếp theo.

### Phân loại 2 dạng card

| Loại | Tiền tố | Mô tả |
|---|---|---|
| **Luồng Hệ thống** | `SF-` (System Flow) | Cách các thành phần kết nối & tương tác |
| **Luồng Dữ liệu** | `DF-` (Data Flow) | Dữ liệu đi từ đâu, qua đâu, biến đổi gì |

### Flow Agent đọc khi bắt đầu US/Bug

```
Bước 0.1: Đọc TẤT CẢ truth cards (~400 dòng tổng, rất nhẹ)
    ▼
Bước 0.2: Xác định cards LIÊN QUAN đến yêu cầu hiện tại
    ▼
Bước 0.3: Đọc thêm source_docs nếu cần chi tiết State Rules
    ▼
Bước 0.4: NHẮC LẠI trong plan + file US:
           "Logic hiện tại theo DF-001: [trích dẫn]"
           "US này BỔ SUNG / XÁC NHẬN / XUNG ĐỘT với logic trên"
```

### Vòng lặp hoạt động tổng thể

```
PHASE 0: ĐỌC TRUTH CARDS (Bắt buộc)
    ▼
PHASE 1: PHÂN TÍCH → plan + đồng bộ vào US → PO duyệt
    ▼
PHASE 2: CODING
    ▼
PHASE 3: USER TEST & TRAO ĐỔI (Vòng lặp)
    User phản hồi → CHẠY GATE (đọc card + verify code)
    → Cập nhật plan + ĐỒNG BỘ VÀO US → User xác nhận → code tiếp
    ┌──────────────────────────────────────────────┐
    │ ⚠️ NẾU USER BẮT LỖI AI NÓI SAI LOGIC:       │
    │ → DỪNG → Kiểm toán 3 tầng (card/code/docs)  │
    │ → Tìm gốc rễ → Sửa card + docs NGAY         │
    │ → Báo cáo user → Tiếp tục                    │
    └──────────────────────────────────────────────┘
    Lặp lại đến khi "test pass"
    ▼
PHASE 4: TEST PASS
    → Cập nhật / Tạo mới truth cards (nếu chưa sửa ở Phase 3)
    → Cập nhật tài liệu gốc nếu mâu thuẫn
    → Ghi vào file US: "Truth Cards bị ảnh hưởng"
```

## 📋 Implementation Plan

### Phase 1: Kiểm toán tài liệu hiện có

Duyệt lại toàn bộ để tạo truth cards và phát hiện mâu thuẫn:

| # | Tài liệu | Trích xuất card | Mâu thuẫn? |
|---|---|---|---|
| 1 | `docs/architecture/system_overview.md` | → SF-001 | Cần kiểm tra |
| 2 | `docs/business_rules/workflows_map.md` Luồng 1 | → DF-003 | Cần kiểm tra |
| 3 | `docs/business_rules/workflows_map.md` Luồng 2 | → DF-004 | Cần kiểm tra |
| 4 | `docs/business_rules/workflows_map.md` Luồng 3 | → DF-001 | Cần kiểm tra |
| 5 | `docs/business_rules/workflows_map.md` Luồng 4 | → DF-005 | Cần kiểm tra |
| 6 | `docs/business_rules/workflows_map.md` Luồng 5 | → DF-002 | ⚠️ **MÂU THUẪN**: Ghi "XÓA SẠCH" DB — sai vs US-129 |
| 7 | `docs/stories/_inbox/US-129_*.md` | → DF-002 (nguồn đúng) | Đã cập nhật |
| 8 | `docs/data_dictionary.md` | Tham chiếu từ cards | Cần kiểm tra |
| 9 | `docs/database_architecture_guidelines.md` | Tham chiếu từ SF-001 | Cần kiểm tra |
| 10 | `docs/business_rules/curation_workflow.md` | → DF-001 | Cần kiểm tra |
| 11 | `docs/business_rules/image_classification.md` | → DF-004 | Cần kiểm tra |
| 12 | `docs/business_rules/naming_conventions.md` | Đã ở AGENTS.md Rule 1 | — |

### Phase 2: Tạo Truth Cards + Sửa mâu thuẫn

- Tạo 6 cards: SF-001, DF-001 → DF-005
- Sửa `workflows_map.md` Luồng 5 cho khớp logic US-129

### Phase 3: Cập nhật Skills + AGENTS.md

- `AGENTS.md`: Thêm Rule 8
- `new-feature/SKILL.md`: Thêm Bước 0
- `fix-bug/SKILL.md`: Thêm Bước 0
- `test-pass/SKILL.md`: Thêm Gate

### Phase 4: Tạo Script verify_truth_cards.py

## 📝 Task Checklist (TODO)
- [x] **Phase 1 Kiểm toán**: [x] Đọc 12 tài liệu | [x] So sánh vs code thực tế | [x] Ghi nhận mâu thuẫn
- [x] **Phase 2 Tạo cards**: [x] SF-001 | [x] DF-001 | [x] DF-002 | [x] DF-003 | [x] DF-004 | [x] DF-005 | [x] Sửa workflows_map.md
- [x] **Phase 3 Skills**: [x] Rule 8 AGENTS.md | [x] new-feature Bước 0 | [x] fix-bug Bước 0 | [x] test-pass Gate
- [x] **Phase 4 Script**: [x] verify_truth_cards.py | [x] Chạy = 0 cảnh báo

## Verification Plan

### Automated Tests
```bash
python scratch/verify_truth_cards.py
```

### Manual Verification
- Đọc lại từng truth card → so sánh vs code thực tế
- Kiểm tra 3 skill files đã tích hợp Bước 0 / Gate
- Bắt đầu US tiếp theo, quan sát AI có đọc cards và nhắc lại logic trước khi đề xuất

## Files touched
- [.agents/AGENTS.md](file:///d:/LHTBrain/.agents/AGENTS.md) — Thêm Rule 8
- [.agents/skills/new-feature/SKILL.md](file:///d:/LHTBrain/.agents/skills/new-feature/SKILL.md) — Thêm Bước 0 đọc truth cards
- [.agents/skills/fix-bug/SKILL.md](file:///d:/LHTBrain/.agents/skills/fix-bug/SKILL.md) — Thêm Bước 0 đọc truth cards
- [.agents/skills/test-pass/SKILL.md](file:///d:/LHTBrain/.agents/skills/test-pass/SKILL.md) — Thêm Gate & Conflict-Triggered Audit
- [.agents/skills/logic-audit/SKILL.md](file:///d:/LHTBrain/.agents/skills/logic-audit/SKILL.md) — Quy trình kiểm toán & giải quyết xung đột
- [.agents/truth_cards/SF-001_system_architecture.md](file:///d:/LHTBrain/.agents/truth_cards/SF-001_system_architecture.md) — Card kiến trúc
- [.agents/truth_cards/DF-001_curation_publish.md](file:///d:/LHTBrain/.agents/truth_cards/DF-001_curation_publish.md) — Card luồng biên tập & xuất bản
- [.agents/truth_cards/DF-002_sync_restore.md](file:///d:/LHTBrain/.agents/truth_cards/DF-002_sync_restore.md) — Card luồng khôi phục & đồng bộ
- [.agents/truth_cards/DF-003_crawl_ingest.md](file:///d:/LHTBrain/.agents/truth_cards/DF-003_crawl_ingest.md) — Card luồng cào & nhập kho
- [.agents/truth_cards/DF-004_image_migration.md](file:///d:/LHTBrain/.agents/truth_cards/DF-004_image_migration.md) — Card luồng di cư ảnh
- [.agents/truth_cards/DF-005_publish_deploy.md](file:///d:/LHTBrain/.agents/truth_cards/DF-005_publish_deploy.md) — Card luồng phát sóng & deploy
- [docs/business_rules/workflows_map.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/docs/business_rules/workflows_map.md) — Sửa mâu thuẫn Luồng 5
- [scratch/verify_truth_cards.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/verify_truth_cards.py) — Script kiểm tra tính cập nhật

## 🔄 Change Requests (Yêu cầu Thay đổi)
*(Chưa có)*

## Notes
- Truth cards được cập nhật tại 2 thời điểm:
  1. **Khi user phát hiện AI nói sai logic** (Conflict-Triggered Audit) → sửa card NGAY LẬP TỨC
  2. **Khi test-pass** → review và cập nhật tổng thể các cards bị ảnh hưởng bởi US
- File US (`US-XXX.md`) được PO ưu tiên hơn `implementation_plan.md` — mỗi khi plan thay đổi phải đồng bộ ngay vào US.
