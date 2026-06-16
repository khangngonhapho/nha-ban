# -*- coding: utf-8 -*-
"""
==================================================
KHANG NGÔ NHÀ PHỐ - DYNAMIC E2E TEST RUNNER
Bộ quét và chạy tự động toàn bộ các kịch bản test E2E Playwright
==================================================
"""

import os
import sys
import subprocess
import glob

def run_all_tests():
    # Thư mục scratch chứa các file test E2E
    scratch_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Tìm kiếm tất cả các file test_e2e_*.py
    test_pattern = os.path.join(scratch_dir, "test_e2e_*.py")
    test_files = glob.glob(test_pattern)
    
    # Loại trừ chính file runner này
    test_files = [f for f in test_files if not os.path.basename(f).startswith("run_all_e2e")]
    
    # Sắp xếp tên file để chạy tuần tự nhất quán
    test_files.sort()
    
    print("\n==================================================")
    print(f"🔍 [E2E RUNNER] PHÁT HIỆN {len(test_files)} KỊCH BẢN KIỂM THỬ E2E:")
    for f in test_files:
        print(f"  - {os.path.basename(f)}")
    print("==================================================\n")
    
    if not test_files:
        print("[⚠️ WARNING] Không tìm thấy tệp test E2E nào!")
        sys.exit(0)
        
    # Nhận các đối số dòng lệnh (ví dụ: --headed)
    args = sys.argv[1:]
    
    passed_tests = []
    failed_tests = []
    
    for idx, test_file in enumerate(test_files, 1):
        filename = os.path.basename(test_file)
        print(f"[{idx}/{len(test_files)}] 🚀 Đang khởi chạy: {filename}...")
        
        # Chạy file test với python interpreter hiện tại
        cmd = [sys.executable, test_file] + args
        
        try:
            # Cho phép in trực tiếp ra console để theo dõi thời gian thực
            result = subprocess.run(cmd, capture_output=False)
            
            if result.returncode == 0:
                print(f"  [✅ PASS] {filename}\n")
                passed_tests.append(filename)
            else:
                print(f"  [❌ FAIL] {filename} (Mã lỗi: {result.returncode})\n")
                failed_tests.append(filename)
        except Exception as e:
            print(f"  [❌ LỖI HỆ THỐNG] Không thể chạy {filename}: {str(e)}\n")
            failed_tests.append(filename)
            
    print("==================================================")
    print("📊 BÁO CÁO TỔNG HỢP KIỂM THỬ E2E:")
    print(f"  - Tổng số test case: {len(test_files)}")
    print(f"  - Thành công:        {len(passed_tests)}")
    print(f"  - Thất bại:          {len(failed_tests)}")
    print("==================================================")
    
    if failed_tests:
        print("\n[🚨 THẤT BẠI] Danh sách các kịch bản lỗi:")
        for f in failed_tests:
            print(f"  - {f}")
        print("\nVui lòng sửa lỗi trước khi merge/deploy!")
        sys.exit(1)
    else:
        print("\n[🎉 THÀNH CÔNG] Toàn bộ kịch bản test E2E chạy thành công 100%!")
        sys.exit(0)

if __name__ == "__main__":
    run_all_tests()
