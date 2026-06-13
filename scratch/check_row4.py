import sqlite3
import sys

def main():
    db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT So_do_thua_dat_1, Anh_1, raw_images_tk_json FROM listings WHERE tk_id = 'f11wg2-mlheid3v-9bd45312'")
    row = c.fetchone()
    if row:
        print("So_do_thua_dat_1:", row[0])
        print("Anh_1:", row[1])
        print("raw_images_tk_json:", row[2])
    else:
        print("Listing not found!")
    conn.close()

if __name__ == '__main__':
    main()
