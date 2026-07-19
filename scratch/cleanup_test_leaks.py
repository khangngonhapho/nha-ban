import sys
import os
import sqlite3
import gspread

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manager
from manager import get_google_credentials, load_config

def delete_sqlite_mock():
    print("=== Dọn dẹp SQLite ===")
    dbs = ['raw_archive.db', 'raw_archive_staging.db']
    for db in dbs:
        if os.path.exists(db):
            try:
                conn = sqlite3.connect(db)
                cursor = conn.cursor()
                # Xóa trong bảng listings
                cursor.execute("DELETE FROM listings WHERE tk_id IN ('test-tk-id-123', 'fba67440-d5a7-45c1-80ca-e939409862a2') OR Ma_Hang IN ('TEST-MA-HANG', 'TKQGYNN5')")
                deleted_listings = cursor.rowcount
                
                # Xóa trong bảng listings_images
                cursor.execute("DELETE FROM listings_images WHERE tk_id IN ('test-tk-id-123', 'fba67440-d5a7-45c1-80ca-e939409862a2')")
                deleted_images = cursor.rowcount
                
                conn.commit()
                conn.close()
                print(f"[✅] DB {db}: Đã xóa {deleted_listings} listings và {deleted_images} listings_images.")
            except Exception as e:
                print(f"[❌] Lỗi khi dọn dẹp DB {db}: {str(e)}")

def delete_sheets_mock():
    print("\n=== Dọn dẹp Google Sheets ===")
    creds = get_google_credentials()
    if not creds:
        print("[⚠️] Không thể lấy Google Credentials, bỏ qua dọn dẹp Sheets.")
        return
        
    client = gspread.authorize(creds)
    cfg = load_config()
    
    # Danh sách sheet IDs để quét dọn dẹp
    sheet_ids = [
        cfg.get("sheet_id"),  # Production Pool
        cfg.get("staging_pool_sheet_id")  # Staging Pool
    ]
    
    # Loại bỏ các giá trị None/rỗng
    sheet_ids = [sid for sid in sheet_ids if sid]
    
    for sid in sheet_ids:
        try:
            print(f"Đang kiểm tra spreadsheet: {sid}...")
            ss = client.open_by_key(sid)
            # Quét tất cả các worksheet
            for wks in ss.worksheets():
                title = wks.title
                if title not in ["Pool", "Source", "Pool_Images"]:
                    continue
                    
                rows = wks.get_all_values()
                if not rows:
                    continue
                    
                # Tìm các dòng có mock data
                rows_to_delete = []
                for idx, row in enumerate(rows):
                    row_str = " ".join(row).lower()
                    if any(term in row_str for term in ["test-tk-id-123", "test-ma-hang", "fba67440-d5a7-45c1-80ca-e939409862a2", "tkqgynn5", "540.36a"]):
                        rows_to_delete.append(idx + 1) # 1-indexed
                        
                if rows_to_delete:
                    print(f"  -> Phát hiện {len(rows_to_delete)} dòng rác tại tab '{title}'")
                    # Xóa ngược từ dưới lên để tránh lệch chỉ số dòng
                    for r_idx in sorted(rows_to_delete, reverse=True):
                        wks.delete_rows(r_idx)
                        print(f"    [✅] Đã xóa dòng {r_idx} tại tab '{title}'")
                else:
                    print(f"  -> Tab '{title}' sạch sẽ.")
        except Exception as e:
            print(f"  [❌] Lỗi khi xử lý spreadsheet {sid}: {str(e)}")

def delete_r2_mock():
    print("\n=== Dọn dẹp Cloudflare R2 ===")
    try:
        import boto3
        cfg = load_config()
        r2_access_key = cfg.get("r2_access_key_id")
        r2_secret_key = cfg.get("r2_secret_access_key")
        r2_bucket = cfg.get("r2_bucket_name")
        account_id = cfg.get("cloudflare_account_id")
        
        if not (r2_access_key and r2_secret_key and r2_bucket and account_id):
            print("[⚠️] Cấu hình R2 không đầy đủ, bỏ qua dọn dẹp R2.")
            return
            
        s3 = boto3.client(
            service_name='s3',
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key,
            region_name="auto"
        )
        
        # Danh sách prefix cần tìm kiếm dọn dẹp
        # BDS-KhangNgo-v2 và BDS-KhangNgo-v3
        prefixes = [
            "BDS-KhangNgo-v2/test-uuid-space",
            "BDS-KhangNgo-v3/test-uuid-space",
            "BDS-KhangNgo-v2/fba67440-d5a7-45c1-80ca-e939409862a2",
            "BDS-KhangNgo-v3/fba67440-d5a7-45c1-80ca-e939409862a2"
        ]
        for prefix in prefixes:
            response = s3.list_objects_v2(Bucket=r2_bucket, Prefix=prefix)
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    print(f"Đang xóa tệp R2: {key}...")
                    s3.delete_object(Bucket=r2_bucket, Key=key)
                    print(f"  [✅] Đã xóa thành công tệp R2: {key}")
            else:
                print(f"Prefix '{prefix}' sạch sẽ.")
    except Exception as e:
        print(f"[❌] Lỗi khi dọn dẹp R2: {str(e)}")

if __name__ == "__main__":
    delete_sqlite_mock()
    delete_sheets_mock()
    delete_r2_mock()
    print("\n=== DỌN DẸP HOÀN TẤT ===")
