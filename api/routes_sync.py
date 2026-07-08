# -*- coding: utf-8 -*-
"""
Database sync and sheets publication routes for BDS KhangNgo.
Handles bulk publication, cross-database sync, JSON UI sync, and recrawling tasks.
"""

import time
import threading
from flask import Blueprint, jsonify, request
import pool_lego

routes_sync = Blueprint('routes_sync', __name__)

@routes_sync.route('/api/publish/<tk_id>', methods=['POST'])
def publish_listing(tk_id):
    """API đẩy dòng dữ liệu 79 cột chính thức lên Google Sheets"""
    import manager
    res = manager.execute_publish_listing(tk_id)
    return jsonify(res)

@routes_sync.route('/api/listings/bulk-publish', methods=['POST'])
def bulk_publish_listings():
    """API đẩy hàng loạt danh sách các căn được chọn lên Google Sheets Pool"""
    import manager
    try:
        data = request.get_json(force=True) or {}
        ids = data.get("ids", [])
        if not ids:
            return jsonify({"status": "error", "message": "Không có mã căn nào được chọn để xuất bản."}), 400
            
        manager.add_log_message(f"[⚡] Bắt đầu đẩy hàng loạt {len(ids)} căn lên Google Sheets Pool...")
        
        success_count = 0
        for idx, tk_id in enumerate(ids):
            manager.add_log_message(f"📦 [{idx+1}/{len(ids)}] Đang đẩy căn {tk_id}...")
            res = manager.execute_publish_listing(tk_id)
            if res.get("status") == "success":
                success_count += 1
            else:
                manager.add_log_message(f"[⚠️ WARNING] Căn {tk_id} đẩy không thành công: {res.get('message')}")
            time.sleep(0.5)  # Throttling to prevent API quota exhaust
            
        manager.add_log_message(f"[✅] Đã hoàn thành đẩy hàng loạt! Thành công: {success_count}/{len(ids)} căn.")
        return jsonify({
            "status": "success",
            "success_count": success_count,
            "total_count": len(ids)
        })
    except Exception as e:
        manager.add_log_message(f"[❌ LỖI] Lỗi trong quá trình xuất bản hàng loạt: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@routes_sync.route('/api/sync-databases', methods=['POST'])
def api_sync_databases():
    """API đồng bộ chéo giữa các pool database cục bộ"""
    import manager
    try:
        data = request.get_json(force=True) or {}
        source = data.get("source")
        target = data.get("target")
        tk_id = data.get("tk_id")
        so_nha = data.get("so_nha")
        duong = data.get("duong")
        
        if not source or not target:
            return jsonify({"status": "error", "message": "Thiếu tham số source hoặc target."}), 400
            
        res = pool_lego.sync_between_databases(source, target, tk_id, so_nha, duong, manager.add_log_message)
        return jsonify(res)
    except Exception as e:
        manager.add_log_message(f"[❌ LỖI] Lỗi trong quá trình đồng bộ API: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
        
@routes_sync.route('/api/sync-json-ui', methods=['POST'])
def api_sync_json_ui():
    """Kích hoạt tiến trình đồng bộ và vá dữ liệu JSON UI"""
    import manager
    try:
        data = request.get_json(force=True) or {}
        limit = data.get("limit")
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                limit = None
                
        def sync_worker():
            try:
                import scratch.sync_json_ui as sync_json_ui
                sync_json_ui.run_sync(limit=limit, add_log_message=manager.add_log_message)
            except Exception as ex:
                manager.add_log_message(f"[❌ LỖI] Lỗi tiến trình đồng bộ JSON UI: {str(ex)}")
                
        threading.Thread(target=sync_worker, daemon=True).start()
        
        return jsonify({
            "status": "success",
            "message": "Tiến trình đồng bộ và vá dữ liệu JSON UI đã được kích hoạt chạy ngầm."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@routes_sync.route('/api/sync-databases/recrawl-all', methods=['POST'])
def api_recrawl_all():
    """API kích hoạt tiến trình cào lại định kỳ chạy ngầm toàn bộ CSDL và tổng hợp thay đổi"""
    import manager
    def run_recrawl():
        try:
            pool_lego.recrawl_all_listings(add_log_message=manager.add_log_message)
        except Exception as e:
            manager.add_log_message(f"[❌ LỖI] Lỗi tiến trình cào lại ngầm: {str(e)}")
            
    threading.Thread(target=run_recrawl, daemon=True).start()
    return jsonify({"status": "success", "message": "Đã bắt đầu tiến trình cào lại định kỳ chạy ngầm toàn bộ CSDL."})
