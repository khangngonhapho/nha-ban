import os
import sys
import json
import sqlite3
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

project_root = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"

def get_google_credentials():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    cred_file = os.path.join(project_root, 'khangngo-admin-a96043c2f638.json')
    if not os.path.exists(cred_file):
        cred_file = os.path.join(project_root, 'credentials.json')
    return service_account.Credentials.from_service_account_file(cred_file, scopes=scopes)

def main():
    print("========== KIEM TRA DONG NHAT DONG CUOI (SQLITE vs GOOGLE SHEET) ==========")
    
    # 1. Doc dong cuoi tu SQLite local
    db_path = os.path.join(project_root, "raw_archive.db")
    if not os.path.exists(db_path):
        print("[-] Loi: Khong tim thay file SQLite raw_archive.db")
        return
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Lay thong tin dong cuoi trong listings
    sqlite_row = cursor.execute("SELECT * FROM listings ORDER BY rowid DESC LIMIT 1").fetchone()
    conn.close()
    
    if not sqlite_row:
        print("[-] CSDL SQLite cuc bo hien dang trong (0 ban ghi)!")
        return
        
    sqlite_dict = dict(sqlite_row)
    print("\n[1] BAN GHI CUOI CUNG TRONG SQLITE CUC BO:")
    print(f"    - ID cuc bo: {sqlite_dict.get('id')}")
    print(f"    - Ma Thien Khoi (Ma_Hang): {sqlite_dict.get('Ma_Hang')}")
    print(f"    - UUID Thien Khoi (tk_id): {sqlite_dict.get('tk_id')}")
    
    # safe encoding prints for address columns
    duong = str(sqlite_dict.get('Duong')).encode('ascii', errors='ignore').decode()
    quan = str(sqlite_dict.get('Quan')).encode('ascii', errors='ignore').decode()
    ma_kn = str(sqlite_dict.get('Ma_Khang_Ngo_ID')).encode('ascii', errors='ignore').decode()
    
    print(f"    - Ma Khang Ngo (ID): {ma_kn}")
    print(f"    - Duong pho: {duong}")
    print(f"    - Quan/Huyen: {quan}")
    print(f"    - Trang thai: {sqlite_dict.get('Trang_thai')}")
    
    # 2. Doc cau hinh sheet_id tu settings.json
    sheet_id = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw" # Default
    settings_path = os.path.join(project_root, "settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                sheet_id = cfg.get("sheet_id", sheet_id)
        except Exception as e:
            print("[-] Loi doc settings.json:", e)
            
    print(f"\n[+] Ket noi Google Sheets (ID: {sheet_id})...")
    
    # 3. Lay dong cuoi tu Google Sheets tab Pool
    try:
        creds = get_google_credentials()
        req = google.auth.transport.requests.Request()
        creds.refresh(req)
        token = creds.token
        
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/Pool!A1:CE1000"
        headers = {'Authorization': f'Bearer {token}'}
        res = requests.get(url, headers=headers)
        
        if res.status_code != 200:
            print("[-] Loi ket noi Google Sheets API:", res.text)
            return
            
        sheet_data = res.json()
        values = sheet_data.get("values", [])
        
        if not values or len(values) < 2:
            print("[-] Google Sheets tab Pool hien dang trong (chi co header hoac khong co du lieu)!")
            return
            
        headers_row = values[0]
        last_sheet_row = values[-1]
        last_row_index = len(values) # Dong thu may trong file Sheets (1-indexed)
        
        sheet_dict = {}
        for idx, header in enumerate(headers_row):
            if idx < len(last_sheet_row):
                sheet_dict[header] = last_sheet_row[idx]
            else:
                sheet_dict[header] = ""
                
        print(f"\n[2] BAN GHI CUOI CUNG TREN GOOGLE SHEETS TAB 'POOL' (Dong so {last_row_index}):")
        
        sheet_tk_id = str(sheet_dict.get('Mã Hàng', '')).encode('ascii', errors='ignore').decode()
        sheet_ma_kn = str(sheet_dict.get('Mã Khang Ngô (ID)', '')).encode('ascii', errors='ignore').decode()
        sheet_duong = str(sheet_dict.get('Đường', '')).encode('ascii', errors='ignore').decode()
        sheet_quan = str(sheet_dict.get('Quận', '')).encode('ascii', errors='ignore').decode()
        sheet_status = str(sheet_dict.get('Trạng thái', '')).encode('ascii', errors='ignore').decode()
        sheet_author = str(sheet_dict.get('Người ký', '')).encode('ascii', errors='ignore').decode()
        
        print(f"    - Ma Hang (tk_id): {sheet_tk_id}")
        print(f"    - Ma Khang Ngo (ID): {sheet_ma_kn}")
        print(f"    - Duong: {sheet_duong}")
        print(f"    - Quan: {sheet_quan}")
        print(f"    - Trang thai: {sheet_status}")
        print(f"    - Nguoi ky: {sheet_author}")
        
        # 4. So sanh doi chieu
        print("\n[3] KET LUAN SO SANH DOI CHIEU:")
        db_ma_hang = sqlite_dict.get('Ma_Hang')
        sheet_tk_id_orig = sheet_dict.get('Mã Hàng')
        
        if db_ma_hang == sheet_tk_id_orig:
            print("    [ OK ] Dong cuoi cung cua SQLite va Google Sheets TRUNG KHOP HOAN TOAN!")
            print(f"    Ca hai noi deu dung o can co Ma Hang: {db_ma_hang}")
            print("    He thong dong bo binh thuong, ban co the tiep tuc cao tin.")
        else:
            print("    [ ERROR ] Dong cuoi cung cua SQLite va Google Sheets KHONG KHOP!")
            print(f"    - SQLite dang dung o: {db_ma_hang}")
            print(f"    - Google Sheets dang dung o: {sheet_tk_id_orig}")
            print("    Vui long kiem tra ky hoac tien hanh dong bo thu cong truoc khi cao tiep.")
            
    except Exception as e:
        print("[-] Loi trong qua trinh ket noi Google Sheets:", e)

if __name__ == "__main__":
    main()
