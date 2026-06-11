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
    
    tk_id = '3d296527-12f8-4796-b759-c501ca421f6b'
    
    # Query System_ID from listings_v2 first
    cursor.execute("SELECT System_ID FROM listings_v2 WHERE tk_id = ?", (tk_id,))
    row = cursor.fetchone()
    sys_id = row[0] if row else None
    
    print("Deleting records associated with tk_id='{}' (System_ID='{}') from {}...".format(tk_id, sys_id, db))
    
    # 1. Delete from listings_v2
    cursor.execute("DELETE FROM listings_v2 WHERE tk_id = ?", (tk_id,))
    deleted_listings_v2 = cursor.rowcount
    
    # 2. Delete from listings_custom_v2
    deleted_custom = 0
    if sys_id:
        cursor.execute("DELETE FROM listings_custom_v2 WHERE System_ID = ?", (sys_id,))
        deleted_custom = cursor.rowcount
    
    # 3. Delete from listings_images
    cursor.execute("DELETE FROM listings_images WHERE tk_id = ?", (tk_id,))
    deleted_images = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print("Successfully deleted:")
    print("  - {} row(s) from listings_v2".format(deleted_listings_v2))
    print("  - {} row(s) from listings_custom_v2".format(deleted_custom))
    print("  - {} row(s) from listings_images".format(deleted_images))

if __name__ == "__main__":
    main()
