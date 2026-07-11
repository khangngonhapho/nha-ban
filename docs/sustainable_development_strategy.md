# 🏗️ Chiến Lược Phát Triển Bền Vững Với AI — BDS KhangNgo

## Chẩn Đoán: Tại Sao AI Hay "Quên" Nghiệp Vụ & Sửa Sai?

Sau khi phân tích toàn bộ codebase và tài liệu, tôi nhận ra **3 nguyên nhân gốc rễ** khiến AI liên tục gặp vấn đề:

### 🔴 Nguyên Nhân 1: Các File Monolith Vượt Quá Khả Năng Xử Lý Của AI

| File | Dòng code | Kích thước |
|------|-----------|-----------|
| [manager.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py) | **6,449** | 235 KB |
| [pool_lego.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/pool_lego.py) | **4,104** | 143 KB |
| [SOURCE_OF_TRUTH.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/SOURCE_OF_TRUTH.md) | **3,916** | 187 KB |
| `pool_scripts_v3.js` | ~4,000 | 160 KB |
| [BDS-AGENTS.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/BDS-AGENTS.md) | **357** | 41 KB |
| **Tổng nghiệp vụ cần nạp** | **~18,000+** | **~766 KB** |

> [!CAUTION]
> **Vấn đề cốt lõi:** Ngay cả AI model mạnh nhất cũng không thể giữ trong "bộ nhớ làm việc" 18,000+ dòng code cùng lúc. Khi AI sửa dòng 5,000 của `manager.py`, nó đã "quên" logic ở dòng 200. Đây không phải lỗi AI — đây là lỗi kiến trúc.

### 🔴 Nguyên Nhân 2: Tri Thức Nghiệp Vụ Bị Phân Tán & Trùng Lặp

Hiện tại, cùng một quy tắc nghiệp vụ xuất hiện ở **4 nơi khác nhau**:
1. [SOURCE_OF_TRUTH.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/SOURCE_OF_TRUTH.md) — 187 KB, trộn lẫn schema, UI spec, business rules, changelog
2. [BDS-AGENTS.md](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/BDS-AGENTS.md) — 41 KB, trộn lẫn rules và workflow
3. [system_prompt.txt](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/system_prompt.txt) — 27 KB, duplicate nội dung SOT
4. Hardcode trong code Python/JS/GAS — Không có tài liệu đi kèm

Khi cập nhật 1 rule ở SOT, 3 nơi còn lại thường **không được đồng bộ**, dẫn đến AI đọc thông tin mâu thuẫn.

### 🔴 Nguyên Nhân 3: Không Có "Hàng Rào An Toàn" (Guardrails) Ở Tầng Code

- **141 User Stories** nhưng chỉ có **1 file E2E test** (`test_e2e_pool.py`), **0 unit tests**
- Không có interface/contract giữa các module → AI không biết đâu là ranh giới
- Không có type hints, docstrings trên 15,000+ dòng Python → AI phải "đoán" logic

---

## 🛡️ Chiến Lược Đề Xuất: 4 Trụ Cột Phát Triển Bền Vững

### Trụ Cột 1: Tái Cấu Trúc Tài Liệu — "Đúng Tài Liệu, Đúng Lúc"

**Nguyên tắc:** AI chỉ cần đọc **đúng tài liệu liên quan** cho task hiện tại, thay vì nạp toàn bộ 187KB SOURCE_OF_TRUTH.

#### 1.1 Tách SOURCE_OF_TRUTH thành Module Docs

```
docs/
├── architecture/
│   ├── system_overview.md          # Sơ đồ kiến trúc tổng thể (< 200 dòng)
│   ├── data_flow.md                # Luồng dữ liệu Sheets ↔ SQLite ↔ HTML
│   └── api_reference.md            # Tất cả API endpoints
│
├── business_rules/
│   ├── INDEX.md                    # Mục lục + tóm tắt 1 dòng mỗi rule
│   ├── naming_conventions.md       # Rules tên đường, mã nhà (TTMC, HTB, 7SD...)
│   ├── pricing_rules.md            # Quy tắc giá, đơn vị, format
│   ├── image_classification.md     # Phân loại ảnh facade/diagram/interior
│   ├── data_security.md            # PII, multi-sheet isolation
│   ├── curation_workflow.md        # Quy trình curator duyệt ảnh/thông tin
│   └── search_filter_rules.md      # Logic tìm kiếm, bộ lọc
│
├── schemas/
│   ├── sqlite_schema.md            # Schema SQLite + ràng buộc
│   ├── pool_sheet_schema.md        # (đã có)
│   ├── settings_json_spec.md       # Spec cho settings.json
│   └── api_payload_schemas.md      # JSON schema cho API requests/responses
│
├── ui_specs/
│   ├── pool_list_view.md           # Đặc tả giao diện danh sách
│   ├── pool_detail_view.md         # Đặc tả giao diện chi tiết
│   ├── admin_curation_panel.md     # Đặc tả admin panel
│   └── mobile_responsive.md        # Đặc tả responsive
│
└── changelog.md                    # Tách riêng changelog
```

> [!TIP]
> **Lợi ích:** Khi AI sửa logic giá, nó chỉ cần đọc `pricing_rules.md` (< 100 dòng) thay vì scan toàn bộ SOURCE_OF_TRUTH 4,000 dòng. Giảm 97% noise, tăng 10x độ chính xác.

#### 1.2 Chuyển BDS-AGENTS.md sang Gemini Skills

Thay vì 1 file AGENTS.md dài 357 dòng, tạo **skills chuyên biệt** cho từng loại task:

```
.agents/
├── AGENTS.md                       # Chỉ chứa 3-5 rules cốt lõi
└── skills/
    ├── fix-bug/
    │   └── SKILL.md                # Quy trình sửa bug: đọc test → reproduce → fix → verify
    ├── new-feature/
    │   └── SKILL.md                # Quy trình thêm tính năng: đọc business_rules → plan → code → test
    ├── curation-workflow/
    │   └── SKILL.md                # Quy trình curator: phân loại ảnh, duyệt thông tin
    ├── data-sync/
    │   └── SKILL.md                # Quy trình đồng bộ Sheets ↔ SQLite
    └── deployment/
        └── SKILL.md                # Quy trình deploy Vercel, Git masking
```

> [!IMPORTANT]
> **AGENTS.md chỉ nên chứa 5-10 rules bất khả xâm phạm**, như:
> - Luôn kiểm tra Git branch trước khi sửa
> - Luôn chờ plan approval
> - Không hardcode column index
> - Không push docs lên Git
>
> Tất cả rules chi tiết khác → chuyển vào Skills hoặc Business Rules docs.

---

### Trụ Cột 2: Tách Code Monolith — "Mỗi File, Một Trách Nhiệm"

#### 2.1 Tách `manager.py` (6,449 dòng → 8-10 modules)

```
api/
├── __init__.py
├── routes_pool.py          # Routes cho Pool listings CRUD
├── routes_curation.py      # Routes cho admin curation
├── routes_sync.py          # Routes đồng bộ Sheets
├── routes_images.py        # Routes xử lý ảnh (upload, rotate, classify)
├── routes_search.py        # Routes tìm kiếm
├── routes_collections.py   # Routes bộ sưu tập
└── routes_auth.py          # Routes authentication

core/
├── __init__.py
├── db.py                   # Database connection + helper queries
├── business_rules.py       # Tất cả business rules (naming, pricing...)
├── image_classifier.py     # Logic phân loại ảnh
├── data_transformer.py     # Transform data giữa Sheets ↔ SQLite
└── sheets_client.py        # Google Sheets API wrapper

models/
├── __init__.py
├── listing.py              # Listing data model với type hints
├── image.py                # Image data model
└── collection.py           # Collection data model
```

#### 2.2 Tách `pool_lego.py` (4,104 dòng → Components)

```
templates/
├── components/
│   ├── card.py             # HTML cho listing card
│   ├── detail_view.py      # HTML cho detail view
│   ├── filter_panel.py     # HTML cho bộ lọc
│   ├── admin_panel.py      # HTML cho admin curation
│   ├── image_editor.py     # HTML cho image editor
│   └── share_view.py       # HTML cho share link
├── layouts/
│   ├── base.py             # Base layout (header, footer, scripts)
│   ├── mobile.py           # Mobile-specific layout
│   └── desktop.py          # Desktop-specific layout
└── helpers.py              # Utility functions cho HTML generation
```

> [!WARNING]
> **Không refactor toàn bộ cùng lúc!** Áp dụng chiến lược "Strangler Fig Pattern":
> 1. Tạo module mới bên cạnh code cũ
> 2. Chuyển từng function sang module mới
> 3. Cập nhật import trong `manager.py`
> 4. Chạy E2E test sau mỗi lần chuyển
> 5. Khi module cũ rỗng → xóa

---

### Trụ Cột 3: Test-Driven Safety Net — "Không Test = Không Merge"

#### 3.1 Unit Tests Cho Business Rules (ưu tiên cao nhất)

```python
# tests/test_business_rules.py

class TestNamingConventions:
    """Rule 1: Chuẩn hóa tên đường đặc biệt"""
    
    def test_cach_mang_thang_8_to_ttmc(self):
        assert normalize_street("Cách Mạng Tháng 8") == "TTMC"
        assert normalize_street("CMT8") == "TTMC"
        assert normalize_street("Cách Mạng Tháng Tám") == "TTMC"
    
    def test_ba_thang_hai_to_htb(self):
        assert normalize_street("Ba tháng hai") == "HTB"
        assert normalize_street("3/2") == "HTB"
    
    def test_duong_so_7_to_7sd(self):
        assert normalize_street("Đường số 7") == "7SD"

class TestComplexHouseNumber:
    """Rule 2: Xử lý số nhà phức hợp"""
    
    def test_plus_sign_takes_first_part(self):
        assert extract_house_number("1168.42+44") == "1168.42"
    
    def test_simple_number_unchanged(self):
        assert extract_house_number("123") == "123"

class TestPricingRules:
    """Quy tắc format giá"""
    
    def test_billion_format(self):
        assert format_price(5_500_000_000) == "5.5 tỷ"
    
    def test_million_format(self):
        assert format_price(800_000_000) == "800 triệu"
```

#### 3.2 Contract Tests Cho API

```python
# tests/test_api_contracts.py

class TestListingAPIContract:
    """Đảm bảo API response luôn có đúng cấu trúc"""
    
    def test_get_listing_response_schema(self, client):
        response = client.get("/api/listings/SAMPLE-ID")
        data = response.json()
        
        # Contract: Các field bắt buộc phải tồn tại
        assert "system_id" in data
        assert "khangngo_id" in data
        assert "images_metadata_json" in data
        assert isinstance(data["images_metadata_json"], list)
    
    def test_save_listing_rejects_missing_fields(self, client):
        response = client.put("/api/listings/SAMPLE-ID", json={})
        assert response.status_code == 400
```

> [!TIP]
> **Mỗi khi AI sửa code mà test fail → AI biết ngay đã phá hỏng logic cũ** → tự revert.
> Đây là "hàng rào" hiệu quả nhất chống việc "sửa cái đã đúng".

---

### Trụ Cột 4: Context Loading Protocol — "Nạp Đúng, Nạp Đủ"

#### 4.1 Thiết Kế `.agents/AGENTS.md` Mới

```markdown
# BDS KhangNgo — Agent Rules

## Critical Rules (NEVER violate)
1. Kiểm tra Git branch trước khi sửa code
2. Chờ plan approval trước khi code
3. Không hardcode column index (dùng header lookup)
4. Không push docs lên Git
5. Dùng None-safety pattern: `(data.get("key") or {}).get("subkey")`

## Before Any Task
1. Đọc `docs/NEXT_SESSION.md` để biết context hiện tại
2. Xác định LOẠI task → load skill tương ứng
3. Xác định VÙNG code bị ảnh hưởng → đọc business_rules liên quan

## Module Map (đọc khi cần biết code ở đâu)
- Pool CRUD: `api/routes_pool.py`
- Curation: `api/routes_curation.py` + `core/image_classifier.py`
- Sync: `api/routes_sync.py` + `core/sheets_client.py`
- Search: `api/routes_search.py`
- Business rules: `core/business_rules.py`
- UI components: `templates/components/*.py`

## Testing Requirements
- Sửa business rule → chạy `pytest tests/test_business_rules.py`
- Sửa API → chạy `pytest tests/test_api_contracts.py`
- Sửa UI → chạy E2E tests
```

#### 4.2 Thiết Kế Context Headers Trong Mỗi File Code

```python
# api/routes_curation.py
"""
Routes cho Admin Curation Dashboard.

BUSINESS RULES: docs/business_rules/curation_workflow.md
                docs/business_rules/image_classification.md

RELATED FILES:
  - core/image_classifier.py    → Logic phân loại ảnh
  - templates/admin_panel.py    → UI components
  - core/sheets_client.py       → Đồng bộ kết quả lên Sheets

TESTS: tests/test_curation.py

OWNER: US-039, US-040, US-046, US-060
"""
```

> [!TIP]
> **Khi AI mở file, nó ngay lập tức biết:**
> - Tài liệu nghiệp vụ nào cần đọc
> - File nào liên quan (để không vô tình phá)
> - Test nào cần chạy
> - User Story nào tạo ra code này

---

## 📊 So Sánh: Trước vs Sau

| Tiêu chí | Hiện tại 🔴 | Sau cải tiến 🟢 |
|-----------|-------------|-----------------|
| **AI cần đọc** | ~18,000 dòng mỗi task | 200-500 dòng đúng context |
| **File lớn nhất** | 6,449 dòng (manager.py) | < 500 dòng/file |
| **Business rules** | Nằm rải rác 4 nơi | 1 nơi duy nhất: `docs/business_rules/` |
| **Unit tests** | 0 | 100+ test cases cho core rules |
| **AI sửa sai** | Không biết → phải user check | Test fail ngay → tự revert |
| **Onboard AI mới** | Đọc 187KB SOT + 41KB AGENTS | Đọc AGENTS.md 50 dòng + skill file |
| **Context loading** | Toàn bộ hoặc random | Module map → load đúng file |

---

> [!IMPORTANT]
> **Tóm lại:** Vấn đề không phải AI "ngu" — mà là **kiến trúc hiện tại vượt quá giới hạn context window của bất kỳ AI nào**. Giải pháp không phải viết thêm rules (đã có 20 rules rồi), mà là **tái cấu trúc để AI chỉ cần đọc đúng thứ cần đọc**.
> 
> Mỗi file code < 500 dòng + mỗi doc < 200 dòng + unit tests = AI sẽ gần như không còn "quên" nghiệp vụ.
