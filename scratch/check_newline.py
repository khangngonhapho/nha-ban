import sqlite3, sys, os

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

db_file = 'd:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

total = cursor.execute('SELECT COUNT(*) FROM listings').fetchone()[0]
print(f'Total listings: {total}')

nl = chr(10)
cr = chr(13)

has_newline = cursor.execute(
    'SELECT COUNT(*) FROM listings WHERE instr(Noi_dung_chinh, ?) > 0', (nl,)
).fetchone()[0]
print(f'Records with \\n in Noi_dung_chinh: {has_newline}')
print(f'Percentage: {has_newline/total*100:.1f}%' if total > 0 else '')

has_cr = cursor.execute(
    'SELECT COUNT(*) FROM listings WHERE instr(Noi_dung_chinh, ?) > 0', (cr,)
).fetchone()[0]
print(f'Records with \\r in Noi_dung_chinh: {has_cr}')

# Kiểm tra Noi_dung_chinh rỗng
empty_ndc = cursor.execute(
    "SELECT COUNT(*) FROM listings WHERE Noi_dung_chinh IS NULL OR Noi_dung_chinh = ''"
).fetchone()[0]
print(f'Records with empty Noi_dung_chinh: {empty_ndc}')

print()

# Lấy 5 ví dụ bất kỳ có dữ liệu để xem repr thực tế
print('=== 5 sample Noi_dung_chinh values (repr) ===')
rows = cursor.execute(
    "SELECT tk_id, Ma_Hang, Noi_dung_chinh FROM listings WHERE Noi_dung_chinh != '' LIMIT 5"
).fetchall()
for r in rows:
    tk_id, ma_hang, ndc = r
    print(f'  tk_id={tk_id} | Ma_Hang={ma_hang}')
    print(f'  repr: {repr(ndc[:250])}')
    print()

# Xem có bất kỳ ký tự đặc biệt nào trong field không
print('=== Character analysis (first 20 chars of each) ===')
rows2 = cursor.execute(
    "SELECT tk_id, Noi_dung_chinh FROM listings WHERE Noi_dung_chinh != '' LIMIT 20"
).fetchall()
has_special = 0
for r in rows2:
    tk_id, ndc = r
    for ch in ndc:
        if ord(ch) < 32:  # control characters
            has_special += 1
            print(f'  tk_id={tk_id}: found control char ord={ord(ch)} (\\n=10, \\r=13, \\t=9)')
            print(f'  context: {repr(ndc[:100])}')
            break

if has_special == 0:
    print('  No control characters found in first 20 records')

conn.close()
