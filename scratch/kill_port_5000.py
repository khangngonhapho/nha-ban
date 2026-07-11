import subprocess
import sys
import os

def kill_port_5000():
    print("==================================================")
    print("🔍 ĐANG TÌM TIẾN TRÌNH CHIẾM GIỮ CỔNG 5000...")
    print("==================================================")
    
    try:
        output = subprocess.check_output("netstat -aon", shell=True).decode('utf-8', errors='ignore')
        found = False
        
        for line in output.strip().split('\n'):
            if "LISTENING" in line and ":5000" in line:
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    found = True
                    print(f"📍 Phát hiện tiến trình đang nghe trên cổng 5000:")
                    print(f"   - Chi tiết netstat: {line.strip()}")
                    print(f"   - PID: {pid}")
                    
                    # Tìm tên tiến trình
                    try:
                        task_output = subprocess.check_output(f'tasklist /fi "pid eq {pid}"', shell=True).decode('utf-8', errors='ignore')
                        print("   - Tên tiến trình:")
                        for t_line in task_output.strip().split('\n'):
                            if pid in t_line or "Image Name" in t_line or "====" in t_line:
                                print(f"     {t_line.strip()}")
                    except Exception as e_task:
                        print(f"     Không thể lấy tên tiến trình: {str(e_task)}")
                    
                    # Tiến hành tắt tiến trình
                    print(f"🔥 Đang tắt tiến trình PID {pid}...")
                    kill_res = subprocess.run(f"taskkill /f /pid {pid}", shell=True, capture_output=True, text=True)
                    if kill_res.returncode == 0:
                        print(f"✅ ĐÃ TẮT THÀNH CÔNG tiến trình PID {pid}!")
                    else:
                        print(f"❌ Không thể tắt tiến trình: {kill_res.stderr.strip()}")
        
        if not found:
            print("🎉 Không tìm thấy tiến trình nào đang chiếm giữ cổng 5000.")
            print("Cổng 5000 đang hoàn toàn trống!")
            
    except Exception as e:
        print(f"❌ Lỗi hệ thống khi quét port: {str(e)}")
        
    print("==================================================")

if __name__ == "__main__":
    kill_port_5000()
