import sqlite3

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check for folder part or image filename part
c.execute("SELECT tk_id, Anh_1 FROM listings WHERE Anh_1 LIKE '%gjkhuth9vmfrbkuu4msa%' OR tk_id LIKE '%7b6cad79%' LIMIT 5")
print("Matches:")
print(c.fetchall())

conn.close()
