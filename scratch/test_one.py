import sqlite3
import requests

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

for tk_id in ['g3rf35-mmz1uh43-1d856ca', '6hianw-mnfnt9s4-5b9bc1cc']:
    url = c.execute("SELECT Anh_1 FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()[0]
    print(f"tk_id: {tk_id}")
    print("URL:", url)
    print("GET Status:", requests.get(url).status_code)
    print("HEAD Status:", requests.head(url).status_code)
    print()

conn.close()
