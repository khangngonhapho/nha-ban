import sqlite3
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_db = "Backup DB/raw_archiveJun30-4.30PM.db"
target_dbs = ["raw_archive.db", "raw_archive_staging.db"]

if not os.path.exists(backup_db):
    print(f"Error: Backup database {backup_db} not found.")
    sys.exit(1)

print(f"Reading original crawl images from backup {backup_db}...")
conn_bak = sqlite3.connect(backup_db)
cursor_bak = conn_bak.cursor()

# Get all listings from backup
cursor_bak.execute("SELECT tk_id, raw_images_tk_json, images_mapping_json, System_ID FROM listings")
bak_data = {}
for row in cursor_bak.fetchall():
    tk_id, raw_json, mapping_json, sys_id = row
    bak_data[tk_id] = {
        "raw_json": raw_json,
        "mapping_json": mapping_json,
        "sys_id": sys_id
    }
conn_bak.close()

print(f"Loaded {len(bak_data)} listings from backup.")

for db_path in target_dbs:
    if not os.path.exists(db_path):
        print(f"Target database {db_path} not found. Skipping.")
        continue
        
    print(f"\nProcessing target database: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table and columns exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings'")
    if not cursor.fetchone():
        print("  - Table 'listings' not found.")
        conn.close()
        continue
        
    cursor.execute("PRAGMA table_info(listings)")
    cols = {row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT tk_id, raw_images_tk_json, System_ID FROM listings")
    target_listings = cursor.fetchall()
    
    updated_count = 0
    
    for tk_id, curr_json, sys_id in target_listings:
        if tk_id not in bak_data:
            continue
            
        bak = bak_data[tk_id]
        if not bak["raw_json"]:
            continue
            
        try:
            bak_raw_list = json.loads(bak["raw_json"])
        except Exception:
            continue
            
        try:
            curr_list = json.loads(curr_json) if curr_json else []
        except Exception:
            curr_list = []
            
        if len(bak_raw_list) <= len(curr_list):
            continue
            
        # Parse mapping if available
        mapping = {}
        if bak["mapping_json"]:
            try:
                mapping = json.loads(bak["mapping_json"])
            except Exception:
                pass
                
        # Translate backup Cloudfront URLs to R2 URLs
        translated_urls = []
        for url in bak_raw_list:
            clean_url = url.strip()
            # If mapped to R2, use it
            if clean_url in mapping and mapping[clean_url]:
                translated_urls.append(mapping[clean_url].strip())
            else:
                translated_urls.append(clean_url)
                
        # Deduplicate while preserving order
        seen = set()
        final_urls = []
        for url in translated_urls:
            if url not in seen:
                seen.add(url)
                final_urls.append(url)
                
        # Write to SQLite
        final_json_str = json.dumps(final_urls, ensure_ascii=False)
        cursor.execute(
            "UPDATE listings SET raw_images_tk_json = ?, raw_drive_images_json = ? WHERE tk_id = ?",
            (final_json_str, final_json_str, tk_id)
        )
        
        # Also update listings_images table if it exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings_images'")
        if cursor.fetchone():
            cursor.execute("DELETE FROM listings_images WHERE tk_id = ? AND origin = 'crawl'", (tk_id,))
            for seq_idx, url in enumerate(final_urls):
                # Classify role
                role = "interior"
                if "sodo" in url.lower() or "so-do" in url.lower() or "diagram" in url.lower():
                    role = "diagram"
                elif "mat-tien" in url.lower() or "facade" in url.lower():
                    role = "facade"
                    
                cursor.execute("""
                    INSERT INTO listings_images (tk_id, system_id, image_url, r2_url, role, sequence_index, origin, is_hidden)
                    VALUES (?, ?, ?, ?, ?, ?, 'crawl', 1)
                """, (tk_id, sys_id or bak["sys_id"] or "", url, url, role, seq_idx, ))
                
        updated_count += 1
        
    conn.commit()
    conn.close()
    print(f"  - Successfully restored full crawl images for {updated_count} listings in {db_path}!")

print("\nDone!")
