import sys
import os
import shutil
import sqlite3
import json
import gspread
from gspread.utils import rowcol_to_a1

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manager import get_google_credentials, load_config

def clear_sqlite_production():
    print("=== [1/4] RESETTING SQLITE PRODUCTION DATABASE ===")
    from core.db import get_db_file
    
    # Ensure STAGING env var is not set to resolve prod DB path
    old_staging_env = os.environ.get("STAGING")
    if "STAGING" in os.environ:
        del os.environ["STAGING"]
    prod_db = get_db_file()
    
    # Set STAGING to resolve staging DB path
    os.environ["STAGING"] = "true"
    staging_db = get_db_file()
    
    # Restore environment variable
    if old_staging_env is not None:
        os.environ["STAGING"] = old_staging_env
    else:
        if "STAGING" in os.environ:
            del os.environ["STAGING"]
            
    print(f"  - Production DB: {prod_db}")
    print(f"  - Staging DB: {staging_db}")
    
    if not os.path.exists(staging_db):
        print(f"[❌ ERROR] Staging database '{staging_db}' not found! Cannot copy structure.")
        sys.exit(1)
        
    # Delete production database files
    files_to_delete = [
        prod_db,
        f"{prod_db}-wal",
        f"{prod_db}-shm",
        f"{prod_db}-journal"
    ]
    for f in files_to_delete:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"  - Deleted old file: {f}")
            except Exception as e:
                print(f"  - [⚠️ WARNING] Could not delete {f}: {e}")
                
    # Copy staging database to production database
    try:
        shutil.copyfile(staging_db, prod_db)
        print(f"  - Copied structure from '{staging_db}' to '{prod_db}'")
    except Exception as e:
        print(f"[❌ ERROR] Failed to copy structure: {e}")
        sys.exit(1)
        
    # Clear tables in production database
    try:
        conn = sqlite3.connect(prod_db)
        cursor = conn.cursor()
        
        tables_to_clear = [
            "listings",
            "listings_images",
            "crawl_sessions",
            "customer_profiles",
            "shared_links",
            "phone_blacklist",
            "exclusion_filters"
        ]
        
        for table in tables_to_clear:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  - Truncated table: {table}")
            
        conn.commit()
        conn.close()
        print("[✅] SQLite production database is now empty and initialized.")
    except Exception as e:
        print(f"[❌ ERROR] Failed to truncate tables in production database: {e}")
        sys.exit(1)

def clear_sheets_production():
    print("\n=== [2/4] RESETTING GOOGLE SHEETS PRODUCTION ===")
    
    creds = get_google_credentials()
    if not creds:
        print("[❌ ERROR] Google OAuth credentials not found.")
        sys.exit(1)
        
    client = gspread.authorize(creds)
    cfg = load_config()
    
    prod_sheets = {
        "Production Pool": {
            "id": cfg.get("sheet_id") or "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw",
            "configs": [
                {"tab": "Pool", "header_rows": 1},
                {"tab": "Pool_Images", "header_rows": 1}
            ]
        },
        "Production Source": {
            "id": "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE",
            "configs": [
                {"tab": "Source", "header_rows": 2}
            ]
        },
        "Production Public": {
            "id": "1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0",
            "configs": [
                {"tab": "Public", "header_rows": 2, "preserve_a3_formula": True}
            ]
        }
    }
    
    for sheet_name, sheet_info in prod_sheets.items():
        sheet_id = sheet_info["id"]
        configs = sheet_info["configs"]
        print(f"\nProcessing {sheet_name} (ID: {sheet_id})...")
        
        try:
            ss = client.open_by_key(sheet_id)
            print(f"Opened spreadsheet: '{ss.title}'")
            
            for config in configs:
                tab_name = config["tab"]
                header_rows = config["header_rows"]
                preserve_a3 = config.get("preserve_a3_formula", False)
                
                try:
                    ws = ss.worksheet(tab_name)
                    print(f"  - Worksheet '{tab_name}': header_rows={header_rows}")
                    
                    if preserve_a3:
                        # For Public tab, resize to 3 rows, clear B3:DZ3 to preserve cell A3 formula!
                        print(f"    * Resizing '{tab_name}' to 3 rows...")
                        ws.resize(rows=3)
                        col_count = ws.col_count
                        last_col_letter = rowcol_to_a1(3, col_count).replace("3", "")
                        range_str = f"B3:{last_col_letter}3"
                        print(f"    * Clearing other cells in row 3 (range: {range_str})...")
                        ws.batch_clear([range_str])
                        print(f"    [✅] Tab '{tab_name}' cleared successfully (Formula in A3 preserved).")
                    else:
                        target_rows = header_rows + 1
                        print(f"    * Resizing '{tab_name}' to {target_rows} rows...")
                        ws.resize(rows=target_rows)
                        col_count = ws.col_count
                        last_col_letter = rowcol_to_a1(target_rows, col_count).replace(str(target_rows), "")
                        range_str = f"A{target_rows}:{last_col_letter}{target_rows}"
                        print(f"    * Clearing row {target_rows} data (range: {range_str})...")
                        ws.batch_clear([range_str])
                        print(f"    [✅] Tab '{tab_name}' cleared successfully.")
                        
                except gspread.exceptions.WorksheetNotFound:
                    print(f"    - [⚠️ WARNING] Worksheet '{tab_name}' not found.")
                except Exception as e:
                    print(f"    - [❌ ERROR] Error clearing worksheet '{tab_name}': {e}")
        except Exception as e:
            print(f"  - [❌ ERROR] Failed to open spreadsheet {sheet_id}: {e}")

def clear_r2_production():
    print("\n=== [3/4] RESETTING CLOUDFLARE R2 PRODUCTION (ONLY v3) ===")
    try:
        import boto3
        cfg = load_config()
        r2_access_key = cfg.get("r2_access_key_id")
        r2_secret_key = cfg.get("r2_secret_access_key")
        r2_bucket = cfg.get("r2_bucket_name")
        account_id = cfg.get("cloudflare_account_id")
        
        if not (r2_access_key and r2_secret_key and r2_bucket and account_id):
            print("[⚠️] R2 configuration is incomplete. Skipping R2 clearance.")
            return
            
        s3 = boto3.client(
            service_name='s3',
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key,
            region_name="auto"
        )
        
        # We only delete v3 images. v2 must remain untouched!
        prefix = "BDS-KhangNgo-v3/"
        print(f"Searching for objects under prefix: '{prefix}'...")
        
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=r2_bucket, Prefix=prefix)
        
        deleted_count = 0
        for page in pages:
            if 'Contents' in page:
                objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
                if objects_to_delete:
                    print(f"  - Deleting {len(objects_to_delete)} objects...")
                    s3.delete_objects(Bucket=r2_bucket, Delete={'Objects': objects_to_delete})
                    deleted_count += len(objects_to_delete)
                    
        print(f"[✅] R2 production (v3) cleared. Total deleted objects: {deleted_count}")
    except Exception as e:
        print(f"[❌ ERROR] Failed to clear Cloudflare R2: {str(e)}")

def reset_listings_json():
    print("\n=== [4/4] RESETTING LISTINGS TO REBUILD STATUS ===")
    json_path = "scratch/listings_to_rebuild.json"
    if not os.path.exists(json_path):
        print(f"  - File does not exist: {json_path} (skip)")
        return
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Loaded {len(data)} listings from '{json_path}'. Resetting status to 'pending'...")
        for item in data:
            item["status"] = "pending"
            
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        print(f"[✅] Reset status for all {len(data)} listings to 'pending' successfully.")
    except Exception as e:
        print(f"[❌ ERROR] Failed to reset listings_to_rebuild.json: {e}")

if __name__ == "__main__":
    clear_sqlite_production()
    clear_sheets_production()
    clear_r2_production()
    reset_listings_json()
    print("\n[🎉 SUCCESS] MASTER PRODUCTION DATA RESET COMPLETED SUCCESSFULLY!")
