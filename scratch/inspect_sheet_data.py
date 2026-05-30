import json

try:
    with open("sheet_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    print("Keys in sheet_data.json:", data.keys() if isinstance(data, dict) else "Not a dict")
    if isinstance(data, dict) and "pool" in data:
        pool_rows = data["pool"]
        print(f"Number of pool rows: {len(pool_rows)}")
        if pool_rows:
            print("First pool row (truncated):", [str(x)[:30] for x in pool_rows[0][:20]])
            print("Row 11 (Price) of first row:", pool_rows[0][11] if len(pool_rows[0]) > 11 else "N/A")
            print("Row 57 (Mo ta Public) of first row:", pool_rows[0][57] if len(pool_rows[0]) > 57 else "N/A")
            print("Row 58 (Gia Public) of first row:", pool_rows[0][58] if len(pool_rows[0]) > 58 else "N/A")
except Exception as e:
    print(f"Error: {e}")
