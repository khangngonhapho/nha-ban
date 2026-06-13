# -*- coding: utf-8 -*-
import sqlite3
import os
import sys

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    db = "raw_archive_v2.db"
    if not os.path.exists(db):
        print(f"Database {db} does not exist.")
        return

    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    # Check listings_v2
    row = cursor.execute("SELECT tk_id, System_ID, status, Ngo_So_nha, streetName, Quan, Phuong FROM listings_v2 WHERE tk_id = '3d296527-12f8-4796-b759-c501ca421f6b'").fetchone()
    print("listings_v2 details:")
    print(row)
    
    # Check listings_custom_v2
    if row:
        sys_id = row[1]
        custom_row = cursor.execute("SELECT System_ID, Ma_Khang_Ngo, Gia_Public, Tieu_De_Public FROM listings_custom_v2 WHERE System_ID = ?", (sys_id,)).fetchone()
        print("listings_custom_v2 details:")
        print(custom_row)
        
    # Check listings_images
    images = cursor.execute("SELECT id, tk_id, image_url, role, sequence_index FROM listings_images WHERE tk_id = '3d296527-12f8-4796-b759-c501ca421f6b'").fetchall()
    print("listings_images details (count = {}):".format(len(images)))
    for img in images[:5]:
        print(img)
    if len(images) > 5:
        print("...")
        
    conn.close()

if __name__ == "__main__":
    main()
