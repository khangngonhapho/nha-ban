# -*- coding: utf-8 -*-
"""
==================================================
KHANG NGÔ NHÀ PHỐ - STANDALONE BACKGROUND CURATOR WORKER
Tiến trình xử lý ngầm độc lập (Luồng 2)
Xử lý AI curation, Di cư hình ảnh R2 và Đồng bộ Google Sheets Pool
==================================================
"""

import os
import sys
import time
import json
import sqlite3
import random
import subprocess
from datetime import datetime

# Đảm bảo import được các module từ thư mục dự án
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import manager
import pool_lego

LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.lock")
WORKER_PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worker.pid")

class DBLock:
    def __init__(self, lock_path=LOCK_FILE):
        self.lock_path = lock_path
        self.fd = None

    def acquire(self, timeout=60):
        start = time.time()
        while True:
            try:
                # Tạo file ở chế độ độc quyền (exclusive write lock)
                self.fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return True
            except FileExistsError:
                # Kiểm tra khóa bị kẹt (quá 5 phút)
                try:
                    mtime = os.path.getmtime(self.lock_path)
                    if time.time() - mtime > 300:
                        try:
                            os.remove(self.lock_path)
                            print("[🛡️ Guard] Phát hiện và giải phóng file lock bị kẹt của phiên cũ.")
                        except Exception:
                            pass
                        continue
                except Exception:
                    pass
                
                if time.time() - start > timeout:
                    raise TimeoutError(f"Không thể lấy khóa ghi database sau {timeout} giây.")
                time.sleep(0.5)

    def release(self):
        if self.fd is not None:
            try:
                os.close(self.fd)
            except Exception:
                pass
            try:
                os.remove(self.lock_path)
            except Exception:
                pass
            self.fd = None


def process_raw_listings():
    db_file = manager.DB_FILE
    if not os.path.exists(db_file):
        return

    # 1. Tìm các căn có status = 'raw_text'
    conn = None
    rows = []
    try:
        conn = sqlite3.connect(db_file, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = cursor.execute(
            f"SELECT tk_id FROM {manager.LISTINGS_TABLE} WHERE status = 'raw_text'"
        ).fetchall()
        conn.close()
    except Exception as e:
        print(f"[⚠️ WARNING] Lỗi đọc danh sách hàng đợi từ SQLite: {str(e)}")
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        return

    if not rows:
        return

    print(f"\n[🚀] Phát hiện {len(rows)} căn thô (raw_text) trong hàng đợi SQLite. Đang chuẩn bị xử lý...")

    # Đọc cookie từ cache
    cookie = ""
    if os.path.exists(manager.COOKIE_FILE):
        try:
            with open(manager.COOKIE_FILE, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
        except Exception:
            pass

    lock = DBLock()
    
    for row in rows:
        tk_id = row["tk_id"]
        print(f"\n[*] --------------------------------------------------")
        print(f"[*] Bắt đầu xử lý căn: {tk_id}")
        print(f"[*] --------------------------------------------------")

        # Đóng gói acquire lock để tránh xung đột với restore_db_from_sheets
        try:
            lock.acquire(timeout=60)
        except Exception as e_lock:
            print(f"[❌ LOCK ERROR] Bỏ qua căn {tk_id} do không thể lấy lock DB: {str(e_lock)}")
            continue

        try:
            # 1. Lấy dữ liệu của căn để phục vụ AI Curation
            conn_item = sqlite3.connect(db_file, timeout=30.0)
            conn_item.row_factory = sqlite3.Row
            item_row = conn_item.execute(
                f"SELECT * FROM {manager.LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)
            ).fetchone()
            conn_item.close()

            if not item_row:
                print(f"[⚠️] Không tìm thấy dữ liệu căn {tk_id} trong database.")
                continue

            item_dict = dict(item_row)
            
            # 2. Chạy AI Curation (Bắt buộc chạy bằng cách set run_ai = True)
            item_dict["run_ai"] = True
            print(f"[🤖] Đang khởi chạy AI Curation để biên tập Tiêu đề & Mô tả...")
            manager.run_ai_curation_for_crawled_listing(tk_id, item_dict)

            # 3. Chạy di cư hình ảnh và xuất bản lên Sheets Pool
            print(f"[📸] Đang tải ảnh, tối ưu hóa R2 và xuất bản lên Sheets Pool...")
            manager.run_image_migration_thread(limit=None, cookie=cookie, target_tk_id=tk_id)

        except Exception as e_proc:
            print(f"[❌ LỖI XỬ LÝ] Gặp sự cố khi xử lý căn {tk_id}: {str(e_proc)}")
        finally:
            lock.release()

        # Throttling nhẹ tránh spam APIs quá nhanh
        time.sleep(2.0)


def _is_pid_alive(pid):
    """Kiểm tra xem process với PID có đang chạy trên Windows không."""
    try:
        result = subprocess.run(
            ['tasklist', '/FI', f'PID eq {pid}', '/NH'],
            capture_output=True, text=True, timeout=5
        )
        return str(pid) in result.stdout
    except Exception:
        return False


def _kill_old_worker():
    """Kiểm tra và kill worker cũ nếu còn sống. Trả về True nếu an toàn tiếp tục."""
    if not os.path.exists(WORKER_PID_FILE):
        return True
    try:
        with open(WORKER_PID_FILE, 'r') as f:
            old_pid = int(f.read().strip())
    except Exception:
        # PID file hỏng → xóa và tiếp tục
        try:
            os.remove(WORKER_PID_FILE)
        except Exception:
            pass
        return True

    if old_pid == os.getpid():
        return True

    if _is_pid_alive(old_pid):
        print(f"[🛡️ Singleton] Phát hiện worker cũ (PID {old_pid}) đang chạy. Đang kill...")
        try:
            subprocess.run(['taskkill', '/F', '/PID', str(old_pid)],
                         capture_output=True, timeout=10)
            time.sleep(1)  # Chờ process cũ tắt hoàn toàn
            print(f"[✅ Singleton] Đã kill worker cũ PID {old_pid}.")
        except Exception as e:
            print(f"[⚠️ Singleton] Không kill được worker cũ PID {old_pid}: {e}")
            return False
    else:
        print(f"[🛡️ Singleton] Worker cũ PID {old_pid} đã tắt. Dọn dẹp PID file...")

    try:
        os.remove(WORKER_PID_FILE)
    except Exception:
        pass
    return True


def _write_pid():
    """Ghi PID hiện tại vào file để các instance sau nhận diện."""
    with open(WORKER_PID_FILE, 'w') as f:
        f.write(str(os.getpid()))


def _cleanup_pid():
    """Xóa PID file khi worker kết thúc."""
    try:
        os.remove(WORKER_PID_FILE)
    except Exception:
        pass


def main():
    # === SINGLETON GUARD ===
    if not _kill_old_worker():
        print("[❌] Không thể tiếp quản từ worker cũ. Thoát.")
        sys.exit(1)
    _write_pid()

    # === DỌN STALE DB LOCK ===
    # Tại thời điểm này, singleton guard đã đảm bảo không có worker nào khác chạy.
    # Nếu db.lock tồn tại → chắc chắn là file kẹt từ lần crash trước → xóa an toàn.
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
            print("[🛡️ Startup] Đã dọn dẹp file db.lock bị kẹt từ phiên cũ.")
        except Exception:
            pass

    # Tự động khởi tạo database nếu chưa tồn tại
    try:
        import fetcher
        fetcher.init_db()
    except Exception as e:
        print(f"[⚠️ WARNING] Không thể khởi tạo database: {str(e)}")

    db_mode = "STAGING" if os.environ.get("STAGING") == "true" else "PRODUCTION"
    print("======================================================================")
    print("🚀 KHỞI CHẠY TIẾN TRÌNH XỬ LÝ NGUỒN HÀNG CHẠY NGẦM ĐỘC LẬP (WORKER)")
    print(f"👉 PID: {os.getpid()}")
    print(f"👉 Chế độ CSDL: {db_mode}")
    print(f"👉 Đường dẫn DB: {manager.DB_FILE}")
    print(f"👉 Vòng quét hàng đợi: Mỗi 5 giây")
    print("======================================================================")

    try:
        while True:
            try:
                process_raw_listings()
            except KeyboardInterrupt:
                raise
            except Exception as e_loop:
                print(f"[❌ ERROR] Lỗi vòng lặp worker: {str(e_loop)}")
                time.sleep(5)
            time.sleep(5.0)
    except KeyboardInterrupt:
        print("\n[-] Tiến trình dừng bởi người dùng.")
    finally:
        _cleanup_pid()

if __name__ == "__main__":
    main()
