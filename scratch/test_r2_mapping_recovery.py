import os
import sys
import sqlite3
import json

# Set project root path
project_root = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
sys.path.append(project_root)

import pool_lego
from manager import run_image_migration_thread, get_google_credentials, load_config

def main():
    print("[+] KHỞI ĐỘNG TEST SO KHỚP VÀ PHỤC HỒI HÌNH ẢNH R2...")
    
    # 1. Khởi tạo database
    db_file = os.path.join(project_root, "raw_archive.db")
    if os.path.exists(db_file):
        os.remove(db_file)
        
    print("[+] Đang khởi tạo CSDL mới...")
    pool_lego.init_db(db_file)
    
    # 2. Chèn căn giả lập có tk_id tương khớp với R2 backup map
    tk_id = "fc3f2de9-8af9-4551-b599-1e59672b1c71"
    raw_images = [
        "https://res.cloudinary.com/deru9p712/image/upload/v1779916713/BDS-KhangNgo/fc3f2de9-8af9-4551-b599-1e59672b1c71/22.jpg",
        "https://res.cloudinary.com/deru9p712/image/upload/v1779916713/BDS-KhangNgo/fc3f2de9-8af9-4551-b599-1e59672b1c71/16.jpg"
    ]
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    col_so_nha = pool_lego.get_safe_col_name("Ngõ/Số nhà")
    col_duong = pool_lego.get_safe_col_name("Đường")
    col_quan = pool_lego.get_safe_col_name("Quận")
    col_phuong = pool_lego.get_safe_col_name("Phường")
    
    cursor.execute(f"""
        INSERT INTO listings (tk_id, status, raw_images_tk_json, `{col_so_nha}`, `{col_duong}`, `{col_quan}`, `{col_phuong}`)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (tk_id, "raw_text", json.dumps(raw_images), "123", "Lê Văn Sỹ", "Quận 3", "Phường 13"))
    
    conn.commit()
    conn.close()
    print(f"[+] Đã chèn căn mock: {tk_id}")
    
    # 3. Khởi chạy luồng di cư hình ảnh
    print("[+] Đang kích hoạt run_image_migration_thread...")
    try:
        run_image_migration_thread(limit=1, cookie="mock_cookie", target_tk_id=tk_id)
    except Exception as e:
        print(f"[-] Lỗi trong lúc di cư: {e}")
        
    # 4. Kiểm tra kết quả trong SQLite
    print("\n[+] Đang truy vấn SQLite để xác minh kết quả...")
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
    conn.close()
    
    if not row:
        print("[-] Lỗi: Căn mock bị mất khỏi CSDL!")
        sys.exit(1)
        
    print(f"  - Trạng thái dòng sau di cư: {row['status']}")
    
    # Đọc curated_config_json
    curated_config = json.loads(row["curated_config_json"])
    urls_in_db = [img["url"] for img in curated_config.get("images", [])]
    
    expected_22 = "https://pub-e92603c36c8d4789917d05d1eba12a7e.r2.dev/BDS-KhangNgo/img_fc3f2de9-8af9-4551-b599-1e59672b1c71_22.jpg"
    expected_16 = "https://pub-e92603c36c8d4789917d05d1eba12a7e.r2.dev/BDS-KhangNgo/img_fc3f2de9-8af9-4551-b599-1e59672b1c71_16.jpg"
    
    print(f"  - URLs trong SQLite curated_config_json: {urls_in_db}")
    
    db_ok = expected_22 in urls_in_db and expected_16 in urls_in_db
    
    # 5. Kiểm tra kết quả trong Google Sheets
    print("[+] Đang kết nối Google Sheets để xác minh...")
    cfg = load_config()
    sheet_id = cfg.get("sheet_id")
    creds = get_google_credentials()
    import gspread
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    sheet = spreadsheet.worksheet("Pool")
    
    all_values = sheet.get_all_values()
    headers = all_values[0]
    
    col_anh1_idx = headers.index("Ảnh 1")
    col_anh2_idx = headers.index("Ảnh 2")
    col_mahang_idx = headers.index("Mã Hàng")
    
    # Tìm dòng chứa căn TK-1E59672B1C71
    found_row = None
    for r in all_values[1:]:
        if len(r) > col_mahang_idx and r[col_mahang_idx] == "TK-1E59672B1C71":
            found_row = r
            break
            
    if not found_row:
        print("[-] Lỗi: Không tìm thấy Mã Hàng TK-1E59672B1C71 trên Google Sheets!")
        sys.exit(1)
        
    val_anh1 = found_row[col_anh1_idx]
    val_anh2 = found_row[col_anh2_idx]
    
    print(f"  - Sheet Ảnh 1: {val_anh1}")
    print(f"  - Sheet Ảnh 2: {val_anh2}")
    
    sheet_ok = val_anh1 == expected_22 and val_anh2 == expected_16
    
    if db_ok and sheet_ok:
        print("\n[🎉 TEST SUCCESSFUL] Hệ thống phục hồi ảnh R2 và đồng bộ lên Google Sheets hoạt động hoàn hảo 100%!")
    else:
        print("\n[❌ TEST FAILED] Kết quả xác minh không khớp!")
        sys.exit(1)

if __name__ == "__main__":
    main()
