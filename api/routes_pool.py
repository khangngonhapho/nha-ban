# -*- coding: utf-8 -*-
"""
Pool and listings management routes for BDS KhangNgo.
Handles listings retrieval, CRUD operations on single listings, diff applications, and listing deletions.
"""

import os
import json
import sqlite3
import re
from flask import Blueprint, jsonify, request

routes_pool = Blueprint('routes_pool', __name__)

@routes_pool.route('/api/listings/clear', methods=['POST'])
def clear_all_listings():
    """Xóa toàn bộ listings khỏi SQLite và dọn dẹp thư mục ảnh cục bộ"""
    import manager
    if not os.path.exists(manager.DB_FILE):
        return jsonify({"status": "success", "message": "Database đã trống."})
        
    try:
        conn = sqlite3.connect(manager.DB_FILE, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {manager.LISTINGS_TABLE}")
        # Reset autoincrement
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{manager.LISTINGS_TABLE}'")
        conn.commit()
        conn.close()
        
        # Dọn dẹp thư mục ảnh static/images
        images_dir = os.path.join("static", "images")
        if os.path.exists(images_dir):
            import shutil
            for filename in os.listdir(images_dir):
                filepath = os.path.join(images_dir, filename)
                try:
                    if os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                    else:
                        os.unlink(filepath)
                except Exception:
                    pass
                    
        manager.add_log_message("[🧹] ĐÃ XÓA SẠCH TOÀN BỘ DỮ LIỆU CRAWL VÀ HÌNH ẢNH CỤC BỘ THÀNH CÔNG!")
        return jsonify({"status": "success", "message": "Đã xóa sạch toàn bộ dữ liệu cào cũ và hình ảnh thành công!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Không thể xóa dữ liệu: {str(e)}"}), 500

@routes_pool.route('/api/listings', methods=['GET'])
def get_listings():
    """API lấy danh sách các căn từ SQLite với đầy đủ metadata"""
    import manager
    if not os.path.exists(manager.DB_FILE):
        return jsonify({"listings": []})
        
    status_filter = request.args.get("status")
    search_q = request.args.get("search")
    
    quan_filter = request.args.get("quan")
    duong_filter = request.args.get("duong")
    so_nha_filter = request.args.get("so_nha")
    
    conn = sqlite3.connect(manager.DB_FILE, timeout=30.0)
    # Trả về kết quả dạng Dict
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Lấy danh sách cột thực tế của bảng listings để chống lỗi lệch cột/font chữ gạch dưới
    try:
        cursor.execute(f"PRAGMA table_info({manager.LISTINGS_TABLE})")
        db_cols = [r[1] for r in cursor.fetchall()]
    except Exception:
        db_cols = []
        
    quan_col = next((c for c in db_cols if c in ["Quan", "Qu_n"]), "Quan")
    duong_col = next((c for c in db_cols if c in ["streetName", "Duong", "___ng"]), "Duong")
    so_nha_col = next((c for c in db_cols if c in ["Ngo_So_nha", "Ng__S__nh_"]), "Ngo_So_nha")
    
    t_prefix = "listings_v2." if manager.LISTINGS_TABLE == "listings_v2" else ""
    if manager.LISTINGS_TABLE == "listings_v2":
        sql = """
            SELECT listings_v2.*, 
                   listings_custom_v2.Ma_Khang_Ngo AS custom_Ma_Khang_Ngo, 
                   listings_custom_v2.Gia_Public AS custom_Gia_Public, 
                   listings_custom_v2.Tieu_De_Public AS custom_Tieu_De_Public, 
                   listings_custom_v2.Mo_ta_Public AS custom_Mo_ta_Public, 
                   listings_custom_v2.Note_Noi_Bo AS custom_Note_Noi_Bo, 
                   listings_custom_v2.Trang_Thai_Giao_Dich AS custom_Trang_Thai_Giao_Dich, 
                   listings_custom_v2.Ngu_Tret AS custom_Ngu_Tret, 
                   listings_custom_v2.CHDV AS custom_CHDV, 
                   listings_custom_v2.Trang_Thai_KN AS custom_Trang_Thai_KN, 
                   listings_custom_v2.images_metadata_json AS custom_images_metadata_json, 
                   listings_custom_v2.Dia_Chi_That AS custom_Dia_Chi_That, 
                   listings_custom_v2.So_Nha AS custom_So_Nha, 
                   listings_custom_v2.Ten_Duong AS custom_Ten_Duong,
                   listings_custom_v2.bedrooms AS custom_bedrooms,
                   listings_custom_v2.restrooms AS custom_restrooms,
                   listings_custom_v2.minimumRoadWidth AS custom_minimumRoadWidth,
                   listings_custom_v2.Noi_dung_chinh AS custom_Noi_dung_chinh,
                   listings_custom_v2.Mo_ta_chi_tiet AS custom_Mo_ta_chi_tiet,
                   listings_custom_v2.Gia_chao AS custom_Gia_chao,
                   listings_custom_v2.DT_Thuc_te AS custom_DT_Thuc_te,
                   listings_custom_v2.DT_Tren_so AS custom_DT_Tren_so,
                   listings_custom_v2.So_Tang AS custom_So_Tang,
                   listings_custom_v2.Mat_Tien AS custom_Mat_Tien,
                   listings_custom_v2.Chieu_dai AS custom_Chieu_dai,
                   listings_custom_v2.Huong AS custom_Huong,
                   listings_custom_v2.Criteria_Duong_truoc_nha AS custom_Criteria_Duong_truoc_nha,
                   listings_custom_v2.Criteria_Noi_that AS custom_Criteria_Noi_that,
                   listings_custom_v2.Criteria_Thang_may AS custom_Criteria_Thang_may,
                   listings_custom_v2.Criteria_Loai_ngo AS custom_Criteria_Loai_ngo,
                   listings_custom_v2.Criteria_Khoang_cach_bai_do_xe AS custom_Criteria_Khoang_cach_bai_do_xe,
                   listings_custom_v2.Criteria_Kinh_doanh_Dong_tien AS custom_Criteria_Kinh_doanh_Dong_tien,
                   listings_custom_v2.Criteria_Huong_nha AS custom_Criteria_Huong_nha,
                   listings_custom_v2.Criteria_Khoang_cach_duong_oto AS custom_Criteria_Khoang_cach_duong_oto
            FROM listings_v2 
            LEFT JOIN listings_custom_v2 ON listings_v2.System_ID = listings_custom_v2.System_ID
        """
    else:
        sql = f"SELECT * FROM {manager.LISTINGS_TABLE}"

    conditions = []
    params = []
    
    if status_filter:
        if status_filter == "crawl_failed":
            conditions.append(f"{t_prefix}status LIKE 'crawl_failed:%'")
        elif status_filter == "missing_raw_json":
            if "raw_json_full" in db_cols:
                conditions.append(f"({t_prefix}raw_json_full IS NULL OR {t_prefix}raw_json_full = '')")
            else:
                conditions.append("1=0")
        else:
            conditions.append(f"{t_prefix}status = ?")
            params.append(status_filter)
        
    if search_q:
        # Tự động trích xuất UUID hoặc mã hàng số từ URL nếu người dùng dán cả link
        uuid_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', search_q, re.I)
        detail_match = re.search(r'/Detail/(\d+)', search_q, re.I)
        
        extracted_id = None
        if uuid_match:
            extracted_id = uuid_match.group(0)
        elif detail_match:
            extracted_id = detail_match.group(1)
            
        if extracted_id:
            conditions.append(f"({t_prefix}tk_id = ? OR {t_prefix}tk_id LIKE ? OR {t_prefix}Ma_Hang LIKE ? OR {t_prefix}`{quan_col}` LIKE ? OR {t_prefix}`{duong_col}` LIKE ? OR {t_prefix}`{so_nha_col}` LIKE ?)")
            search_like = f"%{search_q}%"
            params.extend([extracted_id, search_like, search_like, search_like, search_like, search_like])
        else:
            conditions.append(f"({t_prefix}tk_id LIKE ? OR {t_prefix}Ma_Hang LIKE ? OR {t_prefix}`{quan_col}` LIKE ? OR {t_prefix}`{duong_col}` LIKE ? OR {t_prefix}`{so_nha_col}` LIKE ?)")
            search_like = f"%{search_q}%"
            params.extend([search_like, search_like, search_like, search_like, search_like])
        
    if quan_filter:
        conditions.append(f"{t_prefix}`{quan_col}` LIKE ?")
        params.append(f"%{quan_filter}%")
        
    if duong_filter:
        conditions.append(f"{t_prefix}`{duong_col}` LIKE ?")
        params.append(f"%{duong_filter}%")
        
    if so_nha_filter:
        conditions.append(f"{t_prefix}`{so_nha_col}` LIKE ?")
        params.append(f"%{so_nha_filter}%")
        
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
        
    # Mặc định sắp xếp mới nhất lên trước
    if manager.LISTINGS_TABLE == "listings_v2":
        sql += " ORDER BY listings_v2.rowid DESC"
    else:
        sql += " ORDER BY rowid DESC"
    
    rows = cursor.execute(sql, params).fetchall()
    conn.close()
    
    listings = [manager.normalize_listing_for_client(r) for r in rows]
        
    # Tính toán số lượng căn theo từng trạng thái (status) toàn cục
    counts = {"raw_text": 0, "raw_complete": 0, "published": 0, "crawl_failed": 0, "missing_raw_json": 0}
    if os.path.exists(manager.DB_FILE):
        try:
            conn_count = sqlite3.connect(manager.DB_FILE, timeout=30.0)
            cursor_count = conn_count.cursor()
            for s in ["raw_text", "raw_complete", "published"]:
                c = cursor_count.execute(f"SELECT COUNT(*) FROM {manager.LISTINGS_TABLE} WHERE status = ?", (s,)).fetchone()[0]
                counts[s] = c
            # Thêm đếm số lượng căn lỗi cào
            c_failed = cursor_count.execute(f"SELECT COUNT(*) FROM {manager.LISTINGS_TABLE} WHERE status LIKE 'crawl_failed:%'").fetchone()[0]
            counts["crawl_failed"] = c_failed
            
            # Đếm số lượng căn thiếu raw_json_full
            cursor_count.execute(f"PRAGMA table_info({manager.LISTINGS_TABLE})")
            cols = [r[1] for r in cursor_count.fetchall()]
            if "raw_json_full" in cols:
                c_missing = cursor_count.execute(f"SELECT COUNT(*) FROM {manager.LISTINGS_TABLE} WHERE raw_json_full IS NULL OR raw_json_full = ''").fetchone()[0]
                counts["missing_raw_json"] = c_missing
            else:
                counts["missing_raw_json"] = 0
                
            conn_count.close()
        except Exception:
            pass
            
    return jsonify({
        "listings": listings,
        "status_counts": counts
    })

@routes_pool.route('/api/listings/check-exist', methods=['POST'])
def check_listings_exist():
    """Kiểm tra danh sách tk_id xem có tồn tại trong database local không (tối ưu hóa hiệu năng)"""
    import manager
    data = request.json or {}
    tk_ids = data.get("tk_ids", [])
    if not tk_ids:
        return jsonify({"exists": []})
        
    if not os.path.exists(manager.DB_FILE):
        return jsonify({"exists": []})
        
    # Lọc bỏ giá trị không hợp lệ
    tk_ids = [str(x).strip() for x in tk_ids if x]
    if not tk_ids:
        return jsonify({"exists": []})
        
    try:
        conn = sqlite3.connect(manager.DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        # Tạo câu truy vấn IN với tham số an toàn
        placeholders = ",".join(["?"] * len(tk_ids))
        sql = f"SELECT tk_id FROM {manager.LISTINGS_TABLE} WHERE tk_id IN ({placeholders})"
        rows = cursor.execute(sql, tk_ids).fetchall()
        conn.close()
        
        exists_ids = [r[0] for r in rows if r[0]]
        return jsonify({"exists": exists_ids})
    except Exception as e:
        manager.add_log_message(f"[⚠️ WARNING] Lỗi kiểm tra tồn tại căn: {str(e)}")
        return jsonify({"exists": [], "error": str(e)}), 500

@routes_pool.route('/api/listings/<tk_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_listing_detail(tk_id):
    """Lấy chi tiết hoặc cập nhật cấu hình biên tập cho 1 căn"""
    import manager
    import pool_lego
    from pool_lego import gen_id_khang_ngo_python, get_safe_col_name
    
    if not os.path.exists(manager.DB_FILE):
        return jsonify({"status": "error", "message": "Database không tồn tại"}), 404
        
    conn = sqlite3.connect(manager.DB_FILE, timeout=30.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if manager.LISTINGS_TABLE == "listings_v2":
        sql = """
            SELECT listings_v2.*, 
                   listings_custom_v2.Ma_Khang_Ngo AS custom_Ma_Khang_Ngo, 
                   listings_custom_v2.Gia_Public AS custom_Gia_Public, 
                   listings_custom_v2.Tieu_De_Public AS custom_Tieu_De_Public, 
                   listings_custom_v2.Mo_ta_Public AS custom_Mo_ta_Public, 
                   listings_custom_v2.Note_Noi_Bo AS custom_Note_Noi_Bo, 
                   listings_custom_v2.Trang_Thai_Giao_Dich AS custom_Trang_Thai_Giao_Dich, 
                   listings_custom_v2.Ngu_Tret AS custom_Ngu_Tret, 
                   listings_custom_v2.CHDV AS custom_CHDV, 
                   listings_custom_v2.Trang_Thai_KN AS custom_Trang_Thai_KN, 
                   listings_custom_v2.images_metadata_json AS custom_images_metadata_json, 
                   listings_custom_v2.Dia_Chi_That AS custom_Dia_Chi_That, 
                   listings_custom_v2.So_Nha AS custom_So_Nha, 
                   listings_custom_v2.Ten_Duong AS custom_Ten_Duong,
                   listings_custom_v2.bedrooms AS custom_bedrooms,
                   listings_custom_v2.restrooms AS custom_restrooms,
                   listings_custom_v2.minimumRoadWidth AS custom_minimumRoadWidth,
                   listings_custom_v2.Noi_dung_chinh AS custom_Noi_dung_chinh,
                   listings_custom_v2.Mo_ta_chi_tiet AS custom_Mo_ta_chi_tiet,
                   listings_custom_v2.Gia_chao AS custom_Gia_chao,
                   listings_custom_v2.DT_Thuc_te AS custom_DT_Thuc_te,
                   listings_custom_v2.DT_Tren_so AS custom_DT_Tren_so,
                   listings_custom_v2.So_Tang AS custom_So_Tang,
                   listings_custom_v2.Mat_Tien AS custom_Mat_Tien,
                   listings_custom_v2.Chieu_dai AS custom_Chieu_dai,
                   listings_custom_v2.Huong AS custom_Huong,
                   listings_custom_v2.Criteria_Duong_truoc_nha AS custom_Criteria_Duong_truoc_nha,
                   listings_custom_v2.Criteria_Noi_that AS custom_Criteria_Noi_that,
                   listings_custom_v2.Criteria_Thang_may AS custom_Criteria_Thang_may,
                   listings_custom_v2.Criteria_Loai_ngo AS custom_Criteria_Loai_ngo,
                   listings_custom_v2.Criteria_Khoang_cach_bai_do_xe AS custom_Criteria_Khoang_cach_bai_do_xe,
                   listings_custom_v2.Criteria_Kinh_doanh_Dong_tien AS custom_Criteria_Kinh_doanh_Dong_tien,
                   listings_custom_v2.Criteria_Huong_nha AS custom_Criteria_Huong_nha,
                   listings_custom_v2.Criteria_Khoang_cach_duong_oto AS custom_Criteria_Khoang_cach_duong_oto
            FROM listings_v2 
            LEFT JOIN listings_custom_v2 ON listings_v2.System_ID = listings_custom_v2.System_ID
            WHERE listings_v2.tk_id = ?
        """
        row = cursor.execute(sql, (tk_id,)).fetchone()
    else:
        row = cursor.execute(f"SELECT * FROM {manager.LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
    
    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "Mã căn không tồn tại"}), 404
        
    if request.method == 'DELETE':
        cursor.execute(f"DELETE FROM {manager.LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,))
        conn.commit()
        conn.close()
        
        # Xóa folder ảnh cục bộ
        local_dir = os.path.join("static", "images", tk_id)
        if os.path.exists(local_dir):
            import shutil
            try:
                shutil.rmtree(local_dir)
            except Exception:
                pass
                
        manager.add_log_message(f"[🧹] Đã xóa thành công căn {tk_id} khỏi database SQLite cục bộ!")
        return jsonify({"status": "success", "message": f"Đã xóa thành công căn {tk_id}"})
        
    if request.method == 'PUT':
        # CẬP NHẬT CẤU HÌNH BIÊN TẬP
        data = request.json
        curated_config = data.get("curated_config")
        
        # 1. Cập nhật bảng listings_images và tạo cấu trúc JSON hình ảnh mới
        images_mapping = {}
        system_id = ""
        try:
            row_db = cursor.execute("SELECT images_mapping_json, System_ID FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
            if row_db:
                system_id = row_db[1] or ""
                if row_db[0]:
                    images_mapping = json.loads(row_db[0])
        except Exception:
            pass
            
        r2_to_orig = {v: k for k, v in images_mapping.items() if v}
        
        cfg_settings = {}
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r", encoding="utf-8") as f:
                    cfg_settings = json.load(f)
            except Exception:
                pass
        r2_public_url = cfg_settings.get("r2_public_url", "")
        
        role_map_vi_to_en = {
            "Sơ đồ": "diagram",
            "Mặt tiền": "facade",
            "Bìa": "cover",
            "Hẻm": "alley",
            "Nội thất": "interior",
            "Ẩn": "hidden",
            "diagram": "diagram",
            "facade": "facade",
            "cover": "cover",
            "alley": "alley",
            "interior": "interior",
            "hidden": "hidden",
            "deleted": "deleted"
        }
        
        migrated_images = []
        images_list = curated_config.get("images", []) if isinstance(curated_config, dict) else []
        for idx, img in enumerate(images_list):
            if not isinstance(img, dict) or not img.get("url"):
                continue
            url = img.get("url").strip()
            vi_role = img.get("role", "Nội thất")
            resolved_role = role_map_vi_to_en.get(vi_role, "interior")
            visible = img.get("visible", True)
            
            # Phân loại origin
            filename = os.path.basename(url)
            origin = "crawl"
            if filename.startswith("SYS-") or img.get("origin") == "self":
                origin = "self"
                
            # Phân biệt r2_url vs image_url
            is_r2 = False
            if r2_public_url and r2_public_url in url:
                is_r2 = True
            elif "r2.dev" in url or "r2.cloudflarestorage.com" in url:
                is_r2 = True
                
            if is_r2:
                r2_url = url
                image_url = r2_to_orig.get(r2_url, r2_url)
            else:
                image_url = url
                r2_url = images_mapping.get(image_url, None)
                
            is_hidden_val = 1 if (not visible or resolved_role in ["hidden", "deleted"]) else 0
            migrated_images.append({
                "image_url": image_url,
                "r2_url": r2_url,
                "role": resolved_role,
                "sequence_index": idx,
                "origin": origin,
                "is_hidden": is_hidden_val
            })
            
        try:
            # Xóa các bản ghi cũ và lưu lại các bản ghi mới
            cursor.execute("DELETE FROM listings_images WHERE tk_id = ?", (tk_id,))
            for img in migrated_images:
                cursor.execute("""
                    INSERT INTO listings_images (tk_id, system_id, image_url, r2_url, role, sequence_index, origin, is_hidden)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tk_id,
                    system_id,
                    img["image_url"],
                    img["r2_url"],
                    img["role"],
                    img["sequence_index"],
                    img["origin"],
                    img["is_hidden"]
                ))
        except Exception as e_img_save:
            manager.add_log_message(f"[⚠️ WARNING] Không thể ghi nhận bảng listings_images: {str(e_img_save)}")
            
        images_admin_json_str = json.dumps(migrated_images, ensure_ascii=False)
        
        public_urls = [
            img["r2_url"] if img["r2_url"] else img["image_url"]
            for img in migrated_images
            if img["is_hidden"] == 0 and img["role"] not in ["facade", "diagram", "deleted", "hidden"]
        ]
        images_public_json_str = json.dumps(public_urls, ensure_ascii=False)
        
        # Cập nhật cột JSON và cấu hình chính
        cursor.execute(
            f"UPDATE {manager.LISTINGS_TABLE} SET curated_config_json = ?, images_admin_json = ?, images_public_json = ? WHERE tk_id = ?",
            (json.dumps(curated_config, ensure_ascii=False), images_admin_json_str, images_public_json_str, tk_id)
        )

        # Cập nhật manual_images_json cho Pool1 (đồng bộ nếu có ảnh thủ công bị xóa khỏi curated_config)
        if manager.LISTINGS_TABLE == "listings" and curated_config and isinstance(curated_config, dict):
            row_db = cursor.execute("SELECT manual_images_json FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
            current_manual_json = row_db[0] if row_db else None
            try:
                current_manual = json.loads(current_manual_json) if current_manual_json else []
            except Exception:
                current_manual = []
                
            if current_manual:
                curated_urls = {img.get("url") for img in curated_config.get("images", []) if isinstance(img, dict) and img.get("url")}
                updated_manual = [url for url in current_manual if url in curated_urls]
                cursor.execute(
                    "UPDATE listings SET manual_images_json = ? WHERE tk_id = ?",
                    (json.dumps(updated_manual, ensure_ascii=False), tk_id)
                )
        
        # Cập nhật các trường chỉnh sửa của admin vào các cột tương ứng
        fields_to_update = {
            "Tiêu đề Public": manager.trim_tieu_de_bds(data.get("tieu_de_public")),
            "Mô tả Public": data.get("mo_ta_public"),
            "Giá Public": data.get("gia_public"),
            "Mã Khang Ngô (ID)": data.get("ma_khang_ngo"),
            "Phân loại Hẻm": data.get("phan_loai_hem"),
            "Đường trước nhà (m)": data.get("duong_truoc_nha"),
            "Mặt Tiền": data.get("mat_tien"),
            "Chiều dài": data.get("chieu_dai"),
            "Tình trạng nhà": data.get("tinh_trang_nha"),
            "Số phòng ngủ": data.get("so_phong_ngu"),
            "Số nhà vệ sinh": data.get("so_nha_ve_sinh"),
            "Đánh giá (Admin)": data.get("danh_gia"),
            "Ngủ trệt (Admin)": data.get("ngu_tret"),
            "CHDV (Admin)": data.get("chdv"),
            "Phường cũ (AI)": data.get("phuong_cu_ai"),
            "custom_huong": data.get("custom_huong"),
            "custom_dt_so": data.get("custom_dt_so"),
            "custom_dt_thuc_te": data.get("custom_dt_thuc_te"),
            # Thực tế địa chỉ chỉnh sửa
            "Ngõ/Số nhà": data.get("ngo_so_nha"),
            "Quận": data.get("quan"),
            "Phường": data.get("phuong"),
            "Đường": data.get("duong"),
            # Link ảnh chi tiết đã chọn nhãn
            "Hình Nhận Diện": data.get("hinh_nhan_dien"),
            "Hình Mặt Tiền": data.get("hinh_mat_tien"),
            "Sơ đồ thửa đất 1": data.get("so_do_1"),
            "Sơ đồ thửa đất 2": data.get("so_do_2"),
            "Sơ đồ thửa đất 3": data.get("so_do_3"),
            "Sơ đồ thửa đất 4": data.get("so_do_4"),
            "Sơ đồ thửa đất 5": data.get("so_do_5"),
            "Ảnh Public (VD: 1,3,5)": data.get("anh_public_vd_1_3_5"),
            "Ảnh Hẻm Public (VD: 1,2)": data.get("anh_hem_public_vd_1_2")
        }
        
        # Cập nhật các cột Hẻm 1-10
        hem_imgs = data.get("hem_imgs", [])
        for i in range(10):
            col_name = f"Hình Hẻm {i+1}"
            fields_to_update[col_name] = hem_imgs[i] if i < len(hem_imgs) else ""
            
        # Cập nhật các cột Ảnh 1-25
        public_imgs = data.get("public_imgs", [])
        for i in range(25):
            col_name = f"Ảnh {i+1}"
            fields_to_update[col_name] = public_imgs[i] if i < len(public_imgs) else ""
            
        # Lấy danh sách cột thực tế của bảng SQLite mục tiêu để lọc cột động
        cursor.execute(f"PRAGMA table_info({manager.LISTINGS_TABLE})")
        db_cols = {row[1] for row in cursor.fetchall()}

        # Xây dựng câu lệnh Update SQL động
        update_cols = []
        update_vals = []
        for key, val in fields_to_update.items():
            safe_col = get_safe_col_name(key)
            if safe_col in db_cols:
                update_cols.append(f"`{safe_col}` = ?")
                update_vals.append(str(val) if val is not None else "")
            
        if update_cols:
            update_vals.append(tk_id)
            update_sql = f"UPDATE {manager.LISTINGS_TABLE} SET {', '.join(update_cols)} WHERE tk_id = ?"
            cursor.execute(update_sql, update_vals)
        
        # Nếu đang ở chế độ Pool2, đồng bộ cập nhật vào bảng listings_custom_v2
        if manager.LISTINGS_TABLE == "listings_v2":
            try:
                row_v2 = cursor.execute("SELECT * FROM listings_v2 WHERE tk_id = ?", (tk_id,)).fetchone()
                if row_v2:
                    d_v2 = dict(row_v2)
                    system_id = d_v2.get("System_ID")
                    if system_id:
                        # Kiểm tra xem đã tồn tại System_ID trong listings_custom_v2 chưa
                        custom_exists = cursor.execute(
                            "SELECT 1 FROM listings_custom_v2 WHERE System_ID = ?", (system_id,)
                        ).fetchone()
                        
                        # Trích xuất danh sách ảnh an toàn từ curated_config
                        images_metadata = []
                        if curated_config and isinstance(curated_config, dict):
                            images_list = curated_config.get("images", [])
                            safe_roles = ["interior", "alley", "cover", "interior_public", "alley_public"]
                            images_metadata = [img for img in images_list if img.get("role") in safe_roles or not img.get("role")]
                        
                        # Điền thông tin vào listings_custom_v2
                        custom_data = {
                            "System_ID": system_id,
                            "Ma_Khang_Ngo": data.get("ma_khang_ngo") or d_v2.get("Ma_Khang_Ngo_ID") or "",
                            "Gia_Public": data.get("gia_public") or d_v2.get("Gia_Public") or "",
                            "Tieu_De_Public": manager.trim_tieu_de_bds(data.get("tieu_de_public")) or d_v2.get("Tieu_de_Public") or "",
                            "Mo_ta_Public": data.get("mo_ta_public") or d_v2.get("Mo_ta_Public") or "",
                            "Note_Noi_Bo": data.get("note_noi_bo") or d_v2.get("Note_Noi_Bo") or "",
                            "Trang_Thai_Giao_Dich": data.get("tinh_trang_nha") or d_v2.get("Tinh_trang_nha") or "",
                            "Ngu_Tret": data.get("ngu_tret") or d_v2.get("Ngu_tret_Admin") or "",
                            "CHDV": data.get("chdv") or d_v2.get("CHDV_Admin") or "",
                            "Trang_Thai_KN": data.get("danh_gia") or d_v2.get("Danh_gia_Admin") or "",
                            "images_metadata_json": json.dumps(images_metadata),
                            "Dia_Chi_That": d_v2.get("Dia_Chi_That") or "",
                            "So_Nha": data.get("ngo_so_nha") or d_v2.get("Ngo_So_nha") or "",
                            "Ten_Duong": data.get("duong") or d_v2.get("Duong") or "",
                            "Quan": data.get("quan") or d_v2.get("Quan") or "",
                            "Phuong": data.get("phuong") or d_v2.get("Phuong") or "",
                            "Duong": data.get("duong") or d_v2.get("Duong") or "",
                            "Ngo_So_nha": data.get("ngo_so_nha") or d_v2.get("Ngo_So_nha") or "",
                            "bedrooms": data.get("so_phong_ngu") or d_v2.get("bedrooms") or d_v2.get("So_phong_ngu") or "",
                            "restrooms": data.get("so_nha_ve_sinh") or d_v2.get("restrooms") or d_v2.get("So_nha_ve_sinh") or "",
                            "minimumRoadWidth": data.get("duong_truoc_nha") or d_v2.get("minimumRoadWidth") or d_v2.get("Duong_truoc_nha_m") or "",
                            "Noi_dung_chinh": d_v2.get("Noi_dung_chinh") or "",
                            "Mo_ta_chi_tiet": d_v2.get("Mo_ta_chi_tiet") or "",
                            "Gia_chao": d_v2.get("Gia_chao") or "",
                            "DT_Thuc_te": d_v2.get("DT_Thuc_te") or "",
                            "DT_Tren_so": d_v2.get("DT_Tren_so") or "",
                            "So_Tang": d_v2.get("So_Tang") or "",
                            "Mat_Tien": data.get("mat_tien") or d_v2.get("Mat_Tien") or "",
                            "Chieu_dai": data.get("chieu_dai") or d_v2.get("Chieu_dai") or "",
                            "Huong": d_v2.get("Huong") or "",
                            "Criteria_Duong_truoc_nha": data.get("phan_loai_hem") or d_v2.get("Criteria_Duong_truoc_nha") or "",
                            "Criteria_Noi_that": d_v2.get("Criteria_Noi_that") or "",
                            "Criteria_Thang_may": d_v2.get("Criteria_Thang_may") or "",
                            "Criteria_Loai_ngo": d_v2.get("Criteria_Loai_ngo") or "",
                            "Criteria_Khoang_cach_bai_do_xe": d_v2.get("Criteria_Khoang_cach_bai_do_xe") or "",
                            "Criteria_Kinh_doanh_Dong_tien": d_v2.get("Criteria_Kinh_doanh_Dong_tien") or "",
                            "Criteria_Huong_nha": d_v2.get("Criteria_Huong_nha") or "",
                            "Criteria_Khoang_cach_duong_oto": d_v2.get("Criteria_Khoang_cach_duong_oto") or "",
                        }
                        
                        # Lấy danh sách cột thực tế của listings_custom_v2 đề phòng lệch schema
                        cursor.execute("PRAGMA table_info(listings_custom_v2)")
                        custom_db_cols = [r[1] for r in cursor.fetchall()]
                        
                        # Lọc bỏ cột không tồn tại
                        valid_custom_data = {k: v for k, v in custom_data.items() if k in custom_db_cols}
                        
                        if custom_exists:
                            # UPDATE
                            update_pairs = []
                            update_custom_vals = []
                            for col_k, col_v in valid_custom_data.items():
                                if col_k != "System_ID":
                                    update_pairs.append(f"`{col_k}` = ?")
                                    update_custom_vals.append(str(col_v) if col_v is not None else "")
                            update_custom_vals.append(system_id)
                            cursor.execute(
                                f"UPDATE listings_custom_v2 SET {', '.join(update_pairs)} WHERE System_ID = ?",
                                update_custom_vals
                            )
                        else:
                            # INSERT
                            cols_list = list(valid_custom_data.keys())
                            placeholders = ["?"] * len(cols_list)
                            insert_vals = [str(valid_custom_data[col_k]) if valid_custom_data[col_k] is not None else "" for col_k in cols_list]
                            cursor.execute(
                                f"INSERT INTO listings_custom_v2 ({', '.join(cols_list)}) VALUES ({', '.join(placeholders)})",
                                insert_vals
                            )
            except Exception as e_custom:
                manager.add_log_message(f"[⚠️ WARNING] Lỗi khi đồng bộ vào bảng listings_custom_v2: {str(e_custom)}")
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": f"Đã lưu biên tập cục bộ cho căn {tk_id}"})
    else:
        # LẤY CHI TIẾT
        d = manager.normalize_listing_for_client(row)
        conn.close()
        return jsonify({"status": "success", "listing": d})

@routes_pool.route('/api/listings/apply-diff', methods=['POST'])
def apply_diff():
    """API áp dụng có chọn lọc các trường thay đổi từ Raw sang Custom"""
    import manager
    try:
        data = request.get_json(force=True) or {}
        system_id = data.get("System_ID")
        fields = data.get("fields", [])
        
        if not system_id or not fields:
            return jsonify({"status": "error", "message": "Thiếu tham số System_ID hoặc danh sách fields."}), 400
            
        conn = sqlite3.connect(manager.DB_FILE, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        raw_row = cursor.execute("SELECT * FROM listings_v2 WHERE System_ID = ?", (system_id,)).fetchone()
        if not raw_row:
            conn.close()
            return jsonify({"status": "error", "message": f"Không tìm thấy căn trong listings_v2 với System_ID {system_id}"}), 404
            
        raw_dict = dict(raw_row)
        
        custom_row = cursor.execute("SELECT * FROM listings_custom_v2 WHERE System_ID = ?", (system_id,)).fetchone()
        
        cursor.execute("PRAGMA table_info(listings_custom_v2)")
        custom_cols = {row[1] for row in cursor.fetchall()}
        
        update_fields = {}
        for f in fields:
            if f in custom_cols:
                update_fields[f] = raw_dict.get(f)
                
        if not update_fields:
            conn.close()
            return jsonify({"status": "error", "message": "Không có trường hợp lệ nào để cập nhật."}), 400
            
        if custom_row:
            set_clause = ", ".join([f"`{k}` = ?" for k in update_fields.keys()])
            vals = list(update_fields.values()) + [system_id]
            cursor.execute(f"UPDATE listings_custom_v2 SET {set_clause} WHERE System_ID = ?", vals)
        else:
            insert_fields = dict(update_fields)
            insert_fields['System_ID'] = system_id
            cols = list(insert_fields.keys())
            vals = list(insert_fields.values())
            placeholders = ", ".join(["?"] * len(cols))
            cursor.execute(f"INSERT INTO listings_custom_v2 ({', '.join([f'`{c}`' for c in cols])}) VALUES ({placeholders})", vals)
            
        cursor.execute("UPDATE listings_v2 SET pending_diff_json = NULL WHERE System_ID = ?", (system_id,))
        conn.commit()
        conn.close()
        
        manager.add_log_message(f"[✅] Đã áp dụng thành công các trường {fields} từ Raw sang Custom cho System ID {system_id}.")
        return jsonify({"status": "success", "message": "Đã áp dụng thay đổi thành công."})
    except Exception as e:
        manager.add_log_message(f"[❌ LỖI] Lỗi khi áp dụng diff: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@routes_pool.route('/api/listings/clear-diff', methods=['POST'])
def clear_diff():
    """API bỏ qua thay đổi của đối tác và xóa pending_diff_json"""
    import manager
    try:
        data = request.get_json(force=True) or {}
        system_id = data.get("System_ID")
        if not system_id:
            return jsonify({"status": "error", "message": "Thiếu tham số System_ID."}), 400
            
        conn = sqlite3.connect(manager.DB_FILE, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("UPDATE listings_v2 SET pending_diff_json = NULL WHERE System_ID = ?", (system_id,))
        conn.commit()
        conn.close()
        
        manager.add_log_message(f"[✅] Đã bỏ qua thay đổi và xoá pending_diff_json cho System ID {system_id}.")
        return jsonify({"status": "success", "message": "Đã xóa bỏ qua thay đổi thành công."})
    except Exception as e:
        manager.add_log_message(f"[❌ LỖI] Lỗi khi clear diff: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@routes_pool.route('/api/listings/existing_ids', methods=['GET'])
def get_existing_listing_ids():
    """Lấy danh sách tất cả tk_id đã cào thành công trong SQLite để đối chiếu lọc trùng"""
    import manager
    if not os.path.exists(manager.DB_FILE):
        return jsonify({"existing_ids": []})
        
    try:
        conn = sqlite3.connect(manager.DB_FILE, timeout=30.0)
        cursor = conn.cursor()
        # Chỉ lấy tk_id của các căn cào thành công (không có lỗi crawl_failed)
        cursor.execute(f"SELECT tk_id FROM {manager.LISTINGS_TABLE} WHERE status IS NULL OR status = '' OR status NOT LIKE 'crawl_failed:%'")
        rows = cursor.fetchall()
        conn.close()
        
        existing_ids = [r[0] for r in rows if r[0]]
        return jsonify({"status": "success", "existing_ids": existing_ids})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
