import sys
import os
import requests
import gspread
import time
import datetime
import hmac
import hashlib
from urllib.parse import urlparse

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
import manager

# Load settings to get R2 credentials
import json
config_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/settings.json"
with open(config_file, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

r2_access_key = cfg.get("r2_access_key_id")
r2_secret_key = cfg.get("r2_secret_access_key")
r2_bucket = cfg.get("r2_bucket_name")
account_id = cfg.get("cloudflare_account_id")
r2_public_url = cfg.get("r2_public_url")

def upload_image_to_r2(file_content, filename, content_type="image/jpeg"):
    host = f"{r2_bucket}.{account_id}.r2.cloudflarestorage.com"
    key = f"BDS-KhangNgo/{filename}"
    path = f"/{key}"
    
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    hashed_payload = hashlib.sha256(file_content).hexdigest()
    canonical_headers = f"host:{host}\nx-amz-content-sha256:{hashed_payload}\nx-amz-date:{amz_date}\n"
    signed_headers = "host;x-amz-content-sha256;x-amz-date"
    
    canonical_request = f"PUT\n{path}\n\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    algorithm = "AWS4-HMAC-SHA256"
    region = "auto"
    service = "s3"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"
    
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = hmac.new(("AWS4" + key).encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = sign(k_date, region_name)
        k_service = sign(k_region, service_name)
        k_signing = sign(k_service, "aws4_request")
        return k_signing
        
    signing_key = get_signature_key(r2_secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    authorization_header = f"{algorithm} Credential={r2_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    url = f"https://{host}{path}"
    headers = {
        'Host': host,
        'Authorization': authorization_header,
        'x-amz-date': amz_date,
        'x-amz-content-sha256': hashed_payload,
        'Content-Type': content_type
    }
    
    r = requests.put(url, data=file_content, headers=headers, timeout=30)
    if r.status_code != 200:
        raise Exception(f"R2 PUT failed with status {r.status_code}: {r.text}")
        
    return f"{r2_public_url}/BDS-KhangNgo/{filename}"

def extract_cloudinary_filename_and_tk_id(url):
    parsed = urlparse(url)
    path = parsed.path
    parts = path.split('/')
    
    filename = parts[-1]
    tk_id = ""
    if "BDS-KhangNgo" in parts:
        idx = parts.index("BDS-KhangNgo")
        if idx + 2 < len(parts):
            tk_id = parts[idx+1]
    return filename, tk_id

def main():
    creds = manager.get_google_credentials()
    if not creds:
        print("[❌ LỖI] Không thể load Google Credentials.")
        return
        
    client = gspread.authorize(creds)
    source_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
    
    print(f"[⚡] Đang mở Google Sheet Source (v1) [ID: {source_id}]...")
    try:
        ss = client.open_by_key(source_id)
        sheet = ss.worksheet("Source")
        all_rows = sheet.get_all_values()
        print(f"[✅] Đã tải {len(all_rows)} dòng từ Google Sheets.")
    except Exception as e:
        print(f"[❌ LỖI] Không thể mở hoặc đọc sheet Source: {e}")
        return
        
    # Scan for remaining Cloudinary URLs
    print("[⚡] Quét và di cư trực tiếp các ô Cloudinary sang R2...")
    cells_to_update = []
    
    # We will limit requests or use a simple loop
    processed_count = 0
    success_count = 0
    fail_count = 0
    
    for r_idx, row in enumerate(all_rows[2:], start=3):
        ma_kn = row[3] if len(row) > 3 else ""
        for c_idx, val in enumerate(row):
            if val and "cloudinary.com" in val:
                processed_count += 1
                filename, folder_tk_id = extract_cloudinary_filename_and_tk_id(val)
                r2_filename = f"{folder_tk_id}_{filename}" if folder_tk_id else filename
                
                print(f"[{processed_count}] Căn {ma_kn} | Dòng {r_idx}, Cột {c_idx+1} | Đang tải {filename}...")
                
                migrated_url = None
                try:
                    res = requests.get(val, timeout=15)
                    if res.status_code == 200:
                        file_content = res.content
                        migrated_url = upload_image_to_r2(file_content, r2_filename)
                        success_count += 1
                    else:
                        print(f"  [⚠️ 404/Lỗi] HTTP {res.status_code} khi tải {val}")
                        fail_count += 1
                except Exception as e:
                    print(f"  [❌ LỖI] {e}")
                    fail_count += 1
                    
                if migrated_url:
                    cell = gspread.Cell(r_idx, c_idx + 1, migrated_url)
                    cells_to_update.append(cell)
                    
                # Small throttle to not overload Cloudinary or R2
                time.sleep(0.1)
                
    print(f"\n[📊] Kết quả quét di cư trực tiếp:")
    print(f"  - Tổng số ô Cloudinary phát hiện: {processed_count}")
    print(f"  - Thành công tải và upload R2: {success_count}")
    # Batch update
    if cells_to_update:
        print(f"[⚡] Đang lưu {len(cells_to_update)} ô R2 mới lên Google Sheet...")
        chunk_size = 300
        for i in range(0, len(cells_to_update), chunk_size):
            chunk = cells_to_update[i:i + chunk_size]
            print(f"  -> Đang lưu batch {i // chunk_size + 1}...")
            try:
                sheet.update_cells(chunk, value_input_option='USER_ENTERED')
                print("     [✅] Đã hoàn thành batch.")
                time.sleep(2)
            except Exception as e:
                print(f"     [❌ LỖI] Lỗi ghi batch: {e}")
                
    print("\n[🏁 HOÀN TẤT] Đồng bộ trực tiếp R2 lên sheet Source (v1) đã hoàn thành!")

if __name__ == '__main__':
    main()
