import sqlite3

def main():
    db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM listings WHERE tk_id = 'exufjy-mmp74lfx-3e20cf1c'")
    row = c.fetchone()
    if row:
        d = dict(row)
        print("So_do_thua_dat_1:", d.get("So_do_thua_dat_1"))
        print("raw_images_tk_json:", d.get("raw_images_tk_json"))
        print("Anh_1:", d.get("Anh_1"))
    else:
        print("Listing not found!")
    conn.close()

if __name__ == '__main__':
    main()
