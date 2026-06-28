import sqlite3
import os

def inspect_db(db_path):
    print(f"=== Inspecting {db_path} ===")
    if not os.path.exists(db_path):
        print("File does not exist")
        return
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get all tables
    tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print("Tables:", tables)
    
    for t in tables:
        count = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"Table '{t}' has {count} rows")
        
        # Check column names
        cols = [r[1] for r in c.execute(f"PRAGMA table_info({t})").fetchall()]
        print(f"  Columns: {cols[:10]} ... (+ {len(cols)-10} more)" if len(cols) > 10 else f"  Columns: {cols}")
        
        # Count TK- format matches in any text columns
        # Let's check common columns like id, tk_id, Link_Goc, Ma_Hang, raw_json_full
        tk_id_cols = [col for col in cols if col.lower() in ['id', 'tk_id', 'ma_hang', 'link_goc', 'ma_tk_moi', 'raw_json_full']]
        for col in tk_id_cols:
            try:
                tk_prefix_count = c.execute(f"SELECT COUNT(*) FROM {t} WHERE {col} LIKE 'TK-%'").fetchone()[0]
                if tk_prefix_count > 0:
                    print(f"  Column '{col}' has {tk_prefix_count} rows starting with 'TK-'")
                
                thienkhoi_link_count = c.execute(f"SELECT COUNT(*) FROM {t} WHERE {col} LIKE '%thienkhoi.com%'").fetchone()[0]
                if thienkhoi_link_count > 0:
                    print(f"  Column '{col}' has {thienkhoi_link_count} rows containing 'thienkhoi.com'")
            except Exception as e:
                print(f"  Error querying {col}: {e}")
                
    conn.close()

inspect_db('raw_archive.db')
inspect_db('raw_archive_v2.db')
inspect_db('raw_archive_temp_read.db')
