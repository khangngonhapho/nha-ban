import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    conn = sqlite3.connect('raw_archive.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT raw_json_full, Ma_Hang, Huong FROM listings WHERE raw_json_full IS NOT NULL;")
    rows = cursor.fetchall()
    
    print(f"Checking criteria for {len(rows)} listings...")
    found_count = 0
    examples = []
    
    for row in rows:
        raw_json, ma_hang, huong = row
        try:
            data = json.loads(raw_json)
            criteria = data.get('criteria', [])
            for c in criteria:
                name = c.get('name', '')
                group_code = c.get('groupCode', '')
                group_name = c.get('groupName', '')
                if 'huong' in group_code.lower() or 'hướng' in group_name.lower() or 'huong' in name.lower() or 'hướng' in name.lower():
                    found_count += 1
                    examples.append((ma_hang, huong, c))
                    break
        except Exception:
            pass
            
    print(f"Number of listings with direction criteria: {found_count}")
    if examples:
        print("\nExamples:")
        for ex in examples[:5]:
            print(f"  Ma_Hang: {ex[0]} | Huong: {ex[1]} | Criterion: {ex[2]}")
            
    conn.close()

if __name__ == '__main__':
    main()
