import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.getcwd()))

try:
    from curator_server import get_google_credentials
    import gspread
    
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    ss = client.open_by_key('1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0')
    sheet = ss.worksheet('Public')
    
    # Read formulas
    # We want to read row 2 and row 3 cells up to column 40 (AN)
    print("=== READING ROW 2 (HEADERS) AND ROW 3 FORMULAS ===")
    
    # We use sheet.get(range_name, value_render_option='FORMULA')
    formulas_r2 = sheet.get("A2:AO2", value_render_option='FORMULA')
    formulas_r3 = sheet.get("A3:AO3", value_render_option='FORMULA')
    
    print("\nRow 2 (Headers):")
    if formulas_r2 and len(formulas_r2) > 0:
        row = formulas_r2[0]
        for idx, val in enumerate(row):
            print(f"  Col {idx+1} ({gspread.utils.rowcol_to_a1(1, idx+1)[:2].replace('1','')}): {val}")
            
    print("\nRow 3 (40.78 TQD Data):")
    if formulas_r3 and len(formulas_r3) > 0:
        row = formulas_r3[0]
        for idx, val in enumerate(row):
            print(f"  Col {idx+1} ({gspread.utils.rowcol_to_a1(1, idx+1)[:2].replace('1','')}): {val}")
            
except Exception as e:
    print("Error:", e)
