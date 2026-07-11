---
id: US-XXX
status: in-progress
date: YYYY-MM-DD
size: XL
type: master_epic
---

> [!info]- 📋 Hướng dẫn điền template Master US (Epic)
> **id**: Lấy từ INDEX.md
> **status**: `draft` | `backlog` | `in-progress` | `done` | `accepted`
> **size**: Thường là `L` hoặc `XL` do chứa nhiều tính năng/nâng cấp kiến trúc.
> **type**: `master_epic` để nhận diện cấu trúc phân rã trong Stories Index.
> **DoD của Master US:** Chỉ chuyển sang trạng thái `done`/`accepted` khi 100% các US con trong bảng Tracker đã chuyển sang `done`/`accepted` tương ứng và toàn bộ kịch bản kiểm thử tích hợp E2E tự động bằng Python (đa thiết bị) chạy **100% PASS**.
> ⚠️ Xoá callout này trong file US thật khi tạo.

# US-XXX: [Tên Epic lớn, ví dụ: Tái cấu trúc trang chủ index.html theo kiến trúc Lego Frontend]

## Master User Story
**As a** [Vai trò]  
**I want** [Mục tiêu tổng thể/Thay đổi kiến trúc lớn]  
**So that** [Lợi ích nghiệp vụ/Kỹ thuật đạt được]  

## Chiến lược Di cư & Kiến trúc Khớp nối (Migration & Integration Strategy)
- **Cách tiếp cận:** [Mô tả chiến lược di cư từng bước - ví dụ: chia nhỏ luồng trải nghiệm khách hàng trước, admin sau]
- **Khớp nối dữ liệu (Data & State Junction):** [Mô tả cách các module JS ngoài giao tiếp thông qua State Store window.LegoState]
- **Sơ đồ kiến trúc phân rã (Decomposition Map):**
```mermaid
[Vẽ sơ đồ Mermaid Flowchart lộ trình triển khai các US con]
```

## Bảng theo dõi các User Stories con (Sub-US Progress Tracker)

| Mã US | Tên User Story Con | Size | Trạng thái | Link Tài liệu |
| :--- | :--- | :---: | :---: | :--- |
| US-XXXA | [Tên US con] | [S/M/L] | [Status] | [[US-XXXA_slug|US-XXXA]] |
| US-XXXB | [Tên US con] | [S/M/L] | [Status] | [[US-XXXB_slug|US-XXXB]] |

## 📋 Overall Progress Checklist
- [ ] **US-XXXA:** [Tóm tắt công việc US con A] (Chốt ngày: YYYY-MM-DD)
- [ ] **US-XXXB:** [Tóm tắt công việc US con B] (Chốt ngày: YYYY-MM-DD)

## 🔄 Change Requests (Yêu cầu Thay đổi cấp Epic)
*(Nhật ký ghi nhận các thay đổi về mặt phạm vi hoặc định hướng kỹ thuật lớn tác động đến toàn bộ Epic)*
- **CR-01 (YYYY-MM-DD):**
  - **Yêu cầu cũ:** [Mô tả yêu cầu gốc]
  - **Yêu cầu mới:** [Mô tả yêu cầu thay đổi mới]
  - **Tác động:** [Cập nhật lộ trình các US con]

## Master Verification Plan (Kịch bản kiểm thử E2E tổng thể)

> [!check]- Automated E2E Testing (BẮT BUỘC - Desktop & Mobile)
> - **Script kiểm thử chính:** [test_e2e_curator.py](file:///d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_e2e_curator.py)
> - **Kịch bản E2E:** 
>   1. Chạy trên **Desktop viewport (1280x800)**: Giả lập hành vi Admin và Khách hàng trên PC (Lọc, Preview, Curation, Save...).
>   2. Chạy trên **Mobile viewport (375x812, hasTouch=True)**: Giả lập hành vi vuốt chạm, responsive, Carousel và Lead capture.
>   *Yêu cầu:* Đạt tỷ lệ **100% PASS** trên toàn bộ các test cases đa thiết bị.

> [!check]- Manual Verification
> - [Các bước test thủ công tích hợp tổng thể của PO]
