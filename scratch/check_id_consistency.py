import sqlite3
import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

source_sid = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
pool_sid = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"

try:
    gc = gspread.service_account(filename='credentials.json')
    
    # Read Source
    source_sh = gc.open_by_key(source_sid)
    source_w = source_sh.worksheet("Source")
    source_data = source_w.get_all_values()
    
    # Read Pool
    pool_sh = gc.open_by_key(pool_sid)
    pool_w = pool_sh.worksheet("Pool")
    pool_data = pool_w.get_all_values()
    
except Exception as e:
    print(f"Error loading sheets: {e}")
    sys.exit(1)

# Connect to SQLite
conn = sqlite3.connect('raw_archive.db')
c = conn.cursor()

# 1. Map System_ID -> Ma_Khang_Ngo_ID from SQLite
db_map = {}
for r in c.execute("SELECT System_ID, Ma_Khang_Ngo_ID, Ma_Hang FROM listings").fetchall():
    sys_id, ma_kn, ma_hang = r
    if sys_id:
        db_map[sys_id.strip()] = {
            "ma_kn": ma_kn.strip() if ma_kn else "",
            "ma_hang": ma_hang.strip() if ma_hang else "",
            "source": "SQLite"
        }
conn.close()

# 2. Map System_ID -> Ma_Khang_Ngo_ID from Pool Sheet (to double-check sheets mapping)
# Column headers of Pool sheet:
# SOT.md: G (index 6) is Ngõ/Số nhà, BA (index 52) is Mã Khang Ngô (ID), System ID is Column AL (index 37)?
# Let's inspect the headers of Pool sheet first
pool_headers = pool_data[0]
print(f"Pool Headers: {pool_headers[:10]}... (+ {len(pool_headers)-10} more)")

# Find indices in Pool dynamically
pool_sys_id_idx = -1
pool_ma_kn_idx = -1
for idx, h in enumerate(pool_headers):
    h_clean = h.strip().lower()
    if "system id" in h_clean:
        pool_sys_id_idx = idx
    if "mã khang ngô" in h_clean or "ma_khang_ngo" in h_clean or "mã khang ngô (id)" in h_clean:
        pool_ma_kn_idx = idx

print(f"Pool Indices - System ID: {pool_sys_id_idx}, Mã Khang Ngô: {pool_ma_kn_idx}")

pool_map = {}
for idx, row in enumerate(pool_data[1:], start=2):
    if len(row) > max(pool_sys_id_idx, pool_ma_kn_idx):
        sys_id = row[pool_sys_id_idx].strip()
        ma_kn = row[pool_ma_kn_idx].strip()
        if sys_id:
            pool_map[sys_id] = ma_kn

# 3. Read Source sheet rows (from row 3)
source_headers = source_data[1]
source_sys_id_idx = source_headers.index("System ID") if "System ID" in source_headers else 37
source_ma_kn_idx = source_headers.index("id") if "id" in source_headers else 3

print(f"Source Indices - System ID: {source_sys_id_idx}, Mã Khang Ngô (id): {source_ma_kn_idx}")

mismatches = []
mismatches_pool = []

for idx, row in enumerate(source_data[2:], start=3):
    if len(row) <= max(source_sys_id_idx, source_ma_kn_idx):
        continue
    sys_id = row[source_sys_id_idx].strip()
    ma_kn_source = row[source_ma_kn_idx].strip()
    
    if not sys_id or sys_id == "Chờ duyệt":
        continue
        
    # Check SQLite mapping
    sqlite_info = db_map.get(sys_id)
    if sqlite_info:
        ma_kn_sqlite = sqlite_info["ma_kn"]
        ma_hang = sqlite_info["ma_hang"]
        # Only check new listings (not starting with TK-)
        if not ma_hang.startswith("TK-"):
            if ma_kn_source != ma_kn_sqlite:
                mismatches.append({
                    "row_idx": idx,
                    "sys_id": sys_id,
                    "ma_hang": ma_hang,
                    "ma_kn_source": ma_kn_source,
                    "ma_kn_sqlite": ma_kn_sqlite
                })
                
    # Check Pool Sheet mapping
    pool_ma_kn = pool_map.get(sys_id)
    if pool_ma_kn:
        # Check if the listing in Pool is a new listing (we can identify by Ma_Hang not starting with TK- from sqlite)
        is_new_listing = True
        if sqlite_info:
            is_new_listing = not sqlite_info["ma_hang"].startswith("TK-")
            
        if is_new_listing and ma_kn_source != pool_ma_kn:
            mismatches_pool.append({
                "row_idx": idx,
                "sys_id": sys_id,
                "ma_kn_source": ma_kn_source,
                "ma_kn_pool": pool_ma_kn
            })

print(f"\n=== Mismatches against SQLite (Mã Khang Ngô) ===")
print(f"Total mismatches found: {len(mismatches)}")
for m in mismatches:
    print(f"  Row {m['row_idx']}: Sys_ID={m['sys_id']} (Ma_Hang={m['ma_hang']}) | Source={m['ma_kn_source']} vs SQLite={m['ma_kn_sqlite']}")

print(f"\n=== Mismatches against Pool Sheet (Mã Khang Ngô) ===")
print(f"Total mismatches found: {len(mismatches_pool)}")
for m in mismatches_pool:
    print(f"  Row {m['row_idx']}: Sys_ID={m['sys_id']} | Source={m['ma_kn_source']} vs Pool={m['ma_kn_pool']}")
