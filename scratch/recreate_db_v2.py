# -*- coding: utf-8 -*-
import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_file = 'raw_archive_v2.db'
if os.path.exists(db_file):
    print(f"Deleting existing database {db_file}...")
    os.remove(db_file)

import pool_lego

print("Initializing new database...")
pool_lego.init_db()

print("Verifying schema columns in listings_v2:")
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(listings_v2)")
cols = [r[1] for r in cursor.fetchall()]
print(cols)
conn.close()
