import sqlite3
import os
import requests
import json
import re
import sys
import datetime
import hmac
import hashlib
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Load settings
config_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/settings.json"
if not os.path.exists(config_file):
    print("settings.json not found!")
    sys.exit(1)

with open(config_file, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

r2_access_key = cfg.get("r2_access_key_id")
r2_secret_key = cfg.get("r2_secret_access_key")
r2_bucket = cfg.get("r2_bucket_name")
account_id = cfg.get("cloudflare_account_id")
r2_public_url = cfg.get("r2_public_url")
db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"

if not (r2_access_key and r2_secret_key and r2_bucket and account_id and r2_public_url):
    print("Error: Cloudflare R2 credentials or public URL are missing in settings.json!")
    sys.exit(1)

db_lock = threading.Lock()

def upload_image_to_r2(file_content, filename, content_type="image/jpeg"):
    host = f"{r2_bucket}.{account_id}.r2.cloudflarestorage.com"
    key = f"BDS-KhangNgo/{filename}"
    path = f"/{key}"
    
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    hashed_payload = hashlib.sha256(file_content).hexdigest()
    canonical_headers = f"host:{host}\nx-amz-content-sha256:{hashed_payload}\nx-amz-date:{amz_date}\n"
    signed_headers = "host;x-amz-content-sha256;x-amz-date"
    
    canonical_request = f"PUT\n{path}\n\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    algorithm = "AWS4-HMAC-SHA256"
    region = "auto"
    service = "s3"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"
    
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = hmac.new(("AWS4" + key).encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = sign(k_date, region_name)
        k_service = sign(k_region, service_name)
        k_signing = sign(k_service, "aws4_request")
        return k_signing
        
    signing_key = get_signature_key(r2_secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    authorization_header = f"{algorithm} Credential={r2_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    url = f"https://{host}{path}"
    headers = {
        'Host': host,
        'Authorization': authorization_header,
        'x-amz-date': amz_date,
        'x-amz-content-sha256': hashed_payload,
        'Content-Type': content_type
    }
    
    r = requests.put(url, data=file_content, headers=headers, timeout=30)
    if r.status_code != 200:
        raise Exception(f"R2 PUT failed with status {r.status_code}: {r.text}")
        
    return f"{r2_public_url}/BDS-KhangNgo/{filename}"

def extract_cloudinary_filename_and_tk_id(url):
    parsed = urlparse(url)
    path = parsed.path
    parts = path.split('/')
    
    filename = parts[-1]
    tk_id = ""
    
    if "BDS-KhangNgo" in parts:
        idx = parts.index("BDS-KhangNgo")
        if idx + 2 < len(parts):
            tk_id = parts[idx+1]
            
    return filename, tk_id

def process_single_row(r, active_cols, local_dir, local_files_cache, pool_lego):
    lid, tk_id, duyet_public = r[0], r[1], r[2]
    col_values = r[3:-1]
    raw_images_tk_json = r[-1]
    
    # Check if this row has Cloudinary images
    row_has_cld = False
    col_data = {}
    for idx, col_val in enumerate(col_values):
        col_name = active_cols[idx]
        if col_val and "cloudinary.com" in str(col_val):
            col_data[col_name] = str(col_val)
            row_has_cld = True
            
    if not row_has_cld:
        return False, 0
        
    print(f"[{threading.current_thread().name}] Processing listing: {tk_id}...")
    
    updated_fields = {}
    images_migrated_for_row = 0
    
    # Migrate images
    for col_name, old_url in col_data.items():
        filename, folder_tk_id = extract_cloudinary_filename_and_tk_id(old_url)
        safe_folder = folder_tk_id if folder_tk_id else tk_id
        r2_filename = f"{safe_folder}_{filename}" if safe_folder else filename
        
        migrated_url = None
        
        # Local dir check
        if local_dir and os.path.exists(local_dir):
            local_file_path = local_files_cache.get(filename)
            if local_file_path and os.path.exists(local_file_path):
                try:
                    with open(local_file_path, 'rb') as f:
                        file_content = f.read()
                    migrated_url = upload_image_to_r2(file_content, r2_filename)
                except Exception as e:
                    print(f"    [{tk_id}] Error uploading local file {filename}: {e}")
                    
        # API check
        if not migrated_url:
            try:
                res = requests.get(old_url, timeout=15)
                if res.status_code == 200:
                    file_content = res.content
                    migrated_url = upload_image_to_r2(file_content, r2_filename)
                else:
                    print(f"    [{tk_id}] Failed to download {filename} (HTTP {res.status_code})")
            except Exception as e:
                print(f"    [{tk_id}] Error downloading via API: {e}")
                
        if migrated_url:
            updated_fields[col_name] = migrated_url
            images_migrated_for_row += 1
            
    if updated_fields:
        # Acquire Lock to safely write to SQLite and sync Sheets
        with db_lock:
            try:
                conn = sqlite3.connect(db_file, timeout=60.0)
                c = conn.cursor()
                c.execute("PRAGMA journal_mode=WAL")
                c.execute("PRAGMA synchronous=OFF")
                
                # Update listings columns
                set_parts = [f"`{k}` = ?" for k in updated_fields.keys()]
                vals = list(updated_fields.values())
                vals.append(tk_id)
                c.execute(f"UPDATE listings SET {', '.join(set_parts)} WHERE tk_id = ?", vals)
                conn.commit()
                
                # Update raw_images_tk_json
                if raw_images_tk_json and "cloudinary.com" in raw_images_tk_json:
                    try:
                        urls = json.loads(raw_images_tk_json)
                        updated_urls = []
                        for u in urls:
                            matched = False
                            for col_name, old_url in col_data.items():
                                if u == old_url and col_name in updated_fields:
                                    updated_urls.append(updated_fields[col_name])
                                    matched = True
                                    break
                            if not matched:
                                updated_urls.append(u)
                        c.execute("UPDATE listings SET raw_images_tk_json = ? WHERE tk_id = ?", (json.dumps(updated_urls), tk_id))
                        conn.commit()
                    except Exception as e:
                        print(f"    [{tk_id}] Error updating JSON list: {e}")
                        
                conn.close()
                print(f"  [{tk_id}] SQLite database successfully updated!")
            except Exception as e:
                print(f"    [{tk_id}] SQLite update failed: {e}")
                
            # Trigger Sheets sync if live
            if pool_lego and str(duyet_public).upper() == 'TRUE':
                try:
                    print(f"  [{tk_id}] Syncing to Google Sheets...")
                    def mock_log(msg):
                        print(f"    [{tk_id} Sheets] {msg}")
                    res = pool_lego.publish_listing_pool2(tk_id, pool_lego.get_google_credentials, lambda: cfg, mock_log, db_file=db_file)
                    print(f"    [{tk_id} Sheets] Sync result: {res}")
                except Exception as e:
                    print(f"    [{tk_id}] Sheets sync failed: {e}")
            else:
                if pool_lego and str(duyet_public).upper() != 'TRUE':
                    print(f"  [{tk_id}] Skipping Sheets sync (archived).")
                    
        return True, images_migrated_for_row
    else:
        return False, 0

def migrate_listings(local_dir=None, migrate_all=False):
    if not os.path.exists(db_file):
        print(f"Database file not found at {db_file}")
        return
        
    conn = sqlite3.connect(db_file, timeout=30.0)
    c = conn.cursor()
    
    # Check if pool_lego.py can be loaded to publish listings
    sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
    try:
        import pool_lego
        print("Successfully loaded pool_lego for publishing!")
    except Exception as e:
        print(f"Warning: Could not load pool_lego: {e}. Listings will only be updated in SQLite.")
        pool_lego = None
        
    # Get image columns
    c.execute("PRAGMA table_info(listings)")
    cols = [col[1] for col in c.fetchall()]
    image_cols = [
        "Hinh_Nhan_Dien", "So_do_thua_dat_1", "So_do_thua_dat_2", "So_do_thua_dat_3", "So_do_thua_dat_4", "So_do_thua_dat_5",
        "Hinh_Mat_Tien", "Hinh_Hem_1", "Hinh_Hem_2", "Hinh_Hem_3", "Hinh_Hem_4", "Hinh_Hem_5",
        "Hinh_Hem_6", "Hinh_Hem_7", "Hinh_Hem_8", "Hinh_Hem_9", "Hinh_Hem_10",
        "Anh_1", "Anh_2", "Anh_3", "Anh_4", "Anh_5", "Anh_6", "Anh_7", "Anh_8", "Anh_9", "Anh_10",
        "Anh_11", "Anh_12", "Anh_13", "Anh_14", "Anh_15", "Anh_16", "Anh_17", "Anh_18", "Anh_19", "Anh_20",
        "Anh_21", "Anh_22", "Anh_23", "Anh_24", "Anh_25"
    ]
    active_cols = [col for col in image_cols if col in cols]
    
    # Select listings based on migrate_all flag
    if migrate_all:
        c.execute(f"SELECT id, tk_id, Duyet_Public, {', '.join(active_cols)}, raw_images_tk_json FROM listings")
        print("Mode: Migrating ALL listings in database.")
    else:
        c.execute(f"SELECT id, tk_id, Duyet_Public, {', '.join(active_cols)}, raw_images_tk_json FROM listings WHERE Duyet_Public = 'TRUE'")
        print("Mode: Migrating ONLY live listings (Duyet_Public = 'TRUE').")
        
    rows = c.fetchall()
    conn.close() # Close main connection so threads can open their own
    print(f"Found {len(rows)} listings to migrate.")
    
    # Cache local files recursively to avoid extremely slow nested os.walk lookups
    local_files_cache = {}
    if local_dir and os.path.exists(local_dir):
        print(f"Building local files cache from {local_dir}...")
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_files_cache[file] = os.path.join(root, file)
        print(f"Cached {len(local_files_cache)} local files.")
        
    success_count = 0
    total_images_migrated = 0
    
    # Use ThreadPoolExecutor to run in parallel
    max_workers = 50 # 50 threads to download/upload in parallel
    print(f"Starting ThreadPoolExecutor with {max_workers} threads...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single_row, r, active_cols, local_dir, local_files_cache, pool_lego) for r in rows]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                is_updated, img_count = future.result()
                if is_updated:
                    success_count += 1
                    total_images_migrated += img_count
            except Exception as e:
                print(f"Thread task generated an exception: {e}")
                
    print(f"\n=========================================")
    print(f"Migration completed!")
    print(f"Total listings successfully updated: {success_count} / {len(rows)}")
    print(f"Total image files uploaded to R2: {total_images_migrated}")
    print(f"=========================================")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Migrate listings images from Cloudinary to Cloudflare R2")
    parser.add_argument("--local-dir", help="Path to local folder containing downloaded Cloudinary images")
    parser.add_argument("--all", action="store_true", help="Migrate ALL listings in database instead of only live ones")
    args = parser.parse_args()
    
    migrate_listings(local_dir=args.local_dir, migrate_all=args.all)
