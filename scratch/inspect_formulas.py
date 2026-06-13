import sys
sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
import manager
import gspread

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def main():
    creds = manager.get_google_credentials()
    if not creds:
        print("Could not load credentials.")
        return
        
    client = gspread.authorize(creds)
    
    pool_id = "1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0"
    try:
        ss = client.open_by_key(pool_id)
        sheet = ss.worksheet("Public")
        
        # Get formulas of first few rows
        # gspread worksheet.get('A1:C5', value_render_option='FORMULA')
        formulas = sheet.get('A1:E5', value_render_option='FORMULA')
        print("Formulas in Pool (v1) Public sheet:")
        for r_idx, row in enumerate(formulas):
            print(f"Row {r_idx+1}: {row}")
            
    except Exception as e:
        print("Error inspecting formulas:", e)

if __name__ == '__main__':
    main()
