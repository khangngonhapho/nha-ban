# -*- coding: utf-8 -*-
import os
import sys
import datetime
import json

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import manager
from core.config import read_settings
import gspread

def sync_flags(add_log_message=print):
    add_log_message("[🏁] Bắt đầu đồng bộ hóa Feature Flags lên Google Sheets...")
    settings = read_settings()
    
    # 1. Determine active sheet ID
    is_staging = os.environ.get("STAGING") == "true"
    active_system = settings.get("active_pool_system", "Pool1")
    
    if is_staging:
        sheet_id = settings.get("staging_pool_sheet_id") or "1Nc8OwSHwacvuuS4blI8U9BrDOlVx6S6u9fU3AaKBYdY"
    elif active_system == "Pool2":
        # Pool2 uses custom sheet
        sheet_id = settings.get("pool2_custom_sheet_id")
    else:
        # Pool1 uses default sheet_id
        sheet_id = settings.get("sheet_id")
        
    if not sheet_id:
        add_log_message("[❌ LỖI] Không xác định được Spreadsheet ID để đồng bộ flags.")
        return {"status": "error", "message": "Missing spreadsheet ID"}
        
    add_log_message(f"📂 Sử dụng Spreadsheet ID: {sheet_id} (Hệ thống: {active_system})")
    
    # 2. Get credentials and authorize gspread
    try:
        creds = manager.get_google_credentials()
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
    except Exception as e:
        add_log_message(f"[❌ LỖI] Không thể kết nối hoặc mở spreadsheet: {str(e)}")
        return {"status": "error", "message": f"Connection error: {str(e)}"}
        
    # 3. Open or create Feature_Flags worksheet
    tab_name = "Feature_Flags"
    try:
        worksheet = spreadsheet.worksheet(tab_name)
        add_log_message(f"✅ Tìm thấy tab '{tab_name}'")
    except gspread.exceptions.WorksheetNotFound:
        add_log_message(f"📦 Không tìm thấy tab '{tab_name}'. Tiến hành tạo mới...")
        try:
            worksheet = spreadsheet.add_worksheet(title=tab_name, rows=100, cols=10)
            # Write headers
            headers = ["Tên Flag", "Loại Flag", "Giá Trị Hiện Tại", "Trạng Thái", "Ngày Release", "Ngày Cập Nhật", "Mô tả"]
            worksheet.append_row(headers)
            # Format header row to be bold
            worksheet.format("A1:G1", {"textFormat": {"bold": True}})
            add_log_message(f"✅ Đã tạo mới tab '{tab_name}' với các cột tiêu chuẩn.")
        except Exception as e:
            add_log_message(f"[❌ LỖI] Không thể tạo tab mới: {str(e)}")
            return {"status": "error", "message": f"Worksheet creation error: {str(e)}"}
            
    # 4. Pull existing flags from sheet
    try:
        all_records = worksheet.get_all_records()
    except Exception as e:
        # Fallback if worksheet has empty header format issues
        all_records = []
        add_log_message(f"[⚠️ WARNING] Không thể get_all_records: {str(e)}. Sử dụng danh sách rỗng.")

    # 5. Extract current flags from settings.json
    current_flags = settings.get("feature_flags", {})
    add_log_message(f"🔍 Quét cấu hình settings.json phát hiện {len(current_flags)} flags: {list(current_flags.keys())}")
    
    # Track flags by name
    sheet_flags = {row["Tên Flag"]: row for row in all_records if row.get("Tên Flag")}
    
    today_str = datetime.date.today().isoformat()
    
    # Iterate and sync active flags
    for flag_name, flag_val in current_flags.items():
        val_str = "TRUE" if flag_val else "FALSE"
        # Determine flag type
        flag_type = "Ops Flags" if flag_name in ["maintenance_mode", "bypass_cloudinary_quota"] else "Release Flags"
        
        if flag_name in sheet_flags:
            # Existing flag in sheet
            row_data = sheet_flags[flag_name]
            old_val = str(row_data.get("Giá Trị Hiện Tại")).upper()
            old_status = row_data.get("Trạng Thái")
            
            # If value changed or it was previously cleaned but is now active again
            if old_val != val_str or old_status != "active":
                row_data["Giá Trị Hiện Tại"] = val_str
                row_data["Trạng Thái"] = "active"
                row_data["Ngày Cập Nhật"] = today_str
                add_log_message(f"🔄 Cập nhật flag '{flag_name}': {old_val} ➔ {val_str} (status: active)")
            
            # Keep description if empty but defined in code, otherwise preserve what's on sheet
            if not row_data.get("Mô tả"):
                row_data["Mô tả"] = "Chế độ bảo trì hệ thống" if flag_name == "maintenance_mode" else "Cấu hình cờ tính năng"
        else:
            # New flag
            add_log_message(f"➕ Phát hiện flag mới '{flag_name}': {val_str}")
            sheet_flags[flag_name] = {
                "Tên Flag": flag_name,
                "Loại Flag": flag_type,
                "Giá Trị Hiện Tại": val_str,
                "Trạng Thái": "active",
                "Ngày Release": today_str,
                "Ngày Cập Nhật": today_str,
                "Mô tả": "Chế độ bảo trì hệ thống" if flag_name == "maintenance_mode" else "Cấu hình cờ tính năng"
            }
            
    # Mark flags no longer in settings.json as "cleaned"
    for flag_name, row_data in list(sheet_flags.items()):
        if flag_name not in current_flags:
            if row_data.get("Trạng Thái") != "cleaned":
                row_data["Trạng Thái"] = "cleaned"
                row_data["Giá Trị Hiện Tại"] = "FALSE"  # Cleaned flags are off
                row_data["Ngày Cập Nhật"] = today_str
                add_log_message(f"🧹 Flag '{flag_name}' đã bị xóa khỏi cấu hình code. Đổi trạng thái trên sheet ➔ cleaned")
                
    # 6. Re-write all records to the worksheet to keep it clean and sorted
    headers = ["Tên Flag", "Loại Flag", "Giá Trị Hiện Tại", "Trạng Thái", "Ngày Release", "Ngày Cập Nhật", "Mô tả"]
    rows_to_write = [headers]
    
    # Sort flags: active first, then cleaned; alphabetically within status
    sorted_flags = sorted(sheet_flags.values(), key=lambda x: (x.get("Trạng Thái") != "active", x.get("Tên Flag") or ""))
    
    for flag in sorted_flags:
        rows_to_write.append([
            flag.get("Tên Flag", ""),
            flag.get("Loại Flag", ""),
            flag.get("Giá Trị Hiện Tại", ""),
            flag.get("Trạng Thái", ""),
            flag.get("Ngày Release", ""),
            flag.get("Ngày Cập Nhật", ""),
            flag.get("Mô tả", "")
        ])
        
    try:
        # Clear and write back
        worksheet.clear()
        worksheet.update(values=rows_to_write, range_name="A1")
        # Re-apply header formatting
        worksheet.format("A1:G1", {"textFormat": {"bold": True}})
        add_log_message("[✅] Đồng bộ thành công Feature Flags lên Google Sheets!")
        return {"status": "success", "synced_count": len(sheet_flags)}
    except Exception as e:
        add_log_message(f"[❌ LỖI] Lỗi ghi dữ liệu lên worksheet: {str(e)}")
        return {"status": "error", "message": f"Update worksheet error: {str(e)}"}

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    sync_flags()
