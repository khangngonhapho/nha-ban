import shutil
import os

db_file = "raw_archive.db"
temp_db_file = "raw_archive_temp_read.db"

if os.path.exists(db_file):
    shutil.copy2(db_file, temp_db_file)
    print(f"Successfully copied {db_file} to {temp_db_file} to ensure database consistency.")
else:
    print(f"[❌ ERROR] {db_file} not found!")
