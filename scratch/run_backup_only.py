import os
import sys
import shutil
import json
from datetime import datetime

# Đảm bảo đường dẫn tuyệt đối chính xác
project_root = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
sys.path.append(project_root)

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Khởi chạy tiến trình sao lưu độc lập...")
    
    # 1. Xác định file DB đang kích hoạt từ settings.json
    db_file_name = "raw_archive.db"
    config_file = os.path.join(project_root, "settings.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                if cfg.get("active_pool_system") == "Pool2":
                    db_file_name = "raw_archive_v2.db"
        except Exception as e:
            print("Lỗi đọc file settings.json:", e)
            
    db_file_path = os.path.abspath(os.path.join(project_root, db_file_name))
    print("Database path:", db_file_path)
    
    if not os.path.exists(db_file_path):
        print("[-] Lỗi: Không tìm thấy tệp cơ sở dữ liệu SQLite cục bộ!")
        return

    # 2. Thực hiện sao lưu sang thư mục đồng bộ Google Drive
    backup_dir = "d:/LHTBrain/BDS_Backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Lấy danh sách các bản backup hiện có
    backups = sorted(
        [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.startswith("raw_archive_backup_")],
        key=os.path.getmtime
    )
    
    # Chỉ sao lưu nếu CSDL có sự thay đổi (mtime mới hơn bản backup gần nhất)
    if backups:
        latest_backup = backups[-1]
        if os.path.getmtime(db_file_path) <= os.path.getmtime(latest_backup):
            print("[*] Bỏ qua: Không có thay đổi nào trên Database kể từ bản sao lưu gần nhất.")
            return
            
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"raw_archive_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        shutil.copy2(db_file_path, backup_path)
        print(f"[✅ THÀNH CÔNG] Đã sao lưu database thành công: {backup_name}")
        
        # Thêm bản mới vào danh sách và xoay vòng giữ lại tối đa 5 bản
        backups.append(backup_path)
        while len(backups) > 5:
            try:
                oldest_backup = backups.pop(0)
                os.remove(oldest_backup)
                print(f"  - Đã xóa bản sao lưu cũ: {os.path.basename(oldest_backup)}")
            except Exception as e_del:
                print(f"  [⚠️] Không thể xóa bản cũ: {e_del}")
    except Exception as e_copy:
        print(f"[❌ LỖI] Lỗi trong quá trình copy tệp: {e_copy}")

if __name__ == "__main__":
    main()
