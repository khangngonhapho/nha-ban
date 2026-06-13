import os
import sys

# Force UTF-8 encoding
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

log_path = r"C:\Users\Khang Ngo\.gemini\antigravity\brain\1a0c9a2e-44d4-4ea9-af42-4466ed7341e0\.system_generated\tasks\task-1579.log"

if not os.path.exists(log_path):
    print(f"[❌] Không thấy tệp log tại đường dẫn chỉ định.")
    sys.exit(1)

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"Tổng số dòng log: {len(lines)}")

# Đếm số lượng cào lại thành công, cào lỗi, số lượng phát hiện nghiêng, và số lượng đã sửa đổi thành công
scraped_success = 0
failed_scrapes = 0
tilted_detected = 0
fixed_listings = 0
for line in lines:
    if "[✅ Cào lại]" in line:
        scraped_success += 1
    elif "[❌ Cào lại]" in line:
        failed_scrapes += 1
    elif "Phát hiện thực tế:" in line:
        # Ví dụ: "- Phát hiện thực tế: 123 căn bị lỗi xoay ảnh 90 độ."
        try:
            parts = line.split("Phát hiện thực tế: ")
            if len(parts) > 1:
                tilted_detected = int(parts[1].split()[0])
        except Exception:
            pass
    elif "[✅ Sheets Success]" in line:
        fixed_listings += 1

print(f"Thống kê tiến trình:")
print(f"- Số căn đã khôi phục ảnh gốc: {scraped_success}")
print(f"- Số căn cào lỗi: {failed_scrapes}")
print(f"- Số căn lỗi nghiêng 90 độ phát hiện: {tilted_detected if tilted_detected > 0 else 'Đang quét...'}")
print(f"- Số căn ĐÃ SỬA VÀ ĐỒNG BỘ SHEETS THÀNH CÔNG: {fixed_listings}")

# Tìm vị trí bắt đầu Phase 2 "BẮT ĐẦU SỬA"
start_fixing_idx = -1
for idx, line in enumerate(lines):
    if "BẮT ĐẦU SỬA:" in line:
        start_fixing_idx = idx
        break

if start_fixing_idx != -1:
    print(f"\n[💡] Tiến trình đã bước vào Pha 2 (Sửa lỗi & Đồng bộ) từ dòng {start_fixing_idx}!")
else:
    print(f"\n[💡] Tiến trình vẫn đang ở Pha 1 (Quét & Khôi phục) để lọc EXIF...")

# In 30 dòng log cuối cùng
print("\n30 dòng log cuối cùng:")
for line in lines[-30:]:
    print(line.strip())
