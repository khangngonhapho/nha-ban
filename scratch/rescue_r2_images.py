# scratch/rescue_r2_images.py
import sys
import os
import sqlite3
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manager

def rescue_all_listings():
    print("=== STARTING R2 IMAGE RESCUE UTILITY ===")
    conn = sqlite3.connect(manager.DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Query all active or raw_complete/complete listings
    cursor.execute("SELECT * FROM listings WHERE status NOT IN ('deleted', 'sold')")
    rows = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(rows)} listings in SQLite to inspect.")
    
    cfg = manager.load_config()
    r2_public_url = cfg.get("r2_public_url", "")
    r2_migration_prefix = cfg.get("r2_migration_prefix", "BDS-KhangNgo-v2") or "BDS-KhangNgo-v2"
    
    rescued_count = 0
    
    for row in rows:
        tk_id = row["tk_id"]
        d = manager.normalize_listing_for_client(row)
        raw_images_tk = d["raw_images_tk"]
        
        # Calculate subfolder
        r2_subfolder = manager.get_r2_subfolder(tk_id, dict(row))
        prefix = f"{r2_migration_prefix}/{r2_subfolder}/"
        
        # Query R2
        r2_keys = manager.list_r2_objects(prefix)
        if not r2_keys:
            continue
            
        print(f"\n[+] Listing {tk_id} ({row['Ngo_So_nha']} {row['Duong']}): Found {len(r2_keys)} images on R2.")
        
        # Reconstruct mapping
        images_mapping = {}
        new_images_mapping = {}
        manual_images = []
        
        col_sodo1_key = manager.get_safe_col_name("Sơ đồ thửa đất 1")
        col_sodo2_key = manager.get_safe_col_name("Sơ đồ thửa đất 2")
        col_sodo3_key = manager.get_safe_col_name("Sơ đồ thửa đất 3")
        col_sodo4_key = manager.get_safe_col_name("Sơ đồ thửa đất 4")
        col_sodo5_key = manager.get_safe_col_name("Sơ đồ thửa đất 5")
        original_sodo1 = d.get(col_sodo1_key)
        original_sodo2 = d.get(col_sodo2_key)
        original_sodo3 = d.get(col_sodo3_key)
        original_sodo4 = d.get(col_sodo4_key)
        original_sodo5 = d.get(col_sodo5_key)
        
        for key in r2_keys:
            filename = key.split("/")[-1]
            r2_url = f"{r2_public_url}/{key}"
            
            # 1. Normal image
            if filename.startswith(f"img_{tk_id}_") and filename.endswith(".jpg"):
                try:
                    idx_str = filename[len(f"img_{tk_id}_"):-4]
                    idx = int(idx_str)
                    if 1 <= idx <= len(raw_images_tk):
                        img_url = raw_images_tk[idx - 1]
                        images_mapping[img_url] = r2_url
                        new_images_mapping[img_url] = r2_url
                except Exception:
                    pass
            # 2. Diagram
            elif filename.startswith("sodo") and filename.endswith(f"_{tk_id}.jpg"):
                try:
                    sodo_num = filename[4:filename.find(f"_{tk_id}")]
                    if sodo_num == "1" and original_sodo1:
                        images_mapping[original_sodo1] = r2_url
                        new_images_mapping[original_sodo1] = r2_url
                    elif sodo_num == "2" and original_sodo2:
                        images_mapping[original_sodo2] = r2_url
                        new_images_mapping[original_sodo2] = r2_url
                    elif sodo_num == "3" and original_sodo3:
                        images_mapping[original_sodo3] = r2_url
                        new_images_mapping[original_sodo3] = r2_url
                    elif sodo_num == "4" and original_sodo4:
                        images_mapping[original_sodo4] = r2_url
                        new_images_mapping[original_sodo4] = r2_url
                    elif sodo_num == "5" and original_sodo5:
                        images_mapping[original_sodo5] = r2_url
                        new_images_mapping[original_sodo5] = r2_url
                except Exception:
                    pass
            # 3. Manual upload
            elif (filename.upper().startswith(f"SYS-{tk_id.upper()}_") or 
                  filename.upper().startswith(f"SYS-{tk_id.replace('-', '').upper()}_")):
                if r2_url not in manual_images:
                    manual_images.append(r2_url)
                    
        # Reconstruct curated_config
        new_images_list = []
        added_urls = set()
        
        # Add manual images first
        for url in manual_images:
            filename = url.split("/")[-1]
            role = "Nội thất"
            if "_sodo_" in filename.lower() or "_diagram_" in filename.lower():
                role = "Sơ đồ"
            elif "_facade_" in filename.lower() or "_mattien_" in filename.lower():
                role = "Mặt tiền"
            elif "_cover_" in filename.lower() or "_bia_" in filename.lower():
                role = "Bìa"
            elif "_alley_" in filename.lower() or "_hem_" in filename.lower():
                role = "Hẻm"
                
            new_images_list.append({
                "url": url,
                "role": role,
                "visible": True if role not in ["Sơ đồ", "Mặt tiền"] else False
            })
            added_urls.add(url)
            
        # Add crawled images that exist in new_images_mapping
        first_property_r2 = ""
        stripped_sodo = {url.split('?')[0] for url in d.get("raw_sodo_tk", []) if url}
        for img_url in raw_images_tk:
            stripped_img = img_url.split('?')[0] if img_url else ""
            is_diag = (stripped_img in stripped_sodo) or \
                      (original_sodo1 and stripped_img == original_sodo1.split('?')[0]) or \
                      (original_sodo2 and stripped_img == original_sodo2.split('?')[0]) or \
                      (original_sodo3 and stripped_img == original_sodo3.split('?')[0]) or \
                      (original_sodo4 and stripped_img == original_sodo4.split('?')[0]) or \
                      (original_sodo5 and stripped_img == original_sodo5.split('?')[0])
            if not is_diag and img_url in new_images_mapping:
                first_property_r2 = new_images_mapping[img_url]
                break
                
        for img_url in raw_images_tk:
            if img_url in new_images_mapping:
                r2_url = new_images_mapping[img_url]
                if r2_url not in added_urls:
                    stripped_img = img_url.split('?')[0] if img_url else ""
                    is_diag = (stripped_img in stripped_sodo) or \
                              (original_sodo1 and stripped_img == original_sodo1.split('?')[0]) or \
                              (original_sodo2 and stripped_img == original_sodo2.split('?')[0]) or \
                              (original_sodo3 and stripped_img == original_sodo3.split('?')[0]) or \
                              (original_sodo4 and stripped_img == original_sodo4.split('?')[0]) or \
                              (original_sodo5 and stripped_img == original_sodo5.split('?')[0])
                    
                    if is_diag:
                        role = "Sơ đồ"
                        visible = False
                    elif r2_url == first_property_r2:
                        role = "Mặt tiền"
                        visible = True
                    else:
                        role = "Nội thất"
                        visible = False
                        
                    new_images_list.append({
                        "url": r2_url,
                        "role": role,
                        "visible": visible
                    })
                    added_urls.add(r2_url)
                    
        new_curated_config = {
            "images": new_images_list,
            "Mã_Khang_Ngô__ID_": d.get("Ma_Khang_Ngo_ID", "")
        }
        
        # Build admin and public json
        admin_json_str, public_json_str = manager.rebuild_admin_public_images_json(new_curated_config, manual_images)
        
        # Extract individual clean diagram images
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
        
        hinh_mat_tien = first_property_r2
        
        # Save to SQLite
        conn_db = sqlite3.connect(manager.DB_FILE)
        cursor_db = conn_db.cursor()
        
        cursor_db.execute(f"PRAGMA table_info({manager.LISTINGS_TABLE})")
        db_cols = {r[1] for r in cursor_db.fetchall()}
        
        update_fields = {
            "images_mapping_json": json.dumps(new_images_mapping, ensure_ascii=False),
            "manual_images_json": json.dumps(manual_images, ensure_ascii=False),
            "curated_config_json": json.dumps(new_curated_config, ensure_ascii=False),
            "images_admin_json": admin_json_str,
            "images_public_json": public_json_str,
            "status": "raw_complete"
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
        
        print(f"  -> SQLite updated. Synced status -> raw_complete.")
        
        # Sync to Sheets
        try:
            manager.execute_publish_listing(tk_id)
            print("  -> Synced to Google Sheets successfully.")
        except Exception as e_sync:
            print(f"  -> Sheets sync failed: {str(e_sync)}")
            
        rescued_count += 1
        
    print(f"\n=== RESCUE UTILITY FINISHED: Rescued {rescued_count} listings ===")

if __name__ == "__main__":
    rescue_all_listings()
