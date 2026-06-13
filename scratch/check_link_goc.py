import sqlite3
import os

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Query Link_Goc for the live listings
    c.execute("SELECT tk_id, Link_Goc FROM listings WHERE Duyet_Public = 'TRUE' LIMIT 5")
    rows = c.fetchall()
    
    print("Sample Link_Goc for live listings:")
    for r in rows:
        print(f"  tk_id: {r[0]}")
        print(f"  Link_Goc: {r[1]}")
        
    # Check total listings with non-empty Link_Goc
    c.execute("SELECT COUNT(*) FROM listings WHERE Duyet_Public = 'TRUE' AND Link_Goc IS NOT NULL AND Link_Goc != ''")
    count_link = c.fetchone()[0]
    print(f"\nLive listings with Link_Goc: {count_link} / 90")
    
    conn.close()
else:
    print("DB not found")
