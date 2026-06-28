import os
import sys
import sqlite3
import time
import json
import requests
import gspread

# Ensure imports work from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from manager import get_google_credentials, load_config
from fetcher import extract_tokens, try_refresh_tokens

sys.stdout.reconfigure(encoding='utf-8')

def verify_access_token(access_token):
    """Kiểm tra nhanh xem access_token còn hiệu lực truy cập API không"""
    if not access_token:
        return False
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {access_token}"
        }
        r = requests.get("https://backend.thienkhoi.com/auth/v1/users/me", headers=headers, timeout=10)
        return r.status_code == 200
    except Exception:
        return False

def main():
    print("======================================================================")
    print("🔄 BẮT ĐẦU TRÍCH XUẤT VÀ ĐỒNG BỘ HƯỚNG CHO CÁC CĂN CŨ (BACKFILL)")
    print("======================================================================")
    
    # 1. Đọc và kiểm tra token từ file cookie
    cookie_path = "thienkhoi_cookie.txt"
    if not os.path.exists(cookie_path):
        print("[❌ LỖI] Không tìm thấy file thienkhoi_cookie.txt. Vui lòng cào thử 1 căn trên UI để lưu cookie trước.")
        sys.exit(1)
        
    with open(cookie_path, 'r', encoding='utf-8') as f:
        cookie_str = f.read().strip()
        
    access_token, _, _ = extract_tokens(cookie_str)
    
    print("[*] Đang kiểm tra token hiện tại...")
    if verify_access_token(access_token):
        print("[✅ SUCCESS] Token hiện tại còn hiệu lực. Bỏ qua bước làm mới.")
    else:
        print("[*] Token hiện tại đã hết hạn. Đang thử làm mới token...")
        refreshed_cookie = try_refresh_tokens(cookie_path)
        if refreshed_cookie:
            access_token, _, _ = extract_tokens(refreshed_cookie)
            if verify_access_token(access_token):
                print("[✅ SUCCESS] Làm mới token thành công!")
            else:
                print("[❌ LỖI] Đã refresh token nhưng token mới vẫn không hợp lệ hoặc không có quyền truy cập.")
                sys.exit(1)
        else:
            print("[❌ LỖI] Không thể làm mới token. Phiên đăng nhập/Refresh token đã hết hạn hoàn toàn.")
            print("Vui lòng cào thử hoặc lưu cookie mới từ trình duyệt để chạy lại.")
            sys.exit(1)
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    # 2. Kết nối Google Sheets để lấy bản đồ dòng
    print("[1/4] Đang kết nối Google Sheets...")
    creds = get_google_credentials()
    cfg = load_config()
    sheet_id = cfg.get("sheet_id") or "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
    
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    sheet_pool = spreadsheet.worksheet("Pool")
    
    pool_rows = sheet_pool.get_all_values()
    if len(pool_rows) < 2:
        print("[❌ LỖI] Bảng Pool trống.")
        sys.exit(1)
        
    # Map Mã Hàng -> Dòng trên Google Sheet (1-based)
    ma_hang_to_row_num = {}
    for idx, row in enumerate(pool_rows[1:], start=2):
        if row and row[0]:
            ma_hang_to_row_num[row[0].strip()] = idx
            
    print(f"  - Tìm thấy {len(ma_hang_to_row_num)} mã hàng trong sheet Pool.")

    # 3. Tìm các căn trống Hướng trong SQLite
    print("[2/4] Đang kết nối SQLite thô...")
    conn = sqlite3.connect('raw_archive.db')
    cursor = conn.cursor()
    
    # Lấy các tin có tk_id (không phải LEGACY) và đang bị trống Hướng
    cursor.execute("""
        SELECT tk_id, Ma_Hang, custom_huong 
        FROM listings 
        WHERE (Huong IS NULL OR Huong = '') 
          AND tk_id NOT LIKE 'LEGACY-%'
    """)
    listings_to_backfill = cursor.fetchall()
    
    print(f"  - Phát hiện {len(listings_to_backfill)} căn trong SQLite đang bị trống Hướng.")

    # 4. Trích xuất Hướng từ API và cập nhật
    if listings_to_backfill:
        print("[3/4] Bắt đầu gọi API Thiên Khôi để lấy Hướng...")
        for idx, (tk_id, ma_hang, custom_huong) in enumerate(listings_to_backfill, start=1):
            print(f"  [{idx}/{len(listings_to_backfill)}] Đang xử lý căn {ma_hang} (TK ID: {tk_id})...")
            
            detail_api_url = f"https://backend.thienkhoi.com/product/v1/property/{tk_id}"
            
            try:
                r = requests.get(detail_api_url, headers=headers, timeout=15)
                if r.status_code == 200:
                    detail_data = r.json().get("data") or {}
                    criteria_list = detail_data.get("criteria") or []
                    huong = next((c.get("name", "") for c in criteria_list if c and c.get("groupCode") == "HOUSE_DIRECTION"), "")
                    
                    if huong:
                        print(f"    -> Tìm thấy Hướng: {huong}")
                        
                        # Cập nhật SQLite
                        if not custom_huong or not custom_huong.strip() or custom_huong == "-":
                            cursor.execute("UPDATE listings SET Huong = ?, custom_huong = ? WHERE tk_id = ?", (huong, huong, tk_id))
                        else:
                            cursor.execute("UPDATE listings SET Huong = ? WHERE tk_id = ?", (huong, tk_id))
                        
                        conn.commit()
                    else:
                        print("    -> Căn này không có thông tin Hướng.")
                else:
                    print(f"    [⚠️] Không thể tải dữ liệu: HTTP {r.status_code}")
                    # Nếu bị 401 tiếp thì dừng tiến trình vì token hết hạn hẳn
                    if r.status_code in [401, 403]:
                        print("[❌ LỖI] Token hết hạn hoặc không có quyền truy cập. Vui lòng cập nhật Cookie Thiên Khôi mới trên web rồi chạy lại.")
                        break
            except Exception as e:
                print(f"    [❌ LỖI] Lỗi kết nối API: {e}")
                
            # Thơ giãn 0.5s tránh overload API đối tác
            time.sleep(0.5)
    else:
        print("[3/4] Không có căn mới nào cần trích xuất từ API.")

    # 5. Đồng bộ tất cả Hướng đang có trong SQLite lên Google Sheets Pool
    cursor.execute("""
        SELECT Ma_Hang, Huong 
        FROM listings 
        WHERE Huong IS NOT NULL AND Huong != ''
    """)
    sqlite_directions = cursor.fetchall()
    conn.close()
    
    print(f"[4/4] Phát hiện {len(sqlite_directions)} căn đã có Hướng trong SQLite. Bắt đầu đồng bộ lên Google Sheets Pool (Cột R)...")
    
    if sqlite_directions:
        batch_data = []
        for ma_hang, huong in sqlite_directions:
            row_num = ma_hang_to_row_num.get(ma_hang)
            if row_num:
                batch_data.append({
                    'range': f'R{row_num}',
                    'values': [[huong]]
                })
                
        if batch_data:
            # Chia nhỏ nhóm 100 dòng để push an toàn
            chunk_size = 100
            for i in range(0, len(batch_data), chunk_size):
                chunk = batch_data[i:i+chunk_size]
                sheet_pool.batch_update(chunk, value_input_option='USER_ENTERED')
                print(f"  - Đã đẩy thành công nhóm {i//chunk_size + 1} ({len(chunk)} dòng).")
                
        print(f"======================================================================")
        print(f"🏁 HOÀN TẤT: Đã cập nhật và đồng bộ thành công Hướng cho các căn cũ!")
        print(f"======================================================================")
    else:
        print("Không có Hướng nào trong SQLite để đồng bộ lên Google Sheets.")

if __name__ == '__main__':
    main()
