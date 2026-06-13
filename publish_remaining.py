#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import time
import curator_server

def main():
    # Đảm bảo mã hóa UTF-8
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    db_file = "raw_archive.db"
    if not os.path.exists(db_file):
        print("[❌ LỖI] Không tìm thấy file Database raw_archive.db")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    rows = cursor.execute("SELECT tk_id FROM listings WHERE status = 'raw_complete'").fetchall()
    conn.close()

    if not rows:
        print("[✅] Không còn căn nào ở trạng thái 'raw_complete' để đẩy!")
        return

    tk_ids = [r[0] for r in rows]
    print(f"[🚀] Phát hiện {len(tk_ids)} căn ở trạng thái 'raw_complete' chưa xuất bản.")
    print("Danh sách:", tk_ids)

    success_count = 0
    for idx, tk_id in enumerate(tk_ids):
        print(f"\n📦 [{idx+1}/{len(tk_ids)}] Đang đẩy căn {tk_id} lên Google Sheets Pool...")
        try:
            res = curator_server.execute_publish_listing(tk_id)
            if res.get("status") == "success":
                success_count += 1
                print(f"[✅ THÀNH CÔNG] Đã đẩy thành công {tk_id}! Trạng thái SQLite -> published")
            else:
                print(f"[⚠️ THẤT BẠI] Căn {tk_id} đẩy thất bại: {res.get('message')}")
        except Exception as e:
            print(f"[❌ LỖI] Lỗi hệ thống khi đẩy căn {tk_id}: {str(e)}")
        
        # Throttling nghỉ 1.5 giây giữa các lần gọi gspread để tránh quota Google API
        time.sleep(1.5)

    print(f"\n[🏁 HOÀN TẤT] Đã đẩy xong hàng loạt! Thành công: {success_count}/{len(tk_ids)} căn.")

if __name__ == '__main__':
    main()
