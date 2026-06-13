import sqlite3

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("PRAGMA table_info(listings)")
cols = [col[1] for col in c.fetchall()]
print("Table columns:", cols)

ids = [
    'e3gsy4-mhkfviud-5073d0a3',
    'f7foy1-mcn88aoy-1915db2a',
    'csweaw-mjfmhkqd-8e55866b',
    'ezrvpa-mnlhpnod-fb8bc123',
    'f779ea-mnentzhz-a80ddd77',
    'ffzdvy-mkattff3-2e575241',
    'dsclpv-mimq7phf-74d50415',
    'extyry-lusdmvjj-100b0cd2',
    '6hianw-mnxzn98u-dad5c356',
    'g2ipmv-mnzvm0ne-9d1c73fb',
    'bov9td-mm6athmp-64cb688e',
    'ezbi8a-menqnka8-35e73fca',
    'dz5rsi-lt5oxjre-d7ce0a3a',
    'ezbi8a-moxx82mu-60dbd413',
    'gc4mlg-mj0wc597-38cbd21',
    'fihx7t-mhe9lhjd-8b210596',
    'fihx7t-mffkzydd-e94c7c44',
    'f3hvkm-lswyapmm-576f154a'
]

print("\nChecking details for the 18 404 listings:")
for tk_id in ids:
    # We find columns that actually exist
    select_cols = ["raw_images_tk_json"]
    if "Dia_chi" in cols:
        select_cols.append("Dia_chi")
    elif "dia_chi" in cols:
        select_cols.append("dia_chi")
    if "Gia_trieu_dong" in cols:
        select_cols.append("Gia_trieu_dong")
    elif "gia_trieu_dong" in cols:
        select_cols.append("gia_trieu_dong")
        
    c.execute(f"SELECT {', '.join(select_cols)} FROM listings WHERE tk_id = ?", (tk_id,))
    row = c.fetchone()
    if row:
        print(f"\n- {tk_id}:")
        for col_name, val in zip(select_cols, row):
            print(f"  {col_name}: {val}")
        
conn.close()
