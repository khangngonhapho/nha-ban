# 🗺️ Tổng Quan Kiến Trúc Hệ Thống (System Architecture Overview)

Tài liệu này mô tả sơ đồ kiến trúc tổng thể và mối tương quan giữa các thành phần phần mềm của dự án BDS Khang Ngô.

## 1. Sơ Đồ Kiến Trúc Hệ Thống (Mermaid Diagram)

```mermaid
graph TD
    %% Frontend/Client
    subgraph "Frontend / Client View"
        A["Trình duyệt Client<br>(Vercel/GitHub Pages)"]
        B["Chrome Extension<br>(Cào dữ liệu từ Thiên Khôi)"]
    end
    
    %% API / Service Layer
    subgraph "Python Local Backend (manager.py)"
        C["Flask App Factory"]
        D["api/routes_pool.py<br>(Pool CRUD)"]
        E["api/routes_curation.py<br>(Curation & Publish)"]
        F["api/routes_sync.py<br>(Sheets Sync)"]
        G["api/routes_images.py<br>(Upload & Destroy CDN)"]
        H["api/routes_crawl.py<br>(Crawl Integration)"]
        I["api/routes_config.py<br>(Settings)"]
    end
    
    %% Core Library
    subgraph "Core Shared Library"
        J["core/business_rules.py<br>(Quy tắc đặt tên, giá, lọc PII)"]
        K["core/db.py<br>(SQLite operations & WAL)"]
        L["core/config.py<br>(Cấu hình settings.json)"]
    end
    
    %% Databases & Sheets
    subgraph "Databases & External Sheets"
        M[("SQLite Database<br>raw_archive.db")]
        N["Google Sheets Pool<br>(Kho tin thô)"]
        O["Google Sheets Source<br>(Kho đã duyệt, chứa số nhà)"]
        P["Google Sheets Public<br>(Whitelist công khai)"]
    end
    
    %% Connections
    B -->|"POST raw_json"| H
    C -->|"Register Blueprints"| D & E & F & G & H & I
    D & E & F & G & H & I --> J & K & L
    K -->|"Đọc/Ghi"| M
    F -->|"Đồng bộ Sheets"| N & O
    O -->|"IMPORTRANGE"| P
    A -->|"Đọc qua JSONP"| P
    G -->|"Upload/Destroy"| Q["Cloudinary / Cloudflare R2"]
```

---

## 2. Mô Tả Các Component

### a. Flask App Factory (`manager.py`)
- Khởi tạo ứng dụng Flask, nạp cấu hình tập trung và đăng ký các module API (Blueprints) độc lập.
- Giao diện Admin/Curation được gọi trực tiếp qua Vercel frontend hoặc chạy cục bộ.

### b. API Blueprints (`api/`)
- Phân rã các endpoints thành các module dịch vụ riêng biệt để cô lập lỗi:
  - `routes_pool.py`: Xử lý CRUD tin thô.
  - `routes_curation.py`: Duyệt tin, lưu thay đổi và phát sóng.
  - `routes_sync.py`: Đồng bộ dữ liệu SQLite với Google Sheets.
  - `routes_images.py`: Upload ảnh, gán nhãn và xóa ảnh lỗi.
  - `routes_crawl.py`: Kích hoạt và nhận payload từ Chrome Extension.
  - `routes_config.py`: Đọc ghi cấu hình hệ thống.

### c. Core Shared Library (`core/`)
- `business_rules.py`: Chứa 100% logic nghiệp vụ dùng chung, đảm bảo tính nhất quán của dữ liệu (chuẩn hóa tên đường, xử lý số nhà, sinh mã ID, xóa PII).
- `db.py`: Đóng gói cơ sở dữ liệu SQLite, tối ưu hóa ghi đồng thời bằng chế độ ghi trước nhật ký WAL (Write-Ahead Logging) và xử lý khóa tranh chấp (`timeout=30.0`).
- `config.py`: Quản lý nạp tệp cấu hình `settings.json` tập trung.

### d. Tầng Dữ Liệu Ngoại Vi (Google Sheets)
- Phân cấp 3 tầng (Pool -> Source -> Public) giúp bảo vệ thông tin cá nhân của chủ nhà (PII) và nâng cao hiệu năng truy vấn cho giao diện web tĩnh.
