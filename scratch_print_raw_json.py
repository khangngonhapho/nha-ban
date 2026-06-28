import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    conn = sqlite3.connect('raw_archive.db')
    cursor = conn.cursor()
    
    # Query raw_json_full for the listing
    cursor.execute("SELECT raw_json_full FROM listings WHERE tk_id LIKE '%010afbec%' OR Ma_Hang = 'TKDWA6Y2';")
    row = cursor.fetchone()
    if row and row[0]:
        print("Found raw_json_full!")
        try:
            data = json.loads(row[0])
            print("Keys in raw_json_full:", list(data.keys()))
            
            # Print direction related fields
            print("\n--- Direction fields ---")
            for k, v in data.items():
                if 'huong' in k.lower() or 'direction' in k.lower():
                    print(f"  {k}: {v}")
            
            # Print criteria if exists
            if 'criteria' in data:
                print("\nCriteria list:")
                print(json.dumps(data['criteria'], indent=2, ensure_ascii=False))
                
            # Print raw response direction if exists in other nested fields
            print("\nNested search:")
            def search_nested(d, path=""):
                if isinstance(d, dict):
                    for k, v in d.items():
                        search_nested(v, f"{path}.{k}" if path else k)
                elif isinstance(d, list):
                    for idx, item in enumerate(d):
                        search_nested(item, f"{path}[{idx}]")
                else:
                    if isinstance(d, str) and any(x in d.lower() for x in ['huong', 'hướng', 'nam', 'bắc', 'đông', 'tây']):
                        print(f"  {path}: {repr(d)}")
            search_nested(data)
        except Exception as e:
            print("Error parsing JSON:", e)
    else:
        print("No raw_json_full found for this listing.")
        
    conn.close()

if __name__ == '__main__':
    main()
