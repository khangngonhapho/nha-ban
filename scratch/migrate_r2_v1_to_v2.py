# scratch/migrate_r2_v1_to_v2.py
import sys
import os
import sqlite3
import json
import requests
import hashlib
import hmac
import datetime
import urllib.parse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manager

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_signature_key(key, date_stamp, region_name, service_name):
    k_date = hmac.new(("AWS4" + key).encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    k_signing = sign(k_service, "aws4_request")
    return k_signing

def copy_r2_object(cfg, src_key, dest_key):
    """Sao chép đối tượng nội bộ R2 bằng REST API CopyObject và Signature V4"""
    r2_access_key = cfg.get("r2_access_key_id")
    r2_secret_key = cfg.get("r2_secret_access_key")
    r2_bucket = cfg.get("r2_bucket_name")
    account_id = cfg.get("cloudflare_account_id")
    
    host = f"{r2_bucket}.{account_id}.r2.cloudflarestorage.com"
    endpoint = f"https://{host}"
    
    # URL encode destination path
    # In S3 CopyObject, x-amz-copy-source must be URL encoded: /bucket/source_key
    src_source_val = f"/{r2_bucket}/{urllib.parse.quote(src_key)}"
    
    encoded_dest_key = urllib.parse.quote(dest_key, safe="/")
    path = f"/{encoded_dest_key}"
    
    t = datetime.datetime.now(datetime.UTC)
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    # Payload is empty
    hashed_payload = hashlib.sha256(b"").hexdigest()
    
    canonical_headers = (
        f"host:{host}\n"
        f"x-amz-content-sha256:{hashed_payload}\n"
        f"x-amz-copy-source:{src_source_val}\n"
        f"x-amz-date:{amz_date}\n"
    )
    signed_headers = "host;x-amz-content-sha256;x-amz-copy-source;x-amz-date"
    
    canonical_request = f"PUT\n{path}\n\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    algorithm = "AWS4-HMAC-SHA256"
    region = "auto"
    service = "s3"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"
    
    signing_key = get_signature_key(r2_secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    authorization_header = f"{algorithm} Credential={r2_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    url = f"{endpoint}{path}"
    headers = {
        'Host': host,
        'Authorization': authorization_header,
        'x-amz-date': amz_date,
        'x-amz-content-sha256': hashed_payload,
        'x-amz-copy-source': src_source_val
    }
    
    r = requests.put(url, headers=headers, timeout=20)
    if r.status_code != 200:
        print(f"    [❌ Copy Error] {src_key} -> {dest_key}: {r.status_code} - {r.text}")
        return False
    return True

def delete_r2_object(cfg, key):
    """Xóa đối tượng trên R2 bằng REST API DELETE và Signature V4"""
    r2_access_key = cfg.get("r2_access_key_id")
    r2_secret_key = cfg.get("r2_secret_access_key")
    r2_bucket = cfg.get("r2_bucket_name")
    account_id = cfg.get("cloudflare_account_id")
    
    host = f"{r2_bucket}.{account_id}.r2.cloudflarestorage.com"
    endpoint = f"https://{host}"
    encoded_key = urllib.parse.quote(key, safe="/")
    path = f"/{encoded_key}"
    
    t = datetime.datetime.now(datetime.UTC)
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    hashed_payload = hashlib.sha256(b"").hexdigest()
    
    canonical_headers = f"host:{host}\nx-amz-content-sha256:{hashed_payload}\nx-amz-date:{amz_date}\n"
    signed_headers = "host;x-amz-content-sha256;x-amz-date"
    
    canonical_request = f"DELETE\n{path}\n\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    algorithm = "AWS4-HMAC-SHA256"
    region = "auto"
    service = "s3"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"
    
    signing_key = get_signature_key(r2_secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    authorization_header = f"{algorithm} Credential={r2_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    url = f"{endpoint}{path}"
    headers = {
        'Host': host,
        'Authorization': authorization_header,
        'x-amz-date': amz_date,
        'x-amz-content-sha256': hashed_payload
    }
    
    r = requests.delete(url, headers=headers, timeout=20)
    if r.status_code not in [200, 204]:
        print(f"    [❌ Delete Error] {key}: {r.status_code} - {r.text}")
        return False
    return True

def migrate_all_r2_listings():
    print("=== STARTING R2 V1 TO V2 MIGRATION UTILITY ===")
    conn = sqlite3.connect(manager.DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listings WHERE status NOT IN ('deleted', 'sold')")
    rows = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(rows)} active listings in SQLite to check.")
    
    cfg = manager.load_config()
    r2_public_url = cfg.get("r2_public_url", "")
    r2_migration_prefix = cfg.get("r2_migration_prefix", "BDS-KhangNgo-v2") or "BDS-KhangNgo-v2"
    
    migrated_count = 0
    
    for row in rows:
        tk_id = row["tk_id"]
        
        # Parse image mappings
        images_mapping_json = row["images_mapping_json"]
        manual_images_json = row["manual_images_json"]
        curated_config_json = row["curated_config_json"]
        
        try:
            images_mapping = json.loads(images_mapping_json) if images_mapping_json else {}
        except Exception:
            images_mapping = {}
            
        try:
            manual_images = json.loads(manual_images_json) if manual_images_json else []
        except Exception:
            manual_images = []
            
        try:
            curated_config = json.loads(curated_config_json) if curated_config_json else {}
        except Exception:
            curated_config = {}
            
        # Check if this listing actually has any old R2 urls (containing /BDS-KhangNgo/)
        has_old_urls = False
        
        # Check in mapping
        for orig, migrated in list(images_mapping.items()):
            if migrated and "/BDS-KhangNgo/" in migrated and "/BDS-KhangNgo-v2/" not in migrated:
                has_old_urls = True
                break
                
        # Check in manual images
        for manual in manual_images:
            if manual and "/BDS-KhangNgo/" in manual and "/BDS-KhangNgo-v2/" not in manual:
                has_old_urls = True
                break
                
        if not has_old_urls:
            continue
            
        # Calculate destination subfolder name
        r2_subfolder = manager.get_r2_subfolder(tk_id, dict(row))
        print(f"\n[+] Migrating listing {tk_id} ({row['Ngo_So_nha']} {row['Duong']}) -> '{r2_subfolder}'")
        
        new_images_mapping = {}
        new_manual_images = []
        
        # 1. Migrate image mappings (crawled images)
        for orig, migrated in images_mapping.items():
            if migrated and "/BDS-KhangNgo/" in migrated and "/BDS-KhangNgo-v2/" not in migrated:
                # Extract old key
                # Example url: https://pub-xxx.r2.dev/BDS-KhangNgo/img_xxx.jpg
                parsed_url = urllib.parse.urlparse(migrated)
                old_key = parsed_url.path.lstrip("/") # Remove leading /
                filename = old_key.split("/")[-1]
                new_key = f"{r2_migration_prefix}/{r2_subfolder}/{filename}"
                
                print(f"  - Copying: {old_key} -> {new_key}")
                if copy_r2_object(cfg, old_key, new_key):
                    new_url = f"{r2_public_url}/{new_key}"
                    new_images_mapping[orig] = new_url
                    # Delete old
                    delete_r2_object(cfg, old_key)
                else:
                    new_images_mapping[orig] = migrated
            else:
                new_images_mapping[orig] = migrated
                
        # 2. Migrate manual images
        for manual in manual_images:
            if manual and "/BDS-KhangNgo/" in manual and "/BDS-KhangNgo-v2/" not in manual:
                parsed_url = urllib.parse.urlparse(manual)
                old_key = parsed_url.path.lstrip("/")
                filename = old_key.split("/")[-1]
                new_key = f"{r2_migration_prefix}/{r2_subfolder}/{filename}"
                
                print(f"  - Copying manual: {old_key} -> {new_key}")
                if copy_r2_object(cfg, old_key, new_key):
                    new_url = f"{r2_public_url}/{new_key}"
                    new_manual_images.append(new_url)
                    # Delete old
                    delete_r2_object(cfg, old_key)
                else:
                    new_manual_images.append(manual)
            else:
                new_manual_images.append(manual)
                
        # 3. Update curated_config images list with new URLs
        rebuilt_images_list = []
        curated_images = curated_config.get("images", [])
        for img in curated_images:
            if not isinstance(img, dict):
                continue
            url = img.get("url")
            role = img.get("role")
            visible = img.get("visible", True)
            
            # Map old url to new url
            new_url = url
            # Search in crawled image mapping
            for orig, R2 in images_mapping.items():
                if R2 == url and orig in new_images_mapping:
                    new_url = new_images_mapping[orig]
                    break
                    
            # Search in manual images
            if url in manual_images:
                try:
                    idx = manual_images.index(url)
                    new_url = new_manual_images[idx]
                except ValueError:
                    pass
                    
            rebuilt_images_list.append({
                "url": new_url,
                "role": role,
                "visible": visible
            })
            
        new_curated_config = {
            "images": rebuilt_images_list,
            "Mã_Khang_Ngô__ID_": curated_config.get("Mã_Khang_Ngô__ID_", "")
        }
        
        # Build admin and public json
        admin_json_str, public_json_str = manager.rebuild_admin_public_images_json(new_curated_config, new_manual_images)
        
        # Extract flat lists for column updates
        flat_sodo = []
        flat_hem = []
        flat_anh = []
        parsed_admin = json.loads(admin_json_str)
        for img in parsed_admin:
            url = img.get("r2_url") or img.get("image_url") or ""
            if not url:
                continue
            role = img.get("role")
            if role == "diagram":
                flat_sodo.append(url)
            elif role == "alley":
                flat_hem.append(url)
            else:
                flat_anh.append(url)
                
        clean_sodo1 = flat_sodo[0] if len(flat_sodo) > 0 else ""
        clean_sodo2 = flat_sodo[1] if len(flat_sodo) > 1 else ""
        clean_sodo3 = flat_sodo[2] if len(flat_sodo) > 2 else ""
        clean_sodo4 = flat_sodo[3] if len(flat_sodo) > 3 else ""
        clean_sodo5 = flat_sodo[4] if len(flat_sodo) > 4 else ""
        
        first_property_r2 = ""
        for img in parsed_admin:
            if img.get("role") == "facade":
                first_property_r2 = img.get("r2_url") or img.get("image_url")
                break
                
        hinh_mat_tien = first_property_r2
        
        # Save to SQLite
        conn_db = sqlite3.connect(manager.DB_FILE)
        cursor_db = conn_db.cursor()
        
        cursor_db.execute(f"PRAGMA table_info({manager.LISTINGS_TABLE})")
        db_cols = {r[1] for r in cursor_db.fetchall()}
        
        update_fields = {
            "images_mapping_json": json.dumps(new_images_mapping, ensure_ascii=False),
            "manual_images_json": json.dumps(new_manual_images, ensure_ascii=False),
            "curated_config_json": json.dumps(new_curated_config, ensure_ascii=False),
            "images_admin_json": admin_json_str,
            "images_public_json": public_json_str
        }
        
        col_sodo1 = manager.get_safe_col_name("Sơ đồ thửa đất 1")
        col_sodo2 = manager.get_safe_col_name("Sơ đồ thửa đất 2")
        col_sodo3 = manager.get_safe_col_name("Sơ đồ thửa đất 3")
        col_sodo4 = manager.get_safe_col_name("Sơ đồ thửa đất 4")
        col_sodo5 = manager.get_safe_col_name("Sơ đồ thửa đất 5")
        col_mat_tien = manager.get_safe_col_name("Hình Mặt Tiền")
        
        if col_sodo1 in db_cols: update_fields[col_sodo1] = clean_sodo1
        if col_sodo2 in db_cols: update_fields[col_sodo2] = clean_sodo2
        if col_sodo3 in db_cols: update_fields[col_sodo3] = clean_sodo3
        if col_sodo4 in db_cols: update_fields[col_sodo4] = clean_sodo4
        if col_sodo5 in db_cols: update_fields[col_sodo5] = clean_sodo5
        if col_mat_tien in db_cols: update_fields[col_mat_tien] = hinh_mat_tien
        
        # Add Ảnh 1 to Ảnh 25
        for i in range(25):
            col_name = manager.get_safe_col_name(f"Ảnh {i+1}")
            if col_name in db_cols:
                update_fields[col_name] = flat_anh[i] if i < len(flat_anh) else ""
                
        # Add Hình Hẻm 1 to 10
        for i in range(10):
            col_name = manager.get_safe_col_name(f"Hình Hẻm {i+1}")
            if col_name in db_cols:
                update_fields[col_name] = flat_hem[i] if i < len(flat_hem) else ""
                
        valid_updates = {k: v for k, v in update_fields.items() if k in db_cols}
        sql_parts = [f"`{k}` = ?" for k in valid_updates.keys()]
        sql_vals = list(valid_updates.values())
        sql_vals.append(tk_id)
        
        cursor_db.execute(
            f"UPDATE {manager.LISTINGS_TABLE} SET {', '.join(sql_parts)} WHERE tk_id = ?",
            sql_vals
        )
        conn_db.commit()
        conn_db.close()
        
        print("  -> SQLite updated with migrated subfolder URLs.")
        
        # Sync to Sheets
        try:
            manager.execute_publish_listing(tk_id)
            print("  -> Synced to Google Sheets successfully.")
        except Exception as e_sync:
            print(f"  -> Sheets sync failed: {str(e_sync)}")
            
        migrated_count += 1
        
    print(f"\n=== MIGRATION UTILITY FINISHED: Migrated {migrated_count} listings ===")

if __name__ == "__main__":
    migrate_all_r2_listings()
