import sqlite3

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT tk_id, Duyet_Public, Anh_1, Anh_2, So_do_thua_dat_1 FROM listings WHERE tk_id IN ('e3gsy4-mhkfviud-5073d0a3', 'f7foy1-mcn88aoy-1915db2a', 'csweaw-mjfmhkqd-8e55866b', 'ezrvpa-mnlhpnod-fb8bc123', '6hianw-mnfnt9s4-5b9bc1cc')")
rows = c.fetchall()

for row in rows:
    print(f"tk_id: {row[0]}")
    print(f"  Duyet_Public: {row[1]}")
    print(f"  Anh_1: {row[2]}")
    print(f"  Anh_2: {row[3]}")
    print(f"  So_do: {row[4]}")
    print()
    
conn.close()
