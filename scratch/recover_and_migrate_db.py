import os
import shutil
import sqlite3

def main():
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dest_dir = r"D:\02. CONG VIEC\khangngonhapho.com"
    backup_db = r"D:\LHTBrain\BDS_Backups\raw_archive_staging_backup_20260714_195841.db"

    print("=== DATABASE MIGRATION & RECOVERY PROCESS ===")
    print(f"Source Directory: {src_dir}")
    print(f"Destination Directory: {dest_dir}")
    print(f"Backup Source Database: {backup_db}")

    if not os.path.exists(dest_dir):
        print(f"Error: Destination directory {dest_dir} does not exist!")
        return

    # 1. Migrate DB Files (Copy if not already present, or backup first)
    db_files = ["raw_archive.db", "raw_archive_staging.db"]
    for db_file in db_files:
        src_path = os.path.join(src_dir, db_file)
        dest_path = os.path.join(dest_dir, db_file)
        
        if os.path.exists(src_path):
            if os.path.exists(dest_path):
                # Back up existing destination file before overwriting
                dest_backup = dest_path + ".bak"
                print(f"Destination file {dest_path} already exists. Backing up to {dest_backup}")
                shutil.copy2(dest_path, dest_backup)
            
            print(f"Copying {db_file} from project root to {dest_dir}...")
            shutil.copy2(src_path, dest_path)
        else:
            print(f"Warning: Source file {src_path} not found. Skipping copy.")

    # 2. Connect to Backup DB and read raw_json_full
    if not os.path.exists(backup_db):
        print(f"Error: Backup DB {backup_db} does not exist! Cannot recover raw_json_full.")
        return

    print("Connecting to backup database to read raw_json_full data...")
    backup_conn = sqlite3.connect(backup_db)
    backup_cursor = backup_conn.cursor()
    
    # Query all non-empty raw_json_full rows
    backup_cursor.execute("SELECT tk_id, raw_json_full FROM listings WHERE raw_json_full IS NOT NULL AND raw_json_full != ''")
    raw_data = backup_cursor.fetchall()
    backup_conn.close()
    
    print(f"Found {len(raw_data)} healthy raw_json_full records in backup.")
    if len(raw_data) == 0:
        print("No raw_json_full data to recover.")
        return

    # 3. Recover raw_json_full in Destination DBs
    for db_file in db_files:
        dest_path = os.path.join(dest_dir, db_file)
        if not os.path.exists(dest_path):
            print(f"Skip recovery for {db_file}: file does not exist at destination.")
            continue

        print(f"\nProcessing recovery for {db_file}...")
        conn = sqlite3.connect(dest_path)
        cursor = conn.cursor()

        # Check count before
        cursor.execute("SELECT COUNT(*) FROM listings WHERE raw_json_full IS NOT NULL AND raw_json_full != ''")
        before_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM listings")
        total_count = cursor.fetchone()[0]
        print(f"  Before Recovery: {before_count} / {total_count} listings have raw_json_full.")

        # Update
        updated_count = 0
        for tk_id, raw_json in raw_data:
            cursor.execute(
                "UPDATE listings SET raw_json_full = ? WHERE tk_id = ? AND (raw_json_full IS NULL OR raw_json_full = '')",
                (raw_json, tk_id)
            )
            updated_count += cursor.rowcount

        conn.commit()

        # Check count after
        cursor.execute("SELECT COUNT(*) FROM listings WHERE raw_json_full IS NOT NULL AND raw_json_full != ''")
        after_count = cursor.fetchone()[0]
        print(f"  After Recovery: {after_count} / {total_count} listings have raw_json_full (Recovered/Updated: {updated_count} rows).")
        
        conn.close()

    print("\n=== MIGRATION & RECOVERY COMPLETED ===")

if __name__ == "__main__":
    main()
