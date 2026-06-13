import sqlite3
import json

db_path = "raw_archive.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Search for 270.93.16 in the database tables
for table_tuple in tables:
    table_name = table_tuple[0]
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Let's search all columns for "270.93.16" or similar values
    for col in columns:
        try:
            query = f"SELECT * FROM {table_name} WHERE `{col}` LIKE ?"
            cursor.execute(query, ('%270.93.16%',))
            rows = cursor.fetchall()
            if rows:
                print(f"Found match in table {table_name}, column {col}:")
                for row in rows:
                    print(dict(zip(columns, row)))
        except Exception as e:
            # print(f"Error querying {table_name}.{col}: {e}")
            pass

conn.close()
