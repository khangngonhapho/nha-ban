import sqlite3

def main():
    db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("PRAGMA table_info(listings)")
    cols = [col[1] for col in c.fetchall()]
    image_cols = [col for col in cols if col.startswith("Anh_") or col.startswith("So_do_") or col.startswith("Hinh_")]
    
    total_r2 = 0
    total_cld = 0
    total_empty = 0
    
    for col in image_cols:
        c.execute(f"SELECT COUNT(*) FROM listings WHERE `{col}` LIKE '%r2.dev%'")
        r2_cnt = c.fetchone()[0]
        total_r2 += r2_cnt
        
        c.execute(f"SELECT COUNT(*) FROM listings WHERE `{col}` LIKE '%cloudinary.com%'")
        cld_cnt = c.fetchone()[0]
        total_cld += cld_cnt
        
        c.execute(f"SELECT COUNT(*) FROM listings WHERE `{col}` IS NULL OR `{col}` = ''")
        empty_cnt = c.fetchone()[0]
        total_empty += empty_cnt
        
    print(f"Total image columns: {len(image_cols)}")
    print(f"Total R2 cells in DB: {total_r2}")
    print(f"Total Cloudinary cells in DB: {total_cld}")
    print(f"Total Empty cells in DB: {total_empty}")
    conn.close()

if __name__ == '__main__':
    main()
