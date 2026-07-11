import os
import sqlite3

def recover_data():
    backup_db = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive (1).db"
    active_db = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
    
    if not os.path.exists(backup_db):
        print(f"[-] Khong tim thay ban sao luu cu tai: {backup_db}")
        return
        
    print(f"[*] Dang phuc hoi cot raw_json_full tu {backup_db} sang {active_db}...")
    
    conn_b = sqlite3.connect(backup_db)
    cursor_b = conn_b.cursor()
    
    # Lấy các listings có raw_json_full
    rows = cursor_b.execute("SELECT tk_id, raw_json_full FROM listings WHERE raw_json_full IS NOT NULL AND raw_json_full != ''").fetchall()
    conn_b.close()
    
    print(f"  - Phat hien {len(rows)} can co chua raw_json_full trong ban backup.")
    
    conn_a = sqlite3.connect(active_db)
    cursor_a = conn_a.cursor()
    
    updated_count = 0
    for tk_id, raw_json in rows:
        # Kiểm tra xem căn này có tồn tại trong CSDL hiện tại hay không
        exists = cursor_a.execute("SELECT tk_id FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
        if exists:
            # Chỉ ghi đè nếu cột raw_json_full hiện tại đang trống hoặc NULL
            current_raw = cursor_a.execute("SELECT raw_json_full FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
            if not current_raw or not current_raw[0]:
                cursor_a.execute("UPDATE listings SET raw_json_full = ? WHERE tk_id = ?", (raw_json, tk_id))
                updated_count += 1
                
    conn_a.commit()
    conn_a.close()
    
    print(f"[+] Hoan tat cuu ho: Da dap lai du lieu API tho cho {updated_count}/{len(rows)} can thanh cong!")

if __name__ == "__main__":
    recover_data()
