# -*- coding: utf-8 -*-
"""
Migration script to update JSON_UI with tags for all existing listings in SQLite and Google Sheets.
"""

import os
import sys
import json
import sqlite3

# Ensure we can import manager and pool_lego
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import manager
import pool_lego

def run_migration():
    print("=" * 60)
    print("   BDS KHANG NGÔ - TIẾN TRÌNH MIGRATION TAGS CHO JSON_UI")
    print("=" * 60)
    
    # 1. Load config and determine database & sheet ID
    cfg = manager.load_config()
    is_staging = os.environ.get("STAGING") == "true"
    db_file = manager.DB_FILE
    
    if is_staging:
        sheet_id = cfg.get("staging_pool_sheet_id") or "1Nc8OwSHwacvuuS4blI8U9BrDOlVx6S6u9fU3AaKBYdY"
        print(f"[*] Đang chạy ở chế độ STAGING")
    else:
        sheet_id = cfg.get("sheet_id") or "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
        print(f"[*] Đang chạy ở chế độ PRODUCTION")
        
    print(f"[*] Database file: {db_file}")
    print(f"[*] Google Sheet ID: {sheet_id}")
    
    if not os.path.exists(db_file):
        print(f"[❌ LỖI] Database không tồn tại: {db_file}")
        return
        
    # 2. Connect to SQLite and update the listings table
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Check what table is used (listings or listings_v2)
    listings_table = manager.LISTINGS_TABLE
    print(f"[*] SQLite Table: {listings_table}")
    
    # Check if raw_json_full column exists
    cursor.execute(f"PRAGMA table_info({listings_table})")
    cols = [row[1] for row in cursor.fetchall()]
    if "raw_json_full" not in cols:
        print("[❌ LỖI] Cột raw_json_full không tồn tại trong CSDL. Không thể khôi phục tags.")
        conn.close()
        return
        
    # Query all rows with raw_json_full
    cursor.execute(f"SELECT tk_id, raw_json_full, JSON_UI FROM {listings_table} WHERE raw_json_full IS NOT NULL")
    rows = cursor.fetchall()
    print(f"[*] Tìm thấy {len(rows)} bản ghi trong CSDL để xử lý...")
    
    updated_local_count = 0
    updated_local_map = {} # tk_id -> json_ui_str
    
    for tk_id, raw_json_str, json_ui_str in rows:
        if not raw_json_str:
            continue
        try:
            raw_json = json.loads(raw_json_str)
        except Exception:
            continue
            
        tags = raw_json.get("tags") or []
        
        # Parse current JSON_UI
        json_ui_dict = {}
        if json_ui_str:
            try:
                json_ui_dict = json.loads(json_ui_str)
            except Exception:
                pass
                
        # Update tags in json_ui_dict
        old_tags = json_ui_dict.get("tags")
        if old_tags != tags:
            json_ui_dict["tags"] = tags
            new_json_ui_str = json.dumps(json_ui_dict, ensure_ascii=False)
            cursor.execute(f"UPDATE {listings_table} SET JSON_UI = ? WHERE tk_id = ?", (new_json_ui_str, tk_id))
            updated_local_count += 1
            updated_local_map[tk_id] = new_json_ui_str
            
    if updated_local_count > 0:
        conn.commit()
        print(f"[✅] Đã cập nhật xong SQLite cục bộ: Cập nhật {updated_local_count} bản ghi.")
    else:
        print("[ℹ] Không có thay đổi nào cần cập nhật trong CSDL cục bộ.")
        
    conn.close()
    
    # 3. Connect to Google Sheets and batch update the JSON_UI column
    creds = manager.get_google_credentials()
    if not creds:
        print("[❌ LỖI] Không thể tải Google OAuth credentials. Bỏ qua bước cập nhật Google Sheets.")
        return
        
    print("[*] Đang kết nối tới Google Sheets...")
    try:
        import gspread
        client = gspread.authorize(creds)
        client.http_client.session.timeout = 60
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.worksheet("Pool")
    except Exception as e_sheets:
        print(f"[❌ LỖI] Không thể kết nối tới Google Sheet tab 'Pool': {str(e_sheets)}")
        return
        
    print("[*] Đang tải dữ liệu từ Google Sheet...")
    try:
        # Get all values in first row (headers) to find columns dynamically
        headers = sheet.row_values(1)
        
        # Find index of Mã Hàng (or tk_id, but Mã Hàng is column A in Pool1, System_ID in Pool2)
        # Let's find dynamically
        id_col_name = "Mã Hàng"
        if id_col_name not in headers:
            id_col_name = "System ID"
        if id_col_name not in headers:
            id_col_name = "System_ID"
        if id_col_name not in headers:
            id_col_name = "Mã hàng"
            
        if id_col_name not in headers:
            print("[❌ LỖI] Không tìm thấy cột Mã Hàng hay System ID để đối chiếu dòng.")
            return
            
        id_col_idx = headers.index(id_col_name) + 1
        json_ui_col_idx = headers.index("JSON_UI") + 1
        
        print(f"  - Cột ID đối chiếu: '{id_col_name}' (Cột thứ {id_col_idx})")
        print(f"  - Cột cập nhật: 'JSON_UI' (Cột thứ {json_ui_col_idx})")
        
        # Fetch all ID column values and JSON_UI column values
        id_values = sheet.col_values(id_col_idx)
        json_ui_values = sheet.col_values(json_ui_col_idx)
        
    except Exception as e_fetch:
        print(f"[❌ LỖI] Không thể đọc cấu trúc cột từ Google Sheet: {str(e_fetch)}")
        return
        
    # We will build a list of cell updates
    cells_to_update = []
    updated_sheet_count = 0
    
    # Connect to local DB again to map Mã Hàng/System_ID -> JSON_UI
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Build maps of lookup
    # In SQLite listings table, tk_id matches raw_json_full ID, Ma_Hang/System_ID matches Google Sheet ID
    cursor.execute(f"SELECT tk_id, Ma_Hang, System_ID, JSON_UI FROM {listings_table}")
    db_rows = cursor.fetchall()
    
    # Create lookup dictionaries
    tk_id_to_json_ui = {row[0]: row[3] for row in db_rows if row[0]}
    ma_hang_to_json_ui = {row[1]: row[3] for row in db_rows if row[1]}
    sys_id_to_json_ui = {row[2]: row[3] for row in db_rows if row[2]}
    
    conn.close()
    
    # Loop through the rows in Google Sheet (starting from row 2, which is index 1 in Python lists)
    # col_values length determines rows
    num_rows = max(len(id_values), len(json_ui_values))
    
    for row_idx in range(2, num_rows + 1):
        # Index in lists is row_idx - 1
        g_id = id_values[row_idx - 1].strip() if (row_idx - 1) < len(id_values) else ""
        current_g_json_ui = json_ui_values[row_idx - 1].strip() if (row_idx - 1) < len(json_ui_values) else ""
        
        if not g_id:
            continue
        # Try matching by Ma_Hang, then System_ID, then tk_id
        target_json_ui = ma_hang_to_json_ui.get(g_id) or sys_id_to_json_ui.get(g_id) or tk_id_to_json_ui.get(g_id)
        
        if target_json_ui:
            # Check if updated is different
            try:
                # Compare as parsed objects to ignore key order / formatting diffs
                obj1 = json.loads(current_g_json_ui) if current_g_json_ui else {}
                obj2 = json.loads(target_json_ui)
                
                # Check if tags differ
                if obj1.get("tags") != obj2.get("tags"):
                    cells_to_update.append(gspread.Cell(row=row_idx, col=json_ui_col_idx, value=target_json_ui))
                    updated_sheet_count += 1
            except Exception:
                # If error parsing or empty, force update if different text
                if current_g_json_ui != target_json_ui:
                    cells_to_update.append(gspread.Cell(row=row_idx, col=json_ui_col_idx, value=target_json_ui))
                    updated_sheet_count += 1
                    
    if cells_to_update:
        print(f"[*] Đang thực hiện ghi đè {len(cells_to_update)} ô JSON_UI lên Google Sheets...")
        try:
            sheet.update_cells(cells_to_update, value_input_option='USER_ENTERED')
            print(f"[✅] Đã cập nhật xong Google Sheets: Cập nhật {updated_sheet_count} dòng.")
        except Exception as e_update:
            print(f"[❌ LỖI] Lỗi ghi đè Google Sheets: {str(e_update)}")
    else:
        print("[ℹ] Không có dòng nào cần cập nhật trên Google Sheets.")
        
    print("=" * 60)
    print("   HOÀN TẤT TIẾN TRÌNH MIGRATION!")
    print("=" * 60)

if __name__ == '__main__':
    run_migration()
