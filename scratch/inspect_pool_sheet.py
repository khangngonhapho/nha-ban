import sys
import os
import json

# Add project root to path so we can import curator_server modules
sys.path.append(os.path.abspath("."))

from curator_server import get_google_credentials, load_config
import gspread

def main():
    creds = get_google_credentials()
    if not creds:
        print("Error: Could not load Google credentials.")
        return
        
    cfg = load_config()
    sheet_id = cfg.get("sheet_id")
    if not sheet_id:
        print("Error: Could not load sheet_id from config.")
        return
        
    print(f"Connecting to Spreadsheet: {sheet_id}...")
    try:
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.worksheet("Pool")
        
        headers = sheet.row_values(1)
        print("\n--- Headers (Row 1) ---")
        for idx, h in enumerate(headers):
            print(f"{idx}: {h}")
            
        rows = sheet.get_all_values()
        if len(rows) > 1:
            first_row = rows[1]
            print("\n--- First Data Row (Row 2) ---")
            for idx, val in enumerate(first_row):
                header = headers[idx] if idx < len(headers) else "N/A"
                print(f"{idx} ({header}): {val}")
        else:
            print("\nNo data rows found in Pool sheet.")
            
    except Exception as e:
        print(f"Error connecting to Sheets: {e}")

if __name__ == "__main__":
    main()
