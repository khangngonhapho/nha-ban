# -*- coding: utf-8 -*-
import os
import sys
import shutil
import json
import time
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

# Set UTF-8 encoding for standard output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def create_zip_and_upload():
    project_dir = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo"
    dist_dir = os.path.join(project_dir, "dist")
    target_dir = os.path.join(dist_dir, "KhangNgoCurator")
    zip_base_name = os.path.join(dist_dir, "KhangNgoCurator")
    zip_file_path = zip_base_name + ".zip"
    
    print("==================================================================")
    print("       TIẾN TRÌNH TỰ ĐỘNG NÉN VÀ TẢI LÊN GOOGLE DRIVE")
    print("==================================================================")
    print("")
    
    # 1. Kiểm tra thư mục nguồn
    if not os.path.isdir(target_dir):
        print(f"[❌ LỖI] Không tìm thấy thư mục biên dịch tại: {target_dir}")
        print("Vui lòng chạy build_exe.bat trước.")
        sys.exit(1)
        
    print(f"[*] Thư mục nguồn: {target_dir}")
    print(f"[*] Đang nén thư mục thành file ZIP tại: {zip_file_path} ...")
    
    try:
        # Nén thư mục
        start_time = time.time()
        # root_dir is dist_dir, base_dir is "KhangNgoCurator"
        shutil.make_archive(zip_base_name, "zip", dist_dir, "KhangNgoCurator")
        duration = time.time() - start_time
        zip_size_mb = os.path.getsize(zip_file_path) / (1024 * 1024)
        print(f"[✅ THÀNH CÔNG] Đã tạo xong file zip trong {duration:.2f} giây.")
        print(f"[*] Dung lượng file ZIP: {zip_size_mb:.2f} MB")
    except Exception as e:
        print(f"[❌ LỖI] Không thể tạo file nén ZIP: {str(e)}")
        sys.exit(1)
        
    # 2. Upload file lên Google Drive
    config_path = os.path.join(project_dir, "settings.json")
    credentials_path = os.path.join(project_dir, "credentials.json")
    
    # Đọc cấu hình để lấy folder_id
    drive_folder_id = "10NcfOJ3_YBiPVc4FSK2uGGNs7MPmAFO8"  # Default fallback
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                drive_folder_id = cfg.get("drive_folder_id", drive_folder_id)
        except Exception:
            pass
            
    if not os.path.exists(credentials_path):
        print(f"[❌ LỖI] Không tìm thấy credentials.json tại: {credentials_path}")
        print("Không có quyền kết nối để tải lên Google Drive.")
        sys.exit(1)
        
    print(f"[*] Đang xác thực tài khoản Google Service Account...")
    try:
        scopes = ['https://www.googleapis.com/auth/drive.file']
        creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        token = creds.token
        print("[✅ XÁC THỰC THÀNH CÔNG] Đã lấy được Access Token.")
    except Exception as e:
        print(f"[❌ LỖI] Xác thực Google thất bại: {str(e)}")
        sys.exit(1)
        
    print(f"[*] Thư mục Drive đích: {drive_folder_id}")
    print(f"[*] Đang tải tệp ZIP lên Google Drive (Vui lòng đợi)...")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        metadata = {
            "name": "KhangNgoCurator.zip",
            "parents": [drive_folder_id] if drive_folder_id else []
        }
        
        with open(zip_file_path, "rb") as f:
            zip_data = f.read()
            
        files = {
            "data": ("metadata", json.dumps(metadata), "application/json"),
            "file": ("KhangNgoCurator.zip", zip_data, "application/zip")
        }
        
        # Chạy upload qua Google Drive v3 REST API
        start_upload = time.time()
        r = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
            headers=headers,
            files=files,
            timeout=300  # 5 phút timeout cho file lớn
        )
        
        if r.status_code == 403:
            print("")
            print("==================================================================")
            print("❌ LỖI BẢO MẬT: THƯ MỤC GOOGLE DRIVE CHƯA ĐƯỢC CHIA SẺ!")
            print("==================================================================")
            print("Tài khoản Service Account Google của anh chưa có quyền ghi vào thư mục này.")
            print("")
            print("Anh chỉ cần làm 2 bước đơn giản sau để sửa trong 10 giây:")
            print(f"  1. Mở Google Drive của anh, tìm thư mục có ID: '{drive_folder_id}'")
            print("     (Hoặc thư mục bất kỳ anh muốn dùng làm nơi lưu file zip).")
            print("  2. Click chuột phải chọn 'Chia sẻ' (Share) -> Thêm email này làm 'Người chỉnh sửa' (Editor):")
            print("     👉 bds-autopost-bot@khangngo-admin.iam.gserviceaccount.com")
            print("  3. Nhấn 'Gửi' (Send) và chạy lại file này!")
            print("==================================================================")
            print("")
            sys.exit(1)
            
        if r.status_code != 200:
            print(f"[❌ LỖI API] Google Drive trả về mã lỗi HTTP {r.status_code}: {r.text}")
            sys.exit(1)
            
        res_json = r.json()
        file_id = res_json.get("id")
        upload_duration = time.time() - start_upload
        print(f"[✅ THÀNH CÔNG] Đã tải tệp lên Drive trong {upload_duration:.2f} giây. ID file: {file_id}")
        
        # 3. Cấu hình phân quyền xem công khai (Public Access Sharing)
        print("[*] Đang cấu hình phân quyền tải công khai cho tệp...")
        permission = {
            "role": "reader",
            "type": "anyone"
        }
        r_perm = requests.post(
            f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
            headers=headers,
            json=permission,
            timeout=20
        )
        
        if r_perm.status_code == 200:
            print("[✅ THÀNH CÔNG] Đã mở quyền công khai.")
        else:
            print(f"[⚠️ CẢNH BÁO] Không thể thiết lập quyền công khai: {r_perm.text}")
            
        public_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
        print("")
        print("==================================================================")
        print("                   [🏆 TẤT CẢ ĐÃ HOÀN TẤT]")
        print("")
        print("Đường liên kết tải ứng dụng KhangNgoCurator.zip chính thức:")
        print(f"👉 {public_link}")
        print("==================================================================")
        print("")
        
        # Lưu link download vào file để tiện sử dụng
        link_file = os.path.join(project_dir, "download_link.txt")
        with open(link_file, "w", encoding="utf-8") as lf:
            lf.write(public_link)
            
    except Exception as e:
        print(f"[❌ LỖI CỰC ĐOAN] Gặp sự cố trong quá trình upload: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_zip_and_upload()
