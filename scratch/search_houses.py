import sqlite3
import json

def search_db():
    conn = sqlite3.connect("raw_archive.db")
    cursor = conn.cursor()
    
    # Get columns
    cursor.execute("PRAGMA table_info(listings);")
    cols = [c[1] for c in cursor.fetchall()]
    
    # Query for "Phạm Văn Hai"
    query = "SELECT * FROM listings WHERE " + " OR ".join([f"CAST({c} AS TEXT) LIKE '%Phạm Văn Hai%'" for c in cols])
    cursor.execute(query)
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        results.append(dict(zip(cols, r)))
        
    with open("scratch/db_search_results.txt", "w", encoding="utf-8") as out:
        json.dump(results, out, indent=2, ensure_ascii=False)
        
    print(f"Done. Found {len(results)} matches.")
    conn.close()

if __name__ == "__main__":
    search_db()
