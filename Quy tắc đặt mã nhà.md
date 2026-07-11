
## Quy tắc số nhà, tên đường

### Bộ đặt mã (digit → letter)

| Số | Ký tự |
|---|---|
| 1 | M |
| 2 | H |
| 3 | B |
| 4 | A |
| 5 | N |
| 6 | S |
| 7 | Z |
| 8 | T |
| 9 | C |
| 0 | O |
| / | I |

### Quy ước viết

- Những ký tự trong địa chỉ viết thường để phân biệt với số (vd `36c` → `BSc`).
- Dấu `.` trong địa chỉ xem như dấu `/` → mã hóa thành `I`.
- Tên đường viết tắt và nghịch đảo lại (vd Lê Văn Sỹ → LVS → SVL).
- Giữa phần số nhà và phần tên đường chèn thêm 1 chữ `I` để phân tách.
- Sau khi ghép xong, **chèn `W` hoặc `U` vào vị trí thứ 2** để tạo mã cuối.

### Ví dụ 1: 339/36c Lê Văn Sỹ

1. Số nhà `339/36c` → `B(3)B(3)C(9)I(/)B(3)S(6)c` = `BBCIBSc`
2. Tên đường `Lê Văn Sỹ` → viết tắt `LVS` → đảo `SVL`
3. Ghép có `I` phân tách: `BBCIBSc` + `I` + `SVL` = `BBCIBScISVL`
4. Chèn `W` vị trí 2: **`BWBCIBScISVL`**

### Ví dụ 2: 163.24.80 Tô Hiến Thành

1. Số nhà `163.24.80` (dấu `.` = `/`) → `M(1)S(6)B(3)I(.)H(2)A(4)I(.)T(8)O(0)` = `MSBIHAITO`
2. Tên đường `Tô Hiến Thành` → viết tắt `THT` → đảo `THT` (palindrome)
3. Ghép có `I` phân tách: `MSBIHAITO` + `I` + `THT` = `MSBIHAITOITHT`
4. Chèn `W` vị trí 2: **`MWSBIHAITOITHT`**

## Quy tắc thông tin nhà
Ví dụ: 50.2 5 4 13 12.9 tỷ Hòa Hưng Quận 10
-> Hiển thị các dòng:
- Diện tích: 50.2
- 5 tầng
- Ngang 4
- Dài 13

## Các thông tin trích xuất từ hình
- Diện tích: nếu không có thông tin diện tích thì lấy dài * rộng
- Mặt tiền:
- Giá: 
- Quận: có chữ q đầu. Ví dụ q3
- Tên quận: Quận 3
- Phường (nếu có).
- Loại hình: Mặt tiền/ hẻm
- Hướng nhà: 
- Đường trước nhà: Hẻm ba gác/ Hẻm ô tô lý thuyết / Hẻm ô tô
- Độ rộng hẻm: 
