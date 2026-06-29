import os
import sys

# Set project root path
project_root = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
sys.path.append(project_root)

# Import get_google_credentials from manager.py
from manager import get_google_credentials, load_config

def main():
    print("[+] KHỞI ĐỘNG TIẾN TRÌNH DỌN DẸP SẠCH DỮ LIỆU DÒNG (WIPE) GOOGLE SHEETS & SQLITE...")
    
    cfg = load_config()
    sheet_id = cfg.get("sheet_id")
    if not sheet_id:
        print("[-] Lỗi: Không tìm thấy sheet_id trong settings.json!")
        sys.exit(1)
        
    creds = get_google_credentials()
    if not creds:
        print("[-] Lỗi: Không lấy được credentials Google OAuth!")
        sys.exit(1)
        
    import gspread
    client = gspread.authorize(creds)
    
    print("[+] Đang kết nối tới Google Sheets...")
    spreadsheet = client.open_by_key(sheet_id)
    
    # 1. Dọn dẹp tab Pool (Clear từ dòng 2 trở đi)
    try:
        pool_sheet = spreadsheet.worksheet("Pool")
        pool_row_count = pool_sheet.row_count
        if pool_row_count >= 2:
            print(f"[+] Đang dọn dẹp tab 'Pool' (dòng 2 -> {pool_row_count})...")
            pool_sheet.batch_clear([f"A2:ZZ{pool_row_count}"])
            print("[+] Dọn dẹp tab 'Pool' hoàn tất.")
        else:
            print("[*] Tab 'Pool' không có dòng dữ liệu để dọn dẹp.")
    except Exception as e:
        print(f"[-] Lỗi dọn dẹp tab 'Pool': {e}")
        
    # 2. Dọn dẹp tab Source (Clear từ dòng 3 trở đi)
    try:
        # Source sheet ID is hardcoded in pool_lego.py as "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
        source_sheet_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
        source_spreadsheet = client.open_by_key(source_sheet_id)
        source_sheet = source_spreadsheet.worksheet("Source")
        source_row_count = source_sheet.row_count
        if source_row_count >= 3:
            print(f"[+] Đang dọn dẹp tab 'Source' (dòng 3 -> {source_row_count})...")
            source_sheet.batch_clear([f"A3:ZZ{source_row_count}"])
            print("[+] Dọn dẹp tab 'Source' hoàn tất.")
        else:
            print("[*] Tab 'Source' không có dòng dữ liệu để dọn dẹp.")
    except Exception as e:
        print(f"[-] Lỗi dọn dẹp tab 'Source': {e}")
        
    # 3. Xóa CSDL SQLite cục bộ raw_archive.db
    db_file = os.path.join(project_root, "raw_archive.db")
    print(f"[+] Đang kiểm tra và xóa CSDL SQLite cục bộ tại: {db_file}")
    
    removed_any = False
    for filename in ["raw_archive.db", "raw_archive.db-wal", "raw_archive.db-shm"]:
        file_path = os.path.join(project_root, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  - Đã xóa tệp: {filename}")
                removed_any = True
            except Exception as e_del:
                print(f"  [❌ LỖI] Không thể xóa tệp {filename}: {e_del}")
                
    if not removed_any:
        print("[*] Không tìm thấy file SQLite nào để xóa hoặc đã xóa sạch.")
        
    print("\n[🏁 HOÀN TẤT DỌN DẸP HỆ THỐNG]")
    print("Hệ thống đã trống dữ liệu. Anh có thể bắt đầu cào mới dữ liệu sạch từ đầu!")

if __name__ == "__main__":
    main()
