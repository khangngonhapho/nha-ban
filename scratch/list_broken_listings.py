import sys
import gspread

sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
import manager

def main():
    creds = manager.get_google_credentials()
    if not creds:
        print("Could not load credentials.")
        return
        
    client = gspread.authorize(creds)
    sheet_id = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
    
    ss = client.open_by_key(sheet_id)
    sheet = ss.worksheet("Pool")
    all_rows = sheet.get_all_values()
    
    col_map = {
        1: "Hình Nhận Diện",
        27: "Sơ đồ thửa đất 1",
        28: "Sơ đồ thửa đất 2",
        29: "Hình Mặt Tiền",
        30: "Hình Hẻm 1",
        31: "Hình Hẻm 2",
        32: "Hình Hẻm 3",
        33: "Hình Hẻm 4",
        34: "Hình Hẻm 5",
        35: "Hình Hẻm 6",
        36: "Hình Hẻm 7",
        37: "Hình Hẻm 8",
        38: "Hình Hẻm 9",
        39: "Hình Hẻm 10",
        40: "Ảnh 1",
        41: "Ảnh 2",
        42: "Ảnh 3",
        43: "Ảnh 4",
        44: "Ảnh 5",
        45: "Ảnh 6",
        46: "Ảnh 7",
        47: "Ảnh 8",
        48: "Ảnh 9",
        49: "Ảnh 10",
        50: "Ảnh 11",
        51: "Ảnh 12",
        52: "Ảnh 13",
        53: "Ảnh 14",
        54: "Ảnh 15",
        80: "Sơ đồ thửa đất 3",
        81: "Sơ đồ thửa đất 4",
        82: "Sơ đồ thửa đất 5",
        83: "Ảnh 16",
        84: "Ảnh 17",
        85: "Ảnh 18",
        86: "Ảnh 19",
        87: "Ảnh 20",
        88: "Ảnh 21",
        89: "Ảnh 22",
        90: "Ảnh 23",
        91: "Ảnh 24",
        92: "Ảnh 25"
    }
    
    broken_listings = []
    
    for r_idx, row in enumerate(all_rows[1:], start=2):
        ma_hang = row[0].strip() if len(row) > 0 else ""
        quan = row[3].strip() if len(row) > 3 else ""
        phuong = row[4].strip() if len(row) > 4 else ""
        duong = row[5].strip() if len(row) > 5 else ""
        so_nha = row[6].strip() if len(row) > 6 else ""
        noi_dung = row[9].strip() if len(row) > 9 else ""
        
        broken_cols = []
        for col_idx, col_name in col_map.items():
            if col_idx < len(row):
                cell_val = row[col_idx].strip()
                if "cloudinary.com" in cell_val:
                    broken_cols.append(col_name)
                    
        if broken_cols:
            broken_listings.append({
                "row_number": r_idx,
                "ma_hang": ma_hang,
                "so_nha": so_nha,
                "duong": duong,
                "phuong": phuong,
                "quan": quan,
                "noi_dung": noi_dung,
                "columns": broken_cols
            })
            
    # Write report
    report_file = "C:/Users/Khang Ngo/.gemini/antigravity/brain/72b4b200-2519-4411-8d37-dabef40b9ed0/broken_listings_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Báo cáo danh sách căn bị lỗi ảnh (Cloudinary 404)\n\n")
        f.write("Dưới đây là danh sách toàn bộ các căn trong file Google Sheet **Pool (v1)** vẫn còn chứa link hình ảnh Cloudinary cũ (do ảnh đã bị xóa/hết hạn trên Cloudinary nên không thể di cư sang R2). Bạn cần xử lý thủ công các căn này bằng cách đăng ảnh mới.\n\n")
        f.write(f"**Tổng số căn bị lỗi ảnh:** {len(broken_listings)} căn\n\n")
        f.write("| Dòng | Mã Hàng | Ngõ/Số nhà | Đường | Phường | Quận | Cột bị lỗi ảnh | Nội dung chính |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for bl in broken_listings:
            cols_str = ", ".join(bl["columns"])
            f.write(f"| {bl['row_number']} | **{bl['ma_hang']}** | {bl['so_nha']} | {bl['duong']} | {bl['phuong']} | {bl['quan']} | {cols_str} | {bl['noi_dung']} |\n")
            
    print(f"Report generated with {len(broken_listings)} broken listings.")

if __name__ == '__main__':
    main()
