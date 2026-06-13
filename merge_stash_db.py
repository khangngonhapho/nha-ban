import os
import sys
import sqlite3
import shutil
import json

# Ép terminal Windows/các hệ điều hành mã hóa UTF-8 để hiển thị ký tự Tiếng Việt không bị lỗi
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def merge_database():
    current_db = "raw_archive.db"
    stash_db = "scratch/raw_archive_stash.db"
    backup_db = "scratch/raw_archive_pre_merge.db"

    print("=======================================================================")
    print("🔄 BẮT ĐẦU QUY TRÌNH HỢP NHẤT DATABASE SQLITE TỪ STASH GIT")
    print("👉 Khôi phục an toàn 850 căn chưa push lên Sheets!")
    print("=======================================================================")

    if not os.path.exists(current_db):
        print(f"[❌ LỖI] File database hiện tại '{current_db}' không tồn tại!")
        return

    if not os.path.exists(stash_db):
        print(f"[❌ LỖI] File database stashed '{stash_db}' không tồn tại!")
        return

    # 1. Tạo file backup an toàn
    print("[1/4] Đang sao lưu database hiện tại...")
    try:
        shutil.copy2(current_db, backup_db)
        print(f"  - Đã backup an toàn sang '{backup_db}'")
    except Exception as e:
        print(f"  - [❌ LỖI] Không thể sao lưu file database: {str(e)}")
        return

    # 2. Kết nối tới hai database
    conn_curr = sqlite3.connect(current_db)
    conn_stash = sqlite3.connect(stash_db)
    
    cursor_curr = conn_curr.cursor()
    cursor_stash = conn_stash.cursor()

    # 3. Phân tích các ID thiếu trong database hiện tại
    print("\n[2/4] Phân tích sự khác biệt giữa hai database...")
    
    cursor_curr.execute("SELECT tk_id FROM listings")
    current_ids = set(row[0] for row in cursor_curr.fetchall())
    
    cursor_stash.execute("SELECT tk_id, status FROM listings")
    stash_records = cursor_stash.fetchall()
    
    missing_records = [r for r in stash_records if r[0] not in current_ids]
    
    print(f"  - Số căn trong database hiện tại: {len(current_ids)}")
    print(f"  - Số căn trong database stashed: {len(stash_records)}")
    print(f"  - Số căn bị thiếu trong database hiện tại: {len(missing_records)}")
    
    status_counts = {}
    for tk_id, status in missing_records:
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"    * Trạng thái '{status}': {count} căn")

    if not missing_records:
        print("\n[✅] Không có căn nào bị thiếu. Không cần hợp nhất!")
        conn_curr.close()
        conn_stash.close()
        return

    # 4. Thực hiện sao chép các hàng bị thiếu từ stash sang current
    print("\n[3/4] Bắt đầu hợp nhất dữ liệu bảng 'listings'...")
    
    # Lấy danh sách cột
    cursor_stash.execute("PRAGMA table_info(listings)")
    cols_stash = [row[1] for row in cursor_stash.fetchall()]
    
    col_str = ", ".join([f"`{col}`" for col in cols_stash if col != 'id'])
    placeholder_str = ", ".join(["?" for col in cols_stash if col != 'id'])
    
    merged_count = 0
    for tk_id, status in missing_records:
        # Lấy dữ liệu chi tiết của dòng này từ stash_db
        select_sql = f"SELECT * FROM listings WHERE tk_id = ?"
        cursor_stash.execute(select_sql, (tk_id,))
        row_values = cursor_stash.fetchone()
        
        if not row_values:
            continue
            
        # Ánh xạ thành dictionary để bỏ qua trường 'id' (tự động tăng trong database mới)
        row_dict = {}
        for col_idx, col_name in enumerate(cols_stash):
            row_dict[col_name] = row_values[col_idx]
            
        # Chuẩn bị dữ liệu insert (bỏ qua 'id')
        insert_vals = [row_dict[col] for col in cols_stash if col != 'id']
        
        insert_sql = f"INSERT INTO listings ({col_str}) VALUES ({placeholder_str})"
        cursor_curr.execute(insert_sql, insert_vals)
        merged_count += 1

    conn_curr.commit()
    print(f"  - [✅ listings] Đã hợp nhất thành công {merged_count} căn vào bảng listings!")

    # 5. Hợp nhất bảng 'crawl_sessions' nếu có
    print("\n[4/4] Bắt đầu hợp nhất dữ liệu bảng 'crawl_sessions'...")
    try:
        cursor_curr.execute("SELECT id FROM crawl_sessions")
        current_sess_ids = set(row[0] for row in cursor_curr.fetchall())
        
        cursor_stash.execute("SELECT * FROM crawl_sessions")
        stash_sessions = cursor_stash.fetchall()
        
        cursor_stash.execute("PRAGMA table_info(crawl_sessions)")
        cols_sess = [row[1] for row in cursor_stash.fetchall()]
        
        sess_col_str = ", ".join([f"`{col}`" for col in cols_sess if col != 'id'])
        sess_placeholder_str = ", ".join(["?" for col in cols_sess if col != 'id'])
        
        merged_sess_count = 0
        for sess in stash_sessions:
            sess_dict = {}
            for col_idx, col_name in enumerate(cols_sess):
                sess_dict[col_name] = sess[col_idx]
                
            sess_id = sess_dict['id']
            if sess_id not in current_sess_ids:
                insert_sess_vals = [sess_dict[col] for col in cols_sess if col != 'id']
                insert_sess_sql = f"INSERT INTO crawl_sessions ({sess_col_str}) VALUES ({sess_placeholder_str})"
                cursor_curr.execute(insert_sess_sql, insert_sess_vals)
                merged_sess_count += 1
                
        conn_curr.commit()
        print(f"  - [✅ crawl_sessions] Đã hợp nhất thành công {merged_sess_count} phiên cào!")
    except Exception as sess_err:
        print(f"  - [⚠️ WARNING] Lỗi khi hợp nhất bảng crawl_sessions: {str(sess_err)}")

    # 6. Hiển thị tổng kết cuối cùng
    print("\n=======================================================================")
    print("📊 TỔNG KẾT SAU KHI HỢP NHẤT:")
    cursor_curr.execute("SELECT status, count(*) FROM listings GROUP BY status")
    final_counts = cursor_curr.fetchall()
    for status, count in final_counts:
        print(f"  - Trạng thái '{status}': {count} căn")
    print("=======================================================================")
    
    conn_curr.close()
    conn_stash.close()
    print("🏁 HỢP NHẤT HOÀN TẤT THÀNH CÔNG RỰC RỠ!")

if __name__ == "__main__":
    merge_database()
