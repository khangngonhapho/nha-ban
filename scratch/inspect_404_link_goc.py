import sqlite3

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

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

# Check columns
c.execute("PRAGMA table_info(listings)")
cols = [col[1] for col in c.fetchall()]

link_col = None
for col in cols:
    if col.lower() == "link_goc":
        link_col = col
        break

if not link_col:
    print("Link_Goc column not found. Available columns:", cols)
    conn.close()
    exit(1)

print(f"Using Link_Goc column name: {link_col}")
print("Checking Link_Goc for 18 404 listings:")
count_with_link = 0
for tk_id in ids:
    c.execute(f"SELECT {link_col} FROM listings WHERE tk_id = ?", (tk_id,))
    row = c.fetchone()
    if row:
        link = row[0]
        print(f"- {tk_id}: Link: {link}")
        if link:
            count_with_link += 1

print(f"\nTotal with Link_Goc: {count_with_link} / {len(ids)}")
conn.close()
