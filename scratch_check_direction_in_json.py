import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    conn = sqlite3.connect('raw_archive.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT raw_json_full, Ma_Hang, Huong FROM listings WHERE raw_json_full IS NOT NULL;")
    rows = cursor.fetchall()
    
    print(f"Checking {len(rows)} listings...")
    has_direction_in_json = 0
    examples = []
    
    for row in rows:
        raw_json, ma_hang, huong = row
        try:
            data = json.loads(raw_json)
            # Check for keys containing direction
            dir_keys = [k for k in data.keys() if 'direction' in k.lower() or 'huong' in k.lower()]
            if dir_keys:
                has_direction_in_json += 1
                examples.append((ma_hang, huong, dir_keys, {k: data[k] for k in dir_keys}))
        except Exception:
            pass
            
    print(f"Number of listings with direction-related keys in raw_json_full: {has_direction_in_json}")
    if examples:
        print("\nExamples:")
        for ex in examples[:5]:
            print(f"  Ma_Hang: {ex[0]} | Huong: {ex[1]} | Keys: {ex[2]} | Values: {ex[3]}")
            
    conn.close()

if __name__ == '__main__':
    main()
