import sqlite3
import sys
import os

# Ensure imports work from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pool_lego

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("🧪 Testing DB Schema Migration...")
    
    # Run init_db to perform migration
    pool_lego.init_db()
    
    # Check the columns in the database
    conn = sqlite3.connect('raw_archive.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(listings)")
    cols = [row[1] for row in cursor.fetchall()]
    
    print("Columns in listings table:")
    print("  custom_huong exists:", "custom_huong" in cols)
    
    if "custom_huong" in cols:
        print("  [✅] custom_huong column successfully verified in raw_archive.db!")
        conn.close()
        sys.exit(0)
    else:
        print("  [❌] custom_huong column is missing!")
        conn.close()
        sys.exit(1)

if __name__ == '__main__':
    main()
