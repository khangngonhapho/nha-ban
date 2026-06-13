import sqlite3
import shutil
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
    temp_db = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive_temp_read.db"
    
    try:
        shutil.copy2(db_file, temp_db)
    except Exception as e:
        print(f"Error copying database: {e}")
        return
        
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(listings)")
        cols = [col[1] for col in cursor.fetchall()]
        
        image_cols = [
            "Hinh_Nhan_Dien", "So_do_thua_dat_1", "So_do_thua_dat_2", "So_do_thua_dat_3", "So_do_thua_dat_4", "So_do_thua_dat_5",
            "Hinh_Mat_Tien", "Hinh_Hem_1", "Hinh_Hem_2", "Hinh_Hem_3", "Hinh_Hem_4", "Hinh_Hem_5",
            "Hinh_Hem_6", "Hinh_Hem_7", "Hinh_Hem_8", "Hinh_Hem_9", "Hinh_Hem_10",
            "Anh_1", "Anh_2", "Anh_3", "Anh_4", "Anh_5", "Anh_6", "Anh_7", "Anh_8", "Anh_9", "Anh_10",
            "Anh_11", "Anh_12", "Anh_13", "Anh_14", "Anh_15", "Anh_16", "Anh_17", "Anh_18", "Anh_19", "Anh_20",
            "Anh_21", "Anh_22", "Anh_23", "Anh_24", "Anh_25"
        ]
        active_cols = [c for c in image_cols if c in cols]
        
        cursor.execute(f"SELECT tk_id, {', '.join(active_cols)} FROM listings")
        rows = cursor.fetchall()
        
        cloudinary_count = 0
        r2_count = 0
        null_count = 0
        other_count = 0
        
        for r in rows:
            for val in r[1:]:
                if val is None or str(val).strip() == "":
                    null_count += 1
                elif "cloudinary.com" in str(val):
                    cloudinary_count += 1
                elif "r2.dev" in str(val):
                    r2_count += 1
                else:
                    other_count += 1
                    
        print(f"Total cells checked: {len(rows) * len(active_cols)}")
        print(f"Cloudinary cells: {cloudinary_count}")
        print(f"R2 cells: {r2_count}")
        print(f"Empty/Null cells: {null_count}")
        print(f"Other cells: {other_count}")
        conn.close()
    except Exception as e:
        print(f"Error querying copy: {e}")
    finally:
        if os.path.exists(temp_db):
            try:
                os.remove(temp_db)
            except Exception:
                pass

if __name__ == '__main__':
    main()
