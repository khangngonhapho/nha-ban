import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    conn = sqlite3.connect('raw_archive.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT raw_json_full FROM listings WHERE Ma_Hang = 'TK3YQX4T';")
    row = cursor.fetchone()
    if row and row[0]:
        data = json.loads(row[0])
        print("Keys in JSON:", list(data.keys()))
        
        # search for 'Tây Bắc'
        print("\nSearch for 'Tây Bắc' or 'Tay Bac' in JSON:")
        def search_nested(d, path=""):
            if isinstance(d, dict):
                for k, v in d.items():
                    search_nested(v, f"{path}.{k}" if path else k)
            elif isinstance(d, list):
                for idx, item in enumerate(d):
                    search_nested(item, f"{path}[{idx}]")
            else:
                if isinstance(d, str) and any(x in d.lower() for x in ['tây bắc', 'tay bac']):
                    print(f"  {path}: {repr(d)}")
        search_nested(data)
    else:
        print("Not found.")
    conn.close()

if __name__ == '__main__':
    main()
