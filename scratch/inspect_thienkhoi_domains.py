import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('raw_archive.db')
c = conn.cursor()

# Count domains in Link_Goc
data_tk_count = c.execute("SELECT COUNT(*) FROM listings WHERE Link_Goc LIKE '%data.thienkhoi.com%'").fetchone()[0]
proptech_tk_count = c.execute("SELECT COUNT(*) FROM listings WHERE Link_Goc LIKE '%proptech.thienkhoi.com%'").fetchone()[0]
other_tk_count = c.execute("SELECT COUNT(*) FROM listings WHERE Link_Goc NOT LIKE '%data.thienkhoi.com%' AND Link_Goc NOT LIKE '%proptech.thienkhoi.com%'").fetchone()[0]

print("=== Link_Goc Domain Counts in raw_archive.db ===")
print(f"  data.thienkhoi.com     : {data_tk_count}")
print(f"  proptech.thienkhoi.com : {proptech_tk_count}")
print(f"  Other / None           : {other_tk_count}")

# Check what the other links look like
if other_tk_count > 0:
    print("\nSamples of other links:")
    other_samples = c.execute("SELECT Link_Goc FROM listings WHERE Link_Goc NOT LIKE '%data.thienkhoi.com%' AND Link_Goc NOT LIKE '%proptech.thienkhoi.com%' LIMIT 5").fetchall()
    for s in other_samples:
        print(f"    {s[0]}")

conn.close()
