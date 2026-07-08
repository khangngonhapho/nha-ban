# -*- coding: utf-8 -*-
"""
Image management routes for BDS KhangNgo.
Handles manual image uploads, Cloudflare R2 uploads, image metadata sync, and Google Sheets updates.
"""

import os
import json
import sqlite3
import time
from flask import Blueprint, jsonify, request

routes_images = Blueprint('routes_images', __name__)

@routes_images.route('/api/listings/<tk_id>/upload-image', methods=['POST'])
def upload_manual_image(tk_id):
    """
    API đăng tải hình ảnh thủ công cho căn nhà (Pool2).
    Lưu vào Cloudflare R2 (hoặc Local), cập nhật SQLite listings_images, listings_v2,
    và đồng bộ an toàn lên Google Sheets (cách ly ảnh nhạy cảm).
    """
    import manager
    
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Không tìm thấy file ảnh"}), 400
        
    file = request.files['file']
    role = request.form.get("role", "interior").strip()
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "Chưa chọn file ảnh"}), 400
        
    img_bytes = file.read()
    if not img_bytes:
        return jsonify({"status": "error", "message": "File ảnh rỗng"}), 400
        
    cfg = manager.load_config()
    r2_access_key = cfg.get("r2_access_key_id")
    r2_secret_key = cfg.get("r2_secret_access_key")
    r2_bucket = cfg.get("r2_bucket_name")
    account_id = cfg.get("cloudflare_account_id")
    use_r2 = bool(r2_access_key and r2_secret_key and r2_bucket and account_id)
    
    is_diagram = (role in ["diagram", "sodo"])
    if not is_diagram:
        try:
            img_bytes = manager.compress_image(img_bytes)
        except Exception as e_comp:
            manager.add_log_message(f"[⚠️ Warning] Nén ảnh thủ công thất bại: {str(e_comp)}")
            
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    timestamp = int(time.time())
    filename = f"SYS-{tk_id.upper()}_{role}_{timestamp}{ext}"
    
    img_link = ""
    try:
        if use_r2:
            img_link = manager.upload_image_to_r2(img_bytes, filename)
        else:
            local_dir = os.path.join("static", "images", tk_id)
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, filename)
            with open(local_path, "wb") as f:
                f.write(img_bytes)
            img_link = f"/static/images/{tk_id}/{filename}"
    except Exception as e_upload:
        return jsonify({"status": "error", "message": f"Tải ảnh lên cloud thất bại: {str(e_upload)}"}), 500
        
    conn = sqlite3.connect(manager.DB_FILE, timeout=30.0)
    cursor = conn.cursor()
    try:
        if manager.LISTINGS_TABLE == "listings":
            role_map = {
                "sodo": "Sơ đồ",
                "diagram": "Sơ đồ",
                "facade": "Mặt tiền",
                "interior": "Nội thất",
                "alley": "Hẻm",
                "cover": "Bìa"
            }
            vi_role = role_map.get(role.lower(), "Nội thất")
            visible = False if vi_role in ["Sơ đồ", "Mặt tiền"] else True
            
            cursor.execute("SELECT curated_config_json, manual_images_json FROM listings WHERE tk_id = ?", (tk_id,))
            row_db = cursor.fetchone()
            curated_json = row_db[0] if row_db else None
            manual_json = row_db[1] if row_db else None
            
            try:
                manual_list = json.loads(manual_json) if manual_json else []
            except Exception:
                manual_list = []
            if not isinstance(manual_list, list):
                manual_list = []
            manual_list.append(img_link)
            
            new_img_obj = {
                "url": img_link,
                "role": vi_role,
                "visible": visible
            }
            
            if not curated_json:
                updated_curated = {"images": [new_img_obj]}
            else:
                try:
                    data_curated = json.loads(curated_json)
                except Exception:
                    data_curated = {"images": []}
                
                if isinstance(data_curated, dict):
                    if "images" not in data_curated or not isinstance(data_curated["images"], list):
                        data_curated["images"] = []
                    data_curated["images"].append(new_img_obj)
                    updated_curated = data_curated
                elif isinstance(data_curated, list):
                    data_curated.append(new_img_obj)
                    updated_curated = data_curated
                else:
                    updated_curated = {"images": [new_img_obj]}
            
            cursor.execute(
                "UPDATE listings SET curated_config_json = ?, manual_images_json = ? WHERE tk_id = ?",
                (json.dumps(updated_curated, ensure_ascii=False), json.dumps(manual_list, ensure_ascii=False), tk_id)
            )
        else:
            max_seq = cursor.execute(
                "SELECT MAX(sequence_index) FROM listings_images WHERE tk_id = ?", 
                (tk_id,)
            ).fetchone()[0]
            next_seq = (max_seq + 1) if (max_seq is not None) else 0
            
            cursor.execute("""
                INSERT INTO listings_images (tk_id, image_url, r2_url, role, sequence_index, edited_by, origin)
                VALUES (?, ?, ?, ?, ?, 'Admin', 'self')
            """, (tk_id, img_link, img_link, role, next_seq))
            
            all_imgs = cursor.execute(
                "SELECT image_url, r2_url, role FROM listings_images WHERE tk_id = ? ORDER BY sequence_index ASC",
                (tk_id,)
            ).fetchall()
            
            curated_list = []
            for img_url, r2_url_val, r_role in all_imgs:
                url_to_use = r2_url_val if r2_url_val else img_url
                curated_list.append({"url": url_to_use, "role": r_role or "interior"})
                
            curated_config_json = json.dumps(curated_list, ensure_ascii=False)
            cursor.execute(
                "UPDATE listings_v2 SET curated_config_json = ? WHERE tk_id = ?",
                (curated_config_json, tk_id)
            )
            
            sys_row = cursor.execute("SELECT System_ID FROM listings_v2 WHERE tk_id = ?", (tk_id,)).fetchone()
            system_id = sys_row[0] if sys_row else None
            
            if role in ["interior", "alley", "cover"] and system_id:
                safe_imgs = []
                for img_url, r2_url_val, r_role in all_imgs:
                    if r_role not in ["facade", "diagram", "deleted", "hidden"]:
                        url_to_use = r2_url_val if r2_url_val else img_url
                        safe_imgs.append({"url": url_to_use, "role": r_role or "interior"})
                
                safe_json = json.dumps(safe_imgs, ensure_ascii=False)
                cursor.execute(
                    "UPDATE listings_custom_v2 SET images_metadata_json = ? WHERE System_ID = ?",
                    (safe_json, system_id)
                )
        conn.commit()
    except Exception as e_db:
        conn.close()
        return jsonify({"status": "error", "message": f"Lỗi ghi nhận CSDL: {str(e_db)}"}), 500
    conn.close()
    
    try:
        manager.execute_publish_listing(tk_id)
    except Exception as e_sheet:
        manager.add_log_message(f"[⚠️ Warning] Đồng bộ Sheets thất bại sau khi upload ảnh: {str(e_sheet)}")
        
    return jsonify({
        "status": "success",
        "message": f"Tải lên hình ảnh vai trò '{role}' thành công!",
        "url": img_link
    })
