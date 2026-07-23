# -*- coding: utf-8 -*-
"""
Image management routes for BDS KhangNgo.
Handles manual image uploads, Cloudflare R2 uploads, image metadata sync, and Google Sheets updates.
"""

import os
import re
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
                
                # Standardize role for database insert
                role_lower = role.lower()
                if role_lower in ["sodo", "diagram"]:
                    db_role = "diagram"
                elif role_lower in ["facade"]:
                    db_role = "facade"
                elif role_lower in ["cover"]:
                    db_role = "cover"
                elif role_lower in ["alley"]:
                    db_role = "alley"
                else:
                    db_role = "interior"

                cursor.execute("""
                    INSERT INTO listings_images (tk_id, image_url, r2_url, role, sequence_index, edited_by, origin)
                    VALUES (?, ?, ?, ?, ?, 'Admin', 'self')
                """, (tk_id, img_link, img_link, db_role, next_seq))
                
                all_imgs = cursor.execute(
                    "SELECT image_url, r2_url, role FROM listings_images WHERE tk_id = ? ORDER BY sequence_index ASC",
                    (tk_id,)
                ).fetchall()
                
                curated_list = []
                for img_url, r2_url_val, r_role in all_imgs:
                    url_to_use = r2_url_val if r2_url_val else img_url
                    role_map_en_to_vi = {
                        "diagram": "Sơ đồ",
                        "facade": "Mặt tiền",
                        "cover": "Bìa",
                        "alley": "Hẻm",
                        "interior": "Nội thất",
                        "hidden": "Ẩn",
                        "deleted": "deleted",
                        "sodo": "Sơ đồ"
                    }
                    mapped_role = role_map_en_to_vi.get(r_role, "Nội thất")
                    curated_list.append({"url": url_to_use, "role": mapped_role})
                    
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
                        if r_role not in ["facade", "diagram", "sodo", "deleted", "hidden"]:
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

# ==================================================
# IMAGE COMPARISON & PROXY DOWNLOAD ENDPOINTS (US-157)
# ==================================================

def sanitize_url_py(raw_url):
    if not raw_url:
        return ""
    u = str(raw_url).strip().strip('"').strip("'")
    if not u.startswith("http://") and not u.startswith("https://"):
        if u.startswith("BDS-KhangNgo") or u.startswith("static/"):
            u = "https://pub-e92603c36c8d4789917d05d1eba12a7e.r2.dev/" + u
        else:
            return ""
    try:
        from urllib.parse import urlparse, quote, unquote
        parsed = urlparse(u)
        encoded_path = quote(unquote(parsed.path))
        encoded_query = quote(unquote(parsed.query), safe="=&")
        scheme = parsed.scheme or "https"
        netloc = parsed.netloc
        return f"{scheme}://{netloc}{encoded_path}{'?' + encoded_query if encoded_query else ''}"
    except Exception:
        return u.replace(" ", "%20")

def expand_street_aliases(street_str):
    if not street_str:
        return []
    s = str(street_str).strip()
    aliases = [s]
    if re.search(r'(cách\s*mạng\s*tháng\s*(8|tám)|cmt8)', s, re.IGNORECASE):
        aliases.append(re.sub(r'(cách\s*mạng\s*tháng\s*(8|tám)|cmt8)', 'Cách Mạng Tháng 8', s, flags=re.IGNORECASE))
        aliases.append(re.sub(r'(cách\s*mạng\s*tháng\s*(8|tám)|cmt8)', 'CMT8', s, flags=re.IGNORECASE))
    elif re.search(r'(3\s*tháng\s*2|3\/2|ba\s*tháng\s*hai)', s, re.IGNORECASE):
        aliases.append(re.sub(r'(3\s*tháng\s*2|3\/2|ba\s*tháng\s*hai)', '3 Tháng 2', s, flags=re.IGNORECASE))
        aliases.append(re.sub(r'(3\s*tháng\s*2|3\/2|ba\s*tháng\s*hai)', '3/2', s, flags=re.IGNORECASE))
    elif re.search(r'đường\s*số\s*7', s, re.IGNORECASE):
        aliases.append(re.sub(r'đường\s*số\s*7', 'Đường số 7', s, flags=re.IGNORECASE))
        aliases.append(re.sub(r'đường\s*số\s*7', 'Đường 7', s, flags=re.IGNORECASE))
    return list(dict.fromkeys(aliases))

def normalize_street_name(street_str):
    if not street_str:
        return ""
    s = str(street_str).strip()
    # Quy tắc gen Mã Khang Ngô (ID): CMT8 -> TTMC, 3/2 -> HTB, Đường số 7 -> 7SD
    s_clean = re.sub(r'(cách\s*mạng\s*tháng\s*(8|tám)|cmt8)', 'TTMC', s, flags=re.IGNORECASE)
    s_clean = re.sub(r'(3\s*tháng\s*2|3\/2|ba\s*tháng\s*hai)', 'HTB', s_clean, flags=re.IGNORECASE)
    s_clean = re.sub(r'đường\s*số\s*7', '7SD', s_clean, flags=re.IGNORECASE)
    return s_clean

def extract_filename_py(url):
    try:
        from urllib.parse import urlparse, unquote
        path = urlparse(url).path
        name = os.path.basename(path)
        return unquote(name) if name else "image.jpg"
    except Exception:
        return "image.jpg"

def normalize_house_number(house_str):
    if not house_str:
        return ""
    h = str(house_str).strip()
    # Rule 2: Số nhà chứa dấu +, chỉ lấy phần trước dấu +
    if '+' in h:
        h = h.split('+')[0].strip()
    return h

def parse_image_json_to_list(raw_json):
    if not raw_json:
        return []
    if isinstance(raw_json, list):
        parsed = raw_json
    elif isinstance(raw_json, dict):
        parsed = raw_json.get("images", raw_json)
    else:
        try:
            parsed = json.loads(raw_json)
        except Exception:
            raw_str = str(raw_json)
            tokens = re.split(r'[\t\r\n]+|\s{2,}', raw_str)
            parsed = []
            for t in tokens:
                t_clean = t.strip().strip('"').strip("'")
                if t_clean.startswith("http://") or t_clean.startswith("https://") or t_clean.startswith("BDS-KhangNgo"):
                    parsed.append(t_clean)
            if not parsed:
                parsed = re.findall(r'(https?://[^\s"\'`,{}()\[\]\\]+)', raw_str)
            
    if isinstance(parsed, dict) and "images" in parsed:
        parsed = parsed["images"]
        
    if not isinstance(parsed, list):
        return []
        
    result = []
    for idx, obj in enumerate(parsed):
        if not obj:
            continue
        if isinstance(obj, str):
            url_str = sanitize_url_py(obj)
            if url_str:
                result.append({
                    "id": f"img-{idx}",
                    "url": url_str,
                    "filename": extract_filename_py(url_str),
                    "role": "",
                    "sequence_index": idx,
                    "origin": "",
                    "is_hidden": 0
                })
        elif isinstance(obj, dict):
            raw_u = obj.get("r2_url") or obj.get("image_url") or obj.get("url")
            url_str = sanitize_url_py(raw_u)
            if url_str:
                result.append({
                    "id": f"img-{idx}",
                    "url": url_str,
                    "filename": extract_filename_py(url_str),
                    "role": obj.get("role", ""),
                    "sequence_index": obj.get("sequence_index") if obj.get("sequence_index") is not None else idx,
                    "origin": obj.get("origin", ""),
                    "is_hidden": obj.get("is_hidden", 0)
                })
    return result

@routes_images.route('/api/databases', methods=['GET'])
def get_databases():
    """Trả về danh sách các tệp SQLite .db trong thư mục dự án"""
    try:
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        db_files = [f for f in os.listdir(project_dir) if f.endswith(".db")]
        # Đưa raw_archive.db lên đầu danh sách nếu có
        if "raw_archive.db" in db_files:
            db_files.remove("raw_archive.db")
            db_files.insert(0, "raw_archive.db")
        return jsonify({"status": "success", "databases": db_files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@routes_images.route('/api/compare-images', methods=['GET'])
def compare_images():
    """Tra cứu căn nhà và trích xuất dữ liệu ảnh 3 phân vùng (SQLite, Pool Sheet, Source Sheet)"""
    query_str = request.args.get("query", "").strip()
    db_filename = request.args.get("db_file", "raw_archive.db").strip()
    
    if not query_str:
        return jsonify({"status": "error", "message": "Thiếu tham số query"}), 400
        
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    db_path = os.path.join(project_dir, db_filename)
    
    if not os.path.exists(db_path):
        return jsonify({"status": "error", "message": f"Không tìm thấy CSDL SQLite: {db_filename}"}), 404
        
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Xác định bảng chứa listings
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('listings_v2', 'listings');")
        tables = [r[0] for r in cursor.fetchall()]
        table_name = "listings_v2" if "listings_v2" in tables else ("listings" if "listings" in tables else None)
        
        if not table_name:
            conn.close()
            return jsonify({"status": "error", "message": "Không tìm thấy bảng dữ liệu listings trong SQLite"}), 500

        # Kiểm tra danh sách cột
        cursor.execute(f"PRAGMA table_info({table_name});")
        cols = [r[1] for r in cursor.fetchall()]
        
        so_nha_col = "Ngo_So_nha" if "Ngo_So_nha" in cols else "So_nha"
        duong_col = "Duong" if "Duong" in cols else "duong"
        sys_id_col = "System_ID" if "System_ID" in cols else "System ID"
        ma_kn_col = "Ma_Khang_Ngo_ID" if "Ma_Khang_Ngo_ID" in cols else "Mã Khang Ngô (ID)"

        row = None
        # 1. Khớp trực tiếp theo Mã nhà / System ID / tk_id
        sql_direct = f"SELECT * FROM {table_name} WHERE tk_id = ? OR `{sys_id_col}` = ? OR `{ma_kn_col}` = ?"
        row = cursor.execute(sql_direct, (query_str, query_str, query_str)).fetchone()
        
        if not row:
            # 2. Khớp theo Số nhà và Tên đường thực tế
            clean_q = query_str.replace('+', ' ')
            tokens = [t for t in clean_q.split() if t]
            if len(tokens) >= 1:
                first_tok = tokens[0]
                first_clean = normalize_house_number(first_tok)
                street_input = " ".join(tokens[1:]) if len(tokens) > 1 else query_str
                street_aliases = expand_street_aliases(street_input)
                
                for st in street_aliases:
                    sql_token = f"""
                        SELECT * FROM {table_name}
                        WHERE (`{so_nha_col}` LIKE ? OR `{so_nha_col}` LIKE ?) 
                          AND (`{duong_col}` LIKE ? OR `{duong_col}` LIKE ? OR ? LIKE '%' || `{duong_col}` || '%')
                        ORDER BY id DESC LIMIT 1
                    """
                    row = cursor.execute(sql_token, (f"%{first_tok}%", f"%{first_clean}%", f"%{st}%", f"%{query_str}%", st)).fetchone()
                    if row:
                        break

            if not row:
                sql_like = f"""
                    SELECT * FROM {table_name} 
                    WHERE `{so_nha_col}` LIKE ? OR `{duong_col}` LIKE ? OR (`{so_nha_col}` || ' ' || `{duong_col}`) LIKE ? OR (`{so_nha_col}` || '/' || `{duong_col}`) LIKE ?
                    ORDER BY id DESC LIMIT 1
                """
                q_like = f"%{query_str}%"
                row = cursor.execute(sql_like, (q_like, q_like, q_like, q_like)).fetchone()
                
        if not row:
            conn.close()
            return jsonify({"status": "error", "message": f"Không tìm thấy căn nhà phù hợp với từ khóa '{query_str}' trong CSDL '{db_filename}'"}), 404
            
        row_dict = dict(row)
        tk_id = row_dict.get("tk_id", "")
        system_id = row_dict.get("System_ID") or row_dict.get("system_id") or ""
        ma_khang_ngo = row_dict.get(ma_kn_col) or row_dict.get("Ma_Khang_Ngo_ID") or ""
        so_nha_val = row_dict.get(so_nha_col, "")
        duong_val = row_dict.get(duong_col, "")
        quan_val = row_dict.get("Quan") or row_dict.get("Qu_n") or ""
        
        # Partition 1: Images_Admin_JSON từ SQLite
        admin_json_raw = row_dict.get("images_admin_json") or row_dict.get("Images_Admin_JSON") or row_dict.get("curated_config_json") or ""
        partition_1_sqlite = parse_image_json_to_list(admin_json_raw)
        
        conn.close()
    except Exception as e_db:
        return jsonify({"status": "error", "message": f"Lỗi đọc CSDL SQLite: {str(e_db)}"}), 500

    # Partition 2: Images_Admin_JSON từ Sheet Pool
    partition_2_pool = []
    pool_is_fallback = False
    try:
        partition_2_pool = fetch_image_json_from_sheet("Pool", system_id or tk_id, "Images_Admin_JSON")
    except Exception:
        partition_2_pool = partition_1_sqlite
        pool_is_fallback = True

    # Partition 3: Images_Public_JSON từ Sheet Source
    partition_3_source = []
    source_is_fallback = False
    try:
        partition_3_source = fetch_image_json_from_sheet("Source", ma_khang_ngo or system_id, "Images_Public_JSON")
    except Exception:
        pub_json_raw = row_dict.get("images_public_json") or row_dict.get("Images_Public_JSON") or ""
        partition_3_source = parse_image_json_to_list(pub_json_raw)
        source_is_fallback = True

    house_info = {
        "tk_id": tk_id,
        "system_id": system_id,
        "ma_khang_ngo": ma_khang_ngo,
        "so_nha": so_nha_val,
        "duong": duong_val,
        "quan": quan_val,
        "full_address": f"{so_nha_val} {duong_val}, {quan_val}".strip(" ,"),
        "db_file": db_filename
    }

    return jsonify({
        "status": "success",
        "house_info": house_info,
        "partition_1_sqlite": partition_1_sqlite,
        "partition_2_pool": {
            "images": partition_2_pool,
            "is_fallback": pool_is_fallback
        },
        "partition_3_source": {
            "images": partition_3_source,
            "is_fallback": source_is_fallback
        }
    })

@routes_images.route('/api/proxy-download', methods=['GET'])
def proxy_download():
    """
    Proxy endpoint server-side hỗ trợ tải hình ảnh từ URL bất kỳ về máy khách.
    Tránh rào cản CORS trên trình duyệt.
    """
    import requests
    from flask import Response
    
    url = request.args.get("url", "").strip()
    filename = request.args.get("filename", "").strip()
    
    if not url:
        return jsonify({"status": "error", "message": "Thiếu tham số url"}), 400
        
    if not filename:
        filename = extract_filename_py(url)
        
    clean_filename = re.sub(r'["\r\n\\]', '', filename)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30, stream=True)
        if resp.status_code != 200:
            return jsonify({"status": "error", "message": f"Remote server HTTP {resp.status_code}"}), 502
            
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        
        response = Response(
            resp.raw,
            content_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{clean_filename}"',
                "Access-Control-Allow-Origin": "*"
            }
        )
        return response
    except Exception as e:
        return jsonify({"status": "error", "message": f"Proxy fetch failed: {str(e)}"}), 500

