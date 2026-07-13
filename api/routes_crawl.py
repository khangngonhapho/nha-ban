# -*- coding: utf-8 -*-
"""
Crawling and migration routes for BDS KhangNgo.
Handles background crawlers, image migration triggers, and single-listing recrawls.
"""

import os
import json
import sqlite3
import time
import threading
import queue
from datetime import datetime
from flask import Blueprint, jsonify, request
import fetcher

routes_crawl = Blueprint('routes_crawl', __name__)

ACTIVE_CRAWLER_THREAD = None
ACTIVE_CRAWLER_LOCK = threading.Lock()

# Hàng đợi bộ nhớ CRAWL_TASK_QUEUE và worker thread đã được chuyển hoàn toàn sang background_worker.py
# để độc lập hóa Luồng 2 ra khỏi tiến trình Flask server, tránh sập/nghẽn luồng và xung đột ghi SQLite.


def set_listing_crawl_failed(tk_id, reason):
    import manager
    try:
        conn = sqlite3.connect(manager.DB_FILE, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {manager.LISTINGS_TABLE} SET status = ? WHERE tk_id = ?", (f"crawl_failed:{reason}", tk_id))
        conn.commit()
        conn.close()
    except Exception as e:
        manager.add_log_message(f"[⚠️ WARNING] Lỗi cập nhật trạng thái lỗi cào cho {tk_id}: {str(e)}")

@routes_crawl.route('/api/crawl', methods=['POST'])
def trigger_crawl():
    """Kích hoạt tiến trình cào tin ngầm hoặc lưu Cookie"""
    global ACTIVE_CRAWLER_THREAD
    import manager
    
    data = request.json or {}
    url = data.get("url")
    district = data.get("district")
    limit = data.get("limit")
    start_page = data.get("start_page")
    
    if not url:
        return jsonify({"status": "error", "message": "Thiếu tham số URL danh sách quận."}), 400
        
    # XỬ LÝ LƯU COOKIE TỪ FRONTEND
    if url == 'MOCK_SAVE_ONLY':
        cookie_payload = data.get("cookie")
        if cookie_payload:
            try:
                # Dừng luồng cũ ngay lập tức do cookie đã thay đổi
                fetcher.STOP_REQUESTED = True
                with open(manager.COOKIE_FILE, "w", encoding="utf-8") as f:
                    f.write(cookie_payload.strip())
                # Xóa sạch logs cũ tránh nhảy báo động hết hạn lặp lại ở UI
                with manager.LOGS_LOCK:
                    manager.LOGS_BUFFER.clear()
                manager.add_log_message("[🔑] ĐÃ ĐỒNG BỘ COOKIE THIÊN KHÔI MỚI VÀ DỌN SẠCH LOGS CŨ!")
                return jsonify({"status": "success", "message": "Đã lưu cookie và gửi lệnh dừng tiến trình cũ thành công!"})
            except Exception as e:
                manager.add_log_message(f"[❌ LỖI] Không thể ghi file cookie: {str(e)}")
                return jsonify({"status": "error", "message": f"Không thể ghi file cookie: {str(e)}"}), 500
        return jsonify({"status": "error", "message": "Thiếu dữ liệu cookie."}), 400
        
    # KIỂM TRA VÀ NGẮT TIẾN TRÌNH CŨ NẾU ĐANG CHẠY
    with ACTIVE_CRAWLER_LOCK:
        if ACTIVE_CRAWLER_THREAD and ACTIVE_CRAWLER_THREAD.is_alive():
            manager.add_log_message("[⚠️] Phát hiện tiến trình cào cũ đang chạy. Đang gửi lệnh dừng khẩn cấp...")
            fetcher.STOP_REQUESTED = True
            
            # Đợi luồng cũ dừng tối đa 3 giây
            stopped_successfully = False
            for _ in range(30):
                if not ACTIVE_CRAWLER_THREAD.is_alive():
                    stopped_successfully = True
                    break
                time.sleep(0.1)
                
            if not stopped_successfully:
                manager.add_log_message("[❌] Luồng cũ vẫn chưa dừng hoàn toàn. Vui lòng nhấn nút dán Cookie hoặc tải lại Curator sau 5 giây.")
                return jsonify({
                    "status": "error", 
                    "message": "Tiến trình cào cũ đang chạy và đang được ngắt. Vui lòng đợi 5 giây rồi nhấn Bắt đầu cào lại."
                }), 400
            else:
                manager.add_log_message("[✅] Đã ngắt tiến trình cào cũ thành công. Bắt đầu tiến trình mới...")
                
    # Lấy Cookie từ file cache
    cookie = ""
    if os.path.exists(manager.COOKIE_FILE):
        try:
            with open(manager.COOKIE_FILE, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
        except Exception:
            pass
            
    # Reset cờ STOP_REQUESTED về False và khởi chạy luồng cào mới
    fetcher.STOP_REQUESTED = False
    
    t = threading.Thread(target=manager.run_crawler_thread, args=(url, cookie, district, limit, start_page))
    t.daemon = True
    t.start()
    
    with ACTIVE_CRAWLER_LOCK:
        ACTIVE_CRAWLER_THREAD = t
        
    return jsonify({"status": "success", "message": "Đã khởi động tiến trình cào ngầm mới!"})

@routes_crawl.route('/api/migrate', methods=['POST'])
def trigger_migration():
    """Kích hoạt tiến trình tải ảnh up Drive ngầm"""
    import manager
    
    data = request.json or {}
    limit = data.get("limit")
    
    with manager.MIGRATION_LOCK:
        if manager.IS_MIGRATION_ACTIVE:
            return jsonify({"status": "warning", "message": "Tiến trình di cư hình ảnh hiện đang chạy ngầm rồi!"}), 409
        manager.IS_MIGRATION_ACTIVE = True
    
    cookie = ""
    if os.path.exists(manager.COOKIE_FILE):
        try:
            with open(manager.COOKIE_FILE, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
        except Exception:
            pass
            
    t = threading.Thread(target=manager.run_auto_migration_wrapper_with_limit, args=(limit, cookie))
    t.daemon = True
    t.start()
    
    return jsonify({"status": "success", "message": "Đã bắt đầu di cư hình ảnh lên Drive chạy ngầm!"})

@routes_crawl.route('/api/stop_migration', methods=['POST'])
def stop_migration_endpoint():
    import manager
    manager.SHOULD_STOP_MIGRATION = True
    return jsonify({"status": "success", "message": "Đã gửi yêu cầu dừng di cư hình ảnh."})

@routes_crawl.route('/api/crawl/stop', methods=['POST'])
def stop_crawl_endpoint():
    import fetcher
    import manager
    fetcher.STOP_REQUESTED = True
    manager.add_log_message("[🛑] ĐÃ NHẬN YÊU CẦU DỪNG TIẾN TRÌNH CÀO / QUÉT THAY ĐỔI TỪ HỆ THỐNG.")
    return jsonify({"status": "success", "message": "Đã gửi yêu cầu dừng tiến trình cào/quét thành công!"})


@routes_crawl.route('/api/crawl/sessions', methods=['GET'])
def get_crawl_sessions():
    """Lấy danh sách lịch sử các phiên cào tin và tổng số thống kê tổng thể"""
    import manager
    if not os.path.exists(manager.DB_FILE):
        return jsonify({
            "sessions": [],
            "totals": {
                "total_sessions": 0,
                "total_crawled": 0,
                "total_duration": 0,
                "overall_avg_speed": "N/A"
            }
        })
        
    conn = None
    try:
        conn = sqlite3.connect(manager.DB_FILE, timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if crawl_sessions exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawl_sessions'")
        if not cursor.fetchone():
            return jsonify({
                "sessions": [],
                "totals": {
                    "total_sessions": 0,
                    "total_crawled": 0,
                    "total_duration": 0,
                    "overall_avg_speed": "N/A"
                }
            })
            
        rows = cursor.execute("SELECT * FROM crawl_sessions ORDER BY start_time DESC LIMIT 50").fetchall()
        
        sessions = []
        for r in rows:
            sessions.append(dict(r))
            
        stats = cursor.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(crawled_count) as total_crawled,
                SUM(duration) as total_duration
            FROM crawl_sessions
        """).fetchone()
        
        total_sessions = stats[0] or 0
        total_crawled = stats[1] or 0
        total_duration = stats[2] or 0
        
        avg_speed = "N/A"
        if total_crawled > 0 and total_duration > 0:
            avg_speed = f"{total_duration / total_crawled:.1f}s/căn"
            
        return jsonify({
            "sessions": sessions,
            "totals": {
                "total_sessions": total_sessions,
                "total_crawled": total_crawled,
                "total_duration": total_duration,
                "overall_avg_speed": avg_speed
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if conn:
            conn.close()

@routes_crawl.route('/api/listings/<tk_id>/recrawl', methods=['POST'])
def recrawl_single_listing(tk_id):
    """Cào lại hoặc cào mới duy nhất căn này bằng cookie Thiên Khôi hiện tại"""
    import manager
    import requests
    from bs4 import BeautifulSoup
    import re
    import random
    from pool_lego import gen_id_khang_ngo_python
    
    if not os.path.exists(manager.DB_FILE):
        return jsonify({"status": "error", "message": "Database không tồn tại"}), 404
        
    data = {}
    try:
        data = request.json or {}
    except Exception:
        pass
        
    # US-134: Đồng bộ Cookie mới từ Extension gửi lên
    cookie_payload = data.get("cookie")
    if cookie_payload:
        try:
            with open(manager.COOKIE_FILE, "w", encoding="utf-8") as f:
                f.write(cookie_payload.strip())
            manager.add_log_message("[🔑] ĐÃ ĐỒNG BỘ COOKIE MỚI TỪ EXTENSION")
        except Exception as e_cook:
            manager.add_log_message(f"[❌ LỖI] Không thể ghi file cookie từ extension: {str(e_cook)}")
            
    conn = None
    try:
        conn = sqlite3.connect(manager.DB_FILE, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        row = cursor.execute(f"SELECT * FROM {manager.LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
        
        d_row = {}
        if row:
            d_row = dict(row)
            
        detail_url = ""
        if row:
            detail_url = d_row.get("Link_Goc") or d_row.get("Link_Gốc")
            
        if not detail_url:
            if len(tk_id) == 36:
                detail_url = f"https://proptech.thienkhoi.com/warehouse/sources/{tk_id}"
            else:
                detail_url = f"https://data.thienkhoi.com/Hang/Detail/{tk_id}"
                
        conn.close()
        conn = None
        
        # Lấy Cookie
        cookie = ""
        if os.path.exists(manager.COOKIE_FILE):
            try:
                with open(manager.COOKIE_FILE, "r", encoding="utf-8") as f:
                    cookie = f.read().strip()
            except Exception:
                pass
                
        if not cookie:
            set_listing_crawl_failed(tk_id, "cookie_expired")
            return jsonify({"status": "error", "message": "Không tìm thấy Cookie Thiên Khôi. Vui lòng cập nhật Cookie trước."}), 400
            
        manager.add_log_message(f"[🚀] BẮT ĐẦU TIẾN TRÌNH CÀO LÈ 1 CĂN: {tk_id} - URL: {detail_url}")
        
        is_proptech = "proptech.thienkhoi.com" in detail_url or "backend.thienkhoi.com" in detail_url or len(tk_id) == 36
        
        if is_proptech:
            # Proptech detail API crawl
            access_token, _, _ = fetcher.extract_tokens(cookie)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://proptech.thienkhoi.com",
                "Referer": "https://proptech.thienkhoi.com/"
            }
            detail_api_url = f"https://backend.thienkhoi.com/product/v1/property/{tk_id}"
            r = requests.get(detail_api_url, headers=headers, timeout=20)
            if r.status_code in [401, 403]:
                refreshed_cookie = fetcher.try_refresh_tokens(manager.COOKIE_FILE)
                if refreshed_cookie:
                    cookie = refreshed_cookie
                    _, access_token, _ = fetcher.extract_tokens(cookie)
                    headers["Authorization"] = f"Bearer {access_token}"
                    r = requests.get(detail_api_url, headers=headers, timeout=20)
                else:
                    set_listing_crawl_failed(tk_id, "cookie_expired")
                    return jsonify({"status": "error", "message": "Access token hết hạn và không thể refresh."}), 401
                    
            if r.status_code in [400, 404]:
                set_listing_crawl_failed(tk_id, "deleted")
                return jsonify({"status": "error", "message": f"Căn nhà đã bị khóa nguồn hoặc xóa trên Thiên Khôi (Mã lỗi {r.status_code})."}), 400
            elif r.status_code != 200:
                set_listing_crawl_failed(tk_id, "http_error")
                return jsonify({"status": "error", "message": f"Thiên Khôi API phản hồi mã lỗi {r.status_code}"}), 500
                
            detail_json = r.json()
            detail_data = detail_json.get("data") or {}
            if not detail_data:
                set_listing_crawl_failed(tk_id, "exception")
                return jsonify({"status": "error", "message": "Nội dung phản hồi API trống."}), 400
                
            ma_hang = detail_data.get("code") or tk_id
            tinh = (detail_data.get("district") or {}).get("provinceName", "TP Hồ Chí Minh")
            quan_name = (detail_data.get("district") or {}).get("name", "")
            phuong_name = (detail_data.get("ward") or {}).get("name", "")
            duong_name = (detail_data.get("street") or {}).get("name") if detail_data.get("street") else detail_data.get("streetName", "")
            ngo_so_nha = detail_data.get("address", "")
            
            phan_loai_names = [c.get("name") for c in (detail_data.get("criteria") or []) if c and c.get("name")]
            phan_loai = ", ".join(phan_loai_names)
            # Lấy title từ payload gửi lên nếu có (do Tampermonkey gửi)
            crawled_title = data.get("title", "").strip() if data else ""
            if crawled_title:
                noi_dung_chinh = crawled_title
            else:
                # Fallback clean title
                dt_so = str(detail_data.get("area") or "").strip()
                dt_thuc = str(detail_data.get("actualArea") or "").strip()
                if dt_so and dt_thuc and dt_so != dt_thuc:
                    area_str = f"{dt_so}/{dt_thuc}"
                else:
                    area_str = dt_so or dt_thuc

                floors_val = str(detail_data.get("floors") or "").strip()
                wide_val = str(detail_data.get("wide") or "").strip()
                depth_val = str(detail_data.get("depth") or "").strip()
                price_val = str(detail_data.get("offeringPrice") or "").strip()

                parts = []
                if ngo_so_nha:
                    parts.append(str(ngo_so_nha).strip())
                if duong_name:
                    parts.append(str(duong_name).strip())
                if area_str:
                    parts.append(str(area_str).strip())
                if floors_val:
                    parts.append(str(floors_val).strip())
                if wide_val:
                    parts.append(str(wide_val).strip())
                if depth_val:
                    parts.append(str(depth_val).strip())
                if price_val:
                    parts.append(f"{price_val} tỷ")

                noi_dung_chinh = " ".join([p for p in parts if p])
            
            mo_ta_chi_tiet = detail_data.get("description", "")
            gia_chao = str(detail_data.get("offeringPrice", ""))
            dt_thuc_te = str(detail_data.get("actualArea", ""))
            dt_tren_so = str(detail_data.get("area", ""))
            so_tang = str(detail_data.get("floors", ""))
            mat_tien = str(detail_data.get("wide", ""))
            chieu_dai = str(detail_data.get("depth", ""))
            so_phong_ngu = str(detail_data.get("bedrooms") or "")
            so_nha_ve_sinh = str(detail_data.get("restrooms") or "")
            
            # US-110: Trích xuất Hướng trực tiếp từ criteria HOUSE_DIRECTION của JSON thô
            criteria_list = detail_data.get("criteria") or []
            huong = next((c.get("name", "") for c in criteria_list if c and c.get("groupCode") == "HOUSE_DIRECTION"), "")
            duong_truoc_nha = str(detail_data.get("minimumRoadWidth") or "")
            trang_thai = detail_data.get("status", "")
            loai_hop_dong = detail_data.get("contractType", "")
            
            ten_chu_nha = ", ".join([o.get("name") for o in (detail_data.get("homeOwner") or []) if o and o.get("name")])
            dien_thoai_1 = detail_data.get("contactPhoneNumber", "")
            dt_dau_chu = (detail_data.get("ownerSideUser") or {}).get("phone", "")
            ten_dau_chu = (detail_data.get("ownerSideUser") or {}).get("name", "")
            link_fb = (detail_data.get("ownerSideUser") or {}).get("fbLink", "")
            
            media = detail_data.get("media", [])
            property_images = []
            sodo_images = []
            
            for m in media:
                m_type = m.get("type")
                m_url = m.get("url")
                if not m_url:
                    continue
                if m_type in ["parcel_map", "certificate_image"]:
                    sodo_images.append(m_url)
                else:
                    property_images.append(m_url)
                        
            # Channels and tags processing
            channels_list = detail_data.get("channels") or []
            channels_str = ", ".join([str(c) for c in channels_list if c])
            
            tags_list = detail_data.get("tags") or []
            tags_str = ", ".join([t.get("name") if isinstance(t, dict) else str(t) for t in tags_list if t])

            raw_images_tk_ordered = [m.get("url") for m in media if m.get("url")]

            crawled_data = {
                "raw_images_tk_ordered": raw_images_tk_ordered,
                "Mã Hàng": ma_hang,
                "Tỉnh": tinh,
                "Quận": quan_name,
                "Phường": phuong_name,
                "Đường": duong_name,
                "Ngõ/Số nhà": ngo_so_nha,
                "Phân loại": phan_loai,
                "Nội dung chính": noi_dung_chinh,
                "Mô tả chi tiết": mo_ta_chi_tiet,
                "Giá chào": gia_chao,
                "Giá Public": gia_chao,
                "DT Thực tế": dt_thuc_te,
                "DT Trên sổ": dt_tren_so,
                "Số Tầng": so_tang,
                "Mặt Tiền": mat_tien,
                "Chieu_dai": chieu_dai,
                "Số phòng ngủ": so_phong_ngu,
                "Số nhà vệ sinh": so_nha_ve_sinh,
                "Hướng": huong,
                "Đường trước nhà (m)": duong_truoc_nha,
                "Tình trạng nhà": "Bình thường",
                "Trạng thái": trang_thai,
                "Tên Chủ Nhà": ten_chu_nha,
                "Điện thoại 1": dien_thoai_1,
                "Điện thoại Đầu Chủ": dt_dau_chu,
                "Tên Đầu Chủ (Hợp đồng)": ten_dau_chu,
                "Ten_Dau_Chu": ten_dau_chu,
                "Điểm Facebook": link_fb,
                "Link Gốc": detail_url,
                "System ID": d_row.get("System_ID") or f"SYS-{datetime.now().strftime('%Y%M%d').upper()}-{random.randint(100, 999)}",
                "Mã Khang Ngô (ID)": d_row.get("Ma_Khang_Ngo_ID") or gen_id_khang_ngo_python(ngo_so_nha, duong_name, quan_name),
                "Last Crawl": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                
                # English compatibility mapping
                "bedrooms": so_phong_ngu,
                "restrooms": so_nha_ve_sinh,
                "minimumRoadWidth": duong_truoc_nha,
                
                # Rich contract & technical fields from API
                "isSigned": "1" if detail_data.get("isSigned") else "0",
                "status_nguon": trang_thai,
                "commissionAgent": str(detail_data.get("commissionAgent") or ""),
                "ownerSideUserId": str(detail_data.get("ownerSideUserId") or ""),
                "certificateSeries": str(detail_data.get("certificateSeries") or ""),
                "latitude": str((detail_data.get("coordinate") or {}).get("latitude") or detail_data.get("latitude") or ""),
                "longitude": str((detail_data.get("coordinate") or {}).get("longitude") or detail_data.get("longitude") or ""),
                "placeName": str(detail_data.get("placeName") or ""),
                "streetName": str(detail_data.get("streetName") or ""),
                "balconies": str(detail_data.get("balconies") or ""),
                "sidewalk": str(detail_data.get("sidewalk") or ""),
                "behindOpenSpace": str(detail_data.get("behindOpenSpace") or ""),
                "sideOpenSpace": str(detail_data.get("sideOpenSpace") or ""),
                "createdAt": str(detail_data.get("createdAt") or ""),
                "updatedAt": str(detail_data.get("updatedAt") or ""),
                "listedAt": str(detail_data.get("listedAt") or ""),
                "commissionType": str(detail_data.get("commissionType") or ""),
                "commissionValue": str(detail_data.get("commissionValue") or ""),
                "isDispute": "1" if detail_data.get("isDispute") else "0",
                "createdAtSigned": str(detail_data.get("createdAtSigned") or ""),
                "CCCD_Dau_Chu": str((detail_data.get("ownerSideUser") or {}).get("numberId") or ""),
                "Kenh_tin_TK": channels_str,
                "The_tags_TK": tags_str
            }
            
            for idx, url in enumerate(sodo_images[:5]):
                crawled_data[f"Sơ đồ thửa đất {idx+1}"] = url
                
            # Parse criteria groups and merge into crawled_data
            criteria_list = detail_data.get("criteria") or []
            
            # Save to scratch/last_crawled_criteria.json for debug
            try:
                os.makedirs("scratch", exist_ok=True)
                with open("scratch/last_crawled_criteria.json", "w", encoding="utf-8") as f:
                    json.dump(criteria_list, f, indent=4, ensure_ascii=False)
            except Exception as e_debug:
                manager.add_log_message(f"[⚠️ WARNING] Lỗi ghi file debug criteria: {str(e_debug)}")
                
            criteria_cols = fetcher.parse_criteria_groups(criteria_list)
            crawled_data.update(criteria_cols)
            
            # Lưu raw_json_full và JSON_UI tinh gọn từ Proptech API
            crawled_data["raw_json_full"] = json.dumps(detail_data, ensure_ascii=False)
            try:
                import pool_lego
                json_ui_dict = pool_lego.extract_json_ui_data(detail_data)
                crawled_data["JSON_UI"] = json.dumps(json_ui_dict, ensure_ascii=False)
            except Exception as e_json_ui:
                manager.add_log_message(f"[⚠️ WARNING] Lỗi trích xuất JSON_UI trong recrawl: {str(e_json_ui)}")
                
            fetcher.save_raw_to_sqlite(tk_id, crawled_data, property_images)
            
            # Lưu SQLite với status='raw_text' để background_worker.py quét xử lý ngầm
            manager.add_log_message(f"[✅] Đã cào thô thành công căn (Proptech): {tk_id}. Hàng đợi SQLite sẽ tự động xử lý ngầm...")

                
            # Trả về kết quả dòng đã cập nhật
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
                updated_row = cursor.execute(sql, (tk_id,)).fetchone()
            else:
                updated_row = cursor.execute(f"SELECT * FROM {manager.LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
            conn.close()
            
            d = dict(updated_row)
            d["raw_images_tk"] = json.loads(d["raw_images_tk_json"]) if d.get("raw_images_tk_json") else []
            d["raw_drive_images"] = json.loads(d["raw_drive_images_json"]) if d.get("raw_drive_images_json") else []
            d["curated_config"] = json.loads(d["curated_config_json"]) if d.get("curated_config_json") else None
            
            status_text = d.get("status", "")
            if status_text == "raw_text":
                msg = "Đã cào mới thành công về SQLite. Tiến trình di cư ảnh và AI đang chạy ngầm."
            elif status_text == "published":
                msg = "Đã cào mới, di cư ảnh và xuất bản thành công trực tiếp lên Google Sheets Pool!"
            elif status_text == "raw_complete":
                msg = "Đã cào mới và di cư ảnh thành công (Gặp sự cố khi tự động đẩy lên Sheets Pool)."
            else:
                msg = "Đã cào mới thành công về SQLite (Gặp sự cố khi di cư ảnh hoặc đẩy lên Sheets)."
                
            return jsonify({"status": "success", "message": msg, "listing": d})

        # Thực hiện scrape chi tiết căn này trực tiếp trong Flask thread
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": cookie,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        r = requests.get(detail_url, headers=headers, timeout=20)
        if r.status_code in [400, 404]:
            set_listing_crawl_failed(tk_id, "deleted")
            return jsonify({"status": "error", "message": f"Căn nhà đã bị khóa nguồn hoặc xóa trên Thiên Khôi (HTTP {r.status_code})."}), 400
        elif r.status_code != 200:
            set_listing_crawl_failed(tk_id, "http_error")
            return jsonify({"status": "error", "message": f"Thiên Khôi phản hồi mã lỗi HTTP {r.status_code}"}), 500
            
        if "security.html" in r.url or "Account/Login" in r.url or "login" in r.url.lower():
            try:
                import winsound
                winsound.Beep(1000, 250)
                winsound.Beep(1000, 250)
                winsound.Beep(800, 450)
            except Exception:
                pass
            set_listing_crawl_failed(tk_id, "cookie_expired")
            return jsonify({"status": "error", "message": "Cookie đã hết hạn hoặc bị chặn bảo mật bởi Thiên Khôi."}), 401
            
        from bs4 import BeautifulSoup
        soup_detail = BeautifulSoup(r.text, "html.parser")
        
        # Kiểm tra tính hợp lệ của trang chi tiết để tránh ghi đè dữ liệu trống
        if not soup_detail.select_one('#Detail_sNoiDung') and not soup_detail.select_one('#Detail_sDiaChi') and not soup_detail.select_one('#Detail_iGiaChaoHopDong_show'):
            set_listing_crawl_failed(tk_id, "cookie_expired")
            return jsonify({"status": "error", "message": "Không tìm thấy nội dung chi tiết căn nhà trên trang Thiên Khôi. Vui lòng cập nhật lại Cookie."}), 400
            
        # Bóc tách DOM bằng helper của fetcher
        
        ma_hang_scraped = fetcher.get_val_by_label(soup_detail, "mã hàng") or tk_id
        
        phan_loai_scraped = ""
        btn_tieu_chi = soup_detail.select_one(".multiselect")
        if btn_tieu_chi:
            phan_loai_scraped = btn_tieu_chi.get("title", "").strip()
            
        mo_ta_scraped = fetcher.get_val_by_label(soup_detail, "mô tả")
        if not mo_ta_scraped:
            lbl_mota = soup_detail.find("label", text=re.compile(r'mô tả', re.I))
            if lbl_mota and lbl_mota.find_next_sibling():
                mo_ta_scraped = lbl_mota.find_next_sibling().text.strip()
                
        huong_scraped = ""
        sel_huong = soup_detail.select_one("#Detail_iID_HuongNha option[selected]")
        if sel_huong and sel_huong.get("value") != "0":
            huong_scraped = sel_huong.text.strip()
            
        duong_truoc_nha = fetcher.safe_get_val(soup_detail, '#Detail_iDuongVao_show') or fetcher.safe_get_val(soup_detail, '#Detail_iDuongVao')
        dt_dau_chu = fetcher.safe_get_val(soup_detail, '#Detail_sDienThoaiDauChu') or fetcher.get_val_by_label(soup_detail, "điện thoại đầu chủ") or fetcher.get_val_by_label(soup_detail, "đt đầu chủ")
        ten_dau_chu = fetcher.safe_get_val(soup_detail, '#Detail_sHopDongDauChu') or fetcher.get_val_by_label(soup_detail, "hợp đồng") or fetcher.get_val_by_label(soup_detail, "đầu chủ") or fetcher.get_val_by_label(soup_detail, "tên đầu chủ") or fetcher.get_val_by_label(soup_detail, "người ký")
        
        link_fb = fetcher.get_val_by_label(soup_detail, "facebook") or fetcher.get_val_by_label(soup_detail, "fb")
        if not link_fb:
            a_fb = soup_detail.find("a", href=re.compile(r'facebook\.com', re.I))
            if a_fb:
                link_fb = a_fb.get("href", "")
                
        img_els_td = soup_detail.select('#lightgalleryTD li')
        images_td = [li.get('data-src', '') for li in img_els_td if li.get('data-src')]
        
        img_els_nd = soup_detail.select('#lightgalleryND li')
        images_nd = [li.get('data-src', '') for li in img_els_nd if li.get('data-src')]
        
        so_nha = fetcher.safe_get_val(soup_detail, '#Detail_sDiaChi')
        duong_name = fetcher.safe_get_val(soup_detail, '#Detail_sDuongPho')
        quan_name = fetcher.safe_get_val(soup_detail, '#Detail_sTenQuan')
        phuong_name = fetcher.safe_get_val(soup_detail, '#Detail_sTenPhuongXa')
        
        behind_open_space = fetcher.get_val_by_label(soup_detail, "độ rộng mặt thoáng đằng sau nhà (m)") or fetcher.get_val_by_label(soup_detail, "độ rộng mặt thoáng đằng sau nhà") or fetcher.get_val_by_label(soup_detail, "mặt thoáng đằng sau")
        side_open_space = fetcher.get_val_by_label(soup_detail, "độ rộng mặt thoáng bên cạnh (m)") or fetcher.get_val_by_label(soup_detail, "độ rộng mặt thoáng bên cạnh") or fetcher.get_val_by_label(soup_detail, "mặt thoáng bên cạnh")
        bedrooms_scraped = fetcher.get_val_by_label(soup_detail, "số phòng ngủ") or fetcher.safe_get_val(soup_detail, '#Detail_iSoPhongNgu_show')
        restrooms_scraped = fetcher.get_val_by_label(soup_detail, "số nhà vệ sinh") or fetcher.get_val_by_label(soup_detail, "số toilet") or fetcher.safe_get_val(soup_detail, '#Detail_iSoToilet_show')
        balconies_scraped = fetcher.get_val_by_label(soup_detail, "số ban công")
        sidewalk_scraped = fetcher.get_val_by_label(soup_detail, "vỉa hè")
        commission_value = fetcher.get_val_by_label(soup_detail, "phần trăm trích thưởng") or fetcher.get_val_by_label(soup_detail, "phần trăm hoa hồng")
        certificate_series = fetcher.get_val_by_label(soup_detail, "series sổ đỏ") or fetcher.get_val_by_label(soup_detail, "series sổ")

        crawled_data = {
            "Mã Hàng": ma_hang_scraped,
            "Tỉnh": fetcher.safe_get_val(soup_detail, '#Detail_sTenTinh') or fetcher.get_val_by_label(soup_detail, "tỉnh/thành phố") or fetcher.get_val_by_label(soup_detail, "tỉnh"),
            "Quận": quan_name or fetcher.get_val_by_label(soup_detail, "quận/huyện") or fetcher.get_val_by_label(soup_detail, "quận"),
            "Phường": phuong_name or fetcher.get_val_by_label(soup_detail, "phường/xã") or fetcher.get_val_by_label(soup_detail, "phường"),
            "Đường": duong_name or fetcher.get_val_by_label(soup_detail, "đường/phố") or fetcher.get_val_by_label(soup_detail, "đường"),
            "Ngõ/Số nhà": so_nha or fetcher.get_val_by_label(soup_detail, "ngõ/số nhà"),
            "Phân loại": phan_loai_scraped,
            "Nội dung chính": fetcher.safe_get_val(soup_detail, '#Detail_sNoiDung').replace('\r', '').replace('\n', ' ') if fetcher.safe_get_val(soup_detail, '#Detail_sNoiDung') else "",
            "Mô tả chi tiết": mo_ta_scraped,
            "Giá chào": fetcher.safe_get_val(soup_detail, '#Detail_iGiaChaoHopDong_show') or fetcher.get_val_by_label(soup_detail, "giá chào"),
            "Giá Public": fetcher.safe_get_val(soup_detail, '#Detail_iGiaChaoHopDong_show') or fetcher.get_val_by_label(soup_detail, "giá chào"),
            "DT Thực tế": fetcher.safe_get_val(soup_detail, '#Detail_iDienTich_show') or fetcher.get_val_by_label(soup_detail, "diện tích thực tế"),
            "DT Trên sổ": fetcher.safe_get_val(soup_detail, '#Detail_iDienTichSo_show') or fetcher.get_val_by_label(soup_detail, "diện tích sổ"),
            "Mặt Tiền": fetcher.safe_get_val(soup_detail, '#Detail_iMatTien_show') or fetcher.get_val_by_label(soup_detail, "mặt tiền"),
            "Chieu_dai": fetcher.safe_get_val(soup_detail, '#Detail_iDai_show') or fetcher.safe_get_val(soup_detail, '#Detail_iDai') or fetcher.get_val_by_label(soup_detail, "chiều dài"),
            "Số Tầng": fetcher.safe_get_val(soup_detail, '#Detail_iSoTang_show') or fetcher.get_val_by_label(soup_detail, "số tầng"),
            "Số phòng ngủ": bedrooms_scraped,
            "Số nhà vệ sinh": restrooms_scraped,
            "Hướng": huong_scraped or fetcher.get_val_by_label(soup_detail, "hướng nhà") or fetcher.get_val_by_label(soup_detail, "hướng"),
            "Đường trước nhà (m)": duong_truoc_nha,
            "Tình trạng nhà": "Bình thường",
            "Trạng thái": fetcher.safe_get_val(soup_detail, '#Detail_iTrangThai') or fetcher.get_val_by_label(soup_detail, "trạng thái"),
            "Tên Chủ Nhà": fetcher.safe_get_val(soup_detail, '#Detail_sTenChuNha') or fetcher.get_val_by_label(soup_detail, "tên chủ nhà"),
            "Điện thoại 1": fetcher.safe_get_val(soup_detail, '#Detail_sDienThoaiChuNha') or fetcher.get_val_by_label(soup_detail, "điện thoại 1"),
            "Điện thoại Đầu Chủ": dt_dau_chu,
            "Tên Đầu Chủ (Hợp đồng)": ten_dau_chu,
            "Điểm Facebook": link_fb,
            "Link Gốc": detail_url,
            "System ID": d_row.get("System_ID") or f"SYS-{datetime.now().strftime('%Y%M%d').upper()}-{random.randint(100, 999)}",
            "Mã Khang Ngô (ID)": d_row.get("Ma_Khang_Ngo_ID") or gen_id_khang_ngo_python(so_nha, duong_name, quan_name),
            "Last Crawl": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),

            # English compatibility mapping
            "bedrooms": bedrooms_scraped,
            "restrooms": restrooms_scraped,
            "balconies": balconies_scraped,
            "sidewalk": sidewalk_scraped,
            "behindOpenSpace": behind_open_space,
            "sideOpenSpace": side_open_space,
            "minimumRoadWidth": duong_truoc_nha,
            "commissionValue": commission_value,
            "certificateSeries": certificate_series
        }

        # Lấy title từ payload gửi lên nếu có (do Tampermonkey gửi)
        crawled_title = data.get("title", "").strip() if data else ""
        if crawled_title:
            crawled_data["Nội dung chính"] = crawled_title
        else:
            # Fallback clean title
            dt_so = str(crawled_data.get("DT Trên sổ") or "").strip()
            dt_thuc = str(crawled_data.get("DT Thực tế") or "").strip()
            if dt_so and dt_thuc and dt_so != dt_thuc:
                area_str = f"{dt_so}/{dt_thuc}"
            else:
                area_str = dt_so or dt_thuc

            ngo_so_nha = crawled_data.get("Ngõ/Số nhà", "")
            duong_name = crawled_data.get("Đường", "")
            floors_val = str(crawled_data.get("Số Tầng") or "").strip()
            wide_val = str(crawled_data.get("Mặt Tiền") or "").strip()
            depth_val = str(crawled_data.get("Chieu_dai") or "").strip()
            price_val = str(crawled_data.get("Giá chào") or "").strip()

            parts = []
            if ngo_so_nha:
                parts.append(str(ngo_so_nha).strip())
            if duong_name:
                parts.append(str(duong_name).strip())
            if area_str:
                parts.append(str(area_str).strip())
            if floors_val:
                parts.append(str(floors_val).strip())
            if wide_val:
                parts.append(str(wide_val).strip())
            if depth_val:
                parts.append(str(depth_val).strip())
            if price_val:
                parts.append(f"{price_val} tỷ")

            crawled_data["Nội dung chính"] = " ".join([p for p in parts if p])

        # Parse criteria using direct label scraper + fallback to V1 multiselect
        classified_cols = fetcher.scrape_criteria_from_dom(soup_detail, phan_loai_scraped)
        crawled_data.update(classified_cols)
        
        if len(images_td) >= 1: crawled_data["Sơ đồ thửa đất 1"] = images_td[0]
        if len(images_td) >= 2: crawled_data["Sơ đồ thửa đất 2"] = images_td[1]
        if len(images_td) >= 3: crawled_data["Sơ đồ thửa đất 3"] = images_td[2]
        if len(images_td) >= 4: crawled_data["Sơ đồ thửa đất 4"] = images_td[3]
        if len(images_td) >= 5: crawled_data["Sơ đồ thửa đất 5"] = images_td[4]
        
        # Đưa trạng thái về raw_text để dọn dẹp ảnh cũ hoặc up Drive lại
        combined_images = []
        seen_images = set()
        for img in images_nd: # Only product/interior images, exclude diagrams
            if img and img not in seen_images:
                combined_images.append(img)
                seen_images.add(img)
        crawled_data["raw_images_tk_ordered"] = images_td + combined_images
        
        # Extract basic JSON_UI from columns for the HTML recrawler
        try:
            cfg = manager.load_config()
            fields = cfg.get("json_ui_fields") or ["Criteria_Duong_truoc_nha"]
            json_ui_obj = {}
            for f in fields:
                json_ui_obj[f] = crawled_data.get(f, "")
            crawled_data["JSON_UI"] = json.dumps(json_ui_obj, ensure_ascii=False)
        except Exception as e_json_ui:
            manager.add_log_message(f"[⚠️ WARNING] Lỗi trích xuất JSON_UI (HTML recrawl): {str(e_json_ui)}")
        crawled_data["raw_json_full"] = ""
        
        fetcher.save_raw_to_sqlite(tk_id, crawled_data, combined_images)
        
        # Lưu SQLite với status='raw_text' để background_worker.py quét xử lý ngầm
        manager.add_log_message(f"[✅] Đã cào thô thành công căn: {tk_id}. Hàng đợi SQLite sẽ tự động xử lý ngầm...")

            
        # Lấy lại dòng vừa cập nhật
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
            updated_row = cursor.execute(sql, (tk_id,)).fetchone()
        else:
            updated_row = cursor.execute(f"SELECT * FROM {manager.LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
        conn.close()
        conn = None
        
        d = dict(updated_row)
        d["raw_images_tk"] = json.loads(d["raw_images_tk_json"]) if d.get("raw_images_tk_json") else []
        d["raw_drive_images"] = json.loads(d["raw_drive_images_json"]) if d.get("raw_drive_images_json") else []
        d["curated_config"] = json.loads(d["curated_config_json"]) if d.get("curated_config_json") else None
        
        status_text = d.get("status", "")
        if status_text == "raw_text":
            msg = "Đã cào mới thành công về SQLite. Tiến trình di cư ảnh và AI đang chạy ngầm."
        elif status_text == "published":
            msg = "Đã cào mới, di cư ảnh và xuất bản thành công trực tiếp lên Google Sheets Pool!"
        elif status_text == "raw_complete":
            msg = "Đã cào mới và di cư ảnh thành công (Gặp sự cố khi tự động đẩy lên Sheets Pool)."
        else:
            msg = "Đã cào mới thành công về SQLite (Gặp sự cố khi di cư ảnh hoặc đẩy lên Sheets)."
            
        return jsonify({"status": "success", "message": msg, "listing": d})
        
    except Exception as e:
        manager.add_log_message(f"[❌ LỖI] Lỗi cào lại căn {tk_id}: {str(e)}")
        set_listing_crawl_failed(tk_id, "exception")
        return jsonify({"status": "error", "message": f"Gặp sự cố khi cào lại: {str(e)}"}), 500
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
