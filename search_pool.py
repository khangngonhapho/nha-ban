import json
import os
from curator_server import get_google_credentials, load_config

creds = get_google_credentials()
cfg = load_config()
sheet_id = cfg.get("sheet_id")

if creds and sheet_id:
    try:
        import gspread
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.worksheet("Pool")
        rows = sheet.get_all_values()
        
        targets = ["r488yyawhdd8riairaw5", "pwqcbipldymfs7eil4ey"]
        for t in targets:
            print(f"Searching for {t} in Pool sheet...")
            found = False
            for idx, r in enumerate(rows):
                for col_idx, cell in enumerate(r):
                    if t in str(cell):
                        print(f"  Row {idx+1}, Col {col_idx} (Header: {rows[0][col_idx] if col_idx < len(rows[0]) else ''}): {repr(cell)}")
                        found = True
            if not found:
                print(f"  {t} not found")
    except Exception as e:
        print("Error:", str(e))
else:
    print("No credentials or sheet_id")
