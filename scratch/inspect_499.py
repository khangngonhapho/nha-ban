import sqlite3
import json
import sys

try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

conn = sqlite3.connect('raw_archive.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Lấy danh sách cột thực tế
cursor.execute("PRAGMA table_info(listings)")
columns = [row[1] for row in cursor.fetchall()]

# Tìm kiếm linh hoạt trên tất cả các cột
rows = cursor.execute("SELECT * FROM listings").fetchall()
matched_rows = []

for r in rows:
    row_dict = dict(r)
    # Kiểm tra xem có chứa '499' và 'Điện Biên Phủ' trong bất kỳ trường nào không
    has_499 = False
    has_dbp = False
    for col in columns:
        val = str(row_dict.get(col) or "").lower()
        if '499' in val:
            has_499 = True
        if 'điện biên phủ' in val or 'dien bien phu' in val:
            has_dbp = True
    if has_499 and has_dbp:
        matched_rows.append(row_dict)

print(f"Tìm thấy {len(matched_rows)} kết quả phù hợp:")
for idx, d in enumerate(matched_rows, start=1):
    print(f"\n--- KẾT QUẢ #{idx} ---")
    print("Mã TK:", d.get('tk_id'))
    print("Trạng thái:", d.get('status'))
    
    # In ra tất cả các cột chứa dữ liệu địa chỉ
    for col in columns:
        if any(keyword in col.lower() for keyword in ['ma_hang', 'khang_ngo', 'so_nha', 'duong', 'quan', 'ngo', 'phuong', 'dia_chi', 'system_id']):
            print(f"  {col}: {d.get(col)}")
            
    # 5 Sơ đồ
    print("\n[5 Sơ đồ thửa đất]:")
    for i in range(1, 6):
        col_name = None
        for col in columns:
            if f"so_do_thua_dat_{i}" in col.lower() or f"s__đ__th_a_đ__t_{i}" in col.lower():
                col_name = col
                break
        if col_name:
            print(f"  {col_name}: {d.get(col_name) or 'Trống'}")
            
    # 15 Ảnh
    print("\n[15 Ảnh thường]:")
    for i in range(1, 16):
        col_name = None
        for col in columns:
            if f"anh_{i}" == col.lower() or f"ảnh_{i}" == col.lower():
                col_name = col
                break
        if col_name:
            print(f"  {col_name}: {d.get(col_name) or 'Trống'}")

    # raw_drive_images_json
    print("\n[raw_drive_images_json]:")
    try:
        drive_imgs = json.loads(d.get('raw_drive_images_json') or '[]')
        print(f"  Số lượng: {len(drive_imgs)}")
        for img_idx, img in enumerate(drive_imgs[:5]):
            print(f"    Index {img_idx}: {img}")
    except Exception as e:
        print("  Lỗi parse JSON:", str(e))

conn.close()
