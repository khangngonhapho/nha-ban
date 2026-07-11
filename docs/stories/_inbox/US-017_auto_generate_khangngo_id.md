---
id: US-017
status: done
date: 2026-05-21
size: S
---

# US-017: Tự động sinh và chuẩn hóa Mã Khang Ngô (ID)

## User story
As *an Admin / System*
I want *hệ thống tự động sinh và chuẩn hóa Mã Khang Ngô (ID) dựa trên số nhà và tên đường theo đúng các quy tắc mã hóa đặc thù*
So that *mỗi căn nhà phố có một mã ID duy nhất, nhất quán, bảo mật thông tin địa chỉ thật nhưng vẫn dễ nhận diện và truy xuất nội bộ.*

## Acceptance criteria
- Khi nhập mới dữ liệu qua API hoặc sinh hàng loạt trên Sheet, hệ thống tự động sinh Mã Khang Ngô chuẩn xác.
- Thuật toán xử lý chuẩn xác các quy tắc sống còn bao gồm:
  - **Cắt số phụ (Dấu cộng):** Nếu số nhà có chứa dấu `+`, chỉ lấy phần số trước dấu cộng (Ví dụ: `1168.42+44` -> `1168.42`).
  - **Bảng ánh xạ số sang chữ in hoa:** Ánh xạ các ký tự số và ký tự ngăn cách:
    - `1` ➡️ `M`
    - `2` ➡️ `H`
    - `3` ➡️ `B`
    - `4` ➡️ `A`
    - `5` ➡️ `N`
    - `6` ➡️ `S`
    - `7` ➡️ `Z`
    - `8` ➡️ `T`
    - `9` ➡️ `C`
    - `0` ➡️ `O`
    - `/` và `.` ➡️ `I`
  - **Giữ chữ cái thường:** Các ký tự chữ cái alphabet trong số nhà phải giữ nguyên nhưng chuyển thành chữ thường (Ví dụ: `36c` -> `BSc`).
  - **Chuẩn hóa tên đường đặc biệt:**
    - Cách Mạng Tháng 8 / CMT8 -> viết tắt thành `CMTT` (đảo ngược thành `TTMC`).
    - Ba Tháng Hai / 3/2 / 3-2 -> viết tắt thành `BTH` (đảo ngược thành `HTB`).
    - Đường số X -> viết tắt thành `DSX` (đảo ngược thành `XSD`).
  - **Viết tắt & Đảo ngược tên đường thường:** Trích xuất chữ cái đầu tiên của mỗi từ trong tên đường (đã loại bỏ toàn bộ dấu tiếng Việt), viết hoa, sau đó đảo ngược chuỗi viết tắt này (Ví dụ: `Lê Văn Sỹ` -> `LVS` -> đảo ngược thành `SVL`).
  - **Ghép nối cấu trúc:** Ghép `[Mã Số Nhà] + 'I' + [Tên Đường Viết Tắt Đảo Ngược]`.
  - **Chèn ký tự Cipher 'W':** Chèn ký tự `W` vào vị trí thứ 2 (1-indexed, tức là sau ký tự đầu tiên) để hoàn tất Mã Khang Ngô cuối cùng (Ví dụ: `BBCIBScISVL` -> `BWBCIBScISVL`).
- Hỗ trợ tính năng `batchRegenerateKhangNgoId` chạy trực tiếp từ menu Google Sheet để sinh lại hàng loạt ID cho các dòng dữ liệu được bôi đen.

## Solution

> [!note]- Key logic
> Logic xử lý cốt lõi được triển khai tại Apps Script thông qua hai hàm chính:
> - `genIdKhangNgo(soNha, duong, quan)`: Dùng cho tính năng chạy hàng loạt bằng tay (`batchRegenerateKhangNgoId`).
> - `generateKhangNgoId(address, street)`: Dùng cho API doPost lưu dữ liệu từ Chrome Extension.
> 
> Các bước cụ thể trong thuật toán:
> 1. **Chuẩn hóa Số nhà:**
>    - Tách bỏ phần số phụ phía sau dấu `+` bằng `split('+')[0].trim()`.
>    - Duyệt qua từng ký tự của số nhà, ánh xạ ký tự số và ký tự phân tách (`/`, `.`) thành các ký tự in hoa tương ứng trong bảng từ điển.
>    - Nếu là ký tự chữ cái, chuyển về chữ thường (`toLowerCase()`).
> 2. **Chuẩn hóa và Viết tắt Tên đường:**
>    - Nhận diện và thay thế Regex cho các đường đặc biệt (CMT8, 3/2, Đường số).
>    - Với các tên đường thông thường, loại bỏ toàn bộ dấu tiếng Việt (ví dụ: `Đ` ➡️ `D`, `á` ➡️ `a`, `ồ` ➡️ `o`...) sử dụng hàm `removeVietnameseTones` hoặc normalize Unicode để đưa về ký tự ASCII thuần túy trước khi lấy chữ cái đầu.
>    - Đảo ngược chuỗi viết tắt bằng cách: `split('').reverse().join('')`.
> 3. **Ghép nối & Chèn ký tự Cipher 'W':**
>    - Ghép chuỗi số nhà đã mã hóa, ký tự nối `I`, và tên đường viết tắt đảo ngược.
>    - Chèn `'W'` vào vị trí thứ 2 (sau index 0) để tăng tính bảo mật và tạo tính nhận diện đặc trưng thương hiệu Khang Ngô.

## Files touched
- `pool_backend_v3.gs` — Nơi định nghĩa các hàm `genIdKhangNgo`, `generateKhangNgoId`, `batchRegenerateKhangNgoId`, và `removeVietnameseTones`.
- `BDS-AGENTS.md` — Cập nhật tài liệu quy tắc sống còn về sinh Mã Khang Ngô để hệ thống duy trì context chuẩn xác.
