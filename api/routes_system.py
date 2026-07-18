# -*- coding: utf-8 -*-
"""
System and Config routes for BDS KhangNgo.
Handles dynamic schema alterations, system configs, logs, and cookie storage.
"""

import os
import json
import sqlite3
import manager
from flask import Blueprint, jsonify, request

routes_system = Blueprint('routes_system', __name__)

@routes_system.route('/api/schema/add-column', methods=['POST'])
def add_schema_column():
    """
    API thêm thuộc tính mới động (Dynamic Schema) cho Pool2.
    Đồng bộ: settings.json, SQLite listings_v2 & listings_custom_v2, Google Sheets và tài liệu markdown.
    """
    import manager
    import pool_lego
    
    data = request.json or {}
    column_name = data.get("column_name", "").strip()
    data_type = data.get("data_type", "TEXT").strip().upper()
    is_public = bool(data.get("is_public", False))
    description = data.get("description", "").strip()
    
    if not column_name:
        return jsonify({"status": "error", "message": "Tên cột không được để trống"}), 400
        
    safe_name = pool_lego.get_safe_col_name(column_name)
    
    # 1. Ghi thông tin mới vào settings.json
    cfg = manager.load_config()
    if "custom_schema_columns" not in cfg:
        cfg["custom_schema_columns"] = []
        
    # Check if exists
    for col in cfg["custom_schema_columns"]:
        if pool_lego.get_safe_col_name(col.get("column_name")) == safe_name:
            return jsonify({"status": "error", "message": f"Cột '{column_name}' đã tồn tại trong cấu hình"}), 400
            
    cfg["custom_schema_columns"].append({
        "column_name": column_name,
        "data_type": data_type,
        "is_public": is_public,
        "description": description
    })
    manager.save_config(cfg)
    
    # Nạp lại cấu hình động trong pool_lego memory
    pool_lego.load_custom_columns()
    
    # 2. ALTER TABLE SQLite listings_v2 & listings_custom_v2
    conn = sqlite3.connect(manager.DB_FILE, timeout=30.0)
    cursor = conn.cursor()
    try:
        # listings_v2
        cursor.execute("PRAGMA table_info(listings_v2)")
        v2_cols = [r[1] for r in cursor.fetchall()]
        if safe_name not in v2_cols:
            cursor.execute(f"ALTER TABLE listings_v2 ADD COLUMN `{safe_name}` {data_type}")
            
        # listings_custom_v2 (tất cả là TEXT phục vụ đè)
        cursor.execute("PRAGMA table_info(listings_custom_v2)")
        custom_cols = [r[1] for r in cursor.fetchall()]
        if safe_name not in custom_cols:
            cursor.execute(f"ALTER TABLE listings_custom_v2 ADD COLUMN `{safe_name}` TEXT")
            
        conn.commit()
    except Exception as e_db:
        conn.rollback()
        return jsonify({"status": "error", "message": f"Lỗi cập nhật CSDL: {str(e_db)}"}), 500
    finally:
        conn.close()
        
    # 3. Đồng bộ tạo thêm cột bên Google Sheets Pool2 và file markdown tài liệu
    try:
        manager.add_log_message(f"[*] Đang chèn thêm cột động '{column_name}' sang hệ thống Google Sheets Pool2...")
        pool_lego.add_column_to_google_sheets_v2(
            safe_name, column_name, is_public,
            manager.get_google_credentials, manager.load_config, manager.add_log_message
        )
        manager.add_log_message(f"[✅ OK] Đã chèn xong cột động '{column_name}' sang Google Sheets.")
    except Exception as e_sheets:
        manager.add_log_message(f"[⚠️ WARNING] Không thể tự động chèn cột sang Google Sheets: {str(e_sheets)}")
        
    try:
        pool_lego.append_column_to_docs(column_name, description, is_public)
        manager.add_log_message(f"[✅ OK] Đã tự động cập nhật schema và ghi nhận thuộc tính '{column_name}' vào tài liệu docs/data_dictionary.md")
    except Exception as e_docs:
        manager.add_log_message(f"[⚠️ WARNING] Không thể tự động cập nhật tài liệu: {str(e_docs)}")
        
    return jsonify({
        "status": "success",
        "message": f"Thêm thuộc tính động '{column_name}' thành công!"
    })

@routes_system.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """API lấy và cập nhật cấu hình"""
    import manager
    if request.method == 'POST':
        data = request.json
        cfg = manager.load_config()
        is_staging = os.environ.get("STAGING") == "true"
        is_pool2 = (cfg.get("active_pool_system") == "Pool2")

        # Map pool_sheet_id dynamically to correct key depending on active system mode
        if "pool_sheet_id" in data:
            val = data["pool_sheet_id"].strip() if isinstance(data["pool_sheet_id"], str) else ""
            if is_staging:
                cfg["staging_pool_sheet_id"] = val
            elif is_pool2:
                cfg["pool2_raw_sheet_id"] = val
            else:
                cfg["sheet_id"] = val

        # Ignore sheet_id key if sent from client in Staging or Pool2 mode to protect production credentials
        for k in manager.DEFAULT_CONFIG.keys():
            if k in data:
                if k == "sheet_id" and (is_staging or is_pool2):
                    continue
                # Bảo vệ chống ghi đè OpenAI API Key bằng chuỗi trống hoặc placeholder từ UI
                if k == "openai_api_key":
                    new_key = data[k].strip() if isinstance(data[k], str) else ""
                    if new_key and not new_key.startswith("sk-proj-xxxx") and "xxxxxxxx" not in new_key:
                        cfg[k] = new_key
                else:
                    cfg[k] = data[k]
        # Tự động trích xuất json_ui_fields từ json_ui_filters
        if "json_ui_filters" in data:
            filters = data["json_ui_filters"] or []
            fields = []
            for f in filters:
                if isinstance(f, dict) and f.get("field"):
                    fields.append(f["field"])
            cfg["json_ui_fields"] = fields
        manager.save_config(cfg)
        return jsonify({"status": "success", "config": cfg})
    else:
        cfg = manager.load_config()
        client_cfg = dict(cfg)
        if "openai_api_key" in client_cfg and client_cfg["openai_api_key"]:
            key = client_cfg["openai_api_key"]
            if len(key) > 12:
                client_cfg["openai_api_key"] = f"{key[:8]}...xxxx...{key[-4:]}"
        
        # Quyết định Spreadsheet IDs động dựa vào chế độ STAGING
        is_staging = os.environ.get("STAGING") == "true"
        is_pool2 = (client_cfg.get("active_pool_system") == "Pool2")
        
        if is_staging:
            client_cfg["sheet_id"] = client_cfg.get("staging_public_sheet_id") or "1fDe5nrllgXBdGmYXlIhlYp0sJ_BPuarpD1DjsK_7JWw"
            client_cfg["pool_sheet_id"] = client_cfg.get("staging_pool_sheet_id") or "1Nc8OwSHwacvuuS4blI8U9BrDOlVx6S6u9fU3AaKBYdY"
            client_cfg["source_sheet_id"] = client_cfg.get("staging_source_sheet_id") or "1ljauQNEPA-8wM0vlJDRQkWjT2KQUwdR8tcq0r69dikk"
        else:
            if is_pool2:
                client_cfg["sheet_id"] = client_cfg.get("pool2_public_sheet_id") or ""
                client_cfg["pool_sheet_id"] = client_cfg.get("pool2_raw_sheet_id") or ""
                client_cfg["source_sheet_id"] = client_cfg.get("pool2_custom_sheet_id") or ""
            else:
                client_cfg["sheet_id"] = "1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0"
                client_cfg["pool_sheet_id"] = cfg.get("sheet_id") or "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
                client_cfg["source_sheet_id"] = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
                
        # Đọc động feature flags từ Google Sheets với cơ chế fallback an toàn
        dynamic_flags = {}
        try:
            active_sheet_id = client_cfg.get("pool_sheet_id")
            if active_sheet_id:
                import gspread
                creds = manager.get_google_credentials()
                if creds:
                    gc = gspread.authorize(creds)
                    # Mở worksheet và đọc nhanh
                    sh = gc.open_by_key(active_sheet_id)
                    wks = sh.worksheet("Feature_Flags")
                    records = wks.get_all_records()
                    for row in records:
                        name = row.get("Tên Flag")
                        val = row.get("Giá Trị Hiện Tại")
                        status = row.get("Trạng Thái")
                        if name and status == "active":
                            dynamic_flags[name] = (str(val).upper() == "TRUE")
        except Exception:
            # Fallback thầm lặng nếu không kết nối được hoặc lỗi cấu hình
            pass

        # Gộp cờ từ Google Sheets đè lên settings.json
        local_flags = client_cfg.get("feature_flags") or {}
        merged_flags = {**local_flags, **dynamic_flags}
        client_cfg["feature_flags"] = merged_flags
        client_cfg["maintenance_mode"] = merged_flags.get("maintenance_mode", False)
        
        # Thêm danh sách exclusion rules đang active từ SQLite
        exclusions = []
        try:
            import sqlite3
            import manager
            db_file = getattr(manager, "DB_FILE", "raw_archive.db")
            conn = sqlite3.connect(db_file, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute("SELECT id, field, operator, value, status, note FROM exclusion_filters WHERE status = 'Active'")
            rows = cursor.fetchall()
            for r in rows:
                exclusions.append({
                    "id": r[0],
                    "field": r[1],
                    "operator": r[2],
                    "value": r[3],
                    "status": r[4],
                    "note": r[5]
                })
            conn.close()
        except Exception:
            pass
        client_cfg["exclusions"] = exclusions
        client_cfg["db_file"] = os.path.basename(manager.DB_FILE)
        client_cfg["is_staging"] = is_staging
        
        return jsonify({"status": "success", "config": client_cfg})

@routes_system.route('/api/logs', methods=['GET'])
def get_logs():
    """API lấy logs thời gian thực cho giao diện"""
    import manager
    with manager.LOGS_LOCK:
        return jsonify({"logs": manager.LOGS_BUFFER})

@routes_system.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """API xóa sạch logs buffer"""
    import manager
    with manager.LOGS_LOCK:
        manager.LOGS_BUFFER.clear()
    return jsonify({"status": "success"})

@routes_system.route('/api/cookie/save', methods=['POST'])
def save_cookie_endpoint():
    """API lưu Cookie đăng nhập mới từ frontend và lập tức ngắt luồng cào cũ"""
    import manager
    import fetcher
    
    data = request.json or {}
    cookie_payload = data.get("cookie") or data.get("crawler_cookie")
    if not cookie_payload:
        return jsonify({"status": "error", "message": "Thiếu dữ liệu cookie."}), 400
        
    try:
        # Ngắt tiến trình cào cũ ngay lập tức bằng cách kích hoạt cờ dừng
        fetcher.STOP_REQUESTED = True
        
        # Ghi cookie mới vào file COOKIE_FILE
        with open(manager.COOKIE_FILE, "w", encoding="utf-8") as f:
            f.write(cookie_payload.strip())
            
        # Xóa sạch logs cũ tránh nhảy báo động hết hạn lặp lại ở UI
        with manager.LOGS_LOCK:
            manager.LOGS_BUFFER.clear()
            
        manager.add_log_message("[🔑] ĐÃ CẬP NHẬT ĐỒNG BỘ COOKIE MỚI VÀ LÀM SẠCH NHẬT KÝ LỖI!")
        return jsonify({"status": "success", "message": "Đã lưu cookie thành công!"})
    except Exception as e:
        manager.add_log_message(f"[❌ LỖI] Không thể ghi file cookie: {str(e)}")
        return jsonify({"status": "error", "message": f"Không thể ghi file cookie: {str(e)}"}), 500


@routes_system.route('/system')
def system_dashboard():
    """Trả về giao diện quản trị hệ thống và CSDL nội bộ"""
    import os
    from flask import Response
    if os.path.exists("system.html"):
        with open("system.html", "r", encoding="utf-8") as f:
            content = f.read()
    else:
        return "system.html not found", 404
    resp = Response(content, mimetype='text/html')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


@routes_system.route('/api/system/status', methods=['GET'])
def system_status():
    import manager
    import os
    import sqlite3
    from datetime import datetime
    
    cfg = manager.load_config()
    is_staging = os.environ.get("STAGING") == "true"
    is_pool2 = (cfg.get("active_pool_system") == "Pool2")
    
    active_mode = "PRODUCTION"
    if is_staging:
        active_mode = "STAGING"
    elif is_pool2:
        active_mode = "POOL2 (V2)"
        
    db_files = ["raw_archive.db", "raw_archive_staging.db", "raw_archive_v2.db"]
    db_status = {}
    
    for f in db_files:
        path = os.path.join(manager.PROJECT_ROOT, f)
        exists = os.path.exists(path)
        size = 0
        mtime = ""
        total_listings = 0
        raw_json_count = 0
        
        if exists:
            size = os.path.getsize(path)
            mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
            try:
                conn = sqlite3.connect(path, timeout=5.0)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings'")
                if cursor.fetchone():
                    total_listings = cursor.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
                    raw_json_count = cursor.execute("SELECT COUNT(*) FROM listings WHERE raw_json_full IS NOT NULL AND raw_json_full != ''").fetchone()[0]
                conn.close()
            except Exception:
                pass
                
        db_status[f] = {
            "exists": exists,
            "size_mb": round(size / (1024 * 1024), 2),
            "modified": mtime,
            "total_listings": total_listings,
            "raw_json_count": raw_json_count
        }
        
    backup_dir = "d:/LHTBrain/BDS_Backups"
    backups = []
    if os.path.exists(backup_dir):
        try:
            backups = sorted([
                {
                    "name": f,
                    "size_mb": round(os.path.getsize(os.path.join(backup_dir, f)) / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(os.path.getmtime(os.path.join(backup_dir, f))).strftime("%Y-%m-%d %H:%M:%S")
                }
                for f in os.listdir(backup_dir) if f.startswith("raw_archive_backup_")
            ], key=lambda x: x["created"], reverse=True)
        except Exception:
            pass
            
    safe_cfg = {}
    for k, v in cfg.items():
        if any(sec in k.lower() for sec in ["key", "secret", "password", "token"]):
            safe_cfg[k] = "••••••••••••"
        else:
            safe_cfg[k] = v
            
    return jsonify({
        "status": "success",
        "active_mode": active_mode,
        "db_status": db_status,
        "backups": backups,
        "config": safe_cfg
    })


@routes_system.route('/api/system/run-action', methods=['POST'])
def run_system_action():
    import manager
    import threading
    import os
    
    data = request.json or {}
    action = data.get("action")
    
    if action not in ["restore_prd", "restore_stg", "recover_raw_json", "restore_r2_dry", "restore_r2_real"]:
        return jsonify({"status": "error", "message": "Hành động không hợp lệ."}), 400
        
    def worker():
        try:
            manager.add_log_message(f"[⚙️ Hệ thống] Bắt đầu thực hiện hành động: {action}...")
            
            if action == "restore_prd":
                os.environ["STAGING"] = "false"
                from restore_db_from_sheets import restore_database
                restore_database()
                manager.add_log_message("[✅ Thành công] Hoàn tất khôi phục CSDL Production từ Google Sheets!")
                
            elif action == "restore_stg":
                os.environ["STAGING"] = "true"
                from restore_db_from_sheets import restore_database
                restore_database()
                manager.add_log_message("[✅ Thành công] Hoàn tất khôi phục CSDL Staging từ Google Sheets!")
                
            elif action == "recover_raw_json":
                from scratch.recover_raw_json import recover_data
                recover_data()
                manager.add_log_message("[✅ Thành công] Hoàn tất cứu hộ dữ liệu raw_json_full từ Backup!")
                
            elif action == "restore_r2_dry":
                import builtins
                from scratch.restore_missing_photos import main as restore_photos_main
                
                target_ids_str = data.get("target_ids", "").strip()
                target_ids = [x.strip().upper() for x in target_ids_str.split(",") if x.strip()] if target_ids_str else None
                
                original_print = builtins.print
                def custom_print(*args, **kwargs):
                    msg = " ".join(str(arg) for arg in args)
                    manager.add_log_message(msg)
                    original_print(*args, **kwargs)
                builtins.print = custom_print
                
                try:
                    restore_photos_main(dry_run=True, limit=5, all_flag=False, target_khang_ngo_ids=target_ids)
                    manager.add_log_message("[✅ Thành công] Hoàn tất mô phỏng khôi phục ảnh R2!")
                finally:
                    builtins.print = original_print
                    
            elif action == "restore_r2_real":
                import builtins
                from scratch.restore_missing_photos import main as restore_photos_main
                
                target_ids_str = data.get("target_ids", "").strip()
                target_ids = [x.strip().upper() for x in target_ids_str.split(",") if x.strip()] if target_ids_str else None
                
                original_print = builtins.print
                def custom_print(*args, **kwargs):
                    msg = " ".join(str(arg) for arg in args)
                    manager.add_log_message(msg)
                    original_print(*args, **kwargs)
                builtins.print = custom_print
                
                try:
                    restore_photos_main(dry_run=False, limit=5, all_flag=False, target_khang_ngo_ids=target_ids)
                    manager.add_log_message("[✅ Thành công] Hoàn tất khôi phục ảnh R2 lên Google Sheets!")
                finally:
                    builtins.print = original_print
                
        except Exception as e:
            manager.add_log_message(f"[❌ LỖI] Gặp lỗi khi thực hiện hành động {action}: {str(e)}")
            
    threading.Thread(target=worker, daemon=True).start()
    
    return jsonify({
        "status": "success",
        "message": f"Đã kích hoạt hành động '{action}' chạy ngầm thành công. Theo dõi log tiến trình ở console."
    })
