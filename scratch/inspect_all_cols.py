import sqlite3
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    tk_id = '3d296527-12f8-4796-b759-c501ca421f6b'
    db_file = 'raw_archive_v2.db'
    
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    row = cur.execute('SELECT * FROM listings_v2 WHERE tk_id = ?', (tk_id,)).fetchone()
    if row:
        d = dict(row)
        print("=== ALL COLUMNS AND VALUES FOR THE LISTING ===")
        for k, v in sorted(d.items()):
            print(f"{k}: {repr(v)}")
    else:
        print(f"Listing {tk_id} not found.")
        
    conn.close()

if __name__ == '__main__':
    main()
