import os
import sys
import sqlite3

# Ensure we can import core.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

def main():
    dbs = [
        r"D:\02. CONG VIEC\khangngonhapho.com\raw_archive.db",
        r"D:\02. CONG VIEC\khangngonhapho.com\raw_archive_staging.db"
    ]
    
    print("=== DELETING MOCK LISTING 'test-tk-id-123' ===")
    
    for db in dbs:
        db_name = os.path.basename(db)
        if not os.path.exists(db):
            print(f"[{db_name}] Skip: Database file does not exist.")
            continue
            
        print(f"\nProcessing {db_name}...")
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        try:
            # Check if exists
            cursor.execute("SELECT COUNT(*) FROM listings WHERE tk_id = 'test-tk-id-123'")
            exists = cursor.fetchone()[0]
            
            if exists == 0:
                print(f"  [{db_name}] Mock listing not found. Skipping.")
                conn.close()
                continue
                
            # Delete from listings_images
            cursor.execute("DELETE FROM listings_images WHERE tk_id = 'test-tk-id-123'")
            images_deleted = cursor.rowcount
            print(f"  [{db_name}] Deleted {images_deleted} image records from listings_images.")
            
            # Delete from listings
            cursor.execute("DELETE FROM listings WHERE tk_id = 'test-tk-id-123'")
            listings_deleted = cursor.rowcount
            print(f"  [{db_name}] Deleted {listings_deleted} listing records from listings.")
            
            conn.commit()
            print(f"  [{db_name}] Changes committed successfully.")
            
        except Exception as e:
            conn.rollback()
            print(f"  [{db_name}] Error during deletion: {str(e)}")
        finally:
            conn.close()
            
    print("\n=== DELETION OF MOCK LISTING COMPLETED ===")

if __name__ == "__main__":
    main()
