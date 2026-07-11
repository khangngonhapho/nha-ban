import sqlite3
import json

conn = sqlite3.connect("raw_archive.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

row = cursor.execute("SELECT * FROM listings WHERE raw_json_full IS NOT NULL LIMIT 1").fetchone()
if row:
    d = dict(row)
    print("Mã Hàng:", d.get("Ma_Hàng") or d.get("Ma_Hang"))
    print("Ngay_bat_dau:", d.get("Ngay_bat_dau"))
    print("Last_Crawl:", d.get("Last_Crawl"))
    print("Last_Sync:", d.get("Last_Sync"))
    
    raw_json = d.get("raw_json_full")
    if raw_json:
        try:
            raw_data = json.loads(raw_json)
            print("\nKeys in raw_json_full:", list(raw_data.keys()))
            
            # Print any date-related keys in raw_data
            date_keys = [k for k in raw_data.keys() if any(x in k.lower() for x in ["date", "time", "created", "updated"])]
            print("\nDate-related keys in raw_json_full:")
            for k in date_keys:
                print(f"  {k}: {raw_data[k]}")
                
            print("\ncreatedAt & updatedAt from raw_json_full:")
            print("  createdAt:", raw_data.get("createdAt"))
            print("  updatedAt:", raw_data.get("updatedAt"))
            print("  createdAtSigned:", raw_data.get("createdAtSigned"))
            print("  contractStartDate:", raw_data.get("contractStartDate"))
            print("  contractEndDate:", raw_data.get("contractEndDate"))
            
        except Exception as e:
            print("Error parsing JSON:", e)
else:
    print("No row with raw_json_full found!")

conn.close()
