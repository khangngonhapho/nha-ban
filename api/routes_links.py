# -*- coding: utf-8 -*-
"""
API Blueprint for managing shared links, customer tracking logs, and phone blacklist.
Integrates with SQLite locally and Google Sheets Tracking Log spreadsheet.
"""

import time
import os
import sqlite3
import hashlib
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
import gspread

routes_links = Blueprint('routes_links', __name__)

TRACKING_SHEET_ID = "1zCAP0pUSZdVNxbEkVl94y_hJc1ShM4PqtB-fxpm_I5Y"

def get_db_connection():
    import manager
    db_file = manager.DB_FILE
    conn = sqlite3.connect(db_file, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def get_sheets_client():
    from manager import get_google_credentials
    creds = get_google_credentials()
    if not creds:
        raise Exception("Không tìm thấy Google credentials.")
    return gspread.authorize(creds)

def ensure_sheet_tabs_exists(client):
    """Đảm bảo các tab cần thiết tồn tại trên sheet Tracking Log và khởi tạo công thức"""
    try:
        spreadsheet = client.open_by_key(TRACKING_SHEET_ID)
    except Exception as e:
        raise Exception(f"Không thể mở Spreadsheet Tracking Log: {str(e)}")

    # 1. Link_Registry
    try:
        link_sheet = spreadsheet.worksheet("Link_Registry")
    except Exception:
        link_sheet = spreadsheet.add_worksheet(title="Link_Registry", rows=1000, cols=8)
        headers = ["Link_ID", "Customer_Name", "Customer_Note", "Shared_House_Ids", "Created_At", "Expires_At", "Bound_Phone_Hash", "Status"]
        link_sheet.update(range_name='A1:H1', values=[headers])

    # 2. Phone_Blacklist
    try:
        blacklist_sheet = spreadsheet.worksheet("Phone_Blacklist")
    except Exception:
        blacklist_sheet = spreadsheet.add_worksheet(title="Phone_Blacklist", rows=1000, cols=5)
        headers = ["Raw_Phone", "Phone_Hash", "Blocked_At", "Reason", "Status"]
        blacklist_sheet.update(range_name='A1:E1', values=[headers])

    # 3. Public_Link_Status (Công thức tự động để Vercel đọc)
    try:
        public_link_sheet = spreadsheet.worksheet("Public_Link_Status")
    except Exception:
        public_link_sheet = spreadsheet.add_worksheet(title="Public_Link_Status", rows=1000, cols=4)
        # Thiết lập công thức QUERY để lấy dữ liệu an toàn
        formula = '=QUERY(Link_Registry!A:H, "SELECT A, H, F, G", 1)'
        public_link_sheet.update(range_name='A1', values=[[formula]], value_input_option='USER_ENTERED')

    # 4. Public_Phone_Blacklist (Công thức tự động để Vercel đọc)
    try:
        public_blacklist_sheet = spreadsheet.worksheet("Public_Phone_Blacklist")
    except Exception:
        public_blacklist_sheet = spreadsheet.add_worksheet(title="Public_Phone_Blacklist", rows=1000, cols=1)
        formula = '=QUERY(Phone_Blacklist!A:E, "SELECT B WHERE E = \'Active\'", 1)'
        public_blacklist_sheet.update(range_name='A1', values=[[formula]], value_input_option='USER_ENTERED')

    # 5. Customer_Profiles
    try:
        profile_sheet = spreadsheet.worksheet("Customer_Profiles")
    except Exception:
        profile_sheet = spreadsheet.add_worksheet(title="Customer_Profiles", rows=1000, cols=6)
        headers = ["Raw_Phone", "Phone_Hash", "Name", "Note", "Lifecycle_Status", "Updated_At"]
        profile_sheet.update(range_name='A1:F1', values=[headers])

    return spreadsheet

@routes_links.route('/api/links/register', methods=['POST'])
def register_link():
    """Tạo mới một link chia sẻ, lưu SQLite local và đẩy lên Google Sheets Tracking Log"""
    import manager
    try:
        data = request.get_json(force=True) or {}
        customer_name = data.get("customer_name", "").strip()
        customer_note = data.get("customer_note", "").strip()
        shared_house_ids = data.get("shared_house_ids", "") # Dạng string "SYS-1,SYS-2" hoặc list
        expires_in_days = data.get("expires_in_days", 30)
        raw_phone = data.get("raw_phone", "").strip() # Tùy chọn nhập trước SĐT của khách
        require_verification = data.get("require_verification", False) # True -> Option B, False -> Option A

        if not customer_name:
            return jsonify({"status": "error", "message": "Thiếu tên khách hàng."}), 400
        if not shared_house_ids:
            return jsonify({"status": "error", "message": "Thiếu danh sách nhà chia sẻ."}), 400

        if isinstance(shared_house_ids, list):
            shared_house_ids = ",".join(map(str, shared_house_ids))

        # Sinh link_id độc nhất
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        rand_suffix = hashlib.md5(f"{customer_name}-{shared_house_ids}-{time.time()}".encode('utf-8')).hexdigest()[:6].upper()
        link_id = f"LNK-{timestamp}-{rand_suffix}"

        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(days=int(expires_in_days))).isoformat()

        # Tính mã băm SĐT nếu Admin điền sẵn
        bound_phone_hash = ""
        if raw_phone:
            # Loại bỏ khoảng trắng và ký tự đặc biệt
            clean_phone = raw_phone.replace(" ", "").replace("-", "").replace(".", "")
            if clean_phone:
                bound_phone_hash = hashlib.sha256(clean_phone.encode('utf-8')).hexdigest()

        # 1. Lưu SQLite local
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO shared_links (link_id, customer_name, customer_note, shared_house_ids, created_at, expires_at, bound_phone_hash, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (link_id, customer_name, customer_note, shared_house_ids, created_at, expires_at, bound_phone_hash, 'Active'))
        conn.commit()
        conn.close()

        # 2. Đẩy lên Google Sheets Tracking Log
        try:
            client = get_sheets_client()
            spreadsheet = ensure_sheet_tabs_exists(client)
            link_sheet = spreadsheet.worksheet("Link_Registry")
            row_data = [link_id, customer_name, customer_note, shared_house_ids, created_at, expires_at, bound_phone_hash, 'Active']
            link_sheet.append_row(row_data, value_input_option='USER_ENTERED')
            manager.add_log_message(f"[🔗 LINK REGISTRY] Đã đăng ký Link ID {link_id} lên Google Sheets thành công.")
        except Exception as e_sheet:
            manager.add_log_message(f"[⚠️ WARNING LINK REGISTRY] Lỗi đẩy Sheets: {str(e_sheet)}")

        return jsonify({
            "status": "success",
            "link_id": link_id,
            "bound_phone_hash": bound_phone_hash,
            "created_at": created_at,
            "expires_at": expires_at
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@routes_links.route('/api/links/bind', methods=['POST'])
def bind_link_phone():
    """Khóa số điện thoại khách hàng vào Link ID (dành cho client kích hoạt lần đầu)"""
    import manager
    try:
        data = request.get_json(force=True) or {}
        link_id = data.get("link_id", "").strip()
        phone_hash = data.get("phone_hash", "").strip()

        if not link_id or not phone_hash:
            return jsonify({"status": "error", "message": "Thiếu link_id hoặc phone_hash."}), 400

        # 1. Cập nhật SQLite local
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Chỉ cập nhật nếu bound_phone_hash đang trống
        cursor.execute("SELECT bound_phone_hash FROM shared_links WHERE link_id = ?", (link_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"status": "error", "message": "Không tìm thấy Link ID tương ứng."}), 404
            
        if row['bound_phone_hash'] and row['bound_phone_hash'].strip():
            conn.close()
            return jsonify({"status": "error", "message": "Liên kết này đã được khóa với số điện thoại khác từ trước."}), 400

        cursor.execute("""
            UPDATE shared_links 
            SET bound_phone_hash = ? 
            WHERE link_id = ? AND (bound_phone_hash IS NULL OR bound_phone_hash = '')
        """, (phone_hash, link_id))
        conn.commit()
        conn.close()

        # 2. Cập nhật Google Sheets
        try:
            client = get_sheets_client()
            spreadsheet = ensure_sheet_tabs_exists(client)
            link_sheet = spreadsheet.worksheet("Link_Registry")
            
            link_ids = link_sheet.col_values(1)
            if link_id in link_ids:
                row_idx = link_ids.index(link_id) + 1
                # Cột G (Bound_Phone_Hash) là cột số 7
                link_sheet.update(range_name=f"G{row_idx}", values=[[phone_hash]])
                manager.add_log_message(f"[🔒 BIND LINK] Đã khóa SĐT băm '{phone_hash}' vào Link ID {link_id} trên Sheets.")
        except Exception as e_sheet:
            manager.add_log_message(f"[⚠️ WARNING BIND LINK] Lỗi cập nhật khóa SĐT lên Sheets: {str(e_sheet)}")

        return jsonify({"status": "success", "message": "Đã khóa liên kết thành công."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@routes_links.route('/api/links/revoke', methods=['POST'])
def revoke_link():
    """Hủy bỏ/Thu hồi link chia sẻ"""
    import manager
    try:
        data = request.get_json(force=True) or {}
        link_id = data.get("link_id", "").strip()

        if not link_id:
            return jsonify({"status": "error", "message": "Thiếu Link ID cần thu hồi."}), 400

        # 1. Cập nhật SQLite local
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE shared_links SET status = 'Revoked' WHERE link_id = ?", (link_id,))
        conn.commit()
        conn.close()

        # 2. Cập nhật Google Sheets
        try:
            client = get_sheets_client()
            spreadsheet = ensure_sheet_tabs_exists(client)
            link_sheet = spreadsheet.worksheet("Link_Registry")
            
            link_ids = link_sheet.col_values(1)
            if link_id in link_ids:
                row_idx = link_ids.index(link_id) + 1
                # Cột H (Status) là cột số 8
                link_sheet.update(range_name=f"H{row_idx}", values=[['Revoked']])
                manager.add_log_message(f"[🔴 REVOKE LINK] Đã thu hồi quyền truy cập của Link ID {link_id} trên Sheets.")
        except Exception as e_sheet:
            manager.add_log_message(f"[⚠️ WARNING REVOKE LINK] Lỗi cập nhật status lên Sheets: {str(e_sheet)}")

        return jsonify({"status": "success", "message": f"Đã thu hồi Link {link_id} thành công."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@routes_links.route('/api/blacklist/add', methods=['POST'])
def add_to_blacklist():
    """Block số điện thoại khách hàng"""
    import manager
    try:
        data = request.get_json(force=True) or {}
        raw_phone = data.get("phone", "").strip()
        reason = data.get("reason", "").strip()

        if not raw_phone:
            return jsonify({"status": "error", "message": "Thiếu số điện thoại cần chặn."}), 400

        clean_phone = raw_phone.replace(" ", "").replace("-", "").replace(".", "")
        phone_hash = hashlib.sha256(clean_phone.encode('utf-8')).hexdigest()
        blocked_at = datetime.now().isoformat()

        # 1. Lưu SQLite local
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO phone_blacklist (raw_phone, phone_hash, blocked_at, reason, status)
            VALUES (?, ?, ?, ?, 'Active')
        """, (clean_phone, phone_hash, blocked_at, reason))
        conn.commit()
        conn.close()

        # 2. Đẩy lên Google Sheets
        try:
            client = get_sheets_client()
            spreadsheet = ensure_sheet_tabs_exists(client)
            blacklist_sheet = spreadsheet.worksheet("Phone_Blacklist")
            
            # Kiểm tra xem SĐT này đã có trên Sheet chưa để ghi đè hoặc thêm mới
            hashes = blacklist_sheet.col_values(2)
            if phone_hash in hashes:
                row_idx = hashes.index(phone_hash) + 1
                blacklist_sheet.update(range_name=f"A{row_idx}:E{row_idx}", values=[[clean_phone, phone_hash, blocked_at, reason, 'Active']])
            else:
                row_data = [clean_phone, phone_hash, blocked_at, reason, 'Active']
                blacklist_sheet.append_row(row_data, value_input_option='USER_ENTERED')
                
            manager.add_log_message(f"[🚫 BLACKLIST] Đã block SĐT {clean_phone} (hash: {phone_hash}) thành công.")
        except Exception as e_sheet:
            manager.add_log_message(f"[⚠️ WARNING BLACKLIST] Lỗi đẩy blacklist lên Sheets: {str(e_sheet)}")

        return jsonify({"status": "success", "message": "Đã chặn số điện thoại thành công."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@routes_links.route('/api/blacklist/remove', methods=['POST'])
def remove_from_blacklist():
    """Gỡ block số điện thoại"""
    import manager
    try:
        data = request.get_json(force=True) or {}
        phone_hash = data.get("phone_hash", "").strip()

        if not phone_hash:
            return jsonify({"status": "error", "message": "Thiếu mã băm phone_hash cần gỡ chặn."}), 400

        # 1. Cập nhật SQLite local
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE phone_blacklist SET status = 'Inactive' WHERE phone_hash = ?", (phone_hash,))
        conn.commit()
        conn.close()

        # 2. Cập nhật Google Sheets
        try:
            client = get_sheets_client()
            spreadsheet = ensure_sheet_tabs_exists(client)
            blacklist_sheet = spreadsheet.worksheet("Phone_Blacklist")
            
            hashes = blacklist_sheet.col_values(2)
            if phone_hash in hashes:
                row_idx = hashes.index(phone_hash) + 1
                # Cột E (Status) là cột số 5
                blacklist_sheet.update(range_name=f"E{row_idx}", values=[['Inactive']])
                manager.add_log_message(f"[🟢 UNBLACKLIST] Đã gỡ chặn cho SĐT hash {phone_hash} trên Sheets.")
        except Exception as e_sheet:
            manager.add_log_message(f"[⚠️ WARNING UNBLACKLIST] Lỗi cập nhật status gỡ chặn lên Sheets: {str(e_sheet)}")

        return jsonify({"status": "success", "message": "Đã gỡ chặn thành công."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@routes_links.route('/api/links/list', methods=['GET'])
def list_links():
    """Trả về danh sách link đã tạo và SĐT bị block từ SQLite local (để phục vụ debug local)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Lấy danh sách link
        cursor.execute("SELECT * FROM shared_links ORDER BY created_at DESC")
        links = [dict(row) for row in cursor.fetchall()]
        
        # Lấy danh sách blacklist
        cursor.execute("SELECT * FROM phone_blacklist ORDER BY blocked_at DESC")
        blacklist = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return jsonify({
            "status": "success",
            "links": links,
            "blacklist": blacklist
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@routes_links.route('/api/customers/profiles', methods=['GET'])
def list_customer_profiles():
    """Lấy danh sách thông tin và vòng đời khách hàng từ SQLite local"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customer_profiles")
        profiles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({
            "status": "success",
            "profiles": profiles
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@routes_links.route('/api/customers/profile', methods=['POST'])
def update_customer_profile():
    """Cập nhật ghi chú nhu cầu và trạng thái vòng đời khách hàng (CRM)"""
    import manager
    try:
        data = request.get_json(force=True) or {}
        raw_phone = data.get("phone", "").strip()
        name = data.get("name", "").strip()
        note = data.get("note") # Có thể là None nếu chỉ update status
        lifecycle_status = data.get("lifecycle_status") # Có thể là None nếu chỉ update note

        if not raw_phone:
            return jsonify({"status": "error", "message": "Thiếu số điện thoại khách hàng."}), 400

        clean_phone = raw_phone.replace(" ", "").replace("-", "").replace(".", "")
        if not clean_phone:
            return jsonify({"status": "error", "message": "Số điện thoại không hợp lệ."}), 400

        phone_hash = hashlib.sha256(clean_phone.encode('utf-8')).hexdigest()
        updated_at = datetime.now().isoformat()

        # 1. Cập nhật SQLite cục bộ
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customer_profiles WHERE phone_hash = ?", (phone_hash,))
        existing = cursor.fetchone()
        
        new_note = note if note is not None else (existing['note'] if existing else '')
        new_status = lifecycle_status if lifecycle_status is not None else (existing['lifecycle_status'] if existing else 'Lạnh')
        new_name = name if name else (existing['name'] if existing else '')
        
        cursor.execute("""
            INSERT OR REPLACE INTO customer_profiles (raw_phone, phone_hash, name, note, lifecycle_status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (clean_phone, phone_hash, new_name, new_note, new_status, updated_at))
        conn.commit()
        conn.close()

        # 2. Cập nhật lên Google Sheets
        try:
            client = get_sheets_client()
            spreadsheet = ensure_sheet_tabs_exists(client)
            profile_sheet = spreadsheet.worksheet("Customer_Profiles")
            
            hashes = profile_sheet.col_values(2)
            if phone_hash in hashes:
                row_idx = hashes.index(phone_hash) + 1
                row_vals = profile_sheet.row_values(row_idx)
                # Bảo toàn name nếu client gửi trống
                final_name = new_name if new_name else (row_vals[2] if len(row_vals) > 2 else '')
                profile_sheet.update(range_name=f"A{row_idx}:F{row_idx}", values=[[clean_phone, phone_hash, final_name, new_note, new_status, updated_at]])
            else:
                row_data = [clean_phone, phone_hash, new_name, new_note, new_status, updated_at]
                profile_sheet.append_row(row_data, value_input_option='USER_ENTERED')
            manager.add_log_message(f"[👤 PROFILE] Đã lưu thông tin SĐT {clean_phone} lên Google Sheets thành công.")
        except Exception as e_sheet:
            manager.add_log_message(f"[⚠️ WARNING PROFILE] Lỗi đồng bộ Sheets: {str(e_sheet)}")

        return jsonify({
            "status": "success",
            "message": "Cập nhật thông tin khách hàng thành công.",
            "phone_hash": phone_hash
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
