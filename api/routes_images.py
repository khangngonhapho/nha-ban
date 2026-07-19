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
        # Lấy địa chỉ từ database để tính toán subfolder R2
        r2_subfolder = None
        if use_r2:
            try:
                conn_pre = sqlite3.connect(manager.DB_FILE, timeout=30.0)
                cursor_pre = conn_pre.cursor()
                cursor_pre.execute(f"PRAGMA table_info({manager.LISTINGS_TABLE})")
                cols = {r[1] for r in cursor_pre.fetchall()}
                so_nha_col = "Ngo_So_nha" if "Ngo_So_nha" in cols else ("Ng__S__nh_" if "Ng__S__nh_" in cols else None)
                duong_col = "Duong" if "Duong" in cols else ("___ng" if "___ng" in cols else None)
                
                row_addr = None
                if so_nha_col and duong_col:
                    row_addr = cursor_pre.execute(f"SELECT `{so_nha_col}`, `{duong_col}` FROM {manager.LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
                conn_pre.close()
                
                if row_addr:
                    addr_dict = {
                        "Ngo_So_nha": row_addr[0],
                        "Duong": row_addr[1]
                    }
                    r2_subfolder = manager.get_r2_subfolder(tk_id, addr_dict)
            except Exception as e_addr:
                manager.add_log_message(f"[⚠️ WARNING] Không thể lấy địa chỉ cho upload-image {tk_id}: {str(e_addr)}")

        if use_r2:
            img_link = manager.upload_image_to_r2(img_bytes, filename, r2_subfolder=r2_subfolder)
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
            
            # Đồng bộ Images_Admin_JSON và images_public_json cho listings (Pool1)
            admin_json_str, public_json_str = manager.rebuild_admin_public_images_json(updated_curated, manual_list)
            
            cursor.execute(
                "UPDATE listings SET curated_config_json = ?, manual_images_json = ?, images_admin_json = ?, images_public_json = ? WHERE tk_id = ?",
                (json.dumps(updated_curated, ensure_ascii=False), json.dumps(manual_list, ensure_ascii=False), admin_json_str, public_json_str, tk_id)
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
            
            # Đồng bộ Images_Admin_JSON và images_public_json cho listings_v2 (Pool2)
            curated_config_obj = {"images": curated_list}
            admin_json_str, public_json_str = manager.rebuild_admin_public_images_json(curated_config_obj, [])
            
            cursor.execute(
                "UPDATE listings_v2 SET curated_config_json = ?, images_admin_json = ?, images_public_json = ? WHERE tk_id = ?",
                (curated_config_json, admin_json_str, public_json_str, tk_id)
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

@routes_images.route('/api/upload-r2', methods=['POST'])
def upload_r2_vercel_bridge():
    """
    Endpoint tương thích ngược với Vercel '/api/upload-r2' dùng cho môi trường Local.
    Tái sử dụng 100% logic nén, đặt tên, tính subfolder R2 thực tế và lưu trữ của Python backend.
    """
    import manager
    import base64
    
    data = request.get_json(silent=True) or {}
    file_b64 = data.get("file")
    filename_raw = data.get("filename")
    role = data.get("type", "interior").strip()
    tk_id = data.get("listingId")
    
    if not file_b64 or not filename_raw:
        return jsonify({"status": "error", "error": "Thiếu dữ liệu file hoặc tên file"}), 400
        
    try:
        img_bytes = base64.b64decode(file_b64)
    except Exception as e_dec:
        return jsonify({"status": "error", "error": f"Lỗi giải mã Base64: {str(e_dec)}"}), 400
        
    if not img_bytes:
        return jsonify({"status": "error", "error": "File ảnh rỗng"}), 400
        
    cfg = manager.load_config()
    r2_access_key = cfg.get("r2_access_key_id")
    r2_secret_key = cfg.get("r2_secret_access_key")
    r2_bucket = cfg.get("r2_bucket_name")
    account_id = cfg.get("cloudflare_account_id")
    use_r2 = bool(r2_access_key and r2_secret_key and r2_bucket and account_id)
    
    # 1. Nén ảnh nếu không phải sơ đồ
    is_diagram = (role in ["diagram", "sodo"])
    if not is_diagram:
        try:
            img_bytes = manager.compress_image(img_bytes)
        except Exception as e_comp:
            manager.add_log_message(f"[⚠️ Warning] Nén ảnh thủ công thất bại: {str(e_comp)}")
            
    # 2. Tạo tên file chuẩn hóa: SYS-{tk_id.upper()}_{role}_{timestamp}{ext}
    ext = os.path.splitext(filename_raw)[1] or ".jpg"
    timestamp = int(time.time())
    if tk_id:
        filename = f"SYS-{tk_id.upper()}_{role}_{timestamp}{ext}"
    else:
        filename = f"SYS-UPLOAD_{role}_{timestamp}{ext}"
        
    img_link = ""
    try:
        # Lấy địa chỉ từ database để tính toán subfolder R2
        r2_subfolder = None
        if use_r2 and tk_id:
            try:
                conn_pre = sqlite3.connect(manager.DB_FILE, timeout=30.0)
                cursor_pre = conn_pre.cursor()
                cursor_pre.execute(f"PRAGMA table_info({manager.LISTINGS_TABLE})")
                cols = {r[1] for r in cursor_pre.fetchall()}
                so_nha_col = "Ngo_So_nha" if "Ngo_So_nha" in cols else ("Ng__S__nh_" if "Ng__S__nh_" in cols else None)
                duong_col = "Duong" if "Duong" in cols else ("___ng" if "___ng" in cols else None)
                
                row_addr = None
                if so_nha_col and duong_col:
                    row_addr = cursor_pre.execute(f"SELECT `{so_nha_col}`, `{duong_col}` FROM {manager.LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
                conn_pre.close()
                
                if row_addr:
                    addr_dict = {
                        "Ngo_So_nha": row_addr[0],
                        "Duong": row_addr[1]
                    }
                    r2_subfolder = manager.get_r2_subfolder(tk_id, addr_dict)
            except Exception as e_addr:
                manager.add_log_message(f"[⚠️ WARNING] Không thể lấy địa chỉ cho upload-r2 {tk_id}: {str(e_addr)}")

        if use_r2:
            img_link = manager.upload_image_to_r2(img_bytes, filename, r2_subfolder=r2_subfolder)
        else:
            if tk_id:
                local_dir = os.path.join("static", "images", tk_id)
                os.makedirs(local_dir, exist_ok=True)
                local_path = os.path.join(local_dir, filename)
                with open(local_path, "wb") as f:
                    f.write(img_bytes)
                img_link = f"/static/images/{tk_id}/{filename}"
            else:
                local_dir = os.path.join("static", "images", "uploads")
                os.makedirs(local_dir, exist_ok=True)
                local_path = os.path.join(local_dir, filename)
                with open(local_path, "wb") as f:
                    f.write(img_bytes)
                img_link = f"/static/images/uploads/{filename}"
    except Exception as e_upload:
        return jsonify({"status": "error", "error": f"Tải ảnh lên cloud thất bại: {str(e_upload)}"}), 500
        
    # 3. Ghi nhận thông tin vào SQLite
    if tk_id:
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
                    "r2_url": img_link,
                    "role": vi_role,
                    "visible": visible,
                    "origin": "self"
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
                
                admin_json_str, public_json_str = manager.rebuild_admin_public_images_json(updated_curated, manual_list)
                
                cursor.execute(
                    "UPDATE listings SET curated_config_json = ?, manual_images_json = ?, images_admin_json = ?, images_public_json = ? WHERE tk_id = ?",
                    (json.dumps(updated_curated, ensure_ascii=False), json.dumps(manual_list, ensure_ascii=False), admin_json_str, public_json_str, tk_id)
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
                
                curated_config_obj = {"images": curated_list}
                admin_json_str, public_json_str = manager.rebuild_admin_public_images_json(curated_config_obj, [])
                
                cursor.execute(
                    "UPDATE listings_v2 SET curated_config_json = ?, images_admin_json = ?, images_public_json = ? WHERE tk_id = ?",
                    (curated_config_json, admin_json_str, public_json_str, tk_id)
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
            return jsonify({"status": "error", "error": f"Lỗi ghi nhận CSDL: {str(e_db)}"}), 500
        conn.close()
        
        # 4. Đồng bộ tức thời lên Google Sheets
        try:
            manager.execute_publish_listing(tk_id)
        except Exception as e_sheet:
            manager.add_log_message(f"[⚠️ Warning] Đồng bộ Sheets thất bại sau khi upload ảnh: {str(e_sheet)}")
            
    return jsonify({
        "status": "success",
        "url": img_link
    })
