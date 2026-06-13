import sqlite3

def main():
    db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("PRAGMA table_info(listings)")
    cols = [col[1] for col in c.fetchall()]
    image_cols = [col for col in cols if col.startswith("Anh_") or col.startswith("So_do_") or col.startswith("Hinh_")]
    
    total = 0
    print("Cloudinary columns remaining:")
    for col in image_cols:
        c.execute(f"SELECT COUNT(*) FROM listings WHERE `{col}` LIKE '%cloudinary.com%'")
        cnt = c.fetchone()[0]
        if cnt > 0:
            print(f"  - {col}: {cnt}")
            total += cnt
            
    print(f"Total Cloudinary cells in DB: {total}")
    conn.close()

if __name__ == '__main__':
    main()
