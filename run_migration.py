#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import manager as curator_server

def main():
    # Đảm bảo mã hóa UTF-8
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    cookie = ""
    if os.path.exists("thienkhoi_cookie.txt"):
        try:
            with open("thienkhoi_cookie.txt", "r", encoding="utf-8") as f:
                cookie = f.read().strip()
            print("[🔒] Đã đọc cookie thành công từ thienkhoi_cookie.txt!")
        except Exception as e:
            print(f"[❌ LỖI] Không thể đọc thienkhoi_cookie.txt: {str(e)}")
    else:
        print("[⚠️ WARNING] Không tìm thấy file thienkhoi_cookie.txt. Sẽ chạy không cookie (nếu link ảnh public).")

    print("[🚀] Bắt đầu kích hoạt luồng di cư hình ảnh và tự động đẩy Google Sheets cho các căn còn lại...")
    curator_server.run_image_migration_thread(limit=None, cookie=cookie)

if __name__ == '__main__':
    main()
