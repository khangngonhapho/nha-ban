import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    conn = sqlite3.connect('raw_archive.db')
    cursor = conn.cursor()
    
    # Count populated Huong
    cursor.execute("SELECT COUNT(*) FROM listings WHERE Huong IS NOT NULL AND Huong != '';")
    count_non_empty = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM listings;")
    total = cursor.fetchone()[0]
    print(f"Total listings: {total}")
    print(f"Listings with non-empty Huong: {count_non_empty}")
    
    if count_non_empty > 0:
        print("\nExamples of populated Huong:")
        cursor.execute("SELECT Ma_Hang, Huong, tk_id, raw_json_full FROM listings WHERE Huong IS NOT NULL AND Huong != '' LIMIT 3;")
        for row in cursor.fetchall():
            ma_hang, huong, tk_id, raw_json = row
            print(f"  Ma_Hang: {ma_hang}, Huong: {huong}, tk_id: {tk_id}")
            if raw_json:
                try:
                    data = json.loads(raw_json)
                    # Search for where 'huong' or value of direction is in JSON
                    found_keys = []
                    for k, v in data.items():
                        if str(v) == huong:
                            found_keys.append(k)
                    print(f"    Found value '{huong}' in keys: {found_keys}")
                except Exception:
                    pass
    conn.close()

if __name__ == '__main__':
    main()
