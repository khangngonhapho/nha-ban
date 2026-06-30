import os
import sys
import shutil
import json
from datetime import datetime

# Dam bao duong dan tuyet doi chinh xac
project_root = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
sys.path.append(project_root)

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Khoi chay tien trinh sao luu doc lap...")
    
    # 1. Quet tu file settings.json de tim file DB dang active
    db_file_name = "raw_archive.db"
    config_file = os.path.join(project_root, "settings.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                if cfg.get("active_pool_system") == "Pool2":
                    db_file_name = "raw_archive_v2.db"
        except Exception as e:
            print("Loi doc file settings.json:", e)
            
    db_file_path = os.path.abspath(os.path.join(project_root, db_file_name))
    print("Database path:", db_file_path)
    
    if not os.path.exists(db_file_path):
        print("[-] Loi: Khong tim thay tep co so du lieu SQLite cuc bo!")
        return

    # 2. Thuc hien sao luu sang BDS_Backups
    backup_dir = "d:/LHTBrain/BDS_Backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Lay danh sach cac ban backup hien co
    backups = sorted(
        [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.startswith("raw_archive_backup_")],
        key=os.path.getmtime
    )
    
    # Chi sao luu neu CSDL co su thay doi (mtime moi hon ban backup gan nhat)
    if backups:
        latest_backup = backups[-1]
        if os.path.getmtime(db_file_path) <= os.path.getmtime(latest_backup):
            print("[*] Bo qua: Khong co thay doi nao tren Database ke tu ban sao luu gan nhat.")
            return
            
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"raw_archive_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        shutil.copy2(db_file_path, backup_path)
        print(f"[SUCCESS] Da sao luu database thanh cong: {backup_name}")
        
        # Xoay vong giu lai toi da 5 ban
        backups.append(backup_path)
        while len(backups) > 5:
            try:
                oldest_backup = backups.pop(0)
                os.remove(oldest_backup)
                print(f"  - Da xoa ban sao luu cu: {os.path.basename(oldest_backup)}")
            except Exception as e_del:
                print(f"  [-] Khong the xoa ban cu: {e_del}")
    except Exception as e_copy:
        print(f"[-] Loi trong qua trinh copy tep: {e_copy}")

if __name__ == "__main__":
    main()
