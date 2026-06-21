# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('raw_archive.db')
cur = conn.cursor()
row = cur.execute("SELECT id, tk_id, Ma_Hang, System_ID, Quan, Phuong, Duong FROM listings WHERE tk_id = '3acfcaeb-5304-4129-8c39-842a85610de9'").fetchone()
s = f"Listing details in SQLite: {row}"
print(s.encode('ascii', 'backslashreplace').decode('ascii'))
conn.close()
