import sqlite3
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    tk_id = '3d296527-12f8-4796-b759-c501ca421f6b'
    db_file = 'raw_archive_v2.db'
    
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # 1. Query listings_v2
    row_v2 = cur.execute('SELECT * FROM listings_v2 WHERE tk_id = ?', (tk_id,)).fetchone()
    if row_v2:
        print('=== LISTINGS_V2 ===')
        print(f"tk_id: {row_v2['tk_id']}")
        print(f"status: {row_v2['status']}")
        print(f"System_ID: {row_v2['System_ID']}")
        print(f"Ma_Hang: {row_v2['Ma_Hang']}")
        print(f"Mat_Tien: {row_v2['Mat_Tien']}")
        print(f"Chieu_dai: {row_v2['Chieu_dai']}")
        print(f"Last_Crawl: {row_v2['Last_Crawl']}")
        print(f"DT_Thuc_te: {row_v2['DT_Thuc_te']}")
        print(f"So_Tang: {row_v2['So_Tang']}")
        print(f"Duong: {row_v2['Duong']}")
        print(f"Quan: {row_v2['Quan']}")
        print(f"Phuong: {row_v2['Phuong']}")
        
        system_id = row_v2['System_ID']
        
        # 2. Query listings_custom_v2
        if system_id:
            row_custom = cur.execute('SELECT * FROM listings_custom_v2 WHERE System_ID = ?', (system_id,)).fetchone()
            if row_custom:
                print('\n=== LISTINGS_CUSTOM_V2 ===')
                print(f"System_ID: {row_custom['System_ID']}")
                print(f"Ma_Khang_Ngo: {row_custom['Ma_Khang_Ngo']}")
                print(f"Gia_Public: {row_custom['Gia_Public']}")
                print(f"Tieu_De_Public: {row_custom['Tieu_De_Public']}")
                print(f"Mat_Tien: {row_custom['Mat_Tien']}")
                print(f"Chieu_dai: {row_custom['Chieu_dai']}")
                print(f"Dia_Chi_That: {row_custom['Dia_Chi_That']}")
            else:
                print('\n=== LISTINGS_CUSTOM_V2: NOT FOUND ===')
        else:
            print('\n=== System_ID is NULL in listings_v2 ===')
            
        # 3. Query listings_images
        imgs = cur.execute('SELECT id, role, sequence_index, image_url, cloudinary_url FROM listings_images WHERE tk_id = ?', (tk_id,)).fetchall()
        print(f'\n=== LISTINGS_IMAGES ({len(imgs)} images) ===')
        for i, row in enumerate(imgs):
            print(f"#{i+1}: seq={row['sequence_index']} | role={row['role']} | img_url={row['image_url'][:60]}... | cloudinary={row['cloudinary_url']}")
            
    else:
        print(f"Listing ID {tk_id} not found in listings_v2.")
        
    conn.close()

if __name__ == '__main__':
    main()
