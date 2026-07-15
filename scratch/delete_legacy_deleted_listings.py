import os
import sys
import sqlite3

# Ensure we can import core.db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

def main():
    # Force staging mode to target the staging database
    os.environ["STAGING"] = "true"
    
    from core.db import get_db_file
    db_file = get_db_file()
    
    print("=== DELETING LEGACY DELETED LISTINGS FROM STAGING ===")
    print(f"Staging Database Path: {db_file}")
    
    if not os.path.exists(db_file):
        print(f"Error: Database file {db_file} does not exist!")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # Check counts before delete
        cursor.execute("SELECT COUNT(*) FROM listings WHERE status = 'sheet_deleted' AND (raw_json_full IS NULL OR raw_json_full = '')")
        target_listings_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM listings WHERE status = 'sheet_deleted'")
        total_deleted_listings_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM listings")
        total_listings_before = cursor.fetchone()[0]
        
        print(f"  Target listings to delete: {target_listings_count}")
        print(f"  Total 'sheet_deleted' listings before: {total_deleted_listings_before}")
        print(f"  Total listings in DB before: {total_listings_before}")

        if target_listings_count == 0:
            print("No listings found matching the criteria. Skipping delete.")
            conn.close()
            return

        # Delete from listings_images first
        cursor.execute("""
            DELETE FROM listings_images 
            WHERE tk_id IN (
                SELECT tk_id FROM listings 
                WHERE status = 'sheet_deleted' AND (raw_json_full IS NULL OR raw_json_full = '')
            )
        """)
        deleted_images_count = cursor.rowcount
        print(f"  Deleted {deleted_images_count} associated image records from listings_images.")

        # Delete from listings
        cursor.execute("""
            DELETE FROM listings 
            WHERE status = 'sheet_deleted' AND (raw_json_full IS NULL OR raw_json_full = '')
        """)
        deleted_listings_count = cursor.rowcount
        print(f"  Deleted {deleted_listings_count} listing records from listings.")

        conn.commit()

        # Check counts after delete
        cursor.execute("SELECT COUNT(*) FROM listings WHERE status = 'sheet_deleted'")
        total_deleted_listings_after = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM listings")
        total_listings_after = cursor.fetchone()[0]
        
        print(f"  Total 'sheet_deleted' listings after: {total_deleted_listings_after}")
        print(f"  Total listings in DB after: {total_listings_after}")

    except Exception as e:
        conn.rollback()
        print(f"Error during deletion: {str(e)}")
    finally:
        conn.close()

    print("=== DELETION COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
